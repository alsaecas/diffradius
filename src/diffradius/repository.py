from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class RepositoryAccessError(ValueError):
    pass


@dataclass
class RepositoryView:
    root: Path
    diff_text: str
    ticket: str
    max_file_chars: int = 24000
    max_search_results: int = 60
    before_root: Path | None = None
    base_ref: str | None = None

    def __post_init__(self) -> None:
        self.root = self.root.resolve()
        if not self.root.is_dir():
            raise RepositoryAccessError(f"Repository does not exist: {self.root}")
        if self.before_root is not None:
            self.before_root = self.before_root.resolve()
            if not self.before_root.is_dir():
                raise RepositoryAccessError(f"Before repository does not exist: {self.before_root}")

    def _safe_path(self, relative: str, root: Path | None = None) -> Path:
        base = root or self.root
        candidate = (base / relative).resolve()
        try:
            candidate.relative_to(base)
        except ValueError as exc:
            raise RepositoryAccessError("Path escapes repository root") from exc
        return candidate

    @staticmethod
    def _validate_git_path(relative: str) -> str:
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise RepositoryAccessError("Path escapes repository root")
        return path.as_posix()

    def _bounded_lines(self, text: str, start_line: int, end_line: int) -> str:
        if len(text) > self.max_file_chars:
            text = text[: self.max_file_chars] + "\n...[truncated]"
        lines = text.splitlines()
        start = max(1, start_line)
        end = max(start, end_line)
        selected = lines[start - 1 : end]
        return "\n".join(f"{i}: {line}" for i, line in enumerate(selected, start=start))

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
        return self._bounded_lines(text, start_line, end_line)

    def read_before_file(self, path: str, start_line: int = 1, end_line: int = 240) -> str:
        """Read the file as it existed before the supplied change.

        Benchmark runs provide a materialized before tree. Real Git reviews use the
        configured base ref. If the file was newly added, return an explicit marker
        rather than turning absence into an agent/tool failure.
        """
        if self.before_root is not None:
            target = self._safe_path(path, self.before_root)
            if not target.is_file():
                return "[file did not exist before this change]"
            text = target.read_text(encoding="utf-8", errors="replace")
            return self._bounded_lines(text, start_line, end_line)

        if self.base_ref:
            rel = self._validate_git_path(path)
            completed = subprocess.run(
                ["git", "-C", str(self.root), "show", f"{self.base_ref}:{rel}"],
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                return "[file did not exist at the base ref or before-version is unavailable]"
            return self._bounded_lines(completed.stdout, start_line, end_line)

        return "[before-version unavailable for this review]"

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
