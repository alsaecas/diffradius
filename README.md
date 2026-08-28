# DiffRadius

> **Find the code your diff forgot.**

DiffRadius is an agentic pull-request investigator for senior developers and tech leads. Instead of
reviewing only the changed lines, it traces the **behavioral impact radius** of a change through callers,
consumers, persistence, configuration, caches, retries, permissions and async lifecycles, then makes an
independent verifier prove every release-risk claim against repository evidence.

Built for the **micro1 Agentic Workflows Hackathon 2026**.

## The problem

A code diff is compact; its consequences are not. A reviewer often has to answer questions such as:

- Did a changed exception contract leave an indirect caller unguarded?
- Will old persisted records still load after a new field is introduced?
- Does a response rename break an internal/export consumer that was not touched in the PR?
- Did a retry create duplicate side effects?
- Did a mutation stop invalidating a cache?

A conventional AI review can stop once the diff itself looks plausible. DiffRadius deliberately moves
outside the diff, forms testable failure hypotheses, and then verifies them.

## Intended user and bottleneck

**User:** a senior engineer or tech lead deciding whether a pull request is safe to release.

**Bottleneck:** impact analysis is fragmented and manual. Relevant evidence is spread across call sites,
contracts, configuration and runtime assumptions, and the reviewer must repeatedly decide where to look
next. Missing one indirect dependency can turn a locally-correct change into a production regression.

**Value:** reduce missed release risks while keeping false alarms low enough that the output remains
usable as an engineering review, not an AI-generated checklist.

## Workflow

```text
Ticket + diff + repository
        |
        v
  Impact Scout
  traces changed behavior and dependants
        |
        v
Adversarial Reviewer
  tries to construct concrete failure cases
        |
        v
 Evidence Verifier
  re-opens evidence and rejects weak claims
        |
        v
 Release-risk report
```

Every stage uses the same bounded, read-only tools:

- list repository files;
- read bounded file ranges;
- search repository text;
- read the supplied diff;
- read the supplied ticket.

The final architecture is deliberately **not assumed to be better**. The repository includes a
single-agent baseline using the same model and tools. The multi-stage workflow survives only if the
fixed evaluation shows a worthwhile quality gain.

## Evaluation

The primary metric is **finding F1**. Recall alone would reward an agent that reports every imaginable
risk; precision alone would reward saying nothing. F1 reflects the actual product promise: catch real
release risks without drowning the reviewer in unsupported claims.

The fixed benchmark has **14 synthetic software changes**:

- 12 changes with known hidden regressions;
- 2 safe negative controls;
- one intentionally indirect hard case;
- visible tests that pass after every change;
- evaluator-only oracle tests that expose the hidden regression in broken cases.

A finding matches ground truth only when both its risk category and an affected evidence path match.
A case is perfect only when all expected risks are found **and no false-positive findings are added**.

Baseline and final receive the same ticket, diff, repository, tools and model. The final workflow uses
more model calls because orchestration is the intervention under test, so runtime and token usage are
reported alongside F1, recall, precision and perfect-case rate.

**No improvement number is claimed yet.** The benchmark is fixed first; results are generated only by
running the documented evaluation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py
```

The deterministic validation does **not** require an API key.

To run the agent benchmark:

```bash
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode both --output results/benchmark
```

To review a real local change:

```bash
diffradius review \
  --repo /path/to/repository \
  --base main \
  --head HEAD \
  --ticket "Explain the intended behavior" \
  --output results/review
```

## Agent trajectories

Each run stores a local JSON trajectory containing:

- the instruction/input given to each agent;
- every repository tool call and bounded response preview;
- each structured agent output;
- the final report path.

Hosted Agents SDK tracing is disabled by default. Local trajectories exist specifically so a judge can
follow representative runs from instructions through tool evidence to the final decision.

## Repository map

```text
src/diffradius/
  agents.py          agent roles and instructions
  tools.py           bounded read-only repository tools
  workflow.py        baseline and multi-stage orchestration
  scoring.py         deterministic scoring
  benchmark.py       fixed-case materialization and oracle isolation
  evaluate.py        baseline/final benchmark runner
  trajectory.py      local reproducibility traces

benchmarks/cases.py  14 fixed synthetic change scenarios
scripts/validate_benchmark.py
IMPROVEMENT_CHANGELOG.md
docs/ARCHITECTURE.md
docs/EVALUATION.md
docs/REPRODUCTION.md
docs/VIDEO_SCRIPT.md
```

## Improvement changelog

See [IMPROVEMENT_CHANGELOG.md](IMPROVEMENT_CHANGELOG.md). It records experiments as hypotheses and
keeps results marked pending until measured. Components that do not contribute will be removed rather
than justified after the fact.

## Safety and data handling

DiffRadius performs only read operations on the target repository. Path traversal is blocked at the
repository boundary. Credentials are never required in submission files. The included benchmark uses
synthetic code so evaluation and trajectories can be shared publicly without exposing proprietary data.

## Reproduce it

See [docs/REPRODUCTION.md](docs/REPRODUCTION.md) for clean-environment commands, and
[docs/EVALUATION.md](docs/EVALUATION.md) for the scoring protocol.
