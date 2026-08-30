# DiffRadius final narration

Target: **4:42**. The committed MP4 uses local Samantha TTS at 155 words/minute, split into the same 31 timed cues as the SRT. The exact cue boundaries live in `src/data/content.json`.

## 0:00–0:20 — Hook

A diff tells you what changed. It does not tell you what broke.

DiffRadius finds the code your diff forgot—callers, state, permissions, caches, and lifecycle boundaries beyond the edited lines.

## 0:20–0:50 — Problem

A locally reasonable pull request can pass its visible tests while breaking an untouched workflow somewhere else in the repository.

Reviewers normally trace consumers, compatibility assumptions, persisted data, configuration, authorization, retries, and transaction lifetimes by hand.

The frozen direct-prompt baseline saw only the ticket and diff. It recovered 56.2 percent of the seeded risks.

## 0:50–1:45 — Case 15 investigation

Here is the benchmark's hardest centerpiece: cache permission scopes to reduce repeated directory calls. The edit looks small.

The final investigator showed the diff, read the ticket, listed the repository, and inspected the visible happy-path test.

Then it left the changed file. In untouched `admin.py`, `replace_scopes` mutates permissions—but has no connection to the new cache.

That proves one independent release risk: after a permission change, cached write access can remain stale and incorrectly survive revocation.

The investigator also read the before-version. A directory timeout previously returned false. The new handler returns true.

That is a second, independent risk: a transient directory outage becomes a fail-open authorization bypass.

## 1:45–2:15 — Agentic workflow

This is not prompting over a diff. One investigator chooses among six bounded, read-only tools and decides where the evidence leads.

It can show the ticket and diff, list files, search text, read current files, and read the before-version when compatibility matters.

The goal is fewer, provable warnings—not more warnings. Every finding must become a concrete counterexample backed by inspected paths.

## 2:15–2:55 — Benchmark

We measured that behavior on eighteen deterministic pull requests: fifteen hidden regressions, three safe controls, and one two-risk case.

For every regression, visible tests pass before and after. The held-out oracle passes before, then fails after the change.

The oracle is evaluator-only during review. Safe controls stay pass-pass, punishing a reviewer that simply generates more alarms.

The ordered case set and scoring rubric were frozen under this SHA-256 fingerprint before the final comparison.

## 2:55–3:30 — Results

The direct prompt reached 56.2 percent seeded-risk recall. Giving a general reviewer repository tools raised that to 87.5 percent.

DiffRadius reached 100 percent seeded-risk recall on this frozen benchmark, while every safe control remained warning-free.

Strict F1 was 0.970. All eighteen final reviews cost 2.99 cents.

Repository access produced the first major gain. Before-state evidence and counterexample discipline closed the remaining gap.

## 3:30–4:05 — Failed experiment

But the most important result was a failure. The original design chained an Impact Scout, Adversarial Reviewer, and Evidence Verifier.

It sounded smarter. Measured on the historical rubric, F1 fell from 0.750 for one tool agent to 0.545.

It also cost roughly four times more. A contract-first swarm still underperformed the single-agent baseline on its audited rubric.

The trajectories showed speculation accumulating and useful compatibility evidence disappearing across structured handoffs.

## 4:05–4:30 — Engineering lesson

In our repository-review experiments, the agent boundary can be the bug. Specialist handoffs behaved like lossy compression.

The winning change was not another agent. It was one investigator with the right evidence boundary and a counterexample requirement.

The result is simpler, cheaper than the swarm, auditable, and reproducible from the committed benchmark and trajectories.

## 4:30–4:42 — End

Clone the repository, install the development package, run pytest, then validate the frozen benchmark.

DiffRadius. Find the code your diff forgot.
