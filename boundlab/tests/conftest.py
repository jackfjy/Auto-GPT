from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from boundlab.models import TerritoryMap
from boundlab.territory import load_territories


@pytest.fixture
def territory_file(tmp_path: Path) -> Path:
    data = {
        "version": 1,
        "forbidden": ["src/**"],
        "agents": {
            "researcher": {
                "role": "find",
                "owns": ["workspace/researcher/**"],
                "may_read": ["shared/**", "workspace/researcher/**"],
            },
            "writer": {
                "role": "write",
                "owns": ["workspace/writer/**"],
                "may_read": ["shared/**", "workspace/researcher/**", "workspace/writer/**"],
            },
            "reviewer": {
                "role": "review",
                "owns": ["workspace/reviewer/**"],
                "may_read": ["shared/**", "workspace/**"],
            },
            "coordinator": {
                "role": "merge",
                "owns": ["shared/**", "inbox/**"],
                "may_read": ["**"],
            },
        },
    }
    path = tmp_path / "territories.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.fixture
def territories(territory_file: Path) -> TerritoryMap:
    return load_territories(territory_file)
