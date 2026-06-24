from typing import Annotated, Any

def register(agent: Any) -> None:
    @agent.tool
    def add(
        a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
    ) -> dict[str, int]:
        """Add two numbers together"""
        return {"result": a + b}

    @agent.tool
    def multiply(
        a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
    ) -> dict[str, int]:
        """Multiply two numbers together"""
        return {"result": a * b}

    @agent.tool
    def secret() -> dict[str, str]:
        """Return secret key"""
        return {"result": "fluffy bunnies"}
