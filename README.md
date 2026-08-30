# DiffRadius

> **Find the code your diff forgot.**

DiffRadius is an evidence-seeking pull-request investigator for senior engineers and tech leads. A diff shows edited lines; it does not show every caller, compatibility assumption, cache, permission boundary, transaction lifetime, or downstream consumer that can break because of those edits.

Built for the **micro1 Agentic Workflows Hackathon 2026**.

## Measured result

The final frozen evaluation uses the same **18 cases**, same model (`gpt-5.6-luna`), and same ordered case set for all three modes.

| Mode | Seeded risk recall | Regression PRs caught | Safe controls clean | Strict precision | Strict F1 | Tokens | Est. cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct prompt | **56.2%** | 60.0% | **100%** | 75.0% | 0.643 | 14,065 | $0.0055 |
| General tool reviewer | **87.5%** | 86.7% | **100%** | 87.5% | 0.875 | 72,289 | $0.0216 |
| **DiffRadius final** | **100%** | **100%** | **100%** | **94.1%** | **0.970** | 106,084 | $0.0299 |

From the direct-prompt baseline to DiffRadius, seeded-risk recall improved **43.8 percentage points (77.8% relative)** while safe-case accuracy stayed at **100%**. The final run caught every seeded hidden regression, including the two independent failures in the multi-risk authorization/cache case.

**Primary metric:** seeded regression-risk recall. **False-alarm control:** safe-case accuracy. Strict precision/F1 remain published diagnostics because a broken synthetic PR can contain a real evidence-backed consequence beyond the seeded label set.

The final comparison, benchmark fingerprint, and representative trajectories are committed in [`evidence/`](evidence/). Complete per-case JSON from the same frozen run is preserved in the linked GitHub Actions artifact.

## Final architecture

```text
ticket + diff + changed repository
              |
              v
   DiffRadius Evidence Investigator
              |
      +-------+---------+
      |       |         |
      v       v         v
   search   current   BEFORE
    repo     files     files
      |       |         |
      +-------+---------+
              |
              v
     prove a concrete counterexample
              |
              v
      release-risk report
```

The selected architecture is deliberately **one agent, not a swarm**. It has six bounded read-only tools: ticket, diff, file listing, bounded current-file reads, repository search, and bounded reads of the **before-version** of a file. It iteratively chooses where to look and reports a risk only when it can cash the warning out as a concrete change-induced counterexample.

That simplicity is a measured result. Two earlier multi-agent designs were slower, more expensive, and less accurate. Their failed experiments remain documented in [`IMPROVEMENT_CHANGELOG.md`](IMPROVEMENT_CHANGELOG.md).

## Problem and user

**User:** a senior engineer or tech lead deciding whether a pull request is safe to release.

**Bottleneck:** impact analysis is scattered across callers, consumers, persistence, configuration, caches, retries, permissions and resource lifetimes. A locally-correct diff can pass visible tests and still break an untouched workflow.

Examples represented in the benchmark include exception propagation, stale UI state, old-data compatibility, API contract changes, authorization ordering, config-default semantics, transactionality, retry/idempotency, async lifecycle, path traversal, cache invalidation, identity normalization, and lazy resource lifetime.

## Benchmark integrity

The benchmark contains **15 regression cases + 3 safe controls**. Every regression satisfies:

```text
                     BEFORE   AFTER
visible tests          PASS     PASS
held-out oracle        PASS     FAIL
```

Safe controls are PASS/PASS. The held-out oracle is materialized outside the repository visible to the agent.

Final benchmark SHA-256:

```text
87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889
```

The evidence freezer refuses mixed models, benchmark fingerprints, case orders, or incomplete case sets. No benchmark case, oracle, or scoring rule was changed after the final freeze.

## The experiment changed the product

The original design was `Impact Scout → Adversarial Reviewer → Evidence Verifier`. It looked more agentic. It performed worse.

Trajectory analysis showed that the handoffs were **lossy compression**: useful evidence was reduced to schemas, speculation accumulated, and later agents inherited abstractions instead of re-discovering facts. A contract-first swarm also underperformed.

The final design removed the swarm and kept the capability that mattered: one investigator that can leave the diff, inspect dependants, compare before/after behavior, and prove counterexamples.

> **Hot take:** for repository review, the agent boundary can be the bug. The winning improvement was not a bigger swarm; it was giving one agent the right evidence boundary.

## Quick start

```bash
git clone https://github.com/alsaecas/diffradius.git
cd diffradius
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# deterministic integrity checks — no API key
pytest
python scripts/validate_benchmark.py

# live evaluation
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode all --output results/benchmark
```

Review a real local change:

```bash
diffradius review \
  --repo /path/to/repository \
  --base main \
  --head HEAD \
  --ticket "Describe the intended behavior" \
  --output results/review
```

## Agent trajectories

Representative traces in `evidence/trajectories/` show agent inputs, bounded tool calls/responses, structured outputs, and usage without exposing private chain-of-thought. Start with `15-multi-risk-access-cache-final.md`: it shows the final investigator identifying both stale authorization caching and the newly fail-open timeout path.

## Links

- **Live demo:** https://diffradius.vercel.app
- **Source:** https://github.com/alsaecas/diffradius
- **Frozen evidence:** [`evidence/README.md`](evidence/README.md)
- **Judge quick path:** [`docs/JUDGES.md`](docs/JUDGES.md)
- **Improvement changelog:** [`IMPROVEMENT_CHANGELOG.md`](IMPROVEMENT_CHANGELOG.md)
- **Reproduction guide:** [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md)
