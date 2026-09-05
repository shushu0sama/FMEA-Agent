"""Demo capabilities declared without concrete provider or framework types."""

from typing import Protocol, runtime_checkable

from fmea_agent.application.ports import LLMClient
from fmea_agent.domain.demo_knowledge import KnowledgeQuery, RetrievalResult


@runtime_checkable
class SourceKnowledgeRepository(Protocol):
    def search(self, query: KnowledgeQuery) -> RetrievalResult: ...


@runtime_checkable
class DemoLLMClient(LLMClient, Protocol):
    def usage(self) -> dict[str, int | str | None]: ...
