"""Task 7 — CLI fixture loading tests: valid loads, stable IDs, invalid input errors."""

from pathlib import Path

import pytest

from fmea_agent.cli.loading import load_failure_library, load_system_fixture

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_load_system_fixture_populates_repository_and_request() -> None:
    repo, request = load_system_fixture(EXAMPLES / "simple_pump.json")
    assert request.system_id == "hydraulic-system"
    assert request.component_id == "hydraulic-pump"
    assert request.function_id == "provide-pressure"

    system = repo.get_system("hydraulic-system")
    assert system is not None
    assert system.name == "Hydraulic System"

    component = repo.get_component("hydraulic-pump")
    assert component is not None
    assert component.name == "Hydraulic Pump"
    assert component.parent_id == "hydraulic-system"

    functions = repo.list_functions("hydraulic-pump")
    assert [f.id for f in functions] == ["provide-pressure"]
    assert functions[0].name == "Provide Hydraulic Pressure"


def test_load_failure_library_finds_candidate_by_names() -> None:
    repo = load_failure_library(EXAMPLES / "demo_failure_library.json")
    candidates = repo.find_failure_modes("Hydraulic Pump", "Provide Hydraulic Pressure")
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.value == "Loss of hydraulic pressure"
    assert candidate.item_id is None
    assert candidate.function_id is None
    assert [ev.source for ev in candidate.evidence] == ["demo-failure-library:001"]


def test_load_failure_library_unknown_pair_returns_empty() -> None:
    repo = load_failure_library(EXAMPLES / "demo_failure_library.json")
    assert repo.find_failure_modes("Unknown Item", "Unknown Function") == []


def test_load_system_fixture_rejects_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_system_fixture(bad)


def test_load_system_fixture_rejects_non_object_root(tmp_path: Path) -> None:
    bad = tmp_path / "list.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_system_fixture(bad)


def test_load_system_fixture_rejects_missing_analysis_request(tmp_path: Path) -> None:
    bad = tmp_path / "no_request.json"
    bad.write_text(
        '{"system": {"id": "s", "name": "S"}, "components": [], "functions": []}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="analysis_request"):
        load_system_fixture(bad)


def test_load_failure_library_rejects_missing_entries(tmp_path: Path) -> None:
    bad = tmp_path / "no_entries.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="entries"):
        load_failure_library(bad)


def test_load_failure_library_rejects_invalid_failure_mode(tmp_path: Path) -> None:
    bad = tmp_path / "bad_mode.json"
    bad.write_text(
        '{"entries": [{"item_name": "X", "function_name": "Y", "failure_modes": [{}]}]}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_failure_library(bad)
