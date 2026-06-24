from ddgs import DDGS
import wikipedia
from typing import Annotated, Any

def register(agent: Any) -> None:
    @agent.tool
    def duckduckgo_search(query: Annotated[str, "The search query"]) -> dict[str, Any]:
        """Search the web using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return {"results": results}
        except Exception as e:
            return {"error": str(e)}

    @agent.tool
    def wikipedia_summary(topic: Annotated[str, "The topic to summarize"]) -> dict[str, Any]:
        """Get a summary of a topic from Wikipedia."""
        try:
            # Set language to english
            wikipedia.set_lang("en")
            summary = wikipedia.summary(topic, sentences=3)
            return {"topic": topic, "summary": summary}
        except Exception as e:
            return {"error": str(e)}
