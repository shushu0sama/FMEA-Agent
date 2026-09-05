"""Serializable Demo session snapshots; adapters and locks belong to the service."""

from typing import Literal, Self

from pydantic import Field, model_validator

from fmea_agent.domain.demo_analysis import (
    CandidateReport,
    DiagnosticReport,
    GenerationResult,
    IntakeResult,
)
from fmea_agent.domain.demo_evidence import DemoModel, LoadedInputs, NonBlank, Sha256
from fmea_agent.domain.demo_knowledge import RetrievalResult


class DemoSession(DemoModel):
    id: NonBlank
    input_digest: Sha256
    phase: Literal["NEW", "WAITING_INPUT", "READY", "RUNNING", "COMPLETE", "FAILED"] = "NEW"
    inputs: LoadedInputs
    intake: IntakeResult | None = None
    retrieval: RetrievalResult | None = None
    generation: GenerationResult | None = None
    report: CandidateReport | None = None
    diagnostic: DiagnosticReport | None = None
    question_rounds: int = Field(default=0, ge=0, le=2)
    handled_request_ids: list[NonBlank] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        if self.input_digest != self.inputs.input_digest:
            raise ValueError("session input digest differs from snapshot")
        if len(set(self.handled_request_ids)) != len(self.handled_request_ids):
            raise ValueError("duplicate handled request IDs")
        if self.phase == "COMPLETE":
            if self.report is None or self.generation is None or not self.generation.rows:
                raise ValueError("COMPLETE requires a nonempty candidate report")
        elif self.report is not None:
            raise ValueError("only COMPLETE may carry a candidate report")
        if self.phase == "FAILED":
            if self.diagnostic is None or not self.errors or self.generation is not None:
                raise ValueError("FAILED requires diagnostic, errors and no generation")
        elif self.diagnostic is not None:
            raise ValueError("only FAILED may carry a diagnostic")
        return self


class DemoGraphState(DemoModel):
    session: DemoSession
    operation: Literal["intake", "analyze"]
    message: str = ""
    continue_unknown: bool = False
    allow_without_retrieval: bool = False
