from __future__ import annotations

from pathlib import Path

import pytest

from boundlab.paths import match_glob, normalize_rel, resolve_inside


def test_normalize_rejects_parent_and_absolute() -> None:
    with pytest.raises(ValueError):
        normalize_rel("../secret")
    with pytest.raises(ValueError):
        normalize_rel("/etc/passwd")


def test_glob_directory_ownership() -> None:
    assert match_glob("workspace/researcher/findings.md", "workspace/researcher/**")
    assert not match_glob("workspace/writer/draft.md", "workspace/researcher/**")


def test_resolve_stays_inside(tmp_path: Path) -> None:
    inside = resolve_inside(tmp_path, "workspace/a.md")
    assert inside.is_relative_to(tmp_path.resolve())
