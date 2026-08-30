# Improvement Changelog

This is the experiment log that selected the final architecture. Failed approaches are intentionally kept.

## Final selection

Final frozen run: **56.2% direct-prompt recall → 87.5% general tool recall → 100% DiffRadius recall**, with **100% safe-case accuracy at every stage**. DiffRadius reached strict F1 **0.970** at an estimated **$0.0299** across all 18 cases.

The main lesson was the opposite of the initial architecture assumption: **more agent roles did not make the review better**. Specialization created context loss and additional speculative surface area. The winning design collapsed the workflow into one evidence-seeking agent and invested complexity in tools and verification discipline instead.

## Experiment history

| Experiment | Intervention | Measured outcome | Decision |
|---|---|---|---|
| Direct prompt | Same model; ticket + diff only; no repository tools. | 56.2% seeded-risk recall; 100% safe-case accuracy; strict F1 0.643; $0.0055 / 18 cases. | Keep as the simple baseline. |
| Strong tool comparator | One general reviewer + five bounded current-repository tools. | 87.5% recall; 100% safe-case accuracy; strict F1 0.875; $0.0216 / 18 cases. | Keep as strong comparator; isolates repo access. |
| Multi-agent v1 | Impact Scout → Adversarial Reviewer → Evidence Verifier. | F1 **0.545** vs one-agent tool baseline **0.750**; ~$0.094 vs ~$0.023. | Reject. More stages amplified speculation and lost true risks. |
| Contract-first multi-agent v2 | Change Contract Analyst → Impact Investigator → verifier/synthesis variants, plus before-state evidence. | Best multi-agent recall **0.750** while the one-agent tool baseline reached **1.000** recall on that audited rubric. | Reject swarm; keep before-state capability. |
| Selected v3 | One evidence investigator + current-repo tools + `read_before_file` + explicit counterexample discipline. | **100% recall**, **100% regression-case detection**, **100% safe-case accuracy**, strict F1 **0.970**; $0.0299 / 18 cases. | **Selected final architecture.** |

Historical Action runs are preserved:
- Multi-agent v1: https://github.com/alsaecas/diffradius/actions/runs/33298664170
- Contract-first v2: https://github.com/alsaecas/diffradius/actions/runs/33301477629
- Single-agent candidate: https://github.com/alsaecas/diffradius/actions/runs/33303076070
- Final frozen run: https://github.com/alsaecas/diffradius/actions/runs/33303502804

## What the first failed run revealed

The original Scout/Adversary pipeline improved breadth but generated too many plausible hypotheses. The verifier then became conservative enough to discard real compatibility risks. More calls cost about four times as much while reducing measured quality.

**Decision:** do not add another agent to fix an agent-handoff problem.

## What the second failed run revealed

We added explicit contract reconstruction and a before-version tool. The before-state idea was useful, but splitting it across agents still lost information between structured handoffs.

**Decision:** separate the useful capability from the orchestration. Keep before-state evidence; remove the multi-agent chain.

## Evaluation-method audit

The first scorer required an exact category + evidence-path match and counted every unseeded finding as a false positive. Inspecting trajectories exposed two issues:

1. a model could describe the correct concrete failure under a different defensible category;
2. a broken PR can contain an additional real consequence that the synthetic seed did not enumerate.

Before the final frozen run, the rubric was made explicit:

- each seeded risk has a canonical category and, only where genuinely ambiguous, declared equivalent categories;
- evidence must still touch an expected affected path;
- **seeded risk recall** is primary;
- **safe-case accuracy** is the false-alarm control;
- strict precision/F1 remain visible diagnostics.

Every rubric revision changed the benchmark fingerprint and forced all compared modes to rerun from scratch on the same ordered 18 cases. The final run uses fingerprint `87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`. No benchmark content or scoring rule was edited after that freeze.

## Benchmark-integrity improvements kept

- Three safe negative controls.
- Perfect-case scoring requires all expected risks and zero extra findings.
- Two-risk authorization/cache case and multiple indirect cases.
- Before/after oracle validation: regression oracles pass before and fail after.
- SHA-256 benchmark fingerprinting.
- Token, request, wall-time, and approximate cost reporting.
- Local JSON trajectories plus judge-friendly Markdown rendering.
- Evidence freezer that refuses mixed models, fingerprints, or ordered case sets.
- Vercel demo as presentation only; CLI/evidence remain the source of truth.

## Removed experiment

**Adversarial Reviewer — removed from the submitted final architecture.**

It sounded useful, but across both swarm experiments it did not justify its latency/cost and frequently expanded the hypothesis set without improving final recall. The historical code/run evidence is retained to make this decision auditable.

## Main failure mode

The project started with the hypothesis that AI review fails mainly through **premature locality**: the changed lines look reasonable, so the reviewer stops searching.

The experiments found a second, more important failure mode:

> **Agent handoffs can become lossy compression.**

A specialist may discover useful nuance, but once it is compressed into a schema and handed to another model, later stages can inherit the abstraction instead of the evidence. More agents can therefore reduce both recall and efficiency.

## Hot take

> **For repository review, the agent boundary can be the bug. The winning improvement was not adding a smarter reviewer or a bigger swarm; it was giving one agent the right evidence tools and forcing every warning to cash out as a concrete before/after counterexample.**
