# Architecture

## Selected production architecture

```text
Ticket + diff + changed repository
        |
        v
DiffRadius Evidence Investigator
        |
        +-- list/search/read current repository
        +-- inspect the before-version when compatibility matters
        +-- follow direct and indirect dependants
        +-- construct/falsify concrete counterexamples
        |
        v
Evidence-backed release-risk report
```

The final system uses **one agent** with bounded, read-only tools. This is not a simplification made for presentation; it is the architecture selected after two multi-agent designs underperformed.

## Six tools

The agent can read the supplied ticket and diff, list repository files, search text, read bounded current-file ranges, and read bounded ranges from the before-version. Path traversal is blocked. The agent cannot modify the target or execute arbitrary repository code.

## Why before-state evidence matters

Repository regressions are about change. A current snapshot can prove a caller exists, but backward-compatibility failures often need evidence that a behavior or input worked before. `read_before_file` makes that evidence directly inspectable instead of asking another agent to summarize history.

## Why not a swarm?

The first `Scout → Adversary → Verifier` experiment lost true findings while increasing cost. A contract-first multi-agent redesign also lost information. Trajectories showed that specialist handoffs compressed nuanced evidence into schemas and later agents inherited the abstraction.

The selected design moves complexity from orchestration into the **evidence boundary**.

## Trajectories and safety

Local traces record explicit inputs, tool calls, bounded tool responses, structured outputs and usage. They deliberately exclude private chain-of-thought. Hosted tracing is disabled by default.
