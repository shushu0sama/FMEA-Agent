# MVP-2 规格说明 — 真实故障知识

Status: ACTIVE SPEC / PLANNING ONLY

> 2026-09-05 规划前补充：本文是当前草案入口，`ACTIVE` 不代表已批准。
> 用户已确认现有 SysML 与 Neo4j 案例独立且不重合，不能预设同一案例对应。
> 当前先进行[信息对齐](../product/MVP_2_PREPLANNING_ALIGNMENT.md)；第 4、8、10、16、17 节涉及的
> 实体解析、跨案例适用性及验收边界需在对齐后修订和审查。原草案正文保留，不据此启动 Plan 或生产实现。

## 1. 目标

从现有 Neo4j Failure Knowledge Base 开始，以对真实故障知识来源的只读检索替换 MVP-0 fixture 故障知识，同时保留 MVP-0/MVP-1 行为及架构边界。

MVP-2 生产实现状态为 `NOT_STARTED`。

## 2. 问题说明

当前 `FailureKnowledgeRepository` 以精确的显示名称对为键：

```text
(item_name, function_name) → list[FailureModeCandidate]
```

这足以支持 fixture，但不是适用于真实工程知识的稳定长期查询契约。现有 Neo4j 图也未直接编码完整的行级 `Component + Function + FailureMode` 上下文。

MVP-2 必须定义并实现来源知识检索边界，以支持实体解析、歧义和证据，同时避免将领域层绑定到 Neo4j，或直接从存储返回分析侧候选项。

## 3. 当前基线

已实现基线：

- MVP-0 fixture 故障库和内存查找。
- MVP-1 真实 SysML v2 File Mode 进入 Canonical System Model。
- 已实现的 CSM 子集：`System`、`Component`、`Function`、`SourceReference`。
- 尚无真实 Neo4j 适配器。
- 尚无 Neo4j Python driver 依赖。
- 尚无 Qdrant / RAG / 真实 LLM / Human Review / 风险评分。

外部基线证据：

- 现有 Neo4j 5.26.0 Legacy Failure Knowledge Graph。
- 图的主要优势：FailureMode 到 Cause、Effect、Prevention Control 和 Detection Control 的关联。
- 详细基线：`docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md`。

## 4. 阶段能力分解

2A 现有知识兼容性基线：

- 验证当前实现契约和 fixture 行为；
- 保留 MVP-0/MVP-1 回归；
- 在改变接口前记录兼容性约束。

2B 故障知识契约：

- 定义项目自有的查询与命中 / 来源知识契约；
- 保持来源知识与分析侧候选项的区分；
- 定义证据和来源追踪要求。

2C Neo4j 只读适配器：

- 通过项目自有端口之后的适配器读取现有 Neo4j；
- 不在适配器之外暴露 Neo4j driver 类型；
- 不修改数据库。

2D 实体解析与上下文重建：

- 将 CSM 分析对象 / 功能上下文连接到来源知识；
- 保留歧义及置信度 / 证据；
- 从现有图重建可用上下文，不重建数据库。

2E 工作流集成：

- 将来源知识命中映射为 `FailureModeCandidate` 分析输出；
- 保持工作流状态显式；
- 除非存在授权规则，否则风险保持 `NOT_EVALUATED`。

2F 基准与发布：

- 评估 Level 3 Failure Knowledge Retrieval；
- 运行 MVP-0/MVP-1 回归；
- 实现审查后更新记录和当前状态文档。

本规格说明定义“做什么”，不创建 `docs/plans/MVP_2_IMPLEMENTATION_PLAN.md`。

## 5. 范围内

- 真实故障知识来源契约。
- 端口之后的 Neo4j 只读检索适配器。
- CSM 上下文与故障知识之间的实体解析。
- 从现有图重建上下文。
- 检索所得来源知识的证据和来源追踪。
- 从检索所得来源知识到候选分析对象的映射。
- 在测试需要的地方向后兼容 MVP-0 fixture 行为。
- Level 3 基准设计和发布证据。

