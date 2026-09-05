"""Synthetic graph records exercise the adapter without contacting a database."""

import hashlib
import json
import re

import pytest
from neo4j.exceptions import AuthError, Neo4jError, ServiceUnavailable

from fmea_agent.domain.demo_knowledge import KnowledgeQuery


def candidate(identifier="m1", name="stops", matched=None):
    return {"mode_id": identifier, "mode_name": name, "matched_names": matched or [name]}


def edge(identifier, relation, target, *, mode="m1", start="m1", start_name="stops"):
    return {
        "mode_id": mode,
        "edge_id": identifier,
        "relation": relation,
        "start_id": start,
        "start_name": start_name,
        "end_id": target,
        "end_name": target,
    }


class FakeDriver:
    """Only the documented read session/explicit transaction APIs are available."""

    def __init__(self, batches, failure=None):
        self.batches = list(batches)
        self.calls = []
        self.failure = failure
        self.closed = False
        self.exits = 0

    def session(self, **kwargs):
        assert kwargs == {"database": "neo4j", "default_access_mode": "READ"}
        return self

    def begin_transaction(self, **kwargs):
        assert kwargs == {"timeout": 10.0}
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.exits += 1

    def run(self, query, parameters):
        from fmea_agent.adapters.neo4j.failure_knowledge import READ_QUERIES

        assert query in READ_QUERIES
        assert query.lstrip().startswith("MATCH")
        assert not re.search(
            r"\b(CREATE|MERGE|DELETE|SET|REMOVE|DROP|APOC|LOAD|SHOW)\b", query, re.I
        )
        self.calls.append((query, parameters))
        if self.failure:
            raise self.failure
        return iter(self.batches.pop(0))

    def close(self):
        self.closed = True


def search(driver, *, terms=None, scope="TARGET_ANALYSIS", limit=20):
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    query = KnowledgeQuery(
        terms=terms or ["stops"],
        scope=scope,
        limit=limit,
        **({"component_id": "c1", "function_id": "f1"} if scope == "TARGET_ANALYSIS" else {}),
    )
    return Neo4jSourceKnowledgeRepository(driver, "neo4j").search(query)


def test_four_edges_remain_independent_and_shared_focus_context_is_preserved():
    contexts = [
        edge("fm1", "故障模式", "m1", start="focus1", start_name="focus one"),
        edge("fm2", "故障模式", "m1", start="focus2", start_name="focus two"),
    ]
    associations = [
        edge("c1", "故障起因", "cause1"),
        edge("c2", "故障起因", "cause2"),
        edge("e1", "故障影响", "effect1"),
        edge("e2", "故障影响", "effect2"),
    ]
    driver = FakeDriver([[candidate()], [], contexts, associations])
    result = search(driver)
    assert result.status == "HITS" and not result.truncated
    assert len(result.hits) == 1
    hit = result.hits[0]
    assert hit.applicability == "UNKNOWN"
    assert len(hit.associations) == 4 and len(hit.context) == 3  # mode + two focus edges
    assert {json.loads(ref.text)["edge_id"] for ref in hit.associations} == {"c1", "c2", "e1", "e2"}
    for ref in hit.context + hit.associations:
        locator = json.loads(ref.locator)
        assert locator["database"] == "neo4j" and locator["retrieved_at"].endswith("+00:00")
        assert ref.content_sha256 == hashlib.sha256(ref.text.encode()).hexdigest()
        assert ref.source_kind == "neo4j" and ref.limitations
        assert "row" not in locator and "workbook" not in locator
    assert driver.exits == 2 and not driver.closed  # injected driver belongs to caller


def test_both_entries_merge_by_id_and_exact_normalized_name_ranks_first():
    driver = FakeDriver(
        [
            [candidate("m1", "a partial spin"), candidate("m2", "ＳＰＩＮ")],
            [candidate("m2", "ＳＰＩＮ"), candidate("m3", "z stops", ["spin"])],
            [],
            [],
        ]
    )
    result = search(driver, terms=[" spin "], limit=2, scope="SOURCE_LOOKUP")
    assert [hit.name for hit in result.hits] == ["z stops", "ＳＰＩＮ"]
    assert result.truncated
    assert all(hit.applicability == "SOURCE_CONTEXT_ONLY" for hit in result.hits)
    assert result.terms == [" spin "]


