"""Run with Streamlit; import has no UI, model or database side effects."""

import hashlib
from html import escape
from pathlib import Path
from typing import Literal
from uuid import uuid4

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from fmea_agent.adapters.documents.demo_inputs import DemoInputError
from fmea_agent.adapters.reports.demo_report import export_diagnostics, export_report
from fmea_agent.agents.demo_state import DemoSession
from fmea_agent.application.demo_settings import (
    DemoSettings,
    create_demo_service,
    load_demo_settings,
)
from fmea_agent.application.demo_uploads import UploadedInput, UploadError, load_uploaded_inputs

PACK = Path(__file__).resolve().parents[3] / "examples" / "demo_v1"


def _invalidate() -> None:
    service = st.session_state.pop("service", None)
    if service is not None:
        try:
            service.close()
        except Exception:
            pass  # Never expose a driver shutdown exception on file replacement.
    for key in ("inputs", "session", "downloads", "action_error"):
        st.session_state.pop(key, None)


def _upload(file: UploadedFile | None) -> UploadedInput | None:
    return UploadedInput(file.name, file.getvalue()) if file is not None else None


def _save_result(session: DemoSession) -> None:
    st.session_state["session"] = session
    downloads: dict[str, bytes] = {}
    if session.report is not None:
        candidate_formats: tuple[Literal["json", "html", "csv"], ...] = ("json", "html", "csv")
        downloads = {fmt: export_report(session.report, fmt) for fmt in candidate_formats}
    elif session.diagnostic is not None:
        diagnostic_formats: tuple[Literal["json", "html"], ...] = ("json", "html")
        downloads = {fmt: export_diagnostics(session.diagnostic, fmt) for fmt in diagnostic_formats}
    st.session_state["downloads"] = downloads


