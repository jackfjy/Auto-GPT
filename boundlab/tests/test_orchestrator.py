from __future__ import annotations

from pathlib import Path

from boundlab.models import TerritoryMap
from boundlab.orchestrator import Orchestrator


def test_serial_pipeline_writes_separate_files(
    tmp_path: Path, territories: TerritoryMap
) -> None:
    orch = Orchestrator(root=tmp_path / "run", territories=territories)
    report = orch.run("避免并行覆盖", agents=["researcher", "writer", "reviewer", "coordinator"])
    assert not report.errors
    root = tmp_path / "run"
    assert (root / "workspace/researcher/findings.md").is_file()
    assert (root / "workspace/writer/draft.md").is_file()
    assert (root / "workspace/reviewer/review.md").is_file()
    assert (root / "shared/report.md").is_file()


def test_parallel_workers_do_not_share_write_paths(
    tmp_path: Path, territories: TerritoryMap
) -> None:
    orch = Orchestrator(root=tmp_path / "run", territories=territories)
    report = orch.run("并行", agents=["researcher", "reviewer"], parallel=True)
    assert not report.errors
    assert (tmp_path / "run/workspace/researcher/findings.md").is_file()
    assert (tmp_path / "run/workspace/reviewer/review.md").is_file()
    assert not (tmp_path / "run/workspace/researcher/review.md").exists()
