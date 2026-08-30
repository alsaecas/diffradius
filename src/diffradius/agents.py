from __future__ import annotations

from agents import Agent

from .config import settings
from .models import AdversarialReview, ChangeContract, ImpactMap, ReviewReport
from .tools import CHANGE_AWARE_TOOLS, READ_ONLY_TOOLS, ReviewContext


BASELINE_INSTRUCTIONS = """
You are a senior engineer reviewing a software change in a bounded, read-only repository.
Read the ticket and diff, inspect repository files when useful, and report concrete release risks
caused by this change. Support findings with repository evidence. Do not invent evidence or pad the
review with generic best-practice advice. If the change is safe, return no findings.
"""

SPECIALIST_COMMON = """
You investigate a software change inside a bounded, read-only repository. Never invent evidence.
A claim is useful only when it points to concrete repository evidence. Distinguish an intended
behavioral change from a regression. Do not read files outside the repository.
"""


def baseline_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Baseline Reviewer",
        model=settings().model,
        instructions=BASELINE_INSTRUCTIONS,
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )


def contract_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Change Contract Analyst",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
Before hunting for bugs, reconstruct the behavioral contract of the change. Read the ticket and diff.
For changed files, compare the current implementation with the before-version when useful. Separate:
(1) behavior the ticket intentionally changes,
(2) behavior that should remain compatible,
(3) inputs/call patterns that the before-version demonstrably accepted,
(4) symbols and current dependants that deserve investigation.
Do not report release findings yet. Do not assume that absence of a current fixture means historical
inputs never existed: the before-version itself is evidence of previously accepted behavior.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=ChangeContract,
    )


def impact_scout_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Impact Investigator",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
You receive a structured change contract. Trace the impact radius beyond changed lines and produce
only concrete candidate regressions. Use current callers/consumers and before-vs-after behavior as
evidence. A useful candidate must explain a specific counterexample: something that worked before or
an invariant that should remain true, and how the new code breaks it. Do not generate generic risks
just because a subsystem (cache, auth, transaction, async, config) exists. One failure may have
multiple consequences; avoid duplicates unless they are independently testable regressions.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=ImpactMap,
    )


def adversary_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Adversarial Reviewer",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
This is an experimental stage retained for ablation. You receive contract-first impact candidates.
Try to falsify them first, then look for one genuinely independent missed failure. Do not broaden the
review into hypothetical best-practice concerns. Every added candidate must include a before/after or
caller-based counterexample that could be expressed as a regression test.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=AdversarialReview,
    )


def synthesizer_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Review Synthesizer",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
You receive supported candidate risks from upstream analysis. Convert them into a concise usable
release-risk report. Remove duplicates and generic advice. Do not invent new risks in this stage.
Return a final release decision.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=ReviewReport,
    )


def verifier_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Counterexample Verifier",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
Independently verify every candidate against the actual change. Re-open current and before-version
files rather than trusting upstream summaries. Keep a candidate when you can establish a concrete
change-induced counterexample: a previously accepted input/call path now fails, or a preserved
invariant/current dependant is broken. The before-version is valid compatibility evidence even when
there is no current fixture proving historical production data. Reject intended ticket behavior,
pre-existing problems, duplicates, and speculation that depends on unsupported inputs or runtime
contracts. Preserve distinct supported regressions; do not collapse two independently testable
failures into one. If nothing is proven, return no findings.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=ReviewReport,
    )
