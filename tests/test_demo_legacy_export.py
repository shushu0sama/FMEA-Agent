"""Run the original graph to verify nested provenance survives its real export node."""

import json

from fmea_agent.adapters.inmemory import (
    FailureKnowledgeEntry,
    InMemoryFailureKnowledgeRepository,
    InMemorySystemModelRepository,
    NoOpRiskStrategy,
)
from fmea_agent.agents.workflow import build_workflow_graph
from fmea_agent.agents.workflow_state import WorkflowRequest, WorkflowState
from fmea_agent.domain.fmea import (
    EffectLevel,
    Evidence,
    FailureCauseCandidate,
    FailureEffectCandidate,
    FailureModeCandidate,
    KnowledgeStatus,
)
from fmea_agent.domain.system_model import Component, Function, SourceReference, System


def test_original_graph_export_preserves_nested_provenance_and_legacy_keys():
    ref = SourceReference(
        source_type="sysml_file",
        source_uri="synthetic-contract.sysml",
        source_element_id="S::motor",
        source_version="fixture-v1",
        adapter="test-adapter",
        repository="fixture-repository",
        project="fixture-project",
        commit="fixture-commit",
        branch="fixture-branch",
        locator="line:7",
    )
    component = Component(id="motor-1", name="motor", parent_id="system-1", source_refs=[ref])
    function_ref = ref.model_copy(
        update={"source_element_id": "S::motor::spin", "locator": "line:8"}
    )
    function = Function(
        id="spin-1", name="spin", allocated_to=[component.id], source_refs=[function_ref]
    )
    candidate = FailureModeCandidate(
        value="does not spin",
        description="Synthetic regression example",
        status=KnowledgeStatus.INFERENCE,
        causes=[
            FailureCauseCandidate(
                value="candidate cause",
                status=KnowledgeStatus.INFERENCE,
                mechanism="candidate mechanism",
                description="Cause text must survive",
                evidence=[Evidence(source="test:record:cause")],
            )
        ],
        effects=[
            FailureEffectCandidate(
                level=EffectLevel.NEXT_HIGHER_LEVEL,
                value="candidate consequence",
                status=KnowledgeStatus.UNKNOWN,
                affected_item_id="system-1",
                evidence=[Evidence(source="test:record:effect")],
            )
        ],
        evidence=[Evidence(source="test:record:mode")],
    )
    graph = build_workflow_graph(
        InMemorySystemModelRepository(
            system=System(id="system-1", name="system"),
            components=[component],
            functions=[function],
        ),
        InMemoryFailureKnowledgeRepository(
            [
                FailureKnowledgeEntry(
                    item_name="motor",
                    function_name="spin",
                    failure_modes=[candidate],
                )
            ]
        ),
        NoOpRiskStrategy(),
    )
    state = WorkflowState.model_validate(
        graph.invoke(
            WorkflowState(
                request=WorkflowRequest(
                    system_id="system-1",
                    component_id="motor-1",
                    function_id="spin-1",
                    title="D2 regression",
                )
            )
        )
    )
    assert state.errors == []
    output = json.loads(json.dumps(state.output))
    assert output["item"] == "motor" and output["function"] == "spin"
    assert output["item_id"] == "motor-1" and output["function_id"] == "spin-1"
    assert output["source_refs"] == {
        "item": [ref.model_dump(mode="json")],
        "function": [function_ref.model_dump(mode="json")],
    }
    mode = output["failure_modes"][0]
    assert mode["item_id"] == "motor-1" and mode["function_id"] == "spin-1"
    assert "id" not in mode
    assert mode["description"] == "Synthetic regression example"
    assert mode["causes"][0] == candidate.causes[0].model_dump(mode="json")
    assert mode["effects"][0] == candidate.effects[0].model_dump(mode="json")
    assert mode["evidence"] == [{"source": "test:record:mode"}]
    assert output["risk"]["status"] == "NOT_EVALUATED"
    assert output["stage_status"]["optimization"] == "SKIPPED"
