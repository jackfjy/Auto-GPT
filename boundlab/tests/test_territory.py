from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from boundlab.errors import TerritoryError
from boundlab.territory import load_territories


def test_rejects_overlapping_owns(tmp_path: Path) -> None:
    path = tmp_path / "territories.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "agents": {
                    "a": {"owns": ["workspace/x/**"]},
                    "b": {"owns": ["workspace/x/**"]},
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(TerritoryError, match="owned by both"):
        load_territories(path)


def test_project_territories_load() -> None:
    mapping = load_territories()
    assert "researcher" in mapping.agents
    assert "writer" in mapping.agents
    owns = [pattern for agent in mapping.agents.values() for pattern in agent.owns]
    assert len(owns) == len(set(owns))
