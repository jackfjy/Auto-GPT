from __future__ import annotations

from boundlab.cli import main


def test_check_denies_cross_write() -> None:
    assert (
        main(
            [
                "check",
                "--agent",
                "writer",
                "--path",
                "workspace/researcher/findings.md",
                "--mode",
                "write",
            ]
        )
        == 2
    )


def test_check_allows_owned_write() -> None:
    assert (
        main(
            [
                "check",
                "--agent",
                "writer",
                "--path",
                "workspace/writer/draft.md",
                "--mode",
                "write",
            ]
        )
        == 0
    )


def test_agents_lists_builtin() -> None:
    assert main(["agents"]) == 0
