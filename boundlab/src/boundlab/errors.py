class BoundLabError(Exception):
    """Base error for the runtime."""


class TerritoryError(BoundLabError):
    """Territory map is invalid or missing an agent."""


class BoundaryError(BoundLabError):
    """An agent tried to read or write outside its territory."""


class RuleError(BoundLabError):
    """An agent action violated a declared rule."""
