from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _fenced(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, indent=2, ensure_ascii=False, default=str)
    return f"```text\n{text}\n```"


def render_trajectory_payload(payload: dict) -> str:
    lines = [
        "# DiffRadius Agent Trajectory",
        "",
        f"**Run ID:** `{payload.get('run_id', 'unknown')}`",
        "",
        "This is a representative execution trace: agent inputs, bounded repository tool calls, tool responses, and structured outputs. It intentionally does not expose private chain-of-thought.",
        "",
    ]
    for index, event in enumerate(payload.get("events", []), start=1):
        kind = event.get("kind", "event")
        agent = event.get("agent", "unknown")
        at = event.get("at", "")
        data = event.get("data", {})
        lines.extend([f"## {index}. {agent} — {kind}", "", f"`{at}`", ""])

        if kind == "tool":
            lines.append(f"**Tool:** `{data.get('tool', 'unknown')}`")
            lines.append("")
            lines.append("**Arguments**")
            lines.append("")
            lines.append(_fenced(data.get("args", {})))
            lines.append("")
            lines.append("**Bounded response**")
            lines.append("")
            lines.append(_fenced(data.get("output", "")))
        elif kind == "agent_input":
            lines.append(_fenced(data.get("input", "")))
        elif kind in {"agent_output", "workflow_result"}:
            lines.append(_fenced(data))
        else:
            lines.append(_fenced(data))
        lines.append("")
    return "\n".join(lines)


def render_trajectory_file(source: Path, destination: Path | None = None) -> str:
    payload = json.loads(source.read_text(encoding="utf-8"))
    markdown = render_trajectory_payload(payload)
    if destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
    return markdown
