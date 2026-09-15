"""Copy this file into src/boundlab/agents/ and register it.

1. Set `name` to a unique agent id.
2. Add the same id under `agents:` in territories.yaml with non-overlapping owns.
3. Import the class in src/boundlab/agents/registry.py.
4. Run: python -m boundlab run "your goal" --agents researcher,demo
"""

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context


class DemoAgent(Agent):
    name = "demo"
    description = "Example extra agent. Owns workspace/demo/ only."

    def run(self, ctx: Context) -> AgentResult:
        path = ctx.write(
            "workspace/demo/hello.md",
            f"# Demo\n\ngoal: {ctx.goal}\n\nThis file is owned by demo only.\n",
        )
        ctx.publish("demo", "hello from demo", path=path)
        return AgentResult(agent=self.name, summary="wrote demo note", artifacts=[path])
