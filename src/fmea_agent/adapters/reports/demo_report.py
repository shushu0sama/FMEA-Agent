"""Self-contained exports: all external text is data, never executable markup."""

import csv
import io
import json
from html import escape
from typing import Literal

from fmea_agent.domain.demo_analysis import CandidateReport, DiagnosticReport, FailureRow
from fmea_agent.domain.demo_evidence import FieldValue


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _field(value: FieldValue) -> str:
    return (
        f"{value.value if value.value is not None else 'UNKNOWN'} [{value.status}]"
        + "\n证据："
        + ", ".join(value.evidence_ids)
        + "\n限制："
        + "；".join(value.limitations)
    )


def _values(values: list[FieldValue]) -> str:
    return "\n".join(value.value if value.value is not None else "UNKNOWN" for value in values)


def _safe_cell(value: str) -> str:
    # Quoting CSV is insufficient. Preserve the original in structured provenance.
    stripped = value.lstrip("\ufeff \t\r\n\v\f")
    if stripped.startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


def _section(title: str, data: object) -> str:
    return f"<section><h2>{escape(title)}</h2><pre>{escape(_json(data))}</pre></section>"


def _page(title: str, body: str) -> bytes:
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(title)}</title><style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;color:#172b3a}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd4da;"
        "padding:.5rem;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:1rem}"
        "section{margin:2rem 0}@media print{body{margin:0}pre{background:white}}"
        f"</style></head><body><h1>{escape(title)}</h1>{body}</body></html>"
    ).encode()


def _row_cells(row: FailureRow) -> list[str]:
    return [
        _field(row.mode),
        "\n\n".join(map(_field, row.causes)) or "UNKNOWN",
        _field(row.mechanism),
        _field(row.effects["LOCAL"]),
        _field(row.effects["NEXT_HIGHER_LEVEL"]),
        _field(row.effects["END_EFFECT"]),
        "\n\n".join(map(_field, row.existing_controls)) or "UNKNOWN",
        "\n\n".join(map(_field, row.suggested_actions)) or "UNKNOWN",
        "\n".join(row.validation_suggestions),
    ]


def export_report(report: CandidateReport, format: Literal["json", "html", "csv"]) -> bytes:
    if not isinstance(report, CandidateReport):
        raise ValueError("candidate report required")
    # Dump first: validating an existing mutable Pydantic instance can skip nested validation.
    report = CandidateReport.model_validate(report.model_dump(mode="json"))
    data = report.model_dump(mode="json")
    if format == "json":
        return _json(data).encode("utf-8")
    if format == "html":
        headings = [
            "失效模式",
            "失效起因",
            "失效机理",
            "局部影响 LOCAL",
            "上一级影响 NEXT_HIGHER_LEVEL",
            "最终影响 END_EFFECT",
            "既有控制",
            "建议措施",
            "建议验证方法",
        ]
        body = "<p>CANDIDATE：参考性候选，生成字段为 INFERENCE，待工程审核。"
        body += "风险 NOT_EVALUATED；优化 SKIPPED；不生成 S/O/D/AP，不代表批准或措施实施。</p>"
        body += _section(
            "分析对象、工况与范围",
            {
                k: data[k]
                for k in (
                    "schema_version",
                    "run_id",
                    "input_digest",
                    "component_id",
                    "function_id",
                    "context",
                    "exclusions",
                )
            },
        )
        body += "<section><h2>候选失效表</h2><table><thead><tr>"
        body += "".join(f"<th>{escape(x)}</th>" for x in headings) + "</tr></thead><tbody>"
        for row in report.generation.rows:
            body += "<tr>" + "".join(f"<td>{escape(x)}</td>" for x in _row_cells(row)) + "</tr>"
        body += "</tbody></table></section>"
        if not report.generation.rows:
            body += "<p>未生成候选；不代表系统无失效。</p>"
        body += _section("输入清单、系统结构、资料关联、冲突与缺失", data["input_snapshot"])
        body += _section("检索审计与适用性（词法命中不等于当前对象适用）", data["retrieval"])
        body += _section("完整字段来源、假设与未知项", data["generation"])
        body += _section("原始引用详情与来源链", data["evidence"])
        body += _section("调用审计", data["usage"])
        return _page("候选 FMEA 报告 · CANDIDATE", body)
    if format != "csv":
        raise ValueError("unsupported candidate export format")
    stream = io.StringIO(newline="")
    columns = [
        "mode",
        "cause",
        "mechanism",
        "effect",
        "existing_controls",
        "actions",
        "status",
        "evidence_ids",
        "limitations",
        "validation_suggestions",
        "field_provenance",
        "run_id",
        "input_digest",
        "context",
        "exclusions",
        "risk_status",
        "optimization_status",
        "assumptions",
        "missing_information",
        "input_snapshot",
        "evidence_registry",
        "retrieval",
        "usage",
    ]
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for row in report.generation.rows:
        values = {
            "mode": row.mode.value or "UNKNOWN",
            "cause": _values(row.causes),
            "mechanism": row.mechanism.value or "UNKNOWN",
            "effect": "\n".join(f"{k}: {_field(v)}" for k, v in row.effects.items()),
            "existing_controls": _values(row.existing_controls),
            "actions": _values(row.suggested_actions),
            "status": report.status,
            "evidence_ids": "\n".join(
                dict.fromkeys(ref for value in row.fields() for ref in value.evidence_ids)
            ),
            "limitations": "\n".join(x for value in row.fields() for x in value.limitations),
            "validation_suggestions": "\n".join(row.validation_suggestions),
            "field_provenance": _json(row.model_dump(mode="json")),
            "evidence_registry": _json(data["evidence"]),
            "assumptions": _json(report.generation.assumptions),
            "missing_information": _json(report.generation.missing_information),
        }
        for key in columns:
            if key not in values:
                values[key] = data[key] if isinstance(data[key], str) else _json(data[key])
        writer.writerow({k: _safe_cell(v) for k, v in values.items()})
    return stream.getvalue().encode("utf-8-sig")


def export_diagnostics(report: DiagnosticReport, format: Literal["json", "html"]) -> bytes:
    if not isinstance(report, DiagnosticReport):
        raise ValueError("diagnostic report required")
    report = DiagnosticReport.model_validate(report.model_dump(mode="json"))
    data = report.model_dump(mode="json")
    if format == "json":
        return _json(data).encode("utf-8")
    if format == "html":
        return _page("失败诊断 · FAILED", _section("诊断、输入快照与调用审计", data))
    raise ValueError("unsupported diagnostic export format")
