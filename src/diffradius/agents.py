from __future__ import annotations

from agents import Agent

from .config import settings
from .models import AdversarialReview, ImpactMap, ReviewReport
from .tools import READ_ONLY_TOOLS, ReviewContext


BASELINE_INSTRUCTIONS = """
You are a senior engineer reviewing a software change in a bounded, read-only repository.
Read the ticket and diff, inspect repository files when useful, and report concrete release risks
caused by this change. Support findings with repository evidence. Do not invent evidence or pad the
review with generic best-practice advice. If the change is safe, return no findings.
"""

SPECIALIST_COMMON = """
You investigate a software change inside a bounded, read-only repository. Never invent evidence.
A claim is useful only when it points to concrete repository evidence. Distinguish a real regression
from a generic best-practice suggestion. Do not read files outside the repository.
"""


def baseline_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Baseline Reviewer",
        model=settings().model,
        instructions=BASELINE_INSTRUCTIONS,
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )


def impact_scout_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Impact Scout",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
Map the behavioral impact radius before judging the change. Start from the diff, identify changed
contracts and symbols, then trace direct and indirect dependants. Explicitly consider callers,
consumers, persistence, configuration, caches, retries, permissions, async lifecycles and tests only
where the changed behavior makes them relevant. Generate candidate risks with specific evidence and
an explicit verification plan. A candidate is a hypothesis, not a verdict.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ImpactMap,
    )


def adversary_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Adversarial Reviewer",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
You receive an impact map produced by another agent. Try to break the change in realistic ways.
Challenge assumptions, inspect overlooked paths, and refine or add candidate risks. Prefer concrete
counterexamples that a regression test could express. Do not promote speculation without repository
evidence, and do not repeat a candidate merely with different wording.
""",
        tools=READ_ONLY_TOOLS,
        output_type=AdversarialReview,
    )


def synthesizer_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Review Synthesizer",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
You receive candidate risks from upstream analysis. Convert the supported candidates into a concise,
usable release-risk report. Remove obvious duplicates and generic advice. You may inspect repository
files when clarification is needed, but this stage is not an independent evidence-verification pass.
Return a final release decision.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )


def verifier_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Evidence Verifier",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
You receive candidate risks from prior agents. Independently verify every candidate against the
actual repository: re-open the relevant evidence rather than trusting the upstream summary. Reject
unsupported, duplicate, pre-existing, or merely stylistic claims. A final finding must describe a
concrete failure mode caused by the supplied diff and contain repository evidence. If evidence is
insufficient, reject it. Return a final release decision.
""",
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )
