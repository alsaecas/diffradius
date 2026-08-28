# Reproduction guide

Target environment: Python 3.12 on Linux/macOS. Python 3.11+ is supported.

## 1. Clean setup

```bash
git clone https://github.com/alsaecas/diffradius.git
cd diffradius
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py
```

The last two commands require no API key. Validation should show every regression with
`oracle(before/after)=PASS/FAIL` and every safe control with `PASS/PASS`.

The web demo has no runtime dependencies and can be built separately with:

```bash
npm run build
```

## 2. Run the complete agent experiment

Set the key only in your shell/environment:

```bash
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode all --output results/benchmark
```

Expected artifacts:

```text
results/benchmark/
  baseline.json
  impact.json
  adversarial.json
  final.json
  comparison.json
  comparison.md
  trajectories/
    baseline/*.json
    impact/*.json
    adversarial/*.json
    final/*.json
```

Each mode file includes the benchmark fingerprint, complete per-case predictions, deterministic scores,
and usage. `comparison.md` is the human-readable experiment summary.

## 3. Freeze judge-facing evidence

```bash
python scripts/freeze_evidence.py --results results/benchmark --evidence evidence
```

This copies the measured result matrix and representative baseline/final traces into `evidence/` and
renders those JSON trajectories to Markdown. The script validates that every stage used the same case set
and benchmark fingerprint first.

## 4. Review a real local change

```bash
diffradius review \
  --repo /path/to/repo \
  --base main \
  --head HEAD \
  --ticket "Describe the intended behavior" \
  --output results/review
```

Expected artifacts are `review.md`, `review.json`, and a local trajectory. You can instead provide a
prepared unified diff with `--diff-file`.

Render any trajectory for a human reviewer with:

```bash
diffradius trajectory \
  --input results/review/trajectories/<run>.json \
  --output results/review/trajectory.md
```

## 5. GitHub Actions option

The **Agent benchmark** workflow performs the same integrity checks and full ablation matrix in a clean
GitHub runner and uploads both `results/benchmark` and `evidence` as a downloadable artifact.

Before using it, add `OPENAI_API_KEY` as an **Actions repository secret**. Never commit the key or paste it
into benchmark inputs.

## Runtime and cost

Exact runtime and model usage depend on the selected model. The evaluator records both. For known
GPT-5.6 aliases, estimated cost uses the public uncached input/output token prices captured in
`src/diffradius/pricing.py`; it is an approximation rather than a billing statement.