def _dialogue(settings: DemoSettings) -> None:
    inputs = st.session_state.get("inputs")
    if inputs is None:
        st.info("请先载入 SysML 资料。")
        return
    st.text("输入摘要：" + inputs.input_digest)
    with st.expander("系统结构、文件版本与来源"):
        st.json(inputs.model_dump(mode="json"))
    if inputs.missing_files:
        st.text("缺少可选资料：" + "、".join(inputs.missing_files))
    session: DemoSession | None = st.session_state.get("session")
    if session is None:
        targets = [
            (c.id, f.id, f"{c.name} / {f.name}")
            for c in inputs.model.components
            for f in inputs.model.functions
            if c.id in f.allocated_to
        ]
        with st.form("start_form"):
            target = st.selectbox(
                "分析对象 / 功能", targets, format_func=lambda x: x[2], key="target"
            )
            message = st.text_area(
                "分析目标与工作状况",
                value="请分析此对象。运行环境、工作循环、负载未知。",
                max_chars=10000,
                key="start_message",
            )
            submitted = st.form_submit_button(
                "提交分析目标", key="start", disabled=bool(settings.missing)
            )
        if submitted:
            service = create_demo_service(settings)
            st.session_state["service"] = service
            text = f"选择组件 ID：{target[0]}；功能 ID：{target[1]}。\n{message}"
            with st.spinner("解析目标与补问…"):
                _save_result(service.start(inputs, text, uuid4().hex))
            st.rerun()
        return
    st.text(f"会话：{session.id} · 状态：{session.phase} · 补问轮次：{session.question_rounds}/2")
    service = st.session_state["service"]
    if session.intake:
        st.text(f"当前目标：{session.intake.component_id} / {session.intake.function_id}")
        st.json({key: value.model_dump() for key, value in session.intake.context.items()})
        for question in session.intake.questions:
            st.text(question)
    with st.expander("本次对话记录"):
        for ref in session.inputs.evidence:
            if ref.source_kind == "user":
                st.text(ref.text)
    if session.phase == "WAITING_INPUT":
        with st.form("answer_form"):
            message = st.text_area("补充信息（允许留空）", max_chars=10000, key="answer_message")
            unknown = st.checkbox("仍未知，明确按未知继续", key="continue_unknown")
            submit = st.form_submit_button("提交补充 / 未知继续", key="answer")
        if submit:
            with st.spinner("处理补充信息…"):
                _save_result(
                    service.answer(session, message, uuid4().hex, continue_unknown=unknown)
                )
            st.rerun()
    if session.phase == "READY":
        if session.retrieval is not None and session.retrieval.status == "ERROR":
            st.error("知识检索 ERROR：" + (session.retrieval.error_code or "RETRIEVAL_FAILED"))
            st.info("本次检索失败。只有明确选择后才按已知资料推理；不会自动重查。")
        with st.form("analyze_form"):
            allow = st.checkbox("检索失败时，明确仅按已知资料推理", key="allow_without_retrieval")
            submit = st.form_submit_button("生成候选报告", key="analyze")
        if submit:
            with st.spinner("检索并生成候选…"):
                _save_result(service.analyze(session, uuid4().hex, allow_without_retrieval=allow))
            st.rerun()
    if session.phase == "FAILED":
        st.error("分析失败 FAILED：" + "、".join(session.errors))
    if session.retrieval is not None:
        st.text("实际检索状态：" + session.retrieval.status)
        if session.retrieval.status == "NO_MATCH":
            st.info("本次有界查询无匹配；不表示整个知识库不存在适用知识。")
        elif session.retrieval.status == "HITS":
            st.info("相关知识，适用性待确认；图关联不代表原始 FMEA 行。")
    if st.button("新建分析会话（重新载入资料）", key="reset"):
        _invalidate()
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="FMEA Agent · Demo V1", layout="wide")
    st.title("FMEA Agent · 候选分析工作台")
    st.caption("Demo V1 / D6 · 单用户本机工程助手")
    st.warning("CANDIDATE / INFERENCE：所有生成结果待工程审核。风险 NOT_EVALUATED；优化 SKIPPED。")
    try:
        settings = load_demo_settings()
    except ValueError:
        st.error("CONFIG_INVALID：请检查 FMEA_DEMO_MODE（live / mock）。")
        return
    st.text(
        "模式："
        + settings.mode
        + (
            " · 模型与检索均为模拟（FAKE_NO_MATCH）"
            if settings.mode == "mock"
            else " · 真实 DeepSeek + 只读 Neo4j"
        )
    )
    if settings.missing:
        st.warning("缺少配置：" + "、".join(settings.missing))
    else:
        st.caption("配置已具备；连接状态以显式提交的结果为准，页面重绘不探测服务。")
    st.header("1 · 上传与载入")
    source = st.radio("资料来源", ["上传文件", "演示资料包"], horizontal=True, key="input_source")
    st.caption("一个 SysML 必需；设计说明与 BOM 可选。每文件 ≤5 MiB，总文本 ≤30,000 字符。")
    sysml = st.file_uploader("SysML 模型", type=["sysml"], max_upload_size=5, key="sysml_upload")
    design = st.file_uploader(
        "设计说明", type=["md", "txt", "pdf"], max_upload_size=5, key="design_upload"
    )
    bom = st.file_uploader("BOM", type=["csv", "xlsx"], max_upload_size=5, key="bom_upload")
    signature = (
        source,
        settings.mode,
        tuple(
            (file.name, hashlib.sha256(file.getvalue()).hexdigest()) if file is not None else None
            for file in (sysml, design, bom)
        ),
    )
    if st.session_state.get("source_signature") != signature:
        _invalidate()
        st.session_state["source_signature"] = signature
    if st.button("载入资料", key="load_inputs"):
        _invalidate()
        try:
            uploads: list[UploadedInput | None]
            if source == "演示资料包":
                uploads = [
                    UploadedInput(name, (PACK / name).read_bytes())
                    for name in ("system.sysml", "design.md", "bom.csv")
                ]
            else:
                uploads = [_upload(sysml), _upload(design), _upload(bom)]
            with st.spinner("本机解析资料…"):
                st.session_state["inputs"] = load_uploaded_inputs(*uploads)
        except (UploadError, DemoInputError) as error:
            # Only the known safe application diagnostics reach the page.
            st.session_state["action_error"] = str(error)
        except Exception:
            st.session_state["action_error"] = "INPUT_LOAD_FAILED：资料无法载入。"
    if st.session_state.get("action_error"):
        st.error(st.session_state["action_error"])
    st.header("2 · 摘要与补问")
    try:
        _dialogue(settings)
    except Exception:
        st.error("ACTION_FAILED：操作未完成，请新建会话；不会自动重放外部请求。")
    st.header("3 · 候选与证据")
    session = st.session_state.get("session")
    if session is not None and session.report is not None:
        report = session.report
        st.text("报告状态：CANDIDATE · 风险 NOT_EVALUATED · 优化 SKIPPED")
        preview = '<table style="width:100%;border-collapse:collapse"><thead><tr>'
        preview += "<th>失效模式（INFERENCE）</th><th>已有控制</th><th>建议措施</th>"
        preview += "</tr></thead><tbody>"
        for row in report.generation.rows:
            cells = [
                row.mode.value or "UNKNOWN",
                "；".join(v.value or "UNKNOWN" for v in row.existing_controls) or "UNKNOWN",
                "；".join(v.value or "UNKNOWN" for v in row.suggested_actions) or "UNKNOWN",
            ]
            preview += (
                "<tr>"
                + "".join(
                    '<td style="padding:.5rem;border:1px solid #ccc;overflow-wrap:anywhere">'
                    + escape(cell)
                    + "</td>"
                    for cell in cells
                )
                + "</tr>"
            )
        st.html(preview + "</tbody></table>")
        for title, data in (
            ("候选字段、三层影响、未知项与验证建议", report.generation.model_dump()),
            ("分析排除项", report.exclusions),
            ("检索原始审计与适用性", report.retrieval.model_dump()),
            ("原始证据（引用有效不代表支持结论）", [r.model_dump() for r in report.evidence]),
            ("模型调用统计", report.usage),
        ):
            with st.expander(title):
                st.json(data)
    else:
        st.info("尚无候选报告。失败时仅提供诊断，不能据此认定系统无失效。")
    st.header("4 · 报告下载")
    downloads = st.session_state.get("downloads", {})
    for fmt, content in downloads.items():
        diagnostic = session is not None and session.diagnostic is not None
        label = ("下载失败诊断 " if diagnostic else "下载候选报告 ") + fmt.upper()
        st.download_button(
            label,
            content,
            file_name=("diagnostic" if diagnostic else "candidate") + "." + fmt,
            mime={"json": "application/json", "html": "text/html", "csv": "text/csv"}[fmt],
            on_click="ignore",
            key="download_" + fmt,
        )


if __name__ == "__main__":
    main()
