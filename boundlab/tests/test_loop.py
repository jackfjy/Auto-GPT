from __future__ import annotations

from pathlib import Path

from boundlab.bus import MessageBus
from boundlab.context import Context
from boundlab.guard import BoundedFS
from boundlab.llm.echo import EchoBrain
from boundlab.llm.base import Decision
from boundlab.loop import ToolLoopAgent
from boundlab.memory import Memory
from boundlab.models import TerritoryMap


def test_tool_loop_writes_only_owned_path(tmp_path: Path, territories: TerritoryMap) -> None:
    agent = ToolLoopAgent(
        brain=EchoBrain(
            [
                Decision(
                    tool="write_file",
                    arguments={
                        "path": "workspace/researcher/note.md",
                        "content": "from loop",
                    },
                ),
                Decision(tool="finish", arguments={"summary": "ok"}),
            ]
        )
    )
    agent.name = "researcher"
    ctx = Context(
        goal="loop",
        agent_name="researcher",
        fs=BoundedFS(tmp_path, territories, territories.get("researcher")),
        bus=MessageBus(),
        memory=Memory(),
    )
    result = agent.run(ctx)
    assert result.summary == "ok"
    assert (tmp_path / "workspace/researcher/note.md").read_text(encoding="utf-8") == "from loop"
