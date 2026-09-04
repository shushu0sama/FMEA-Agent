"""Task 5 — LangGraph workflow skeleton tests: full traversal and explicit stage statuses."""

from typing import Any

from langgraph.graph.state import CompiledStateGraph

from fmea_agent.adapters.inmemory import (
    FailureKnowledgeEntry,
    InMemoryFailureKnowledgeRepository,
    InMemorySystemModelRepository,
    NoOpRiskStrategy,
)
from fmea_agent.agents.workflow import build_workflow_graph
from fmea_agent.agents.workflow_state import StageStatus, WorkflowRequest, WorkflowState
from fmea_agent.domain.fmea import (
    AnalysisStatus,
    EffectLevel,
    Evidence,
    FailureCauseCandidate,
    FailureEffectCandidate,
    FailureModeCandidate,
    RiskStatus,
)
from fmea_agent.domain.system_model import Component, Function, System


def _demo_facts() -> tuple[System, Component, Function]:
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


def _demo_graph() -> tuple[
    CompiledStateGraph[WorkflowState, Any, WorkflowState, Any],
    InMemorySystemModelRepository,
    InMemoryFailureKnowledgeRepository,
]:
    system, component, function = _demo_facts()
    system_repo = InMemorySystemModelRepository(
        system=system, components=[component], functions=[function]
    )
    knowledge_repo = InMemoryFailureKnowledgeRepository(
        [
            FailureKnowledgeEntry(
                item_name=component.name,
                function_name=function.name,
                failure_modes=[_demo_candidate()],
            )
        ]
    )
    graph = build_workflow_graph(system_repo, knowledge_repo, NoOpRiskStrategy())
    return graph, system_repo, knowledge_repo


def _demo_request() -> WorkflowRequest:
    return WorkflowRequest(
        system_id="hydraulic-system",
        component_id="hydraulic-pump",
        function_id="provide-pressure",
        title="Demo FMEA",
    )


def _run(
    graph: CompiledStateGraph[WorkflowState, Any, WorkflowState, Any], state: WorkflowState
) -> WorkflowState:
    result = graph.invoke(state)
    return result if isinstance(result, WorkflowState) else WorkflowState.model_validate(result)


def test_workflow_traverses_all_stages_to_end() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.errors == []
    assert final.stage_status == {
        "planning": StageStatus.COMPLETED,
        "structure_analysis": StageStatus.COMPLETED,
        "function_analysis": StageStatus.COMPLETED,
        "failure_analysis": StageStatus.COMPLETED,
        "risk_analysis": StageStatus.NOT_EVALUATED,
        "optimization": StageStatus.SKIPPED,
        "results_documentation": StageStatus.COMPLETED,
    }


def test_workflow_loads_system_component_and_function() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.system is not None
    assert final.system.id == "hydraulic-system"
    assert final.selected_component is not None
    assert final.selected_component.id == "hydraulic-pump"
    assert final.selected_function is not None
    assert final.selected_function.id == "provide-pressure"
    assert final.selected_item is not None
    assert final.selected_item.canonical_system_element_id == "hydraulic-pump"


def test_workflow_candidates_link_stable_domain_ids() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert len(final.failure_candidates) == 1
    candidate = final.failure_candidates[0]
    assert candidate.item_id == "hydraulic-pump"
    assert candidate.function_id == "provide-pressure"
    assert candidate.item_id != "Hydraulic Pump"
    assert candidate.function_id != "Provide Hydraulic Pressure"


def test_workflow_risk_is_not_evaluated_and_optimization_skipped() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.risk is not None
    assert final.risk.status == RiskStatus.NOT_EVALUATED


def test_workflow_produces_structured_output() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.output is not None
    assert final.analysis_context is not None
    assert final.output["analysis_id"] == final.analysis_context.id
    assert final.output["method"] == "AIAG_VDA"
    assert final.output["item"] == "Hydraulic Pump"
    assert final.output["function"] == "Provide Hydraulic Pressure"
    assert final.output["failure_modes"][0]["value"] == "Loss of hydraulic pressure"
    assert final.output["failure_modes"][0]["status"] == "CANDIDATE"
    assert final.output["failure_modes"][0]["evidence"] == [
        {"source": "demo-failure-library:001"}
    ]
    assert final.output["risk"]["status"] == "NOT_EVALUATED"
    assert final.output["stage_status"]["optimization"] == "SKIPPED"


def test_workflow_marks_analysis_context_completed() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.analysis_context is not None
    assert final.analysis_context.status == AnalysisStatus.COMPLETED


def test_workflow_missing_system_records_error_and_reaches_end() -> None:
    graph, _, _ = _demo_graph()
    request = _demo_request().model_copy(update={"system_id": "missing-system"})
    final = _run(graph, WorkflowState(request=request))
    assert final.stage_status["structure_analysis"] == StageStatus.FAILED
    assert final.errors
    assert "structure_analysis" in final.errors[0]
    assert final.output is None


def test_workflow_missing_function_records_error_and_reaches_end() -> None:
    graph, _, _ = _demo_graph()
    request = _demo_request().model_copy(update={"function_id": "missing-function"})
    final = _run(graph, WorkflowState(request=request))
    assert final.stage_status["function_analysis"] == StageStatus.FAILED
    assert (
        "function_analysis: function 'missing-function' not found "
        "for component 'hydraulic-pump'" in final.errors
    )
    assert final.output is None


def test_workflow_missing_request_records_error() -> None:
    graph, _, _ = _demo_graph()
    final = _run(graph, WorkflowState())
    assert final.stage_status["planning"] == StageStatus.FAILED
    assert final.errors[0] == "planning: workflow request missing"
    assert final.output is None


def test_workflow_no_knowledge_yields_empty_candidates_and_not_evaluated() -> None:
    system, component, function = _demo_facts()
    system_repo = InMemorySystemModelRepository(
        system=system, components=[component], functions=[function]
    )
    knowledge_repo = InMemoryFailureKnowledgeRepository()
    graph = build_workflow_graph(system_repo, knowledge_repo, NoOpRiskStrategy())
    final = _run(graph, WorkflowState(request=_demo_request()))
    assert final.failure_candidates == []
    assert final.risk is not None
    assert final.risk.status == RiskStatus.NOT_EVALUATED
    assert final.output is not None
    assert final.output["failure_modes"] == []
