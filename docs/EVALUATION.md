# Evaluation protocol

## Primary metric

**Finding F1** is the primary metric. It balances catching real release risks (recall) with avoiding
unsupported alarms (precision), which is important for a tool a senior reviewer must be able to trust.

A finding matches ground truth only when:

1. its risk category matches, and
2. at least one evidence path matches an expected affected path.

A case is *perfect* only when every expected risk is found **and no false-positive findings are added**.

## Fixed benchmark

The repository contains 14 deterministic synthetic change scenarios:

- 12 regressions across error propagation, stale state, backward data compatibility, interface
  contracts, authorization, configuration semantics, transactionality, idempotency, async lifecycle,
  security validation, cache consistency and indirect dependencies;
- 2 safe negative controls to punish indiscriminate risk reporting;
- at least one intentionally indirect hard case.

Each case has visible tests that pass after the change and an evaluator-only oracle test. For broken
cases the oracle fails; for safe controls it passes. The oracle is never placed inside the repository
visible to the reviewing agent.

## Fair comparison

Baseline and final workflow receive:

- the same ticket;
- the same diff;
- the same repository contents;
- the same read-only tools;
- the same model selected by `DIFFRADIUS_MODEL`.

The final workflow is allowed more model calls because orchestration is the intervention being tested.
Runtime and token usage are therefore reported alongside quality.

## Commands

```bash
python scripts/validate_benchmark.py
diffradius evaluate --mode baseline --output results/baseline
diffradius evaluate --mode final --output results/final
diffradius evaluate --mode both --output results/comparison
```

Do not publish improvement claims until the fixed benchmark has been run and its JSON results are
committed as evidence.
