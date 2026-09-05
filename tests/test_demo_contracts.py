"""D2 contracts reject unsupported authority, broken provenance and incomplete reports."""

import copy
import hashlib
import json

import pytest
from pydantic import ValidationError


def evidence(identifier="ev-spin"):
    return {
        "id": identifier,
        "source_kind": "sysml",
        "locator": "sysml-1#element=spin",
        "text": "spin",
        "content_sha256": "a" * 64,
        "derived_from": ["sysml-1"],
        "limitations": ["Synthetic contract fixture; no engineering approval"],
    }


def field(value=None, status="UNKNOWN", refs=None):
    return {"value": value, "status": status, "evidence_ids": refs or [], "limitations": []}


@pytest.fixture
def report_data():
    files = [
        {
            "id": "sysml-1",
            "filename": "model.sysml",
            "kind": "sysml",
            "sha256": "a" * 64,
            "size_bytes": 4,
            "derived_from": [],
            "parser": "opensysml",
            "parser_version": "0.4.0",
            "runtime_version": "v0.4.3",
        }
    ]
    digest = hashlib.sha256(
        json.dumps(files, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    model = {
        "system": {"id": "s1", "name": "system"},
        "components": [{"id": "c1", "name": "motor", "parent_id": "s1"}],
        "functions": [
            {
                "id": "f1",
                "name": "spin",
                "allocated_to": ["c1"],
                "source_refs": [
                    {
                        "source_type": "sysml_file",
                        "source_uri": "sysml-1",
                        "source_element_id": "spin",
                    }
                ],
            }
        ],
    }
    inputs = {
        "files": files,
        "model": model,
        "evidence": [evidence()],
        "missing_files": ["design", "bom"],
        "conflicts": [],
        "input_digest": digest,
    }
    return {
        "schema_version": "demo-v1",
        "run_id": "run-1",
        "input_digest": digest,
        "input_snapshot": inputs,
        "status": "CANDIDATE",
        "component_id": "c1",
        "function_id": "f1",
        "context": {},
        "evidence": [evidence()],
        "retrieval": {
            "status": "NO_MATCH",
            "hits": [],
            "terms": ["motor"],
            "truncated": False,
            "error_code": None,
        },
        "generation": {
            "rows": [
                {
                    "mode": field("does not spin", "INFERENCE", ["ev-spin"]),
                    "causes": [],
                    "mechanism": field(),
                    "effects": {
                        level: field() for level in ["LOCAL", "NEXT_HIGHER_LEVEL", "END_EFFECT"]
                    },
                    "existing_controls": [],
                    "suggested_actions": [],
                    "validation_suggestions": [],
                }
            ],
            "assumptions": [],
            "missing_information": ["load"],
        },
        "exclusions": [],
        "risk_status": "NOT_EVALUATED",
        "optimization_status": "SKIPPED",
        "usage": {},
    }


@pytest.mark.parametrize(
    "payload",
    [
        field("voltage", "FACT"),
        field("history", "RETRIEVED_KNOWLEDGE"),
        field(None, "FACT", ["ev-spin"]),
        field("", "FACT", ["ev-spin"]),
        field("x", "APPROVED", ["ev-spin"]),
        {"value": "x"},
        {**field("x", "INFERENCE"), "AP": "H"},
    ],
)
def test_field_rejects_unfounded_status_or_extra_fields(payload):
    from fmea_agent.domain.demo_evidence import FieldValue

    with pytest.raises(ValidationError):
        FieldValue.model_validate(payload)


def test_fact_with_reference_does_not_prove_engineering_truth():
    from fmea_agent.domain.demo_evidence import FieldValue

    value = FieldValue.model_validate(field("spin", "FACT", ["ev-spin"]))
    assert value.value == "spin" and value.status == "FACT"


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "HITS", "hits": [], "terms": ["motor"]},
        {"status": "NO_MATCH", "error_code": "TIMEOUT"},
        {"status": "ERROR", "error_code": None},
    ],
)
def test_retrieval_states_are_consistent(payload):
    from fmea_agent.domain.demo_knowledge import RetrievalResult

    with pytest.raises(ValidationError):
        RetrievalResult.model_validate(payload)


@pytest.mark.parametrize(
    "updates",
    [
        {"terms": []},
        {"terms": [" "]},
        {"terms": ["x"] * 6},
        {"terms": ["x" * 81]},
        {"limit": 0},
        {"limit": 21},
        {"scope": "SOURCE_LOOKUP", "component_id": "c1"},
        {"scope": "TARGET_ANALYSIS"},
    ],
)
def test_knowledge_query_has_bounded_terms_and_explicit_scope(updates):
    from fmea_agent.domain.demo_knowledge import KnowledgeQuery

    with pytest.raises(ValidationError):
        KnowledgeQuery.model_validate({"terms": ["motor"], "scope": "SOURCE_LOOKUP", **updates})


