"""D7 public SysML + live DeepSeek + explicit FAKE_NO_MATCH acceptance scenario."""

import hashlib
import json
import logging
import os
import runpy
from contextlib import closing, redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
from fmea_agent.adapters.llm.demo_mock import MockSourceKnowledgeRepository
from fmea_agent.adapters.reports.demo_report import export_report
from fmea_agent.application.demo_ports import DemoModelError
from fmea_agent.application.demo_service import DemoService
from fmea_agent.domain.demo_analysis import CandidateReport

ROOT = Path(__file__).resolve().parents[1]


def run_public_scenario(summary: dict[str, object], output: Path) -> None:
    summary.update(
        retrieval_mode="FAKE_NO_MATCH", graph_used=False, engineering_quality="NOT_ACCEPTED"
    )
    # Reuse D4's pinned allowlist and before/after parse hashes. No graph adapter is created.
    public = runpy.run_path(str(ROOT / "scripts/demo_model_smoke.py"))["_public_inputs"]
    inputs = public()
    with closing(DeepSeekLLMClient.from_env()) as client:
        try:
            service = DemoService(MockSourceKnowledgeRepository(), client)
            component = next(c for c in inputs.model.components if c.name == "motor")
            function = next(f for f in inputs.model.functions if f.name == "spin")
            message = f"请分析 {component.id} {function.id}。运行环境、工作循环、负载均未知。"
            first = service.start(inputs, message, "public-start")
            if first.phase != "WAITING_INPUT":
                raise DemoModelError("SMOKE_FAILED")
            calls = client.usage()["request_count"]
            if service.start(inputs, message, "public-start") != first:
                raise DemoModelError("SMOKE_FAILED")
            ready = service.answer(first, "", "public-unknown", continue_unknown=True)
            if ready.phase != "READY" or client.usage()["request_count"] != calls:
                raise DemoModelError("SMOKE_FAILED")
            result = service.analyze(ready, "public-analyze")
            if result.phase != "COMPLETE" or result.report is None:
                raise DemoModelError("SMOKE_FAILED")
            calls = client.usage()["request_count"]
            if service.analyze(ready, "public-analyze") != result:
                raise DemoModelError("SMOKE_FAILED")
            if client.usage()["request_count"] != calls:
                raise DemoModelError("SMOKE_FAILED")
            report = CandidateReport.model_validate_json(result.report.model_dump_json())
            if report.component_id != component.id or report.function_id != function.id:
                raise DemoModelError("SMOKE_FAILED")
            report.usage.update(retrieval_mode="FAKE_NO_MATCH", graph_used="false")
            # The report is now independent of the service and its temporary input context.
            del service, result, ready, first, inputs
            output.mkdir(parents=True, exist_ok=True)
            exports = {}
            formats: tuple[Literal["json", "html", "csv"], ...] = ("json", "html", "csv")
            for fmt in formats:
                data = export_report(report, fmt)
                (output / f"candidate.{fmt}").write_bytes(data)
                exports[fmt] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            summary.update(
                status="PASS",
                workflow="PASS",
                standalone_exports="PASS",
                candidate_count=len(report.generation.rows),
                exports=exports,
            )
        finally:
            summary["usage"] = client.usage()


def main() -> int:
    summary: dict[str, object] = {
        "evidence": "LOCAL",
        "checked_at": datetime.now(UTC).isoformat(),
        "status": "ERROR",
        "workflow": "NOT_RUN",
        "standalone_exports": "NOT_RUN",
        "sysml_mode": "REAL_FILE",
        "model_mode": "LIVE_DEEPSEEK",
        "retrieval_mode": "FAKE_NO_MATCH",
        "graph_used": False,
        "engineering_quality": "NOT_ACCEPTED",
    }
    previous_disable = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with open(os.devnull, "w") as sink, redirect_stdout(sink), redirect_stderr(sink):
            try:
                run_public_scenario(summary, ROOT / "outputs/d7-public-smoke")
            except DemoModelError as exc:
                safe_codes = runpy.run_path(str(ROOT / "scripts/demo_model_smoke.py"))["SAFE_CODES"]
                code = exc.code if exc.code in safe_codes else "SMOKE_FAILED"
                summary.update(
                    status="SKIPPED" if code == "CONFIG_MISSING" else "ERROR", reason=code
                )
            except Exception:
                summary.update(status="ERROR", reason="SMOKE_FAILED")
    finally:
        logging.disable(previous_disable)
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
