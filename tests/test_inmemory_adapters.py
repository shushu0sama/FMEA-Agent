"""Task 3 — in-memory adapter tests: fixture lookup and missing-data behavior."""

from fmea_agent.adapters.inmemory import (
    FailureKnowledgeEntry,
    InMemoryFailureKnowledgeRepository,
    InMemorySystemModelRepository,
    MockLLMClient,
    NoOpRiskStrategy,
)
from fmea_agent.application.ports import (
    FailureKnowledgeRepository,
    LLMClient,
    RiskStrategy,
    SystemModelRepository,
)
from fmea_agent.domain.fmea import (
    AnalysisContext,
    EffectLevel,
    Evidence,
    FailureCauseCandidate,
    FailureEffectCandidate,
    FailureModeCandidate,
    FMEAItem,
    RiskStatus,
)
from fmea_agent.domain.system_model import Component, Function, System


def _fixture_facts() -> tuple[System, Component, Function]:
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


def test_inmemory_system_repository_fixture_lookup() -> None:
    system, component, function = _fixture_facts()
    repo: SystemModelRepository = InMemorySystemModelRepository(
        system=system, components=[component], functions=[function]
    )
    assert repo.get_system("hydraulic-system") == system
    assert repo.get_component("hydraulic-pump") == component
    assert repo.list_components("hydraulic-system") == [component]
    assert repo.list_functions("hydraulic-pump") == [function]


def test_inmemory_system_repository_missing_data() -> None:
    system, component, function = _fixture_facts()
    repo: SystemModelRepository = InMemorySystemModelRepository(
        system=system, components=[component], functions=[function]
    )
    assert repo.get_system("missing-system") is None
    assert repo.get_component("missing-component") is None
    assert repo.list_components("missing-system") == []
    assert repo.list_functions("missing-element") == []


def test_inmemory_system_repository_empty_construction() -> None:
    repo: SystemModelRepository = InMemorySystemModelRepository()
    assert repo.get_system("any") is None
    assert repo.get_component("any") is None
    assert repo.list_components("any") == []
    assert repo.list_functions("any") == []


def _demo_candidate() -> FailureModeCandidate:
    return FailureModeCandidate(
        value="Loss of hydraulic pressure",
        causes=[FailureCauseCandidate(value="Demo mechanical failure")],
        effects=[
            FailureEffectCandidate(
                level=EffectLevel.LOCAL,
                value="Required outlet pressure is unavailable",
            )
        ],
        evidence=[Evidence(source="demo-failure-library:001")],
    )


def test_inmemory_failure_knowledge_exact_match_lookup() -> None:
    candidate = _demo_candidate()
    repo: FailureKnowledgeRepository = InMemoryFailureKnowledgeRepository(
        [
            FailureKnowledgeEntry(
                item_name="Hydraulic Pump",
                function_name="Provide Hydraulic Pressure",
                failure_modes=[candidate],
            )
        ]
    )
    found = repo.find_failure_modes("Hydraulic Pump", "Provide Hydraulic Pressure")
    assert found == [candidate]
    assert repo.find_failure_modes("Hydraulic Pump", "Other Function") == []
    assert repo.find_failure_modes("Other Item", "Provide Hydraulic Pressure") == []
    assert repo.find_failure_modes("Other Item", "Other Function") == []


def test_inmemory_failure_knowledge_empty_construction() -> None:
    repo: FailureKnowledgeRepository = InMemoryFailureKnowledgeRepository()
    assert repo.find_failure_modes("Anything", "Anything") == []


def test_inmemory_failure_knowledge_accumulates_entries_for_same_key() -> None:
    first = _demo_candidate()
    second = _demo_candidate()
    second = second.model_copy(update={"value": "Cavitation"})
    repo = InMemoryFailureKnowledgeRepository(
        [
            FailureKnowledgeEntry(
                item_name="Hydraulic Pump",
                function_name="Provide Hydraulic Pressure",
                failure_modes=[first],
            ),
            FailureKnowledgeEntry(
                item_name="Hydraulic Pump",
                function_name="Provide Hydraulic Pressure",
                failure_modes=[second],
            ),
        ]
    )
    assert repo.find_failure_modes("Hydraulic Pump", "Provide Hydraulic Pressure") == [
        first,
        second,
    ]


def test_knowledge_candidates_never_put_display_names_into_ids() -> None:
    system, component, function = _fixture_facts()
    candidate = FailureModeCandidate(
        value="Loss of hydraulic pressure",
        item_id=component.id,
        function_id=function.id,
    )
    repo = InMemoryFailureKnowledgeRepository(
        [
            FailureKnowledgeEntry(
                item_name=component.name,
                function_name=function.name,
                failure_modes=[candidate],
            )
        ]
    )
    found = repo.find_failure_modes(component.name, function.name)
    assert found == [candidate]
    assert found[0].item_id == "hydraulic-pump"
    assert found[0].function_id == "provide-pressure"
    assert found[0].item_id != component.name
    assert found[0].function_id != function.name


def test_noop_risk_strategy_returns_not_evaluated() -> None:
    system, component, function = _fixture_facts()
    strategy: RiskStrategy = NoOpRiskStrategy()
    assessment = strategy.evaluate(
        context=AnalysisContext(id="an-001", title="T"),
        item=FMEAItem(
            id="fmea-item-1",
            name=component.name,
            canonical_system_element_id=component.id,
        ),
        failure_mode=FailureModeCandidate(value="x", function_id=function.id),
    )
    assert assessment.status == RiskStatus.NOT_EVALUATED
    assert assessment.strategy == "noop"


def test_mock_llm_client_is_deterministic() -> None:
    llm: LLMClient = MockLLMClient()
    first = llm.generate("hello")
    second = llm.generate("hello")
    assert first == second == "[mock-llm] hello"
    assert isinstance(llm.generate("other"), str)


def test_adapters_conform_to_ports() -> None:
    system, component, function = _fixture_facts()
    assert isinstance(
        InMemorySystemModelRepository(system, [component], [function]),
        SystemModelRepository,
    )
    assert isinstance(InMemoryFailureKnowledgeRepository(), FailureKnowledgeRepository)
    assert isinstance(NoOpRiskStrategy(), RiskStrategy)
    assert isinstance(MockLLMClient(), LLMClient)
