# DiffRadius — Hackathon submission draft

## One-line pitch

**DiffRadius finds the code your diff forgot:** an agentic PR investigator that traces the behavioral
impact radius of a change, constructs concrete failure cases, and independently verifies every release-risk
claim against repository evidence.

## Who has the problem?

Senior developers and tech leads deciding whether a pull request is safe to release.

## What bottleneck makes it worth solving?

A diff shows edited lines, not their full behavioral consequences. Reviewers manually jump between
callers, consumers, persisted data, authorization, configuration, caches, retries and lifecycle boundaries.
A locally correct change can therefore pass visible tests and still break an indirect workflow. Ordinary
single-pass AI review can compound the problem by stopping at the changed lines or, when told to be
exhaustive, generating plausible but unsupported warnings.

## Agent solution

DiffRadius separates the workflow into purposeful roles:

- **Impact Scout** maps changed contracts and affected dependants.
- **Adversarial Reviewer** creates concrete counterexamples and looks for missed paths.
- **Evidence Verifier** independently re-opens repository evidence and rejects weak, duplicate or
  pre-existing claims before making the release decision.

Agents are restricted to bounded read-only repository tools. They cannot modify the repository or run
arbitrary project code.

## Baseline and measured improvement

The fair baseline is one general-purpose reviewer using the **same model, ticket, diff, repository and
repository tools**. The fixed 18-case benchmark is run through four modes:

`baseline → impact → adversarial → final`

This exposes the incremental contribution and cost of each design choice. Finding **F1** is primary;
regression-case detection, safe-case accuracy, perfect-case rate, wall time, tokens and estimated cost are
also reported. Final measured values are inserted only from the frozen evaluator artifacts—never by hand.

## Reproducibility

From a clean environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py
export OPENAI_API_KEY='...'
diffradius evaluate --mode all --output results/benchmark
```

The benchmark validator proves every hidden regression passes its oracle before the change and fails it
after the change while visible tests continue to pass. Each live result records a SHA-256 benchmark
fingerprint, model, package versions, complete per-case predictions and resource usage.

## Hot take

**Provisional until the live trajectories are analyzed:** better AI code review may depend less on making
the reviewer smarter than on controlling *where it looks* and making a second pass prove its accusations.

## Links

- Demo: https://diffradius.vercel.app
- Source: https://github.com/alsaecas/diffradius
- Judge quick path: `docs/JUDGES.md`
- Evaluation protocol: `docs/EVALUATION.md`
- Improvement changelog: `IMPROVEMENT_CHANGELOG.md`
