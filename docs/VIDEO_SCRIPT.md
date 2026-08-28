# Submission video — ≤5 minute outline

## 0:00–0:35 — Problem

A PR diff is not the system. Senior reviewers repeatedly trace callers, consumers, persisted data,
configuration and lifetime assumptions to answer one question: **what else did this change break?**

## 0:35–1:05 — Fair baseline

Show one fixed hard benchmark case and the single-agent baseline. Explain that every experiment gets the
same model, repository tools, ticket and diff; only the workflow changes.

## 1:05–2:25 — One end-to-end DiffRadius execution

Show Impact Scout leaving the diff, Adversarial Reviewer constructing a concrete counterexample, and
Evidence Verifier independently reopening the relevant files. Finish on `review.md`, not raw JSON.

## 2:25–3:25 — Evidence

Show the 18-case benchmark and the before/after oracle invariant. Then show `comparison.md`: F1, recall,
precision, perfect-case rate, time, tokens and estimated cost for baseline → impact → adversarial → final.
Do not cherry-pick a case; show the complete aggregate result.

## 3:25–4:15 — Improvement changelog

Show the measured stage deltas. Name the component that contributed most and explicitly show one
experiment that was removed/revised—or, if every component survived, the weakest stage and why its gain
still justified the cost.

## 4:15–4:45 — Failure mode / hot take

Use an actual trajectory failure to state the lesson. Current hypothesis: AI review fails first through
**premature locality**, then through speculative warnings when told to search more broadly. Impact mapping
attacks the first; evidence verification attacks the second.

## 4:45–5:00 — Reproduce

Show the clean install, deterministic benchmark validation, one evaluation command, benchmark fingerprint,
and trajectory directory.
