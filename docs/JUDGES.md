# Judge quick path

If you have five minutes, use this order.

## 1. Understand the bottleneck — 45 seconds

A pull request is a small diff over a much larger behavioral system. The hard review question is not
“does this changed function look reasonable?” but **“what else now behaves differently?”**.

DiffRadius is for a senior engineer or tech lead making a release decision. It deliberately traces
callers, consumers, persistence, configuration, caches, retry semantics, authorization and lifetime
boundaries before reporting a risk.

## 2. See why this is agentic — 60 seconds

The final candidate workflow separates three jobs:

1. **Impact Scout** — leaves the diff and maps affected behavior/dependants.
2. **Adversarial Reviewer** — turns that map into concrete failure counterexamples.
3. **Evidence Verifier** — independently re-opens files and rejects unsupported claims.

This is not “more agents = better.” The repo contains four evaluation modes—`baseline`, `impact`,
`adversarial`, `final`—so every added stage has to earn its latency and token cost.

## 3. Attack the benchmark — 90 seconds

Run:

```bash
pytest
python scripts/validate_benchmark.py
```

The fixed benchmark has 18 synthetic PRs: 15 regressions and 3 safe controls. Every regression enforces:

```text
visible tests before  PASS
visible tests after   PASS
oracle before         PASS
oracle after          FAIL
```

Safe controls are PASS/PASS. The oracle is evaluator-only and materialized outside the repository exposed
to agents. Every live result carries the same SHA-256 benchmark fingerprint.

## 4. Inspect measured evidence — 60 seconds

After the live benchmark is frozen, start with:

- `evidence/README.md`
- `evidence/results/comparison.md`
- `evidence/results/comparison.json`

The primary metric is finding F1. Secondary metrics expose regression-case detection, safe-case accuracy,
perfect-case rate, time, tokens and estimated cost. The evidence freezer refuses mixed models,
fingerprints or case orders and copies the raw evaluator outputs instead of hand-entering scores.

## 5. Follow one trajectory — 45 seconds

Open a Markdown trace in `evidence/trajectories/`. It shows explicit agent input, bounded repository tool
calls/responses and structured output from instruction to release decision. It deliberately does not
publish private chain-of-thought.

## 6. Try a real change

```bash
diffradius review \
  --repo /path/to/repository \
  --base main \
  --head HEAD \
  --ticket "Describe the intended behavior" \
  --output results/review
```

The usable artifact is `results/review/review.md`; JSON and the trajectory remain available for audit.

**Live demo:** https://diffradius.vercel.app  
**Source:** https://github.com/alsaecas/diffradius
