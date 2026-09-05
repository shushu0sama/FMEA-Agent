"""Intake, candidate and diagnostic envelopes for Demo V1, not engineering approval."""

from typing import Literal, Self

from pydantic import Field, model_validator

from fmea_agent.domain.demo_evidence import (
    DemoModel,
    EvidenceRef,
    FieldValue,
    LoadedInputs,
    NonBlank,
    Sha256,
    validate_registry,
)
from fmea_agent.domain.demo_knowledge import RetrievalResult

EffectLevel = Literal["LOCAL", "NEXT_HIGHER_LEVEL", "END_EFFECT"]


class IntakeResult(DemoModel):
    component_id: NonBlank | None = None
    function_id: NonBlank | None = None
    context: dict[str, FieldValue] = Field(default_factory=dict)
    questions: list[str] = Field(default_factory=list)
    status: Literal["WAITING_INPUT", "READY", "BLOCKED"]

    @model_validator(mode="after")
    def validate_ready(self) -> Self:
        if self.status == "READY" and (not self.component_id or not self.function_id):
            raise ValueError("READY intake requires target IDs")
        return self


class FailureRow(DemoModel):
    mode: FieldValue
    causes: list[FieldValue] = Field(default_factory=list)
    mechanism: FieldValue
    effects: dict[EffectLevel, FieldValue]
    existing_controls: list[FieldValue] = Field(default_factory=list)
    suggested_actions: list[FieldValue] = Field(default_factory=list)
    validation_suggestions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_levels(self) -> Self:
        if set(self.effects) != {"LOCAL", "NEXT_HIGHER_LEVEL", "END_EFFECT"}:
            raise ValueError("all three effect levels must be present, even if UNKNOWN")
        return self

    def fields(self) -> list[FieldValue]:
        return [
            self.mode,
            *self.causes,
            self.mechanism,
            *self.effects.values(),
            *self.existing_controls,
            *self.suggested_actions,
        ]


class GenerationResult(DemoModel):
    rows: list[FailureRow] = Field(default_factory=list, max_length=8)
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


def target_is_valid(inputs: LoadedInputs, component_id: str, function_id: str) -> bool:
    return any(c.id == component_id for c in inputs.model.components) and any(
        f.id == function_id and component_id in f.allocated_to for f in inputs.model.functions
    )


class CandidateReport(DemoModel):
    schema_version: Literal["demo-v1"]
    run_id: NonBlank
    input_digest: Sha256
    input_snapshot: LoadedInputs
    status: Literal["CANDIDATE"]
    component_id: NonBlank
    function_id: NonBlank
    context: dict[str, FieldValue] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    retrieval: RetrievalResult
    generation: GenerationResult
    exclusions: list[str] = Field(default_factory=list)
    risk_status: Literal["NOT_EVALUATED"]
    optimization_status: Literal["SKIPPED"]
    usage: dict[str, int | str | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        inputs = self.input_snapshot
        if self.input_digest != inputs.input_digest:
            raise ValueError("report input_digest differs from its snapshot")
        if not target_is_valid(inputs, self.component_id, self.function_id):
            raise ValueError("component/function target is not allocated in the input model")
        if inputs.conflicts:
            raise ValueError("unresolved input conflicts block a successful report")
        ids = validate_registry(self.evidence, {file.id for file in inputs.files})
        registry = {ref.id: ref for ref in self.evidence}
        required = list(inputs.evidence)
        for hit in self.retrieval.hits:
            required.extend([*hit.context, *hit.associations])
        for ref in required:
            if registry.get(ref.id) != ref:
                raise ValueError("input/retrieval evidence must be preserved unchanged in registry")
        fields = list(self.context.values())
        for row in self.generation.rows:
            fields.extend(row.fields())
        if any(not set(value.evidence_ids) <= ids for value in fields):
            raise ValueError("field references evidence outside this report registry")
        return self


class DiagnosticReport(DemoModel):
    schema_version: Literal["demo-v1-diagnostic"]
    run_id: NonBlank
    status: Literal["FAILED"]
    input_snapshot: LoadedInputs
    errors: list[NonBlank] = Field(min_length=1)
    usage: dict[str, int | str | None] = Field(default_factory=dict)
