"""BoundLab: bounded multi-agent runtime."""

from boundlab.agents.base import Agent, AgentResult
from boundlab.context import Context
from boundlab.errors import BoundaryError, RuleError, TerritoryError
from boundlab.orchestrator import Orchestrator

__all__ = [
    "Agent",
    "AgentResult",
    "BoundaryError",
    "Context",
    "Orchestrator",
    "RuleError",
    "TerritoryError",
]
__version__ = "0.1.0"
