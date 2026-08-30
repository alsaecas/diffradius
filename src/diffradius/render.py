from __future__ import annotations

from .models import ReviewReport, RunUsage


def _decision_label(decision: str) -> str:
    return {
        "approve": "APPROVE",
        "needs_review": "NEEDS REVIEW",
        "block": "BLOCK RELEASE",
    }.get(decision, decision.upper())


def render_review(report: ReviewReport, usage: RunUsage) -> str:
    lines = [
        "# DiffRadius Release Risk Report",
        "",
        f"**Decision:** {_decision_label(report.decision)}",
        "",
        report.summary.strip(),
        "",
        "## Verified findings",
        "",
    ]
    if not report.findings:
        lines.extend(["No verified release risks were found.", ""])
    for index, finding in enumerate(report.findings, start=1):
        lines.extend(
            [
                f"### {index}. {finding.title}",
                "",
                f"- **Severity:** {finding.severity.upper()}",
                f"- **Category:** `{finding.category.value}`",
                f"- **Confidence:** {finding.confidence:.0%}",
                f"- **Failure mode:** {finding.failure_mode}",
                f"- **Recommended test:** {finding.recommended_test}",
                "",
                "**Evidence**",
                "",
            ]
        )
        for evidence in finding.evidence:
            location = f" ({evidence.line_hint})" if evidence.line_hint else ""
            lines.append(f"- `{evidence.path}`{location} — {evidence.explanation}")
        lines.append("")

    if report.rejected_findings:
        lines.extend(["## Rejected hypotheses", ""])
        for rejected in report.rejected_findings:
            lines.append(f"- **{rejected.title}** (`{rejected.category.value}`) — {rejected.reason}")
        lines.append("")

    cost = "unknown" if usage.estimated_cost_usd is None else f"${usage.estimated_cost_usd:.4f}"
    lines.extend(
        [
            "## Run facts",
            "",
            f"- Model requests: {usage.requests}",
            f"- Tokens: {usage.total_tokens:,} ({usage.input_tokens:,} input / {usage.output_tokens:,} output)",
            f"- Wall-clock agent time: {usage.elapsed_seconds:.2f}s",
            f"- Approximate model cost: {cost}",
            "",
            "_Cost is an uncached-token estimate for known GPT-5.6 model aliases and may differ from billing._",
            "",
        ]
    )
    return "\n".join(lines)


def render_comparison(comparison: dict) -> str:
    lines = [
        "# DiffRadius Benchmark Comparison",
        "",
        "Primary metric: **SEEDED RISK RECALL**",
        "",
        comparison.get("metric_note", ""),
        "",
        "| Stage | Risk recall | Regression cases caught | Safe cases clean | Strict precision* | F1* | Perfect cases* | Time (s) | Tokens | Est. cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for stage, values in comparison["stages"].items():
        cost = "—" if values["estimated_cost_usd"] is None else f"${values['estimated_cost_usd']:.4f}"
        lines.append(
            f"| {stage} | {values['recall']:.3f} | {values['regression_case_detection_rate']:.1%} | "
            f"{values['safe_case_accuracy']:.1%} | {values['precision']:.3f} | {values['f1']:.3f} | "
            f"{values['perfect_case_rate']:.1%} | {values['elapsed_seconds']:.1f} | "
            f"{values['total_tokens']:,} | {cost} |"
        )
    lines.extend(
        [
            "",
            "_*Strict precision/F1/perfect-case rate treat every unseeded finding as a false positive. "
            "They are diagnostics, not the primary metric; safe negative controls measure unsupported "
            "findings directly._",
        ]
    )
    if comparison.get("stage_deltas"):
        lines.extend(["", "## Incremental contribution", ""])
        for delta in comparison["stage_deltas"]:
            lines.append(
                f"- **{delta['from']} → {delta['to']}**: risk recall "
                f"{delta['risk_recall_change']:+.3f}, safe-case accuracy "
                f"{delta['safe_case_accuracy_change']:+.3f}, strict precision "
                f"{delta['strict_precision_change']:+.3f}."
            )
    lines.append("")
    return "\n".join(lines)
