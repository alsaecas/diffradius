# DiffRadius

> **Find the code your diff forgot.**

DiffRadius is an agentic pull-request investigator for senior developers and tech leads. Instead of
reviewing only the changed lines, it traces the **behavioral impact radius** of a change through callers,
consumers, persistence, configuration, caches, retries, permissions and lifecycle boundaries, then asks
an independent verifier to prove every release-risk claim against repository evidence.

Built for the **micro1 Agentic Workflows Hackathon 2026**.

## The problem

A code diff is compact; its consequences are not. A reviewer often has to answer questions such as:

- Did a changed exception contract leave an indirect caller unguarded?
- Will old persisted records still load after a new field is introduced?
- Does a response rename break a consumer that was not touched in the PR?
- Did a retry duplicate a side effect?
- Did a new cache make authorization stale?
- Did a lazy iterator escape the transaction that owns its data?

A locally-correct patch can therefore be globally unsafe. DiffRadius deliberately leaves the diff,
forms concrete failure hypotheses, follows dependencies, and verifies the evidence before reporting.

## Intended user and bottleneck

**User:** a senior engineer or tech lead deciding whether a pull request is safe to release.

**Bottleneck:** impact analysis is fragmented and manual. Relevant evidence is spread across call sites,
contracts, configuration and runtime assumptions, and the reviewer must repeatedly decide where to look
next. Missing one indirect dependency can turn a reasonable-looking change into a production regression.

**Value:** improve hidden-risk detection without drowning the reviewer in speculative AI warnings.

## Final workflow hypothesis

```text
Ticket + diff + repository
        |
        v
  Impact Scout
  traces changed contracts and dependants
        |
        v
Adversarial Reviewer
  constructs realistic counterexamples
        |
        v
 Evidence Verifier
  independently re-opens evidence
  and rejects weak claims
        |
        v
 Polished release-risk report
```

Every agent gets only five bounded, read-only tools: list files, read bounded file ranges, search text,
read the supplied diff, and read the supplied ticket. Repository path traversal is blocked.

The architecture is a **hypothesis**, not a foregone conclusion. The evaluation includes an ablation
matrix so each extra stage has to earn its latency and cost:

| Stage | Workflow | What it tests |
|---|---|---|
| `baseline` | one general reviewer | fair starting point |
| `impact` | Impact Scout → Review Synthesizer | value of explicit impact mapping |
| `adversarial` | Impact Scout → Adversary → Synthesizer | incremental value of counterexample generation |
| `final` | Impact Scout → Adversary → **Evidence Verifier** | whether independent verification improves trustworthiness |

## Evaluation

The primary metric is **finding F1**. Recall alone rewards an agent that reports every imaginable risk;
precision alone rewards silence. F1 reflects the product promise: catch real release risks while keeping
unsupported alarms low.

The fixed benchmark currently contains **18 synthetic software changes**:

- **15 regression cases**, including one PR with two independent hidden risks;
- **3 safe negative controls** to penalize indiscriminate warning generation;
- several deliberately indirect/hard cases;
- visible tests that pass both before and after the change;
- evaluator-only oracle tests that pass **before** each regression and fail **after** it.

That last invariant matters: it proves the held-out failure is attributable to the change rather than a
pre-existing broken test. The evaluator also records a SHA-256 benchmark fingerprint so all compared
runs can be tied to the same frozen cases.

A predicted finding matches ground truth only when both its risk category and an expected evidence path
match. A case is perfect only when every expected risk is found **and no false-positive findings are
added**.

All experiment stages receive the same ticket, diff, repository, model and repository tools. The
orchestration and specialist instructions are the intervention. Runtime, requests, tokens and an
approximate uncached-token cost are reported alongside F1, recall, precision, regression-case detection,
safe-case accuracy and perfect-case rate.

**No quality-improvement number is claimed yet.** Results stay pending until the fixed benchmark is run
with the real model and the complete JSON evidence is saved.

## Judge demo

A lightweight Vercel demo is included under `demo/`. It visualizes the workflow, frozen benchmark,
integrity invariant and — after a live evaluation is frozen — reads the exact committed comparison
artifact rather than a hand-entered marketing number. The CLI remains the source of truth.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py
```

The deterministic validation requires **no API key** and verifies the full before/after oracle invariant for all 18 cases.

Run the full experiment matrix:

```bash
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode all --output results/benchmark
```

This produces machine-readable JSON, a Markdown comparison table, and local trajectories for every
stage. To compare only the simple baseline and final workflow, use `--mode both`.

Review a real local change:

```bash
diffradius review \
  --repo /path/to/repository \
  --base main \
  --head HEAD \
  --ticket "Explain the intended behavior" \
  --output results/review
```

The user-facing result is written to `results/review/review.md`; the structured result is preserved as
`review.json`.

## Agent trajectories

Each run stores a local JSON trajectory containing:

- the instruction/input given to each agent;
- every repository tool call and bounded response preview;
- each structured agent output;
- per-stage usage;
- the final report and workflow usage.

Hosted Agents SDK tracing is disabled by default. Local trajectories exist so a judge can follow a run
from instruction → tool evidence → hypothesis → verification → decision without exposing unrelated
telemetry.

## Repository map

```text
src/diffradius/
  agents.py          baseline + specialist agent instructions
  tools.py           bounded read-only repository tools
  workflow.py        baseline, ablations and final orchestration
  scoring.py         deterministic finding-level scoring
  benchmark.py       case materialization, oracle isolation, fingerprint
  evaluate.py        fixed benchmark runner + experiment comparison
  render.py          polished Markdown review/comparison output
  trajectory.py      local reproducibility traces
  trajectory_render.py judge-friendly Markdown trace renderer
  pricing.py         transparent approximate model-cost calculation

benchmarks/           18 fixed synthetic change scenarios
demo/                 static Vercel judge demo
evidence/             frozen live results (pending until measured)
scripts/validate_benchmark.py
scripts/freeze_evidence.py
.github/workflows/benchmark.yml
IMPROVEMENT_CHANGELOG.md
docs/ARCHITECTURE.md
docs/EVALUATION.md
docs/REPRODUCTION.md
docs/VIDEO_SCRIPT.md
docs/SUBMISSION_CHECKLIST.md
```

## Improvement changelog

[IMPROVEMENT_CHANGELOG.md](IMPROVEMENT_CHANGELOG.md) is intentionally an experiment log rather than a
success story written in advance. Components that do not contribute will be removed and the failed
experiment will remain documented.

## Safety and data handling

DiffRadius performs only read operations on the target repository and deliberately does not execute
arbitrary target-repository code. Credentials are never written to submission files. Hosted tracing is
disabled. The included benchmark uses synthetic code so evaluation results and representative
trajectories can be shared publicly without exposing proprietary data. See [SECURITY.md](SECURITY.md).

## Reproduce it

See [docs/REPRODUCTION.md](docs/REPRODUCTION.md) for clean-environment commands,
[docs/EVALUATION.md](docs/EVALUATION.md) for the scoring protocol, and
[docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md) for the remaining hackathon deliverables.
