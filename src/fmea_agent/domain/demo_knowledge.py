"""Bounded source-knowledge contracts; no database/provider imports."""

from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from fmea_agent.domain.demo_evidence import DemoModel, EvidenceRef, NonBlank


class KnowledgeQuery(DemoModel):
    terms: list[NonBlank] = Field(min_length=1, max_length=5)
    scope: Literal["SOURCE_LOOKUP", "TARGET_ANALYSIS"]
    component_id: NonBlank | None = None
    function_id: NonBlank | None = None
    limit: int = Field(default=20, ge=1, le=20)

    @field_validator("terms")
    @classmethod
    def validate_terms(cls, terms: list[str]) -> list[str]:
        if any(len(term) > 80 for term in terms):
            raise ValueError("query terms cannot exceed 80 characters")
        return terms

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope == "TARGET_ANALYSIS" and (not self.component_id or not self.function_id):
            raise ValueError("TARGET_ANALYSIS requires component and function IDs")
        if self.scope == "SOURCE_LOOKUP" and (self.component_id or self.function_id):
            raise ValueError("SOURCE_LOOKUP cannot assert a target association")
        return self


class KnowledgeHit(DemoModel):
    id: NonBlank
    name: NonBlank
    context: list[EvidenceRef] = Field(default_factory=list)
    associations: list[EvidenceRef] = Field(default_factory=list)
    applicability: Literal["UNKNOWN", "REJECTED", "SOURCE_CONTEXT_ONLY"]
    reasons: list[str] = Field(default_factory=list)


class RetrievalResult(DemoModel):
    status: Literal["HITS", "NO_MATCH", "ERROR"]
    hits: list[KnowledgeHit] = Field(default_factory=list, max_length=20)
    terms: list[NonBlank] = Field(default_factory=list, max_length=5)
    truncated: bool = False
    error_code: NonBlank | None = None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.status == "HITS" and (not self.hits or self.error_code):
            raise ValueError("HITS requires hits and no error")
        if self.status == "NO_MATCH" and (self.hits or self.error_code or self.truncated):
            raise ValueError("NO_MATCH must be empty with no error or truncation")
        if self.status == "ERROR" and (self.hits or not self.error_code):
            raise ValueError("ERROR requires an error code and no hits")
        if len({hit.id for hit in self.hits}) != len(self.hits):
            raise ValueError("duplicate knowledge hit ID")
        if any(len(term) > 80 for term in self.terms):
            raise ValueError("query terms cannot exceed 80 characters")
        return self
