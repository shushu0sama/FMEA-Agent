# CLAUDE.md — FMEA Agent 项目指令

> 本文件是 Claude Code 的主要操作指令。
> 保持精简，便于每次会话读取。
> 长期原则存放于 `docs/foundation/`。

## 1. 项目使命

构建可维护、以证据为依据、具备 MBSE 感知能力的 FMEA Agent。

项目必须从可运行的纵向切片 MVP，逐步演进为可扩展的工程分析系统。

系统定位为**工程助手**，不具备自主裁决权。

最终工程决策仍须经过人工审核。

## 2. 当前 FMEA 方法配置

项目 FMEA 方法与版本的权威详细来源为：
`docs/domain/FMEA_PROFILE_V1.md`。

当前基线为 **AIAG & VDA FMEA Handbook, First Edition, 2019,
Seven-Step Approach**。

工作流采用七步法结构：

1. 策划与准备（Planning and Preparation）
2. 结构分析（Structure Analysis）
3. 功能分析（Function Analysis）
4. 失效分析（Failure Analysis）
5. 风险分析（Risk Analysis）
6. 优化（Optimization）
7. 结果文件化（Results Documentation）

不得复制或编造专有的 AIAG-VDA 评分表或 Action Priority 矩阵。
实现风险规则必须有获许可或用户提供的规则来源，或另行获授权的规则定义。

## 3. 核心架构决策

除非已接受的 ADR 修改了以下决策，否则均作为项目约束：

- LangGraph 是编排基线。
- LangChain 是可选的集成与适配基础设施，不属于领域核心。
- SysML/MBSE 是主要系统事实来源。
- 规范系统模型（Canonical System Model）是工程模型适配器与 FMEA 逻辑之间的边界。
- System Model 与 Failure Model 分离。
- 证据（Evidence）与来源追踪（Provenance）是一等数据。
- MCP 是外部能力接口，不属于领域核心。
- Neo4j 是当前图存储基线，必须封装在接口之后。
- 人工审核是正式的工作流边界。
- 工作流优先；自主多智能体行为延后。
- 优先实现可运行的纵向切片，再逐步替换桩实现。

## 4. 开发策略

### 4.1 最小功能，正确边界

首个实现可以只具备很少的智能能力。

但仍必须具备正确的模块边界。

优先选择：

```text
small capability
+ stable interfaces
+ tests
+ replaceable adapters
```

而不是：

```text
large demo
+ coupled code
+ hidden prompt logic
```

### 4.2 纵向切片优先

首个可运行 MVP 应使用：

- JSON 测试夹具输入；
- 最小 Canonical System Model；
- 最小 FMEA 领域模型；
- 内存仓储；
- 模拟或可选 LLM；
- LangGraph 工作流骨架；
- 结构化输出；
- 测试。

首个可运行 MVP 不得被以下能力阻塞：

- OpenSysML;
- Neo4j;
- Qdrant;
- Docling;
- MCP;
- 生产 UI；
- 完整的 AIAG-VDA 风险规则；
- 多智能体编排。

这些能力在后续阶段替换桩实现。

## 5. 事实来源优先级

系统事实的来源优先级：

```text
approved engineering model / SysML
> approved structured engineering data
> reviewed engineering documents
> retrieval result
> LLM inference
```

故障知识的来源优先级：

```text
approved FMEA / official standard / approved engineering record
> failure / test / maintenance record
> reviewed technical literature
> unreviewed document
> LLM inference
```

不得静默覆盖相互冲突的证据。
保留冲突；重大冲突必须上报处理。

## 6. 领域依赖规则

`domain/` 不得直接依赖：

- LangGraph;
- LangChain;
- Neo4j 驱动；
- Qdrant 客户端；
- MCP SDK;
- OpenSysML 运行时；
- 任何特定的 LLM 提供方；
- CLI/UI 框架。

外部技术必须位于端口与适配器之后。

## 7. 推荐代码结构

目标架构：

```text
domain/
application/
adapters/
agents/
evaluation/
cli/
```

目标端口（长期架构）：

```text
SystemModelRepository
FailureKnowledgeRepository
EvidenceRepository
LLMClient
RiskStrategy
ReviewRepository
```

