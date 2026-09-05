# 依赖清单 v0.1

> 本文件跟踪重要外部依赖和研究仓库。
> 依赖实际集成时必须补齐精确版本/提交。

## 分类

复用分类：

```text
S = Self-build
W = Wrap
D = Direct reuse
R = Reference only
```

成熟度：

```text
STABLE
CANDIDATE
EXPERIMENTAL
WIP
DEFERRED
```

## 外部 FMEA 研究实现

| 项目 | 固定提交 | 复用分类 | 当前决策 |
|---|---|---|---|
| [LLMRiskAnalyzer](https://github.com/YuchenXia/LLMRiskAnalyzer) | `03dfd4cf3e6095d71f6b78317f333911016a65e3` | R | 未发现许可证声明；仅参考字段建议交互，不引入代码/数据/依赖。[核查记录](LLMRISKANALYZER_REUSE_REVIEW_2026_09_05.md) |

## 核心开发依赖

| 项目 | URL | 作用 | 复用分类 | 成熟度 | 当前决策 |
|---|---|---|---|---|---|
| Pydantic | https://github.com/pydantic/pydantic | 领域/数据契约 | D | STABLE | 使用 |
| pytest | https://github.com/pytest-dev/pytest | 测试 | D | STABLE | 使用 |
| Ruff | https://github.com/astral-sh/ruff | 检查/格式化 | D | STABLE | 使用 |
| mypy | https://github.com/python/mypy | 静态类型检查 | D | STABLE | 使用 |
| LangGraph | https://github.com/langchain-ai/langgraph | 有状态工作流编排 | D/W | STABLE/CANDIDATE | 基线编排器 |
| MCP Python SDK | https://github.com/modelcontextprotocol/python-sdk | MCP 协议 | D | STABLE | 阶段 8；不要重新实现 |
| langchain-mcp-adapters | https://github.com/langchain-ai/langchain-mcp-adapters | 从 LangChain/LangGraph 使用 MCP | D/W | CANDIDATE | 采用时固定版本并执行契约测试 |

## SysML / MBSE

| 项目 | URL | 作用 | 复用分类 | 成熟度 | 当前决策 |
|---|---|---|---|---|---|
| SysML-v2-Release | https://github.com/Systems-Modeling/SysML-v2-Release | 官方模型/示例/规范产物 | D/R | STABLE/CANDIDATE | 基准测试/参考 |
| SysML-v2-Pilot-Implementation | https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation | 参考实现 | R | CANDIDATE | 语义交叉检查 |
| SysML-v2-API-Services | https://github.com/Systems-Modeling/SysML-v2-API-Services | 仓库/REST 访问 | D/W | CANDIDATE | Repository Mode |
| SysML-v2-API-Cookbook | https://github.com/Systems-Modeling/SysML-v2-API-Cookbook | API 用例示范 | D/R | CANDIDATE | 复用遍历模式 |
| OpenSysML | https://github.com/Open-MBEE/OpenSysML | `.sysml` 运行时/解析器/Python-gRPC 集成 | D/W | STABLE（已固定版本） | 已启用 — MVP-1C File Mode 适配器（记录见下） |
| SYSMOD SysML v2 | https://github.com/MBSE4U/sysmod-sysmlv2 | Delivery Drone/模型示例 | D/R | CANDIDATE | 基准测试 |
| SYSMOD SysML v2 API/MCP | https://github.com/Open-MBEE/sysmod-sysmlv2-api | SysML API + MCP 模式 | W/R | WIP | 架构/MCP 参考；不得绑定核心领域 |
| SysML-v2 Applications and Examples | https://github.com/Open-MBEE/SysML-v2-Applications-and-Examples | CubeSat/航天器示例 | D/R | CANDIDATE | 航空航天基准测试 |

## 知识 / 检索 / 文档

| 项目 | URL | 作用 | 复用分类 | 成熟度 | 当前决策 |
|---|---|---|---|---|---|
| Neo4j Python Driver | https://github.com/neo4j/neo4j-python-driver | 图持久化/查询 | D/W | STABLE | 图存储基线 |
| neosemantics | https://github.com/neo4j-labs/neosemantics | RDF/OWL/SKOS/SHACL 桥接 | D/W | CANDIDATE | 本体集成需要时使用 |
| RDFLib | https://github.com/RDFLib/rdflib | RDF/Turtle/SPARQL 处理 | D | STABLE | 工具 |
| Qdrant | https://github.com/qdrant/qdrant | 向量检索 | D/W | STABLE | 候选；MVP-0 不要求 |
| Docling | https://github.com/docling-project/docling | PDF/Office 结构化解析 | D/W | STABLE/CANDIDATE | 候选；需要文档摄取时添加 |
| pandas | https://github.com/pandas-dev/pandas | 表格化 FMEA 处理 | D | STABLE | 按需使用 |
| openpyxl | https://openpyxl.readthedocs.io/ | Excel I/O | D | STABLE | 使用；源码仓库链接见官方文档 |

## MCP 实现

| 项目 | URL | 作用 | 复用分类 | 成熟度 | 当前决策 |
|---|---|---|---|---|---|
| Official MCP Reference Servers | https://github.com/modelcontextprotocol/servers | MCP 模式/参考 | D/R | STABLE/CANDIDATE | 参考 |
| Neo4j MCP | https://github.com/neo4j/mcp | 通用图 MCP | D/W | CANDIDATE | 复用，不自建通用 Neo4j MCP |
| Neo4j Labs MCP | https://github.com/neo4j-contrib/mcp-neo4j | 实验性图 MCP 示例 | R | EXPERIMENTAL | 次要参考 |
| Qdrant MCP | https://github.com/qdrant/mcp-server-qdrant | 向量搜索 MCP | D/W | CANDIDATE | 需要 MCP 向量访问时复用 |
| Docling MCP | https://github.com/docling-project/docling-mcp | 文档处理 MCP | D/W | CANDIDATE | 需要面向 Agent 的文档处理时复用 |
| SYSMOD SysML MCP | https://github.com/Open-MBEE/sysmod-sysmlv2-api | SysML/SYSMOD Agent 工具 | W/R | WIP | 研究/封装；具有方法论专属性 |

## Demo V1 / D4 HTTP 与模型适配（2026-09-05）

`httpx==0.28.1`（W）从已有锁定依赖补为 optional extra `demo` 的直接依赖；
未新增包或升级现有版本，锁文件仍为 78 packages。许可证 BSD-3-Clause，
已核对安装元数据；未复制上游源码。适配器：`src/fmea_agent/adapters/llm/deepseek.py`；
契约：`tests/test_demo_deepseek.py`，语义校验不依赖 HTTPX。

上游：[DeepSeek API](https://api-docs.deepseek.com/api/create-chat-completion/)、
[HTTPX 超时](https://www.python-httpx.org/advanced/timeouts/)。模型固定请求别名 `deepseek-v4-pro`，
不声称固定权重 SHA。没有引入 DeepSeek/OpenAI SDK；替换提供商时保持 LLMClient 边界。
升级仍须单依赖、契约与全套回归。D4 初次真实 smoke 因 CONFIG_MISSING 跳过；
用户后续配置后，2026-09-05 的通用 JSON/完整 schema live smoke 已通过，未验收工程质量。
详细证据和限制见 [D4 记录](../records/DEMO_V1/D4_DEEPSEEK_AND_GENERATION_VALIDATION.md)。

## Demo V1 / D3 Neo4j 只读驱动（2026-09-05）

optional extra `demo` 新增 neo4j==5.28.2（W）和传递 pytz==2026.3.post1（D），
已有锁定版本不变，wheel/source hash 由 `uv.lock` 保存。
neo4j 安装元数据为 Apache License, Version 2.0，原文位于
`neo4j-5.28.2.dist-info/licenses/` 的 LICENSE.txt、LICENSE.APACHE2.txt、LICENSE.PYTHON.txt；
pytz 为 MIT，原文位于 `pytz-2026.3.post1.dist-info/LICENSE.txt`。

适配器：`src/fmea_agent/adapters/neo4j/failure_knowledge.py`；
契约：`tests/test_demo_neo4j_contract.py`；真实 smoke：`scripts/demo_neo4j_smoke.py`。
固定只读 Cypher、显式 10 秒事务、无自动事务重试；驱动不进入 domain/application。
目标服务沿用已盘点 Neo4j 5.26.0；初次真实 smoke 为 CONFIG_MISSING/SKIPPED；用户后续配置并修正密码后，
2026-09-05 真实只读 smoke 已通过，结果有界且标记截断；不将单次 smoke 等同于完整服务契约验收。
替换实现须保持 D2 SourceKnowledgeRepository，升级一次一个集成并回归。
执行证据与上游 API 核对见 [D3 记录](../records/DEMO_V1/D3_READONLY_NEO4J_RETRIEVAL.md)。

## Demo V1 / D2 文件解析依赖（2026-09-05）

以下仅通过 optional extra `demo` 安装；原依赖版本没有升级，基础 CLI 不依赖这些包。
精确 wheel/source hash 由 `uv.lock` 记录，契约测试见 `tests/test_demo_document_inputs.py`。

| 包 | 固定版本 | 已安装包许可证元数据/原文 | 分类 | 用途 |
|---|---|---|---|---|
| pypdf | 6.17.0 | BSD-3-Clause；dist-info/licenses/LICENSE | W | 本地 PDF 逐页提取文本；不做 OCR/布局还原 |
| openpyxl | 3.1.5 | MIT；dist-info/LICENCE.rst | W | read_only=True、data_only=False、keep_links=False 读取 BOM |
| et-xmlfile | 2.0.0 | MIT；dist-info/LICENCE.rst，另带 LICENCE.python | D（传递） | openpyxl 传递依赖 |

API 依据：[pypdf 文本提取](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、
[openpyxl 只读模式](https://openpyxl.readthedocs.io/en/stable/optimized.html)与
[load_workbook](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html)。
openpyxl stable 文档显示 3.1.3，实际安装并测试版本为 3.1.5；不把文档标签当作运行版本。
包从公开 registry 安装，没有复制外部产品资料或修改许可证原文。

## 已启用依赖记录（MVP-0，集成于 2026-09-04）

由 `uv.lock` 锁定。构建后端：hatchling（通过 `uv`）。

| 包 | 选定版本 | 许可证 | 作用 |
|---|---|---|---|
| pydantic | 2.13.5 | MIT | 领域/数据契约 |
| pytest | 8.4.2 | MIT | 测试 |
| ruff | 0.16.6 | MIT | 检查/格式化 |
| mypy | 1.20.2 | MIT | 类型检查 |

## 已启用依赖记录 — OpenSysML（MVP-1C，集成于 2026-09-04）

版本固定依据与复现证据：
`docs/research/OPENSYSML_SPIKE_REPORT.md`（1A）+
`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`（1C-0，PYPI_PIN_CONFIRMED）。

```text
Python client:  opensysml==0.4.0（PyPI wheel，精确 pin；Apache-2.0）
                wheel sha256 d3a9cfea481818656ec2f30f432c85ac74c41ab22adb51c5d9095c7cc1da3fca
                依赖集合与 Spike 记录一致（grpcio 1.83.1 / protobuf 7.36.1）

Runtime:        sysml-grpc v0.4.3 windows-amd64（非 Python dependency）
                GitHub release Open-MBEE/OpenSysML @ tag v0.4.3
                asset: sysml-grpc-windows-amd64.exe
                commit 99e02003c9c49358828b1c491a75de61745646ce
                sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe

Adapter path:       src/fmea_agent/adapters/sysml/open_sysml_file.py
Contract test path: tests/test_open_sysml_file_adapter.py
Known limitations:
  - single-file subset；用户文件 import 不支持（C1，unresolved import 显式诊断）
  - Model.hash = load-context fingerprint（F1），非跨路径/跨版本稳定 identity
  - performed ActionUsage 无 typing facts（C4），禁止推断
  - runtime provisioning：本机缓存 ~/.opensysml/bin；备选 $OPENSYSML_BINARY /
    $OPENSYSML_GRPC_VERSION；client 0.4.0 digest 表只 pin 到 v0.3.0（自动下载回退）
Replacement option: sysml-grpc v0.3.0（digest 已在 client pin 表内，可自动校验下载）
Upgrade policy:    一次只升级一个 major integration；contract tests + MVP-0 regression
                   通过后才接受（见本文件 Upgrade Policy）

Upgrade policy: one dev-dependency major at a time; run `pytest` + `ruff check .` + `mypy src` before accepting.
```

## 参考基线 — 现有 Neo4j 故障知识（Pre-MVP-2，2026-09-04）

以下是历史规划基线；当前 Demo D3 驱动安装与验证状态见上方 D3 专节，不改写当时状态。

详细基线：
`docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md`.

```text
Neo4j version: 5.26.0
Role:          existing Legacy Failure Knowledge Graph
MVP-2 status:  planning baseline only; future read-only adapter
Driver:        not installed in current project dependencies
Write-back:    out of scope for MVP-2
Security:      legacy importer is reference evidence only; do not copy secrets
               or run destructive import behavior against production
```

## Demo D6 本机 UI 依赖（2026-09-05）

`streamlit==1.63.0` 加入 optional extra `demo`，分类 D/W；应用入口
`src/fmea_agent/ui/demo_app.py`，配置装配 `application/demo_settings.py`，契约测试
`tests/test_demo_ui.py` / `test_demo_settings.py`。安装元数据声明许可证 Apache-2.0；
本机 wheel 文件清单未附 LICENSE，已核对
[固定版本上游原文](https://raw.githubusercontent.com/streamlit/streamlit/1.63.0/LICENSE)，
不将不存在的本机许可证文件记作已核实；本次不修改许可文本或分发二进制。
官方来源：[固定版本 PyPI](https://pypi.org/project/streamlit/1.63.0/)、
[AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)、
[上传](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)、
[下载](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)。

首次解析引入 NumPy 2.5.2（另有平台/Python 分支 2.4.6），其 PEP 695 类型声明使项目
`mypy python_version=3.11` 在依赖内发生语法错误。仅对新传递依赖增加
`[tool.uv].constraint-dependencies = ["numpy==2.3.5"]`，复验类型检查通过，
没有升级/降级 D5 既有核心依赖，也没有屏蔽项目类型检查。最终锁文件 104 packages，
与 `8a77ed9` 的 name/version 集合比较，既有包全部保持；新增 26 包：

| 新增包及固定版本 | 许可证（安装元数据 / 原文核对） |
|---|---|
| streamlit 1.63.0、pyarrow 25.0.1、pydeck 0.9.3、python-multipart 0.0.32、watchdog 6.0.0 | Apache-2.0 |
| altair 6.2.2、click 8.5.0、itsdangerous 2.2.0、jinja2 3.1.6、markupsafe 3.0.3、numpy 2.3.5、pandas 3.0.5、starlette 1.6.0、uvicorn 0.52.4 | BSD-3-Clause；NumPy 二进制另含第三方声明 |
| attrs 26.1.0、httptools 0.8.0、jsonschema 4.26.0、jsonschema-specifications 2025.9.1、narwhals 2.25.0、referencing 0.37.0、rpds-py 2026.6.3、six 1.17.0、toml 0.10.2 | MIT |
| pillow 12.3.0 | MIT-CMU |
| python-dateutil 2.9.0.post0 | Apache-2.0 / BSD 双许可证 |
| tzdata 2026.3 | Python 包 Apache-2.0；IANA 时区数据另见随包许可说明 |

其余已核实许可保留在各自 `*.dist-info/{LICENSE*,licenses/}`，分发二进制时须保留随包第三方声明，
不能只用上表替代完整许可。stdlib `html/csv/json/tempfile` 直接复用；没有新增排版、解析或 Agent 框架。
完整执行、依赖差异与适用限制见 [D6 记录](../records/DEMO_V1/D6_REPORTS_AND_LOCAL_UI.md)。

## 集成记录模板

启用依赖时填写：

```text
Selected version:
Selected commit:
License:
Adapter path:
Contract test path:
Known limitations:
Replacement option:
Upgrade policy:
```

## 升级政策

对于：

```text
OpenSysML
SysML API
LangGraph
MCP SDK
langchain-mcp-adapters
Neo4j
Qdrant
Docling
```

每次只升级一个主要集成：

```text
read changelog
→ upgrade branch
→ contract tests
→ regression benchmark
→ ADR if architecture changes
→ merge
```

不得批量升级整个技术栈。

## MCP 兼容性说明

MCP 生态变化迅速。
集成时必须验证以下组件的精确 SDK/协议兼容性：

```text
MCP Python SDK
LangChain MCP adapters
third-party MCP servers
```

并固定可用版本。
