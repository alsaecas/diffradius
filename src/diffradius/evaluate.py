from __future__ import annotations

import json
import platform
import tempfile
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Callable

from .benchmark import all_cases, benchmark_fingerprint, materialize, repository_view
from .config import settings
from .models import WorkflowResult
from .scoring import aggregate, score_case
from .workflow import run_adversarial, run_baseline, run_final, run_impact


RUNNERS: dict[str, Callable[..., WorkflowResult]] = {
    "baseline": run_baseline,
    "impact": run_impact,
    "adversarial": run_adversarial,
    "final": run_final,
}


def _aggregate_usage(records: list[dict]) -> dict:
    usages = [record["usage"] for record in records]
    costs = [u["estimated_cost_usd"] for u in usages]
    return {
        "requests": sum(u["requests"] for u in usages),
        "input_tokens": sum(u["input_tokens"] for u in usages),
        "output_tokens": sum(u["output_tokens"] for u in usages),
        "total_tokens": sum(u["total_tokens"] for u in usages),
        "elapsed_seconds": round(sum(u["elapsed_seconds"] for u in usages), 3),
        "estimated_cost_usd": round(sum(c for c in costs if c is not None), 6)
        if all(c is not None for c in costs)
        else None,
    }


def evaluate(mode: str, output_dir: Path, case_ids: list[str] | None = None) -> dict:
    if mode not in RUNNERS:
        raise ValueError(f"mode must be one of {', '.join(RUNNERS)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    trajectories = output_dir / "trajectories" / mode
    available = all_cases()
    selected = [c for c in available if case_ids is None or c.id in case_ids]
    if case_ids is not None:
        requested = set(case_ids)
        found = {c.id for c in selected}
        unknown = sorted(requested - found)
        if unknown:
            raise ValueError(f"Unknown benchmark case IDs: {', '.join(unknown)}")
    if not selected:
        raise ValueError("No benchmark cases selected")
    records: list[dict] = []
    scores = []
    runner = RUNNERS[mode]

    with tempfile.TemporaryDirectory(prefix="diffradius-") as tmp:
        root = Path(tmp)
        for spec in selected:
            case = materialize(spec.id, root)
            result = runner(repository_view(case), trajectories)
            score = score_case(result.report, case.expected)
            scores.append(score)
            records.append(
                {
                    "case_id": case.id,
                    "title": case.title,
                    "hard": case.hard,
                    "expected": [
                        {
                            "category": risk.category.value,
                            "accepted_categories": [c.value for c in risk.accepted_categories],
                            "paths": list(risk.paths),
                        }
                        for risk in case.expected
                    ],
                    "report": result.report.model_dump(mode="json"),
                    "score": score.__dict__,
                    "usage": result.usage.model_dump(),
                    "trajectory_path": result.trajectory_path,
                }
            )

    agg = aggregate(scores)
    try:
        agents_version = version("openai-agents")
    except PackageNotFoundError:
        agents_version = "unknown"
    cfg = settings()
    payload = {
        "mode": mode,
        "model": cfg.model,
        "max_turns": cfg.max_turns,
        "benchmark_fingerprint": benchmark_fingerprint(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "openai_agents": agents_version,
        },
        "aggregate": agg.__dict__,
        "usage": _aggregate_usage(records),
        "cases": records,
    }
    (output_dir / f"{mode}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def compare_results(results: dict[str, dict]) -> dict:
    stages = [stage for stage in RUNNERS if stage in results]
    if not stages:
        raise ValueError("No benchmark results supplied")
    fingerprints = {results[stage]["benchmark_fingerprint"] for stage in stages}
    if len(fingerprints) != 1:
        raise ValueError("Cannot compare results from different benchmark fingerprints")
    models = {results[stage].get("model") for stage in stages}
    if len(models) != 1:
        raise ValueError("Cannot compare stages run with different models")
    case_sets = {
        stage: [case["case_id"] for case in results[stage]["cases"]]
        for stage in stages
    }
    first_case_set = case_sets[stages[0]]
    if any(case_sets[stage] != first_case_set for stage in stages[1:]):
        raise ValueError("Cannot compare stages run on different ordered case sets")
    summary = {
        stage: {
            "f1": results[stage]["aggregate"]["f1"],
            "recall": results[stage]["aggregate"]["recall"],
            "precision": results[stage]["aggregate"]["precision"],
            "perfect_case_rate": results[stage]["aggregate"]["perfect_case_rate"],
            "regression_case_detection_rate": results[stage]["aggregate"]["regression_case_detection_rate"],
            "safe_case_accuracy": results[stage]["aggregate"]["safe_case_accuracy"],
            "elapsed_seconds": results[stage]["usage"]["elapsed_seconds"],
            "estimated_cost_usd": results[stage]["usage"]["estimated_cost_usd"],
            "total_tokens": results[stage]["usage"]["total_tokens"],
        }
        for stage in stages
    }
    deltas = []
    for previous, current in zip(stages, stages[1:]):
        deltas.append(
            {
                "from": previous,
                "to": current,
                "risk_recall_change": summary[current]["recall"] - summary[previous]["recall"],
                "safe_case_accuracy_change": summary[current]["safe_case_accuracy"]
                - summary[previous]["safe_case_accuracy"],
                "strict_precision_change": summary[current]["precision"] - summary[previous]["precision"],
                "f1_change": summary[current]["f1"] - summary[previous]["f1"],
            }
        )
    return {
        "primary_metric": "risk_recall",
        "model": next(iter(models)),
        "benchmark_fingerprint": next(iter(fingerprints)),
        "case_count": len(first_case_set),
        "stages": summary,
        "stage_deltas": deltas,
        "metric_note": (
            "Risk recall is primary. Strict finding precision is diagnostic because regression cases "
            "can contain valid unseeded consequences; safe-case accuracy is the hallucination control."
        ),
    }
