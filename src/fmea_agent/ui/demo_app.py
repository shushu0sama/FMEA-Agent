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
    for key in ("inputs", "session", "downloads", "action_error", "operation_failed"):
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
    targets = [
        (c.id, f.id, f"{c.name} / {f.name}")
        for c in inputs.model.components
        for f in inputs.model.functions
        if c.id in f.allocated_to
    ]
    st.text(
        f"已识别系统：{inputs.model.system.name} · {len(inputs.model.components)} 个组件 · "
        f"{len(inputs.model.functions)} 个功能 · {len(targets)} 个可分析对象"
    )
    with st.expander("系统结构、文件版本与来源"):
        st.json(inputs.model_dump(mode="json"))
    if inputs.missing_files:
        names = {"design": "设计说明", "bom": "BOM"}
        st.text("未提供可选资料：" + "、".join(names[k] for k in inputs.missing_files))
        st.caption("可按模型已知事实继续；缺少的资料不会被当作已有事实。")
    session: DemoSession | None = st.session_state.get("session")
    if session is None:
        st.info("下一步：选择组件和功能，说明希望分析的问题，再提交分析目标。")
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
                "提交分析目标", key="start", disabled=bool(settings.missing), type="primary"
            )
        if submitted:
            if not message.strip():
                st.warning("请填写分析目标；工况不清楚时可以写“未知”。本次未调用模型。")
                return
            service = create_demo_service(settings)
            st.session_state["service"] = service
            text = f"选择组件 ID：{target[0]}；功能 ID：{target[1]}。\n{message}"
            with st.spinner("解析目标与补问…"):
                _save_result(service.start(inputs, text, uuid4().hex))
            st.rerun()
        return
    service = st.session_state["service"]
    if session.intake:
        target_name = next(
            (name for c, f, name in targets
             if (c, f) == (session.intake.component_id, session.intake.function_id)),
            f"{session.intake.component_id} / {session.intake.function_id}",
        )
        st.text("当前分析对象：" + target_name)
        context_names = {"environment": "运行环境", "operating_phase": "运行阶段", "load": "负载"}
        for key, value in session.intake.context.items():
            st.text(f"{context_names.get(key, key)}：{value.value or '未知'}（{value.status}）")
        if session.phase == "WAITING_INPUT":
            for question in session.intake.questions:
                st.text(question)
    with st.expander("本次对话记录"):
        st.text(
            f"会话：{session.id} · 状态：{session.phase} · 补问轮次：{session.question_rounds}/2"
        )
        for ref in session.inputs.evidence:
            if ref.source_kind == "user":
                st.text(ref.text)
    if session.phase == "WAITING_INPUT":
        st.info("下一步：补充上述信息；无法确认时直接点击“按未知继续”。回答后才能生成报告。")
        with st.form("answer_form"):
            message = st.text_area("补充信息", max_chars=10000, key="answer_message")
            submit = st.form_submit_button("提交补充", key="answer", type="primary")
            unknown = st.form_submit_button("按未知继续", key="continue_unknown")
            st.caption("按未知继续会提交已填写内容，并将仍缺少的信息保留为 UNKNOWN。")
        if submit or unknown:
            if not message.strip() and not unknown:
                st.warning("请填写补充信息，或点击“按未知继续”。本次未调用模型，也未消耗补问轮次。")
                return
            with st.spinner("处理补充信息…"):
                _save_result(
                    service.answer(session, message, uuid4().hex, continue_unknown=unknown)
                )
            st.rerun()
    if session.phase == "READY":
        retrieval_failed = session.retrieval is not None and session.retrieval.status == "ERROR"
        if retrieval_failed:
            assert session.retrieval is not None
            st.error("知识检索 ERROR：" + (session.retrieval.error_code or "RETRIEVAL_FAILED"))
            st.info(
                "下一步：可点击“确认降级并生成候选报告”，仅按已知资料进行参考推断；"
                "也可新建会话。当前尚未生成报告，不会自动重查，原故障会保留在报告中。"
            )
        else:
            st.info("下一步：点击“生成候选报告”。系统将检索相关知识并生成待审核候选。")
        with st.form("downgrade_form" if retrieval_failed else "analyze_form"):
            submit = st.form_submit_button(
                "确认降级并生成候选报告" if retrieval_failed else "生成候选报告",
                key="confirm_downgrade" if retrieval_failed else "analyze", type="primary",
            )
        if submit:
            with st.spinner("正在生成参考候选…" if retrieval_failed else "正在检索知识并生成候选…"):
                _save_result(service.analyze(
                    session, uuid4().hex, allow_without_retrieval=retrieval_failed,
                ))
            st.rerun()
    if session.phase == "FAILED":
        st.error("分析失败 FAILED：" + "、".join(session.errors))
        st.info("下一步：下载下方失败诊断以便排查，或新建会话。失败不表示系统没有失效。")
    elif session.phase == "COMPLETE":
        st.success("候选报告已生成。下一步：查看下方候选与依据，并下载报告；工程质量仍需人工审核。")
    if session.retrieval is not None:
        st.text("实际检索状态：" + session.retrieval.status)
        if session.retrieval.status == "NO_MATCH":
            st.info("本次有界查询无匹配，候选属于参考推断；不表示整个知识库不存在适用知识。")
        elif session.retrieval.status == "HITS":
            st.info("相关知识，适用性待确认；图关联不代表原始 FMEA 行。")