当前 MVP 必需端口（以当前 Spec 为准）：

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

以下端口延后到需要时再实现：

```text
EvidenceRepository — until real Evidence / KG-RAG capabilities are needed
ReviewRepository   — until the Human Review stage
```

当前 MVP 的必需实现范围由当前 Spec 决定。

初始实现可以是：

```text
InMemorySystemModelRepository
InMemoryFailureKnowledgeRepository
MockLLMClient
NoOpRiskStrategy
```

后续替换实现可以包括：

```text
OpenSysMLSystemModelRepository
SysMLAPIRepository
Neo4jFailureKnowledgeRepository
QdrantEvidenceRepository
ProviderLLMClient
AIAGVDARiskStrategy
```

更换适配器时，上层不应需要重新设计。

## 8. 必读材料

每次必读：

1. `CLAUDE.md`
2. `PROGRESS.md`

按相关性读取：

- 架构与边界：
  `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md`
- 阶段、MVP 与复用：
  `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md`
- FMEA 语义：
  `docs/domain/FMEA_PROFILE_V1.md`
- 术语：
  `docs/domain/FMEA_GLOSSARY.md`
- 系统模型 schema：
  `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`
- 基准测试与评估：
  `docs/evaluation/BENCHMARK_SPEC.md`
- 第三方依赖：
  `docs/research/DEPENDENCY_INVENTORY.md`
- 重要决策：
  `docs/adr/`
- 当前功能：
  `docs/specs/` 和 `docs/plans/` 下的相关文件
- 阶段历史与发布状态：
  `docs/records/` + `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`

细小修改不必读取所有长篇文档。

## 9. 开发记录与会话恢复

完整治理规则：

```text
docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md
```

- 开始非简单 Stage 前，读取：
  `CLAUDE.md` / `PROGRESS.md`、当前 Spec、当前 Plan，
  以及上一阶段记录（`docs/records/`）。
- 一个正式 Stage 约对应一个主会话。切换会话时，从 Git + PROGRESS +
  Spec + Plan + Stage Records 恢复状态，不得依赖聊天记忆。
- `PROGRESS.md` 只记录当前状态；执行历史存放于
  `docs/records/`（每个 Stage 一份收尾记录，每个 MVP 一份发布记录）。
- Plan 不等于执行记录；提示词不等于事实来源。Stage Records 必须记录真实演化，
  不得为了迎合当前状态而改写历史。
- 防漂移：Stage 开始前和声明完成前，检查分支、HEAD 与范围；
  明确报告范围漂移。
- Stage 状态：IMPLEMENTED → READY_FOR_REVIEW → 独立审核
  → ACCEPTED / CHANGES_REQUIRED。
  未运行验证时，不得声称 COMPLETE/ACCEPTED/PASS。
- 验证证据必须标注为 LOCAL / CI / EXTERNAL_REVIEW
  （目前尚未配置 CI）。

## 10. 任务分类

非简单任务采用以下流程：

```text
Explore
→ Spec
→ Plan
→ Test
→ Implement
→ Verify
→ Review
→ Update PROGRESS
```

理解现有代码和当前阶段之前，不得开始实现。

## 11. 复用政策

编写基础设施之前：

1. 检索仓库。
2. 检索已选用的依赖。
3. 检查上游 API。
4. 对能力分类：

```text
S = Self-build
W = Wrap
D = Direct reuse
R = Reference only
```

FMEA 专属语义由项目自行实现。
通用基础设施优先复用。

没有书面理由时，不得重写 SysML 解析器、图数据库、向量数据库、MCP 协议、Agent 运行时或文档解析器。

## 12. 外部依赖政策

对于重要第三方项目：

- 固定版本；
- 需要可复现性时，记录重要 commit SHA；
- 记录许可证；
- 保持在适配器之后；
- 添加契约测试；
- 不要同时升级多个主要依赖；
- 接受升级前运行回归测试。

如果上游文档与可执行行为不一致，记录差异，并以可复现的测试证据为依据。

## 13. 测试

工具已配置时，至少运行：

```bash
pytest
ruff check .
mypy src
```

