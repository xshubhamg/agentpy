import json
from dataclasses import dataclass, field
from typing import Any, Callable, Generator

from .client import LLMClient
from .tools import Tools


@dataclass
class Agent:
    """
    An AI agent that can interact with a model via an LLMClient, use tools, and maintain context.
    """
    client: LLMClient
    system_prompt: str = "You are my software development mentor"
    tools: Tools = field(default_factory=Tools)
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def tool(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to register a tool with the agent."""
        return self.tools.register(func)

    def context(self, func: Callable[[], str]) -> Callable[[], str]:
        """Decorator to register a context provider with the agent."""
        self.contexts[func.__name__] = func
        return func

    def _build_system_prompt(self) -> str:
        """Construct the full system prompt including active contexts."""
        active_contexts = []
        for name, func in self.contexts.items():
            try:
                content = func().strip()
                if content:
                    active_contexts.append(f"<{name}>\n{content}\n</{name}>")
            except Exception as e:
                active_contexts.append(f"<{name}>\nError: {e}\n</{name}>")

        full_prompt = self.system_prompt
        if active_contexts:
            context_str = "\n\n".join(active_contexts)
            full_prompt += (
                f"\n\nRelevant Context:\n{context_str}\n\n"
                "Use the provided context to answer questions about the current state, user, or environment."
            )
        return full_prompt

    def _handle_tool_calls(self, tool_calls: list[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
        """Execute tool calls and record results in message history."""
        for tool_call in tool_calls:
            name = tool_call.get("function", {}).get("name")
            yield {"type": "tool_call", "name": name}
            
            try:
                result = self.tools.execute(tool_call)
            except Exception as e:
                result = {"error": str(e)}
            
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "content": json.dumps(result),
            })
        
        yield {"type": "status", "message": "Tool results received, generating final response..."}

    def chat(self, user_message: str) -> Generator[dict[str, Any], None, str]:
        """
        Send a message to the agent and stream its response.
        Yields:
            dict: {"type": "content", "chunk": str}, {"type": "thinking", ...}, etc.
        Returns:
            str: The full accumulated message content.
        """
        self.messages.append({"role": "user", "content": user_message})

        while True:
            full_system_prompt = self._build_system_prompt()
            messages = [{"role": "system", "content": full_system_prompt}] + self.messages
            
            full_content = ""
            full_thinking = ""
            tool_calls = []

            # Stream from LLM Client
            for event in self.client.stream_chat(messages, self.tools.get_schemas()):
                if event["type"] == "thinking":
                    full_thinking += event["chunk"]
                    yield event
                elif event["type"] == "content":
                    full_content += event["chunk"]
                    yield event
                elif event["type"] == "tool_calls":
                    tool_calls = event["calls"]

            # Prepare assistant message for history
            stored_content = full_content
            if full_thinking:
                stored_content = f"<think>\n{full_thinking}\n</think>\n{full_content}"

            self.messages.append({
                "role": "assistant",
                "content": stored_content,
                "tool_calls": tool_calls,
            })

            if not tool_calls:
                return full_content

            # Execute tools and continue the loop
            yield from self._handle_tool_calls(tool_calls)