def main() -> None:
    st.set_page_config(page_title="FMEA Agent · Demo V1", layout="wide")
    st.title("FMEA Agent · 候选分析工作台")
    st.caption("Demo V1 · 单用户本机工程助手")
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
        st.info("可以先在本机载入并检查资料；提交分析前需通过启动命令注入已有配置。")
    else:
        st.caption("配置已具备；连接状态以显式提交的结果为准，页面重绘不探测服务。")
    st.caption("使用流程：载入资料 → 确认目标与补充信息 → 生成候选 → 查看与下载")
    st.header("1 · 上传与载入")
    source = st.radio("资料来源", ["上传文件", "演示资料包"], horizontal=True, key="input_source")
    st.caption("一个 SysML 必需；设计说明与 BOM 可选。每文件 ≤5 MiB，总文本 ≤30,000 字符。")
    sysml = design = bom = None
    if source == "上传文件":
        st.caption(
            "支持一个自包含的 SysML 单文件子集，需有可分析的组件/功能对；"
            "不支持用户文件 imports。"
        )
        sysml = st.file_uploader(
            "SysML 模型", type=["sysml"], max_upload_size=5, key="sysml_upload"
        )
        design = st.file_uploader(
            "设计说明（可选）", type=["md", "txt", "pdf"], max_upload_size=5, key="design_upload"
        )
        bom = st.file_uploader(
            "BOM（可选）", type=["csv", "xlsx"], max_upload_size=5, key="bom_upload"
        )
    else:
        st.caption("公开教学资料包：一个 SysML 模型、设计说明和 BOM。")
    signature = (
        source,
        settings.mode,
        tuple(
            (file.name, hashlib.sha256(file.getvalue()).hexdigest()) if file is not None else None
            for file in (sysml, design, bom)
        ),
    )
    if st.session_state.get("source_signature") != signature:
        had_inputs = "inputs" in st.session_state
        _invalidate()
        st.session_state["source_signature"] = signature
        if had_inputs:
            st.info("资料已更改，旧会话和下载已撤销。下一步：重新载入资料。")
    if st.button(
        "载入资料", key="load_inputs",
        type="primary" if "inputs" not in st.session_state else "secondary",
    ):
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
        except DemoInputError as error:
            # Only the known safe application diagnostics reach the page.
            st.session_state["action_error"] = f"{error.code}：{error}"
        except UploadError as error:
            st.session_state["action_error"] = str(error)
        except Exception:
            st.session_state["action_error"] = "INPUT_LOAD_FAILED：资料无法载入。"
    if st.session_state.get("action_error"):
        st.error(st.session_state["action_error"])
        st.info(
            "下一步：按错误提示检查或更换文件，再重新载入；也可选择演示资料包验证流程。"
            "模型需有单一可用系统根及组件/功能对，多文件 imports 暂不支持；"
            "超限时请选取完整的小模型，程序不会静默截断。"
        )
    if "inputs" not in st.session_state:
        if not st.session_state.get("action_error"):
            st.info("下一步：提供 SysML 文件或选择演示资料包，然后点击“载入资料”。")
        return
    st.header("2 · 摘要与补问")
    if not st.session_state.get("operation_failed"):
        try:
            _dialogue(settings)
        except Exception:
            st.session_state["operation_failed"] = True
            st.rerun()
    if st.session_state.get("operation_failed"):
        st.error("ACTION_FAILED：操作未完成，当前会话已停止提交；不会自动重放外部请求。")
        st.info("下一步：点击“新建分析会话”后重新载入资料。当前没有可交付的新报告。")
    if st.button("新建分析会话（重新载入资料）", key="reset"):
        _invalidate()
        st.rerun()
    if st.session_state.get("operation_failed"):
        return
    session = st.session_state.get("session")
    if session is not None and session.report is not None:
        st.header("3 · 候选与证据")
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
    downloads = st.session_state.get("downloads", {})
    if downloads:
        st.header("4 · 报告下载")
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
