from __future__ import annotations

from pathlib import Path

import pytest

from boundlab.errors import BoundaryError
from boundlab.guard import BoundedFS
from boundlab.models import TerritoryMap


def test_writer_cannot_overwrite_researcher(
    tmp_path: Path, territories: TerritoryMap
) -> None:
    researcher = BoundedFS(tmp_path, territories, territories.get("researcher"))
    writer = BoundedFS(tmp_path, territories, territories.get("writer"))
    researcher.write_text("workspace/researcher/findings.md", "mine")

    with pytest.raises(BoundaryError, match="cannot write"):
        writer.write_text("workspace/researcher/findings.md", "stolen")

    assert researcher.read_text("workspace/researcher/findings.md") == "mine"
    assert writer.read_text("workspace/researcher/findings.md") == "mine"


def test_forbidden_paths(tmp_path: Path, territories: TerritoryMap) -> None:
    fs = BoundedFS(tmp_path, territories, territories.get("researcher"))
    with pytest.raises(BoundaryError, match="forbidden"):
        fs.write_text("src/boundlab/guard.py", "nope")


def test_write_creates_owned_file(tmp_path: Path, territories: TerritoryMap) -> None:
    fs = BoundedFS(tmp_path, territories, territories.get("writer"))
    fs.write_text("workspace/writer/draft.md", "ok")
    assert (tmp_path / "workspace/writer/draft.md").read_text(encoding="utf-8") == "ok"
