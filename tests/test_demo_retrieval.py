"""Application query provenance, identity and explicit exclusion boundaries."""

import pytest
from test_demo_contracts import report_data as shared_report_data

from fmea_agent.domain.demo_analysis import IntakeResult
from fmea_agent.domain.demo_evidence import EvidenceRef, LoadedInputs
from fmea_agent.domain.demo_knowledge import KnowledgeHit, KnowledgeQuery, RetrievalResult

report_data = shared_report_data


def test_prepare_uses_csm_names_and_keeps_recorded_alias_without_identity_merge(report_data):
    from fmea_agent.application.demo_retrieval import prepare_query

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    inputs.evidence.append(
        EvidenceRef(
            id="u1",
            source_kind="user",
            locator="answer:1",
            text="可用别名 电动机",
            limitations=["用户查询词，未经验证"],
        )
    )
    intake = IntakeResult(component_id="c1", function_id="f1", status="READY")
    query = prepare_query(inputs, intake, ["电动机"])
    assert query.terms == ["motor", "spin", "电动机"]
    assert query.component_id == "c1" and query.function_id == "f1"
    assert query.scope == "TARGET_ANALYSIS"


@pytest.mark.parametrize("change", ["bad_target", "waiting", "conflict", "unrecorded_alias"])
def test_prepare_rejects_invalid_targets_or_untraceable_terms(report_data, change):
    from fmea_agent.application.demo_retrieval import prepare_query

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    intake = IntakeResult(component_id="c1", function_id="f1", status="READY")
    terms = []
    if change == "bad_target":
        intake.component_id = "missing"
    elif change == "waiting":
        intake.status = "WAITING_INPUT"
    elif change == "conflict":
        inputs.conflicts.append("parent mismatch")
    else:
        terms = ["invented"]
    with pytest.raises(ValueError):
        prepare_query(inputs, intake, terms)


def test_explicit_exclusions_preserve_hits_audit_and_filter_reference_context():
    from fmea_agent.application.demo_retrieval import reference_hits, retrieve

    original = RetrievalResult(
        status="HITS",
        terms=["motor"],
        truncated=True,
        hits=[
            KnowledgeHit(id="1", name="a", applicability="UNKNOWN"),
            KnowledgeHit(id="2", name="b", applicability="UNKNOWN"),
        ],
    )

    class Repository:
        def search(self, query):
            return original

    result = retrieve(
        Repository(),
        KnowledgeQuery(
            terms=["motor"], scope="TARGET_ANALYSIS", component_id="c1", function_id="f1"
        ),
        rejected_ids={"1": "用户排除此对象"},
        rejected_terms={"b": "用户排除此名称"},
    )
    assert result.status == "HITS" and result.truncated and len(result.hits) == 2
    assert all(hit.applicability == "REJECTED" and hit.reasons for hit in result.hits)
    assert reference_hits(result) == []
    assert all(hit.applicability == "UNKNOWN" for hit in original.hits)


def test_sort_normalization_does_not_change_names_or_merge_identity():
    from fmea_agent.application.demo_retrieval import match_sort_key

    assert match_sort_key(" ＭＯＴＯＲ ", "id1", ["motor"], []) < match_sort_key(
        "a motor", "id2", ["motor"], []
    )


def test_query_word_budget_rejects_overflow_without_silent_loss(report_data):
    from fmea_agent.application.demo_retrieval import prepare_query

    inputs = LoadedInputs.model_validate(report_data["input_snapshot"])
    inputs.evidence.append(
        EvidenceRef(id="u", source_kind="user", locator="answer:1", text="one two three four")
    )
    intake = IntakeResult(component_id="c1", function_id="f1", status="READY")
    with pytest.raises(ValueError):
        prepare_query(inputs, intake, ["one", "two", "three", "four"])


@pytest.mark.parametrize("status", ["NO_MATCH", "ERROR"])
def test_exclusions_do_not_mask_no_match_or_error(status):
    from fmea_agent.application.demo_retrieval import reference_hits, retrieve

    class Repository:
        def search(self, query):
            return RetrievalResult(
                status=status,
                terms=query.terms,
                error_code="TIMEOUT" if status == "ERROR" else None,
            )

    result = retrieve(
        Repository(),
        KnowledgeQuery(terms=["x"], scope="SOURCE_LOOKUP"),
        rejected_ids={"absent": "用户明确排除"},
    )
    assert result.status == status and reference_hits(result) == []
