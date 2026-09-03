# FMEA Agent 长期开发指导与工程地基文档
## FMEA Agent Foundation & Development Guide for Claude Code

> 文档定位：本文件是 FMEA Agent 项目的长期“地基文档 / 项目宪法 / Claude Code 总体参考文档”之一。  
> 适用对象：Claude Code、项目维护者、后续协作者、实验与评测脚本。  
> 文档版本：v0.1  
> 基线日期：2026-09-03  
> 状态：Living Document（持续演化，但核心原则不得随意漂移）

---

# v0.2 架构冻结补充（Bootstrap Pack v0.1）

> 本节是对原 Foundation Guide 的正式补充。若本节与早期探索性表述冲突，以本节和已接受 ADR 为准。

## A. FMEA 方法基线

`[DECISION]`

首个正式 FMEA Profile 采用：

> **AIAG-VDA FMEA**

系统工作流以七步法为流程骨架：

```text
Planning & Preparation
→ Structure Analysis
→ Function Analysis
→ Failure Analysis
→ Risk Analysis
→ Optimization
→ Results Documentation
```

本项目文档与代码不得复制或臆造受版权/授权约束的评分表和 Action Priority 矩阵。正式 S/O/D/AP 规则仅在获得授权规则来源后实现。

## B. Runnable Vertical Slice First

`[DECISION]`

长期 Phase 路线用于描述能力成熟度；实际编码优先采用短周期 MVP 路线。

第一个可运行版本允许使用：

```text
JSON fixtures
InMemory repositories
Mock/optional LLM
NoOpRiskStrategy
```

先跑通：

```text
Input
→ AIAG-VDA-shaped workflow
→ structured FMEA candidate
→ output
```

再逐项替换：

```text
fixture system facts → OpenSysML / SysML API
fixture failure knowledge → Neo4j / retrieval
mock generation → real LLM
NoOp risk → authorized AIAG-VDA RiskStrategy
basic validation → semantic verification
auto flow → Human Review
```

原则：

> **最小功能，正确边界。**

不要为了“先跑起来”把所有逻辑塞进单文件 Demo。

## C. Phase 1 / Phase 2 边界

`[DECISION]`

Phase 1 输出统一称为：

> **SysMLFactSnapshot**

它是 parser/API 事实快照，不是 Canonical System Model。

```text
SysML
→ Parser/API
→ SysMLFactSnapshot
→ Semantic Mapping
→ Canonical System Model
```

Phase 2 才负责 tool-independent Canonical semantics。

## D. Phase 5 / Phase 6 边界

`[DECISION]`

Phase 5：

```text
evidence retrieval
→ LLM candidate generation
→ basic schema validation
→ candidate output
```

不负责正式 Human Review。

Phase 6：

```text
semantic validation
system-model validation
evidence validation
risk/policy gate
human review
audit
approved/rejected result
```

## E. Risk Strategy

`[DECISION]`

风险逻辑通过可替换策略实现：

```text
RiskStrategy
├─ NoOpRiskStrategy
├─ AIAGVDARiskStrategy
├─ FutureCriticalityStrategy
└─ EnterpriseRiskStrategy
```

MVP-0 允许：

```text
NOT_EVALUATED
```

禁止 LLM 在无规则依据时自由生成 S/O/D/AP。

## F. Capability-first Phase 4

`[DECISION]`

Phase 4 的 MVP 由能力定义，而不是由技术栈数量定义。

第一目标只要求形成稳定能力，例如：

```text
find_failure_modes()
find_similar_cases()
get_evidence()
```

Neo4j、Qdrant、Docling、Ontology、MCP 均按需求增量加入，不要求同时部署。

## G. Dependency Maturity

`[DECISION]`

外部项目除 S/W/D/R 复用分类外，还必须标记：

```text
STABLE
CANDIDATE
EXPERIMENTAL
WIP
DEFERRED
```

文档中出现项目名称不等于其已经获准作为 production dependency。

## H. Evidence Authority and Conflict

`[DECISION]`

事实/证据存在冲突时，不进行静默覆盖。

保存：

```text
source
version
authority
conflict
review status
```

重要冲突进入 Human Review。

---

# 0. 如何使用本文件

本文件的目标不是描述某一次具体实现，而是回答以下长期问题：

1. FMEA Agent **到底要解决什么问题**；
2. 项目 **明确处理什么、不处理什么**；
3. SysML / MBSE、知识图谱、RAG、LLM、LangGraph、MCP 在系统中分别承担什么职责；
4. 哪些信息属于“工程事实”，哪些属于“故障经验”，哪些属于“模型推理”；
5. 如何保证 FMEA 输出具有 **证据、可追溯性、可验证性和人工审核边界**；
6. Claude Code 在本仓库中应如何规划、编码、测试、评审和提交；
7. 如何最大化复用开源项目与前人研究，而不是重复造轮子；
8. 如何逐步把系统做成可以像“积木”一样扩展的工程 Agent。

## 0.1 决策状态标记

本文使用以下四种状态。

### `[DECISION]`
已经形成的长期架构决策。  
除非有新的实验、标准、工程约束证明其明显不合适，否则不得随意修改。

### `[BASELINE]`
当前版本的默认实现基线。  
允许替换，但替换前必须说明原因、影响、迁移方法和验证结果。

### `[HYPOTHESIS]`
研究假设或尚未完全验证的技术判断。  
Claude Code 不得将其描述为已经证实的事实。

### `[DEFERRED]`
已经讨论过，但当前阶段明确不优先实施的能力。

---

# 1. 项目使命

## 1.1 总体目标

`[DECISION]`

FMEA Agent 的目标不是简单地让大语言模型“生成一张 FMEA 表”，而是构建一个：

> **以系统设计事实为约束、以历史故障知识和工程证据为支撑、以结构化 FMEA 流程为骨架、以 Agent 进行工具编排与候选推理、以工程师进行最终确认的智能 FMEA 辅助分析系统。**

长期希望实现：

```text
工程模型 / 设计数据 / 历史经验
            ↓
      可信结构化事实
            ↓
    失效知识检索与推理
            ↓
    FMEA 候选分析与风险评估
            ↓
       自动验证与溯源
            ↓
         Human Review
            ↓
      可审计 FMEA 结果
```

## 1.2 项目不追求什么

`[DECISION]`

本项目当前不以以下目标为核心：

- 不追求“一句话生成完整 FMEA”；
- 不追求完全替代可靠性/FMEA 工程师；
- 不追求让 LLM 自由决定最终风险等级；
- 不追求一次性支持全部 MBSE、CAD、CAE、PLM 文件格式；
- 不追求建立一个与具体模型、具体供应商、具体 LLM 强绑定的单体系统；
- 不以语言流畅度作为主要效果指标；
- 不把模型“自信度”直接当作工程可信度；
- 不让 LLM 凭空构造不存在的系统结构、接口、功能或需求。

---

# 2. 项目的核心工程原则

## 2.1 事实优先于生成

`[DECISION]`

系统应遵循：

```text
工程事实 > 已审核工程知识 > 历史案例 > 检索结果 > LLM 推断
```

