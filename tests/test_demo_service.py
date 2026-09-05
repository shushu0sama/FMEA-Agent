"""D5 session boundaries: resumable questions and at-most-once external work."""

import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from test_demo_contracts import field, report_data  # noqa: F401

from fmea_agent.application.demo_ports import DemoModelError
from fmea_agent.domain.demo_evidence import LoadedInputs, input_digest
from fmea_agent.domain.demo_knowledge import RetrievalResult


class SequenceClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response(prompt) if callable(response) else json.dumps(response)

    def usage(self):
        return {"request_count": len(self.prompts), "model": "deterministic-fake"}


class Repository:
    def __init__(self, status="NO_MATCH"):
        self.calls = []
        self.status = status

    def search(self, query):
        self.calls.append(query)
        return RetrievalResult(
            status=self.status,
            terms=query.terms,
            error_code="AUTH_FAILED" if self.status == "ERROR" else None,
        )


def waiting(**changes):
    return {"component_id": "c1", "function_id": "f1", "status": "WAITING_INPUT", **changes}


def ready(prompt):
    payload = json.loads(prompt.split("\n", 1)[1])
    user = [ref for ref in payload["untrusted_data"]["evidence"] if ref["source_kind"] == "user"][
        -1
    ]
    return json.dumps(
        {
            "component_id": "c1",
            "function_id": "f1",
            "status": "READY",
            "context": {
                name: field("公开工况", "FACT", [user["id"]])
                for name in ["environment", "operating_phase", "load"]
            },
        }
    )


@pytest.fixture
def inputs(report_data):  # noqa: F811
    return LoadedInputs.model_validate(report_data["input_snapshot"])


def service(*responses, repo=None):
    from fmea_agent.application.demo_service import DemoService

    client = SequenceClient(*responses)
    repository = repo or Repository()
    return DemoService(repository, client), client, repository


def test_waiting_never_retrieves_or_generates_and_start_is_idempotent(inputs):
    api, client, repo = service(waiting())
    session = api.start(inputs, "分析 motor/spin", "start")
    assert session.phase == "WAITING_INPUT" and session.question_rounds == 1
    assert session.intake.questions and session.report is None
    assert api.start(inputs, "分析 motor/spin", "start") == session
    result = api.analyze(session, "too-early", allow_without_retrieval=True)
    assert result.phase == "WAITING_INPUT"
    assert len(client.prompts) == 1 and not repo.calls


def test_two_rounds_stop_model_questions_until_explicit_unknown(inputs, report_data):  # noqa: F811
    api, client, repo = service(waiting(), waiting(), report_data["generation"])
    first = api.start(inputs, "分析", "s")
    second = api.answer(first, "仍然未知", "a")
    assert second.question_rounds == 2 and second.phase == "WAITING_INPUT"
    third = api.answer(second, "", "empty")
    assert third.inputs.evidence == second.inputs.evidence
    assert third.question_rounds == 2 and len(client.prompts) == 2
    resumed = api.answer(third, "", "consent", continue_unknown=True)
    assert resumed.phase == "READY" and resumed.intake.questions
    assert all(v.status == "UNKNOWN" and v.value is None for v in resumed.intake.context.values())
    result = api.analyze(resumed, "run")
    assert result.phase == "COMPLETE" and result.report.status == "CANDIDATE"
    assert any("environment" in x for x in result.generation.missing_information)
    assert result.report.risk_status == "NOT_EVALUATED"
    assert len(repo.calls) == 1 and len(client.prompts) == 3


def test_nonempty_answer_after_round_cap_can_supply_facts_without_third_question(inputs):
    api, client, _ = service(waiting(), waiting(), ready)
    first = api.start(inputs, "分析", "s")
    second = api.answer(first, "不知道", "a")
    third = api.answer(second, "公开工况", "b")
    assert third.phase == "READY" and third.question_rounds == 2
    assert third.intake.context["load"].status == "FACT"
    assert len(client.prompts) == 3


@pytest.mark.parametrize("kind", ["conflict", "invalid_target", "parse"])
def test_unknown_cannot_bypass_blockers(inputs, kind):
    response = waiting(component_id="invented") if kind == "invalid_target" else waiting()
    if kind == "conflict":
        inputs.conflicts = ["BOM disagrees with CSM"]
    if kind == "parse":

        def response(_):
            return "not JSON"

    api, client, repo = service(response)
    first = api.start(inputs, "分析", "s")
    assert first.phase == "FAILED" and first.diagnostic.status == "FAILED"
    second = api.answer(first, "未知", "a", continue_unknown=True)
    final = api.analyze(second, "run", allow_without_retrieval=True)
    assert final.phase == "FAILED" and final.report is None and not repo.calls
    assert len(client.prompts) == (0 if kind == "conflict" else 1)


