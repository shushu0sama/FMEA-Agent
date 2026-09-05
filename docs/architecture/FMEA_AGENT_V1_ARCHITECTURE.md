# FMEA Agent V1 架构

Status: ACTIVE

## 1. 目的

本文档定义长期有效的 V1 架构边界，不将所有功能都描述为当前已实现的能力。

## 2. 分层

```text
User / API
  ↓
Agent Orchestration (LangGraph)
  ↓
Domain Services
  ↓
Canonical System Model + Failure Knowledge Model
  ↓
Ports
  ↓
Adapters
  ↓
Engineering / Knowledge / External Sources
```

LangGraph 是编排基线。FMEA 领域模型保持项目自有且独立于框架。

## 3. 依赖规则

`domain/` 不得直接依赖：

- Neo4j driver；
- LangGraph；
- LangChain；
- Qdrant client；
- OpenSysML runtime；
- MCP SDK；
- 任何特定 LLM 提供商；
- CLI 或 UI 框架。

外部技术应置于端口和适配器之后。

## 4. 工程上下文边界

Engineering Context 适配器将外部工程来源转换为项目自有事实，再转换为规范系统模型（Canonical System Model）。

当前已实现的来源：

- 通过 OpenSysML 进入 `SysMLFactSnapshot` 的 SysML v2 File Mode。

规划 / 未来来源：

- SysML Repository API；
- MBSE 仓库；
- BOM；
- Product Design Manual 和设计文档；
- PLM 和需求数据库。

Canonical System Model 是工程模型适配器与 FMEA 逻辑之间的长期边界。领域层不得变为 SysML 专用实现。

## 5. 故障知识边界

Failure Knowledge 适配器将外部故障知识转换为项目自有的来源知识记录。

当前已实现的来源：

- 用于回归的 MVP-0 fixture / 内存知识。

MVP-2 来源：

- 现有 Neo4j Failure Knowledge Base，只读。

未来来源：

- 历史 FMEA Excel / CSV；
- FMEA 报告；
- 已审查的失效、测试和维护记录；
- 从文档提取的知识。

Neo4j 是适配器 / 存储基线，不是领域边界。

## 6. 来源知识与候选分析

故障知识检索和 FMEA 候选构建是独立步骤。

目标链路如下：

```text
CSM / Engineering Context
→ FailureKnowledgeQuery
→ FailureKnowledgeRepository
→ FailureKnowledgeHit / source knowledge
→ applicability / entity resolution / evidence
→ mapping
→ FailureModeCandidate
```

仓库契约不应永久要求精确的显示名称对，例如 `(item_name, function_name)`；也不应强制 Neo4j 适配器直接返回分析侧 `FailureModeCandidate` 对象。

## 7. 证据和来源追踪

证据和来源追踪是一等数据。架构必须保留：

- 工程来源引用；
- 故障知识来源引用；
- 检索证据；
- 映射 / 实体解析证据；
- 分析状态；
- 相应阶段存在时的审查 / 批准元数据。

无依据的断言必须显式保留为 `UNKNOWN`、`NOT_EVALUATED` 或仅为候选的内容。

## 8. 实体解析

当来源 schema 不共享稳定标识符时，实体解析（Entity Resolution）负责连接工程上下文与故障知识。

MVP-2 必须考虑已知 Neo4j 缺口：现有图中 FailureMode 与 Cause、Effect、Prevention Control 和 Detection Control 的关联较强，但并未直接编码完整的行级 `Component + Function + FailureMode` 分析上下文。

实体解析必须保留歧义，不得静默选择单个来源命中。

## 9. LLM 边界

LLM 位于 `LLMClient` 或未来等效端口之后，保持提供商中立。

MVP-2 不调用真实 LLM。MVP-3 仅在真实故障知识检索已存在后，引入以证据为依据的 LLM 生成。

LLM 输出在经过审查和批准前属于候选或推断。

## 10. RiskStrategy

风险评估保持在 `RiskStrategy` 之后。

MVP-2 不实现 AIAG-VDA S/O/D/AP 或 Action Priority 逻辑。授权风险规则需要有许可或独立授权的来源。

## 11. 人工审查边界

人工审查是正式工作流边界。候选内容可以自动生成、检索和检查，但批准需要明确的审查状态。

审查持久化和未来知识生命周期安排在真实故障知识及以证据为依据的生成阶段之后。

## 12. 外部能力边界

API、MCP 和外部工具是能力边界，不是领域模型。

项目未来可以暴露或调用工具，但领域层应能够在不使用 MCP 专用请求 / 响应类的情况下运行。

## 13. 未来 KnowledgeWriter 边界

知识写回不属于 MVP-2。

在 Human Review 定义 Candidate 如何成为经审查或已批准的来源知识之后，长期架构可以增加 `KnowledgeWriter` 或等效边界。MVP-2 保持只读。
