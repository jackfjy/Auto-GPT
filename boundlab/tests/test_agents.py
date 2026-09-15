from __future__ import annotations

from pathlib import Path

from boundlab.agents.researcher import ResearcherAgent
from boundlab.bus import MessageBus
from boundlab.context import Context
from boundlab.errors import BoundaryError
from boundlab.guard import BoundedFS
from boundlab.memory import Memory
from boundlab.models import TerritoryMap
import pytest


def _ctx(tmp_path: Path, territories: TerritoryMap, name: str, goal: str = "demo") -> Context:
    return Context(
        goal=goal,
        agent_name=name,
        fs=BoundedFS(tmp_path, territories, territories.get(name)),
        bus=MessageBus(),
        memory=Memory(),
    )


def test_researcher_stays_in_lane(tmp_path: Path, territories: TerritoryMap) -> None:
    ctx = _ctx(tmp_path, territories, "researcher")
    result = ResearcherAgent().run(ctx)
    assert result.artifacts == ["workspace/researcher/findings.md"]


def test_writer_cannot_use_researcher_path(tmp_path: Path, territories: TerritoryMap) -> None:
    ctx = _ctx(tmp_path, territories, "writer")
    with pytest.raises(BoundaryError):
        ctx.write("workspace/researcher/findings.md", "no")
