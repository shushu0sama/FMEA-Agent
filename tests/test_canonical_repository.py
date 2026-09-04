"""MVP-1E — canonical-backed SystemModelRepository + workflow integration.

The 1E-0 gate: the existing workflow looks up functions via
``SystemModelRepository.list_functions(component.id)``, which filters on
``element_id in function.allocated_to``. 1D mapped every typed actionUsage
with ``allocated_to == []``, so a canonical model could not satisfy the
workflow contract. These tests pin the fixed contract: functions must be
allocated to mapped elements by evidence (owner traversal), and the
repository over the CanonicalSystemModel must serve the existing workflow
unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph.state import CompiledStateGraph

from fmea_agent.adapters.inmemory import (
    CanonicalSystemModelRepository,
    FailureKnowledgeEntry,
    InMemoryFailureKnowledgeRepository,
    NoOpRiskStrategy,
)
from fmea_agent.adapters.sysml import CanonicalSystemMapper, OpenSysMLFileAdapter
from fmea_agent.agents.workflow import build_workflow_graph
from fmea_agent.agents.workflow_state import StageStatus, WorkflowRequest, WorkflowState
from fmea_agent.application.ports import SystemModelRepository
from fmea_agent.domain.fmea import (
    EffectLevel,
    Evidence,
    FailureCauseCandidate,
    FailureEffectCandidate,
    FailureModeCandidate,
)
from fmea_agent.domain.system_model import CanonicalSystemModel

MODELS_DIR = Path(__file__).resolve().parent / "fixtures" / "sysml" / "models"
TYPED_INSIDE_MODEL = MODELS_DIR / "typed_inside_probe.sysml"


def _mapped_model() -> CanonicalSystemModel:
    snapshot = OpenSysMLFileAdapter().load(TYPED_INSIDE_MODEL)
    return CanonicalSystemMapper().map_snapshot(snapshot)


def _run(
    graph: CompiledStateGraph[WorkflowState, Any, WorkflowState, Any], state: WorkflowState
) -> WorkflowState:
    result = graph.invoke(state)
    return result if isinstance(result, WorkflowState) else WorkflowState.model_validate(result)


# --- 1E-0 gate: list_functions must satisfy the workflow lookup ---


def test_repository_list_functions_satisfies_workflow_lookup() -> None:
    model = _mapped_model()
    repo = CanonicalSystemModelRepository(model)
    motor = next(c for c in model.components if c.name == "motor")
    assert [f.name for f in repo.list_functions(motor.id)] == ["spin"]


# --- repository contract tests ---


def test_canonical_repository_lookup() -> None:
    model = _mapped_model()
    repo: SystemModelRepository = CanonicalSystemModelRepository(model)
    assert repo.get_system(model.system.id) == model.system
    motor = repo.get_component("component-1")
    assert motor is not None and motor.name == "motor"
    assert repo.list_components(model.system.id) == [motor]
    assert [f.id for f in repo.list_functions(motor.id)] == ["function-2"]


def test_canonical_repository_lists_system_level_functions() -> None:
    model = _mapped_model()
    repo = CanonicalSystemModelRepository(model)
    assert [f.name for f in repo.list_functions(model.system.id)] == ["pumpSpin"]


def test_canonical_repository_missing_data() -> None:
    repo = CanonicalSystemModelRepository(_mapped_model())
    assert repo.get_system("missing") is None
    assert repo.get_component("missing") is None
    assert repo.list_components("missing") == []
    assert repo.list_functions("missing") == []


def test_canonical_repository_conforms_to_port() -> None:
    assert isinstance(
        CanonicalSystemModelRepository(_mapped_model()), SystemModelRepository
    )


# --- workflow integration over the canonical repository ---


def _motor_spin_request(model: CanonicalSystemModel) -> WorkflowRequest:
    motor = next(c for c in model.components if c.name == "motor")
    spin = next(f for f in model.functions if f.name == "spin")
    return WorkflowRequest(
        system_id=model.system.id,
        component_id=motor.id,
        function_id=spin.id,
        title="MVP-1E real SysML E2E",
    )


def _candidate() -> FailureModeCandidate:
    return FailureModeCandidate(
        value="Motor fails to spin",
        causes=[FailureCauseCandidate(value="Demo bearing failure")],
        effects=[
            FailureEffectCandidate(level=EffectLevel.LOCAL, value="Pump loses drive")
        ],
        evidence=[Evidence(source="e2e-failure-library:001")],
    )


def _knowledge_repo(model: CanonicalSystemModel) -> InMemoryFailureKnowledgeRepository:
    motor = next(c for c in model.components if c.name == "motor")
    spin = next(f for f in model.functions if f.name == "spin")
    return InMemoryFailureKnowledgeRepository(
        [
            FailureKnowledgeEntry(
                item_name=motor.name,
                function_name=spin.name,
                failure_modes=[_candidate()],
            )
        ]
    )


def test_workflow_runs_end_to_end_on_real_sysml_model() -> None:
    model = _mapped_model()
    repo = CanonicalSystemModelRepository(model)
    graph = build_workflow_graph(repo, _knowledge_repo(model), NoOpRiskStrategy())
    final = _run(graph, WorkflowState(request=_motor_spin_request(model)))
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
    assert final.selected_item is not None
    assert final.selected_item.canonical_system_element_id == "component-1"
    assert final.selected_function is not None
    assert final.selected_function.id == "function-2"
    assert final.output is not None
    assert final.output["item"] == "motor"
    assert final.output["function"] == "spin"
    assert final.output["failure_modes"][0]["value"] == "Motor fails to spin"
    assert final.output["risk"]["status"] == "NOT_EVALUATED"
    assert final.output["stage_status"]["optimization"] == "SKIPPED"
    assert final.failure_candidates[0].item_id == "component-1"
    assert final.failure_candidates[0].function_id == "function-2"


def test_workflow_reports_error_when_function_not_allocated_to_component() -> None:
    model = _mapped_model()
    repo = CanonicalSystemModelRepository(model)
    graph = build_workflow_graph(repo, _knowledge_repo(model), NoOpRiskStrategy())
    request = _motor_spin_request(model).model_copy(update={"function_id": "function-1"})
    final = _run(graph, WorkflowState(request=request))
    assert final.stage_status["function_analysis"] == StageStatus.FAILED
    assert (
        "function_analysis: function 'function-1' not found for component 'component-1'"
        in final.errors
    )
