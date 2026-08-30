# Reproduction guide

Target environment: Python 3.12 on Linux/macOS. Python 3.11+ is supported.

## 1. Clean deterministic setup

```bash
git clone https://github.com/alsaecas/diffradius.git
cd diffradius
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest
python scripts/validate_benchmark.py
```

No API key is needed for these checks. The validator should report 18 cases: every regression with `visible(before/after)=PASS/PASS` and `oracle(before/after)=PASS/FAIL`, and every safe control with oracle PASS/PASS.

Expected final benchmark fingerprint:

`87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`

## 2. Run the same live comparison

```bash
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode all --output results/benchmark
```

This runs three modes on the same ordered case set:

- `prompt`: ticket + unified diff only;
- `tool`: one general reviewer with current-repository read/search tools;
- `final`: DiffRadius Evidence Investigator with the same repo access plus before-version evidence and explicit counterexample discipline.

Expected artifacts:

```text
results/benchmark/
  prompt.json
  tool.json
  final.json
  comparison.json
  comparison.md
  trajectories/
```

LLM sampling can vary on rerun; reproducibility means the evaluation task, case set, model configuration, metrics, tool boundary, and artifact path are fully specified.

## 3. Freeze judge-facing evidence

```bash
python scripts/freeze_evidence.py --results results/benchmark --evidence evidence
```

The freezer refuses mismatched models, benchmark fingerprints, case orders, or incomplete matrices. The final committed evidence came from GitHub Action run `33303502804`.

## 4. Review a real local change

```bash
diffradius review \
  --repo /path/to/repo \
  --base main \
  --head HEAD \
  --ticket "Describe the intended behavior" \
  --output results/review
```

DiffRadius does not execute arbitrary target-repository code. Repository tools are read-only and path-bounded.

## 5. Build the judge demo

```bash
npm run build
```

The static site copies the committed frozen evidence into the deployment; it does not maintain a second set of hand-entered metrics.
