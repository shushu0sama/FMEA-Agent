"""AppTest exercises real upload/loading/service/export; only LLM/graph are explicit fakes."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src/fmea_agent/ui/demo_app.py"
PACK = ROOT / "examples/demo_v1"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("FMEA_DEMO_MODE", "mock")
    return AppTest.from_file(str(APP), default_timeout=30).run()


def load_pack(app):
    app.radio(key="input_source").set_value("演示资料包").run()
    return app.button(key="load_inputs").click().run()


def start(app):
    return app.button(key="start").click().run()


def test_missing_sysml_and_doc_only_upload_never_start(app):
    assert not app.exception
    app.file_uploader(key="design_upload").upload("设计.md", b"public").run()
    app.button(key="load_inputs").click().run()
    assert any("SysML" in e.value for e in app.error)
    assert "service" not in app.session_state
    assert not app.download_button


def test_two_rounds_unknown_reruns_and_downloads_do_not_repeat_calls(app):
    load_pack(app)
    assert app.session_state["inputs"].model.system.name == "hydraulicPump"
    start(app)
    assert app.session_state["session"].phase == "WAITING_INPUT"
    app.text_area(key="answer_message").set_value("仍未知").run()
    app.button(key="answer").click().run()
    assert app.session_state["session"].question_rounds == 2
    app.text_area(key="answer_message").set_value("").run()
    app.checkbox(key="continue_unknown").check().run()
    app.button(key="answer").click().run()
    assert app.session_state["session"].phase == "READY"
    app.button(key="analyze").click().run()
    session = app.session_state["session"]
    assert session.phase == "COMPLETE" and session.report.usage["request_count"] == 3
    assert any("有界查询" in e.value for e in app.info)
    assert len(app.download_button) == 3
    assert not app.dataframe  # Native dataframe CSV bypasses our safe, sourced exporter.
    app.run()
    app.download_button[0].click().run()
    assert app.session_state["session"] == session
    assert not app.exception


def test_upload_safe_names_and_change_invalidates_old_report(app):
    raw = (PACK / "system.sysml").read_bytes()
    app.file_uploader(key="sysml_upload").upload("../../原始.sysml", raw).run()
    app.button(key="load_inputs").click().run()
    inputs = app.session_state["inputs"]
    assert inputs.files[0].filename == "原始.sysml"
    assert inputs.files[0].sha256 == __import__("hashlib").sha256(raw).hexdigest()
    start(app)
    old_service = app.session_state["service"]
    app.file_uploader(key="sysml_upload").upload("不同.sysml", raw + b"\n").run()
    assert "session" not in app.session_state and "inputs" not in app.session_state
    assert "service" not in app.session_state and not app.download_button
    app.button(key="load_inputs").click().run()
    start(app)
    assert app.session_state["service"] is not old_service


def test_failure_only_diagnostic_downloads(app, monkeypatch):
    from fmea_agent.adapters.llm.demo_mock import DemoMockLLMClient

    monkeypatch.setattr(DemoMockLLMClient, "generate", lambda *a: "broken-json")
    load_pack(app)
    start(app)
    assert app.session_state["session"].phase == "FAILED"
    assert len(app.download_button) == 2
    assert all("CSV" not in button.label for button in app.download_button)
    assert app.error and not app.exception


def test_retrieval_failure_requires_explicit_action(app, monkeypatch):
    from fmea_agent.adapters.llm.demo_mock import MockSourceKnowledgeRepository
    from fmea_agent.domain.demo_knowledge import RetrievalResult

    monkeypatch.setattr(
        MockSourceKnowledgeRepository,
        "search",
        lambda self, q: RetrievalResult(
            status="ERROR", terms=q.terms, error_code="CONNECTION_FAILED"
        ),
    )
    load_pack(app)
    start(app)
    app.checkbox(key="continue_unknown").check().run()
    app.button(key="answer").click().run()
    app.button(key="analyze").click().run()
    assert app.session_state["session"].phase == "READY" and app.error
    app.run()
    assert not app.download_button
    app.checkbox(key="allow_without_retrieval").check().run()
    app.button(key="analyze").click().run()
    assert app.session_state["session"].report.retrieval.status == "ERROR"


def test_upload_limit_is_enforced_before_disk_or_parser(tmp_path, monkeypatch):
    from fmea_agent.application.demo_uploads import UploadedInput, load_uploaded_inputs

    with pytest.raises(ValueError, match="5 MiB"):
        load_uploaded_inputs(UploadedInput("huge.sysml", b"x" * (5 * 1024 * 1024 + 1)))
    with pytest.raises(ValueError, match="类型"):
        load_uploaded_inputs(UploadedInput("wrong.exe", b"x"))


def test_live_missing_configuration_visible_without_values(monkeypatch):
    monkeypatch.setenv("FMEA_DEMO_MODE", "live")
    for key in ("DEEPSEEK_API_KEY", "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"):
        monkeypatch.delenv(key, raising=False)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert any("DEEPSEEK_API_KEY" in e.value for e in app.warning)
    load_pack(app)
    assert app.button(key="start").disabled
    assert "service" not in app.session_state and not app.exception


def test_empty_answer_and_upload_removal_preserve_call_boundary(app):
    load_pack(app)
    start(app)
    before = app.session_state["session"]
    app.button(key="answer").click().run()
    after = app.session_state["session"]
    assert after.question_rounds == before.question_rounds
    assert len(after.inputs.evidence) == len(before.inputs.evidence)
    app.radio(key="input_source").set_value("上传文件").run()
    assert "session" not in app.session_state and not app.download_button


def test_input_parser_error_cannot_render_external_markup(app, monkeypatch):
    from fmea_agent.application import demo_uploads

    monkeypatch.setattr(
        demo_uploads,
        "load_inputs",
        lambda *a: (_ for _ in ()).throw(ValueError("![x](https://invalid/x)")),
    )
    load_pack(app)
    assert not app.exception
    assert all("https://invalid" not in e.value for e in app.error)