def test_report_roundtrip_needs_no_session_files(report_data):
    from fmea_agent.domain.demo_analysis import CandidateReport

    report = CandidateReport.model_validate(report_data)
    restored = CandidateReport.model_validate_json(report.model_dump_json())
    assert restored == report
    assert restored.input_snapshot.model.functions[0].source_refs[0].source_element_id == "spin"
    assert restored.generation.rows[0].mode.evidence_ids == ["ev-spin"]


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate_evidence",
        "missing_evidence",
        "missing_input_evidence",
        "altered_input_evidence",
        "unknown_parent",
        "digest_mismatch",
        "input_digest_mismatch",
        "unknown_component",
        "unknown_function",
        "unallocated_function",
        "missing_effect",
        "extra_score",
        "approved",
        "missing_file_ref",
        "duplicate_file",
        "absolute_filename",
        "traversal_filename",
        "extra_csm_field",
        "extra_source_field",
        "cyclic_provenance",
    ],
)
def test_report_rejects_invalid_provenance_scope_and_authority(report_data, mutation):
    from fmea_agent.domain.demo_analysis import CandidateReport

    data = copy.deepcopy(report_data)
    inputs = data["input_snapshot"]
    row = data["generation"]["rows"][0]
    if mutation == "duplicate_evidence":
        data["evidence"].append(evidence())
    elif mutation == "missing_evidence":
        row["mode"]["evidence_ids"] = ["invented"]
    elif mutation == "missing_input_evidence":
        data["evidence"] = []
        row["mode"]["evidence_ids"] = []
    elif mutation == "altered_input_evidence":
        data["evidence"][0]["text"] = "changed claim"
    elif mutation == "unknown_parent":
        data["evidence"].append({**evidence("ev-extra"), "derived_from": ["invented"]})
    elif mutation == "digest_mismatch":
        data["input_digest"] = "b" * 64
    elif mutation == "input_digest_mismatch":
        inputs["input_digest"] = data["input_digest"] = "b" * 64
    elif mutation in {"unknown_component", "unknown_function"}:
        data["component_id" if mutation == "unknown_component" else "function_id"] = "invented"
    elif mutation == "unallocated_function":
        inputs["model"]["functions"][0]["allocated_to"] = ["s1"]
    elif mutation == "missing_effect":
        del row["effects"]["END_EFFECT"]
    elif mutation == "extra_score":
        row["S"] = 10
    elif mutation == "approved":
        data["status"] = "APPROVED"
    elif mutation == "missing_file_ref":
        inputs["model"]["functions"][0]["source_refs"][0]["source_uri"] = "missing.sysml"
    elif mutation == "duplicate_file":
        inputs["files"].append(inputs["files"][0])
    elif mutation == "absolute_filename":
        inputs["files"][0]["filename"] = "C:/secret/model.sysml"
    elif mutation == "traversal_filename":
        inputs["files"][0]["filename"] = "../../model.sysml"
    elif mutation == "extra_csm_field":
        inputs["model"]["components"][0]["approved"] = True
    elif mutation == "extra_source_field":
        inputs["model"]["functions"][0]["source_refs"][0]["invented_row"] = 47
    elif mutation == "cyclic_provenance":
        data["evidence"].extend(
            [
                {**evidence("ev-a"), "derived_from": ["ev-b"]},
                {**evidence("ev-b"), "derived_from": ["ev-a"]},
            ]
        )
    with pytest.raises(ValidationError):
        CandidateReport.model_validate(data)


def test_diagnostic_requires_failure_and_preserves_inputs(report_data):
    from fmea_agent.domain.demo_analysis import DiagnosticReport

    data = {
        "schema_version": "demo-v1-diagnostic",
        "run_id": "run-1",
        "status": "FAILED",
        "input_snapshot": report_data["input_snapshot"],
        "errors": ["INVALID_RESPONSE"],
    }
    report = DiagnosticReport.model_validate(data)
    assert DiagnosticReport.model_validate_json(report.model_dump_json()) == report
    with pytest.raises(ValidationError):
        DiagnosticReport.model_validate({**data, "errors": []})


def test_intake_blocks_conflict_or_invalid_target(report_data):
    from fmea_agent.application.demo_intake import validate_intake
    from fmea_agent.domain.demo_analysis import IntakeResult
    from fmea_agent.domain.demo_evidence import LoadedInputs

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    intake = IntakeResult(component_id="c1", function_id="f1", status="READY")
    assert validate_intake(inputs, intake).status == "READY"
    inputs.conflicts.append("BOM parent mismatch")
    blocked = validate_intake(inputs, intake)
    assert blocked.status == "BLOCKED"
    assert intake.status == "READY"


@pytest.mark.parametrize("component_id,function_id", [("c1", None), (None, "f1"), (None, None)])
def test_incomplete_valid_target_remains_waiting_for_input(report_data, component_id, function_id):
    from fmea_agent.application.demo_intake import validate_intake
    from fmea_agent.domain.demo_analysis import IntakeResult
    from fmea_agent.domain.demo_evidence import LoadedInputs

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    intake = IntakeResult(
        component_id=component_id, function_id=function_id, status="WAITING_INPUT"
    )
    assert validate_intake(inputs, intake).status == "WAITING_INPUT"


@pytest.mark.parametrize("component_id,function_id", [("invented", None), (None, "invented")])
def test_nonexistent_partial_target_is_blocked(report_data, component_id, function_id):
    from fmea_agent.application.demo_intake import validate_intake
    from fmea_agent.domain.demo_analysis import IntakeResult
    from fmea_agent.domain.demo_evidence import LoadedInputs

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    intake = IntakeResult(
        component_id=component_id, function_id=function_id, status="WAITING_INPUT"
    )
    assert validate_intake(inputs, intake).status == "BLOCKED"
