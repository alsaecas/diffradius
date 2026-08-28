from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .benchmark import all_cases, materialize, repository_view
from .scoring import aggregate, score_case
from .workflow import run_baseline, run_final


def evaluate(mode: str, output_dir: Path, case_ids: list[str] | None = None) -> dict:
    if mode not in {"baseline", "final"}:
        raise ValueError("mode must be baseline or final")
    output_dir.mkdir(parents=True, exist_ok=True)
    trajectories = output_dir / "trajectories"
    selected = [c for c in all_cases() if case_ids is None or c.id in case_ids]
    records = []
    scores = []

    with tempfile.TemporaryDirectory(prefix="diffradius-") as tmp:
        root = Path(tmp)
        for spec in selected:
            case = materialize(spec.id, root)
            view = repository_view(case)
            result = run_baseline(view, trajectories) if mode == "baseline" else run_final(view, trajectories)
            score = score_case(result.report, case.expected)
            scores.append(score)
            records.append(
                {
                    "case_id": case.id,
                    "title": case.title,
                    "hard": case.hard,
                    "expected": [
                        {"category": risk.category.value, "paths": list(risk.paths)} for risk in case.expected
                    ],
                    "report": result.report.model_dump(mode="json"),
                    "score": score.__dict__,
                    "usage": result.usage.model_dump(),
                    "trajectory_path": result.trajectory_path,
                }
            )

    agg = aggregate(scores)
    payload = {"mode": mode, "aggregate": agg.__dict__, "cases": records}
    (output_dir / f"{mode}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def compare_results(baseline: dict, final: dict) -> dict:
    b = baseline["aggregate"]
    f = final["aggregate"]
    return {
        "primary_metric": "f1",
        "baseline_f1": b["f1"],
        "final_f1": f["f1"],
        "absolute_change": f["f1"] - b["f1"],
        "baseline_recall": b["recall"],
        "final_recall": f["recall"],
        "baseline_precision": b["precision"],
        "final_precision": f["precision"],
        "baseline_perfect_case_rate": b["perfect_case_rate"],
        "final_perfect_case_rate": f["perfect_case_rate"],
    }
