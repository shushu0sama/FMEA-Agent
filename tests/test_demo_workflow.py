"""D5 report provenance and integration with real D4 transport budgets."""

import json

import httpx
import pytest
from pydantic import ValidationError
from test_demo_contracts import report_data  # noqa: F401
from test_demo_service import (  # noqa: F401
    Repository,
    SequenceClient,
    inputs,
    ready,
    service,
    waiting,
)

from fmea_agent.domain.demo_evidence import EvidenceRef
from fmea_agent.domain.demo_knowledge import KnowledgeHit, RetrievalResult
from fmea_agent.domain.system_model import Function


def test_graph_waiting_state_can_roundtrip_without_adapters(inputs):  # noqa: F811
    from fmea_agent.agents.demo_state import DemoGraphState, DemoSession
    from fmea_agent.agents.demo_workflow import build_demo_workflow_graph

    client = SequenceClient(waiting())
    repo = Repository()
    graph = build_demo_workflow_graph(repo, client)
    state = DemoGraphState(
        session=DemoSession(id="session", input_digest=inputs.input_digest, inputs=inputs),
        operation="intake",
        message="分析 motor",
    )
    result = DemoSession.model_validate(graph.invoke(state)["session"])
    assert result.phase == "WAITING_INPUT" and not repo.calls
    assert DemoSession.model_validate_json(result.model_dump_json()) == result
    payload = result.model_dump()
    payload["http_client"] = object()
    with pytest.raises(ValidationError):
        DemoSession.model_validate(payload)


def test_report_preserves_rejected_evidence_but_generation_never_receives_it(
    inputs,  # noqa: F811
    report_data,  # noqa: F811
):
    keep = EvidenceRef(id="keep", source_kind="neo4j", locator="graph:a", text="历史参考")
    reject = EvidenceRef(id="reject", source_kind="neo4j", locator="graph:b", text="REJECTED_TEXT")
    audit = RetrievalResult(
        status="HITS",
        terms=["motor", "spin"],
        truncated=True,
        hits=[
            KnowledgeHit(id="h1", name="历史模式", context=[keep], applicability="UNKNOWN"),
            KnowledgeHit(
                id="h2",
                name="排除模式",
                context=[reject],
                applicability="REJECTED",
                reasons=["明确不适用"],
            ),
        ],
    )

    class HitsRepository:
        def search(self, query):
            assert query.component_id == "c1" and query.function_id == "f1"
            return audit

    inputs.model.functions.append(Function(id="root", name="pumpSpin", allocated_to=["s1"]))
    api, client, _ = service(ready, report_data["generation"], repo=HitsRepository())
    session = api.start(inputs, "公开工况", "s")
    result = api.analyze(session, "run")
    assert result.phase == "COMPLETE" and result.report.retrieval == audit
    assert {ref.id for ref in result.report.evidence} >= {"keep", "reject", "ev-spin"}
    assert "REJECTED_TEXT" not in client.prompts[-1] and "历史参考" in client.prompts[-1]
    assert any("pumpSpin" in x for x in result.report.exclusions)
    assert any("h2" in x for x in result.report.exclusions)
    assert result.report.input_snapshot == result.inputs
    assert result.report.usage["request_count"] == 2


def test_rejected_registry_collision_fails_documentation_instead_of_losing_source(
    inputs,  # noqa: F811
    report_data,  # noqa: F811
):
    class CollisionRepository:
        def search(self, query):
            return RetrievalResult(
                status="HITS",
                terms=query.terms,
                hits=[
                    KnowledgeHit(
                        id="bad",
                        name="bad",
                        applicability="REJECTED",
                        reasons=["excluded"],
                        context=[
                            EvidenceRef(
                                id="ev-spin",
                                source_kind="neo4j",
                                locator="graph:x",
                                text="different",
                            )
                        ],
                    )
                ],
            )

    api, _, _ = service(ready, report_data["generation"], repo=CollisionRepository())
    result = api.analyze(api.start(inputs, "公开工况", "s"), "run")
    assert result.phase == "FAILED" and result.report is None and result.generation is None
    assert result.errors == ["INVALID_GENERATION_INPUT"]


def test_unexpected_repository_failure_needs_explicit_degradation(
    inputs,  # noqa: F811
    report_data,  # noqa: F811
):
    class BrokenRepository:
        def search(self, query):
            raise RuntimeError("PRIVATE_CONNECTION_DETAILS")

    api, client, _ = service(ready, report_data["generation"], repo=BrokenRepository())
    stopped = api.analyze(api.start(inputs, "公开工况", "s"), "run")
    assert stopped.phase == "READY" and stopped.retrieval.status == "ERROR"
    assert (
        len(client.prompts) == 1 and "PRIVATE_CONNECTION_DETAILS" not in stopped.model_dump_json()
    )
    result = api.analyze(stopped, "consent", allow_without_retrieval=True)
    assert result.report.retrieval.error_code == "RETRIEVAL_FAILED"


def test_real_adapter_budget_and_request_deduplication_are_isolated_by_session(inputs):  # noqa: F811
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_service import DemoService

    calls = []

    def reply(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"content": json.dumps(waiting())}}
                ]
            },
        )

    with httpx.Client(transport=httpx.MockTransport(reply)) as http:
        first_client = DeepSeekLLMClient("synthetic-token", http)
        first_api = DemoService(Repository(), first_client)
        first = first_api.start(inputs, "分析", "same-start")
        for index in range(5):
            first = first_api.answer(first, "仍未知", str(index))
        assert first.question_rounds == 2 and first_client.usage()["request_count"] == 6
        failed = first_api.answer(first, "仍未知", "over-budget")
        assert failed.phase == "FAILED" and failed.errors == ["CALL_BUDGET_EXCEEDED"]
        assert first_api.answer(first, "仍未知", "over-budget") == failed
        second_client = DeepSeekLLMClient("synthetic-token", http)
        second_api = DemoService(Repository(), second_client)
        second = second_api.start(inputs, "分析", "same-start")
        assert second.phase == "WAITING_INPUT" and second.handled_request_ids == ["same-start"]
        assert second_client.usage()["request_count"] == 1 and len(calls) == 7


def test_tampered_ready_snapshot_cannot_bypass_waiting_gate(inputs):  # noqa: F811
    from fmea_agent.domain.demo_analysis import IntakeResult

    api, client, repo = service(waiting())
    first = api.start(inputs, "分析", "s")
    forged = first.model_copy(deep=True)
    forged.phase = "READY"
    forged.intake = IntakeResult(component_id="c1", function_id="f1", status="READY")
    result = api.analyze(forged, "run", allow_without_retrieval=True)
    assert result.phase == "WAITING_INPUT" and len(client.prompts) == 1 and not repo.calls


def test_unknown_continue_does_not_confirm_inferred_conditions(inputs):  # noqa: F811
    from test_demo_contracts import field

    api, client, _ = service(waiting(context={"load": field("unsupported load", "INFERENCE")}))
    first = api.start(inputs, "分析", "s")
    result = api.answer(first, "", "allow", continue_unknown=True)
    assert result.phase == "READY" and result.intake.context["load"].value is None
    assert result.intake.context["load"].status == "UNKNOWN" and len(client.prompts) == 1


def test_continue_unknown_cannot_select_a_missing_target(inputs):  # noqa: F811
    api, _, repo = service(waiting(component_id=None, function_id=None))
    first = api.start(inputs, "分析", "s")
    result = api.answer(first, "", "allow", continue_unknown=True)
    assert result.phase == "FAILED" and result.errors == ["INVALID_TARGET"] and not repo.calls
