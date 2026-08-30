# DiffRadius — HackerEarth submission copy

## One-line pitch

**DiffRadius finds the code your diff forgot:** an evidence-seeking PR investigator that leaves the changed lines, traces affected behavior, compares before/after contracts, and reports concrete release-risk counterexamples backed by repository evidence.

## Problem and user value

The user is a senior engineer or tech lead deciding whether a pull request is safe to release.

A diff shows edits, not the full impact radius. Reviewers manually trace callers, consumers, persisted data, authorization, caches, retries, configuration, and resource lifetimes. Missing one indirect dependency can turn a locally correct change into a production regression.

DiffRadius automates that investigation while keeping the output auditable.

## Agentic solution

The final system uses **one tool-using agent**. This is deliberate: two measured multi-agent experiments performed worse.

The DiffRadius Evidence Investigator can inspect the ticket/diff, list/search/read bounded current repository files, inspect the **before-version** of a file, iteratively gather evidence, and emit a structured release decision with a concrete failure mode, evidence, confidence, and recommended regression test.

Repository access is read-only and path-bounded.

## Baseline and measured improvement

Final frozen benchmark, **18 cases**, same model and ordered case set:

| Mode | Seeded risk recall | Regression PRs caught | Safe controls clean | Strict precision | Strict F1 | Tokens | Est. cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct prompt | **56.2%** | 60.0% | **100%** | 75.0% | 0.643 | 14,065 | $0.0055 |
| General tool reviewer | **87.5%** | 86.7% | **100%** | 87.5% | 0.875 | 72,289 | $0.0216 |
| **DiffRadius final** | **100%** | **100%** | **100%** | **94.1%** | **0.970** | 106,084 | $0.0299 |

Primary metric is seeded regression-risk recall; safe-case accuracy is the false-alarm control. Strict precision/F1, tokens, wall time, and estimated cost are also published.

The strong `tool` comparator is important: it shows how much is gained from ordinary repository access before evaluating the selected before-state/evidence discipline.

## Improvement story

Our original `Impact Scout → Adversarial Reviewer → Evidence Verifier` workflow was a failed experiment. It was slower, about four times more expensive, and worse than one general tool agent. A contract-first swarm also underperformed.

Trajectory analysis showed that agent handoffs were acting like lossy compression. We removed the swarm and kept the useful capability: change-aware repository evidence.

**Hot take:** for repository review, the agent boundary can be the bug. One investigator with the right evidence boundary can beat a specialist swarm.

## Reproducibility

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py

export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode all --output results/benchmark
```

Final benchmark fingerprint:

`87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`

Final frozen Action run: https://github.com/alsaecas/diffradius/actions/runs/33303502804

## Links

- Live demo: https://diffradius.vercel.app
- Source: https://github.com/alsaecas/diffradius
- Judge quick path: https://github.com/alsaecas/diffradius/blob/main/docs/JUDGES.md
- Frozen evidence: https://github.com/alsaecas/diffradius/tree/main/evidence
- Improvement changelog: https://github.com/alsaecas/diffradius/blob/main/IMPROVEMENT_CHANGELOG.md
- Video: **ADD FINAL VIDEO URL**