以上要求适用于已配置的工具。

测试类型：

- 单元测试；
- 集成测试；
- 契约测试；
- 回归测试；
- 基准测试。

外部适配器必须有契约测试。

依赖 LLM 的功能必须使用确定性夹具或模拟对象进行常规测试。

## 14. 完成条件

相关条件未满足时，不得声称任务完成：

- 范围与 Spec 明确；
- 实现遵守架构；
- 已添加或更新测试；
- 测试通过；
- lint 与类型检查通过；
- 相关基准测试未退化；
- 无无关修改；
- 证据与来源追踪得到保留；
- 文档已更新；
- `PROGRESS.md` 已更新；
- 未解决风险已明确报告。

## 15. FMEA 安全规则

不得把未经审核的候选项呈现为已批准的工程结果。

必须始终区分：

```text
FACT
RETRIEVED_KNOWLEDGE
INFERENCE
CANDIDATE
REVIEWED
APPROVED
UNKNOWN
```

缺少证据或规则时，不得编造 S/O/D/AP 值。

不得混淆：

- 失效模式（Failure Mode）；
- 失效起因（Failure Cause）；
- 失效机理（Failure Mechanism）；
- 失效影响（Failure Effect）。

## 16. 阶段纪律

不得仅因某项技术有吸引力，就提前实现后续阶段的基础设施。

当前实现优先级由 `PROGRESS.md` 定义。

当前推进策略：

```text
Runnable MVP first
→ real SysML
→ real failure knowledge
→ evidence-grounded LLM
→ risk/verification
→ human review
→ propagation
→ aerospace benchmark
→ MCP
→ dynamic FMEA
```

## 17. Git 纪律

- 每个分支或工作树只承担一个明确目标；
- 保持小粒度提交；
- 不做无关格式化；
- 不修改第三方 Git 历史；
- 实验与生产代码分离；
- 提交前先验证。

## 18. 完成报告

任务结束时，报告变更、原因、文件、测试及验证结果、基准影响、依赖变化、
已知限制和下一步建议；对应字段如下：

```text
What changed
Why
Files changed
Tests run
Verification results
Benchmark impact
Dependencies added/changed
Known limitations
Next recommended task
```

未运行验证时，不得声称“完成”。

## 19. 文档语言政策（Documentation Language Policy）

项目自有文档默认语言为 **简体中文（zh-CN）**。除非用户或当前任务明确要求英文，
Claude Code 新建的项目自有 Markdown 必须以中文为主体；修改中文文档时，不得无理由将中文段落改写为英文。

本政策覆盖项目 README、PROGRESS、Agent 指令与记忆/交接文档，以及
Spec、Plan、Architecture、ADR、Research Report、Benchmark Report、Stage Record、
Release Record、Session Handoff、Coding Agent Prompt 和 Completion Report。
适用目录包括 `docs/product/`、`docs/architecture/`、`docs/domain/`、`docs/specs/`、
`docs/plans/`、`docs/governance/`、`docs/evaluation/`、`docs/research/`、
`docs/records/`、`docs/prompts/`、`docs/adr/` 和 `docs/foundation/`。

代码、class/function/variable/enum/schema 标识符、JSON key、协议/API/CLI 名称、
路径、命令、Cypher、URL、Git branch/tag/commit SHA/commit message、技术与产品名、
标准名、包名和机器状态值保持英文或原始 canonical form。不得重命名文件或生产类来实现中文化。
代码块、CLI/test/Git output、原始外部资料、原始导入证据、上游原文副本、vendor 文件、
`LICENSE*` 和 `third_party/licenses/**` 保持原样；许可证必须逐字保留。

重要术语首次出现可使用“中文（English Canonical Term）”，后续按语境使用中文或 canonical term，
不机械制作逐句双语。术语以 `docs/domain/FMEA_GLOSSARY.md` 为准。
翻译历史文档只改变语言，不改变历史状态、测试数量、commit SHA、基准结果、已知限制、
当时计划或预测，也不得删除历史差异；发现非翻译事实问题，另记后续任务。

完整规则与 Documentation Language Gate 见
`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`；
术语政策补充见 `docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md`。
