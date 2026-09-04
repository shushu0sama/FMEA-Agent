"""MVP-0 LangGraph workflow skeleton: seven AIAG-VDA-shaped stages, linear flow.

LangGraph is confined to this layer. The default path uses in-memory
repositories and the NoOpRiskStrategy; no LLM is invoked.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from fmea_agent.agents.workflow_state import StageStatus, WorkflowState
from fmea_agent.application.ports import (
    FailureKnowledgeRepository,
    RiskStrategy,
    SystemModelRepository,
)
from fmea_agent.domain.fmea import (
    AnalysisContext,
    AnalysisStatus,
    FMEAItem,
    RiskAssessment,
    RiskStatus,
)

_STAGES = (
    "planning",
    "structure_analysis",
    "function_analysis",
    "failure_analysis",
    "risk_analysis",
    "optimization",
    "results_documentation",
)


def _started(state: WorkflowState, stage: str) -> dict[str, StageStatus]:
    return {**state.stage_status, stage: StageStatus.IN_PROGRESS}


def _failed(
    state: WorkflowState,
    stage: str,
    statuses: dict[str, StageStatus],
    message: str,
) -> dict[str, Any]:
    return {
        "stage_status": {**statuses, stage: StageStatus.FAILED},
        "errors": [*state.errors, message],
    }


def build_workflow_graph(
    system_repo: SystemModelRepository,
    knowledge_repo: FailureKnowledgeRepository,
    risk_strategy: RiskStrategy,
) -> CompiledStateGraph[WorkflowState, Any, WorkflowState, Any]:
    """Compile the linear seven-stage MVP-0 workflow graph."""

    def planning(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "planning")
        request = state.request
        if request is None:
            return _failed(state, "planning", statuses, "planning: workflow request missing")
        return {
            "stage_status": {**statuses, "planning": StageStatus.COMPLETED},
            "analysis_context": AnalysisContext(
                id=f"an-{uuid4().hex[:12]}",
                title=request.title,
                system_id=request.system_id,
                status=AnalysisStatus.IN_PROGRESS,
            ),
        }

    def structure_analysis(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "structure_analysis")
        request = state.request
        if request is None:
            return _failed(
                state, "structure_analysis", statuses, "structure_analysis: request missing"
            )
        system = system_repo.get_system(request.system_id)
        component = system_repo.get_component(request.component_id)
        if system is None or component is None:
            return _failed(
                state,
                "structure_analysis",
                statuses,
                f"structure_analysis: system '{request.system_id}' or "
                f"component '{request.component_id}' not found",
            )
        return {
            "stage_status": {**statuses, "structure_analysis": StageStatus.COMPLETED},
            "system": system,
            "selected_component": component,
            "selected_item": FMEAItem(
                id=f"fmea-item-{component.id}",
                name=component.name,
                canonical_system_element_id=component.id,
                source_refs=component.source_refs,
            ),
        }

    def function_analysis(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "function_analysis")
        request = state.request
        component = state.selected_component
        if request is None or component is None:
            return _failed(
                state, "function_analysis", statuses, "function_analysis: no component selected"
            )
        function = next(
            (f for f in system_repo.list_functions(component.id) if f.id == request.function_id),
            None,
        )
        if function is None:
            return _failed(
                state,
                "function_analysis",
                statuses,
                f"function_analysis: function '{request.function_id}' not found "
                f"for component '{component.id}'",
            )
        return {
            "stage_status": {**statuses, "function_analysis": StageStatus.COMPLETED},
            "selected_function": function,
        }

    def failure_analysis(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "failure_analysis")
        component = state.selected_component
        function = state.selected_function
        if component is None or function is None:
            return _failed(
                state, "failure_analysis", statuses, "failure_analysis: no item/function selected"
            )
        candidates = []
        for candidate in knowledge_repo.find_failure_modes(component.name, function.name):
            updates: dict[str, Any] = {}
            if candidate.item_id is None:
                updates["item_id"] = component.id
            if candidate.function_id is None:
                updates["function_id"] = function.id
            candidates.append(candidate.model_copy(update=updates) if updates else candidate)
        return {
            "stage_status": {**statuses, "failure_analysis": StageStatus.COMPLETED},
            "failure_candidates": candidates,
        }

    def risk_analysis(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "risk_analysis")
        context = state.analysis_context
        item = state.selected_item
        if context is None or item is None:
            return _failed(
                state, "risk_analysis", statuses, "risk_analysis: no context/item available"
            )
        candidates = state.failure_candidates
        if candidates:
            assessment = risk_strategy.evaluate(context, item, candidates[0])
        else:
            assessment = RiskAssessment()
        stage_status = (
            StageStatus.NOT_EVALUATED
            if assessment.status == RiskStatus.NOT_EVALUATED
            else StageStatus.COMPLETED
        )
        return {
            "stage_status": {**statuses, "risk_analysis": stage_status},
            "risk": assessment,
        }

    def optimization(state: WorkflowState) -> dict[str, Any]:
        return {"stage_status": {**state.stage_status, "optimization": StageStatus.SKIPPED}}

    def results_documentation(state: WorkflowState) -> dict[str, Any]:
        statuses = _started(state, "results_documentation")
        context = state.analysis_context
        component = state.selected_component
        function = state.selected_function
        risk = state.risk
        if context is None or component is None or function is None or risk is None:
            return _failed(
                state,
                "results_documentation",
                statuses,
                "results_documentation: incomplete analysis state",
            )
        final_statuses = {
            **statuses,
            "results_documentation": StageStatus.COMPLETED,
        }
        output: dict[str, Any] = {
            "analysis_id": context.id,
            "method": context.method.value,
            "item": component.name,
            "function": function.name,
            "failure_modes": [
                {
                    "value": mode.value,
                    "status": mode.status.value,
                    "causes": [
                        {"value": cause.value, "status": cause.status.value}
                        for cause in mode.causes
                    ],
                    "effects": [
                        {"level": effect.level.value, "value": effect.value}
                        for effect in mode.effects
                    ],
                    "evidence": [{"source": ev.source} for ev in mode.evidence],
                }
                for mode in state.failure_candidates
            ],
            "risk": risk.model_dump(mode="json"),
            "stage_status": {name: s.value for name, s in final_statuses.items()},
        }
        return {
            "stage_status": final_statuses,
            "analysis_context": context.model_copy(
                update={"status": AnalysisStatus.COMPLETED, "updated_at": datetime.now(UTC)}
            ),
            "output": output,
        }

    graph = StateGraph(WorkflowState)
    graph.add_node("planning", planning)
    graph.add_node("structure_analysis", structure_analysis)
    graph.add_node("function_analysis", function_analysis)
    graph.add_node("failure_analysis", failure_analysis)
    graph.add_node("risk_analysis", risk_analysis)
    graph.add_node("optimization", optimization)
    graph.add_node("results_documentation", results_documentation)
    graph.set_entry_point("planning")
    for stage, next_stage in zip(_STAGES, [*_STAGES[1:], END], strict=True):
        graph.add_edge(stage, next_stage)
    return graph.compile()
