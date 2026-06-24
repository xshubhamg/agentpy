import unittest
from unittest.mock import MagicMock
from agentpy.agent import Agent
from agentpy.client import LLMClient

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=LLMClient)
        self.agent = Agent(client=self.mock_client)

    def test_agent_chat_yields_content(self):
        # Mock the stream_chat generator
        self.mock_client.stream_chat.return_value = iter([
            {"type": "content", "chunk": "Hello"},
            {"type": "content", "chunk": " world!"}
        ])

        # Run chat
        gen = self.agent.chat("Hi")
        results = list(gen)

        # Check events
        self.assertEqual(results[0], {"type": "content", "chunk": "Hello"})
        self.assertEqual(results[1], {"type": "content", "chunk": " world!"})

        # Check message history
        self.assertEqual(len(self.agent.messages), 2)
        self.assertEqual(self.agent.messages[0]["role"], "user")
        self.assertEqual(self.agent.messages[1]["role"], "assistant")
        self.assertEqual(self.agent.messages[1]["content"], "Hello world!")

    def test_agent_build_system_prompt_with_context(self):
        self.agent.system_prompt = "Base prompt"
        
        @self.agent.context
        def test_context():
            return "Some context"
            
        prompt = self.agent._build_system_prompt()
        self.assertIn("Base prompt", prompt)
        self.assertIn("<test_context>", prompt)
        self.assertIn("Some context", prompt)

    def test_agent_tool_calling_loop(self):
        # 1. First call yields a tool call
        # 2. Agent executes tool and calls client again
        # 3. Second call yields final content
        
        @self.agent.tool
        def get_weather(location: str):
            return {"temp": 20}

        # Mock stream_chat side_effects for two turns
        self.mock_client.stream_chat.side_effect = [
            iter([
                {"type": "tool_calls", "calls": [{"id": "1", "function": {"name": "get_weather", "arguments": "{\"location\": \"London\"}"}}]}
            ]),
            iter([
                {"type": "content", "chunk": "The weather is 20 degrees."}
            ])
        ]

        gen = self.agent.chat("What's the weather?")
        events = list(gen)

        # Check events
        self.assertEqual(events[0]["type"], "tool_call")
        self.assertEqual(events[0]["name"], "get_weather")
        self.assertEqual(events[1]["type"], "status")
        self.assertEqual(events[2]["type"], "content")
        self.assertEqual(events[2]["chunk"], "The weather is 20 degrees.")

        # Check history length: user, assistant(tool_call), tool_result, assistant(final)
        self.assertEqual(len(self.agent.messages), 4)
        self.assertEqual(self.agent.messages[1]["role"], "assistant")
        self.assertTrue(len(self.agent.messages[1]["tool_calls"]) > 0)
        self.assertEqual(self.agent.messages[2]["role"], "tool")
        self.assertEqual(self.agent.messages[3]["role"], "assistant")

if __name__ == "__main__":

    unittest.main()
