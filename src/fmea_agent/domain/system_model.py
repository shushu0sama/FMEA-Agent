"""Minimal Canonical System Model — system-side domain contracts."""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


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


MappingStatus = Literal[
    "CONFIRMED", "TENTATIVE", "NEEDS_RESEARCH", "REJECTED", "DEFERRED"
]


class MappingNotice(BaseModel):
    """Record of how a source element (or the snapshot as a whole) was treated.

    ``source_id`` is ``None`` for model-level notices (e.g. a partial load).
    """

    source_id: str | None = None
    status: MappingStatus
    message: str


class CanonicalSystemModel(BaseModel):
    """Aggregate of mapped canonical facts for one system model."""

    system: System
    components: list[Component] = Field(default_factory=list)
    functions: list[Function] = Field(default_factory=list)
    notices: list[MappingNotice] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_identities(self) -> Self:
        errors: list[str] = []
        seen: set[str] = set()
        for entity_id in (
            [self.system.id]
            + [c.id for c in self.components]
            + [f.id for f in self.functions]
        ):
            if entity_id in seen:
                errors.append(f"duplicate canonical id {entity_id!r}")
            seen.add(entity_id)
        resolvable = {self.system.id} | {c.id for c in self.components}
        for component in self.components:
            if (
                component.parent_id is not None
                and component.parent_id not in resolvable
            ):
                errors.append(
                    f"component {component.id!r} parent_id "
                    f"{component.parent_id!r} does not resolve"
                )
        for function in self.functions:
            for target in function.allocated_to:
                if target not in resolvable:
                    errors.append(
                        f"function {function.id!r} allocated_to "
                        f"{target!r} does not resolve"
                    )
        if errors:
            raise ValueError("; ".join(errors))
        return self
