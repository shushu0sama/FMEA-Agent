"""Task 1 — FMEA-side domain contract tests."""

import pytest
from pydantic import ValidationError

from fmea_agent.domain.fmea import (
    AnalysisContext,
    AnalysisStatus,
    EffectLevel,
    Evidence,
    FailureCauseCandidate,
    FailureEffectCandidate,
    FailureModeCandidate,
    FMEAItem,
    FMEAMethod,
    KnowledgeStatus,
    RiskAssessment,
    RiskStatus,
)
from fmea_agent.domain.system_model import Component


def test_analysis_context_defaults() -> None:
    ctx = AnalysisContext(id="an-001", title="Hydraulic System FMEA")
    assert ctx.id == "an-001"
    assert ctx.method == FMEAMethod.AIAG_VDA
    assert ctx.status == AnalysisStatus.NOT_STARTED
    assert ctx.scope == ""
    assert ctx.assumptions == []
    assert ctx.exclusions == []
    assert ctx.created_at is not None
    assert ctx.updated_at is not None


def test_analysis_context_missing_id_raises() -> None:
    with pytest.raises(ValidationError):
        AnalysisContext(title="No ID")  # type: ignore[call-arg]


def test_analysis_context_serializes_method_as_string() -> None:
    ctx = AnalysisContext(id="an-001", title="T")
    data = ctx.model_dump(mode="json")
    assert data["method"] == "AIAG_VDA"
    assert data["status"] == "NOT_STARTED"


def test_fmea_item_minimal_construction() -> None:
    item = FMEAItem(
        id="fmea-item-1",
        name="Hydraulic Pump",
        canonical_system_element_id="hydraulic-pump",
    )
    assert item.parent_item_id is None
    assert item.source_refs == []


def test_fmea_item_requires_canonical_element_id() -> None:
    with pytest.raises(ValidationError):
        FMEAItem(id="fmea-item-1", name="Hydraulic Pump")  # type: ignore[call-arg]


def test_fmea_item_missing_id_raises() -> None:
    with pytest.raises(ValidationError):
        FMEAItem(name="Hydraulic Pump", canonical_system_element_id="hydraulic-pump")  # type: ignore[call-arg]


def test_component_and_fmea_item_stay_distinct_concepts() -> None:
    component = Component(id="hydraulic-pump", name="Hydraulic Pump")
    item = FMEAItem(
        id="fmea-item-1",
        name="Hydraulic Pump",
        canonical_system_element_id=component.id,
    )
    assert type(component) is not type(item)
    assert item.canonical_system_element_id == component.id


def test_evidence_requires_source() -> None:
    ev = Evidence(source="demo-failure-library:001")
    assert ev.source == "demo-failure-library:001"
    with pytest.raises(ValidationError):
        Evidence()  # type: ignore[call-arg]


def test_failure_mode_candidate_defaults() -> None:
    mode = FailureModeCandidate(value="Loss of hydraulic pressure")
    assert mode.status == KnowledgeStatus.CANDIDATE
    assert mode.causes == []
    assert mode.effects == []
    assert mode.evidence == []


def test_failure_mode_candidate_with_cause_effect_evidence() -> None:
    mode = FailureModeCandidate(
        value="Loss of hydraulic pressure",
        item_id="fmea-item-1",
        function_id="provide-pressure",
        causes=[
            FailureCauseCandidate(
                value="Demo mechanical failure",
                mechanism="mechanical degradation",
            )
        ],
        effects=[
            FailureEffectCandidate(
                level=EffectLevel.LOCAL,
                value="Required outlet pressure is unavailable",
            )
        ],
        evidence=[Evidence(source="demo-failure-library:001")],
    )
    assert mode.causes[0].value == "Demo mechanical failure"
    assert mode.causes[0].mechanism == "mechanical degradation"
    assert mode.effects[0].level == EffectLevel.LOCAL


def test_failure_mode_ids_are_domain_ids_not_display_names() -> None:
    component = Component(id="hydraulic-pump", name="Hydraulic Pump")
    mode = FailureModeCandidate(
        value="Loss of hydraulic pressure",
        item_id=component.id,
        function_id="provide-pressure",
    )
    assert mode.item_id == "hydraulic-pump"
    assert mode.item_id != component.name
    assert mode.function_id == "provide-pressure"
    assert mode.function_id != "Provide Hydraulic Pressure"


def test_candidate_status_rejects_unknown_value() -> None:
    with pytest.raises(ValidationError):
        FailureModeCandidate(value="x", status="NOT_A_STATUS")  # type: ignore[arg-type]


def test_effect_level_enum_values() -> None:
    assert set(EffectLevel) == {
        EffectLevel.LOCAL,
        EffectLevel.NEXT_HIGHER_LEVEL,
        EffectLevel.END_EFFECT,
    }


def test_effect_rejects_invalid_level() -> None:
    with pytest.raises(ValidationError):
        FailureEffectCandidate(level="SYSTEM", value="boom")  # type: ignore[arg-type]


def test_knowledge_status_enum_values() -> None:
    assert set(KnowledgeStatus) == {
        KnowledgeStatus.FACT,
        KnowledgeStatus.RETRIEVED_KNOWLEDGE,
        KnowledgeStatus.INFERENCE,
        KnowledgeStatus.CANDIDATE,
        KnowledgeStatus.REVIEWED,
        KnowledgeStatus.APPROVED,
        KnowledgeStatus.UNKNOWN,
    }


def test_risk_assessment_defaults_to_not_evaluated() -> None:
    risk = RiskAssessment()
    assert risk.status == RiskStatus.NOT_EVALUATED
    assert risk.strategy is None


def test_risk_assessment_evaluated_requires_strategy() -> None:
    with pytest.raises(ValidationError):
        RiskAssessment(status=RiskStatus.EVALUATED)
    risk = RiskAssessment(status=RiskStatus.EVALUATED, strategy="authorized-rule-source-v1")
    assert risk.strategy == "authorized-rule-source-v1"


def test_candidate_serialization_matches_spec_shape() -> None:
    mode = FailureModeCandidate(
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
    data = mode.model_dump(mode="json")
    assert data["value"] == "Loss of hydraulic pressure"
    assert data["status"] == "CANDIDATE"
    assert data["causes"][0]["value"] == "Demo mechanical failure"
    assert data["effects"][0]["level"] == "LOCAL"
    assert data["evidence"][0]["source"] == "demo-failure-library:001"
