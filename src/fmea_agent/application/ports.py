"""Application ports: stable interfaces between workflow logic and replaceable infrastructure.

No external framework or provider types may appear in these signatures.
"""

from typing import Protocol, runtime_checkable

from fmea_agent.domain.fmea import (
    AnalysisContext,
    FailureModeCandidate,
    FMEAItem,
    RiskAssessment,
)
from fmea_agent.domain.system_model import Component, Function, System


@runtime_checkable
class SystemModelRepository(Protocol):
    """Read-side access to canonical system facts."""

    def get_system(self, system_id: str) -> System | None: ...

    def get_component(self, component_id: str) -> Component | None: ...

    def list_components(self, system_id: str) -> list[Component]: ...

    def list_functions(self, element_id: str) -> list[Function]: ...


@runtime_checkable
class FailureKnowledgeRepository(Protocol):
    """Retrieval of candidate failure knowledge for an item/function pair."""

    def find_failure_modes(
        self, item_name: str, function_name: str
    ) -> list[FailureModeCandidate]: ...


@runtime_checkable
class LLMClient(Protocol):
    """Minimal text-generation capability, provider-agnostic by design."""

    def generate(self, prompt: str) -> str: ...


@runtime_checkable
class RiskStrategy(Protocol):
    """Risk evaluation strategy; MVP-0 implementations return NOT_EVALUATED only."""

    def evaluate(
        self,
        context: AnalysisContext,
        item: FMEAItem,
        failure_mode: FailureModeCandidate,
    ) -> RiskAssessment: ...
