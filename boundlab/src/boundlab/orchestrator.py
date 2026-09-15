from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from boundlab.agents.base import Agent, AgentResult
from boundlab.agents.registry import get as get_agent
from boundlab.bus import MessageBus
from boundlab.context import Context
from boundlab.errors import BoundLabError, TerritoryError
from boundlab.guard import BoundedFS
from boundlab.memory import Memory
from boundlab.models import RunReport, StepRecord, TerritoryMap
from boundlab.rules.engine import RuleEngine
from boundlab.territory import load_territories


DEFAULT_PIPELINE = ("researcher", "writer", "reviewer", "coordinator")


class Orchestrator:
    def __init__(
        self,
        root: Path,
        territories: TerritoryMap | None = None,
        rules: RuleEngine | None = None,
    ) -> None:
        self.root = root
        self.territories = territories or load_territories()
        self.rules = rules or RuleEngine()
        self.rules.assert_unique_owners(self.territories)
        self.bus = MessageBus()

    def run(
        self,
        goal: str,
        agents: list[str] | None = None,
        parallel: bool = False,
    ) -> RunReport:
        names = list(agents or DEFAULT_PIPELINE)
        self.root.mkdir(parents=True, exist_ok=True)
        instances = [self._build(name) for name in names]
        if parallel:
            return self._run_parallel(goal, instances)
        return self._run_serial(goal, instances)

    def _build(self, name: str) -> Agent:
        if name not in self.territories.agents:
            raise TerritoryError(f"{name} has no entry in territories.yaml")
        return get_agent(name)()

    def _context(self, goal: str, agent_name: str) -> Context:
        return Context(
            goal=goal,
            agent_name=agent_name,
            fs=BoundedFS(self.root, self.territories, self.territories.get(agent_name)),
            bus=self.bus,
            memory=Memory(),
        )

    def _run_serial(self, goal: str, agents: list[Agent]) -> RunReport:
        results: dict[str, object] = {}
        steps: list[StepRecord] = []
        errors: list[str] = []
        for agent in agents:
            result, agent_steps, error = self._invoke(goal, agent)
            steps.extend(agent_steps)
            if error:
                errors.append(error)
                break
            results[agent.name] = result
        return RunReport(goal=goal, root=self.root, results=results, steps=steps, errors=errors)

    def _run_parallel(self, goal: str, agents: list[Agent]) -> RunReport:
        results: dict[str, object] = {}
        steps: list[StepRecord] = []
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=max(1, len(agents))) as pool:
            futures = {pool.submit(self._invoke, goal, agent): agent.name for agent in agents}
            for future in as_completed(futures):
                result, agent_steps, error = future.result()
                steps.extend(agent_steps)
                if error:
                    errors.append(error)
                elif result is not None:
                    results[futures[future]] = result
        return RunReport(goal=goal, root=self.root, results=results, steps=steps, errors=errors)

    def _invoke(
        self, goal: str, agent: Agent
    ) -> tuple[AgentResult | None, list[StepRecord], str | None]:
        ctx = self._context(goal, agent.name)
        try:
            result = agent.run(ctx)
        except BoundLabError as exc:
            ctx.log("error", str(exc), ok=False)
            return None, ctx.steps, f"{agent.name}: {exc}"
        return result, ctx.steps, None
