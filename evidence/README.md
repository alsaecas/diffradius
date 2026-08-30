# Frozen evaluation evidence

Generated from final GitHub Action run [`33303502804`](https://github.com/alsaecas/diffradius/actions/runs/33303502804).

Benchmark fingerprint: `87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`  
Model: `gpt-5.6-luna`  
Cases: **18**

Values in this folder are copied from one complete frozen evaluation matrix; they are not hand-entered.

## Measured comparison

| Stage | Risk recall | Regression cases caught | Safe cases clean | Strict precision | Strict F1 | Tokens | Est. cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| prompt | 56.2% | 60.0% | 100.0% | 75.0% | 0.643 | 14,065 | $0.0055 |
| tool | 87.5% | 86.7% | 100.0% | 87.5% | 0.875 | 72,289 | $0.0216 |
| **final** | **100.0%** | **100.0%** | **100.0%** | **94.1%** | **0.970** | 106,084 | $0.0299 |

## Representative trajectory

Start with [`trajectories/15-multi-risk-access-cache-final.md`](trajectories/15-multi-risk-access-cache-final.md). It shows the submitted `DiffRadius Evidence Investigator` leaving the changed file, inspecting the untouched permission mutation path, reading the before-version of the authorization check, and independently identifying both seeded risks.

The Markdown trace exposes explicit input, bounded tool calls/responses, structured output, and usage. It deliberately does **not** expose private chain-of-thought.

## Complete raw matrix

The final Action artifact contains `prompt.json`, `tool.json`, `final.json`, every per-case trajectory, `comparison.json`, and `comparison.md`:

https://github.com/alsaecas/diffradius/actions/runs/33303502804

The committed [`results/comparison.json`](results/comparison.json) is also the source consumed by the Vercel demo.