对于系统结构、组件、功能、接口、连接、需求、状态、版本等信息：

> **优先从 SysML / MBSE / 结构化设计数据中读取，不允许由 LLM 猜测。**

LLM 的职责是：

- 语义归一化；
- 候选失效生成；
- 文本信息抽取；
- 证据组织；
- 原因/影响候选推理；
- 工具选择；
- 分析解释；
- 缺失信息识别。

LLM 不应直接成为系统事实源。

---

## 2.2 证据链是一等数据对象

`[DECISION]`

任何重要 FMEA 候选结论都应能够回答：

```text
这个结论从哪里来？
依据什么设计事实？
依据哪条历史故障/FMEA/文献/规则？
经过哪些工具和规则？
哪个字段是事实，哪个字段是推断？
是否经过人工确认？
```

因此 Evidence / Provenance 不是备注字段，而应成为核心数据模型之一。

建议所有候选结论至少包含：

```json
{
  "value": "...",
  "status": "candidate",
  "evidence": [],
  "source_model_refs": [],
  "rule_refs": [],
  "generated_by": "...",
  "review_status": "pending"
}
```

---

## 2.3 System Model 与 Failure Model 分离

`[DECISION]`

不要把 SysML 系统模型和 FMEA 失效模型揉成一个巨大的 Schema。

应长期保持：

```text
System Model
    │
    ├─ system
    ├─ subsystem
    ├─ component
    ├─ function
    ├─ interface
    ├─ flow
    ├─ requirement
    ├─ state
    └─ relationship

Failure Model
    │
    ├─ failure mode
    ├─ cause
    ├─ effect
    ├─ propagation
    ├─ control
    ├─ risk
    └─ action
```

二者通过显式映射关联。

这样可以：

- 避免 FMEA Agent 绑定某个 SysML 实现；
- 支持未来接入其他工程数据源；
- 支持不同 FMEA/FMECA 方法；
- 保持数据层清晰；
- 便于独立评测“系统解析”和“失效推理”。

---

## 2.4 固定工作流优先，自治 Agent 后置

`[DECISION]`

第一阶段采用：

> **Workflow-first, Agent-later**

也就是：

```text
先建立确定性 FMEA pipeline
        ↓
再在必要节点引入 LLM
        ↓
再增加条件分支
        ↓
再增加工具自主选择
        ↓
最后才考虑更复杂的多 Agent 协作
```

不要一开始就构建高度自治 Multi-Agent 系统。

FMEA 是安全关键工程分析活动，流程可解释性、状态可控性和审核点比“Agent 自由度”更加重要。

---

# 3. FMEA 领域流程基线

## 3.1 传统 FMEA 主流程

`[BASELINE]`

项目中的 FMEA pipeline 至少应能表达：

```text
1. System / Scope Definition
2. Structure Analysis
3. Function Analysis
4. Failure Mode Identification
5. Failure Cause Analysis
6. Failure Effect Analysis
7. Failure Propagation Analysis
8. Risk Evaluation
9. Current Control / Detection Analysis
10. Recommended Action
11. Verification
12. Human Review
13. Export / Versioning
```

映射为 Agent/模块：

```text
Structure
   ↓
Function
   ↓
Failure Mode
   ↓
Cause
   ↓
Effect
   ↓
Propagation
   ↓
Risk
   ↓
Control / Action
   ↓
Verification
   ↓
Human Review
```

## 3.2 Agent 最适合替代/辅助的环节

### 高适合度

- 文档解析；
- FMEA 历史案例检索；
- 术语归一；
- 功能候选抽取；
- 失效模式候选生成；
- 原因候选检索；
- 局部影响/上层影响候选生成；
- 相似案例匹配；
- 规则检查；
- FMEA 表格结构化；
- 证据组织；
- 版本差异分析；
- 报告生成。

### 中等适合度

- Failure Cause 推理；
- Failure Effect 推理；
- Failure Propagation 推理；
- Detection Control 建议；
- Recommended Action 建议；
- S/O/D 或 AP 建议。

这些能力必须有模型、知识、规则或人工校验约束。

### 不应完全自动决定

- 最终严重度确认；
- 最终风险优先级；
- 安全关键结论；
- 新型高风险失效的最终确认；
- 工程措施批准；
- 最终 FMEA 发布。

---

# 4. 应用边界

## 4.1 第一层：V1 必须支持

`[DECISION]`

### 系统设计事实

优先支持：

- SysML v2；
- SysML v2 文件；
- SysML Repository / Systems Modeling API；
- 系统层级；
- Component / Part；
- Function / Action；
- Requirement；
- Port；
- Interface；
- Connection；
- Flow；
- State；
- Allocation；
- Containment。

### FMEA / 故障知识

支持：

- 历史 FMEA 表格；
- 已审核 FMEA 条目；
- 故障报告；
- 维修记录；
- 技术文档；
- 论文；
- 标准/规则；
- 典型失效模式库；
- 专家规则；
- 人工构建 benchmark / Ground Truth。

### 输出

V1 目标输出：

- 结构化 System Model；
- 结构化 Failure Model；
- FMEA Candidate；
- Evidence；
- FMEA Table；
- Verification Report；
- Human Review Status。

---

## 4.2 第二层：后续阶段支持

`[DEFERRED]`

未来可以逐步接入：

- PLM/PDM；
- BOM；
- Requirements Database；
- 故障树 FTA；
- 扩展故障树；
- PHM 数据；
- 试验数据；
- 遥测数据；
- 时序故障数据；
- 数字孪生；
- Simulink；
- Capella；
- SysML v1；
- 企业知识库；
- 维修保障数据；
- 设计变更增量分析。

这些能力必须通过 Adapter / Tool / MCP 等边界接入，避免破坏核心领域模型。

---

## 4.3 当前明确不优先支持

`[DEFERRED]`

除非新的科研需求明确证明必要，否则当前不优先：

- CATIA 原生零件/装配深度解析；
- STEP 全量几何解析；
- CAD 几何推理；
- CAE 原始模型；
- 大型 Cameo `.mdzip` 私有工程；
- 全量 Simulink；
- 全量数字孪生；
- 所有 SysML 元模型元素；
- 所有 PLM 系统；
- 企业级多租户产品化。

原则：

> **先证明“系统语义 → FMEA”链路，再扩展输入格式。**

---

# 5. 数据源分层与权威性

## 5.1 Layer A：System Facts

权威来源：

```text
SysML / MBSE
BOM
Requirements
PLM
Structured Design Data
```

负责：

- What exists?
- How are components connected?
- What function is allocated where?
- What is the system hierarchy?
- What are the interfaces and flows?
- What requirements constrain the design?
- What is the model version?

---

## 5.2 Layer B：Failure Knowledge

来源：

```text
Historical FMEA
Failure Reports
Maintenance Records
Reliability Databases
Papers
Standards
Expert Rules
Test Data
```

负责：

- What usually fails?
- Why?
- What effects have occurred?
- Which failure mechanisms are known?
- Which controls are commonly used?
- What evidence supports a candidate?

