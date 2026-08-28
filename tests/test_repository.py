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
