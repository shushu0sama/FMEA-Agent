"""D6 portable exports, untrusted text and provenance boundaries."""

import csv
import io
import json

import pytest
from test_demo_contracts import field, report_data  # noqa: F401

from fmea_agent.domain.demo_analysis import CandidateReport, DiagnosticReport


def test_detached_exports_preserve_snapshot_and_field_provenance(report_data):  # noqa: F811
    from fmea_agent.adapters.reports.demo_report import export_report

    row = report_data["generation"]["rows"][0]
    row["causes"] = [field("原因一", "INFERENCE", ["ev-spin"]), field("原因二", "INFERENCE")]
    row["existing_controls"] = [field("spin", "FACT", ["ev-spin"])]
    row["suggested_actions"] = [field("建议验证", "INFERENCE", ["ev-spin"])]
    row["mode"]["limitations"] = ["未经工程审核"]
    report_data["generation"]["missing_information"] = ["负载未知"]
    original = CandidateReport.model_validate(report_data)
    encoded = export_report(original, "json")
    restored = CandidateReport.model_validate_json(encoded)
    assert restored == original
    del original, report_data
    html = export_report(restored, "html").decode("utf-8")
    for expected in [
        "model.sysml",
        "a" * 64,
        "opensysml",
        "0.4.0",
        "v0.4.3",
        "allocated_to",
        "spin",
        "derived_from",
        "ev-spin",
        "负载未知",
        "既有控制",
        "建议措施",
        "NOT_EVALUATED",
        "SKIPPED",
    ]:
        assert expected in html
    raw = export_report(restored, "csv")
    assert raw.startswith(b"\xef\xbb\xbf")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert len(rows) == 1
    assert "原因一\n原因二" == rows[0]["cause"]
    assert rows[0]["existing_controls"] == "spin"
    assert rows[0]["actions"] == "建议验证"
    provenance = json.loads(rows[0]["field_provenance"])
    assert provenance["mode"]["evidence_ids"] == ["ev-spin"]
    assert provenance["mode"]["limitations"] == ["未经工程审核"]
    assert all(
        provenance["effects"][x]["status"] == "UNKNOWN"
        for x in ["LOCAL", "NEXT_HIGHER_LEVEL", "END_EFFECT"]
    )
    assert json.loads(rows[0]["input_snapshot"])["files"][0]["sha256"] == "a" * 64
    assert json.loads(rows[0]["evidence_registry"])[0]["text"] == "spin"


@pytest.mark.parametrize("prefix", ["=", "+", "-", "@", "\t=", "\r+", "\n-", "  @", "\ufeff="])
def test_csv_neutralizes_formula_prefixes(report_data, prefix):  # noqa: F811
    from fmea_agent.adapters.reports.demo_report import export_report

    report_data["generation"]["rows"][0]["mode"]["value"] = prefix + "危险中文"
    raw = export_report(CandidateReport.model_validate(report_data), "csv")
    row = next(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert row["mode"] == "'" + prefix + "危险中文"


def test_html_never_activates_untrusted_markup(report_data):  # noqa: F811
    from fmea_agent.adapters.reports.demo_report import export_report

    payload = '<script>alert("x")</script><img src="https://invalid/x">&'
    report_data["generation"]["rows"][0]["mode"]["value"] = payload
    html = export_report(CandidateReport.model_validate(report_data), "html").decode()
    assert "<script" not in html and "<img" not in html
    assert "&lt;script&gt;" in html and "&amp;" in html


def test_diagnostic_roundtrip_has_no_candidate_table_or_csv(report_data):  # noqa: F811
    from fmea_agent.adapters.reports.demo_report import export_diagnostics, export_report

    failed = DiagnosticReport(
        schema_version="demo-v1-diagnostic",
        run_id="failure",
        status="FAILED",
        input_snapshot=report_data["input_snapshot"],
        errors=["INVALID_GENERATION"],
    )
    restored = DiagnosticReport.model_validate_json(export_diagnostics(failed, "json"))
    html = export_diagnostics(restored, "html").decode()
    assert "FAILED" in html and "失败诊断" in html and "model.sysml" in html
    assert "候选失效表" not in html and "CANDIDATE" not in html
    with pytest.raises(ValueError):
        export_diagnostics(restored, "csv")
    with pytest.raises(ValueError):
        export_report(restored, "csv")


def test_export_revalidates_mutated_report(report_data):  # noqa: F811
    from fmea_agent.adapters.reports.demo_report import export_report

    report = CandidateReport.model_validate(report_data)
    report.generation.rows[0].mode.evidence_ids = ["invented"]
    with pytest.raises(ValueError):
        export_report(report, "html")
