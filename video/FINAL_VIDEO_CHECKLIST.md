# Final video checklist

## Artifact

- File: `video/out/diffradius-hackathon-final.mp4`
- Duration: **282.048 seconds (4:42.048)**
- Resolution: **1920 × 1080**
- Frame rate: **30 fps**
- Video: **H.264**, yuv420p
- Audio: **AAC stereo**, 48 kHz
- File size: **20,389,712 bytes (20.4 MB decimal)**
- MP4 SHA-256: `eef0fbc1ad9373628e1697dbbe17fdfa9876017f81534fcb106e10c327ab42ca`
- SRT SHA-256: `78f086cb3b0c561169fcb26e3d6de0315d8ea8b4336a9c82151997b6c49d4164`
- Render command: `cd video && npm install && npm run render`
- Captions: embedded open captions plus `video/out/diffradius-hackathon-final.srt` with 31 cues

## Verification results

- [x] Duration is below the 4:59 absolute maximum.
- [x] Resolution and frame rate match the 1080p/30 target.
- [x] MP4 contains both video and audio streams for the full runtime.
- [x] FFmpeg black-frame scan found no black run of 0.5 seconds or longer.
- [x] Representative frames inspected at ~0:10, ~1:10, ~3:05, ~3:45, and the final card.
- [x] Captions are laptop-readable and remain below primary code/results content.
- [x] Case 15 tool actions and findings match the committed trajectory.
- [x] Frozen results are synced programmatically and fingerprint-guarded.
- [x] Repository tests: **19 passed** under Python 3.12.
- [x] `python scripts/validate_benchmark.py`: **18/18 PASS**, fingerprint matched.
- [x] Demo build: `npm run build` succeeded.
- [x] TypeScript: `npx tsc --noEmit` succeeded.

## Exact evidence sources

- `evidence/results/comparison.json` and `.md` — final metrics, tokens, cost, model, fingerprint.
- `evidence/trajectories/15-multi-risk-access-cache-final.md` — exact tool order, inspected files, findings, run usage.
- `benchmarks/cases_5.py` — case-15 before/after code, visible test and evaluator oracle.
- `src/diffradius/tools.py` — six bounded read-only tool names and capabilities.
- `src/diffradius/agents.py` and `workflow.py` — final one-investigator architecture and historical agents.
- `IMPROVEMENT_CHANGELOG.md` — historical multi-agent F1/cost and engineering conclusions.
- `docs/EVALUATION.md`, `ARCHITECTURE.md`, and `REPRODUCTION.md` — protocol, architecture and exact commands.

## Remaining caveat

The committed narration uses macOS system TTS rather than a recorded human voice. It is complete, synchronized, local, and requires no secret or paid service. The narration script and SRT make a later human-voice replacement straightforward without changing visual timing.
