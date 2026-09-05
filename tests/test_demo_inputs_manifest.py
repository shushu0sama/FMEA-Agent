"""D1 pack contracts: byte provenance, real mapping, reproducibility and safe writes."""

import csv
import hashlib
import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from fmea_agent.adapters.sysml import CanonicalSystemMapper, OpenSysMLFileAdapter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/fixtures/sysml/models/typed_inside_probe.sysml"
SCRIPT = ROOT / "scripts/build_demo_inputs.py"
SOURCE_SHA256 = "fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5"
MOTOR_SOURCE_ID = "TypedInsideProbe::hydraulicPump::motor"


def build(source, destination):
    return runpy.run_path(str(SCRIPT))["build_demo_inputs"](source, destination)


def pack_bytes(path):
    return {file.name: file.read_bytes() for file in path.iterdir()}


def test_pack_preserves_model_and_unknown_quantity(tmp_path):
    result = build(SOURCE, tmp_path)
    assert (tmp_path / "system.sysml").read_bytes() == SOURCE.read_bytes()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    with (tmp_path / "bom.csv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == [
            "item_id", "parent_id", "name", "quantity", "unit", "source_element_id"
        ]
        assert list(reader) == [{
            "item_id": "component-1", "parent_id": "system-1", "name": "motor",
            "quantity": "", "unit": "UNKNOWN", "source_element_id": MOTOR_SOURCE_ID,
        }]
    assert set(result) == {"system.sysml", "bom.csv", "design.md", "README.md", "manifest.json"}
    for name, digest in result.items():
        assert hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest


def test_manifest_traces_files_and_model_without_absolute_paths(tmp_path):
    build(SOURCE, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"] == {
        "path": "tests/fixtures/sysml/models/typed_inside_probe.sysml",
        "sha256": SOURCE_SHA256,
        "ownership": "PROJECT_OWNED_TEACHING_FIXTURE",
    }
    assert "manifest.json" not in manifest["files"]
    for name, record in manifest["files"].items():
        assert record["sha256"] == hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
    assert manifest["files"]["bom.csv"]["derived_from"] == ["system.sysml"]
    assert manifest["bom_rows"] == [{
        "row": 2, "item_id": "component-1", "source_element_id": MOTOR_SOURCE_ID,
        "unknown_fields": ["quantity", "unit"],
    }]
    model = manifest["canonical_model"]
    entities = [model["system"], *model["components"], *model["functions"]]
    assert len(entities) == 4
    for entity in entities:
        assert entity["source_refs"][0]["source_uri"] == "system.sysml"
        assert entity["source_refs"][0]["source_element_id"].startswith("TypedInsideProbe::")
    assert str(ROOT) not in json.dumps(manifest)
    assert str(tmp_path) not in json.dumps(manifest)
    assert manifest["parser"]["name"] == "opensysml"
    assert manifest["parser"]["version"] == "0.4.0"
    assert manifest["parser"]["runtime_version"].lstrip("v") == "0.4.3"
    assert manifest["parser"]["load_status"] == "ok"
    assert manifest["parser"]["diagnostics_count"] == 0


def test_pack_is_deterministic_and_matches_committed_artifacts(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    build(SOURCE, first)
    before = pack_bytes(first)
    build(SOURCE, first)
    build(SOURCE, second)
    assert pack_bytes(first) == before == pack_bytes(second)
    assert before == pack_bytes(ROOT / "examples/demo_v1")


def test_generated_model_reloads_real_target_and_records_exclusion(tmp_path):
    build(SOURCE, tmp_path)
    snapshot = OpenSysMLFileAdapter().load(tmp_path / "system.sysml")
    assert snapshot.load_status == "ok"
    assert snapshot.diagnostics == []
    model = CanonicalSystemMapper().map_snapshot(snapshot)
    assert model.system.name == "hydraulicPump"
    assert [(c.id, c.name, c.parent_id) for c in model.components] == [
        ("component-1", "motor", "system-1")
    ]
    assert {(f.id, f.name, tuple(f.allocated_to)) for f in model.functions} == {
        ("function-1", "pumpSpin", ("system-1",)),
        ("function-2", "spin", ("component-1",)),
    }
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["analysis_scope"]["component_id"] == "component-1"
    assert manifest["analysis_scope"]["function_id"] == "function-2"
    assert manifest["analysis_scope"]["excluded_function_ids"] == ["function-1"]
    design = (tmp_path / "design.md").read_text(encoding="utf-8")
    assert "演示派生资料" in design
    assert "pumpSpin" in design and "未纳入分析" in design
    for entity in [model.system, *model.components, *model.functions]:
        assert entity.source_refs[0].source_element_id in design
    for name in ["额定电压", "转速", "材料", "数量", "运行环境", "工作循环", "主要负载"]:
        assert f"{name}：UNKNOWN" in design


def test_changed_source_is_rejected_before_writing(tmp_path):
    source = tmp_path / "changed.sysml"
    source.write_bytes(SOURCE.read_bytes() + b"\n")
    destination = tmp_path / "output"
    with pytest.raises(ValueError, match="SHA-256"):
        build(source, destination)
    assert not destination.exists()


def test_source_as_destination_cannot_overwrite_model():
    before = SOURCE.read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        build(SOURCE, SOURCE)
    assert SOURCE.read_bytes() == before


def test_output_hardlink_to_source_is_rejected(tmp_path):
    source = tmp_path / "original.sysml"
    source.write_bytes(SOURCE.read_bytes())
    destination = tmp_path / "output"
    destination.mkdir()
    os.link(source, destination / "system.sysml")
    before = source.read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        build(source, destination)
    assert source.read_bytes() == before
    assert set(pack_bytes(destination)) == {"system.sysml"}


def test_cli_works_from_another_directory(tmp_path):
    destination = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--source", str(SOURCE), "--output", str(destination)],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert set(json.loads(result.stdout)) == set(pack_bytes(destination))


def test_relocated_identical_source_has_the_same_portable_pack(tmp_path):
    source = tmp_path / "relocated.sysml"
    source.write_bytes(SOURCE.read_bytes())
    destination = tmp_path / "output"
    build(source, destination)
    assert pack_bytes(destination) == pack_bytes(ROOT / "examples/demo_v1")


def test_partial_parse_cannot_replace_existing_pack(tmp_path, monkeypatch):
    snapshot = OpenSysMLFileAdapter().load(SOURCE)
    partial = snapshot.model_copy(update={"load_status": "partial"})
    monkeypatch.setattr(OpenSysMLFileAdapter, "load", lambda self, path: partial)
    (tmp_path / "bom.csv").write_bytes(b"previous pack")
    before = pack_bytes(tmp_path)
    with pytest.raises(ValueError, match="complete parse"):
        build(SOURCE, tmp_path)
    assert pack_bytes(tmp_path) == before
