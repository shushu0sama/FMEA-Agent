"""MVP-1C — OpenSysMLFileAdapter contract tests (real sysml-grpc runtime).

These tests exercise the real OpenSysML public API against a real
sysml-grpc v0.4.3 service. They are the MVP-1C contract tests for:

- the dependency pin (opensysml==0.4.0 / sysml-grpc v0.4.3),
- the single-file load policy and exception boundary,
- traversal-based extraction with real owner context,
- typing facts without inference (C4),
- partial-load and unresolved-import diagnostics (C1),
- the Model.hash verbatim-recording policy (F1),
- connection cleanup on success/partial/error paths.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import opensysml
import pytest

from fmea_agent.adapters.sysml import (
    OpenSysMLFileAdapter,
    SysMLLoadError,
    SysMLParseError,
    UnsupportedSysMLElement,
)
from fmea_agent.adapters.sysml.contracts import (
    SysMLFactSnapshot,
    SysMLTypeFacts,
)
from fmea_agent.adapters.sysml.open_sysml_file import _load_model, _walk

MODELS_DIR = Path(__file__).resolve().parent / "fixtures" / "sysml" / "models"
VALID_MODEL = MODELS_DIR / "perform_probe.sysml"
INVALID_MODEL = MODELS_DIR / "invalid_syntax.sysml"
UNRESOLVED_IMPORT_MODEL = MODELS_DIR / "unresolved_import.sysml"
SIBLING_ROOTS_MODEL = MODELS_DIR / "sibling_roots_probe.sysml"


def _load_valid() -> SysMLFactSnapshot:
    return OpenSysMLFileAdapter().load(VALID_MODEL)


def _elements_by_id(snapshot: SysMLFactSnapshot) -> dict[str, object]:
    return {element.source_id: element for element in snapshot.elements}


# --- 1. dependency pin ---


def test_opensysml_python_client_version_is_pinned() -> None:
    assert opensysml.__version__ == "0.4.0"


def test_pyproject_pins_opensysml_exactly() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    assert '"opensysml==0.4.0"' in text


# --- 2. missing file -> SysMLLoadError ---


def test_missing_file_raises_sysml_load_error() -> None:
    adapter = OpenSysMLFileAdapter()
    with pytest.raises(SysMLLoadError):
        adapter.load(MODELS_DIR / "does_not_exist.sysml")


# --- 3. valid .sysml -> ok snapshot ---


def test_valid_model_loads_ok_snapshot() -> None:
    snapshot = _load_valid()
    assert snapshot.load_status == "ok"
    assert snapshot.diagnostics == []


# --- source provenance ---


def test_snapshot_source_provenance() -> None:
    snapshot = _load_valid()
    source = snapshot.source
    assert source.source_type == "sysml_file"
    assert source.source_path == str(VALID_MODEL.resolve())
    assert source.parser == "opensysml"
    assert source.parser_version == "0.4.0"
    assert source.runtime_version == "v0.4.3"
    assert source.adapter == "open_sysml_file"
    assert source.source_version is None
    assert source.model_hash


# --- 8. invalid model -> partial + diagnostics ---


def test_invalid_model_returns_partial_snapshot_with_diagnostics() -> None:
    snapshot = OpenSysMLFileAdapter().load(INVALID_MODEL)
    assert snapshot.load_status == "partial"
    messages = [d.message for d in snapshot.diagnostics]
    assert "expected '{' or ';' after declaration" in messages
    assert "expected '}'" in messages
    assert all(d.severity == "error" for d in snapshot.diagnostics)
    assert all(
        d.file is not None and d.file.endswith("invalid_syntax.sysml")
        for d in snapshot.diagnostics
    )
    assert all(d.start_line is not None for d in snapshot.diagnostics)


# --- 9. unresolved import -> partial + explicit diagnostic ---


def test_unresolved_import_returns_partial_with_explicit_diagnostics() -> None:
    snapshot = OpenSysMLFileAdapter().load(UNRESOLVED_IMPORT_MODEL)
    assert snapshot.load_status == "partial"
    assert len(snapshot.diagnostics) == 4
    assert all(d.severity == "error" for d in snapshot.diagnostics)
    messages = [d.message for d in snapshot.diagnostics]
    assert "unresolved reference: Action Decomposition" in messages
    assert "unresolved reference: takePicture" in messages
    assert "unresolved member: focus" in messages
    assert "unresolved member: shoot" in messages


# --- 4. traversal + owner_id from real parent context ---


def test_elements_cover_tree_with_real_owner_ids() -> None:
    snapshot = _load_valid()
    by_id = _elements_by_id(snapshot)
    expected = {
        "PerformProbe": ("package", None),
        "PerformProbe::Pump": ("partDef", "PerformProbe"),
        "PerformProbe::Motor": ("partDef", "PerformProbe"),
        "PerformProbe::Spin": ("actionDef", "PerformProbe"),
        "PerformProbe::Spin::speed": ("attributeUsage", "PerformProbe::Spin"),
        "PerformProbe::hydraulicPump": ("partUsage", "PerformProbe"),
        "PerformProbe::hydraulicPump::motor": (
            "partUsage",
            "PerformProbe::hydraulicPump",
        ),
        "PerformProbe::hydraulicPump::motor::spin": (
            "actionUsage",
            "PerformProbe::hydraulicPump::motor",
        ),
        "PerformProbe::spin": ("actionUsage", "PerformProbe"),
    }
    assert set(by_id) == set(expected)
    for source_id, (metatype, owner_id) in expected.items():
        element = by_id[source_id]
        assert element.metatype == metatype
        assert element.owner_id == owner_id


def test_root_namespace_is_not_in_elements() -> None:
    snapshot = _load_valid()
    assert all(e.metatype != "RootNamespace" for e in snapshot.elements)
    assert all(e.source_id for e in snapshot.elements)


def test_element_names_are_short_names() -> None:
    by_id = _elements_by_id(_load_valid())
    assert by_id["PerformProbe"].name == "PerformProbe"
    assert by_id["PerformProbe::hydraulicPump"].name == "hydraulicPump"
    assert by_id["PerformProbe::hydraulicPump::motor::spin"].name == "spin"


class _FakeSymbol:
    def __init__(
        self,
        kind: str,
        name: str,
        children: list[_FakeSymbol] | None = None,
    ) -> None:
        self.kind = kind
        self.name = name
        self._children = children or []

    def children(self) -> list[_FakeSymbol]:
        return self._children


def test_walk_preserves_root_children_traversal_order() -> None:
    a1 = _FakeSymbol("partUsage", "a1")
    a = _FakeSymbol("package", "a", [a1])
    b1 = _FakeSymbol("partUsage", "b1")
    b = _FakeSymbol("package", "b", [b1])
    root = _FakeSymbol("RootNamespace", "", [a, b])
    visited = [symbol.name for _, symbol in _walk(root)]
    assert visited == ["a", "a1", "b", "b1"]


def test_snapshot_elements_follow_source_order() -> None:
    snapshot = OpenSysMLFileAdapter().load(SIBLING_ROOTS_MODEL)
    assert [e.source_id for e in snapshot.elements] == [
        "AlphaPackage",
        "AlphaPackage::Pump",
        "AlphaPackage::alphaPump",
        "AlphaPackage::alphaPump::alphaInner",
        "AlphaPackage::alphaMotor",
        "BetaPackage",
        "BetaPackage::Pump",
        "BetaPackage::betaPump",
    ]


# --- 5. type_facts ---


def test_typed_usage_type_facts() -> None:
    by_id = _elements_by_id(_load_valid())
    assert by_id["PerformProbe::hydraulicPump"].type_facts == SysMLTypeFacts(
        declared="Pump",
        resolved_id="PerformProbe::Pump",
        resolved_kind="partDef",
    )
    assert by_id["PerformProbe::hydraulicPump::motor"].type_facts == SysMLTypeFacts(
        declared="Motor",
        resolved_id="PerformProbe::Motor",
        resolved_kind="partDef",
    )
    assert by_id["PerformProbe::spin"].type_facts == SysMLTypeFacts(
        declared="Spin",
        resolved_id="PerformProbe::Spin",
        resolved_kind="actionDef",
    )


def test_definitions_have_no_type_facts() -> None:
    by_id = _elements_by_id(_load_valid())
    for source_id in (
        "PerformProbe::Pump",
        "PerformProbe::Motor",
        "PerformProbe::Spin",
    ):
        assert by_id[source_id].type_facts is None


# --- 6. specialization / typing relationships ---


def test_typing_relationships_come_from_real_specializations() -> None:
    snapshot = _load_valid()
    expected = {
        ("PerformProbe::hydraulicPump", "PerformProbe::Pump"),
        ("PerformProbe::hydraulicPump::motor", "PerformProbe::Motor"),
        ("PerformProbe::spin", "PerformProbe::Spin"),
        ("PerformProbe::Spin::speed", "ScalarValues::Real"),
    }
    typing = {
        (r.source_id, r.target_id) for r in snapshot.relationships if r.type == "typing"
    }
    assert typing == expected
    assert all(r.type == "typing" for r in snapshot.relationships)


def test_relationship_target_may_be_external_library_element() -> None:
    snapshot = _load_valid()
    by_id = _elements_by_id(snapshot)
    assert "ScalarValues::Real" not in by_id
    external = [
        r
        for r in snapshot.relationships
        if r.target_id == "ScalarValues::Real"
    ]
    assert [r.source_id for r in external] == ["PerformProbe::Spin::speed"]


# --- 7. performed ActionUsage: no fabricated typing (C4) ---


def test_performed_action_usage_has_no_fabricated_typing() -> None:
    snapshot = _load_valid()
    by_id = _elements_by_id(snapshot)
    performed = by_id["PerformProbe::hydraulicPump::motor::spin"]
    assert performed.metatype == "actionUsage"
    assert performed.type_facts is None
    assert not [
        r for r in snapshot.relationships if r.source_id == performed.source_id
    ]


# --- partial loads still extract observable elements ---


def test_invalid_model_partial_elements_are_extracted() -> None:
    snapshot = OpenSysMLFileAdapter().load(INVALID_MODEL)
    by_id = _elements_by_id(snapshot)
    assert by_id["BrokenProbe"].metatype == "package"
    assert by_id["BrokenProbe::Pump"].metatype == "partDef"
    assert by_id["BrokenProbe::broken"].metatype == "partUsage"
    assert by_id["BrokenProbe::broken"].owner_id == "BrokenProbe"


def test_unresolved_import_partial_elements_are_extracted() -> None:
    snapshot = OpenSysMLFileAdapter().load(UNRESOLVED_IMPORT_MODEL)
    by_id = _elements_by_id(snapshot)
    assert "Action Performance Example" in by_id
    camera = by_id["Action Performance Example::camera"]
    assert camera.metatype == "partUsage"
    assert camera.type_facts == SysMLTypeFacts(
        declared="Camera",
        resolved_id="Action Performance Example::Camera",
        resolved_kind="partDef",
    )
    performed = by_id["Action Performance Example::camera::takePhoto"]
    assert performed.metatype == "actionUsage"
    assert performed.type_facts is None


# --- snapshot is strictly JSON-safe ---


def test_snapshot_json_roundtrip_semantic_equality() -> None:
    snapshot = _load_valid()
    restored = SysMLFactSnapshot.model_validate_json(snapshot.model_dump_json())
    assert restored == snapshot


def test_partial_snapshot_json_roundtrip_semantic_equality() -> None:
    snapshot = OpenSysMLFileAdapter().load(INVALID_MODEL)
    restored = SysMLFactSnapshot.model_validate_json(snapshot.model_dump_json())
    assert restored == snapshot


# --- 10. path / hash policy (F1) ---


def test_relative_path_is_resolved_and_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(MODELS_DIR)
    snapshot = OpenSysMLFileAdapter().load("perform_probe.sysml")
    assert snapshot.source.source_path == str(VALID_MODEL.resolve())


def test_path_object_input_is_accepted() -> None:
    snapshot = OpenSysMLFileAdapter().load(VALID_MODEL)
    assert snapshot.load_status == "ok"


def test_model_hash_recorded_verbatim_and_repeatable_same_path() -> None:
    first = _load_valid()
    second = _load_valid()
    assert first.source.model_hash
    assert first.source.model_hash == second.source.model_hash


def test_model_hash_depends_on_load_path_context(tmp_path: Path) -> None:
    copy = tmp_path / "perform_probe_copy.sysml"
    copy.write_bytes(VALID_MODEL.read_bytes())
    original = _load_valid()
    copied = OpenSysMLFileAdapter().load(copy)
    assert original.source.model_hash != copied.source.model_hash


def test_missing_file_error_chains_the_cause() -> None:
    adapter = OpenSysMLFileAdapter()
    with pytest.raises(SysMLLoadError) as excinfo:
        adapter.load(MODELS_DIR / "does_not_exist.sysml")
    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


# --- exception boundary ---


def test_unrepresentable_symbol_raises_unsupported_element() -> None:
    adapter = OpenSysMLFileAdapter()

    class _FakeSymbol:
        id = ""
        kind = "partDef"
        name = "x"

    with pytest.raises(UnsupportedSysMLElement):
        adapter._to_element(_FakeSymbol(), None)


def test_model_error_without_model_raises_sysml_parse_error() -> None:
    class _FakeConnection:
        def load(self, file_path: str, strict: bool = False) -> None:
            raise opensysml.ModelError("boom", diagnostics=[], model=None)

    with pytest.raises(SysMLParseError):
        _load_model(_FakeConnection(), Path("x.sysml"))


# --- 11. connection / process cleanup ---
#
# The adapter closes its connection on every path (ok / partial / error).
# All previous tests in this module exercise those paths; if any of them
# leaked the private sysml-grpc child, it is still alive here.
#
# The check compares the current PID set against the set observed at module
# import time (before any adapter activity), so pre-existing legitimate
# sysml-grpc processes are not flagged — only newly spawned orphans are.


def _sysml_grpc_pids() -> set[str]:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "@(Get-Process sysml-grpc* -ErrorAction SilentlyContinue).Id -join ','",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return {pid for pid in result.stdout.strip().split(",") if pid}


_MODULE_START_PIDS = _sysml_grpc_pids()


def test_no_new_orphan_sysml_grpc_processes_remain() -> None:
    _load_valid()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and (_sysml_grpc_pids() - _MODULE_START_PIDS):
        time.sleep(0.5)
    assert not (_sysml_grpc_pids() - _MODULE_START_PIDS)


# --- no protobuf span leakage ---


def test_diagnostic_spans_are_not_leaked() -> None:
    snapshot = OpenSysMLFileAdapter().load(INVALID_MODEL)
    assert snapshot.diagnostics
    assert all(d.span is None for d in snapshot.diagnostics)
