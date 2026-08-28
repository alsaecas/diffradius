# Hackathon submission checklist

## Complete solution code + Improvement Changelog

- [x] Public runnable repository
- [x] Intended user and bottleneck explained
- [x] Agent instructions committed
- [x] Fair single-agent baseline
- [x] Explicit ablation modes
- [x] Improvement Changelog with removed/revisable experiment policy
- [x] 18-case frozen benchmark with before/after oracle integrity
- [x] Safe negative controls and multi-risk/hard cases
- [x] Judge-facing web demo that reads frozen evidence rather than hand-entered metrics
- [ ] Replace pending evidence with final measured results
- [ ] Freeze final architecture after ablation
- [ ] Replace provisional hot take with trajectory-backed insight

## Reproduction guide

- [x] Clean-environment setup commands
- [x] Exact baseline/final/ablation evaluation commands
- [x] Deterministic benchmark validation
- [x] Core agent SDK pinned
- [x] Runtime/token/cost collection
- [x] Manual GitHub Actions benchmark workflow + artifact
- [x] Evidence-freeze script validates fingerprint/case set
- [ ] Commit final benchmark evidence artifacts
- [ ] Confirm reproduction once from a fresh clone after final freeze

## Solution video — maximum 5 minutes

- [x] Script/shot outline prepared
- [ ] Record final video after benchmark freeze
- [ ] Show problem + baseline first
- [ ] Show one realistic end-to-end execution
- [ ] Show complete measured comparison
- [ ] Show most valuable change and one removed/revised experiment
- [ ] Keep final export ≤5:00

## Agent trajectories

- [x] Local trajectory recorder implemented
- [x] Inputs, tool calls, outputs and usage captured
- [x] JSON trajectories render to judge-friendly Markdown
- [x] Evidence freezer selects representative baseline/final hard-case traces
- [ ] Confirm representative traces cover every submitted agent role
- [ ] Include a natural retry/failure/human checkpoint if one occurs; do not fabricate one
- [ ] Verify selected trajectories contain only synthetic/shareable data