---

## 5.3 Layer C：Reasoning

来源：

```text
Rules
Graph Traversal
Retrieval
LLM
Agent
```

负责：

- 候选映射；
- 相似案例匹配；
- Cause → Mode → Effect 推理；
- 跨层级失效传播；
- 证据综合；
- 缺失信息识别；
- 风险建议。

---

## 5.4 Layer D：Human Decision

负责：

- 审核边界；
- 确认关键失效；
- 确认风险；
- 确认措施；
- 接受/修改/拒绝候选；
- 形成正式版本。

---

# 6. 总体目标架构

`[BASELINE]`

```text
                           ┌──────────────────────┐
                           │        User          │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │   FMEA Orchestrator  │
                           │      LangGraph       │
                           └──────────┬───────────┘
                                      │
          ┌───────────────────────────┼──────────────────────────┐
          │                           │                          │
          ▼                           ▼                          ▼
┌───────────────────┐     ┌────────────────────┐      ┌───────────────────┐
│ System Model Tool │     │ Failure Knowledge  │      │ Document/RAG Tool │
│ SysML / MBSE      │     │ KG / Rules / Cases │      │ Text Evidence     │
└─────────┬─────────┘     └──────────┬─────────┘      └─────────┬─────────┘
          │                           │                          │
          ▼                           ▼                          ▼
┌───────────────────┐     ┌────────────────────┐      ┌───────────────────┐
│ Canonical System  │     │   Failure Model    │      │ Vector / Corpus   │
│      Model        │     │      Neo4j         │      │      Store        │
└─────────┬─────────┘     └──────────┬─────────┘      └─────────┬─────────┘
          │                           │                          │
          └───────────────────────────┼──────────────────────────┘
                                      ▼
                          ┌────────────────────────┐
                          │ Structured FMEA State  │
                          └────────────┬───────────┘
                                       │
                 ┌─────────────────────┼──────────────────────┐
                 ▼                     ▼                      ▼
             Failure               Risk                  Verification
             Analysis              Analysis              / Evidence
                 └─────────────────────┼──────────────────────┘
                                       ▼
                             ┌────────────────────┐
                             │    Human Review    │
                             └──────────┬─────────┘
                                        ▼
                             ┌────────────────────┐
                             │ Versioned Outputs  │
                             └────────────────────┘
```

---

# 7. Canonical System Model

## 7.1 目的

`[DECISION]`

Canonical System Model 的核心目标是：

> **让 FMEA Agent 不依赖任何一种 SysML parser、Repository 或 MBSE 软件。**

底层可变化：

```text
OpenSysML
Systems Modeling API
Capella
Future PLM
Other MBSE
```

上层 Agent 看到的接口保持稳定。

---

## 7.2 第一阶段核心实体

建议至少：

```text
System
Subsystem
Component
Function
Requirement
Port
Interface
Connection
Flow
State
Allocation
Relationship
SourceReference
```

示例：

```json
{
  "id": "component-id",
  "name": "HydraulicPump",
  "kind": "component",
  "parent_id": "hydraulic-system",
  "functions": ["provide-pressure"],
  "ports": ["inlet", "outlet"],
  "requirements": [],
  "source": {
    "source_type": "sysml",
    "repository": "...",
    "element_id": "...",
    "version": "..."
  }
}
```

---

## 7.3 必须具备的性质

Canonical Model 应：

- typed；
- versioned；
- source-traceable；
- parser-independent；
- serialization-friendly；
- deterministic；
- testable；
- stable ID；
- 支持 partial model；
- 支持 validation。

推荐采用：

`[BASELINE]`

- Python Pydantic；
- JSON Schema；
- JSON 序列化；
- 显式枚举；
- 显式 SourceReference。

---

# 8. SysML / MBSE 技术路线

## 8.1 File Mode

`[DECISION]`

```text
.sysml
   ↓
Parser / OpenSysML
   ↓
SysML Adapter
   ↓
Canonical System Model
```

主要用于：

- 离线研究；
- Benchmark；
- 数据集；
- 单文件实验；
- 论文验证；
- CI fixture。

---

## 8.2 Repository Mode

`[DECISION]`

```text
SysML Repository
      ↓
Systems Modeling API
      ↓
Repository Adapter
      ↓
Canonical System Model
```

主要用于：

- 工程模型；
- 多项目；
- branch / commit；
- model version；
- 在线查询；
- 设计变更分析。

---

## 8.3 Agent Tool Mode

`[DECISION]`

```text
LangGraph / Claude / Other Agent
              ↓
         Tool / MCP
              ↓
          SysMLTool
              ↓
     File / Repository Adapter
```

必须明确：

> **MCP 属于 Agent 接口层，不属于 SysML 解析层。**

不要让 MCP Server 承担 Canonical Model 的核心领域职责。

---

## 8.4 SysMLTool 接口基线

第一阶段建议暴露：

```python
get_systems()
get_subsystems(system_id)
get_components(system_id)
get_component(component_id)
get_functions(element_id)
get_requirements(element_id)
get_ports(element_id)
get_interfaces(element_id)
get_connections(element_id)
get_flows(element_id)
get_states(element_id)
get_allocations(element_id)
get_parent(element_id)
get_children(element_id)
```

未来：

```python
get_function_chain()
get_requirement_trace()
get_system_hierarchy()
get_failure_propagation_candidates()
```

第二组属于更高层语义服务，不应与基础 parser 一起仓促实现。

---

# 9. SysML → FMEA 语义映射

`[HYPOTHESIS]`

初始映射：

| SysML | FMEA | 当前解释 |
|---|---|---|
| Part Definition | Item Type | 系统/设备类型 |
| Part Usage | FMEA Item | 实际对象 |
| Action / Function | Function | FMEA 功能 |
| Port | Interface Point | 接口点 |
| Interface | Interface | 系统接口 |
| Connection | Connection | 传播基础 |
| Flow | Material/Energy/Information Flow | 传播路径 |
| Requirement | Requirement / Effect Constraint | 后果与严重度参考 |
| State | Operating / Failure State | 状态相关分析 |
| Allocation | Function-to-Component | 功能分配 |
| Containment | System Hierarchy | Local / Next / End Effect 层次 |

注意：

> 此映射必须通过真实 SysML v2 元模型和实例逐项验证。

每条映射建议记录：

```text
Confirmed
Tentative
Needs Research
Rejected
```

禁止 Claude Code 将 Tentative 直接写成领域事实。

---

# 10. Failure Model

## 10.1 第一阶段实体

```text
FailureMode
FailureCause
FailureEffect
FailureMechanism
FailurePropagation
Control
DetectionMethod
RiskAssessment
RecommendedAction
Evidence
ReviewDecision
```

---

## 10.2 Effect 层级

FMEA 输出至少应区分：

```text
Local Effect
Next Higher Level Effect
End Effect
```

而不是只生成一个模糊的 `effect` 文本。

---

## 10.3 Cause / Mode / Effect 不得混淆

必须尽量通过 Schema、Prompt、Validation 防止：

