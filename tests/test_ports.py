"""Task 2 — application port tests: fakes satisfy the ports structurally and behaviorally."""

from fmea_agent.application.ports import (
    FailureKnowledgeRepository,
    LLMClient,
    RiskStrategy,
    SystemModelRepository,
)
from fmea_agent.domain.fmea import (
    AnalysisContext,
    FailureModeCandidate,
    FMEAItem,
    RiskAssessment,
    RiskStatus,
)
from fmea_agent.domain.system_model import Component, Function, System


class FakeSystemModelRepository:
    def __init__(
        self,
        system: System,
        components: list[Component],
        functions: list[Function],
    ) -> None:
        self._system = system
        self._components = {c.id: c for c in components}
        self._functions = {f.id: f for f in functions}

    def get_system(self, system_id: str) -> System | None:
        return self._system if self._system.id == system_id else None

    def get_component(self, component_id: str) -> Component | None:
        return self._components.get(component_id)

    def list_components(self, system_id: str) -> list[Component]:
        return [c for c in self._components.values() if c.parent_id == system_id]

    def list_functions(self, element_id: str) -> list[Function]:
        return [f for f in self._functions.values() if element_id in f.allocated_to]


class FakeFailureKnowledgeRepository:
    def __init__(
        self,
        entries: dict[tuple[str, str], list[FailureModeCandidate]],
    ) -> None:
        self._entries = dict(entries)

    def find_failure_modes(
        self, item_name: str, function_name: str
    ) -> list[FailureModeCandidate]:
        return list(self._entries.get((item_name, function_name), []))


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return "fake response"


class FakeRiskStrategy:
    def evaluate(
        self,
        context: AnalysisContext,
        item: FMEAItem,
        failure_mode: FailureModeCandidate,
    ) -> RiskAssessment:
        return RiskAssessment()


def _fixtures() -> tuple[System, Component, Function]:
    system = System(id="hydraulic-system", name="Hydraulic System")
    component = Component(
        id="hydraulic-pump",
        name="Hydraulic Pump",
        parent_id="hydraulic-system",
    )
    function = Function(
        id="provide-pressure",
        name="Provide Hydraulic Pressure",
        allocated_to=["hydraulic-pump"],
    )
    return system, component, function


def test_fakes_conform_to_ports_structurally() -> None:
    system, component, function = _fixtures()
    system_repo: SystemModelRepository = FakeSystemModelRepository(
        system, [component], [function]
    )
    knowledge_repo: FailureKnowledgeRepository = FakeFailureKnowledgeRepository({})
    llm: LLMClient = FakeLLMClient()
    risk: RiskStrategy = FakeRiskStrategy()
    assert isinstance(system_repo, SystemModelRepository)
    assert isinstance(knowledge_repo, FailureKnowledgeRepository)
    assert isinstance(llm, LLMClient)
    assert isinstance(risk, RiskStrategy)


def test_fake_system_repository_lookup_and_missing_behavior() -> None:
    system, component, function = _fixtures()
    repo: SystemModelRepository = FakeSystemModelRepository(system, [component], [function])
    assert repo.get_system("hydraulic-system") == system
    assert repo.get_system("missing") is None
    assert repo.get_component("hydraulic-pump") == component
    assert repo.get_component("missing") is None
    assert repo.list_components("hydraulic-system") == [component]
    assert repo.list_functions("hydraulic-pump") == [function]
    assert repo.list_functions("missing") == []


def test_fake_knowledge_repository_returns_matching_modes() -> None:
    mode = FailureModeCandidate(
        value="Loss of hydraulic pressure",
        item_id="hydraulic-pump",
        function_id="provide-pressure",
    )
    repo: FailureKnowledgeRepository = FakeFailureKnowledgeRepository(
        {("Hydraulic Pump", "Provide Hydraulic Pressure"): [mode]}
    )
    assert repo.find_failure_modes("Hydraulic Pump", "Provide Hydraulic Pressure") == [mode]
    assert repo.find_failure_modes("Other", "Other") == []


def test_fake_llm_client_generates_text() -> None:
    llm: LLMClient = FakeLLMClient()
    assert isinstance(llm.generate("prompt"), str)


def test_fake_risk_strategy_returns_not_evaluated() -> None:
    _, component, function = _fixtures()
    risk: RiskStrategy = FakeRiskStrategy()
    assessment = risk.evaluate(
        context=AnalysisContext(id="an-001", title="T"),
        item=FMEAItem(
            id="fmea-item-1",
            name="Hydraulic Pump",
            canonical_system_element_id=component.id,
        ),
        failure_mode=FailureModeCandidate(value="x", function_id=function.id),
    )
    assert assessment.status == RiskStatus.NOT_EVALUATED
