from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Finding, ReviewReport, RiskCategory


@dataclass(frozen=True)
class ExpectedRisk:
    category: RiskCategory
    paths: tuple[str, ...]
    accepted_categories: tuple[RiskCategory, ...] = ()

    @property
    def categories(self) -> tuple[RiskCategory, ...]:
        return (self.category, *self.accepted_categories)


@dataclass(frozen=True)
class CaseScore:
    true_positives: int
    false_positives: int
    false_negatives: int
    perfect: bool
    expected_count: int

    @property
    def is_safe(self) -> bool:
        return self.expected_count == 0

    @property
    def detected_regression(self) -> bool:
        return self.expected_count > 0 and self.true_positives > 0

    @property
    def clean_safe_case(self) -> bool:
        return self.is_safe and self.false_positives == 0


@dataclass(frozen=True)
class AggregateScore:
    recall: float
    precision: float
    f1: float
    perfect_case_rate: float
    regression_case_detection_rate: float
    safe_case_accuracy: float
    true_positives: int
    false_positives: int
    false_negatives: int
    regression_cases: int
    safe_cases: int


def _paths(finding: Finding) -> set[str]:
    return {e.path for e in finding.evidence}


def score_case(report: ReviewReport, expected: Iterable[ExpectedRisk]) -> CaseScore:
    """Score seeded risks deterministically.

    A seeded risk may declare a small set of accepted mechanism categories when the
    same concrete failure is reasonably described in more than one way (for example,
    a lazy cursor escaping a transaction can be called transactionality or lifecycle).
    Path evidence is still mandatory. Extra findings remain visible as strict false
    positives, but recall is the primary benchmark metric because regression cases can
    legitimately contain additional, unseeded release risks.
    """
    expected = list(expected)
    remaining = list(expected)
    matched_findings: set[int] = set()
    tp = 0

    for expected_risk in list(remaining):
        for index, finding in enumerate(report.findings):
            if index in matched_findings:
                continue
            if finding.category not in expected_risk.categories:
                continue
            if _paths(finding).intersection(expected_risk.paths):
                tp += 1
                matched_findings.add(index)
                remaining.remove(expected_risk)
                break

    fp = len(report.findings) - len(matched_findings)
    fn = len(remaining)
    return CaseScore(tp, fp, fn, perfect=(fn == 0 and fp == 0), expected_count=len(expected))


def aggregate(scores: Iterable[CaseScore]) -> AggregateScore:
    scores = list(scores)
    tp = sum(s.true_positives for s in scores)
    fp = sum(s.false_positives for s in scores)
    fn = sum(s.false_negatives for s in scores)
    recall = tp / (tp + fn) if tp + fn else 1.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    f1 = 2 * recall * precision / (recall + precision) if recall + precision else 0.0
    perfect = sum(1 for s in scores if s.perfect) / len(scores) if scores else 0.0

    regression_scores = [s for s in scores if not s.is_safe]
    safe_scores = [s for s in scores if s.is_safe]
    regression_detection = (
        sum(1 for s in regression_scores if s.detected_regression) / len(regression_scores)
        if regression_scores
        else 1.0
    )
    safe_accuracy = (
        sum(1 for s in safe_scores if s.clean_safe_case) / len(safe_scores) if safe_scores else 1.0
    )

    return AggregateScore(
        recall=recall,
        precision=precision,
        f1=f1,
        perfect_case_rate=perfect,
        regression_case_detection_rate=regression_detection,
        safe_case_accuracy=safe_accuracy,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        regression_cases=len(regression_scores),
        safe_cases=len(safe_scores),
    )
