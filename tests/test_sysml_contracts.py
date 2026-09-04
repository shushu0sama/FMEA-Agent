"""MVP-1B — parser-neutral SysML fact snapshot contract tests.

The contracts under test are project-owned data envelopes. These tests assert
parser neutrality (no opensysml/grpc/protobuf imports), strict schema
(extra fields rejected, required non-empty strings), open-world relationship
semantics, absence-representable typing facts (C4), and JSON round-trip
semantic equality. No sysml-grpc process is started here; version pins are
not asserted here (that belongs to MVP-1C contract tests).
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from fmea_agent.adapters.sysml.contracts import (
    SysMLDiagnostic,
    SysMLElementFact,
    SysMLFactSnapshot,
    SysMLRelationshipFact,
    SysMLSource,
    SysMLTypeFacts,
)

CONTRACTS_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "fmea_agent"
    / "adapters"
    / "sysml"
    / "contracts.py"
)
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sysml" / "snapshot_minimal.json"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def make_source(**overrides: object) -> SysMLSource:
    data: dict[str, object] = {
        "source_type": "sysml_file",
        "source_path": "examples/minimal.sysml",
        "parser": "opensysml",
        "adapter": "open_sysml_file",
    }
    data.update(overrides)
    return SysMLSource.model_validate(data)


def make_element(source_id: str, metatype: str, **overrides: object) -> SysMLElementFact:
    data: dict[str, object] = {"source_id": source_id, "metatype": metatype}
    data.update(overrides)
    return SysMLElementFact.model_validate(data)


def make_diagnostic(**overrides: object) -> SysMLDiagnostic:
    data: dict[str, object] = {"severity": "error", "message": "unresolved reference: X"}
    data.update(overrides)
    return SysMLDiagnostic.model_validate(data)


def make_snapshot(**overrides: object) -> SysMLFactSnapshot:
    data: dict[str, object] = {
        "source": make_source(),
        "elements": [],
        "relationships": [],
        "diagnostics": [],
        "load_status": "ok",
    }
    data.update(overrides)
    return SysMLFactSnapshot.model_validate(data)


# --- parser-runtime independence ---


def test_contracts_module_imports_only_stdlib_and_pydantic() -> None:
    modules = _imported_modules(CONTRACTS_PATH)
    assert modules, "expected to find imports in the contracts module"
    for module in modules:
        assert module in sys.stdlib_module_names or module == "pydantic", module


def test_contracts_module_has_no_parser_runtime_imports() -> None:
    forbidden = ("opensysml", "grpc", "google.protobuf")
    for module in _imported_modules(CONTRACTS_PATH):
        for prefix in forbidden:
            assert not module.startswith(prefix), module


# --- schema whitelist: no FMEA / canonical fields ---


def test_snapshot_schema_fields() -> None:
    assert set(SysMLFactSnapshot.model_fields) == {
        "source",
        "elements",
        "relationships",
        "diagnostics",
        "load_status",
    }


def test_source_schema_fields() -> None:
    assert set(SysMLSource.model_fields) == {
        "source_type",
        "source_path",
        "source_version",
        "model_hash",
        "parser",
        "parser_version",
        "runtime_version",
        "adapter",
    }


def test_element_schema_fields() -> None:
    assert set(SysMLElementFact.model_fields) == {
        "source_id",
        "metatype",
        "name",
        "owner_id",
        "type_facts",
        "properties",
    }


def test_relationship_schema_fields() -> None:
    assert set(SysMLRelationshipFact.model_fields) == {
        "type",
        "source_id",
        "target_id",
        "properties",
    }


def test_diagnostic_schema_fields() -> None:
    assert set(SysMLDiagnostic.model_fields) == {
        "severity",
        "message",
        "file",
        "start_line",
        "start_column",
        "end_line",
        "end_column",
        "span",
    }


# --- required fields and defaults ---


def test_source_optional_fields_default_none() -> None:
    source = make_source()
    assert source.source_version is None
    assert source.model_hash is None
    assert source.parser_version is None
    assert source.runtime_version is None


def test_source_version_and_model_hash_are_independent() -> None:
    source = make_source(source_version="repo-rev-1", model_hash="abc123")
    assert source.source_version == "repo-rev-1"
    assert source.model_hash == "abc123"


def test_element_optional_fields_default() -> None:
    element = make_element("PerformProbe::Pump", "partDef")
    assert element.name is None
    assert element.owner_id is None
    assert element.type_facts is None
    assert element.properties == {}


def test_relationship_properties_default() -> None:
    relationship = SysMLRelationshipFact(type="typing", source_id="a", target_id="b")
    assert relationship.properties == {}


def test_diagnostic_locator_defaults_none() -> None:
    diagnostic = make_diagnostic()
    assert diagnostic.file is None
    assert diagnostic.start_line is None
    assert diagnostic.start_column is None
    assert diagnostic.end_line is None
    assert diagnostic.end_column is None
    assert diagnostic.span is None


def test_source_requires_source_type_parser_adapter() -> None:
    with pytest.raises(ValidationError):
        SysMLSource(source_type="sysml_file", source_path="x.sysml", adapter="a")
    with pytest.raises(ValidationError):
        SysMLSource(source_type="sysml_file", source_path="x.sysml", parser="p")
    with pytest.raises(ValidationError):
        SysMLSource(source_path="x.sysml", parser="p", adapter="a")


def test_element_requires_source_id_and_metatype() -> None:
    with pytest.raises(ValidationError):
        SysMLElementFact(metatype="partDef")
    with pytest.raises(ValidationError):
        SysMLElementFact(source_id="PerformProbe::Pump")


def test_relationship_requires_type_and_endpoints() -> None:
    with pytest.raises(ValidationError):
        SysMLRelationshipFact(source_id="a", target_id="b")
    with pytest.raises(ValidationError):
        SysMLRelationshipFact(type="typing", target_id="b")
    with pytest.raises(ValidationError):
        SysMLRelationshipFact(type="typing", source_id="a")


def test_diagnostic_requires_severity_and_message() -> None:
    with pytest.raises(ValidationError):
        SysMLDiagnostic(message="m")
    with pytest.raises(ValidationError):
        SysMLDiagnostic(severity="error")


# --- non-empty required strings (clarification D) ---


@pytest.mark.parametrize(
    "build",
    [
        lambda: SysMLSource(source_type="", source_path="x.sysml", parser="p", adapter="a"),
        lambda: SysMLSource(
            source_type="sysml_file", source_path="x.sysml", parser="", adapter="a"
        ),
        lambda: SysMLSource(
            source_type="sysml_file", source_path="x.sysml", parser="p", adapter=""
        ),
        lambda: SysMLElementFact(source_id="", metatype="partDef"),
        lambda: SysMLElementFact(source_id="x", metatype=""),
        lambda: SysMLRelationshipFact(type="", source_id="a", target_id="b"),
        lambda: SysMLRelationshipFact(type="typing", source_id="", target_id="b"),
        lambda: SysMLRelationshipFact(type="typing", source_id="a", target_id=""),
        lambda: SysMLDiagnostic(severity="", message="m"),
        lambda: SysMLDiagnostic(severity="error", message=""),
    ],
)
def test_required_strings_reject_empty(build: Callable[[], object]) -> None:
    with pytest.raises(ValidationError):
        build()


# --- strict contract boundary (clarification C) ---


@pytest.mark.parametrize(
    "build",
    [
        lambda: SysMLSource(
            source_type="sysml_file", source_path="x.sysml", parser="p", adapter="a", unexpected="x"
        ),
        lambda: SysMLTypeFacts(unexpected="x"),
        lambda: SysMLElementFact(source_id="x", metatype="y", unexpected="x"),
        lambda: SysMLRelationshipFact(type="t", source_id="a", target_id="b", unexpected="x"),
        lambda: SysMLDiagnostic(severity="error", message="m", unexpected="x"),
        lambda: SysMLFactSnapshot(
            source=make_source(), elements=[], relationships=[], diagnostics=[], load_status="ok",
            unexpected="x",
        ),
    ],
)
def test_extra_fields_are_rejected(build: Callable[[], object]) -> None:
    with pytest.raises(ValidationError):
        build()


# --- parser-neutral identity (clarification A) ---


def test_source_id_is_plain_source_native_string() -> None:
    # The contract must not validate or parse FQN format; any non-empty
    # source-native identity is valid.
    numeric = SysMLElementFact(source_id="42", metatype="partUsage")
    urn = SysMLElementFact(source_id="urn:example:elem-1", metatype="partDef")
    assert numeric.source_id == "42"
    assert urn.source_id == "urn:example:elem-1"


# --- open-world relationship semantics (V2) ---


def test_relationship_target_may_reference_external_identity() -> None:
    element = make_element("PerformProbe::hydraulicPump", "partUsage")
    snapshot = make_snapshot(
        elements=[element],
        relationships=[
            SysMLRelationshipFact(
                type="typing",
                source_id="PerformProbe::hydraulicPump",
                target_id="External::Pump",
            )
        ],
    )
    assert snapshot.relationships[0].target_id == "External::Pump"


def test_relationship_source_must_reference_element_in_snapshot() -> None:
    with pytest.raises(ValidationError):
        make_snapshot(
            elements=[make_element("PerformProbe::Pump", "partDef")],
            relationships=[
                SysMLRelationshipFact(
                    type="typing",
                    source_id="PerformProbe::hydraulicPump",
                    target_id="PerformProbe::Pump",
                )
            ],
        )


# --- uniqueness (V1) ---


def test_duplicate_source_ids_rejected() -> None:
    with pytest.raises(ValidationError):
        make_snapshot(
            elements=[make_element("a", "package"), make_element("a", "partDef")],
        )


# --- owner_id may be unresolved (V3) ---


def test_owner_id_may_be_unresolved_in_partial_snapshot() -> None:
    element = make_element(
        "PerformProbe::hydraulicPump",
        "partUsage",
        owner_id="PerformProbe::notIncludedOwner",
    )
    snapshot = make_snapshot(
        elements=[element],
        load_status="partial",
        diagnostics=[
            make_diagnostic(
                severity="warning",
                message="incomplete extraction: owner element not included",
            )
        ],
    )
    assert snapshot.load_status == "partial"
    assert snapshot.elements[0].owner_id == "PerformProbe::notIncludedOwner"


# --- load_status semantics (V5) ---


def test_ok_with_error_diagnostic_rejected() -> None:
    with pytest.raises(ValidationError):
        make_snapshot(diagnostics=[make_diagnostic()])


def test_partial_without_error_diagnostic_is_valid() -> None:
    snapshot = make_snapshot(
        load_status="partial",
        diagnostics=[make_diagnostic(severity="warning", message="unsupported construct")],
    )
    assert snapshot.load_status == "partial"


def test_load_status_rejects_unknown_values() -> None:
    with pytest.raises(ValidationError):
        make_snapshot(load_status="degraded")


# --- source_path requirement (V6) ---


def test_file_mode_requires_source_path() -> None:
    with pytest.raises(ValidationError):
        SysMLSource(source_type="sysml_file", parser="p", adapter="a")


def test_file_mode_accepts_source_path() -> None:
    source = make_source()
    assert source.source_path == "examples/minimal.sysml"


def test_non_file_source_may_omit_source_path() -> None:
    source = SysMLSource(source_type="sysml_repository", parser="p", adapter="a")
    assert source.source_path is None


# --- unknown parser facts must not break the contract ---


def test_unknown_metatype_is_accepted() -> None:
    element = make_element("PerformProbe::odd", "futureKind")
    snapshot = make_snapshot(elements=[element])
    assert snapshot.model_dump_json()


def test_unknown_diagnostic_severity_is_accepted() -> None:
    diagnostic = make_diagnostic(severity="notice")
    snapshot = make_snapshot(diagnostics=[diagnostic])
    assert snapshot.diagnostics[0].severity == "notice"


def test_unknown_relationship_type_is_accepted() -> None:
    element = make_element("a", "package")
    snapshot = make_snapshot(
        elements=[element],
        relationships=[
            SysMLRelationshipFact(type="futureKind", source_id="a", target_id="external-target")
        ],
    )
    assert snapshot.relationships[0].type == "futureKind"


# --- performed-action typing absence (C4) ---


def test_performed_action_typing_absence_is_representable() -> None:
    missing = make_element("PerformProbe::motor::spin", "actionUsage", type_facts=None)
    empty = make_element("PerformProbe::motor::spin", "actionUsage", type_facts=SysMLTypeFacts())
    assert missing.type_facts is None
    assert empty.type_facts == SysMLTypeFacts(declared=None, resolved_id=None, resolved_kind=None)


def test_all_none_type_facts_serialize_roundtrip() -> None:
    element = make_element("PerformProbe::motor::spin", "actionUsage", type_facts=SysMLTypeFacts())
    restored = SysMLElementFact.model_validate_json(element.model_dump_json())
    assert restored == element


# --- unresolved import representable (C1) ---


def test_unresolved_import_diagnostic_representable() -> None:
    diagnostic = SysMLDiagnostic(
        severity="error",
        message="unresolved reference: Action Decomposition",
        file="Action Performance Example.sysml",
        start_line=4,
        start_column=12,
        end_line=4,
        end_column=32,
    )
    snapshot = make_snapshot(
        load_status="partial",
        diagnostics=[diagnostic],
        elements=[make_element("PerformProbe", "package")],
    )
    assert snapshot.load_status == "partial"
    assert snapshot.diagnostics[0].message.startswith("unresolved reference")


# --- strict JSON-safety (V8) ---


class _OpaqueRuntimeObject:
    pass


def test_properties_reject_runtime_objects() -> None:
    with pytest.raises(ValidationError):
        SysMLElementFact(
            source_id="x",
            metatype="partDef",
            properties={"payload": _OpaqueRuntimeObject()},
        )


def test_span_rejects_runtime_objects() -> None:
    with pytest.raises(ValidationError):
        SysMLDiagnostic(severity="error", message="m", span=_OpaqueRuntimeObject())


def test_properties_accept_nested_json_values() -> None:
    element = make_element(
        "x",
        "partDef",
        properties={"meta": {"visibility": "public", "tags": ["a", 1, True]}},
    )
    assert element.properties["meta"] == {"visibility": "public", "tags": ["a", 1, True]}


# --- JSON round-trip semantic equality ---


def _full_snapshot() -> SysMLFactSnapshot:
    return make_snapshot(
        source=make_source(
            source_version="repo-rev-1",
            model_hash="hash-1",
            parser_version="0.4.0",
            runtime_version="v0.4.3",
        ),
        elements=[
            make_element("PerformProbe", "package", name="PerformProbe"),
            make_element("PerformProbe::Pump", "partDef", name="Pump", owner_id="PerformProbe"),
            make_element(
                "PerformProbe::hydraulicPump",
                "partUsage",
                name="hydraulicPump",
                owner_id="PerformProbe",
                type_facts=SysMLTypeFacts(
                    declared="Pump",
                    resolved_id="PerformProbe::Pump",
                    resolved_kind="partDef",
                ),
            ),
            make_element(
                "PerformProbe::motor::spin",
                "actionUsage",
                name="spin",
                owner_id="PerformProbe::hydraulicPump::motor",
                type_facts=None,
            ),
        ],
        relationships=[
            SysMLRelationshipFact(
                type="typing",
                source_id="PerformProbe::hydraulicPump",
                target_id="PerformProbe::Pump",
            )
        ],
    )


def test_snapshot_json_roundtrip_semantic_equality() -> None:
    snapshot = _full_snapshot()
    restored = SysMLFactSnapshot.model_validate_json(snapshot.model_dump_json())
    assert restored == snapshot


def test_diagnostic_json_roundtrip_semantic_equality() -> None:
    diagnostic = SysMLDiagnostic(
        severity="error",
        message="m",
        file="f.sysml",
        start_line=1,
        start_column=2,
        end_line=1,
        end_column=10,
        span={"start": 0, "end": 9},
    )
    restored = SysMLDiagnostic.model_validate_json(diagnostic.model_dump_json())
    assert restored == diagnostic


# --- minimal fixture ---


def test_minimal_fixture_is_valid_and_roundtrips() -> None:
    snapshot = SysMLFactSnapshot.model_validate_json(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert snapshot.load_status == "ok"
    assert not snapshot.diagnostics
    assert len(snapshot.elements) >= 4
    assert any(e.metatype == "package" for e in snapshot.elements)
    assert any(e.metatype == "partDef" for e in snapshot.elements)
    assert any(e.metatype == "partUsage" for e in snapshot.elements)
    assert any(e.metatype == "actionUsage" for e in snapshot.elements)
    assert any(r.type == "typing" for r in snapshot.relationships)
    restored = SysMLFactSnapshot.model_validate_json(snapshot.model_dump_json())
    assert restored == snapshot
