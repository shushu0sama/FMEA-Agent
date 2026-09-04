"""In-memory SystemModelRepository backed by plain Python collections."""

from collections.abc import Iterable

from fmea_agent.domain.system_model import Component, Function, System


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
