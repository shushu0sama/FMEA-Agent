"""D7 integration boundaries; generated prose is never engineering gold."""

import csv
import io
import json
import runpy
from pathlib import Path

import pytest

from fmea_agent.adapters.documents.demo_inputs import load_inputs
from fmea_agent.adapters.llm.demo_mock import DemoMockLLMClient, MockSourceKnowledgeRepository
from fmea_agent.adapters.reports.demo_report import export_diagnostics, export_report
from fmea_agent.application.demo_ports import DemoModelError
from fmea_agent.application.demo_service import DemoService
from fmea_agent.domain.demo_analysis import CandidateReport
from fmea_agent.domain.demo_knowledge import RetrievalResult

PACK = Path(__file__).resolve().parents[1] / "examples/demo_v1"


@pytest.fixture(scope="module")
def public_inputs():
    return load_inputs(PACK / "system.sysml", PACK / "design.md", PACK / "bom.csv")


def ready_service(inputs, client=None, repo=None):
    client = client or DemoMockLLMClient()
    service = DemoService(repo or MockSourceKnowledgeRepository(), client)
    component = next(c for c in inputs.model.components if c.name == "motor")
    function = next(f for f in inputs.model.functions if f.name == "spin")
    session = service.start(inputs, f"分析 {component.id} {function.id}；工况未知", "start")
    assert session.phase == "WAITING_INPUT"
    session = service.answer(session, "", "unknown", continue_unknown=True)
    assert session.phase == "READY"
    return service, session, client


def test_real_sysml_mock_service_to_standalone_three_formats(public_inputs):
    service, ready, client = ready_service(public_inputs)
    session = service.analyze(ready, "analyze")
    assert session.phase == "COMPLETE"
    assert service.analyze(ready, "analyze") == session
    assert client.usage()["request_count"] == 2
    raw = export_report(session.report, "json")
    del service, session, ready
    report = CandidateReport.model_validate_json(raw)
    assert report.input_snapshot.model.system.name == "hydraulicPump"
    assert any("pumpSpin" in exclusion for exclusion in report.exclusions)
    assert report.retrieval.status == "NO_MATCH" and not report.retrieval.hits
    assert report.usage["retrieval_mode"] == "FAKE_NO_MATCH"
    assert (report.status, report.risk_status, report.optimization_status) == (
        "CANDIDATE",
        "NOT_EVALUATED",
        "SKIPPED",
    )
    assert report.generation.missing_information
    assert all(row.mode.status == "INFERENCE" for row in report.generation.rows)
    assert {ref.source_kind for ref in report.evidence} >= {"sysml", "document", "bom", "user"}
    assert report.input_snapshot.files == public_inputs.files
    assert export_report(report, "json") == raw
    html = export_report(report, "html").decode("utf-8")
    assert "NOT_EVALUATED" in html and "pumpSpin" in html and "<script" not in html
    rows = list(csv.DictReader(io.StringIO(export_report(report, "csv").decode("utf-8-sig"))))
    assert len(rows) == len(report.generation.rows)
    assert json.loads(rows[0]["input_snapshot"]) == report.input_snapshot.model_dump(mode="json")


@pytest.mark.parametrize("fault", ["empty_fact_source", "wrong_reference", "empty_output"])
def test_invalid_generation_is_diagnostic_only(public_inputs, fault):
    class InvalidClient(DemoMockLLMClient):
        def generate(self, prompt):
            result = json.loads(super().generate(prompt))
            if "rows" in result:
                if fault == "empty_fact_source":
                    result["rows"][0]["existing_controls"] = [
                        {"value": "unsupported control", "status": "FACT", "evidence_ids": []}
                    ]
                elif fault == "wrong_reference":
                    result["rows"][0]["mode"]["evidence_ids"] = ["nonexistent-source"]
                else:
                    result["rows"] = []
            return json.dumps(result)

    service, ready, client = ready_service(public_inputs, InvalidClient())
    failed = service.analyze(ready, "analyze")
    assert failed.phase == "FAILED" and failed.report is None and failed.generation is None
    assert failed.errors == ["INVALID_GENERATION"]
    assert service.analyze(ready, "analyze") == failed
    assert client.usage()["request_count"] == 2
    payload = json.loads(export_diagnostics(failed.diagnostic, "json"))
    assert payload["status"] == "FAILED" and "generation" not in payload
    assert "FAILED" in export_diagnostics(failed.diagnostic, "html").decode("utf-8")


