from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    ERROR_PROPAGATION = "error_propagation"
    STALE_STATE = "stale_state"
    DATA_COMPATIBILITY = "data_compatibility"
    INTERFACE_CONTRACT = "interface_contract"
    AUTHORIZATION = "authorization"
    CONFIGURATION = "configuration"
    TRANSACTIONALITY = "transactionality"
    IDEMPOTENCY = "idempotency"
    ASYNC_LIFECYCLE = "async_lifecycle"
    SECURITY_VALIDATION = "security_validation"
    CACHE_CONSISTENCY = "cache_consistency"
    INDIRECT_DEPENDENCY = "indirect_dependency"
    OTHER = "other"


Severity = Literal["low", "medium", "high", "critical"]
Decision = Literal["approve", "needs_review", "block"]


class Evidence(BaseModel):
    path: str = Field(description="Repository-relative file path supporting the claim")
    line_hint: str = Field(default="", description="Function, symbol, or approximate line range")
    explanation: str = Field(description="Why this code supports the claim")


class CandidateRisk(BaseModel):
    category: RiskCategory
    title: str
    severity: Severity
    failure_mode: str
    evidence: list[Evidence] = Field(default_factory=list)
    verification_plan: str


class ImpactMap(BaseModel):
    changed_behavior: list[str] = Field(default_factory=list)
    affected_symbols: list[str] = Field(default_factory=list)
    candidate_risks: list[CandidateRisk] = Field(default_factory=list)
    blind_spots: list[str] = Field(default_factory=list)


class AdversarialReview(BaseModel):
    candidate_risks: list[CandidateRisk] = Field(default_factory=list)
    attack_notes: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    category: RiskCategory
    title: str
    severity: Severity
    failure_mode: str
    evidence: list[Evidence]
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_test: str


class RejectedFinding(BaseModel):
    category: RiskCategory
    title: str
    reason: str


class ReviewReport(BaseModel):
    decision: Decision
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    rejected_findings: list[RejectedFinding] = Field(default_factory=list)


class RunUsage(BaseModel):
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    elapsed_seconds: float = 0.0


class WorkflowResult(BaseModel):
    report: ReviewReport
    usage: RunUsage
    trajectory_path: str | None = None
