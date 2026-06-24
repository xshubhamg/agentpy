from typing import Annotated, Any
from .math import register as register_math
from .system import register as register_system
from .productivity import register as register_productivity
from .developer import register as register_developer
from .search import register as register_search

def register_all(agent: Any) -> None:
    """Register all builtin tool plugins with the agent."""
    register_math(agent)
    register_system(agent)
    register_productivity(agent)
    register_developer(agent)
    register_search(agent)
