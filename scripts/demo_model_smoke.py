"""Local live smoke: fixed public teaching inputs only, safe summary only."""

import hashlib
import json
import logging
import os
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

from fmea_agent.adapters.documents.demo_inputs import load_inputs
from fmea_agent.adapters.llm.deepseek import MODEL, DeepSeekLLMClient
from fmea_agent.application._demo_json import json_object
from fmea_agent.application.demo_generation import generate_analysis
from fmea_agent.application.demo_intake import WORKING_CONDITIONS
from fmea_agent.application.demo_ports import DemoModelError
from fmea_agent.domain.demo_analysis import IntakeResult
from fmea_agent.domain.demo_evidence import FieldValue, LoadedInputs
from fmea_agent.domain.demo_knowledge import RetrievalResult

PACK = Path(__file__).resolve().parents[1] / "examples" / "demo_v1"
PUBLIC_HASHES = {
    "system.sysml": "fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5",
    "bom.csv": "0aafeebc9492bc80dc7cf968cdd5a6689cf11347fa6a1db9d0fd3f832e68421e",
    "design.md": "01d249081fa097e918dfc84ee852277f3e37ce6fc14772cb927dbe6d5c7f3784",
}
SAFE_CODES = {
    "CONFIG_MISSING",
    "CONFIG_INVALID",
    "DEPENDENCY_MISSING",
    "AUTH_FAILED",
    "TIMEOUT",
    "CONNECTION_FAILED",
    "REQUEST_FAILED",
    "RATE_LIMITED",
    "CALL_BUDGET_EXCEEDED",
    "INVALID_RESPONSE",
    "INVALID_GENERATION",
    "PUBLIC_INPUT_MISMATCH",
    "SMOKE_FAILED",
}


def _public_inputs() -> LoadedInputs:
    for name, digest in PUBLIC_HASHES.items():
        with (PACK / name).open("rb") as source:
            data = source.read(5 * 1024 * 1024 + 1)
        if hashlib.sha256(data).hexdigest() != digest:
            raise DemoModelError("PUBLIC_INPUT_MISMATCH") from None
    inputs = load_inputs(PACK / "system.sysml", PACK / "design.md", PACK / "bom.csv")
    if any(PUBLIC_HASHES.get(file.filename) != file.sha256 for file in inputs.files):
        raise DemoModelError("PUBLIC_INPUT_MISMATCH") from None
    return inputs


def _run(summary: dict[str, object]) -> None:
    with DeepSeekLLMClient.from_env() as client:
        try:
            inputs = _public_inputs()
            generic = json_object(
                client.generate('Return JSON exactly as this example: {"ok":true}')
            )
            if generic != {"ok": True} or type(generic["ok"]) is not bool:
                raise DemoModelError("INVALID_RESPONSE") from None
            summary["generic_json"] = "PASS"
            component = next(c for c in inputs.model.components if c.name == "motor")
            function = next(
                f
                for f in inputs.model.functions
                if f.name == "spin" and component.id in f.allocated_to
            )
            intake = IntakeResult(
                component_id=component.id,
                function_id=function.id,
                status="READY",
                context={
                    name: FieldValue(
                        value=None,
                        status="UNKNOWN",
                        limitations=["公开演示工况未知，本 smoke 明确选择继续参考性分析。"],
                    )
                    for name in WORKING_CONDITIONS
                },
            )
            # Intentionally no graph reference in this smoke; never read private graph records.
            retrieval = RetrievalResult(status="NO_MATCH", terms=[component.name, function.name])
            result = generate_analysis(client, inputs, intake, retrieval)
            summary.update(
                status="PASS",
                generation_schema="PASS",
                candidate_count=len(result.rows),
                graph_used=False,
                engineering_quality="NOT_ACCEPTED",
            )
        finally:
            summary["usage"] = client.usage()


def main() -> int:
    summary: dict[str, object] = {
        "evidence": "LOCAL",
        "checked_at": datetime.now(UTC).isoformat(),
        "model": MODEL,
        "status": "ERROR",
        "generic_json": "NOT_RUN",
        "generation_schema": "NOT_RUN",
    }
    previous_disable = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        # Standalone smoke owns stdout/stderr for this synchronous invocation.
        with open(os.devnull, "w") as sink, redirect_stdout(sink), redirect_stderr(sink):
            try:
                _run(summary)
            except DemoModelError as exc:
                code = exc.code if exc.code in SAFE_CODES else "SMOKE_FAILED"
                summary.update(
                    status="SKIPPED" if code == "CONFIG_MISSING" else "ERROR", reason=code
                )
            except Exception:
                summary.update(status="ERROR", reason="SMOKE_FAILED")
    finally:
        logging.disable(previous_disable)
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if summary["status"] in {"PASS", "SKIPPED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