```text
Cause 被写成 Failure Mode
Failure Mode 被写成 Effect
Effect 被写成 Cause
```

这类语义边界问题是 FMEA 自动化评测的重要部分。

---

# 11. 知识图谱与 RAG

## 11.1 双知识底座

`[DECISION]`

不要把所有数据都做 embedding，也不要所有问题都通过 LLM。

推荐：

```text
Structured Knowledge
      │
      ├─ Neo4j / Graph
      ├─ Ontology
      ├─ Rules
      └─ Structured FMEA

Unstructured Knowledge
      │
      ├─ Papers
      ├─ Reports
      ├─ Maintenance Text
      ├─ Manuals
      └─ Historical Documents
```

---

## 11.2 查询策略

`[DECISION]`

如果问题是：

- 某组件连接哪些组件？
- 某功能分配给哪个部件？
- 某 Failure Mode 已知有哪些 Cause？
- 某条传播路径是什么？

优先：

```text
Cypher / graph traversal / structured query
```

如果问题是：

- 有没有相似历史案例？
- 哪篇论文描述了类似故障？
- 某维修报告有没有相关描述？

优先：

```text
Vector Retrieval / Text Retrieval
```

最后才由 LLM 综合。

---

## 11.3 KG-RAG 推荐顺序

```text
Query
  ↓
Entity Resolution
  ↓
Structured KG Retrieval
  ↓
Semantic Retrieval
  ↓
Evidence Merge / Rerank
  ↓
Context Construction
  ↓
LLM Reasoning
  ↓
Validation
```

---

## 11.4 Neo4j 定位

`[BASELINE]`

Neo4j 作为当前 Knowledge Graph 主存储候选。

但 Domain Model 不应直接依赖 Neo4j Driver。

应通过：

```text
KnowledgeRepository
FailureKnowledgeTool
GraphAdapter
```

等接口隔离。

这样未来可以替换：

- RDF/SPARQL；
- 其他 Graph DB；
- 内存图；
- 测试 fake repository。

---

# 12. 本体 Ontology 的定位

本体负责：

- 统一术语；
- 定义实体类型；
- 定义关系语义；
- 约束 Cause–Mode–Effect；
- 对齐不同来源；
- 支持一致性校验；
- 为 KG 提供 schema。

Ontology 不应：

- 承担全部推理；
- 被做成极度复杂且难维护的“大而全本体”；
- 在没有案例验证时持续扩张。

优先：

> Minimum Useful Ontology。

---

# 13. Agent 架构

## 13.1 Main Orchestrator

`[BASELINE]`

LangGraph 作为主要状态化编排层。

负责：

- Workflow；
- State；
- Node；
- Edge；
- Conditional routing；
- Checkpoint；
- Human-in-the-loop；
- Tool orchestration；
- retry；
- execution trace。

---

## 13.2 LangChain 的定位

`[DECISION]`

LangChain 不作为项目的总体架构核心。

它主要作为：

- model adapter；
- retriever adapter；
- prompt/tool integration；
- ecosystem compatibility layer。

原则：

```text
LangGraph = orchestration core
LangChain = compatibility / component layer
```

尽量避免业务领域模型直接依赖 LangChain 类型。

---

## 13.3 Agent/Node 职责

### Document Agent

负责：

- 文档解析；
- chunk；
- metadata；
- evidence extraction；
- terminology normalization。

不负责：

- 决定系统结构真相；
- 最终 FMEA 判断。

---

### Structure Agent

输入：

```text
SysML / Canonical System Model / BOM
```

输出：

```text
system boundary
hierarchy
components
interfaces
connections
version
```

---

### Function Agent

负责：

- 功能清单；
- function-to-component allocation；
- function chain；
- requirement trace；
- 术语归一。

---

### Failure Analysis Agent

负责：

- Failure Mode Candidate；
- Cause Candidate；
- Effect Candidate；
- Failure Propagation Candidate；
- Evidence。

必须尽可能使用：

```text
System Facts
+
Failure Knowledge
+
Rules
```

而不是只依赖 LLM prior。

---

### Risk Agent

负责：

- S/O/D 输入收集；
- 规则匹配；
- 评分建议；
- AP/RPN 计算；
- 风险解释；
- 缺失数据提示。

Risk Agent 不拥有最终工程裁决权。

---

### Verification Agent

负责：

- Schema validation；
- Cause–Mode–Effect consistency；
- Evidence completeness；
- graph consistency；
- model version consistency；
- duplicate detection；
- unsupported claim detection；
- missing field detection。

---

### Human Review

Human Review 不是 UI 附属功能，而是正式 pipeline node。

至少支持：

```text
Accept
Modify
Reject
Request Evidence
Mark Unknown
Escalate
```

---

# 14. MCP 的长期定位

## 14.1 MCP 是能力接口，不是业务核心

`[DECISION]`

MCP 用于把外部能力包装成 Agent 可发现、可调用的工具，例如：

```text
SysML Repository
PLM
Neo4j service
Enterprise FMEA Database
Literature service
Simulation service
External Agent
```

MCP 不应该侵入：

```text
domain/
canonical models/
FMEA schemas/
core reasoning rules/
```

---

## 14.2 什么时候使用 MCP

优先使用 MCP：

- 外部服务；
- 远程数据；
- 可独立部署工具；
- 其他团队维护能力；
- 需要统一 tool protocol 的能力；
- 希望被 Claude Code / LangGraph / 其他 Agent 复用的服务。

不必 MCP 化：

- 本地纯 Python 函数；
- pytest；
- ruff；
- Git；
- 普通文件操作；
- 已有成熟 CLI 的简单能力。

---

# 15. 数据契约

## 15.1 所有跨模块数据都应结构化

`[DECISION]`

模块间不要长期传递“大段 prompt 文本”。

优先：

- Pydantic；
- dataclass；
- JSON；
- JSON Schema；
- TypedDict；
- Enum。

---

## 15.2 推荐核心对象

```text
SystemModel
Component
Function
Requirement
Interface
Flow

FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
FailurePropagationCandidate

Evidence
SourceReference
RiskAssessment
ReviewStatus
VerificationIssue
```

---

## 15.3 Evidence 推荐字段

```json
{
  "id": "...",
  "source_type": "sysml|fmea|paper|report|rule|expert",
  "source_id": "...",
  "source_version": "...",
  "locator": "...",
  "excerpt": "...",
  "supports": ["candidate-id"],
  "authority": "...",
  "reviewed": false
}
```

---

# 16. 风险评分原则

## 16.1 RPN / S-O-D

系统可以：

- 读取 S/O/D；
- 验证范围；
- 计算 RPN；
- 显示评分依据；
- 对照规则；
- 提出建议值。

系统不能：

> 在没有规则、数据、统计或人工依据时把 LLM 生成的数字包装成确定性工程评分。

---

## 16.2 未来 AP

应保持 Risk Model 可扩展，未来支持：

- RPN；
- AIAG-VDA Action Priority；
- criticality；
- 自定义企业评分。

不要把所有风险算法硬编码进 Agent Prompt。

---

# 17. Benchmark 与 Ground Truth

