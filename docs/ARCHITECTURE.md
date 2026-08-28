# Architecture

DiffRadius investigates the *impact radius* of a code change instead of treating the diff as the whole system.

```text
Ticket + diff + repository
        |
        v
  Impact Scout
  - changed contracts
  - dependants
  - candidate risks
        |
        v
Adversarial Reviewer
  - attempts counterexamples
  - looks for missed paths
  - refines hypotheses
        |
        v
 Evidence Verifier
  - independently re-opens evidence
  - rejects unsupported claims
  - emits final release report
```

All agents receive the same bounded, read-only repository tools: file listing, bounded file reads,
text search, ticket access and diff access. The evaluator's ground truth is outside that repository.

## Why three stages?

The architecture is a hypothesis, not a predetermined conclusion. The benchmark compares it with a
single-agent baseline using the same model, same task cases and same repository tools. If the extra
stages do not improve F1 enough to justify their cost and latency, they should be removed.

## Safety and privacy

- Repository tools are read-only.
- Paths are resolved and checked against the repository root.
- Hosted Agents SDK tracing is disabled by default.
- Local trajectories intentionally log tool inputs/outputs for reproducibility; only run against code
  you are allowed to include in those artifacts.
- No credentials are written to results.
