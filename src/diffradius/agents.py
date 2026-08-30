from __future__ import annotations

from agents import Agent

from .config import settings
from .models import AdversarialReview, ChangeContract, ImpactMap, ReviewReport
from .tools import CHANGE_AWARE_TOOLS, READ_ONLY_TOOLS, ReviewContext


DIRECT_BASELINE_INSTRUCTIONS = """
You are a senior engineer reviewing a software change from only a ticket and unified diff.
Report concrete release risks caused by this change. Do not invent repository context you cannot see.
Support findings only with paths that actually appear in the supplied diff. Avoid generic best-practice
advice. If the supplied evidence does not support a risk, do not report it.
"""

TOOL_REVIEWER_INSTRUCTIONS = """
You are a senior engineer reviewing a software change in a bounded, read-only repository.
Read the ticket and diff, then inspect repository files when useful. Look beyond changed lines for
callers, consumers, persisted-data assumptions, configuration, caches, retries, permissions and
lifecycle boundaries. Report concrete release risks caused by this change and support them with
repository evidence. Do not invent evidence or pad the review with generic advice. If the change is
safe, return no findings.
"""

PROOF_REVIEWER_INSTRUCTIONS = """
You are DiffRadius, an evidence-seeking release-risk investigator inside a bounded, read-only repository.
Your job is not to produce more warnings; it is to find change-induced counterexamples and prove them.

Use this investigation discipline:
1. Read the ticket and diff and separate intentional behavior changes from behavior that should remain
   compatible.
2. Trace current callers/consumers of changed behavior instead of stopping at the diff.
3. When compatibility matters, compare the current file with its before-version. The before-version is
   valid evidence that an input or call pattern used to work even if no current fixture mentions it.
4. Report a finding only when you can describe a concrete counterexample: something that worked before,
   or a current preserved caller/invariant, that the new code breaks.
5. Do not treat "the ticket asked for it" as proof that downstream breakage is acceptable. Intended local
   behavior can still violate preserved interfaces, security expectations or callers.
6. Merge multiple consequences of the same root defect into one finding unless they are independently
   testable regressions. Do not invent unrelated speculative risks.
7. Safe changes should produce no findings.

Every final finding must cite repository-relative evidence paths that you actually inspected. Prefer a
small number of high-confidence findings over broad speculation.
"""

SPECIALIST_COMMON = """
You investigate a software change inside a bounded, read-only repository. Never invent evidence.
A claim is useful only when it points to concrete repository evidence. Distinguish an intended
behavioral change from a regression. Do not read files outside the repository.
"""


def prompt_baseline_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Direct Prompt Baseline",
        model=settings().model,
        instructions=DIRECT_BASELINE_INSTRUCTIONS,
        output_type=ReviewReport,
    )


def tool_reviewer_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="General Tool Reviewer",
        model=settings().model,
        instructions=TOOL_REVIEWER_INSTRUCTIONS,
        tools=READ_ONLY_TOOLS,
        output_type=ReviewReport,
    )


def proof_reviewer_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="DiffRadius Evidence Investigator",
        model=settings().model,
        instructions=PROOF_REVIEWER_INSTRUCTIONS,
        tools=CHANGE_AWARE_TOOLS,
        output_type=ReviewReport,
    )


# Historical experiment agents are retained so the failed multi-agent iterations remain reproducible.
def contract_agent() -> Agent[ReviewContext]:
    return Agent[ReviewContext](
        name="Change Contract Analyst",
        model=settings().model,
        instructions=SPECIALIST_COMMON
        + """
Before hunting for bugs, reconstruct the behavioral contract of the change. Read the ticket and diff.
For changed files, compare the current implementation with the before-version when useful. Separate
intentional behavior, preserved compatibility, previously accepted behaviors, changed symbols and
investigation targets. Do not report release findings yet.
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
only concrete candidate regressions. A useful candidate must explain a specific before/after or
caller-based counterexample. Avoid duplicates and generic subsystem risks.
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
Historical ablation stage. Falsify upstream candidates first, then look for at most one genuinely
independent missed failure. Added candidates must have a concrete regression-test-shaped
counterexample rather than generic best-practice concerns.
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
Historical ablation stage. Convert supported candidate risks into a concise report. Remove duplicates
and generic advice; do not invent new risks.
""",
        tools=CHANGE_AWARE_TOOLS,
        output_type=ReviewReport,
    )
