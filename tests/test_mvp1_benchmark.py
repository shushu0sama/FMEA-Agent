"""MVP-1F benchmark — B0 project-owned exact benchmark + B1 official external model.

B0: ``tests/fixtures/sysml/models/typed_inside_probe.sysml`` (project-owned,
reused from 1E; satisfies the MVP-1 benchmark spec's minimal-fixture
requirement). B1: ``tests/fixtures/sysml/models/parts_example_2_official.sysml``
— byte-identical copy of the official SysML-v2-Release training example
``sysml/src/training/07. Parts/Parts Example-2.sysml`` (provenance below).

Gold data below is human-authored expected truth. It was authored from
observed runtime facts (OpenSysML 0.4.0 + sysml-grpc v0.4.3, probe evidence
recorded in ``docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md``), never by
calling the mapper. Source identity strings are name-derived FQNs (C3) and
are asserted verbatim to pin adapter behavior.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from fmea_agent.adapters.sysml import CanonicalSystemMapper, OpenSysMLFileAdapter
from fmea_agent.adapters.sysml.exceptions import CanonicalMappingError
from fmea_agent.domain.system_model import CanonicalSystemModel

MODELS_DIR = Path(__file__).resolve().parent / "fixtures" / "sysml" / "models"

# ---------------------------------------------------------------------------
# B0 — project-owned minimal fixture: typed_inside_probe.sysml
# ---------------------------------------------------------------------------

B0_FILE = MODELS_DIR / "typed_inside_probe.sysml"

B0_GOLD = {
    "system": ("hydraulicPump", "TypedInsideProbe::hydraulicPump"),
    # (name, parent canonical id, source_element_id)
    "components": {
        ("motor", "system-1", "TypedInsideProbe::hydraulicPump::motor"),
    },
    # (name, allocated_to canonical id, source_element_id)
    "functions": {
        ("pumpSpin", "system-1", "TypedInsideProbe::hydraulicPump::pumpSpin"),
        ("spin", "component-1", "TypedInsideProbe::hydraulicPump::motor::spin"),
    },
    # (status, source_id)
    "notices": {
        ("TENTATIVE", "TypedInsideProbe"),
        ("NEEDS_RESEARCH", "TypedInsideProbe::Pump"),
        ("NEEDS_RESEARCH", "TypedInsideProbe::Motor"),
        ("NEEDS_RESEARCH", "TypedInsideProbe::Spin"),
    },
}

# ---------------------------------------------------------------------------
# B1 — official external model: Parts Example-2.sysml
#
# provenance:
#   repository: https://github.com/Systems-Modeling/SysML-v2-Release
#   commit:     29a3d2acdd49600cff872e7a55962a40400f3335 (tag 2026-07)
#   model:      sysml/src/training/07. Parts/Parts Example-2.sysml
#   license:    EPL-2.0
#   sha256:     F3CD762F65D6D51E970CAC2FD597D0785949A3566066FE8B7D6C9679A9D8E491
# ---------------------------------------------------------------------------

B1_FILE = MODELS_DIR / "parts_example_2_official.sysml"
B1_UPSTREAM_SHA256 = "F3CD762F65D6D51E970CAC2FD597D0785949A3566066FE8B7D6C9679A9D8E491"
B1_ROOT_NAME = "vehicle"

B1_GOLD = {
    "system": ("vehicle", "Parts Example-2::vehicle"),
    # (name, parent canonical id, source_element_id)
    "components": {
        ("eng", "system-1", "Parts Example-2::vehicle::eng"),
        ("cyl", "component-1", "Parts Example-2::vehicle::eng::cyl"),
    },
    "functions": set(),  # model has no ActionUsage under the selected root
    # (status, source_id)
    "notices": {
        ("TENTATIVE", "Parts Example-2"),
        ("NEEDS_RESEARCH", "Parts Example-2::Vehicle"),
        ("NEEDS_RESEARCH", "Parts Example-2::Engine"),
        ("NEEDS_RESEARCH", "Parts Example-2::Cylinder"),
        ("DEFERRED", "Parts Example-2::smallVehicle"),
        ("DEFERRED", "Parts Example-2::smallVehicle::eng"),
        ("DEFERRED", "Parts Example-2::smallVehicle::eng::cyl"),
        ("DEFERRED", "Parts Example-2::bigVehicle"),
        ("DEFERRED", "Parts Example-2::bigVehicle::eng"),
        ("DEFERRED", "Parts Example-2::bigVehicle::eng::cyl"),
    },
}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _load(file: Path):
    return OpenSysMLFileAdapter().load(file)


def _metrics(gold: set[str], actual: set[str]) -> tuple[float | None, float | None]:
    """(precision, recall); None = N/A (denominator zero), never a fake 100%."""
    precision = len(gold & actual) / len(actual) if actual else None
    recall = len(gold & actual) / len(gold) if gold else None
    return precision, recall


def _assert_exact(gold: dict, model: CanonicalSystemModel) -> None:
    system = model.system
    assert (system.name, system.source_refs[0].source_element_id) == gold["system"]
    assert system.id == "system-1"

    components = {
        (c.name, c.parent_id, c.source_refs[0].source_element_id)
        for c in model.components
    }
    assert components == gold["components"]

    functions = {
        (f.name, f.allocated_to[0], f.source_refs[0].source_element_id)
        for f in model.functions
    }
    assert functions == gold["functions"]

    notices = {(n.status, n.source_id) for n in model.notices}
    assert notices == gold["notices"]


# ---------------------------------------------------------------------------
# B0
# ---------------------------------------------------------------------------


def test_b0_loads_ok() -> None:
    snapshot = _load(B0_FILE)
    assert snapshot.load_status == "ok"
    assert snapshot.diagnostics == []


def test_b0_exact_mapping_matches_gold() -> None:
    model = CanonicalSystemMapper().map_snapshot(_load(B0_FILE))
    _assert_exact(B0_GOLD, model)


def test_b0_metrics() -> None:
    model = CanonicalSystemMapper().map_snapshot(_load(B0_FILE))
    gold_names = {name for name, _, _ in B0_GOLD["components"]}
    actual_names = {c.name for c in model.components}
    assert _metrics(gold_names, actual_names) == (1.0, 1.0)  # component P/R

    gold_functions = {name for name, _, _ in B0_GOLD["functions"]}
    actual_functions = {f.name for f in model.functions}
    assert _metrics(gold_functions, actual_functions) == (1.0, 1.0)  # function P/R

    # parent accuracy (exact pairs)
    gold_pairs = {(name, parent) for name, parent, _ in B0_GOLD["components"]}
    actual_pairs = {(c.name, c.parent_id) for c in model.components}
    assert gold_pairs == actual_pairs

    # source-reference completeness: every mapped entity carries the exact
    # source_element_id recorded in gold
    expected_srcs = {src for _, _, src in B0_GOLD["components"]} | {
        B0_GOLD["system"][1]
    } | {src for _, _, src in B0_GOLD["functions"]}
    actual_srcs = {model.system.source_refs[0].source_element_id} | {
        c.source_refs[0].source_element_id for c in model.components
    } | {f.source_refs[0].source_element_id for f in model.functions}
    assert actual_srcs == expected_srcs


def test_b0_unsupported_element_reporting_is_exact() -> None:
    model = CanonicalSystemMapper().map_snapshot(_load(B0_FILE))
    notices = {(n.status, n.source_id) for n in model.notices}
    assert notices == B0_GOLD["notices"]


# ---------------------------------------------------------------------------
# B1
# ---------------------------------------------------------------------------


def test_b1_fixture_is_byte_identical_to_upstream() -> None:
    digest = hashlib.sha256(B1_FILE.read_bytes()).hexdigest().upper()
    assert digest == B1_UPSTREAM_SHA256


def test_b1_loads_ok_standalone() -> None:
    snapshot = _load(B1_FILE)
    assert snapshot.load_status == "ok"
    assert snapshot.diagnostics == []


def test_b1_auto_root_rejected_with_candidate_list() -> None:
    try:
        CanonicalSystemMapper().map_snapshot(_load(B1_FILE))
    except CanonicalMappingError as exc:
        message = str(exc)
        assert "vehicle" in message
        assert "smallVehicle" in message
        assert "bigVehicle" in message
    else:
        raise AssertionError("auto root selection must fail for multi-root models")


def test_b1_explicit_root_mapping_matches_gold() -> None:
    snapshot = _load(B1_FILE)
    # root source id comes from the real snapshot, never from a guessed FQN
    root = next(
        e
        for e in snapshot.elements
        if e.metatype == "partUsage" and e.name == B1_ROOT_NAME
    )
    assert root.source_id == B1_GOLD["system"][1]
    model = CanonicalSystemMapper().map_snapshot(
        snapshot, root_source_id=root.source_id
    )
    _assert_exact(B1_GOLD, model)


def test_b1_functions_are_absent_and_metrics_are_na() -> None:
    snapshot = _load(B1_FILE)
    root = next(
        e
        for e in snapshot.elements
        if e.metatype == "partUsage" and e.name == B1_ROOT_NAME
    )
    model = CanonicalSystemMapper().map_snapshot(
        snapshot, root_source_id=root.source_id
    )
    assert model.functions == []
    gold_functions = {name for name, _, _ in B1_GOLD["functions"]}
    actual_functions = {f.name for f in model.functions}
    # denominator zero on both sides -> N/A, never a fabricated 100%
    assert _metrics(gold_functions, actual_functions) == (None, None)


def test_b1_component_metrics() -> None:
    snapshot = _load(B1_FILE)
    root = next(
        e
        for e in snapshot.elements
        if e.metatype == "partUsage" and e.name == B1_ROOT_NAME
    )
    model = CanonicalSystemMapper().map_snapshot(
        snapshot, root_source_id=root.source_id
    )
    gold_names = {name for name, _, _ in B1_GOLD["components"]}
    actual_names = {c.name for c in model.components}
    assert _metrics(gold_names, actual_names) == (1.0, 1.0)

    gold_pairs = {(name, parent) for name, parent, _ in B1_GOLD["components"]}
    actual_pairs = {(c.name, c.parent_id) for c in model.components}
    assert gold_pairs == actual_pairs


def test_b1_unsupported_element_reporting_is_exact() -> None:
    snapshot = _load(B1_FILE)
    root = next(
        e
        for e in snapshot.elements
        if e.metatype == "partUsage" and e.name == B1_ROOT_NAME
    )
    model = CanonicalSystemMapper().map_snapshot(
        snapshot, root_source_id=root.source_id
    )
    notices = {(n.status, n.source_id) for n in model.notices}
    assert notices == B1_GOLD["notices"]
