from diffradius.models import Evidence, Finding, ReviewReport, RiskCategory, RunUsage
from diffradius.render import render_comparison, render_review


def test_review_markdown_is_user_facing():
    report = ReviewReport(
        decision="block",
        summary="One verified risk.",
        findings=[
            Finding(
                category=RiskCategory.ERROR_PROPAGATION,
                title="Caller now crashes",
                severity="high",
                failure_mode="An exception crosses the caller boundary.",
                evidence=[Evidence(path="app/form.py", line_hint="switch_org", explanation="No handler remains.")],
                confidence=0.95,
                recommended_test="Exercise the failing client.",
            )
        ],
    )
    text = render_review(report, RunUsage(total_tokens=1234, estimated_cost_usd=0.01))
    assert "BLOCK RELEASE" in text
    assert "Caller now crashes" in text
    assert "`app/form.py`" in text
    assert "1,234" in text


def test_comparison_markdown_contains_stages():
    comparison = {
        "primary_metric": "risk_recall",
        "metric_note": "Risk recall is primary.",
        "stages": {
            "baseline": {"f1": 0.5, "recall": 0.5, "precision": 0.5, "regression_case_detection_rate": 0.6, "safe_case_accuracy": 0.7, "perfect_case_rate": 0.2, "elapsed_seconds": 1.0, "total_tokens": 100, "estimated_cost_usd": 0.01},
            "final": {"f1": 0.8, "recall": 0.8, "precision": 0.8, "regression_case_detection_rate": 0.9, "safe_case_accuracy": 1.0, "perfect_case_rate": 0.5, "elapsed_seconds": 3.0, "total_tokens": 300, "estimated_cost_usd": 0.03},
        },
        "stage_deltas": [{"from": "baseline", "to": "final", "risk_recall_change": 0.3, "safe_case_accuracy_change": 0.3, "strict_precision_change": 0.3, "f1_change": 0.3}],
    }
    text = render_comparison(comparison)
    assert "SEEDED RISK RECALL" in text
    assert "| baseline |" in text
    assert "| final |" in text
    assert "baseline → final" in text
