from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskSpec:
    category: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    ticket: str
    before: dict[str, str]
    after: dict[str, str]
    oracle: str
    expected: tuple[RiskSpec, ...]
    hard: bool = False
