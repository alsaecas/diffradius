from diffradius.models import Evidence, Finding, ReviewReport, RiskCategory
from diffradius.scoring import ExpectedRisk, aggregate, score_case


def finding(category: RiskCategory, path: str) -> Finding:
    return Finding(
        category=category,
        title="risk",
        severity="high",
        failure_mode="breaks",
        evidence=[Evidence(path=path, explanation="evidence")],
        confidence=0.9,
        recommended_test="test it",
    )


def report(*findings: Finding) -> ReviewReport:
    return ReviewReport(decision="block" if findings else "approve", summary="x", findings=list(findings))


def test_exact_match_is_perfect():
    score = score_case(
        report(finding(RiskCategory.ERROR_PROPAGATION, "app/form.py")),
        [ExpectedRisk(RiskCategory.ERROR_PROPAGATION, ("app/form.py",))],
    )
    assert score.true_positives == 1
    assert score.false_positives == 0
    assert score.false_negatives == 0
    assert score.perfect


def test_extra_claim_prevents_perfect_score():
    score = score_case(
        report(
            finding(RiskCategory.ERROR_PROPAGATION, "app/form.py"),
            finding(RiskCategory.CONFIGURATION, "app/config.py"),
        ),
        [ExpectedRisk(RiskCategory.ERROR_PROPAGATION, ("app/form.py",))],
    )
    assert score.false_positives == 1
    assert not score.perfect


def test_wrong_evidence_path_does_not_match():
    score = score_case(
        report(finding(RiskCategory.ERROR_PROPAGATION, "app/other.py")),
        [ExpectedRisk(RiskCategory.ERROR_PROPAGATION, ("app/form.py",))],
    )
    assert score.true_positives == 0
    assert score.false_positives == 1
    assert score.false_negatives == 1


def test_negative_control_rewards_no_findings():
    score = score_case(report(), [])
    assert score.perfect


def test_aggregate_metrics():
    scores = [
        score_case(report(finding(RiskCategory.CONFIGURATION, "a.py")), [ExpectedRisk(RiskCategory.CONFIGURATION, ("a.py",))]),
        score_case(report(finding(RiskCategory.OTHER, "b.py")), []),
    ]
    result = aggregate(scores)
    assert result.recall == 1.0
    assert result.precision == 0.5
    assert 0.66 < result.f1 < 0.67
    assert result.perfect_case_rate == 0.5
