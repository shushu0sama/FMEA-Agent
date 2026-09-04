"""Task 8 — Smoke tests: run the CLI demo through a subprocess.

The whole run is offline: fixture loading, in-memory repositories and the
NoOpRiskStrategy require no external service, so a successful run proves the
no-external-dependency requirement by construction.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "examples" / "simple_pump.json"
LIBRARY = ROOT / "examples" / "demo_failure_library.json"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "fmea_agent", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


def test_demo_cli_exits_zero_and_prints_valid_json() -> None:
    result = _run_cli("demo", str(FIXTURE))
    assert result.returncode == 0, result.stderr
    output: dict[str, Any] = json.loads(result.stdout)
    assert output["method"] == "AIAG_VDA"
    assert output["item"] == "Hydraulic Pump"
    assert output["function"] == "Provide Hydraulic Pressure"


def test_demo_output_contains_candidate_failure_mode() -> None:
    result = _run_cli("demo", str(FIXTURE))
    assert result.returncode == 0, result.stderr
    output: dict[str, Any] = json.loads(result.stdout)
    failure_modes = output["failure_modes"]
    assert len(failure_modes) == 1
    mode = failure_modes[0]
    assert mode["value"] == "Loss of hydraulic pressure"
    assert mode["status"] == "CANDIDATE"
    assert mode["causes"][0]["value"] == "Demo mechanical failure"
    assert mode["effects"][0] == {
        "level": "LOCAL",
        "value": "Required outlet pressure is unavailable",
    }


def test_demo_risk_not_evaluated_and_optimization_skipped() -> None:
    result = _run_cli("demo", str(FIXTURE))
    assert result.returncode == 0, result.stderr
    output: dict[str, Any] = json.loads(result.stdout)
    assert output["risk"]["status"] == "NOT_EVALUATED"
    assert output["stage_status"]["optimization"] == "SKIPPED"


def test_demo_evidence_points_to_fixture_library() -> None:
    result = _run_cli("demo", str(FIXTURE))
    assert result.returncode == 0, result.stderr
    output: dict[str, Any] = json.loads(result.stdout)
    assert output["failure_modes"][0]["evidence"] == [
        {"source": "demo-failure-library:001"}
    ]


def test_demo_output_flag_writes_file(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    result = _run_cli("demo", str(FIXTURE), "--output", str(target))
    assert result.returncode == 0, result.stderr
    written: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
    assert written["method"] == "AIAG_VDA"
    assert "output written to" in result.stderr


def test_demo_explicit_failure_library_argument() -> None:
    result = _run_cli("demo", str(FIXTURE), "--failure-library", str(LIBRARY))
    assert result.returncode == 0, result.stderr
    output: dict[str, Any] = json.loads(result.stdout)
    assert output["failure_modes"][0]["evidence"] == [
        {"source": "demo-failure-library:001"}
    ]


def test_demo_missing_fixture_exits_nonzero() -> None:
    result = _run_cli("demo", str(ROOT / "does_not_exist.json"))
    assert result.returncode != 0
    assert "error:" in result.stderr


def test_demo_invalid_fixture_json_exits_nonzero(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = _run_cli("demo", str(bad))
    assert result.returncode != 0
    assert "error:" in result.stderr


def test_demo_missing_analysis_request_exits_nonzero(tmp_path: Path) -> None:
    bad = tmp_path / "no_request.json"
    bad.write_text(
        '{"system": {"id": "s", "name": "S"}, "components": [], "functions": []}',
        encoding="utf-8",
    )
    result = _run_cli("demo", str(bad), "--failure-library", str(LIBRARY))
    assert result.returncode != 0
    assert "error:" in result.stderr


def test_cli_without_command_exits_nonzero() -> None:
    result = _run_cli()
    assert result.returncode != 0