`[DECISION]`

FMEA Agent 必须建立独立 benchmark。

如果没有 benchmark，项目会逐渐变成：

> 功能越来越多，但无法证明效果变好。

---

## 17.1 Benchmark 分层

```text
Level 0
SysML Semantic Unit Tests

Level 1
OMG Simple Vehicle

Level 2
Delivery Drone

Level 3
CubeSat / Spacecraft

Level 4
Large / Heterogeneous System
```

### Level 0

目标：

> 验证 parser / adapter 对 Part、Action、Requirement、Interface、Flow、State 等基本语义的正确性。

### Level 1

目标：

> 第一套端到端系统级 FMEA benchmark。

### Level 2

目标：

> 验证跨层级组件、接口、功能、需求和传播。

### Level 3

目标：

> 航空航天领域验证。

### Level 4

目标：

> 可扩展性和复杂模型验证。

---

## 17.2 Ground Truth

SysML 模型通常没有天然 FMEA Ground Truth。

因此需逐渐建立：

```text
Source Model
+
Human Verified FMEA
+
Evidence
```

示例：

```json
{
  "item": "HydraulicPump",
  "function": "ProvideHydraulicPressure",
  "failure_mode": "LossOfPressure",
  "cause": "PumpMechanicalFailure",
  "local_effect": "NoHydraulicPressureAtOutlet",
  "next_level_effect": "ActuatorCannotGenerateForce",
  "end_effect": "LandingGearFailsToRetract",
  "evidence": [],
  "review_status": "human_verified"
}
```

---

# 18. 评测体系

## 18.1 System Extraction

```text
Component Extraction Accuracy
Function Extraction Accuracy
Requirement Extraction Accuracy
Interface Extraction Accuracy
Relationship Accuracy
Traceability Accuracy
```

---

## 18.2 Retrieval

```text
Recall@K
Precision@K
MRR
Evidence Coverage
Source Accuracy
```

---

## 18.3 FMEA

```text
Failure Mode Precision
Failure Mode Recall
Failure Cause Accuracy
Failure Effect Accuracy
Cause–Mode–Effect Consistency
Propagation Path Accuracy
Unsupported Claim Rate
```

---

## 18.4 Human Collaboration

```text
Accept Rate
Modify Rate
Reject Rate
Review Time
Evidence Request Rate
Expert Agreement
```

---

## 18.5 Dynamic Update

未来：

```text
Affected-item Recall
Affected-item Precision
Update Omission Rate
Version Trace Completeness
```

---

# 19. 推荐代码架构

`[BASELINE]`

```text
fmea-agent/
│
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── PROGRESS.md
│
├── docs/
│   ├── foundation/
│   │   └── FMEA_AGENT_FOUNDATION_GUIDE.md
│   │
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── data-flow.md
│   │   ├── agent-architecture.md
│   │   ├── mcp-architecture.md
│   │   └── canonical-model.md
│   │
│   ├── specs/
│   ├── plans/
│   ├── adr/
│   ├── research/
│   └── experiments/
│
├── src/
│   └── fmea_agent/
│       ├── domain/
│       │   ├── system_model/
│       │   ├── failure_model/
│       │   ├── risk/
│       │   └── evidence/
│       │
│       ├── ingestion/
│       │   ├── sysml/
│       │   ├── fmea/
│       │   └── documents/
│       │
│       ├── knowledge/
│       │   ├── graph/
│       │   ├── ontology/
│       │   ├── retrieval/
│       │   └── rules/
│       │
│       ├── agents/
│       │   ├── graph.py
│       │   ├── state.py
│       │   └── nodes/
│       │
│       ├── tools/
│       ├── mcp/
│       ├── evaluation/
│       ├── application/
│       └── api/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   ├── contract/
│   └── benchmark/
│
├── benchmarks/
│   ├── level_0_sysml/
│   ├── level_1_vehicle/
│   ├── level_2_drone/
│   ├── level_3_spacecraft/
│   └── ground_truth/
│
├── examples/
├── scripts/
│   └── verify.sh
│
├── vendor/
│   └── README.md
│
└── .claude/
    ├── settings.json
    ├── rules/
    ├── skills/
    └── agents/
```

---

# 20. 模块依赖原则

建议依赖方向：

```text
domain
  ↑
application
  ↑
tools / adapters
  ↑
agents / api
```

核心规则：

- `domain` 不依赖 LangGraph；
- `domain` 不依赖 LangChain；
- `domain` 不依赖 Neo4j；
- `domain` 不依赖特定 LLM；
- `domain` 不依赖 MCP；
- Agent Node 不应直接包含大量业务规则；
- Prompt 不应该成为唯一业务逻辑；
- Adapter 负责第三方格式；
- Repository 负责存储访问；
- Tool 负责 Agent 可调用接口。

---

# 21. 第三方项目复用原则

## 21.1 总原则

`[DECISION]`

本项目的长期目标之一是：

> **最大限度复用前人研究和开源成果，并保持对外部成果的兼容性。**

因此：

> Search / Inspect / Run / Compare / Wrap / Adapt  
> 优先于  
> Rewrite / Rebuild.

---

## 21.2 SysML 优先研究仓库

当前重点：

```text
Systems-Modeling/SysML-v2-Release
Systems-Modeling/SysML-v2-API-Services
Systems-Modeling/SysML-v2-API-Cookbook
MBSE4U/sysmod-sysmlv2
MBSE4U/sysmod-sysmlv2-api-mcp
Open-MBEE/OpenSysML
Open-MBEE/SysML-v2-Applications-and-Examples
```

后期：

```text
Open-MBEE/TMT-SysML-Model
Capella-related models
```

---

## 21.3 FMEA / Agent 参考项目

已调研或运行过的方向包括：

```text
LLMRiskAnalyzer
iso26262-agent
kg-rag-fmea
fmea-risk-analyzer
smolagents experiments
BERT + FastAPI extraction experiments
```

这些项目主要用于：

- 学习已有工作；
- 复用组件；
- 对比架构；
- 提取 benchmark idea；
- 避免重复实现。

不得因为某个 Demo 能运行就直接把其架构提升为本项目长期架构。

---

## 21.4 第三方仓库管理

建议：

```text
vendor/
external/
research_repos/
```

第三方仓库：

- 保持原 Git 历史；
- 不直接魔改；
- 记录 commit hash；
- 记录 license；
- 记录适用范围；
- 通过 Adapter 或独立实验调用；
- 自己的核心代码不要写进第三方 repo。

---

# 22. 技术栈基线

## 22.1 编程语言

`[BASELINE]`

主要语言：

```text
Python
```

原因：

- AI/LLM ecosystem；
- LangGraph；
- Pydantic；
- Neo4j；
- NLP；
- scientific evaluation；
- SysML 工具整合成本较低。

---

## 22.2 Agent Orchestration

```text
LangGraph
```

作为主编排。

---

## 22.3 Ecosystem Adapter

```text
LangChain
```

只在真正需要时使用。

---

## 22.4 Data Contract

```text
Pydantic
JSON Schema
Typed Python
```

