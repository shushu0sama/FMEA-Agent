"""Provider-neutral D2 evidence and self-contained input contracts."""

import hashlib
import json
from graphlib import CycleError, TopologicalSorter
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from fmea_agent.domain.system_model import (
    CanonicalSystemModel,
    Component,
    Function,
    MappingNotice,
    SourceReference,
    System,
)

NonBlank = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
SourceKind = Literal["sysml", "document", "bom", "user", "neo4j"]


class DemoModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, revalidate_instances="always")


class EvidenceRef(DemoModel):
    id: NonBlank
    source_kind: SourceKind
    locator: NonBlank
    text: str
    content_sha256: Sha256 | None = None
    derived_from: list[NonBlank] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class FieldValue(DemoModel):
    value: NonBlank | None
    status: Literal["FACT", "RETRIEVED_KNOWLEDGE", "INFERENCE", "UNKNOWN"]
    evidence_ids: list[NonBlank] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_authority(self) -> Self:
        if self.value is None and self.status != "UNKNOWN":
            raise ValueError("a null value must be UNKNOWN")
        if self.status in {"FACT", "RETRIEVED_KNOWLEDGE"} and not self.evidence_ids:
            raise ValueError("FACT/RETRIEVED_KNOWLEDGE require evidence_ids")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("duplicate evidence_ids")
        return self


class InputFileRecord(DemoModel):
    id: NonBlank
    filename: NonBlank
    kind: Literal["sysml", "document", "bom"]
    sha256: Sha256
    size_bytes: int = Field(ge=0, le=5 * 1024 * 1024)
    derived_from: list[NonBlank] = Field(default_factory=list)
    parser: str | None = None
    parser_version: str | None = None
    runtime_version: str | None = None

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if any(char in value for char in "/\\:\x00") or value in {".", ".."}:
            raise ValueError("filename must be a basename, not a path")
        return value


def input_digest(files: list[InputFileRecord]) -> str:
    """Hash the ordered role manifest, including versions; never local file paths."""
    payload = [file.model_dump(mode="json") for file in files]
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_registry(evidence: list[EvidenceRef], file_ids: set[str]) -> set[str]:
    ids = {ref.id for ref in evidence}
    if len(ids) != len(evidence) or ids & file_ids:
        raise ValueError("duplicate or ambiguous evidence ID")
    known = ids | file_ids
    for ref in evidence:
        if not set(ref.derived_from) <= known or ref.id in ref.derived_from:
            raise ValueError("evidence derived_from contains an unknown or self reference")
    _acyclic({ref.id: ref.derived_from for ref in evidence})
    return ids


def _acyclic(graph: dict[str, list[str]]) -> None:
    try:
        TopologicalSorter(graph).prepare()
    except CycleError as exc:
        raise ValueError("derived_from provenance must not contain cycles") from exc


def _check_keys(value: object, model: type[BaseModel]) -> None:
    if isinstance(value, dict) and set(value) - model.model_fields.keys():
        raise ValueError(f"extra fields in {model.__name__} are forbidden in Demo inputs")


class LoadedInputs(DemoModel):
    files: list[InputFileRecord]
    model: CanonicalSystemModel
    evidence: list[EvidenceRef] = Field(default_factory=list)
    missing_files: list[Literal["design", "bom"]] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    input_digest: Sha256

    @field_validator("model", mode="before")
    @classmethod
    def forbid_extra_csm_fields(cls, value: object) -> object:
        # Keep the legacy CSM API unchanged; reject discarded fields at this boundary.
        _check_keys(value, CanonicalSystemModel)
        if isinstance(value, dict):
            _check_keys(value.get("system"), System)
            groups: list[tuple[str, type[BaseModel]]] = [
                ("components", Component),
                ("functions", Function),
                ("notices", MappingNotice),
            ]
            entities = [value.get("system")]
            for key, entity_type in groups:
                group = value.get(key, [])
                if isinstance(group, list):
                    for entity in group:
                        _check_keys(entity, entity_type)
                    entities.extend(group)
            for entity in entities:
                if isinstance(entity, dict) and isinstance(entity.get("source_refs"), list):
                    for ref in entity["source_refs"]:
                        _check_keys(ref, SourceReference)
        return value

    @model_validator(mode="after")
    def validate_inputs(self) -> Self:
        file_ids = {file.id for file in self.files}
        kinds = [file.kind for file in self.files]
        if (
            len(file_ids) != len(self.files)
            or len(set(kinds)) != len(kinds)
            or "sysml" not in kinds
        ):
            raise ValueError("one sysml and at most one design/BOM file; IDs must be unique")
        for file in self.files:
            if not set(file.derived_from) <= file_ids or file.id in file.derived_from:
                raise ValueError("file derived_from contains an unknown or self reference")
        validate_registry(self.evidence, file_ids)
        _acyclic({file.id: file.derived_from for file in self.files})
        entities: list[System | Component | Function] = [
            self.model.system,
            *self.model.components,
            *self.model.functions,
        ]
        for entity in entities:
            for ref in entity.source_refs:
                if ref.source_uri not in file_ids:
                    raise ValueError("CSM source_uri must reference an input file ID")
        if self.input_digest != input_digest(self.files):
            raise ValueError("input_digest does not match the input manifest")
        expected_missing = {
            name for name, kind in [("design", "document"), ("bom", "bom")] if kind not in kinds
        }
        if set(self.missing_files) != expected_missing:
            raise ValueError("missing_files does not match input file roles")
        return self
