"""Minimal Canonical System Model (MVP-0 scope) — system-side domain contracts."""

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Origin pointer for an engineering fact; retains source-side identity."""

    source_type: str
    source_uri: str
    source_element_id: str
    source_version: str | None = None
    adapter: str | None = None
    repository: str | None = None
    project: str | None = None
    commit: str | None = None
    branch: str | None = None
    locator: str | None = None


class System(BaseModel):
    """System under analysis."""

    id: str
    name: str
    description: str | None = None
    source_refs: list[SourceReference] = Field(default_factory=list)


class Component(BaseModel):
    """Component inside a system.

    Engineering-side fact. Kept distinct from the FMEA-side FMEAItem; the two are
    linked by canonical element id.
    """

    id: str
    name: str
    parent_id: str | None = None
    component_type: str | None = None
    source_refs: list[SourceReference] = Field(default_factory=list)


class Function(BaseModel):
    """Intended behavior/function allocated to system elements."""

    id: str
    name: str
    description: str | None = None
    allocated_to: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceReference] = Field(default_factory=list)
