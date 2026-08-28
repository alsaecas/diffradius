# Reproduction guide

Tested target: Python 3.12 on Linux/macOS. Python 3.11+ is supported.

## Clean setup

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

## Run the agent evaluation

Set an OpenAI API key only in your environment:

```bash
export OPENAI_API_KEY='...'
export DIFFRADIUS_MODEL='gpt-5.6-luna'
diffradius evaluate --mode both --output results/benchmark
```

The evaluator writes `baseline.json`, `final.json`, `comparison.json` and representative local
trajectories. Exact runtime and token use vary by model and network conditions and are stored per case.

## Review a real local change

```bash
diffradius review \
  --repo /path/to/repo \
  --base main \
  --head HEAD \
  --ticket "Describe the intended behavior" \
  --output results/review
```

Or provide a prepared diff with `--diff-file`.

## Expected deterministic result

`pytest` and `python scripts/validate_benchmark.py` must pass without an API key. Broken benchmark
cases intentionally have a failing evaluator-only oracle while their visible test suite passes.