@pytest.mark.parametrize("fault", ["CONNECTION_FAILED", "TIMEOUT", "unexpected"])
def test_connection_failure_requires_explicit_degradation_and_preserves_error(public_inputs, fault):
    class BrokenRepository:
        def search(self, query):
            if fault == "unexpected":
                raise RuntimeError("PRIVATE_CONNECTION_BODY")
            return RetrievalResult(status="ERROR", terms=query.terms, error_code=fault)

    service, ready, client = ready_service(public_inputs, repo=BrokenRepository())
    stopped = service.analyze(ready, "analyze")
    assert stopped.phase == "READY" and stopped.report is None
    assert client.usage()["request_count"] == 1
    completed = service.analyze(stopped, "explicit-degrade", allow_without_retrieval=True)
    report = completed.report
    assert report.retrieval.status == "ERROR" and report.retrieval == stopped.retrieval
    assert not report.retrieval.hits and report.generation.missing_information
    assert "PRIVATE_CONNECTION_BODY" not in export_report(report, "json").decode("utf-8")
    assert client.usage()["request_count"] == 2


def test_copied_and_renamed_input_identity_is_not_generalization(tmp_path, public_inputs):
    copied = tmp_path / "system.sysml"
    copied.write_bytes((PACK / "system.sysml").read_bytes())
    original = load_inputs(PACK / "system.sysml", None, None)
    moved = load_inputs(copied, None, None)
    renamed = tmp_path / "renamed.sysml"
    renamed.write_bytes(copied.read_bytes())
    changed = load_inputs(renamed, None, None)
    assert original.files[0].sha256 == moved.files[0].sha256 == changed.files[0].sha256
    assert original.input_digest == moved.input_digest
    assert changed.input_digest != moved.input_digest
    assert str(tmp_path) not in moved.model_dump_json()
    service, ready, _ = ready_service(moved)
    forged = ready.model_copy(deep=True)
    forged.inputs = changed
    forged.input_digest = changed.input_digest
    with pytest.raises(DemoModelError, match="NEW_SESSION_REQUIRED"):
        service.analyze(forged, "swapped")
    report = service.analyze(ready, "valid").report
    assert set(report.input_snapshot.missing_files) == {"design", "bom"}


def test_public_acceptance_smoke_runs_service_and_exports_without_graph(monkeypatch, tmp_path):
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository

    class Client(DemoMockLLMClient):
        closed = False

        def close(self):
            self.closed = True

    client = Client()
    monkeypatch.setattr(DeepSeekLLMClient, "from_env", lambda: client)
    monkeypatch.setattr(
        Neo4jSourceKnowledgeRepository, "from_env", lambda: pytest.fail("private graph accessed")
    )
    run = runpy.run_path("scripts/demo_acceptance_smoke.py")["run_public_scenario"]
    summary = {}
    run(summary, tmp_path)
    assert client.closed
    assert summary["status"] == "PASS" and summary["workflow"] == "PASS"
    assert summary["retrieval_mode"] == "FAKE_NO_MATCH" and summary["graph_used"] is False
    assert summary["engineering_quality"] == "NOT_ACCEPTED"
    assert set(summary["exports"]) == {"json", "html", "csv"}
    report = CandidateReport.model_validate_json((tmp_path / "candidate.json").read_bytes())
    assert report.usage["retrieval_mode"] == "FAKE_NO_MATCH"
    assert report.usage["model"] == "deterministic-demo-mock"
    for fmt in ("json", "html", "csv"):
        assert (tmp_path / f"candidate.{fmt}").read_bytes() == export_report(report, fmt)


@pytest.mark.parametrize("code", ["CONFIG_MISSING", "AUTH_FAILED", "PRIVATE_EXCEPTION"])
def test_acceptance_smoke_failure_is_nonpass_and_sanitized(monkeypatch, capsys, code):
    main = runpy.run_path("scripts/demo_acceptance_smoke.py")["main"]

    def fail(*_):
        print("PRIVATE_BODY")
        raise DemoModelError(code)

    monkeypatch.setitem(main.__globals__, "run_public_scenario", fail)
    assert main() == 1
    captured = capsys.readouterr()
    assert "PRIVATE" not in captured.out + captured.err
    summary = json.loads(captured.out)
    assert summary["status"] == ("SKIPPED" if code == "CONFIG_MISSING" else "ERROR")
    assert summary["workflow"] == "NOT_RUN" and summary["standalone_exports"] == "NOT_RUN"
