"""Minimal FMEA domain contracts (MVP-0 scope) — failure-analysis side."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from fmea_agent.domain.system_model import SourceReference


class KnowledgeStatus(StrEnum):
    """Authority status distinguishing facts, retrieved knowledge, inference, review."""

    FACT = "FACT"
    RETRIEVED_KNOWLEDGE = "RETRIEVED_KNOWLEDGE"
    INFERENCE = "INFERENCE"
    CANDIDATE = "CANDIDATE"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    UNKNOWN = "UNKNOWN"


class FMEAMethod(StrEnum):
    AIAG_VDA = "AIAG_VDA"


class AnalysisStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class EffectLevel(StrEnum):
    LOCAL = "LOCAL"
    NEXT_HIGHER_LEVEL = "NEXT_HIGHER_LEVEL"
    END_EFFECT = "END_EFFECT"


class RiskStatus(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    UNKNOWN = "UNKNOWN"
    EVALUATED = "EVALUATED"


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AnalysisContext(BaseModel):
    """Planning & Preparation stage result: scope and metadata for one analysis run."""

    id: str
    title: str
    method: FMEAMethod = FMEAMethod.AIAG_VDA
    scope: str = ""
    system_id: str | None = None
    system_version: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    status: AnalysisStatus = AnalysisStatus.NOT_STARTED
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class FMEAItem(BaseModel):
    """The analyzed item inside the current AnalysisContext.

    Analysis-side identity; linked to an engineering-side canonical element by
    canonical_system_element_id. Never merged with Component.
    """

    id: str
    name: str
    canonical_system_element_id: str
    parent_item_id: str | None = None
    source_refs: list[SourceReference] = Field(default_factory=list)


class Evidence(BaseModel):
    """Pointer to supporting evidence for a candidate or fact."""

    source: str


class FailureCauseCandidate(BaseModel):
    """Candidate cause that can lead to a failure mode.

    `mechanism` stays free-text in MVP-0: Failure Mechanism is an independent
    concept with no dedicated model yet, and must not be mislabeled as a cause.
    """

    value: str
    status: KnowledgeStatus = KnowledgeStatus.CANDIDATE
    mechanism: str | None = None
    description: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class FailureEffectCandidate(BaseModel):
    """Candidate effect of a failure mode, classified by effect level."""

    level: EffectLevel
    value: str
    status: KnowledgeStatus = KnowledgeStatus.CANDIDATE
    affected_item_id: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class FailureModeCandidate(BaseModel):
    """Candidate failure mode: the manner in which an item/function fails to meet intent.

    `item_id` and `function_id` hold stable domain identifiers (e.g. Component.id,
    Function.id) — never display names; names belong to the linked objects.
    """

    value: str
    status: KnowledgeStatus = KnowledgeStatus.CANDIDATE
    item_id: str | None = None
    function_id: str | None = None
    description: str | None = None
    causes: list[FailureCauseCandidate] = Field(default_factory=list)
    effects: list[FailureEffectCandidate] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    """Risk result declared by a RiskStrategy.

    MVP-0 only produces NOT_EVALUATED; S/O/D/AP values are never invented.
    """

    status: RiskStatus = RiskStatus.NOT_EVALUATED
    strategy: str | None = None

    @model_validator(mode="after")
    def _evaluated_requires_strategy(self) -> "RiskAssessment":
        if self.status == RiskStatus.EVALUATED and not self.strategy:
            raise ValueError("An evaluated risk must declare its strategy/source")
        return self
