# FMEA Agent V1 产品边界

Status: ACTIVE

> 2026-09-05 近期交付意图补充：用户希望设计文档/BOM/SysML、自然语言交互、前端 UI、
> 参考性推理和候选报告形成可演示流程，并提出使用中积累知识。
> 具体 Demo 范围及阶段重排见[信息对齐第 9 节](MVP_2_PREPLANNING_ALIGNMENT.md#9-完整问卷答复与-demo-目标澄清)，仍待设计确认。
> 下文现有/规划/长期能力分类保留，不能将新增意图误读为这些能力已实现。

## 1. 主要用户

V1 的主要用户是 FMEA 工程师。

## 2. V1 使命

FMEA Agent V1 是以证据为依据的半自主 DFMEA 助手。它应根据工程设计上下文、历史故障知识和已审查的来源证据，帮助生成完整的候选 FMEA（Candidate FMEA），供工程审查。

系统是工程助手，不是工程决策权威。最终工程决策仍须经过人工审查。

## 3. 输入

当前已实现：

- 用于 MVP-0 回归的 JSON fixture 输入。
- 用于 MVP-1 真实系统事实的 SysML v2 File Mode。

V1 规划内容：

- 现有 Neo4j Failure Knowledge Base；MVP-2 只读使用。
- 明确导入后作为来源证据的历史 FMEA Excel / CSV。
- FMEA 报告及已审查的失效、测试和维护知识。
- 文档摄取范围确定后的产品设计文档和 Product Design Manual 来源。

长期扩展：

- MBSE 仓库、BOM、PLM 和需求数据库。
- 从文档提取的知识的生命周期及经批准的写回。
- 通过 API / MCP 能力边界接入外部工具。

## 4. 输出

V1 的目标是生成包含以下内容的结构化 Candidate FMEA：

- 分析对象 / 组件；
- 功能 / 需求上下文；
- 失效模式；
- 失效起因；
- 可选的失效机理；
- 局部影响；
- 上一级影响；
- 最终影响；
- 预防控制；
- 探测控制；
- 推荐措施；
- 改进建议；
- 证据和来源追踪；
- 知识来源和分析状态；
- 仅在存在授权规则时提供风险字段。

当前 MVP 的输出范围更小。MVP-1 使用 System / Component / Function / SourceReference 和 fixture 故障知识生成结构化候选输出。它尚不提供基于真实 Neo4j 的故障知识、真实 LLM 生成、人工审查批准或经授权的 AIAG-VDA 风险字段。

## 5. 工作流形态

V1 遵循 AIAG-VDA 七步工作流形态：

1. 策划和准备
2. 结构分析
3. 功能分析
4. 失效分析
5. 风险分析
6. 优化
7. 结果文件化

对于规则尚未实现的步骤，早期 MVP 可以显式输出 `NOT_EVALUATED` 或 `SKIPPED`。

## 6. 自动化边界

Agent 可以自动执行检索、映射、候选生成、证据关联、一致性检查和报告组装。

Agent 不得静默批准工程结果、编造缺失事实、编造 S/O/D/AP 值或覆盖冲突证据。审查和批准仍是明确的工作流边界。

## 7. 证据要求

每个非简单候选项都应保留可追踪的证据。各字段的来源应区分系统事实、检索到的故障知识、推断、候选分析和经人工审查的决策。

证据冲突时，应保留冲突，并在影响重大时升级处理。

## 8. 能力状态

当前已实现：

- MVP-0 可离线运行的纵向切片。
- MVP-1 真实 SysML v2 File Mode 经 `SysMLFactSnapshot` 进入 Canonical System Model 的路径。
- 已实现的 CSM 子集：`System`、`Component`、`Function`、`SourceReference`。
- LangGraph 工作流骨架，风险状态显式为 `NOT_EVALUATED`，优化状态显式为 `SKIPPED`。

V1 规划内容：

- MVP-2 从现有 Neo4j 只读检索真实故障知识。
- MVP-3 通过提供商中立的边界实现以证据为依据的 LLM 生成。
- MVP-4 授权风险策略和语义校验。
- MVP-5 人工审查工作流及未来知识生命周期边界。

长期扩展：

- Canonical System Model 中的 Requirement / Port / Interface / Connection / Flow / State / Allocation。
- 失效传播。
- 航空航天基准扩展。
- MCP 能力层。
- Dynamic FMEA 和经批准的知识写回。

## 9. 非目标

V1 不将 Agent 变成工程决策权威。

V1 不复制专有 AIAG-VDA 评分表或 Action Priority 矩阵。

V1 不将 FMEA 领域模型直接绑定到 SysML、Neo4j、Qdrant、MCP、OpenSysML、LangGraph、LangChain、任何 LLM 提供商或 UI 框架。

V1 不将未经审查的候选项视为已批准结果。

## 10. V1 完成边界

只有当系统能够基于真实工程上下文和真实故障知识生成有证据支撑的 Candidate DFMEA、保留来源追踪、避免无依据的风险值，并将结果交付人工审查时，V1 才算完成。

MVP-2 至 MVP-5 是达到该 V1 边界的最低规划路径。
