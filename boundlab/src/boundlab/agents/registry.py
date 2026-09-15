from __future__ import annotations

from boundlab.agents.base import Agent
from boundlab.agents.coordinator import CoordinatorAgent
from boundlab.agents.researcher import ResearcherAgent
from boundlab.agents.reviewer import ReviewerAgent
from boundlab.agents.writer import WriterAgent

_BUILTIN: dict[str, type[Agent]] = {
    CoordinatorAgent.name: CoordinatorAgent,
    ResearcherAgent.name: ResearcherAgent,
    WriterAgent.name: WriterAgent,
    ReviewerAgent.name: ReviewerAgent,
}


def available() -> dict[str, type[Agent]]:
    return dict(_BUILTIN)


def get(name: str) -> type[Agent]:
    try:
        return _BUILTIN[name]
    except KeyError as exc:
        known = ", ".join(sorted(_BUILTIN))
        raise KeyError(f"unknown agent {name!r}. built-in: {known}") from exc


def register(agent_cls: type[Agent]) -> type[Agent]:
    if not getattr(agent_cls, "name", ""):
        raise ValueError("agent class must set name")
    _BUILTIN[agent_cls.name] = agent_cls
    return agent_cls
