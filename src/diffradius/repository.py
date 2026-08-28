from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path


class RepositoryAccessError(ValueError):
    pass


@dataclass
class RepositoryView:
    root: Path
    diff_text: str
    ticket: str
    max_file_chars: int = 24000
    max_search_results: int = 60

    def __post_init__(self) -> None:
        self.root = self.root.resolve()
        if not self.root.is_dir():
            raise RepositoryAccessError(f"Repository does not exist: {self.root}")

    def _safe_path(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise RepositoryAccessError("Path escapes repository root") from exc
        return candidate

    def list_files(self, pattern: str = "*") -> list[str]:
        files: list[str] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            rel = path.relative_to(self.root).as_posix()
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
                files.append(rel)
        return sorted(files)

    def read_file(self, path: str, start_line: int = 1, end_line: int = 240) -> str:
        target = self._safe_path(path)
        if not target.is_file():
            raise RepositoryAccessError(f"Not a file: {path}")
        text = target.read_text(encoding="utf-8", errors="replace")
        if len(text) > self.max_file_chars:
            text = text[: self.max_file_chars] + "\n...[truncated]"
        lines = text.splitlines()
        start = max(1, start_line)
        end = max(start, end_line)
        selected = lines[start - 1 : end]
        return "\n".join(f"{i}: {line}" for i, line in enumerate(selected, start=start))

    def search_text(self, query: str, glob: str = "*") -> list[str]:
        if not query:
            return []
        hits: list[str] = []
        q = query.lower()
        for rel in self.list_files(glob):
            target = self._safe_path(rel)
            text = target.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if q in line.lower():
                    hits.append(f"{rel}:{lineno}: {line.strip()}")
                    if len(hits) >= self.max_search_results:
                        return hits
        return hits


def git_diff(repo: Path, base: str, head: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "diff", "--no-ext-diff", f"{base}...{head}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RepositoryAccessError(completed.stderr.strip() or "git diff failed")
    return completed.stdout
