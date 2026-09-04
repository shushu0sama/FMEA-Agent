"""Task 1 — system-side domain contract tests (SourceReference, System, Component, Function)."""

import pytest
from pydantic import ValidationError

from fmea_agent.domain.system_model import Component, Function, SourceReference, System


def test_source_reference_valid_construction() -> None:
    ref = SourceReference(
        source_type="fixture",
        source_uri="examples/simple_pump.json",
        source_element_id="hydraulic-pump",
    )
    assert ref.source_type == "fixture"
    assert ref.source_uri == "examples/simple_pump.json"
    assert ref.source_element_id == "hydraulic-pump"
    assert ref.source_version is None
    assert ref.adapter is None


def test_source_reference_missing_required_fields_raise() -> None:
    with pytest.raises(ValidationError):
        SourceReference(source_uri="x", source_element_id="y")  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        SourceReference(source_type="x", source_element_id="y")  # type: ignore[call-arg]


def test_source_reference_retains_optional_origin_fields() -> None:
    ref = SourceReference(
        source_type="sysml",
        source_uri="repo://model",
        source_element_id="el-1",
        source_version="v1.2",
        adapter="open_sysml",
        repository="https://example.invalid/repo",
        commit="abc123",
        branch="main",
        locator="pkg::El",
    )
    assert ref.source_version == "v1.2"
    assert ref.adapter == "open_sysml"
    assert ref.commit == "abc123"
    assert ref.branch == "main"
    assert ref.locator == "pkg::El"


def test_system_valid_construction() -> None:
    system = System(id="hydraulic-system", name="Hydraulic System")
    assert system.id == "hydraulic-system"
    assert system.name == "Hydraulic System"
    assert system.description is None
    assert system.source_refs == []


def test_system_missing_id_raises() -> None:
    with pytest.raises(ValidationError):
        System(name="Hydraulic System")  # type: ignore[call-arg]


def test_component_with_parent_and_type() -> None:
    comp = Component(
        id="hydraulic-pump",
        name="Hydraulic Pump",
        parent_id="hydraulic-system",
        component_type="mechanical",
    )
    assert comp.parent_id == "hydraulic-system"
    assert comp.component_type == "mechanical"


def test_component_missing_id_raises() -> None:
    with pytest.raises(ValidationError):
        Component(name="Pump")  # type: ignore[call-arg]


def test_function_allocation_and_requirements() -> None:
    func = Function(
        id="provide-pressure",
        name="Provide Hydraulic Pressure",
        allocated_to=["hydraulic-pump"],
        requirement_ids=["req-001"],
    )
    assert func.allocated_to == ["hydraulic-pump"]
    assert func.requirement_ids == ["req-001"]


def test_function_missing_id_raises() -> None:
    with pytest.raises(ValidationError):
        Function(name="Provide Pressure")  # type: ignore[call-arg]


def test_system_model_serialization_round_trip() -> None:
    system = System(
        id="hydraulic-system",
        name="Hydraulic System",
        description="Demo fixture system",
        source_refs=[
            SourceReference(
                source_type="fixture",
                source_uri="examples/simple_pump.json",
                source_element_id="hydraulic-system",
            )
        ],
    )
    data = system.model_dump(mode="json")
    assert data["id"] == "hydraulic-system"
    assert data["source_refs"][0]["source_type"] == "fixture"
    restored = System.model_validate(data)
    assert restored == system
