"""Public-data-only live smoke entry contract; routine tests never contact a provider."""

import io
import json
import logging
import runpy

import pytest
from test_demo_contracts import report_data  # noqa: F401

from fmea_agent.domain.demo_evidence import LoadedInputs


@pytest.mark.parametrize(
    "case,status",
    [
        ("ok", "PASS"),
        ("auth", "ERROR"),
        ("bad_json", "ERROR"),
        ("empty", "ERROR"),
        ("unexpected", "ERROR"),
    ],
)
def test_smoke_safe_output_and_two_stage_validation(monkeypatch, capsys, report_data, case, status):  # noqa: F811
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_ports import DemoModelError

    class Client:
        calls = 0
        closed = False

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.closed = True

        def generate(self, prompt):
            self.calls += 1
            if case == "auth":
                raise DemoModelError("AUTH_FAILED")
            if case == "unexpected":
                raise RuntimeError("PRIVATE_SECRET")
            if self.calls == 1:
                return "no json" if case == "bad_json" else '{"ok":true}'
            assert "motor" in prompt and "spin" in prompt
            assert "NO_MATCH" in prompt
            return '{"rows":[]}' if case == "empty" else json.dumps(report_data["generation"])

        def usage(self):
            return {"request_count": self.calls, "model": "deepseek-v4-pro"}

    client = Client()
    monkeypatch.setattr(DeepSeekLLMClient, "from_env", lambda: client)
    main = runpy.run_path("scripts/demo_model_smoke.py")["main"]
    monkeypatch.setitem(
        main.__globals__,
        "_public_inputs",
        lambda: LoadedInputs.model_validate(report_data["input_snapshot"]),
    )
    assert main() == (0 if status == "PASS" else 1)
    output = capsys.readouterr()
    summary = json.loads(output.out)
    assert summary["status"] == status
    assert "PRIVATE" not in output.out + output.err and client.closed
    if case == "ok":
        assert client.calls == 2 and summary["candidate_count"] == 1


def test_missing_key_does_not_load_inputs_or_call_network(monkeypatch, capsys):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    main = runpy.run_path("scripts/demo_model_smoke.py")["main"]
    monkeypatch.setitem(main.__globals__, "_public_inputs", lambda: pytest.fail("input load"))
    assert main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "SKIPPED" and result["reason"] == "CONFIG_MISSING"


def test_debug_child_loggers_are_suppressed_and_restored(monkeypatch, capsys):
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_ports import DemoModelError

    output = io.StringIO()
    logger = logging.getLogger("httpcore.connection")
    old_level, old_disabled, old_threshold = (
        logger.level,
        logger.disabled,
        logging.root.manager.disable,
    )
    handler = logging.StreamHandler(output)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.disabled = False

    def fail():
        logger.debug("PRIVATE_SECRET")
        raise DemoModelError("CONFIG_MISSING")

    monkeypatch.setattr(DeepSeekLLMClient, "from_env", fail)
    try:
        main = runpy.run_path("scripts/demo_model_smoke.py")["main"]
        assert main() == 0
        assert "PRIVATE" not in output.getvalue() + capsys.readouterr().out
        assert logging.root.manager.disable == old_threshold
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)
        logger.disabled = old_disabled


def test_public_input_pack_uses_real_parser_and_fixed_target():
    module = runpy.run_path("scripts/demo_model_smoke.py")
    inputs = module["_public_inputs"]()
    assert inputs.model.system.name == "hydraulicPump"
    assert {file.kind for file in inputs.files} == {"sysml", "document", "bom"}


def test_modified_pack_is_rejected_before_parser(tmp_path, monkeypatch):
    module = runpy.run_path("scripts/demo_model_smoke.py")
    load = module["_public_inputs"]
    monkeypatch.setitem(load.__globals__, "PACK", tmp_path)
    (tmp_path / "system.sysml").write_text("PRIVATE ENGINEERING RECORD")
    from fmea_agent.application.demo_ports import DemoModelError

    with pytest.raises(DemoModelError, match="PUBLIC_INPUT_MISMATCH"):
        load()
