"""OpenSysML file-mode adapter (MVP-1C).

Loads one standalone .sysml file through the OpenSysML public API and
materializes a parser-native SysMLFactSnapshot. Single-file subset only
(C1): user-file imports are not supported and surface as error diagnostics
from the parser, preserved verbatim in the snapshot.

Load policy (documented, F1):

- the input path is normalized once with ``expanduser().resolve(strict=True)``
  and that resolved absolute path string is used both for the OpenSysML load
  and for ``SysMLSource.source_path``;
- ``SysMLSource.model_hash`` records OpenSysML's ``Model.hash`` verbatim. It
  is a fingerprint of the load context (name + per-file content digest), not
  a stable cross-path or cross-version identity; no hash is recomputed here.

The connection is an explicit ``with opensysml.connect(version=...)`` block;
load, diagnostics, traversal, type facts, specializations and snapshot
construction all complete before the connection closes.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import cast

import opensysml

from fmea_agent.adapters.sysml.contracts import (
    SysMLDiagnostic,
    SysMLElementFact,
    SysMLFactSnapshot,
    SysMLRelationshipFact,
    SysMLSource,
    SysMLTypeFacts,
)
from fmea_agent.adapters.sysml.exceptions import (
    SysMLLoadError,
    SysMLParseError,
    UnsupportedSysMLElement,
)

_ADAPTER_NAME = "open_sysml_file"
_PARSER_NAME = "opensysml"
_RUNTIME_VERSION = "v0.4.3"
_ROOT_NAMESPACE_KIND = "RootNamespace"


class OpenSysMLFileAdapter:
    """Adapts a single .sysml file loaded through OpenSysML into a SysMLFactSnapshot."""

    def load(self, file_path: str | Path) -> SysMLFactSnapshot:
        """Load ``file_path`` through OpenSysML and materialize a snapshot.

        Returns a snapshot with ``load_status == "ok"`` for a valid model.
        A model OpenSysML parsed with error diagnostics is still extracted
        and returned with ``load_status == "partial"``.

        Raises:
            SysMLLoadError: the file is missing/unreadable, or the OpenSysML
                runtime cannot be started or reached.
            SysMLParseError: OpenSysML reported errors and returned no model.
            UnsupportedSysMLElement: a non-root symbol cannot be represented
                in the snapshot contracts.
        """
        resolved = _normalize_path(file_path)
        try:
            with opensysml.connect(  # type: ignore[no-untyped-call]
                version=_RUNTIME_VERSION
            ) as connection:
                model = _load_model(connection, resolved)
                return self._build_snapshot(model, resolved, connection)
        except opensysml.OpenSysMLError as exc:
            raise SysMLLoadError(
                f"OpenSysML failed to load {resolved}: {exc}"
            ) from exc

    def _build_snapshot(
        self,
        model: opensysml.Model,
        resolved: Path,
        connection: opensysml.Connection,
    ) -> SysMLFactSnapshot:
        diagnostics = [self._to_diagnostic(d) for d in model.diagnostics]
        elements: list[SysMLElementFact] = []
        relationships: list[SysMLRelationshipFact] = []
        for owner, symbol in _walk(model.root):
            element = self._to_element(symbol, owner)
            elements.append(element)
            relationships.extend(self._to_relationships(symbol))
        server_info = connection.server_info()  # type: ignore[no-untyped-call]
        return SysMLFactSnapshot(
            source=SysMLSource(
                source_type="sysml_file",
                source_path=str(resolved),
                model_hash=model.hash or None,
                parser=_PARSER_NAME,
                parser_version=opensysml.__version__,
                runtime_version=server_info.version or None,
                adapter=_ADAPTER_NAME,
            ),
            elements=elements,
            relationships=relationships,
            diagnostics=diagnostics,
            load_status=(
                "ok"
                if not any(d.severity == "error" for d in diagnostics)
                else "partial"
            ),
        )

    def _to_element(
        self, symbol: opensysml.Symbol, owner: opensysml.Symbol | None
    ) -> SysMLElementFact:
        if not symbol.id or not symbol.kind:
            raise UnsupportedSysMLElement(
                f"cannot represent symbol {symbol!r} in the snapshot contracts: "
                "source_id and metatype must be non-empty"
            )
        return SysMLElementFact(
            source_id=symbol.id,
            metatype=symbol.kind,
            name=symbol.name or None,
            owner_id=owner.id if owner is not None else None,
            type_facts=self._to_type_facts(symbol),
        )

    def _to_type_facts(self, symbol: opensysml.Symbol) -> SysMLTypeFacts | None:
        facts = symbol.type_facts
        if facts is None:
            return None
        declared = facts.declared or None
        resolved_id = facts.resolved_id or None
        resolved_kind = facts.resolved_kind or None
        if declared is None and resolved_id is None and resolved_kind is None:
            return None
        return SysMLTypeFacts(
            declared=declared, resolved_id=resolved_id, resolved_kind=resolved_kind
        )

    def _to_relationships(
        self, symbol: opensysml.Symbol
    ) -> list[SysMLRelationshipFact]:
        relationships: list[SysMLRelationshipFact] = []
        for spec in symbol.specializations:
            if not spec.target_id:
                continue
            relationships.append(
                SysMLRelationshipFact(
                    type=spec.kind, source_id=symbol.id, target_id=spec.target_id
                )
            )
        return relationships

    def _to_diagnostic(self, diagnostic: opensysml.Diagnostic) -> SysMLDiagnostic:
        return SysMLDiagnostic(
            severity=diagnostic.severity,
            message=diagnostic.message,
            file=diagnostic.file or None,
            start_line=diagnostic.start_line or None,
            start_column=diagnostic.start_column or None,
            end_line=diagnostic.end_line or None,
            end_column=diagnostic.end_column or None,
            span=None,
        )


def _normalize_path(file_path: str | Path) -> Path:
    try:
        return Path(file_path).expanduser().resolve(strict=True)
    except FileNotFoundError as exc:
        raise SysMLLoadError(f"sysml file not found: {file_path}") from exc
    except OSError as exc:
        raise SysMLLoadError(f"cannot access sysml file {file_path}: {exc}") from exc


def _load_model(connection: opensysml.Connection, path: Path) -> opensysml.Model:
    try:
        return cast(
            opensysml.Model,
            connection.load(str(path), strict=True),  # type: ignore[no-untyped-call]
        )
    except opensysml.ModelError as exc:
        if exc.model is None:
            raise SysMLParseError(
                f"OpenSysML reported errors for {path} and returned no model: {exc}"
            ) from exc
        return cast(opensysml.Model, exc.model)


def _walk(
    root: opensysml.Symbol,
) -> Iterator[tuple[opensysml.Symbol | None, opensysml.Symbol]]:
    """Pre-order traversal of the symbol tree, skipping the RootNamespace."""
    stack: list[tuple[opensysml.Symbol | None, opensysml.Symbol]] = [
        (None, child) for child in reversed(root.children())
    ]
    while stack:
        owner, symbol = stack.pop()
        children = symbol.children()
        stack.extend((symbol, child) for child in reversed(children))
        if symbol.kind == _ROOT_NAMESPACE_KIND:
            continue
        yield owner, symbol
