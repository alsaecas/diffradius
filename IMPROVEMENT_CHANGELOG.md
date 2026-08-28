# Improvement Changelog

This is an experiment log, not marketing copy. Quality results remain **pending** until the frozen
benchmark is run with the live model.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | One general-purpose reviewer with the same model and repository tools. No explicit impact-radius recipe. | Pending live run. Deterministic harness validated. | Fair starting point. |
| Iteration 1 — `impact` | Force a separate Impact Scout to map changed contracts and dependants before ordinary synthesis. | Pending live run. | Keep only if F1 gain justifies the second model stage. |
| Iteration 2 — `adversarial` | Add a specialist that tries to turn hypotheses into realistic counterexamples before synthesis. | Pending live run. | Keep/revise/remove from its incremental delta. |
| Iteration 3 — `final` | Replace ordinary final synthesis with an independent Evidence Verifier that re-opens repository evidence and rejects weak claims. | Pending live run. | Expected to improve precision; verify rather than assume. |
| Final architecture | Keep only stages whose measured contribution is worth their runtime/cost. | Pending live run. | Architecture is deliberately not frozen yet. |

## Experiment-design changes already kept

### Added negative controls

A benchmark containing only broken changes rewards an agent for always predicting risk. Safe controls
were added so false positives reduce precision and prevent a perfect-case score.

### Tightened the perfect-case definition

Finding every expected risk is not enough. A case is perfect only when it also contains **zero extra
false-positive findings**. This prevents noisy reviews from looking deceptively successful.

### Added safe-case and regression-case outcome metrics

F1 remains primary, but it can be hard to explain in a five-minute demo. The evaluator now also reports
how many broken PRs produced at least one true finding and how many safe controls remained warning-free.
These metrics do not replace F1; they make its precision/recall tradeoff visible. **Keep.**

### Added before/after oracle validation

Originally the harness checked only that visible tests passed after the change and the held-out oracle
failed. That was not strong enough: an oracle itself could encode a pre-existing failure. The harness
now requires every regression oracle to pass on the **before** implementation and fail on the **after**
implementation, while visible tests pass on both. Several fixtures had to be corrected after this check
exposed weak ground truth. **Keep.**

### Added multi-risk and indirect cases

The initial tiny cases risked making a one-shot reviewer unrealistically easy to score. The benchmark
now includes 18 changes, a two-risk authorization/cache change, multiple indirect dependencies, lazy
transaction lifetime behavior, identity-normalization compatibility, and three safe controls. **Keep,
then freeze before the live run.**

### Added benchmark fingerprinting

Every live evaluation records a SHA-256 fingerprint of the complete case definitions. That makes it
obvious that baseline, ablations and final were measured on the same frozen benchmark. **Keep.**

### Added usage/cost and polished reports

Agent quality is not enough if an extra stage costs too much. The harness reports requests, tokens, wall
time and a transparent approximate uncached-token cost. Real reviews render to Markdown rather than
ending as raw model JSON. **Keep.**

### Added readable local trajectories instead of hosted trace dependency

The hackathon requires agent trajectories. The first implementation saved structured JSON. We added a
Markdown renderer and an evidence-freeze step so judges can follow agent inputs, bounded tool calls,
tool responses and structured outputs without needing access to a third-party trace viewer. Private
chain-of-thought is intentionally not part of the artifact. **Keep.**

### Added a web demo but kept the CLI as source of truth

A polished demo helps end-to-end presentation, but a second web-specific evaluator could create drift or
encourage hand-entered metrics. The Vercel site is therefore static and reads the exact frozen
`comparison.json` when evidence exists. Before that, it visibly says results are pending. **Keep as
presentation, not as evaluation logic.**

## Experiment we are explicitly willing to remove

The Adversarial Reviewer is the prime candidate. A specialist agent can easily add latency while merely
paraphrasing the Impact Scout. If `impact -> adversarial` does not produce a meaningful F1/recall gain,
it will be removed and that negative result will stay in this changelog.

## Current failure-mode hypothesis

The likely failure mode of ordinary AI PR review is **premature locality**: once the changed lines look
reasonable, the reviewer stops searching. The second likely failure is the opposite: once prompted to
look for hidden risks, a model may over-generate plausible-sounding warnings. DiffRadius tests a two-part
response: explicit impact traversal for recall, followed by independent evidence verification for
precision.

## Hot take — provisional until trajectories are measured

> Better AI code review may depend less on making the reviewer smarter than on controlling *where it
> looks* and making a second pass prove its accusations.
