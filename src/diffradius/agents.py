from __future__ import annotations

from agents import Agent

from .config import settings
from .models import AdversarialReview, ImpactMap, ReviewReport
from .tools import READ_ONLY_TOOLS, ReviewContext


COMMON = """
You review a software change inside a bounded, read-only repository. Never invent evidence.
A claim is useful only when it points to concrete repository evidence. Distinguish a real
regression from a generic best-practice suggestion. Inspect beyond the changed lines when
behavior can propagate to callers, consumers, persistence, configuration, caches, retries,
permissions, async lifecycles, or tests. Do not read files outside the repository.
"""


def baseline_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Baseline Reviewer",
        model=settings().model,
        instructions=COMMON
        + """
Perform one competent pull-request review. Use the ticket, diff and repository tools as needed.
Return only release risks caused by this change. Verify each finding before including it.
If the change is safe, return no findings. Keep false positives low.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )


def impact_scout_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Impact Scout",
        model=settings().model,
        instructions=COMMON
        + """
Map the behavioral impact radius before judging the change. Start from the diff, identify changed
contracts and symbols, then trace direct and indirect dependants. Generate candidate risks with
specific evidence and an explicit verification plan. A candidate is a hypothesis, not a verdict.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ImpactMap,
    )


def adversary_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Adversarial Reviewer",
        model=settings().model,
        instructions=COMMON
        + """
You receive an impact map produced by another agent. Try to break the change in realistic ways.
Challenge assumptions, look for overlooked paths, and refine or add candidate risks. Prefer
concrete counterexamples that a hidden regression test could express. Do not promote speculation
without repository evidence.
""",
        tools=READ_ONLY_TOOLS,
        output_type=AdversarialReview,
    )


def verifier_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Evidence Verifier",
        model=settings().model,
        instructions=COMMON
        + """
You receive candidate risks from prior agents. Independently verify every candidate against the
actual repository. Reject unsupported, duplicate, pre-existing, or merely stylistic claims.
A final finding must describe a concrete failure mode caused by the supplied diff and contain
repository evidence. If evidence is insufficient, reject it. Return a final release decision.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )
