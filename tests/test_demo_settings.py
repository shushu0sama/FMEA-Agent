"""Configuration must not leak values or silently become a fake service."""

import pytest
from pydantic import SecretStr
from test_demo_contracts import report_data  # noqa: F401
from test_demo_service import inputs  # noqa: F401


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in (
        "FMEA_DEMO_MODE",
        "DEEPSEEK_API_KEY",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
    ):
        monkeypatch.delenv(key, raising=False)


def test_default_live_reports_missing_keys_and_refuses_mock_fallback():
    from fmea_agent.application.demo_settings import create_demo_service, load_demo_settings

    settings = load_demo_settings()
    assert settings.mode == "live"
    assert set(settings.missing) == {
        "DEEPSEEK_API_KEY",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
    }
    with pytest.raises(ValueError, match="CONFIG_MISSING"):
        create_demo_service(settings)


def test_secrets_and_invalid_mode_never_leak(monkeypatch):
    from fmea_agent.application.demo_settings import DemoSettings, load_demo_settings

    monkeypatch.setenv("DEEPSEEK_API_KEY", "synthetic-private-token")
    monkeypatch.setenv("NEO4J_PASSWORD", "synthetic-password")
    settings = load_demo_settings()
    assert isinstance(settings.api_key, SecretStr) and isinstance(
        settings.neo4j_password, SecretStr
    )
    assert "synthetic" not in repr(settings)
    assert "synthetic" not in settings.model_dump_json()
    monkeypatch.setenv("FMEA_DEMO_MODE", "synthetic-private-mode")
    with pytest.raises(ValueError) as error:
        load_demo_settings()
    assert "synthetic" not in str(error.value)
    with pytest.raises(ValueError) as error:
        DemoSettings(mode="synthetic-private-mode", api_key="synthetic-private-token")
    assert "synthetic" not in str(error.value)


def test_explicit_mock_services_use_fresh_budget_and_real_workflow(inputs, monkeypatch):  # noqa: F811
    from fmea_agent.application.demo_settings import create_demo_service, load_demo_settings

    monkeypatch.setenv("FMEA_DEMO_MODE", "mock")
    settings = load_demo_settings()
    first, second = create_demo_service(settings), create_demo_service(settings)
    try:
        session = first.start(inputs, "分析 motor spin", "start")
        assert session.phase == "WAITING_INPUT"
        ready = first.answer(session, "", "continue", continue_unknown=True)
        complete = first.analyze(ready, "analyze")
        assert complete.phase == "COMPLETE" and complete.report.usage["request_count"] == 2
        assert complete.report.usage["mode"] == "mock"
        assert complete.report.retrieval.status == "NO_MATCH"
        fresh = second.start(inputs, "分析 motor spin", "start")
        assert fresh.phase == "WAITING_INPUT" and fresh.id != session.id
    finally:
        first.close()
        second.close()


def test_live_assembly_is_lazy_and_closes_owned_resources(monkeypatch):
    from fmea_agent.application.demo_settings import DemoSettings, create_demo_service

    closed = []

    class Driver:
        def close(self):
            closed.append("driver")

    import neo4j

    monkeypatch.setattr(neo4j.GraphDatabase, "driver", lambda *a, **k: Driver())
    service = create_demo_service(
        DemoSettings(
            api_key=SecretStr("synthetic-key"),
            neo4j_uri="bolt://localhost:7687",
            neo4j_username="user",
            neo4j_password=SecretStr("synthetic-pass"),
        )
    )
    service.close()
    service.close()
    assert closed == ["driver"]


@pytest.mark.parametrize("component_id,function_id", [("c2", "f2"), ("c10", "f10")])
def test_mock_clarification_preserves_nonfirst_selected_target(
    inputs,  # noqa: F811
    component_id,
    function_id,
):
    from fmea_agent.application.demo_settings import DemoSettings, create_demo_service
    from fmea_agent.domain.system_model import Component, Function

    inputs.model.components.append(Component(id=component_id, name="second motor", parent_id="s1"))
    inputs.model.functions.append(
        Function(id=function_id, name="second spin", allocated_to=[component_id])
    )
    api = create_demo_service(DemoSettings(mode="mock"))
    try:
        session = api.start(
            inputs, f"选择组件 ID：{component_id}；功能 ID：{function_id}。", "start"
        )
        assert (session.intake.component_id, session.intake.function_id) == (
            component_id,
            function_id,
        )
        session = api.answer(session, "仍未知", "answer")
        assert (session.intake.component_id, session.intake.function_id) == (
            component_id,
            function_id,
        )
        session = api.answer(session, "", "unknown", continue_unknown=True)
        result = api.analyze(session, "analyze")
        assert (result.report.component_id, result.report.function_id) == (
            component_id,
            function_id,
        )
    finally:
        api.close()
