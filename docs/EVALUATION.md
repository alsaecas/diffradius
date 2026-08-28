# Evaluation protocol

## Primary metric

**Finding F1** is the primary metric. It balances catching real release risks (recall) with avoiding
unsupported alarms (precision), which matters for a review a senior engineer must be able to trust.

A predicted finding matches ground truth only when:

1. its risk category matches; and
2. at least one cited evidence path matches an expected affected path.

Each prediction can match at most one expected risk. A case is *perfect* only when every expected risk
is found **and no false-positive findings are added**.

## Secondary metrics

The report also exposes metrics that are easier to interpret operationally:

- **regression-case detection rate** — percentage of broken PRs where at least one true hidden risk was found;
- **safe-case accuracy** — percentage of safe controls where the reviewer produced zero false alarms;
- **perfect-case rate** — percentage of cases where every expected risk was found with zero extras;
- **requests / tokens / wall time / estimated cost** — the resource price of each workflow stage.

The primary claim should still be based on F1; secondary metrics explain *how* it changed.

## Frozen synthetic benchmark

The benchmark contains **18 deterministic changes**:

- 15 regression cases;
- 3 safe negative controls;
- one two-risk case;
- multiple explicitly hard/indirect cases.

Covered failure families include error propagation, stale state, backward data compatibility, interface
contracts, authorization, configuration semantics, transactionality, retry/idempotency, async lifecycle,
security validation, cache consistency, identity normalization and lazy resource lifetimes.

### Ground-truth integrity

Every case has an ordinary visible test suite plus an evaluator-only oracle. Validation enforces:

```text
Regression case:
  visible tests before = PASS
  visible tests after  = PASS
  oracle before        = PASS
  oracle after         = FAIL

Safe control:
  visible tests before = PASS
  visible tests after  = PASS
  oracle before        = PASS
  oracle after         = PASS
```

This makes the hidden failure attributable to the submitted change instead of a pre-existing bug in the
fixture. Oracle files are materialized outside the repository that agents can inspect.

The evaluator writes a SHA-256 fingerprint of the complete benchmark definition into every result file.
Compared runs must have the same fingerprint. At the current freeze, the expected fingerprint is printed
by `python scripts/validate_benchmark.py`; do not hard-code it into scoring logic.

## Fair experiment matrix

All modes receive the same ticket, diff, changed repository, model and read-only repository tools.

| Mode | Purpose |
|---|---|
| `baseline` | normal single-agent review |
| `impact` | test explicit impact mapping |
| `adversarial` | measure incremental counterexample generation |
| `final` | test independent verification at the same stage count as `adversarial` |

The extra model calls are part of the intervention, not hidden. Every mode reports quality plus requests,
input/output tokens, wall-clock agent time and approximate model cost. The project does **not** claim the
multi-agent path is “fair” because it costs the same; it is fair because the resource difference is
explicit and measured alongside outcome quality.

## Commands

```bash
python scripts/validate_benchmark.py

diffradius evaluate --mode baseline --output results/benchmark
diffradius evaluate --mode impact --output results/benchmark
diffradius evaluate --mode adversarial --output results/benchmark
diffradius evaluate --mode final --output results/benchmark

# Full matrix + comparison.json + comparison.md
diffradius evaluate --mode all --output results/benchmark
```

A repository-level **Agent benchmark** GitHub Action exposes the same full-matrix run through
`workflow_dispatch`. It requires `OPENAI_API_KEY` as a repository Actions secret and uploads the raw
results plus a frozen judge-facing evidence bundle as an artifact.

## Freezing evidence

After one complete live run:

```bash
python scripts/freeze_evidence.py \
  --results results/benchmark \
  --evidence evidence
```

The freezer refuses to combine different benchmark fingerprints, differently ordered case sets, or
fewer than ten cases. It copies the complete result matrix and representative baseline/final trajectories
without editing measured values.

Do not publish improvement claims until the fixed benchmark has been run and its complete result files
are saved as evidence. Model sampling can make exact reruns vary; reproducibility here means a clean,
documented path to the same evaluation task, inputs, metrics and artifacts rather than a promise of
bit-for-bit identical LLM output.
