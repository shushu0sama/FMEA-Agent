"""User task regressions: real UI/parser/service, deterministic model and graph."""

import pytest
from test_demo_ui import PACK, app, load_pack, start  # noqa: F401


def test_only_relevant_steps_and_input_summary_are_shown(app):  # noqa: F811
    assert not any("候选与证据" in h.value for h in app.header)
    load_pack(app)
    assert any("hydraulicPump" in t.value for t in app.text)
    assert any("可分析对象" in t.value for t in app.text)
    assert not app.file_uploader  # The pack needs no upload controls.
    start(app)
    assert any("补充" in t.value and "下一步" in t.value for t in app.info)
    assert not any("尚无候选报告" in t.value for t in app.info)
    assert not app.download_button


def test_blank_goal_keeps_loaded_inputs_without_creating_service(app):  # noqa: F811
    load_pack(app)
    app.text_area(key="start_message").set_value("   ").run()
    start(app)
    assert "service" not in app.session_state
    assert any("分析目标" in t.value for t in app.warning)
    assert "inputs" in app.session_state


def test_blank_answer_explains_next_action_without_consuming_a_round(app):  # noqa: F811
    load_pack(app)
    start(app)
    before = app.session_state["session"].model_copy(deep=True)
    app.text_area(key="answer_message").set_value("   ").run()
    app.button(key="answer").click().run()
    assert app.session_state["session"] == before
    assert any("按未知继续" in t.value for t in app.warning)
    assert not app.exception


def test_unknown_is_one_explicit_action_then_generation_and_downloads(app):  # noqa: F811
    load_pack(app)
    start(app)
    app.button(key="continue_unknown").click().run()
    assert app.session_state["session"].phase == "READY"
    assert any("生成候选报告" in t.value for t in app.info)
    assert not app.checkbox and not app.download_button
    app.button(key="analyze").click().run()
    session = app.session_state["session"]
    assert session.phase == "COMPLETE"
    assert session.report.usage["request_count"] == 2
    assert len(app.download_button) == 3
    assert any("下载" in t.value for t in app.success)
    app.run()
    app.download_button[0].click().run()
    assert app.session_state["session"] == session


def test_connection_error_offers_explicit_downgrade_without_silent_retry(app, monkeypatch):  # noqa: F811
    from fmea_agent.adapters.llm.demo_mock import MockSourceKnowledgeRepository
    from fmea_agent.domain.demo_knowledge import RetrievalResult

    searches = []

    def unavailable(self, query):
        searches.append(query)
        return RetrievalResult(status="ERROR", terms=query.terms, error_code="CONNECTION_FAILED")

    monkeypatch.setattr(MockSourceKnowledgeRepository, "search", unavailable)
    load_pack(app)
    start(app)
    app.button(key="continue_unknown").click().run()
    app.button(key="analyze").click().run()
    before = app.session_state["session"].model_copy(deep=True)
    assert before.phase == "READY" and before.retrieval.status == "ERROR"
    assert "确认降级" in app.button(key="analyze").label
    assert not app.download_button
    app.run()
    assert app.session_state["session"] == before and len(searches) == 1
    app.button(key="analyze").click().run()
    assert app.session_state["session"].report.retrieval.status == "ERROR"
    assert len(searches) == 1


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (b"part vehicle;", "组件/功能"),
        ((PACK / "system.sysml").read_bytes() + b" " * 30_001, "30,000"),
    ],
)
def test_rejected_real_inputs_offer_recovery_before_model_calls(app, raw, expected):  # noqa: F811
    app.file_uploader(key="sysml_upload").upload("case.sysml", raw).run()
    app.button(key="load_inputs").click().run()
    assert app.error and "service" not in app.session_state
    assert any(expected in t.value for t in app.error)
    assert any("重新载入" in t.value for t in app.info)
    assert not app.download_button


def test_unexpected_start_failure_blocks_replay_and_keeps_reset_available(app, monkeypatch):  # noqa: F811
    from fmea_agent.application.demo_service import DemoService

    calls = []

    def fail(*args):
        calls.append(True)
        raise RuntimeError("private diagnostic must not appear")

    monkeypatch.setattr(DemoService, "start", fail)
    load_pack(app)
    start(app)
    app.run()
    assert len(calls) == 1
    assert not any(b.key == "start" for b in app.button)
    assert app.button(key="reset")
    assert all("private diagnostic" not in t.value for t in app.error)
    app.button(key="reset").click().run()
    assert "service" not in app.session_state and "inputs" not in app.session_state
    assert not app.exception
