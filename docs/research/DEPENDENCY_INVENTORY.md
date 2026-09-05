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
