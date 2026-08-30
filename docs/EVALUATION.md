# Evaluation protocol

## Primary metric

**Seeded regression-risk recall** is primary: detected seeded risks / all seeded risks. **Safe-case accuracy** is the false-alarm control. Strict precision/F1 are also published as diagnostics.

A seeded risk matches when its predicted category is the canonical category (or a pre-declared equivalent for genuinely ambiguous cross-cutting failures) and at least one cited evidence path intersects the expected affected paths. Each prediction can match at most one seeded risk.

This rubric was finalized **before** the final frozen run. The final benchmark fingerprint is `87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`.

## Final matrix

| Mode | Seeded risk recall | Regression PRs caught | Safe controls clean | Strict precision | Strict F1 | Tokens | Est. cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct prompt | **56.2%** | 60.0% | **100%** | 75.0% | 0.643 | 14,065 | $0.0055 |
| General tool reviewer | **87.5%** | 86.7% | **100%** | 87.5% | 0.875 | 72,289 | $0.0216 |
| **DiffRadius final** | **100%** | **100%** | **100%** | **94.1%** | **0.970** | 106,084 | $0.0299 |

All stages use the same model and 18 ordered cases. The intervention is the information/tool boundary:

| Mode | Information available | Purpose |
|---|---|---|
| `prompt` | ticket + unified diff only | simple baseline |
| `tool` | prompt inputs + five bounded current-repository tools | quantify ordinary repo-tool access |
| `final` | tool comparator + bounded `read_before_file` and explicit evidence/counterexample discipline | selected DiffRadius workflow |

## Ground-truth integrity

The benchmark has 15 regression cases and 3 safe controls. Every regression must satisfy visible PASS/PASS and oracle PASS/FAIL before/after. Safe controls must remain PASS/PASS. Oracle data is outside the agent-visible repository.

## Resource reporting

Every stage records wall time, tokens, requests, and approximate model cost. The final matrix cost was $0.0055 / $0.0216 / $0.0299 for prompt/tool/final respectively across 18 cases.

## Historical experiments

Earlier multi-agent systems are retained in the changelog and GitHub Action history but are not the selected final architecture. Their failure is part of the submission evidence.

## Commands

```bash
python scripts/validate_benchmark.py
diffradius evaluate --mode prompt --output results/benchmark
diffradius evaluate --mode tool --output results/benchmark
diffradius evaluate --mode final --output results/benchmark
diffradius evaluate --mode all --output results/benchmark
```

The final frozen run is GitHub Action `33303502804`.
