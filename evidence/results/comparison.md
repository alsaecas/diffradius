# DiffRadius Benchmark Comparison

Primary metric: **SEEDED RISK RECALL**

Seeded risk recall is primary. Safe-case accuracy is the false-alarm control. Strict precision/F1 remain diagnostic because regression cases can contain valid unseeded consequences.

| Stage | Risk recall | Regression cases caught | Safe cases clean | Strict precision* | F1* | Perfect cases* | Time (s) | Tokens | Est. cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| prompt | 0.562 | 60.0% | 100.0% | 0.750 | 0.643 | 55.6% | 40.4 | 14,065 | $0.0055 |
| tool | 0.875 | 86.7% | 100.0% | 0.875 | 0.875 | 83.3% | 118.0 | 72,289 | $0.0216 |
| final | 1.000 | 100.0% | 100.0% | 0.941 | 0.970 | 94.4% | 144.5 | 106,084 | $0.0299 |

_*Strict precision/F1/perfect-case rate treat every unseeded finding as a false positive. They are diagnostics, not the primary metric; safe negative controls measure unsupported findings directly._

## Incremental contribution

- **prompt → tool**: risk recall +0.312, safe-case accuracy +0.000, strict precision +0.125.
- **tool → final**: risk recall +0.125, safe-case accuracy +0.000, strict precision +0.066.