---

## 22.5 Knowledge Graph

```text
Neo4j
```

当前基线。

---

## 22.6 Ontology

可使用：

```text
OWL
RDF
Protégé
n10s
```

但 Ontology 与 Neo4j 具体实现不应侵入 Domain。

---

## 22.7 Local LLM / Embedding

本地实验可以复用：

```text
Ollama
local embedding models
local LLM
```

但 LLM Provider 必须做接口隔离。

---

# 23. 当前开发环境参考

`[BASELINE]`

当前主要本地环境：

```text
Windows 11
WSL2 Ubuntu
VS Code
Claude Code
Conda
Python
Neo4j 5.26.x
n10s
Protégé
Java 17
Node.js 22
Ollama
```

硬件：

```text
CPU: Ryzen 7 9800X3D
GPU: RTX 5080
```

设计时应默认：

- 支持 Windows + WSL2 开发；
- 路径不要硬编码；
- shell script 与 Python script 尽量可复现；
- GPU 不是所有测试的强依赖；
- CI / unit tests 应尽量 CPU 可运行。

---

# 24. Claude Code 开发总流程

`[DECISION]`

非 trivial 任务必须遵循：

```text
Requirement
    ↓
Explore
    ↓
Spec
    ↓
Plan
    ↓
Branch / Worktree
    ↓
Tests
    ↓
Implementation
    ↓
Verification
    ↓
Review
    ↓
Commit
    ↓
Progress Handoff
```

---

# 25. Claude Code 每次开始任务的读取顺序

建议 Claude Code 首先阅读：

```text
1. CLAUDE.md
2. docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md
3. PROGRESS.md
4. relevant spec
5. relevant ADR
6. git log --oneline -10
7. current implementation
8. relevant tests
```

然后才提出实现方案。

---

# 26. Explore 阶段

复杂任务开始时：

> **不要立即编码。**

Claude Code 应：

1. 定位相关模块；
2. 阅读接口；
3. 阅读测试；
4. 查找是否已有类似实现；
5. 查找 third-party dependency；
6. 识别 architecture impact；
7. 列出 unknowns；
8. 判断是否需要新 ADR；
9. 给出最小实现路径。

---

# 27. Spec 阶段

对于非 trivial feature 创建：

```text
docs/specs/<feature>.md
```

建议结构：

```markdown
# Background
# Goal
# Non-goals
# Inputs
# Outputs
# Domain Model
# Interfaces
# Architecture Impact
# Error Handling
# Evidence / Traceability
# Test Cases
# Acceptance Criteria
# Open Questions
```

Spec 是 Feature 的需求真源。

---

# 28. Plan 阶段

创建：

```text
docs/plans/<feature>-plan.md
```

每个 Task 应包括：

```text
Goal
Files
Interfaces
Tests
Implementation Steps
Verification
Completion Criteria
```

Task 应足够小：

> 一个 task 最好形成一个独立测试闭环。

---

# 29. 测试驱动开发

`[DECISION]`

关键业务逻辑优先采用：

```text
RED
 ↓
GREEN
 ↓
REFACTOR
```

至少需要：

### Unit Test

验证：

- domain；
- parsing；
- validation；
- risk calculation；
- mapping；
- pure functions。

### Integration Test

验证：

- SysML adapter；
- Neo4j；
- RAG；
- Agent Tool；
- Repository。

### Regression Test

防止：

- Prompt 修改导致历史 benchmark 退化；
- parser upgrade 破坏旧模型；
- model change 引起结果漂移。

### Contract Test

验证：

- MCP；
- SysML Tool；
- external API；
- data schema。

### Benchmark Test

验证最终 FMEA 能力。

---

# 30. Verification

Claude Code 不得用：

> “代码看起来正确”

作为完成依据。

推荐：

```bash
pytest
ruff check .
mypy src
```

未来可增加：

```text
coverage
benchmark
contract tests
integration tests
schema validation
```

创建：

```text
scripts/verify.sh
```

把项目完成标准自动化。

---

# 31. Definition of Done

一个 Feature 只有满足以下条件才算完成：

```text
[ ] Spec 已明确
[ ] Architecture boundary 正确
[ ] Data contract 明确
[ ] Tests 已加入
[ ] Tests pass
[ ] Lint pass
[ ] Type check pass
[ ] No unrelated modifications
[ ] Evidence / traceability preserved
[ ] Documentation updated
[ ] PROGRESS.md updated
[ ] Relevant benchmark no regression
[ ] Human review required points preserved
```

Claude Code 不得在验证失败时声称：

> Done / Complete / Fully Implemented。

---

# 32. Git 工作流

推荐：

```text
main
  │
  ├── feature/sysml-parser
  ├── feature/canonical-model
  ├── feature/failure-kg
  └── experiment/kg-rag
```

复杂独立任务优先使用 Git Worktree。

---

## 32.1 Commit 原则

- 一个 commit 一个清晰意图；
- 不混入 unrelated formatting；
- commit 前运行验证；
- 大重构拆阶段；
- 实验和生产代码分开；
- 不修改第三方 Git 历史。

建议：

```text
feat:
fix:
test:
refactor:
docs:
experiment:
chore:
```

---

# 33. PROGRESS.md

`[DECISION]`

长期项目必须维护：

```text
PROGRESS.md
```

至少包含：

```markdown
# Current Milestone
# Done
# In Progress
# Next
# Blockers
# Technical Debt
# Open Research Questions
# Recent Decisions
# Benchmark Status
```

作用：

- 跨 Claude Code Session 传递状态；
- 防止 Context Reset 后重复劳动；
- 明确当前阶段；
- 记录尚未完成问题。

---

# 34. ADR

重要架构选择必须记录：

```text
docs/adr/
```

例如：

```text
001-langgraph-as-orchestrator.md
002-canonical-system-model.md
003-neo4j-knowledge-layer.md
004-mcp-boundary.md
005-sysml-dual-input-mode.md
```

ADR 建议：

```text
Context
Decision
Alternatives
Consequences
Status
Evidence
```

---

# 35. Claude Code Rules

建议：

```text
.claude/rules/
```

例如：

```text
python.md
testing.md
architecture.md
fmea-domain.md
sysml.md
langgraph.md
mcp.md
knowledge-graph.md
research.md
```

不要把所有规则塞入 CLAUDE.md。

---

# 36. Claude Code Skills

当某类操作重复出现时，才固化为 Skill。

推荐未来建立：

```text
add-fmea-tool
add-agent-node
add-sysml-adapter
add-mcp-tool
add-benchmark-case
run-fmea-evaluation
review-fmea-schema
```

Skill 应描述：

```text
Input
Process
Files
Tests
Validation
Output
```

---

# 37. Claude Code Subagents

不要一开始建立十几个 subagent。

成熟后优先：

## Architecture Reviewer

检查：

- layer violation；
- coupling；
- dependency direction；
- external framework leakage；
- extensibility。

## Test Reviewer

检查：

- missing tests；
- edge cases；
- mock quality；
- flaky tests；
- regression。

## FMEA Domain Reviewer

