from pathlib import Path

import pytest

from diffradius.repository import RepositoryAccessError, RepositoryView


def test_repository_blocks_path_escape(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    view = RepositoryView(repo, "", "")
    with pytest.raises(RepositoryAccessError):
        view.read_file("../secret.txt")


def test_search_and_bounded_read(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text("one\ntarget\nthree\n", encoding="utf-8")
    view = RepositoryView(repo, "", "")
    assert view.search_text("TARGET") == ["a.py:2: target"]
    assert view.read_file("a.py", 2, 2) == "2: target"


def test_reads_materialized_before_version(tmp_path: Path):
    before = tmp_path / "before"
    after = tmp_path / "after"
    before.mkdir()
    after.mkdir()
    (before / "a.py").write_text("old\n", encoding="utf-8")
    (after / "a.py").write_text("new\n", encoding="utf-8")
    view = RepositoryView(after, "", "", before_root=before)
    assert view.read_file("a.py") == "1: new"
    assert view.read_before_file("a.py") == "1: old"
    assert view.read_before_file("new.py") == "[file did not exist before this change]"