def test_error_requires_new_explicit_request_and_preserves_original_audit(
    inputs,
    report_data,  # noqa: F811
):
    api, client, repo = service(ready, report_data["generation"], repo=Repository("ERROR"))
    session = api.start(inputs, "公开工况", "s")
    stopped = api.analyze(session, "run")
    assert stopped.phase == "READY" and stopped.retrieval.error_code == "AUTH_FAILED"
    assert stopped.report is None and len(client.prompts) == 1
    assert api.analyze(session, "run") == stopped
    with pytest.raises(DemoModelError, match="REQUEST_ID_CONFLICT"):
        api.analyze(stopped, "run", allow_without_retrieval=True)
    result = api.analyze(stopped, "allow", allow_without_retrieval=True)
    assert result.phase == "COMPLETE" and result.report.retrieval == stopped.retrieval
    assert len(repo.calls) == 1 and len(client.prompts) == 2


@pytest.mark.parametrize(
    "response",
    [{"rows": []}, lambda _: "bad", DemoModelError("TIMEOUT"), RuntimeError("PRIVATE_ERROR_BODY")],
)
def test_generation_failures_are_diagnostics_and_never_retried(inputs, response):
    api, client, repo = service(ready, response)
    session = api.start(inputs, "公开工况", "s")
    result = api.analyze(session, "run")
    assert result.phase == "FAILED" and result.report is None and result.generation is None
    assert result.diagnostic.input_snapshot == result.inputs
    assert result.diagnostic.usage["request_count"] == 2
    assert "PRIVATE_ERROR_BODY" not in result.model_dump_json()
    assert api.analyze(session, "run") == result
    assert api.analyze(result, "different").phase == "FAILED"
    assert len(client.prompts) == 2 and len(repo.calls) == 1


def test_stale_serialized_snapshots_and_concurrent_duplicate_do_not_rerun(
    inputs,
    report_data,  # noqa: F811
):
    from fmea_agent.agents.demo_state import DemoSession

    api, client, repo = service(ready, report_data["generation"])
    session = api.start(inputs, "公开工况", "s")
    restored = DemoSession.model_validate_json(session.model_dump_json())
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: api.analyze(restored, "run"), range(2)))
    assert results[0] == results[1] and results[0].phase == "COMPLETE"
    assert len(client.prompts) == 2 and len(repo.calls) == 1
    results[0].report.generation.rows.clear()
    assert api.analyze(session, "run").report.generation.rows


def test_changed_inputs_require_new_service_and_request_ids_are_session_local(inputs):
    api, client, _ = service(waiting())
    first = api.start(inputs, "分析", "s")
    changed = first.model_copy(deep=True)
    changed.inputs.files[0].sha256 = "b" * 64
    changed.inputs.input_digest = input_digest(changed.inputs.files)
    changed.input_digest = changed.inputs.input_digest
    with pytest.raises(DemoModelError, match="NEW_SESSION_REQUIRED"):
        api.answer(changed, "", "a", continue_unknown=True)
    with pytest.raises(DemoModelError, match="NEW_SESSION_REQUIRED"):
        api.start(inputs, "分析", "new-start")
    other, other_client, _ = service(waiting())
    second = other.start(inputs, "分析", "s")
    assert second.id != first.id and second.handled_request_ids == ["s"]
    assert len(client.prompts) == len(other_client.prompts) == 1
    with pytest.raises(DemoModelError, match="UNKNOWN_SESSION"):
        other.analyze(first, "run")


def test_client_cannot_be_reused_after_consuming_budget(inputs):
    from fmea_agent.application.demo_service import DemoService

    client = SequenceClient(waiting())
    client.generate("already consumed")
    api = DemoService(Repository(), client)
    with pytest.raises(DemoModelError, match="FRESH_CLIENT_REQUIRED"):
        api.start(inputs, "分析", "s")


def test_interruption_reserves_request_and_prevents_retry_side_effects(inputs):
    api, client, repo = service(ready, KeyboardInterrupt())
    session = api.start(inputs, "公开工况", "s")
    with pytest.raises(KeyboardInterrupt):
        api.analyze(session, "run")
    result = api.analyze(session, "run")
    assert result.phase == "FAILED" and "REQUEST_INTERRUPTED" in result.errors
    assert result.report is None and len(client.prompts) == 2 and len(repo.calls) == 1


def test_invalid_start_request_does_not_poison_session(inputs):
    api, client, _ = service(waiting())
    with pytest.raises(DemoModelError, match="INVALID_REQUEST_ID"):
        api.start(inputs, "分析", " ")
    result = api.start(inputs, "分析", "valid")
    assert result.phase == "WAITING_INPUT" and result.handled_request_ids == ["valid"]
    assert len(client.prompts) == 1


def test_answer_cannot_change_an_analysis_after_retrieval_even_on_repeat(inputs):
    api, client, _ = service(ready, repo=Repository("ERROR"))
    session = api.analyze(api.start(inputs, "公开工况", "s"), "run")
    for _ in range(2):
        with pytest.raises(DemoModelError, match="ANALYSIS_ALREADY_STARTED"):
            api.answer(session, "改目标", "change")
    assert len(client.prompts) == 1
