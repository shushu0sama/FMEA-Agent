# Demo V1 D0 — 规格与实施计划记录

日期：2026-09-05
Stage status: ACCEPTED（仅规格/计划准备）
Scope: Demo 规格、分阶段实施计划、资料/接口准备核查；不是功能实现。

## 1. 用户意图与范围演化

用户已同意“选取小型 SysML 案例，资料上传/自然语言/自动检索/参考性推理/UI/候选报告”的方向，
并要求进行下一步。此前用户选定现有 SysML 派生演示资料，已有 DeepSeek API，目标约一周且可放宽。
该范围跨越原本只做检索的 MVP-2，因此本次定义 Demo V1 里程碑，不把旧 MVP-2 草案默默扩为全部产品。

采用 [Demo Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md) 和
[Demo Plan](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md) 作为下一阶段入口。
原 [信息对齐台账](../../product/MVP_2_PREPLANNING_ALIGNMENT.md)转为历史讨论来源，
原 MVP-2 草案保留原文并标注为后续完整检索阶段参考。未回答的长期问题仍未知，不表示全部需求永久冻结。

## 2. Git 与范围

```text
Start branch: fix/pre-mvp2-review-remediation
Start HEAD:   47858aa45c9177ca943838c263605f1ef1496f45
Start tree:   clean
Work branch:  codex/demo-v1-spec-plan（本次从 Start HEAD 新建）
```

本次只修改项目文档；未安装项目依赖、重建图、读取 ignored 凭据文件、执行 API 调用、
创建前端或生成案例集。不合并、推送、创建或移动 tag。
规格定义的 D1–D7 全部尚未实施；Plan 的代码/命令是后续步骤，不是本次执行记录。

## 3. LOCAL — 真实 SysML 准备核查

读取现有端口、FMEA/CSM模型、workflow/state、输入入口和现有benchmark。
复用基础：OpenSysML adapter、CanonicalSystemMapper、现有 domain/Application ports、LangGraph。
发现原 graph 的结果字段缺失来源/嵌套证据，与既有 PROGRESS 一致；D2计划补齐，当前未修复。

使用当前 `.venv` 执行下列等价读取流程，无生产改动：

```python
from fmea_agent.adapters.sysml.open_sysml_file import OpenSysMLFileAdapter
from fmea_agent.adapters.sysml.canonical_mapping import CanonicalSystemMapper
snapshot = OpenSysMLFileAdapter().load("tests/fixtures/sysml/models/typed_inside_probe.sysml")
model = CanonicalSystemMapper().map_snapshot(snapshot)
```

结果：`load_status=ok`，diagnostics=0；System=hydraulicPump；Component=motor；
Function=pumpSpin→system-1，spin→component-1。首个目标只取 motor/spin。
文件 SHA-256：`fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5`。
该样例是项目自有教学夹具；没有工况/额定参数或工程审核背书。

抽查官方 Flashlight/Camera 模型文本：前者使用 performed action，后者有 import/跨包引用；
结合已有 C1/C4限制，不把它们替换成一周首例。未运行这两个官方样例，也未判定其上游模型错误。

只检查当前 Python 进程变量是否存在：DEEPSEEK_API_KEY、NEO4J_URI、NEO4J_USERNAME、
NEO4J_PASSWORD 均为 false。没有输出值或读取配置文件。
这不证明用户未在其他位置配置，仅说明本次进程尚不能据这些变量运行真实外部接入。

## 4. 外部接口与依赖核查（文档/registry）

以下为 2026-09-05 在线文档阅读，非真实账号调用，也不宣称依赖已通过本项目契约测试。

