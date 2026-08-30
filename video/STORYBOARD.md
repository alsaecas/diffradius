# DiffRadius final storyboard

| Time | Scene | Visual treatment | Evidence |
|---|---|---|---|
| 0:00–0:20 | Hook | Large thesis typography; real case-15 diff; repository-boundary nodes expand around the changed file | `benchmarks/cases_5.py` |
| 0:20–0:50 | Problem | Untouched dependency grid; visible-green/hidden-red contrast; direct-prompt baseline | `README.md`, frozen comparison |
| 0:50–1:45 | Real investigation | Three-column case, exact tool sequence, current/before snippets, two independent risk cards | `evidence/trajectories/15-multi-risk-access-cache-final.md` |
| 1:45–2:15 | Agentic workflow | Six read-only tools pulse; evidence loop and proof discipline | `src/diffradius/tools.py`, `agents.py` |
| 2:15–2:55 | Benchmark | Animated before/after invariant, oracle boundary, frozen fingerprint | benchmark definitions, `docs/EVALUATION.md` |
| 2:55–3:30 | Results | Three animated recall bars plus safe accuracy, regression detection, F1, tokens and cost | `evidence/results/comparison.json` |
| 3:30–4:05 | Failed experiment | Scout → Adversary → Verifier collapses; historical F1/cost comparison; trajectory failure modes | `IMPROVEMENT_CHANGELOG.md` |
| 4:05–4:30 | Lesson | “The agent boundary can be the bug” with explicit “in our experiments” scope | changelog and architecture docs |
| 4:30–4:42 | Reproduce/end | Exact clean commands, final metrics, demo and GitHub links | `docs/REPRODUCTION.md` |

## Visual system

- 1920×1080 at 30 fps.
- Near-black grid background, mint primary accent, blue secondary accent, restrained red for evidence-backed failures.
- System sans for judge-readable hierarchy; monospace for repository evidence and metrics.
- Captions remain in a dedicated lower band and never cover code or primary figures.
- All audio is local: segmented system TTS plus a procedural two-tone ambient bed.
