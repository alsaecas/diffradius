# Improvement Changelog

This file is an experiment log, not marketing copy. Results remain **pending** until measured on the
fixed benchmark.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | One competent review agent with the same repository tools as the final workflow. | Pending fixed-benchmark run. | Establish the fair starting point. |
| Iteration 1 | Add an Impact Scout that traces behavioral contracts and dependants before reviewing. | Pending. | Keep only if recall/F1 improves enough to justify added cost. |
| Iteration 2 | Add an adversarial pass that tries to express concrete hidden-test counterexamples. | Pending. | Keep, revise, or remove based on measured contribution. |
| Iteration 3 | Add independent evidence verification to reject unsupported or duplicate claims. | Pending. | Expected to trade some recall for materially better precision; verify empirically. |
| Final | Combine only the stages that survive the ablation/evaluation. | Pending. | Architecture is not frozen yet. |

## Experiments we expect may fail

A separate specialist agent can easily add latency while echoing the same reasoning. If it does not
produce a measurable gain, it will be removed and documented here. The hackathon rewards purposeful
components, not agent count.

## Current main failure-mode hypothesis

The likely failure mode of ordinary AI PR review is **premature locality**: once the changed lines look
reasonable, the model stops searching. DiffRadius tests whether forcing explicit impact traversal and
then independent verification improves real-risk detection without turning the reviewer into a noisy
lint bot.

## Hot take (provisional)

> Better AI code review may depend less on making the reviewer smarter than on forcing it to leave the
> diff, trace the behavioral contract, and prove its own accusations.

This wording will be revised after trajectories show what actually failed.
