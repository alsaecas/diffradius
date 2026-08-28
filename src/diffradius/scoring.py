from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Finding, ReviewReport, RiskCategory


@dataclass(frozen=True)
class ExpectedRisk:
    category: RiskCategory
    paths: tuple[str, ...]


@dataclass(frozen=True)
class CaseScore:
    true_positives: int
    false_positives: int
    false_negatives: int
    perfect: bool


@dataclass(frozen=True)
class AggregateScore:
    recall: float
    precision: float
    f1: float
    perfect_case_rate: float
    true_positives: int
    false_positives: int
    false_negatives: int


def _paths(finding: Finding) -> set[str]:
    return {e.path for e in finding.evidence}


def score_case(report: ReviewReport, expected: Iterable[ExpectedRisk]) -> CaseScore:
    remaining = list(expected)
    matched_findings: set[int] = set()
    tp = 0

    for expected_risk in list(remaining):
        for index, finding in enumerate(report.findings):
            if index in matched_findings:
                continue
            if finding.category != expected_risk.category:
                continue
            if _paths(finding).intersection(expected_risk.paths):
                tp += 1
                matched_findings.add(index)
                remaining.remove(expected_risk)
                break

    fp = len(report.findings) - len(matched_findings)
    fn = len(remaining)
    return CaseScore(tp, fp, fn, perfect=(fn == 0 and fp == 0))


def aggregate(scores: Iterable[CaseScore]) -> AggregateScore:
    scores = list(scores)
    tp = sum(s.true_positives for s in scores)
    fp = sum(s.false_positives for s in scores)
    fn = sum(s.false_negatives for s in scores)
    recall = tp / (tp + fn) if tp + fn else 1.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    f1 = 2 * recall * precision / (recall + precision) if recall + precision else 0.0
    perfect = sum(1 for s in scores if s.perfect) / len(scores) if scores else 0.0
    return AggregateScore(recall, precision, f1, perfect, tp, fp, fn)
