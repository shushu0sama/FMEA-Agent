"""Parser-neutral SysML source-fact snapshot contracts (MVP-1B).

Project-owned data envelopes for parser/API facts. No dependency on any
SysML parser runtime (no opensysml / gRPC / protobuf). Normative semantics
live in docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class SysMLSource(BaseModel):
    """Provenance of the source behind a snapshot."""

    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(min_length=1)
    source_path: str | None = None
    source_version: str | None = None
    model_hash: str | None = None
    parser: str = Field(min_length=1)
    parser_version: str | None = None
    runtime_version: str | None = None
    adapter: str = Field(min_length=1)

    @model_validator(mode="after")
    def _require_path_for_file_mode(self) -> Self:
        if self.source_type == "sysml_file" and not self.source_path:
            raise ValueError("source_path is required when source_type is 'sysml_file'")
        return self


class SysMLTypeFacts(BaseModel):
    """Typing facts observed for an element; all-None means not observed."""

    model_config = ConfigDict(extra="forbid")

    declared: str | None = None
    resolved_id: str | None = None
    resolved_kind: str | None = None


class SysMLElementFact(BaseModel):
    """A single source element fact (parser-native identity, no FMEA semantics)."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    metatype: str = Field(min_length=1)
    name: str | None = None
    owner_id: str | None = None
    type_facts: SysMLTypeFacts | None = None
    properties: dict[str, JsonValue] = Field(default_factory=dict)


class SysMLRelationshipFact(BaseModel):
    """An explicit relationship fact; source must be in-snapshot, target is open-world."""

    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    properties: dict[str, JsonValue] = Field(default_factory=dict)


class SysMLDiagnostic(BaseModel):
    """Project-owned normalized diagnostic envelope (parser or adapter origin)."""

    model_config = ConfigDict(extra="forbid")

    severity: str = Field(min_length=1)
    message: str = Field(min_length=1)
    file: str | None = None
    start_line: int | None = None
    start_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None
    span: JsonValue | None = None


class SysMLFactSnapshot(BaseModel):
    """Source-fact envelope; not the Canonical System Model."""

    model_config = ConfigDict(extra="forbid")

    source: SysMLSource
    elements: list[SysMLElementFact] = Field(default_factory=list)
    relationships: list[SysMLRelationshipFact] = Field(default_factory=list)
    diagnostics: list[SysMLDiagnostic] = Field(default_factory=list)
    load_status: Literal["ok", "partial"]

    @model_validator(mode="after")
    def _validate_facts(self) -> Self:
        errors: list[str] = []
        seen: set[str] = set()
        for element in self.elements:
            if element.source_id in seen:
                errors.append(f"duplicate element source_id {element.source_id!r}")
            seen.add(element.source_id)
        for relationship in self.relationships:
            if relationship.source_id not in seen:
                errors.append(
                    f"relationship source_id {relationship.source_id!r} "
                    "does not reference an element"
                )
        if self.load_status == "ok" and any(
            diagnostic.severity == "error" for diagnostic in self.diagnostics
        ):
            errors.append("load_status is 'ok' but error diagnostics are present")
        if errors:
            raise ValueError("; ".join(errors))
        return self
