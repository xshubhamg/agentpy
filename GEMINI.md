# AgentPy: Architecture & Design Principles

## Core Architecture
This project follows a strict layered architecture with clear separation of concerns:

1.  **I/O Layer (`LLMClient`)**: Handles all HTTP communication with the Ollama API. It is responsible for session management, stream parsing, and chunk aggregation.
2.  **Domain Layer (`Agent`)**: Manages the agent's memory (message history), context providers, and tool orchestration. It depends on `LLMClient` via **Dependency Injection**.
3.  **Tooling Layer (`Tools`)**: Handles type reflection, schema generation, and function execution for tools.
4.  **CLI Layer (`main.py`)**: The entry point that assembles the components and handles the Rich-based UI.

## Design Patterns Applied
- **Single Responsibility Principle (SRP)**: Each class has a single reason to change. `Agent` no longer handles HTTP parsing.
- **Dependency Injection (DI)**: `Agent` receives its `LLMClient` instance, making it easily testable with mocks.
- **Composition over Inheritance**: Behavior is built by combining `Agent`, `LLMClient`, and `Tools`.
- **Function Size Guidelines**: Large functions like `chat()` have been broken down into smaller, focused private methods (`_build_system_prompt`, `_handle_tool_calls`).

## Testing Strategy
- **Unit Tests**: Found in `tests/`. Use mocks for the `LLMClient` to test `Agent` logic in isolation.
- **Adding Features**: When adding new capabilities, ensure they fit into the appropriate layer and are covered by unit tests.
