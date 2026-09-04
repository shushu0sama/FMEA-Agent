"""SysML -> Canonical System Model mapping (MVP-1D).

Root selection policy v1 (explicit, deterministic):

- with ``root_source_id``: that element must be a named partUsage in the
  snapshot and becomes the System root;
- without it: candidates are named partUsage elements with no partUsage
  ancestor; exactly one candidate is required, otherwise
  ``CanonicalMappingError``.

Mapping rules v1 (registered in
``docs/architecture/SYSML_TO_CANONICAL_MAPPING.md``):

- selected root partUsage -> ``System``;
- named partUsage inside the root's containment subtree -> ``Component``
  (parent = nearest mapped partUsage ancestor);
- partUsage outside that subtree -> notice (DEFERRED);
- named actionUsage with typing evidence (``type_facts.resolved_id`` plus
  ``resolved_kind == "actionDef"``) whose nearest partUsage ancestor is
  inside the selected root subtree -> ``Function`` with
  ``allocated_to = [canonical id of that ancestor]`` (evidence: real owner
  traversal, never name/FQN matching);
- typed actionUsage with no partUsage ancestor (package/file-level) ->
  notice (NEEDS_RESEARCH, attribution unconfirmed) — not silently added;
- typed actionUsage under another part tree -> notice (DEFERRED);
- actionUsage without typing evidence (C4) -> notice (NEEDS_RESEARCH),
  never fabricated;
- partDef / actionDef / package / other metatypes -> notices only.

Canonical ids are generated here (``system-1``, ``component-N``,
``function-N``, per-kind counters in snapshot order). They are
deterministic for identical snapshots but are not cross-version stable and
are never derived from source identity; source identity is retained in
``SourceReference.source_element_id``.
"""

from __future__ import annotations

from fmea_agent.adapters.sysml.contracts import SysMLElementFact, SysMLFactSnapshot
from fmea_agent.adapters.sysml.exceptions import CanonicalMappingError
from fmea_agent.domain.system_model import (
    CanonicalSystemModel,
    Component,
    Function,
    MappingNotice,
    SourceReference,
    System,
)