def test_no_match_queries_both_entries_and_does_not_expand_context():
    driver = FakeDriver([[], []])
    result = search(driver)
    assert result.status == "NO_MATCH" and not result.truncated and result.error_code is None
    assert len(driver.calls) == 2


def test_user_cypher_is_only_a_parameter_and_never_query_text():
    term = "x') DETACH DELETE n //"
    driver = FakeDriver([[], []])
    search(driver, terms=[term], limit=1)
    for query, parameters in driver.calls:
        assert term not in query
        assert parameters == {"terms": [term], "fetch_limit": 2}


@pytest.mark.parametrize(
    "error,code",
    [
        (AuthError("private password"), "AUTH_FAILED"),
        (TimeoutError("private URI"), "TIMEOUT"),
        (
            type(
                "ServerTimeout",
                (Neo4jError,),
                {"code": property(lambda self: "Neo.ClientError.Transaction.TransactionTimedOut")},
            )("private"),
            "TIMEOUT",
        ),
        (ServiceUnavailable("private host"), "CONNECTION_FAILED"),
        (Neo4jError("private"), "QUERY_FAILED"),
    ],
)
def test_errors_are_safe_errors_not_empty_success(error, code):
    driver = FakeDriver([], failure=error)
    result = search(driver)
    assert result.status == "ERROR" and result.error_code == code and not result.hits
    assert "private" not in result.model_dump_json()
    assert len(driver.calls) == 1 and driver.exits == 2


def test_partial_query_failure_discards_hits():
    driver = FakeDriver([[candidate()], [], [], [edge("c1", "故障起因", "cause")]])
    original = driver.run

    def run(query, parameters):
        if len(driver.calls) == 3:
            raise TimeoutError("sensitive")
        return original(query, parameters)

    driver.run = run
    result = search(driver)
    assert result.status == "ERROR" and result.error_code == "TIMEOUT" and result.hits == []


def test_malformed_graph_record_is_error_not_silently_dropped():
    result = search(FakeDriver([[candidate(name="")], [], [], []]))
    assert result.status == "ERROR" and result.error_code == "INVALID_RECORD"


def test_context_and_association_budget_reports_truncation():
    edges = [edge(f"e{i}", "故障起因", f"cause{i}") for i in range(1001)]
    result = search(FakeDriver([[candidate()], [], [], edges]))
    assert result.truncated and len(result.hits[0].associations) == 1000
    assert any("截断" in reason for reason in result.hits[0].reasons)


def test_same_name_different_ids_and_parallel_edges_are_not_merged():
    rows = [candidate("m1"), candidate("m2")]
    edges = [edge("e1", "故障起因", "cause"), edge("e2", "故障起因", "cause")]
    result = search(FakeDriver([rows, [], [], edges]))
    assert len(result.hits) == 2 and len(result.hits[0].associations) == 2


def test_factory_missing_config_never_constructs_driver(monkeypatch):
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    for name in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE"]:
        monkeypatch.delenv(name, raising=False)
    with Neo4jSourceKnowledgeRepository.from_env() as repo:
        result = repo.search(KnowledgeQuery(terms=["x"], scope="SOURCE_LOOKUP"))
    assert result.status == "ERROR" and result.error_code == "CONFIG_MISSING"


def test_factory_bounds_connections_retries_and_closes_owned_driver(monkeypatch):
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    for key, value in {
        "URI": "bolt://localhost:7687",
        "USERNAME": "test",
        "PASSWORD": "test-only",
    }.items():
        monkeypatch.setenv("NEO4J_" + key, value)
    monkeypatch.delenv("NEO4J_DATABASE", raising=False)
    driver = FakeDriver([[], []])

    def create(uri, **kwargs):
        assert uri == "bolt://localhost:7687"
        assert kwargs["auth"] == ("test", "test-only")
        assert kwargs["connection_timeout"] == kwargs["connection_acquisition_timeout"] == 10.0
        assert kwargs["max_transaction_retry_time"] == 0.0
        return driver

    monkeypatch.setattr("neo4j.GraphDatabase.driver", create)
    with Neo4jSourceKnowledgeRepository.from_env() as repo:
        assert repo.search(KnowledgeQuery(terms=["x"], scope="SOURCE_LOOKUP")).status == "NO_MATCH"
    assert driver.closed