检查：

- Cause / Mode / Effect；
- Function mapping；
- Effect hierarchy；
- risk logic；
- evidence；
- human boundary。

## Code Reviewer

检查：

- Python quality；
- typing；
- exception；
- duplication；
- maintainability。

---

# 38. Hooks

Hooks 用于：

> 必须发生的工程纪律。

例如：

```text
Stop
→ scripts/verify.sh
```

不要用 Hook 承担复杂领域推理。

适合：

- formatting；
- validation；
- testing；
- forbidden path；
- secret detection；
- generated-file check。

---

# 39. Research 与 Production 分离

`[DECISION]`

科研探索代码不要直接污染核心。

推荐：

```text
experiments/
research/
notebooks/
```

当实验验证有效后：

```text
experiment
   ↓
benchmark
   ↓
architecture decision
   ↓
production implementation
```

---

# 40. 实验方法

任何重要 AI 架构改动建议定义实验：

```text
Hypothesis
Baseline
Variant
Dataset
Metrics
Results
Conclusion
Decision
```

例如：

```text
Hypothesis:
Adding SysML structure improves FMEA effect consistency.

Baseline:
LLM only

Variant A:
LLM + RAG

Variant B:
LLM + SysML

Variant C:
LLM + SysML + KG
```

然后比较：

```text
Failure Mode Recall
Cause Accuracy
Effect Accuracy
Propagation Accuracy
Unsupported Claim Rate
Review Time
```

---

# 41. 不允许只凭主观感觉判断效果

禁止：

```text
“这个回答看起来更智能”
“结果感觉不错”
“LLM 应该理解了”
```

应尽量使用：

```text
Ground Truth
Metrics
Expert Review
Regression Test
Evidence Coverage
```

---

# 42. 当前推荐研究路线

`[BASELINE]`

```text
Phase 0
Architecture / repository research

Phase 1
SysML semantic access

Phase 2
Canonical System Model

Phase 3
SysMLTool

Phase 4
Simple Vehicle benchmark

Phase 5
Failure Knowledge / KG / RAG

Phase 6
Structured FMEA workflow

Phase 7
Failure propagation

Phase 8
Risk + Verification + Human Review

Phase 9
LangGraph Agent orchestration

Phase 10
MCP external capability integration

Phase 11
Aerospace benchmark

Phase 12
Dynamic FMEA / design-change analysis
```

注意：

> 实际 Roadmap 可根据实验结果调整，不机械遵循阶段编号。

---

# 43. 当前第一个 SysML 技术验证原则

`[DECISION]`

不要一开始让 LLM 生成 Failure Mode。

优先完成：

```text
SysML
  ↓
System
Component
Function
Port
Interface
Connection
Requirement
  ↓
Normalized JSON
  ↓
Human Verification
```

只有事实提取稳定后，再增加：

```text
Function
  ↓
Failure Mode Candidate
```

---

# 44. 设计变更与 Dynamic FMEA

`[DEFERRED]`

长期值得研究：

```text
Model Version N
       ↓
      Diff
       ↓
Affected System Elements
       ↓
Affected FMEA Entries
       ↓
Incremental Re-analysis
```

这将是 MBSE + FMEA Agent 相比“静态 FMEA 表生成器”的重要研究价值。

但应在 V1 稳定后实现。

---

# 45. 可解释性原则

输出不能只显示：

```text
Pump Failure
→ Landing Gear Failure
```

应尽可能显示：

```text
Pump
  └─ provides Pressure
       ↓
Hydraulic Line
  └─ supplies Actuator
       ↓
Actuator
  └─ provides Retraction Force
       ↓
Landing Gear
```

并关联：

```text
SysML elements
Failure knowledge
Historical case
Rules
```

---

# 46. 工程置信度

不要直接使用 LLM token probability。

未来可以研究 Evidence Confidence，例如基于：

```text
Source Authority
Evidence Coverage
Relationship Consistency
Multi-source Agreement
```

它表示：

> 证据完整程度。

不等于：

> Failure Probability。

---

# 47. 错误处理原则

工程系统中禁止静默失败。

应区分：

```text
ParseError
ModelValidationError
ExternalServiceError
KnowledgeNotFound
EvidenceInsufficient
UnsupportedModelElement
RiskDataMissing
HumanReviewRequired
```

不要统一：

```python
except Exception:
    return None
```

---

# 48. Observability

未来每次 Agent Run 应可记录：

```text
run_id
model_version
input_version
graph_version
tools_called
retrieval_queries
retrieved_evidence
LLM model
prompt/version
validation issues
human decisions
final output
```

用于：

- reproducibility；
- debugging；
- experiment comparison；
- audit。

---

# 49. LLM Provider 解耦

`[DECISION]`

不要在领域代码中直接：

```python
from openai import ...
```

或：

```python
from anthropic import ...
```

然后散布调用。

应该提供抽象层：

```text
LLMClient
EmbeddingClient
Reranker
```

这样可以：

- Claude；
- OpenAI；
- local Ollama；
- other providers；
- mocked test models。

---

# 50. Prompt 管理

Prompt 应：

- versioned；
- testable；
- centralized；
- associated with schema；
- benchmarked。

不要在很多 node 内散落几十段难以追踪的字符串。

建议：

```text
prompts/
```

或由 typed prompt registry 管理。

---

# 51. 安全与数据治理

未来面向真实航空航天数据时：

- 数据来源必须有访问边界；
- 记录 source；
- 不把敏感工程数据自动上传到未知服务；
- 本地模型/私有部署应保留兼容能力；
- 不将真实企业数据混入公开 benchmark；
- 日志中避免泄露敏感内容；
- 第三方 API 使用必须明确数据流向。

---

# 52. 文档体系

推荐：

```text
README
→ 项目入口

FOUNDATION
→ 长期原则

SPEC
→ 某功能要做什么

PLAN
→ 某功能怎么做

ADR
→ 为什么这么设计

PROGRESS
→ 当前做到哪里

RESEARCH NOTES
→ 尚未确定的研究问题

EXPERIMENT
→ 实验与结果

API DOC
→ 如何调用
```

不要用 README 承载全部知识。

---

# 53. 文档真源优先级

发生冲突时建议：

```text
Current Spec
    ↓
Accepted ADR
    ↓
Foundation Guide
    ↓
Current Code + Tests
    ↓
PROGRESS
    ↓
Research Notes
    ↓
Old Conversation / Old Prompt
```

如果 Spec 与 Foundation 冲突：

> Claude Code 应停止扩大实现，并明确指出冲突。

---

# 54. Claude Code 禁止事项

`[DECISION]`

Claude Code 在没有明确必要性的情况下禁止：