class CanonicalSystemMapper:
    """Maps a parser-neutral SysMLFactSnapshot into the Canonical System Model."""

    def map_snapshot(
        self,
        snapshot: SysMLFactSnapshot,
        *,
        root_source_id: str | None = None,
    ) -> CanonicalSystemModel:
        """Map ``snapshot`` into a CanonicalSystemModel.

        Raises:
            CanonicalMappingError: no system root could be selected (see the
                root selection policy in the module docstring).
        """
        elements = {element.source_id: element for element in snapshot.elements}
        root = self._select_root(elements, root_source_id)
        assert root.name is not None
        notices: list[MappingNotice] = []
        if snapshot.load_status == "partial":
            notices.append(
                MappingNotice(
                    status="NEEDS_RESEARCH",
                    message=(
                        "snapshot load_status is 'partial'; the canonical model "
                        "may be incomplete"
                    ),
                )
            )
        system = System(
            id="system-1",
            name=root.name,
            source_refs=[_source_ref(snapshot, root)],
        )
        subtree_parts = [
            element
            for element in snapshot.elements
            if element.metatype == "partUsage"
            and element.source_id != root.source_id
            and element.name is not None
            and _in_subtree(elements, root, element)
        ]
        component_ids = {
            element.source_id: f"component-{index}"
            for index, element in enumerate(subtree_parts, start=1)
        }
        components: list[Component] = []
        functions: list[Function] = []
        function_counter = 0
        for element in snapshot.elements:
            if element.source_id == root.source_id:
                continue
            if element.metatype == "partUsage":
                if element.name is None:
                    notices.append(
                        MappingNotice(
                            source_id=element.source_id,
                            status="NEEDS_RESEARCH",
                            message=(
                                "partUsage has no name; System and Component "
                                "require a name"
                            ),
                        )
                    )
                    continue
                if element.source_id not in component_ids:
                    notices.append(
                        MappingNotice(
                            source_id=element.source_id,
                            status="DEFERRED",
                            message=(
                                "partUsage is outside the selected system root's "
                                "containment subtree; not mapped in MVP-1D"
                            ),
                        )
                    )
                    continue
                parent = _part_usage_ancestors(elements, element)[0]
                if parent.source_id == root.source_id:
                    parent_id: str | None = system.id
                elif parent.source_id in component_ids:
                    parent_id = component_ids[parent.source_id]
                else:
                    parent_id = None
                if parent_id is None:
                    notices.append(
                        MappingNotice(
                            source_id=element.source_id,
                            status="NEEDS_RESEARCH",
                            message=(
                                "partUsage parent cannot be represented (unnamed "
                                "or unmapped partUsage ancestor)"
                            ),
                        )
                    )
                    continue
                components.append(
                    Component(
                        id=component_ids[element.source_id],
                        name=element.name,
                        parent_id=parent_id,
                        source_refs=[_source_ref(snapshot, element)],
                    )
                )
            elif element.metatype == "actionUsage":
                if element.name is None:
                    notices.append(
                        MappingNotice(
                            source_id=element.source_id,
                            status="NEEDS_RESEARCH",
                            message="actionUsage has no name; Function requires a name",
                        )
                    )
                elif not _typing_to_action_def(element):
                    notices.append(
                        MappingNotice(
                            source_id=element.source_id,
                            status="NEEDS_RESEARCH",
                            message=(
                                "actionUsage typing to an actionDef is not "
                                "confirmed (C4); not mapped to Function"
                            ),
                        )
                    )
                else:
                    allocated_to = self._function_allocation(
                        elements, root, element, component_ids, system.id, notices
                    )
                    if allocated_to is None:
                        continue
                    function_counter += 1
                    functions.append(
                        Function(
                            id=f"function-{function_counter}",
                            name=element.name,
                            allocated_to=[allocated_to],
                            source_refs=[_source_ref(snapshot, element)],
                        )
                    )
            elif element.metatype == "partDef":
                notices.append(
                    MappingNotice(
                        source_id=element.source_id,
                        status="NEEDS_RESEARCH",
                        message=(
                            "PartDefinition is type metadata; direct mapping to "
                            "Component is forbidden"
                        ),
                    )
                )
            elif element.metatype == "actionDef":
                notices.append(
                    MappingNotice(
                        source_id=element.source_id,
                        status="NEEDS_RESEARCH",
                        message=(
                            "ActionDefinition is behavior/type metadata; not "
                            "directly mapped to Function"
                        ),
                    )
                )
            elif element.metatype == "package":
                notices.append(
                    MappingNotice(
                        source_id=element.source_id,
                        status="TENTATIVE",
                        message="package is source context; not mapped to a canonical entity",
                    )
                )
            else:
                notices.append(
                    MappingNotice(
                        source_id=element.source_id,
                        status="DEFERRED",
                        message=(
                            f"metatype {element.metatype!r} is not mapped in MVP-1D"
                        ),
                    )
                )
        return CanonicalSystemModel(
            system=system,
            components=components,
            functions=functions,
            notices=notices,
        )

    def _function_allocation(
        self,
        elements: dict[str, SysMLElementFact],
        root: SysMLElementFact,
        element: SysMLElementFact,
        component_ids: dict[str, str],
        system_id: str,
        notices: list[MappingNotice],
    ) -> str | None:
        """Resolve the canonical allocation target of a typed actionUsage.

        Returns the canonical id of the nearest mapped partUsage ancestor,
        or None (with a notice appended) when attribution cannot be
        confirmed. Never derives allocation from names or FQN strings.
        """
        ancestors = _part_usage_ancestors(elements, element)
        if not ancestors:
            notices.append(
                MappingNotice(
                    source_id=element.source_id,
                    status="NEEDS_RESEARCH",
                    message=(
                        "actionUsage has no partUsage ancestor; attribution to "
                        "the selected system cannot be confirmed; not mapped "
                        "to Function"
                    ),
                )
            )
            return None
        nearest = ancestors[0]
        if nearest.source_id == root.source_id:
            return system_id
        if nearest.source_id in component_ids:
            return component_ids[nearest.source_id]
        if _in_subtree(elements, root, nearest):
            notices.append(
                MappingNotice(
                    source_id=element.source_id,
                    status="NEEDS_RESEARCH",
                    message=(
                        "actionUsage partUsage ancestor cannot be represented "
                        "(unnamed or unmapped partUsage)"
                    ),
                )
            )
            return None
        notices.append(
            MappingNotice(
                source_id=element.source_id,
                status="DEFERRED",
                message=(
                    "actionUsage belongs to a partUsage outside the selected "
                    "system root's containment subtree; not mapped in MVP-1D"
                ),
            )
        )
        return None

    def _select_root(
        self, elements: dict[str, SysMLElementFact], root_source_id: str | None
    ) -> SysMLElementFact:
        if root_source_id is not None:
            root = elements.get(root_source_id)
            if root is None:
                raise CanonicalMappingError(
                    f"root_source_id {root_source_id!r} does not reference any "
                    "element in the snapshot"
                )
            if root.metatype != "partUsage":
                raise CanonicalMappingError(
                    f"root_source_id {root_source_id!r} references a "
                    f"{root.metatype} element; the system root must be a partUsage"
                )
            if root.name is None:
                raise CanonicalMappingError(
                    f"root_source_id {root_source_id!r} references an unnamed "
                    "partUsage; the system root must have a name"
                )
            return root
        candidates = [
            element
            for element in elements.values()
            if element.metatype == "partUsage"
            and element.name is not None
            and not _part_usage_ancestors(elements, element)
        ]
        if not candidates:
            raise CanonicalMappingError(
                "no named PartUsage candidate for the system root (no named "
                "partUsage without a partUsage ancestor)"
            )
        if len(candidates) > 1:
            ids = ", ".join(repr(candidate.source_id) for candidate in candidates)
            raise CanonicalMappingError(
                f"multiple PartUsage candidates for the system root: {ids}; "
                "select one explicitly via root_source_id"
            )
        return candidates[0]


