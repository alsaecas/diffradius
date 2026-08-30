from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from diffradius.trajectory_render import render_trajectory_file


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing required benchmark artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float) -> str:
    return f"{value:.1%}"


def freeze(results_dir: Path, evidence_dir: Path) -> None:
    modes = ["prompt", "tool", "final"]
    payloads = {mode: _load(results_dir / f"{mode}.json") for mode in modes}
    comparison = _load(results_dir / "comparison.json")

    fingerprints = {payload["benchmark_fingerprint"] for payload in payloads.values()}
    if len(fingerprints) != 1:
        raise SystemExit(f"Refusing to freeze mixed benchmark fingerprints: {sorted(fingerprints)}")
    fingerprint = next(iter(fingerprints))
    if comparison.get("benchmark_fingerprint") != fingerprint:
        raise SystemExit("Refusing to freeze: comparison fingerprint does not match stage outputs")

    models = {payload.get("model") for payload in payloads.values()}
    if len(models) != 1:
        raise SystemExit(f"Refusing to freeze mixed models: {sorted(str(m) for m in models)}")
    model = next(iter(models))
    if comparison.get("model") != model:
        raise SystemExit("Refusing to freeze: comparison model does not match stage outputs")

    case_sets = {mode: [c["case_id"] for c in payload["cases"]] for mode, payload in payloads.items()}
    first = case_sets[modes[0]]
    if any(case_sets[mode] != first for mode in modes[1:]):
        raise SystemExit("Refusing to freeze: modes were not run on the same ordered case set")
    if len(first) < 10:
        raise SystemExit("Refusing to freeze: fewer than 10 evaluation cases")

    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)
    (evidence_dir / "results").mkdir(parents=True)
    (evidence_dir / "trajectories").mkdir(parents=True)

    for filename in [*map(lambda m: f"{m}.json", modes), "comparison.json", "comparison.md"]:
        shutil.copy2(results_dir / filename, evidence_dir / "results" / filename)

    final_cases = payloads["final"]["cases"]
    differing = []
    prompt_by_id = {c["case_id"]: c for c in payloads["prompt"]["cases"]}
    for case in final_cases:
        prompt_case = prompt_by_id[case["case_id"]]
        if prompt_case["score"] != case["score"]:
            differing.append(case)
    candidates = [c for c in differing if c.get("hard")] or differing or [c for c in final_cases if c.get("hard")] or final_cases
    selected = []
    for case in candidates:
        if case["case_id"] not in {c["case_id"] for c in selected}:
            selected.append(case)
        if len(selected) == 2:
            break

    selected_ids = [c["case_id"] for c in selected]
    for case_id in selected_ids:
        for mode in modes:
            record = next(c for c in payloads[mode]["cases"] if c["case_id"] == case_id)
            src = Path(record["trajectory_path"])
            if not src.is_absolute() and not src.exists():
                src = results_dir.parent.parent / src
            if not src.exists():
                raise SystemExit(f"Missing trajectory for {mode}/{case_id}: {record['trajectory_path']}")
            dst = evidence_dir / "trajectories" / f"{case_id}-{mode}.json"
            shutil.copy2(src, dst)
            render_trajectory_file(dst, dst.with_suffix(".md"))

    stages = comparison["stages"]
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Frozen evaluation evidence",
        "",
        f"Generated: `{now}`",
        f"Benchmark fingerprint: `{fingerprint}`",
        f"Model: `{model}`",
        f"Cases: **{len(first)}**",
        "",
        "These files were copied directly from one complete evaluation matrix. Values in this folder are not hand-edited.",
        "",
        "## Measured comparison",
        "",
        "| Stage | Risk recall | Regression cases caught | Safe cases clean | Strict precision | Strict F1 | Tokens | Est. cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for stage in modes:
        values = stages[stage]
        cost = "—" if values["estimated_cost_usd"] is None else f"${values['estimated_cost_usd']:.4f}"
        lines.append(
            f"| {stage} | {values['recall']:.3f} | {_pct(values['regression_case_detection_rate'])} | "
            f"{_pct(values['safe_case_accuracy'])} | {values['precision']:.3f} | {values['f1']:.3f} | "
            f"{values['total_tokens']:,} | {cost} |"
        )
    lines.extend(["", "## Representative trajectories", ""])
    for case_id in selected_ids:
        lines.append(f"- `{case_id}` — prompt, tool-agent and final JSON + Markdown traces are in `trajectories/`.")
    lines.extend([
        "",
        "The Markdown traces expose prompts, tool calls, bounded tool responses and structured outputs. They deliberately do **not** expose private model chain-of-thought.",
        "",
    ])
    (evidence_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/benchmark")
    parser.add_argument("--evidence", default="evidence")
    args = parser.parse_args()
    freeze(Path(args.results), Path(args.evidence))