1. 直接重写整个项目；
2. 一次实现多个独立 subsystem；
3. 为追求“更先进”随意换框架；
4. 绕过已有接口；
5. 把领域模型改成某个框架私有类型；
6. 让 LLM 自由生成工程事实；
7. 在测试失败时继续扩大实现；
8. 把研究假设写成已经验证的事实；
9. 未阅读现有代码就重复实现；
10. 未检查第三方项目就造新 parser；
11. 未经评测增加复杂 Multi-Agent；
12. 用大 Prompt 替代 Domain Model；
13. 用 Vector DB 替代所有结构化查询；
14. 用 Neo4j 替代所有领域逻辑；
15. 用 MCP 替代内部模块设计；
16. 把全部功能塞进单个 LangGraph Node；
17. 把所有异常吞掉；
18. 修改 third-party repo Git history；
19. 把实验代码直接视作 production；
20. 声称未经验证的任务“已经完成”。

---

# 55. 新功能决策检查表

每次增加能力先回答：

```text
1. 这个能力解决什么 FMEA 问题？
2. 输入是什么？
3. 输出是什么？
4. 输入是事实、知识还是推断？
5. 谁是 Source of Truth？
6. 需要新的 Domain Model 吗？
7. 是否已有第三方工具可复用？
8. 是 Adapter、Tool、MCP 还是 Core？
9. 是否需要 LLM？
10. 如果不用 LLM 能否解决？
11. 如何测试？
12. 如何 Benchmark？
13. 如何追溯证据？
14. 哪一步需要 Human Review？
15. 失败时系统应该怎么表现？
```

如果这些问题不能回答清楚：

> 不进入大规模编码。

---

# 56. 架构升级检查表

引入新框架前必须回答：

```text
Existing problem:
Why current stack fails:
Alternative:
Benefits:
Migration cost:
New coupling:
Test impact:
Rollback plan:
```

禁止：

> 因为某库最近很流行，所以替换。

---

# 57. Claude Code 推荐任务模板

```text
Read:
- CLAUDE.md
- docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md
- PROGRESS.md
- relevant spec
- relevant tests

Task:
<one clearly scoped task>

Before coding:
1. Inspect the existing implementation.
2. Identify reusable interfaces and third-party capabilities.
3. State architectural impact.
4. Identify unknowns.
5. Propose the minimum implementation.

Implementation:
1. Write/update tests.
2. Implement only this task.
3. Preserve domain boundaries.
4. Preserve evidence and traceability.
5. Do not begin unrelated work.

Verification:
- run unit tests
- run integration tests if relevant
- run lint
- run type check
- run benchmark if relevant

Finish:
1. Summarize changed files.
2. Report verification results.
3. Update PROGRESS.md.
4. Report unresolved risks.
```

---

# 58. 第一阶段成功标准

V1 不需要“什么都能做”。

真正有价值的 V1 应证明：

```text
SysML / Design Data
       ↓
Reliable Canonical System Model
       ↓
Function / Structure Context
       ↓
Failure Knowledge Retrieval
       ↓
Structured FMEA Candidate
       ↓
Evidence
       ↓
Verification
       ↓
Human Review
```

并且：

- 每一步有明确数据结构；
- 可独立测试；
- 可回溯来源；
- 可替换底层工具；
- 可逐渐扩展。

---

# 59. 项目长期竞争力

本项目最重要的差异化不应该只是：

> “我用了 LLM。”

而应该是：

```text
MBSE-aware
+
Evidence-grounded
+
Knowledge-enhanced
+
Workflow-controlled
+
Human-reviewed
+
Benchmark-evaluated
+
Extensible
```

即：

> **一个真正理解系统结构与工程证据的 FMEA Analysis Agent。**

---

# 60. 当前项目的一句话架构原则

> **先把系统模型变成可信、可查询、可验证的工程事实；再把历史故障与领域知识变成可追溯证据；最后让 Agent 在结构化流程中进行受约束的 FMEA 推理，并由工程师完成最终确认。**

---

# 61. 给 Claude Code 的最高优先级指令

Claude Code 在本项目中始终遵循以下顺序：

```text
Understand
  ↓
Reuse
  ↓
Model
  ↓
Test
  ↓
Implement
  ↓
Verify
  ↓
Evaluate
  ↓
Document
```

不要变成：

```text
Prompt
  ↓
Generate a lot of code
  ↓
Hope it works
```

---

# 62. 当前决策快照

截至本基线：

| 项目 | 当前状态 |
|---|---|
| FMEA Agent 定位 | `[DECISION]` 工程辅助，不完全替代专家 |
| FMEA Profile | `[DECISION]` AIAG-VDA FMEA（七步法流程骨架） |
| 核心编排 | `[BASELINE]` LangGraph |
| LangChain | `[DECISION]` 适配/生态层 |
| MCP | `[DECISION]` 外部能力接口层 |
| SysML | `[DECISION]` 技术路线核心输入之一 |
| SysML File Mode | `[DECISION]` 保留 |
| SysML Repository Mode | `[DECISION]` 保留 |
| Canonical System Model | `[DECISION]` 必须建立 |
| System / Failure Model | `[DECISION]` 分离 |
| Knowledge Graph | `[BASELINE]` Neo4j |
| RAG | `[DECISION]` 文本/案例证据检索 |
| Structured Query | `[DECISION]` 优先处理明确关系查询 |
| Data Contract | `[BASELINE]` Pydantic + JSON Schema |
| Agent Strategy | `[DECISION]` workflow-first |
| Human Review | `[DECISION]` 正式流程节点 |
| Evidence | `[DECISION]` 一等数据对象 |
| Benchmark | `[DECISION]` 必须建设 |
| CATIA / STEP | `[DEFERRED]` 当前不优先 |
| Dynamic FMEA | `[DEFERRED]` V1 后研究 |
| Multi-Agent | `[DEFERRED]` 在固定 workflow 稳定后逐步引入 |

---

# 63. 本文件的维护规则

本文件允许更新，但以下变化必须留下 ADR 或变更说明：

- 更换 Agent 主框架；
- 改变 Canonical Model 原则；
- 改变 SysML 输入路线；
- 改变 Human Review 边界；
- 改变 Evidence 模型；
- 改变 Knowledge Graph 核心方案；
- 改变 FMEA 风险模型；
- 扩大/缩小项目应用边界。

对于普通实现细节，不应频繁修改本文件。

---

# 64. 推荐配套文档

本文件之后建议逐步补齐：

```text
CLAUDE.md

docs/architecture/
  overview.md
  canonical-system-model.md
  failure-model.md
  sysml-integration.md
  knowledge-architecture.md
  agent-workflow.md

docs/adr/

docs/specs/

docs/plans/

docs/research/
  repository_inventory.md
  sysml_to_fmea_mapping.md
  api_capability_matrix.md
  research_notes.md

PROGRESS.md
```

---

# 65. 结束语

这个项目不应被开发成一个“会填 FMEA 表的聊天机器人”。

正确方向是逐渐形成：

> **工程模型驱动 + 故障知识增强 + Agent 流程编排 + 证据约束 + 人机协同 + 可量化评测**

的 FMEA 智能分析基础设施。

未来无论增加：

```text
SysML
FTA
PHM
PLM
Digital Twin
Simulation
New Knowledge Graph
New LLM
New Agent
New MCP Server
```

都应当像增加积木一样通过稳定接口加入，而不是不断推翻核心。

这就是本项目长期开发的最重要边界。
