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


def test_exact_category_and_path_matches():
    score = score_case(
        report(finding(RiskCategory.AUTHORIZATION, "app/auth.py")),
        [ExpectedRisk(RiskCategory.AUTHORIZATION, ("app/auth.py",))],
    )
    assert (score.true_positives, score.false_positives, score.false_negatives) == (1, 0, 0)
    assert score.perfect


def test_wrong_path_is_false_positive_and_false_negative():
    score = score_case(
        report(finding(RiskCategory.AUTHORIZATION, "app/other.py")),
        [ExpectedRisk(RiskCategory.AUTHORIZATION, ("app/auth.py",))],
    )
    assert (score.true_positives, score.false_positives, score.false_negatives) == (0, 1, 1)
    assert not score.perfect


def test_extra_finding_prevents_perfect_case():
    score = score_case(
        report(
            finding(RiskCategory.AUTHORIZATION, "app/auth.py"),
            finding(RiskCategory.CONFIGURATION, "app/config.py"),
        ),
        [ExpectedRisk(RiskCategory.AUTHORIZATION, ("app/auth.py",))],
    )
    assert (score.true_positives, score.false_positives, score.false_negatives) == (1, 1, 0)
    assert not score.perfect


def test_safe_case_with_no_findings_is_perfect():
    score = score_case(report(), [])
    assert score.perfect
    assert score.is_safe
    assert score.clean_safe_case


def test_aggregate_reports_regression_detection_and_safe_accuracy():
    scores = [
        score_case(
            report(finding(RiskCategory.AUTHORIZATION, "app/auth.py")),
            [ExpectedRisk(RiskCategory.AUTHORIZATION, ("app/auth.py",))],
        ),
        score_case(
            report(),
            [ExpectedRisk(RiskCategory.CONFIGURATION, ("app/config.py",))],
        ),
        score_case(report(), []),
        score_case(report(finding(RiskCategory.OTHER, "app/x.py")), []),
    ]
    agg = aggregate(scores)
    assert agg.regression_case_detection_rate == 0.5
    assert agg.safe_case_accuracy == 0.5
    assert agg.regression_cases == 2
    assert agg.safe_cases == 2
