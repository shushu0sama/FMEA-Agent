"""In-memory SystemModelRepository implementations backed by domain objects."""

from collections.abc import Iterable

from fmea_agent.domain.system_model import (
    CanonicalSystemModel,
    Component,
    Function,
    System,
)


class InMemorySystemModelRepository:
    """Fixture-backed read-side system facts for MVP-0."""

    def __init__(
        self,
        system: System | None = None,
        components: Iterable[Component] = (),
        functions: Iterable[Function] = (),
    ) -> None:
        self._system = system
        self._components = {c.id: c for c in components}
        self._functions = {f.id: f for f in functions}

    def get_system(self, system_id: str) -> System | None:
        if self._system is None or self._system.id != system_id:
            return None
        return self._system

    def get_component(self, component_id: str) -> Component | None:
        return self._components.get(component_id)

    def list_components(self, system_id: str) -> list[Component]:
        return [c for c in self._components.values() if c.parent_id == system_id]

    def list_functions(self, element_id: str) -> list[Function]:
        return [f for f in self._functions.values() if element_id in f.allocated_to]


class CanonicalSystemModelRepository:
    """Read-side SystemModelRepository over a mapped CanonicalSystemModel (MVP-1E).

    Serves the existing ``SystemModelRepository`` port from the 1D mapping
    output. No SysML re-parsing and no parser runtime objects: the input is
    the project-owned canonical aggregate.
    """

    def __init__(self, model: CanonicalSystemModel) -> None:
        self._model = model

    def get_system(self, system_id: str) -> System | None:
        if self._model.system.id != system_id:
            return None
        return self._model.system

    def get_component(self, component_id: str) -> Component | None:
        return next(
            (c for c in self._model.components if c.id == component_id), None
        )

    def list_components(self, system_id: str) -> list[Component]:
        return [c for c in self._model.components if c.parent_id == system_id]

    def list_functions(self, element_id: str) -> list[Function]:
        return [f for f in self._model.functions if element_id in f.allocated_to]