## 6. 范围外

- 在本次治理基线会话中修改 `src/` 或测试。
- 重建 Neo4j 数据库。
- 对生产数据库运行旧导入器。
- 在实现计划经过审查前安装 Neo4j driver。
- Schema 迁移。
- 知识写回。
- Candidate 到 Approved 的写入流程。
- 真实 LLM 生成。
- RAG / Qdrant 集成。
- MCP 集成。
- AIAG-VDA S/O/D/AP 或 Action Priority 实现。
- Human Review 实现。
- 失效传播。
- 改变 MVP-1 SysML 能力。

## 7. 领域语义

MVP-2 必须保留以下概念的区分：

- 失效模式（Failure Mode）；
- 失效起因（Failure Cause）；
- 失效机理（Failure Mechanism）；
- 失效影响（Failure Effect）；
- 预防控制（Prevention Control）；
- 探测控制（Detection Control）；
- 推荐措施（Recommended Action）；
- 证据（Evidence）。

从来源知识中检索到的历史控制必须能与 Agent 生成的建议区分。

缺失信息保持为 `UNKNOWN`，或以明确状态表示缺失。不得编造。

## 8. 来源知识与候选项

故障知识来源记录与分析侧 FMEA 候选项不是同一概念。

预期链路如下：

```text
CSM / Engineering Context
→ FailureKnowledgeQuery
→ FailureKnowledgeRepository
→ FailureKnowledgeHit / source knowledge
→ applicability / entity resolution / evidence
→ mapping
→ FailureModeCandidate
```

最终契约名称可以在 2B 冻结。本规格说明有意避免过早落实过多类名。

## 9. 证据和来源追踪要求

来源侧故障知识必须将证据（Evidence）与来源追踪（Provenance）作为一等数据。
每个来源命中至少必须能够表达：

- 来源身份（source identity）；
- 来源类型（source type）；
- 来源版本（source version）；
- 定位信息（locator），例如 repository / project / file、row、node 或 relationship；
- 来源权威性（authority）；
- 来源本身的审查 / 批准状态（review / approval state）；
- 从来源记录到检索命中及候选映射的可追踪链（traceability）；
- 匹配的实体；
- 关系路径或来源结构；
- 检索依据；
- 实体解析状态；
- 已定义时的置信度或适用性元数据；
- 已知时的 source hash / revision、rights / authorization 与 conflict state；
- 来源追踪字段不可用时的局限及显式 `UNKNOWN` / `unavailable` 状态。

旧图缺少行级来源追踪时，适配器必须显式表达这种缺失，不得编造来源行。

权威性与审查状态来自知识来源本身，例如 approved FMEA、reviewed engineering
record、test / maintenance evidence、technical literature 或 unreviewed source。
知识存储在 Neo4j 中只说明其 storage / retrieval source，不构成高 authority 或
已审查 / 已批准的证明。

本节不要求所有来源天然具备全部字段，也不要求 MVP-2 提前创建
`EvidenceRepository`、复杂 RAG、vector DB 或 LLM evidence extraction。
具体 production contract / class shape 留到 MVP-2B 冻结。

## 10. 实体解析要求

当前 Canonical System Model ID（例如 `component-N`、`function-N`）仅是当前
snapshot / mapping context 内的 canonical identifier，不承诺跨版本、跨文件或
跨 commit 稳定，不得作为永久 Failure Knowledge identity。规范身份事实以
`docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md` 和
`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md` 为权威来源，本规格不复制其完整规则。

实体解析必须支持：

- 综合当前 canonical context 将 CSM 分析对象 / 组件 / 功能上下文匹配到来源知识；
- 使用 item / component display name、alias / normalized name；
- 使用 Function semantics 与 Component semantics；
- 使用 `SourceReference`、`SourceReference.source_element_id`、source / model version
  以及 source URI / locator；
