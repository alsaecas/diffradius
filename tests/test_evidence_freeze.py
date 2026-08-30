import json
from pathlib import Path

import pytest

from scripts.freeze_evidence import freeze


MODES = ["prompt", "tool", "final"]


def _trajectory(path: Path, run_id: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"run_id": run_id, "events": []}), encoding="utf-8")
    return str(path)


def _stage_payload(tmp_path: Path, mode: str, fingerprint: str = "frozen") -> dict:
    cases = []
    for index in range(10):
        case_id = f"case-{index:02d}"
        cases.append(
            {
                "case_id": case_id,
                "title": case_id,
                "hard": index in {0, 1},
                "expected": [{"category": "other", "accepted_categories": [], "paths": ["app/a.py"]}],
                "report": {"decision": "block", "summary": "x", "findings": []},
                "score": {"true_positives": 1 if index == 0 else 0, "false_positives": 0, "false_negatives": 0 if index == 0 else 1, "perfect": index == 0, "expected_count": 1},
                "usage": {"requests": 1, "input_tokens": 10, "output_tokens": 5, "total_tokens": 15, "elapsed_seconds": 0.1, "estimated_cost_usd": 0.001},
                "trajectory_path": _trajectory(tmp_path / "raw-trajectories" / mode / f"{case_id}.json", f"{mode}-{case_id}"),
            }
        )
    return {
        "mode": mode,
        "model": "test-model",
        "benchmark_fingerprint": fingerprint,
        "aggregate": {"recall": 0.5, "precision": 0.5, "f1": 0.5, "perfect_case_rate": 0.1, "regression_case_detection_rate": 0.5, "safe_case_accuracy": 1.0, "true_positives": 1, "false_positives": 0, "false_negatives": 9, "regression_cases": 10, "safe_cases": 0},
        "usage": {"requests": 10, "input_tokens": 100, "output_tokens": 50, "total_tokens": 150, "elapsed_seconds": 1.0, "estimated_cost_usd": 0.01},
        "cases": cases,
    }


def _write_matrix(tmp_path: Path, fingerprint: str = "frozen") -> Path:
    results = tmp_path / "results"
    results.mkdir()
    payloads = {mode: _stage_payload(tmp_path, mode, fingerprint) for mode in MODES}
    for mode, payload in payloads.items():
        (results / f"{mode}.json").write_text(json.dumps(payload), encoding="utf-8")
    stages = {mode: {"f1": 0.5, "recall": 0.5, "precision": 0.5, "regression_case_detection_rate": 0.5, "safe_case_accuracy": 1.0, "perfect_case_rate": 0.1, "elapsed_seconds": 1.0, "total_tokens": 150, "estimated_cost_usd": 0.01} for mode in MODES}
    comparison = {"primary_metric": "risk_recall", "model": "test-model", "benchmark_fingerprint": fingerprint, "case_count": 10, "stages": stages, "stage_deltas": []}
    (results / "comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    (results / "comparison.md").write_text("# comparison\n", encoding="utf-8")
    return results


def test_freeze_copies_exact_results_and_renders_representative_traces(tmp_path: Path):
    results = _write_matrix(tmp_path)
    evidence = tmp_path / "evidence"
    freeze(results, evidence)
    assert (evidence / "results" / "comparison.json").read_bytes() == (results / "comparison.json").read_bytes()
    assert "Benchmark fingerprint: `frozen`" in (evidence / "README.md").read_text(encoding="utf-8")
    rendered = sorted((evidence / "trajectories").glob("*.md"))
    assert rendered
    assert "private chain-of-thought" in rendered[0].read_text(encoding="utf-8")


def test_freeze_rejects_mixed_fingerprints(tmp_path: Path):
    results = _write_matrix(tmp_path)
    final = json.loads((results / "final.json").read_text(encoding="utf-8"))
    final["benchmark_fingerprint"] = "different"
    (results / "final.json").write_text(json.dumps(final), encoding="utf-8")
    with pytest.raises(SystemExit, match="mixed benchmark fingerprints"):
        freeze(results, tmp_path / "evidence")


def test_freeze_rejects_different_case_order(tmp_path: Path):
    results = _write_matrix(tmp_path)
    final = json.loads((results / "final.json").read_text(encoding="utf-8"))
    final["cases"] = list(reversed(final["cases"]))
    (results / "final.json").write_text(json.dumps(final), encoding="utf-8")
    with pytest.raises(SystemExit, match="same ordered case set"):
        freeze(results, tmp_path / "evidence")
