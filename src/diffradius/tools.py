from __future__ import annotations

from dataclasses import dataclass

from agents import RunContextWrapper
from agents.decorators import tool

from .repository import RepositoryView
from .trajectory import TrajectoryRecorder


@dataclass
class ReviewContext:
    repository: RepositoryView
    trajectory: TrajectoryRecorder
    current_agent: str = "unknown"

    def log_tool(self, name: str, args: dict, output: object) -> None:
        preview = str(output)
        if len(preview) > 5000:
            preview = preview[:5000] + "...[truncated]"
        self.trajectory.add("tool", self.current_agent, tool=name, args=args, output=preview)


@tool
def list_files(ctx: RunContextWrapper[ReviewContext], pattern: str = "*") -> list[str]:
    """List repository files. Use a glob such as '*.py' or 'src/*'."""
    out = ctx.context.repository.list_files(pattern)
    ctx.context.log_tool("list_files", {"pattern": pattern}, out)
    return out


@tool
def read_file(
    ctx: RunContextWrapper[ReviewContext], path: str, start_line: int = 1, end_line: int = 240
) -> str:
    """Read a bounded range of a repository file using a repository-relative path."""
    out = ctx.context.repository.read_file(path, start_line, end_line)
    ctx.context.log_tool(
        "read_file", {"path": path, "start_line": start_line, "end_line": end_line}, out
    )
    return out


@tool
def search_text(
    ctx: RunContextWrapper[ReviewContext], query: str, glob: str = "*"
) -> list[str]:
    """Search repository text case-insensitively and return path/line matches."""
    out = ctx.context.repository.search_text(query, glob)
    ctx.context.log_tool("search_text", {"query": query, "glob": glob}, out)
    return out


@tool
def show_diff(ctx: RunContextWrapper[ReviewContext]) -> str:
    """Return the complete supplied change diff."""
    out = ctx.context.repository.diff_text
    ctx.context.log_tool("show_diff", {}, out)
    return out


@tool
def show_ticket(ctx: RunContextWrapper[ReviewContext]) -> str:
    """Return the supplied task/ticket description."""
    out = ctx.context.repository.ticket
    ctx.context.log_tool("show_ticket", {}, out)
    return out


READ_ONLY_TOOLS = [list_files, read_file, search_text, show_diff, show_ticket]