- 使用 applicability context 与来源提供时的 historical FMEA row context；
- 保留歧义及已定义时的 confidence；
- 不静默覆盖冲突匹配；
- 不将显示名称作为唯一的长期身份策略；
- 不将 `component-N` / `function-N` 作为唯一的长期身份策略；
- 每个接受的匹配都有可追踪证据。

精确显示名称匹配可以保留为兼容性基线或回退方式，但不得成为长期规范查询契约。
具体 `EntityResolution` class shape 留到 MVP-2B，本规格不提前冻结实现。

## 11. 仓库语义契约要求

`FailureKnowledgeRepository` 契约必须从 fixture 专用的候选查找演进为来源知识检索。

不应要求仓库直接从存储返回 `FailureModeCandidate`。候选构建属于应用 / 领域映射步骤，该步骤可以附加分析上下文和证据。

## 12. Neo4j 只读边界

MVP-2 的 Neo4j 行为为只读。

适配器不得：

- 调用破坏性图操作；
- 运行生产写入查询；
- 执行 schema 迁移；
- 将 Excel 导入 Neo4j；
- 复制旧凭据；
- 在适配器之外暴露 driver 专有类型。

## 13. Excel 和本体的作用

历史 Excel / CSV 在通过受治理契约明确摄取后，可以成为故障知识来源。旧 Excel 导入器仅作为参考证据，不得原样成为生产路径。

Ontology / n10s 的存在可以为未来语义提供参考，但 MVP-2 不得依赖本体迁移或 RDF 重建来检索现有基线图。

## 14. 向后兼容

MVP-2 必须保留：

- MVP-0 演示行为，除非经审查的规格 / 计划明确改变它；
- MVP-1 真实 SysML 链路；
- 无授权风险规则时的 `RiskAssessment(status=NOT_EVALUATED)` 行为；
- 无优化能力时显式的 `SKIPPED` 优化；
- `domain/` 不依赖 Neo4j 的架构规则。

## 15. 回归要求

实现阶段必须运行已配置的验证套件：

```text
pytest
ruff check .
mypy src
git diff --check
```

如果完整生产验证不适用于仅文档工作，报告必须明确说明。

## 16. 基准预期

MVP-2 增加 Level 3 Failure Knowledge Retrieval 评估：

```text
Recall@K
Precision@K
MRR (optional)
Evidence Coverage
Entity Resolution Accuracy
Source Trace Completeness
```

团队接受基准数据和阈值之前，不得编造数值发布门槛。

## 17. 验收标准

- 现有 Neo4j 基线已形成文档，并按只读处理。
- 来源知识契约区分检索命中与候选项。
- 仓库契约的长期规范接口不再仅依赖精确显示名称对查找。
- 实体解析保留歧义和证据。
- 工作流集成将来源知识映射为候选项，不将未经审查内容变为已批准内容。
- MVP-0/MVP-1 回归持续通过。
- MVP-2 不引入真实 LLM / RAG / MCP / 风险评分 / Human Review 实现。
- 文档和记录准确说明 MVP-2 实现状态。

## 18. 已知风险

- 旧图缺少行级来源追踪。
- 领域标签为中文，且多数仅有名称。
- 关系属性缺失。
- 功能 / 组件上下文可能需要从间接路径重建。
- 精确名称可能与 CSM 名称不一致。
- n10s 基础设施存在，但可能未编码所需 FMEA 语义。
- 实现前必须规划 driver / 版本和凭据处理。

## 19. 延后能力

- 知识写回。
- Candidate 到 Approved 的持久化。
- 真实 LLM 以证据为依据的生成。
- Qdrant / KG-RAG 融合。
- AIAG-VDA 风险策略和 AP 规则。
- Human Review 工作流。
- 失效传播。
- MCP 工具和外部能力暴露。
