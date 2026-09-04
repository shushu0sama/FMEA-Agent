"""Task 4 — workflow state tests: structured state, no chat transcript."""

from fmea_agent.agents.workflow_state import StageStatus, WorkflowRequest, WorkflowState


def test_workflow_state_defaults_are_structured_and_empty() -> None:
    state = WorkflowState()
    assert state.request is None
    assert state.analysis_context is None
    assert state.system is None
    assert state.selected_component is None
    assert state.selected_function is None
    assert state.selected_item is None
    assert state.failure_candidates == []
    assert state.risk is None
    assert state.stage_status == {}
    assert state.output is None
    assert state.errors == []


def test_workflow_state_is_not_a_chat_transcript() -> None:
    state = WorkflowState()
    assert not hasattr(state, "messages")
    assert "messages" not in state.model_dump()


def test_workflow_request_carries_analysis_targets() -> None:
    request = WorkflowRequest(
        system_id="hydraulic-system",
        component_id="hydraulic-pump",
        function_id="provide-pressure",
        title="Demo FMEA",
    )
    assert request.system_id == "hydraulic-system"
    assert request.component_id == "hydraulic-pump"
    assert request.function_id == "provide-pressure"
    assert request.title == "Demo FMEA"


def test_workflow_request_requires_ids_and_title() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        WorkflowRequest(  # type: ignore[call-arg]
            component_id="hydraulic-pump",
            function_id="provide-pressure",
            title="Demo FMEA",
        )


def test_stage_status_covers_explicit_mvp_statuses() -> None:
    assert set(StageStatus) == {
        StageStatus.NOT_STARTED,
        StageStatus.IN_PROGRESS,
        StageStatus.COMPLETED,
        StageStatus.FAILED,
        StageStatus.NOT_EVALUATED,
        StageStatus.SKIPPED,
    }


def test_state_serializes_enums_as_strings() -> None:
    state = WorkflowState(stage_status={"planning": StageStatus.COMPLETED})
    data = state.model_dump(mode="json")
    assert data["stage_status"]["planning"] == "COMPLETED"
