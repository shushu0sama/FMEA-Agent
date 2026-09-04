"""Deterministic mock LLM for tests and offline demos.

The MVP-0 default workflow path never invokes an LLMClient.
"""


class MockLLMClient:
    """Echoes the prompt with a fixed prefix; fully deterministic."""

    def generate(self, prompt: str) -> str:
        return f"[mock-llm] {prompt}"