- [DeepSeek 官方接入](https://api-docs.deepseek.com/)：模型标识包含 `deepseek-v4-pro`，
  base URL 为 `https://api.deepseek.com`；服务别名可能随上游更新。
- [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)：
  `thinking.type=disabled`、`response_format.type=json_object` 为已记录参数。
- [JSON Output](https://api-docs.deepseek.com/guides/json_mode/)：需要 JSON 提示，可能空内容；
  因此计划包含空值、截断、schema和引用校验，不依赖格式请求直接证明工程正确。
- [Neo4j 官方查询文档](https://neo4j.com/docs/python-manual/current/query-simple/)：
  参数化查询/显式 database；read routing 不是访问控制，计划使用固定只读模板。
- [Streamlit 对话输入](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input) 与
  [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)：
  选用现成 UI/测试接口；上传控件仍须应用层内容校验。
- [pypdf 文本提取](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、
  [openpyxl 教程](https://openpyxl.readthedocs.io/en/stable/tutorial.html)、
  [HTTPX transport](https://www.python-httpx.org/advanced/transports/) 用于解析/读取/mock transport 复用。
  openpyxl 教程页面显示 3.1.3，本次 registry 选定包为 3.1.5，实际行为须在 D2 契约测试中核对。

通过 PyPI JSON 元数据检查版本、Python要求与许可证，未下载/执行包：

| 包 | 选定版本 | Python 要求 | 元数据许可证 | 来源 |
|---|---|---|---|---|
| neo4j | 5.28.2 | >=3.7 | Apache-2.0 | https://pypi.org/pypi/neo4j/5.28.2/json |
| streamlit | 1.63.0 | >=3.10 | Apache-2.0 | https://pypi.org/pypi/streamlit/1.63.0/json |
| pypdf | 6.17.0 | >=3.9 | BSD-3-Clause | https://pypi.org/pypi/pypdf/6.17.0/json |
| openpyxl | 3.1.5 | >=3.8 | MIT | https://pypi.org/pypi/openpyxl/3.1.5/json |
| httpx | 0.28.1 | 当前 uv.lock 已锁定 | 安装时核对许可证材料 | 当前锁文件与官方 transport 文档 |

后三个新增包本次实际读取 `/pypi/<name>/json` 的当时最新元数据，表内版本 URL 用于后续定位。
项目 pyproject/uv.lock 保持不变；表内版本是分阶段接入选择，不等于全部依赖解算已通过。

## 5. 验证、审查与限制

LOCAL 已执行所选样例解析；另运行：

```text
python -m pytest tests/test_open_sysml_file_adapter.py::test_valid_model_loads_ok_snapshot
                 tests/test_mvp1_benchmark.py::test_b0_exact_mapping_matches_gold -q
```

结果：`2 passed in 0.49s`。仅为所选既有解析/基准用例，不是 Demo 功能测试。

EXTERNAL_REVIEW 初审：独立 Agent `/root/c1_final_review` 判定 `CHANGES_REQUIRED`，
CRITICAL=0、IMPORTANT=2、MINOR=0：成功报告无法自包含输入/系统摘要，失败诊断缺少导出契约。
随后补充 InputFileRecord/CandidateReport.input_snapshot 与 DiagnosticReport/export_diagnostics，
明确脱离会话往返测试；同时统一 HTTP 为连接/读取阶段超时，说明旧模式只有 item/function 关联 ID。
初审时 D0 文件正在创建，引用尚未存在；现已补齐。

EXTERNAL_REVIEW 复验：独立 Agent `/root/c1_final_review` 判定 `ACCEPTED`，
CRITICAL=0、IMPORTANT=0、MINOR=0；确认两项初审问题关闭、输入/失败导出接口完整、入口一致。
reviewer 独立复核下方文档检查、首例 hash 和生产范围无变化；未重复运行两个测试，未访问API/数据库。
该结论只接受 D0 规格/计划及入口文档，不代表 D1–D7 已实施或技术/工程验收完成。

LOCAL 文档检查：10 份 Markdown 围栏、47 个本地目标和 3 个章节锚点通过；
原 MVP-2 Spec 与信息对齐第 1 节起正文完整保留；Plan 无 TODO/TBD 占位符；
`git diff --check` 通过；src/tests/scripts/pyproject.toml/uv.lock 相对起点无变化。
Spec/Plan/D0 中 Python 示例仅做 AST 语法检查，不将计划中的测试片段算作已运行测试。
本次不重复执行全套 pytest/ruff/mypy：无代码或依赖变化；不把历史 223 项验证写成本次执行。
当前benchmark文件与gold无变化，D1案例包尚未创建；真实API/Neo4j适配器与UI均未实现或验收。

## 6. 下一步

D0 审查后从 D1 固定案例与演示资料开始。项目源码与已发布能力仍是 MVP-1。
当前不要求用户再提供工程方法细节；真实接入前需要用户在本机配置服务凭据，
仅传递变量名/配置路径，密钥不进入聊天、Git、模型上下文或报告。
