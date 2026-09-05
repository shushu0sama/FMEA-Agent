"""Run the smoke entry with controlled repositories and check redacted output."""

import json
import runpy

import pytest

from fmea_agent.domain.demo_evidence import EvidenceRef
from fmea_agent.domain.demo_knowledge import KnowledgeHit, RetrievalResult


@pytest.mark.parametrize(
    "case,expected,exit_code",
    [
        ("missing", "SKIPPED", 0),
        ("auth", "ERROR", 1),
        ("empty", "FAILED", 1),
        ("ok", "PASS", 0),
        ("bad_locator", "FAILED", 1),
        ("false_no_match", "FAILED", 1),
    ],
)
def test_smoke_checks_lookup_locator_and_absent_term_without_printing_records(
    monkeypatch,
    capsys,
    case,
    expected,
    exit_code,
):
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    class Repository:
        closed = False

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.closed = True

        def smoke_focus(self):
            errors = {
                "missing": "CONFIG_MISSING",
                "auth": "AUTH_FAILED",
                "empty": "NO_SOURCE_FOCUS",
            }
            return (
                (None, None, errors[case])
                if case in errors
                else ("private-id", "private-name", None)
            )

        def search(self, query):
            if query.terms == ["private-name"]:
                assert query.scope == "SOURCE_LOOKUP"
                ref = EvidenceRef(
                    id="e1",
                    source_kind="neo4j",
                    text="private-text",
                    locator=json.dumps(
                        {
                            "start_id": "wrong" if case == "bad_locator" else "private-id",
                            "edge_id": "edge1",
                            "database": "neo4j",
                            "retrieved_at": "timestamp",
                        }
                    ),
                )
                return RetrievalResult(
                    status="HITS",
                    terms=query.terms,
                    hits=[
                        KnowledgeHit(
                            id="m1",
                            name="private-mode",
                            context=[ref],
                            applicability="SOURCE_CONTEXT_ONLY",
                        )
                    ],
                )
            assert query.terms[0].startswith("demo-no-match-")
            if case == "false_no_match":
                return RetrievalResult(status="ERROR", terms=query.terms, error_code="TIMEOUT")
            return RetrievalResult(status="NO_MATCH", terms=query.terms)

    repo = Repository()
    monkeypatch.setattr(Neo4jSourceKnowledgeRepository, "from_env", lambda: repo)
    main = runpy.run_path("scripts/demo_neo4j_smoke.py")["main"]
    assert main() == exit_code
    output = capsys.readouterr().out
    assert json.loads(output)["status"] == expected
    assert "private" not in output and repo.closed
