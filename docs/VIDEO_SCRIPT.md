# 5-minute submission video outline

**0:00–0:35 — Problem**  
A PR diff is not the system. Senior reviewers lose time tracing callers, consumers, persisted data,
configuration and failure paths to answer: *what else did this change break?*

**0:35–1:05 — Baseline**  
Show one fixed benchmark case and the single-agent baseline. Explain that baseline and final use the
same model, same tools and same inputs.

**1:05–2:35 — One end-to-end DiffRadius execution**  
Show Impact Scout traversing beyond the diff, Adversarial Reviewer proposing a concrete counterexample,
and Evidence Verifier reopening files and rejecting/accepting claims. End on the usable release report.

**2:35–3:35 — Evidence**  
Show the 14-case benchmark, negative controls, hard case, F1/recall/precision/perfect-case rate, runtime
and token usage. Do not cherry-pick; show complete baseline and final results.

**3:35–4:25 — Improvement changelog**  
Show which stage contributed most and one stage/idea that was removed or revised because evidence did
not justify it.

**4:25–5:00 — Hot take + reproducibility**  
State the observed failure mode, the lesson for reliable agents, then show the clean-install commands
and trajectory artifacts.
