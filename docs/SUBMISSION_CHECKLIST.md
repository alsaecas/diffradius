# Final hackathon submission checklist

## Repository and evidence
- [x] Public runnable repository
- [x] Intended user/problem explained
- [x] Direct-prompt baseline
- [x] Strong tool comparator
- [x] Selected final agent architecture
- [x] 18-case benchmark: 15 regressions + 3 safe controls
- [x] Before/after oracle integrity
- [x] Frozen final result matrix
- [x] Benchmark fingerprint
- [x] Token/time/cost reporting
- [x] Failed experiments preserved
- [x] Representative readable trajectories
- [x] Reproduction guide
- [x] Vercel demo

## Manual tasks before pressing Submit
- [ ] Record video using `docs/VIDEO_SCRIPT.md` (≤5:00)
- [ ] Upload the video and make it accessible to judges
- [ ] Put the video URL in the HackerEarth project form
- [ ] Paste/adapt `SUBMISSION.md` into the project description fields
- [ ] Add demo URL: https://diffradius.vercel.app
- [ ] Add source URL: https://github.com/alsaecas/diffradius
- [ ] Confirm the HackerEarth draft shows correctly
- [ ] Open video, demo, and GitHub once in an incognito/private window
- [ ] Submit before the deadline

## Exact evidence identifiers
- Final Action run: https://github.com/alsaecas/diffradius/actions/runs/33303502804
- Model: `gpt-5.6-luna`
- Cases: 18
- Benchmark fingerprint: `87c7f191a64e9beb1e55d32ddfa3b67782028aca75720203a4471ba31fad5889`
- Final seeded-risk recall: 100%
- Final safe-case accuracy: 100%
- Final strict F1: 0.970