def _owner_chain(
    elements: dict[str, SysMLElementFact], element: SysMLElementFact
) -> list[SysMLElementFact]:
    """Ancestors of ``element`` nearest-first; stops at unknown or cyclic owners."""
    chain: list[SysMLElementFact] = []
    seen: set[str] = set()
    current = element
    while current.owner_id is not None and current.owner_id not in seen:
        seen.add(current.owner_id)
        owner = elements.get(current.owner_id)
        if owner is None:
            break
        chain.append(owner)
        current = owner
    return chain


def _part_usage_ancestors(
    elements: dict[str, SysMLElementFact], element: SysMLElementFact
) -> list[SysMLElementFact]:
    return [a for a in _owner_chain(elements, element) if a.metatype == "partUsage"]


def _in_subtree(
    elements: dict[str, SysMLElementFact],
    root: SysMLElementFact,
    element: SysMLElementFact,
) -> bool:
    return any(a.source_id == root.source_id for a in _owner_chain(elements, element))


def _typing_to_action_def(element: SysMLElementFact) -> bool:
    facts = element.type_facts
    return (
        facts is not None
        and facts.resolved_id is not None
        and facts.resolved_kind == "actionDef"
    )


def _source_ref(
    snapshot: SysMLFactSnapshot, element: SysMLElementFact
) -> SourceReference:
    source = snapshot.source
    return SourceReference(
        source_type=source.source_type,
        source_uri=source.source_path or "",
        source_element_id=element.source_id,
        source_version=source.source_version,
        adapter=source.adapter,
    )