def test_function_lower_part_and_lower_function_context_edges_remain_independent():
    contexts = [
        edge("fm", "故障模式", "m1", start="focus"),
        edge("ff", "功能", "function", start="focus"),
        edge("fl", "下一低分析层次", "lower", start="focus"),
        edge("lf", "下一低层次功能", "lower-function", start="lower"),
        edge("fh", "上一高层次功能及要求", "higher", start="focus"),
    ]
    controls = [edge("pc", "预防控制措施", "prevention"), edge("dc", "探测措施", "detection")]
    driver = FakeDriver([[], [candidate(matched=["lower-function"])], contexts, controls])
    result = search(driver, terms=["lower-function"])
    hit = result.hits[0]
    assert len(hit.context) == 6 and len(hit.associations) == 2
    assert {json.loads(ref.text)["relation"] for ref in hit.associations} == {
        "预防控制措施",
        "探测措施",
    }
    assert "lower-function" in "".join(hit.reasons)


def test_shared_context_edge_has_same_evidence_id_and_content_across_modes():
    one = edge("same-edge", "功能", "function", start="focus")
    two = {**one, "mode_id": "m2"}
    result = search(FakeDriver([[candidate(), candidate("m2")], [], [one, two], []]))
    first, second = [hit.context[1] for hit in result.hits]
    assert first == second


@pytest.mark.parametrize(
    "bad",
    [
        {"mode_id": "unknown"},
        {"end_name": None},
        {"edge_id": " "},
    ],
)
def test_invalid_relation_never_becomes_partial_success(bad):
    relation = {**edge("e1", "故障起因", "cause"), **bad}
    result = search(FakeDriver([[candidate()], [], [], [relation]]))
    assert result.status == "ERROR" and result.error_code == "INVALID_RECORD"


def test_context_budget_also_marks_truncation_and_missing_context_is_not_inferred():
    contexts = [edge(f"e{i}", "功能", f"function{i}", start="focus") for i in range(1001)]
    result = search(FakeDriver([[candidate()], [], contexts, []]))
    assert result.truncated and len(result.hits[0].context) == 1001  # mode plus 1000 edges
    assert result.hits[0].applicability == "UNKNOWN"


def test_duplicate_candidates_do_not_false_truncate_and_new_search_has_new_ids():
    driver = FakeDriver([[candidate()], [candidate()], [], []] * 2)
    first, second = search(driver, limit=1), search(driver, limit=1)
    assert not first.truncated and not second.truncated
    assert len(first.hits) == 1
    assert first.hits[0].id != second.hits[0].id
    assert first.hits[0].context[0].content_sha256 == second.hits[0].context[0].content_sha256


def test_wrapped_connection_timeout_is_classified_without_leaking_message():
    error = ServiceUnavailable("private address")
    error.__cause__ = TimeoutError("private socket")
    result = search(FakeDriver([], failure=error))
    assert result.error_code == "TIMEOUT" and "private" not in result.model_dump_json()


@pytest.mark.parametrize(
    "case,code", [("blank_db", "CONFIG_INVALID"), ("bad_uri", "CONFIG_INVALID")]
)
def test_invalid_configuration_is_safely_reported(monkeypatch, case, code):
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    for key, value in {
        "URI": "not-a-uri-private",
        "USERNAME": "private",
        "PASSWORD": "private",
        "DATABASE": " " if case == "blank_db" else "neo4j",
    }.items():
        monkeypatch.setenv("NEO4J_" + key, value)
    with Neo4jSourceKnowledgeRepository.from_env() as repo:
        result = repo.search(KnowledgeQuery(terms=["x"], scope="SOURCE_LOOKUP"))
    assert result.error_code == code and "private" not in result.model_dump_json()


def test_smoke_focus_uses_fixed_read_and_handles_empty_graph():
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    driver = FakeDriver([[{"focus_id": "f1", "focus_name": "focus"}], []])
    repo = Neo4jSourceKnowledgeRepository(driver, "neo4j")
    assert repo.smoke_focus() == ("f1", "focus", None)
    assert repo.smoke_focus() == (None, None, "NO_SOURCE_FOCUS")
    assert driver.exits == 4
