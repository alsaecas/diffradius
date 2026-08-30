# Judge quick path

If you have five minutes, use this order.

## 1. See the result — 30 seconds

| Mode | Seeded risk recall | Regression PRs caught | Safe controls clean | Strict precision | Strict F1 |
|---|---:|---:|---:|---:|---:|
| Direct prompt | **56.2%** | 60.0% | **100%** | 75.0% | 0.643 |
| General tool reviewer | **87.5%** | 86.7% | **100%** | 87.5% | 0.875 |
| **DiffRadius final** | **100%** | **100%** | **100%** | **94.1%** | **0.970** |

The headline is **56.2% → 100% seeded-risk recall**, while safe-case accuracy remained **100%**.

## 2. Understand the problem — 40 seconds

A PR is a small diff over a larger behavioral system. DiffRadius is for the engineer answering: **“what else now behaves differently?”** It follows callers, consumers and preserved contracts instead of stopping at changed lines.

## 3. See why the final design is agentic — 50 seconds

The final `DiffRadius Evidence Investigator` chooses which bounded repository tools to call, where to search next, whether to inspect the before-version, and whether the evidence supports a concrete counterexample. It is one agent because the experiments rejected a specialist swarm.

## 4. Attack the benchmark — 60 seconds

```bash
pytest
python scripts/validate_benchmark.py
```

18 cases: 15 hidden regressions and 3 safe controls. Every regression has visible tests PASS before/after and a held-out oracle PASS before / FAIL after.

Final fingerprint: `87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`.

## 5. Inspect exact evidence — 60 seconds

Open:

- `evidence/README.md`
- `evidence/results/comparison.md`
- `evidence/results/comparison.json`
- `evidence/trajectories/15-multi-risk-access-cache-final.md`

The full per-case matrix is also preserved in final Action run [33303502804](https://github.com/alsaecas/diffradius/actions/runs/33303502804).

## 6. Read the failed experiments — 40 seconds

Open `IMPROVEMENT_CHANGELOG.md`. The original multi-agent pipeline was about 4× more expensive and worse. The final architecture was selected by measured evidence, not drawn first and justified later.

## 7. Try a real change

```bash
diffradius review --repo /path/to/repo --base main --head HEAD \
  --ticket "Describe intended behavior" --output results/review
```

**Demo:** https://diffradius.vercel.app  
**Source:** https://github.com/alsaecas/diffradius
