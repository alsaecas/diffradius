# Submission video — target 4:40–4:55

## 0:00–0:25 — Hook

**Say:** “A diff tells you what changed. It does not tell you what broke. DiffRadius finds the code your diff forgot.”

Show the homepage hero and immediately switch to the multi-risk cache/authorization case.

## 0:25–0:55 — Problem + baseline

Show the small diff. Explain that all visible tests still pass. Show the direct-prompt result from the frozen comparison: **56.2% seeded-risk recall** across the full benchmark.

**Say:** “The baseline sees only the ticket and diff. That is useful, but hidden consequences often live elsewhere.”

## 0:55–2:05 — One real DiffRadius trajectory

Open `evidence/trajectories/15-multi-risk-access-cache-final.md`. Scroll through:
1. `show_diff`;
2. `list_files`;
3. `read_file(app/admin.py)` — the untouched mutation path;
4. `read_before_file(app/access.py)` — timeout used to fail closed;
5. final output identifying **both** independent risks.

Explain that the agent chooses where to look; no oracle is visible to it.

## 2:05–2:50 — The benchmark proof

Show the 18-case invariant: visible tests PASS before/after, hidden oracle PASS before / FAIL after. Mention 15 regressions + 3 safe controls and fingerprint.

Show the final table:
- prompt: **56.2% recall**;
- tool reviewer: **87.5%**;
- DiffRadius: **100%**;
- safe controls: **100% clean at all stages**;
- final strict F1: **0.970**.

## 2:50–3:55 — The failed experiment (the memorable part)

Show the Improvement Changelog.

**Say:** “My first design was more impressive on a diagram: Impact Scout, Adversarial Reviewer, Evidence Verifier. It was also worse—F1 fell from 0.750 for one tool agent to 0.545, at roughly four times the cost. I tried a contract-first swarm. It still lost information.”

Then show the final one-agent architecture.

**Say:** “The traces suggested the handoffs were lossy compression. So I removed agents instead of adding another one.”

## 3:55–4:25 — Hot take

**Say:** “For repository review, the agent boundary can be the bug. The improvement was not a bigger swarm; it was giving one agent the right evidence boundary and forcing warnings to become concrete before/after counterexamples.”

## 4:25–4:50 — Reproduce

Show `docs/JUDGES.md`, then terminal commands `pytest`, `python scripts/validate_benchmark.py`, and the evaluation command. End on the live demo + GitHub links.

## Recording checklist

- Keep final export under 5:00.
- Use 1080p and a large terminal/editor font.
- Do not scroll through raw JSON; prefer Markdown traces and the web result table.
- Do not say “100% accurate”; say **“100% seeded-risk recall on this frozen 18-case benchmark.”**
- Mention the safe controls so the 100% figure cannot be mistaken for alarm spam.
