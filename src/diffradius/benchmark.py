from __future__ import annotations

import difflib
import importlib.util
import inspect
import runpy
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import RiskCategory
from .repository import RepositoryView
from .scoring import ExpectedRisk


@dataclass(frozen=True)
class MaterializedCase:
    id: str
    title: str
    ticket: str
    repo: Path
    oracle: Path
    diff: str
    expected: tuple[ExpectedRisk, ...]
    hard: bool


def _load_cases_module():
    root = Path(__file__).resolve().parents[2]
    path = root / "benchmarks" / "cases.py"
    inserted = str(root) not in sys.path
    if inserted:
        sys.path.insert(0, str(root))
    try:
        spec = importlib.util.spec_from_file_location("diffradius_benchmark_cases", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load benchmark cases")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted:
            sys.path.remove(str(root))


def all_cases():
    return _load_cases_module().CASES


def get_case(case_id: str):
    for case in all_cases():
        if case.id == case_id:
            return case
    raise KeyError(case_id)


def make_diff(before: dict[str, str], after: dict[str, str]) -> str:
    chunks: list[str] = []
    for path in sorted(set(before) | set(after)):
        a = before.get(path, "").splitlines(keepends=True)
        b = after.get(path, "").splitlines(keepends=True)
        chunks.extend(
            difflib.unified_diff(a, b, fromfile=f"a/{path}", tofile=f"b/{path}", lineterm="")
        )
    return "\n".join(chunks)


def materialize(case_id: str, root: Path) -> MaterializedCase:
    case = get_case(case_id)
    repo = root / case.id / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    for rel, content in case.after.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    oracle = root / case.id / "oracle_test.py"
    oracle.parent.mkdir(parents=True, exist_ok=True)
    oracle.write_text(case.oracle, encoding="utf-8")
    diff = make_diff(case.before, case.after)
    expected = tuple(
        ExpectedRisk(RiskCategory(spec.category), spec.paths) for spec in case.expected
    )
    return MaterializedCase(case.id, case.title, case.ticket, repo, oracle, diff, expected, case.hard)


def repository_view(case: MaterializedCase) -> RepositoryView:
    return RepositoryView(case.repo, case.diff, case.ticket)


@dataclass(frozen=True)
class ExecResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def _clear_case_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


def _with_repo_path(repo: Path):
    class _PathContext:
        def __enter__(self):
            _clear_case_modules()
            sys.path.insert(0, str(repo))
        def __exit__(self, exc_type, exc, tb):
            try:
                sys.path.remove(str(repo))
            except ValueError:
                pass
            _clear_case_modules()
    return _PathContext()


def run_visible_tests(case: MaterializedCase) -> ExecResult:
    try:
        with _with_repo_path(case.repo):
            ns = runpy.run_path(str(case.repo / "tests/test_visible.py"))
            for name, fn in sorted(ns.items()):
                if not (name.startswith("test_") and callable(fn)):
                    continue
                params = inspect.signature(fn).parameters
                if not params:
                    fn()
                elif list(params) == ["tmp_path"]:
                    with tempfile.TemporaryDirectory() as d:
                        fn(Path(d))
                else:
                    raise RuntimeError(
                        f"Unsupported visible-test fixture signature: {name}{inspect.signature(fn)}"
                    )
        return ExecResult(0)
    except Exception:
        return ExecResult(1, stderr=traceback.format_exc())


def run_oracle(case: MaterializedCase) -> ExecResult:
    try:
        with _with_repo_path(case.repo):
            code = case.oracle.read_text(encoding="utf-8")
            exec(compile(code, str(case.oracle), "exec"), {"__name__": "__main__"})
        return ExecResult(0)
    except Exception:
        return ExecResult(1, stderr=traceback.format_exc())
