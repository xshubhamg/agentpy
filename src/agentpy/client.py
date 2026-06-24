import json
from typing import Any, Generator

import requests


class LLMClient:
    """
    A client for interacting with the Ollama LLM API.
    Handles HTTP communication, streaming, and response parsing.
    """

    def __init__(self, model: str, base_url: str = "http://localhost:11434", api_key: str = "NO_API_KEY"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def stream_chat(
        self, 
        messages: list[dict[str, Any]], 
        tools: list[dict[str, Any]] | None = None
    ) -> Generator[dict[str, Any], None, None]:
        """
        Sends a chat request and yields stream events.
        
        Events yielded:
            - {"type": "thinking", "chunk": str}
            - {"type": "content", "chunk": str}
            - {"type": "tool_calls", "calls": list[dict]} (Sent once at the end of the stream if any)
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "think": True
        }
        if tools:
            payload["tools"] = tools

        response = self._session.post(
            url,
            json=payload,
            timeout=300,
            stream=True,
        )
        response.raise_for_status()

        tool_calls_map = {}

        for line in response.iter_lines():
            if not line:
                continue
            
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            message = data.get("message", {})
            
            # 1. Handle Thinking
            if thinking_chunk := message.get("thinking"):
                yield {"type": "thinking", "chunk": thinking_chunk}

            # 2. Handle Content
            if content_chunk := message.get("content"):
                yield {"type": "content", "chunk": content_chunk}

            # 3. Aggregate Tool Calls
            if incoming_tool_calls := message.get("tool_calls"):
                for tc in incoming_tool_calls:
                    idx = tc.get("index", 0)
                    if idx not in tool_calls_map:
                        tool_calls_map[idx] = tc
                    else:
                        base = tool_calls_map[idx]
                        if "function" in tc:
                            if "arguments" in tc["function"]:
                                base["function"]["arguments"] = (
                                    base["function"].get("arguments", "") + 
                                    tc["function"]["arguments"]
                                )
                            if "name" in tc["function"] and tc["function"]["name"]:
                                base["function"]["name"] = tc["function"]["name"]
                        if "id" in tc and tc["id"]:
                            base["id"] = tc["id"]

            if data.get("done"):
                break

        if tool_calls_map:
            yield {"type": "tool_calls", "calls": list(tool_calls_map.values())}
