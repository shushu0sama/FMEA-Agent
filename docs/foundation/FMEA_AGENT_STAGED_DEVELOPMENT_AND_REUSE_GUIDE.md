# FMEA Agent 分阶段开发路线、MVP 与开源复用指南
## FMEA Agent Staged Development, MVP & Reuse Guide for Claude Code

> **文档定位**：本文件是 `FMEA_AGENT_FOUNDATION_GUIDE.md` 的执行配套文档。  
> Foundation Guide 回答“项目是什么、边界是什么、长期原则是什么”；本文件回答“**每个阶段具体做什么、哪些必须自己写、哪些不要自己写、MVP 如何验收、哪些开源项目/MCP 可以直接复用**”。  
> **主要使用者**：Claude Code、项目维护者、后续协作者。  
> **版本**：v0.1  
> **基线日期**：2026-09-03  
> **状态**：Living Document  
> **开发原则**：Reuse first, wrap second, implement core semantics ourselves.

---

# Bootstrap v0.1 执行优先级补充：Phase 路线 + MVP 路线

> **本节是本文件的执行优先级说明。**

原 Phase 0–9 保留，用于描述长期能力成熟度。

实际编码采用更短的 MVP 迭代：

```text
MVP-0  Runnable Skeleton
       JSON + InMemory + LangGraph

MVP-1  Real System Facts
       SysML → SysMLFactSnapshot → Canonical

MVP-2  Real Failure Knowledge
       Historical FMEA / KG / Retrieval

MVP-3  Evidence-grounded LLM Generation

MVP-4  AIAG-VDA Risk + Semantic Validation

MVP-5  Human Review

MVP-6  Failure Propagation

MVP-7  Aerospace Benchmark

MVP-8  MCP Capability Layer

MVP-9  Dynamic FMEA
```

## 执行原则

```text
先跑通端到端细线
→ 保持接口可替换
→ 逐项替换 stub
→ 每次只增加一个主要真实能力
```

MVP-0 明确不依赖：

```text
OpenSysML
Neo4j
Qdrant
Docling
MCP
完整 AIAG-VDA 风险规则
```

---

# 0. 最高优先级原则

Claude Code 在任何阶段开始编码前，都必须首先判断目标能力属于以下哪一种：

| 分类 | 含义 | 默认策略 |
|---|---|---|
| **S — Self-build** | FMEA 项目的核心领域能力、研究创新、长期稳定接口 | **自己设计和实现** |
| **W — Wrap** | 外部项目能力有价值，但接口不适合直接进入核心 | **通过 Adapter / Repository / Tool / MCP 包装** |
| **D — Direct reuse** | 成熟基础设施、通用工具、协议 SDK | **直接依赖，不重复开发** |
| **R — Reference only** | 可借鉴思路、示例、测试或数据，但不适合作为核心依赖 | **只研究，不耦合** |

## 0.1 总原则

项目优先采用：

```text
Search
  ↓
Inspect
  ↓
Run
  ↓
Evaluate
  ↓
Reuse
  ↓
Wrap
  ↓
Only then: Self-build
```

禁止默认采用：

```text
Need a feature
      ↓
Ask LLM to write everything from scratch
```

## 0.2 哪些东西原则上不要自己重写

除非经过 ADR 明确论证，否则不要自主重写：

- SysML v2 parser；
- SysML Repository API；
- JSON Schema / 基础数据验证框架；
- PDF / DOCX 基础解析器；
- OCR 引擎；
- Vector Database；
- Graph Database；
- LLM Runtime；
- Embedding 模型；
- Agent Runtime；
- MCP 协议；
- Git 工具；
- 测试框架；
- Linter / Formatter；
- 通用 Web API 框架；
- 通用原型 UI 框架。

本项目的自主开发资源应集中在：

```text
Canonical System Model
SysML → FMEA Semantic Mapping
FMEA Domain Model
Failure Knowledge Schema
Evidence / Provenance Model
FMEA Workflow
KG + RAG Fusion
Cause–Mode–Effect Validation
Failure Propagation
Human Review Policy
FMEA Benchmark / Ground Truth
Dynamic FMEA / Change Impact Analysis
```

---

# 1. 总体阶段划分

本项目建议分为 **10 个阶段**。

```text
Phase 0   Engineering Foundation
              ↓
Phase 1   SysML Fact Access
              ↓
Phase 2   Canonical System Model
              ↓
Phase 3   FMEA Domain Core
              ↓
Phase 4   Failure Knowledge + KG/RAG
              ↓
Phase 5   LLM-assisted FMEA Workflow
              ↓
Phase 6   Verification + Human Review
              ↓
Phase 7   Failure Propagation + Aerospace Benchmark
              ↓
         ───── FMEA Agent 1.0 ─────
              ↓
Phase 8   MCP Capability Ecosystem
              ↓
Phase 9   Dynamic FMEA / Design Change
```

版本映射：

```text
FMEA Agent 0.x
= Phase 0–3
= 数据与领域地基

FMEA Agent 1.x
= Phase 4–7
= 真正可用的智能 FMEA Agent

FMEA Agent 2.x
= Phase 8–9
= 可扩展、可被其他 Agent 调用、可随设计变化更新的工程 Agent
```

---

# 2. 阶段推进规则

任何 Phase 进入下一阶段前，应满足：

```text
[ ] 当前 MVP 可独立运行
[ ] 当前 MVP 有自动测试
[ ] 输入输出有明确 Schema
[ ] 关键结论可追溯
[ ] 当前阶段 benchmark 达标
[ ] 未将下一阶段能力偷渡进当前阶段
[ ] 可替换的第三方实现已经通过接口隔离
[ ] PROGRESS.md 已更新
```

如果 MVP 不能独立验证，不进入下一阶段。

---

# 3. Phase 0 — Engineering Foundation
## 工程地基、测试地基与 Benchmark 骨架

## 3.1 目标

本阶段**不开发 FMEA 智能推理**。

目标是让项目具备长期开发所需的工程纪律：

```text
Repository
  +
Typed Python
  +
Testing
  +
Linting
  +
Type Check
  +
Docs
  +
Benchmark Skeleton
  +
Claude Code Workflow
```

---

## 3.2 MVP 0 必须实现的功能

MVP 0 完成时，项目至少应具备：

```text
fmea-agent/
├── CLAUDE.md
├── PROGRESS.md
├── pyproject.toml
├── README.md
│
├── docs/
│   ├── foundation/
│   ├── architecture/
│   ├── specs/
│   ├── plans/
│   └── adr/
│
├── src/fmea_agent/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
│
├── benchmarks/
│   └── README.md
│
├── scripts/
│   └── verify.*
│
└── .claude/
    ├── rules/
    ├── skills/
    └── agents/
```

验证命令：

```bash
pytest
ruff check .
mypy src
```

至少有：

- 一个 sample domain model；
- 一个 sample test；
- 一个完整 CI/local verification 流程；
- 一个 benchmark fixture 目录；
- 一个 ADR 示例；
- Claude Code 能依据 `CLAUDE.md + Foundation Guide + PROGRESS.md` 开始任务。

---

## 3.3 必须自己编写（S）

本阶段自研内容很少，但以下必须自己定义：

### S0-1 项目目录与模块边界

必须由本项目决定：

```text
domain/
ingestion/
knowledge/
agents/
tools/
mcp/
evaluation/
application/
api/
```

### S0-2 Definition of Done

必须适合本 FMEA 项目，而不是复制普通 Web 项目的完成标准。

### S0-3 Benchmark 目录协议

定义：

```text
input/
expected/
metadata/
evidence/
evaluation/
```

### S0-4 Claude Code 项目规则

包括：

- 不绕过 Domain；
- 不把 Prompt 当 Domain Model；
- 不重复造基础设施；
- 非 trivial feature 先 Spec/Plan；
- 完成前必须验证。

---

## 3.4 可以直接复用（D）

### Pydantic

用途：

- typed model；
- validation；
- JSON Schema；
- serialization。

项目：

https://github.com/pydantic/pydantic

复用等级：

**D — Direct reuse**

不要自己开发通用数据验证器。

---

### pytest

用途：

- unit test；
- integration test；
- fixture；
- regression。

项目：

https://github.com/pytest-dev/pytest

复用等级：

**D**

---

### Ruff

用途：

- lint；
- formatting；
- import/style quality。

项目：

https://github.com/astral-sh/ruff

复用等级：

**D**

---

### Claude Code

用途：

- 主开发 Agent；
- Plan；
- Subagent；
- Skill；
- Hook；
- Worktree 协作。

本项目只配置规则，不重写 Coding Agent。

---

## 3.5 可复用 MCP（W/D）

### MCP Filesystem Reference Server

项目：

https://github.com/modelcontextprotocol/servers

具体能力：

- read/write files；
- directory control；
- file search；
- metadata。

用途：

**只作为 Claude/实验环境的工具接口。**

核心代码不要依赖 Filesystem MCP。

复用等级：

**D/W**

---

### MCP Git Reference Server

同仓库：

https://github.com/modelcontextprotocol/servers

用途：

- repo 查询；
- Git read/search；
- 可作为 Claude Code 外部实验工具。

核心开发仍优先使用 Git CLI。

---

## 3.6 本阶段不要自己开发

```text
Custom testing framework
Custom linter
Custom package manager
Custom Git protocol
Custom MCP protocol
Custom logging platform
Custom CI framework
```

---

## 3.7 MVP 0 验收标准

```text
Given:
fresh clone

When:
install dependencies
run verify

Then:
all verification passes
and
Claude Code can understand project rules
```

---

# 4. Phase 1 — SysML Fact Access
## SysML 工程事实读取

## 4.1 核心研究问题

本阶段只回答：

> **能否可靠地从真实 SysML v2 模型读取系统事实？**

不回答：

> “它为什么会失效？”

---

## 4.2 MVP 1 输入

第一优先：

```text
OMG SysML v2 Training Examples
Simple Vehicle
```

第二优先：

```text
SYSMOD Delivery Drone
```

---

## 4.3 MVP 1 输出

程序至少可以从真实模型抽取：

```text
System
Component / Part
Function / Action
Requirement
Port
Interface
Connection
Flow
State
Allocation
Containment
SourceReference
```

输出第一版 `SysMLFactSnapshot`（parser/API 事实快照），不要在 Phase 1 把它称为 Canonical System Model。

建议以 source-native snapshot envelope 表达，例如：

```json
{
  "source": {
    "adapter": "open_sysml",
    "model": "..."
  },
  "elements": [
    {
      "source_id": "...",
      "name": "...",
      "type": "...",
      "parent_source_id": "..."
    }
  ]
}
```

---

## 4.4 MVP 1 能实现的用户功能

用户/测试程序可以询问：

```text
有哪些系统？
有哪些子系统？
有哪些组件？
组件属于哪个系统？
有哪些功能？
某功能由什么组件承担？
有哪些需求？
有哪些接口？
A 与 B 是否存在连接？
有哪些 Flow？
```

这些答案必须来自 SysML，不来自 LLM 猜测。

---

## 4.5 必须自己编写（S）

### S1-1 `SysMLAdapter` 抽象接口

例如：

```python
class SysMLAdapter:
    def load(...): ...
    def get_elements(...): ...
    def get_relationships(...): ...
```

### S1-2 OpenSysML Adapter

负责把 OpenSysML 的输出转换成项目内部中间对象。

### S1-3 Repository Adapter

负责调用 SysML v2 API。

### S1-4 SourceReference

必须保留：

```text
repository
project
commit
file
element_id
version
```

### S1-5 SysML semantic fixtures

必须建立自己的：

```text
Part
Function
Requirement
Interface
Flow
State
```

最小测试模型。

---

## 4.6 可以直接复用（D）

### OMG SysML v2 Release

**权威模型、标准库与 Example 的主要来源。**

项目：

https://github.com/Systems-Modeling/SysML-v2-Release

用途：

- SysML v2 example；
- standard library；
- grammar/spec reference；
- benchmark source。

复用等级：

**D/R**

不要修改官方 repo。

---

### OpenSysML

项目：

https://github.com/Open-MBEE/OpenSysML

用途：

- `.sysml` 解析；
- language runtime；
- gRPC；
- Python client；
- offline File Mode。

复用等级：

**D/W**

原则：

> 不自主编写新的 SysML Parser，优先给 OpenSysML 做 Adapter。

---

### OMG SysML v2 Pilot Implementation

项目：

https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation

用途：

- 官方/参考实现对照；
- parser semantics reference；
- model validation cross-check。

复用等级：

**R**

建议不要作为 Python 主运行时的第一选择，但可用来做语义交叉验证。

---

### SysML v2 API Services

项目：

https://github.com/Systems-Modeling/SysML-v2-API-Services

用途：

- Repository Mode；
- REST API；
- project/commit/element access。

复用等级：

**D/W**

---

### SysML v2 API Cookbook

项目：

https://github.com/Systems-Modeling/SysML-v2-API-Cookbook

用途：

直接复用或改写其 API traversal pattern，尤其：

- Requirement decomposition；
- Structure decomposition；
- Behavior decomposition；
- owned elements；
- queries；
- Project / Commit / Branch / Tag。

复用等级：

**R/D**

---

## 4.7 可以复用包装的 MCP 项目

### SYSMOD SysML v2 API + MCP Server

当前仓库：

https://github.com/Open-MBEE/sysmod-sysmlv2-api

历史/README 中也使用过项目名：

`sysmod-sysmlv2-api-mcp`

用途：

- 查询 SysML Repository；
- requirements；
- contexts；
- stakeholders；
- use cases；
- feature tree；
- model quality；
- MCP tools。

复用等级：

**W/R**

重要限制：

> 该项目面向 SYSMOD 方法学，不应直接成为 FMEA Agent 的核心 SysML Domain API。

正确复用方式：

```text
SYSMOD MCP
     ↓
Research / integration reference

我们的 SysMLTool
     ↓
Canonical System Model
```

可学习其：

- SysML API → REST；
- REST → MCP；
- model query tool design；
- agent/model interaction pattern。

不要把 SYSMOD-specific schema 渗透进 FMEA Domain。

---

## 4.8 本阶段不要开发

```text
Failure Mode
Failure Cause
Risk
Neo4j large KG
RAG
LangGraph Agent
LLM prompt generation
MCP FMEA Server
```

---

## 4.9 MVP 1 验收标准

使用至少一个 Simple Vehicle 模型：

```text
SysML
  ↓
Program
  ↓
Normalized Facts
```

人工逐项对照模型。

最低要求：

```text
Component extraction
Function extraction
Requirement extraction
Connection extraction
```

均可通过测试验证。

---

# 5. Phase 2 — Canonical System Model
## 建立与底层工具解耦的统一系统模型

本阶段的明确输入边界是：

```text
SysMLFactSnapshot
→ Semantic Mapping
→ Canonical System Model
```


## 5.1 目标

FMEA Agent 不应知道：

```text
OpenSysML object
REST response
SysML server implementation
```

FMEA Agent 只应知道：

```text
Canonical System Model
```

---

## 5.2 MVP 2 功能

建立统一模型：

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

并提供：

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

---

## 5.3 必须自己编写（S）

这一阶段属于核心自研。

### S2-1 Canonical Schema

这是 FMEA Agent 最重要的长期接口之一。

### S2-2 Stable ID Strategy

明确：

```text
source_id
canonical_id
version_id
```

### S2-3 Mapping

```text
OpenSysML → Canonical
REST API → Canonical
```

### S2-4 Validation

验证：

- parent-child；
- allocation；
- dangling references；
- duplicate IDs；
- source trace。

### S2-5 Serialization

支持：

```text
JSON
JSON Schema
```

---

## 5.4 可以直接复用（D）

### Pydantic

https://github.com/pydantic/pydantic

用于：

- typed schema；
- discriminated union；
- validation；
- JSON Schema。

### Python standard typing

无需自建 type system。

---

## 5.5 可以复用包装的 MCP

本阶段 **MCP 不是必要依赖**。

但可将 Phase 1 的 SysML MCP 当成一个外部 Adapter source：

```text
MCP response
   ↓
MCP SysML Adapter
   ↓
Canonical Model
```

注意：

Canonical Model 不允许 import MCP SDK 类型。

---

## 5.6 核心对照实验

同一模型通过：

```text
OpenSysML
    ↓
Canonical A

SysML API
    ↓
Canonical B
```

比较：

```text
A ≈ B
```

如果差异存在，必须定位是：

- parser difference；
- API representation；
- mapping bug；
- model/version mismatch。

---

## 5.7 MVP 2 验收标准

Agent 上层只依赖：

```text
SystemModelRepository
```

将 OpenSysML 替换成 API Adapter 后，上层测试无需重写。

---

# 6. Phase 3 — FMEA Domain Core
## FMEA 领域模型与确定性规则

## 6.1 目标

建立“没有 LLM 也成立”的 FMEA 核心。

---

## 6.2 MVP 3 功能

至少定义：

```text
FMEAItem
Function
FailureMode
FailureCause
FailureEffect
FailureMechanism
Control
DetectionMethod
RiskAssessment
RecommendedAction
Evidence
ReviewStatus
```

支持：

```text
Component
  ↓
Function
  ↓
Failure Mode
  ↓
Cause
  ↓
Local Effect
  ↓
Next Higher Level Effect
  ↓
End Effect
```

---

## 6.3 MVP 3 用户功能

### Historical FMEA Import

支持首批：

```text
.xlsx
.csv
.json
```

### FMEA Validation

检测：

```text
Missing function
Missing mode
Cause/Mode/Effect ambiguity
Duplicate rows
Invalid S/O/D
Incorrect RPN
Missing evidence
Broken item references
```

### Risk Strategy Interface

风险评估必须通过可替换的 `RiskStrategy`。MVP-0/早期阶段允许 `NoOpRiskStrategy → NOT_EVALUATED`。正式 AIAG-VDA S/O/D/AP 逻辑只从授权规则来源实现。

### Deterministic Risk Calculation

例如：

```text
RPN = S × O × D
```

禁止 LLM 负责乘法。

### Export

首批支持：

```text
JSON
Excel
```

---

## 6.4 必须自己编写（S）

### S3-1 FMEA Domain Schema

### S3-2 Cause–Mode–Effect semantics

### S3-3 Effect hierarchy

至少：

```text
local
next_higher_level
end_effect
```

### S3-4 Risk domain interface

风险模型要允许未来扩展：

```text
RPN
AP
Criticality
Custom enterprise rules
```

### S3-5 Evidence Model

### S3-6 Review Model

### S3-7 SysML → FMEA semantic mapping layer

这是重要研究内容：

```text
System/Component ↔ Item
Action/Function ↔ Function
Containment ↔ Effect hierarchy context
Flow/Connection ↔ Propagation context
Requirement ↔ Effect/severity constraint context
```

---

## 6.5 可以直接复用（D）

### pandas

用于历史 FMEA 表格批处理。

项目：

https://github.com/pandas-dev/pandas

### openpyxl

用于 Excel 读写与格式保留。

项目：

https://github.com/ericgazoni/openpyxl
（如仓库状态变化，以 PyPI/官方文档为准）

### Pydantic

继续作为 Schema/Validation 基础。

---

## 6.6 MCP 复用建议

本阶段 FMEA Domain **不要 MCP-first**。

正确顺序：

```text
Python Domain API
    ↓
stable
    ↓
Future MCP wrapper
```

暂时不要为了“Agent 化”把基础领域逻辑写进 MCP Server。

---

## 6.7 本阶段不要开发

```text
LLM autonomous FMEA
Multi-Agent
Dynamic FMEA
Complex KG
External MCP ecosystem
```

---

## 6.8 MVP 3 验收标准

给定人工制作的 FMEA 表：

系统可以：

```text
Import
  ↓
Normalize
  ↓
Validate
  ↓
Calculate Risk
  ↓
Export
```

全流程不依赖 LLM。

---

# 7. Phase 4 — Failure Knowledge + KG/RAG
## 故障知识底座、证据检索与多源融合

## 7.1 目标

前面解决：

> “系统是什么？”

这一阶段解决：

> “相似系统以前如何失效？证据在哪里？”

---

## 7.2 MVP 4 功能

输入：

```text
Component / Function
```

输出：

```text
Known Failure Modes
Known Causes
Known Effects
Similar FMEA Entries
Historical Cases
Evidence Sources
```

每个结果必须绑定 Evidence。

---

## 7.3 MVP 4 典型体验

查询：

```text
Hydraulic Pump
Function: Provide Hydraulic Pressure
```

返回：

```text
Candidate Failure Mode:
Loss of Pressure

Evidence:
E01 Historical FMEA
E02 Maintenance report
E03 Failure knowledge graph relation
```

---

## 7.4 必须自己编写（S）

### S4-1 Failure Knowledge Schema

定义：

```text
Component
Function
FailureMode
Cause
Effect
Mechanism
Control
Case
Evidence
```

### S4-2 Entity Resolution

解决：

```text
Hydraulic Pump
Hyd Pump
Pump Assembly
液压泵
```

是否是同一对象。

### S4-3 KG Query Strategy

自行定义适合 FMEA 的 Cypher/query service。

### S4-4 KG + Vector Fusion

决定：

```text
什么时候 graph first？
什么时候 vector first？
如何 merge？
如何 rerank？
```

### S4-5 Evidence Ranking

不能仅返回 top-K 文本。

需要综合：

```text
source authority
relevance
entity match
relationship match
review state
version
```

---

## 7.5 可以直接复用（D）

### Neo4j

主知识图谱候选。

Python driver：

https://github.com/neo4j/neo4j-python-driver

用途：

- node/relationship；
- Cypher；
- path query；
- graph persistence。

Domain 不直接依赖 driver。

---

### neosemantics / n10s

项目：

https://github.com/neo4j-labs/neosemantics

用途：

- RDF import/export；
- OWL/RDFS/SKOS；
- SHACL；
- semantic mapping。

复用等级：

**D/W**

不要重写 RDF → Neo4j importer。

---

### RDFLib

项目：

https://github.com/RDFLib/rdflib

用途：

- RDF；
- Turtle；
- SPARQL；
- ontology preprocessing。

复用等级：

**D**

---

### Docling

项目：

https://github.com/docling-project/docling

用途：

- PDF；
- Office；
- document structure；
- tables；
- document conversion；
- RAG preprocessing。

复用等级：

**D**

原则：

> 不自己从零实现 PDF layout/table parser。

---

### Qdrant

项目：

https://github.com/qdrant/qdrant

用途：

- vector retrieval；
- metadata filtering；
- local/server mode。

复用等级：

**D**

Vector DB 是基础设施，不是本项目创新点。

---

## 7.6 可以直接复用的 MCP

### Docling MCP

项目：

https://github.com/docling-project/docling-mcp

能力：

- 文档转换；
- document manipulation；
- structured output；
- Agent 可通过 MCP 调用。

用途：

```text
Failure Report
Paper
Manual
Maintenance Document
        ↓
Docling MCP
        ↓
Structured Document
```

复用等级：

**D/W**

在核心 ingestion 中可以直接调用 Docling Python；
在 Claude/Agent 工具环境中可以复用 Docling MCP。

---

### Qdrant MCP Server

官方项目：

https://github.com/qdrant/mcp-server-qdrant

用途：

- semantic store；
- semantic find；
- MCP vector search。

复用等级：

**D/W**

不要自己重新写一个“通用向量搜索 MCP”。

本项目如需额外 FMEA semantics，应：

```text
Qdrant MCP
   +
FMEA Retrieval Wrapper
```

而不是 fork 后大量魔改。

---

### Neo4j Official MCP

项目：

https://github.com/neo4j/mcp

用途：

- MCP-compatible structured graph access；
- read-only 可配置；
- schema/data query。

复用等级：

**D/W**

原则：

> 通用 Neo4j 查询能力直接复用；  
> FMEA-specific graph semantics 自己写成上层 FailureKnowledgeTool。

---

### Neo4j Labs MCP

项目：

https://github.com/neo4j-contrib/mcp-neo4j

用途：

- 实验性 Neo4j MCP 能力参考。

复用等级：

**R**

如果官方 `neo4j/mcp` 已满足需求，优先官方版本。

---

## 7.7 本阶段不要自己开发

```text
Vector database engine
PDF parser engine
OWL parser
Graph database
Generic Neo4j MCP server
Generic Qdrant MCP server
Generic document MCP server
```

---

## 7.8 MVP 4 验收标准

对一组人工已知故障问题：

至少测：

```text
Recall@K
Precision@K
Evidence Coverage
Entity Match Accuracy
```

必须能显示来源。

---

# 8. Phase 5 — LLM-assisted FMEA Workflow
## 第一个真正意义上的 FMEA Agent

## 8.1 目标

首次引入：

```text
LLM
+
LangGraph
```

但仍采用：

> Single orchestrated workflow first.

Phase 5 只负责形成**有证据、结构化、可验证的 Candidate**。正式的语义验证、Risk/Policy Gate 与 Human Review 进入 Phase 6。

---

## 8.2 MVP 5 Graph

第一版控制在约 6 个节点：

```text
START
  ↓
load_system
  ↓
retrieve_failure_knowledge
  ↓
generate_candidates
  ↓
basic_schema_validation
  ↓
candidate_output
  ↓
END
```

不要立即拆出十几个 Agent。

---

## 8.3 MVP 5 用户功能

输入：

```text
对 HydraulicPump 进行 FMEA
```

系统自动：

1. 查询 Canonical System Model；
2. 获取 Function；
3. 查询 Failure KG；
4. 查询历史案例/RAG；
5. LLM 生成候选；
6. 输出结构化 FMEA Candidate；
7. 附 Evidence。

---

## 8.4 必须自己编写（S）

### S5-1 FMEA Graph State

状态不是聊天消息列表。

必须结构化，例如：

```text
system_context
selected_item
functions
retrieved_failure_knowledge
evidence
candidates
validation_issues
review_status
```

### S5-2 FMEA Nodes

自己实现领域 Node：

```text
load_system
retrieve_failure_knowledge
generate_candidates
validate_candidates
```

### S5-3 Structured Prompt

Prompt 必须绑定 Schema。

### S5-4 LLM abstraction

如：

```text
LLMClient
StructuredGenerator
```

### S5-5 Candidate policy

明确：

```text
fact
retrieved evidence
inference
unsupported
```

---

## 8.5 可以直接复用（D）

### LangGraph

项目：

https://github.com/langchain-ai/langgraph

用途：

- state graph；
- nodes；
- routing；
- persistence；
- interrupts；
- resilient execution。

复用等级：

**D**

不要自己写 Agent runtime。

---

### LangChain（可选）

用途：

- provider adapters；
- tool adapters；
- retriever integration。

原则：

```text
LangGraph = orchestration
LangChain = optional compatibility layer
```

---

## 8.6 MCP 可复用

这一阶段可开始**消费 MCP**，但不要急着发布自己的 FMEA MCP。

### LangChain MCP Adapters

项目：

https://github.com/langchain-ai/langchain-mcp-adapters

用途：

- 将 MCP tools 转成 LangChain/LangGraph 可用 tools；
- 多 MCP server client。

复用等级：

**D/W**

### 重要版本风险

截至本基线，MCP Python SDK 已进入 v2 稳定线，但 `langchain-mcp-adapters` 仍存在 MCP v2 兼容相关变更/PR。

因此必须：

```text
pin versions
+
contract tests
+
upgrade ADR
```

不要使用：

```text
pip install -U everything
```

然后直接提交。

---

## 8.7 第一阶段可接入 MCP

推荐只接：

```text
SysML MCP      → system facts
Neo4j MCP      → graph inspection / generic query
Qdrant MCP     → semantic retrieval
Docling MCP    → document processing
```

但核心 workflow 应通过项目自己的 Tool 接口使用它们：

```text
LangGraph
   ↓
SystemModelTool
FailureKnowledgeTool
DocumentTool
   ↓
MCP / direct adapter
```

不要让 Graph Node 到处直接写 MCP client call。

---

## 8.8 MVP 5 验收标准

对一个已知系统：

输出候选 FMEA 必须同时包含：

```text
Item
Function
Failure Mode
Cause
Effect
Evidence
Generation status
```

至少能区分：

```text
supported
partially supported
unsupported
```

---

# 9. Phase 6 — Verification + Human Review
## 从“生成 Demo”进入“工程辅助系统”

## 9.1 目标

任何 LLM Candidate 都不能直接成为正式 FMEA。

---

## 9.2 MVP 6 Pipeline

```text
Candidate
   ↓
Schema Validation
   ↓
FMEA Semantic Validation
   ↓
System Model Validation
   ↓
Evidence Validation
   ↓
Risk/Policy Gate
   ↓
Human Review
```

---

## 9.3 MVP 6 用户功能

工程师可以：

```text
Accept
Edit
Reject
Request Evidence
Mark Unknown
Escalate
```

审核结果被版本化保存。

---

## 9.4 必须自己编写（S）

### S6-1 FMEA semantic validators

如：

```text
Cause is not Effect
Mode maps to Function
Effect hierarchy matches system hierarchy
Evidence supports the candidate
```

### S6-2 Review Policy

决定什么时候必须人工：

```text
new mode
high severity
low evidence
model conflict
rule conflict
unsupported claim
```

### S6-3 Evidence completeness score

注意：

> Evidence confidence ≠ failure probability.

### S6-4 Human decision persistence

### S6-5 Audit log

记录：

```text
who/what changed
original candidate
edited candidate
evidence
model version
timestamp
```

---

## 9.5 可以直接复用（D）

### LangGraph persistence / interrupt

继续复用 LangGraph。

不要自建一个特殊“暂停 Agent runtime”。

### Pydantic validation

继续使用。

---

## 9.6 可复用 MCP

MCP 在此阶段主要作为证据查询接口。

例如：

```text
Docling MCP
Qdrant MCP
Neo4j MCP
SysML MCP
```

Human Review 本身暂时不需要做 MCP。

---

## 9.7 MVP 6 验收标准

对每一个最终 FMEA 条目，都能回答：

```text
设计事实来自哪里？
故障知识来自哪里？
哪些字段是 LLM 推断？
验证过哪些规则？
人工做了什么决定？
```

---

# 10. Phase 7 — Failure Propagation + Aerospace Benchmark
## 系统结构约束下的失效传播

## 10.1 目标

形成明显区别于“LLM 自动填 FMEA 表”的能力：

> **SysML-aware Failure Propagation**

---

## 10.2 MVP 7 功能

示例：

```text
HydraulicPump
     X
LossOfPressure
     ↓
HydraulicFlow
     ↓
Actuator
     ↓
LossOfForce
     ↓
LandingGear
     ↓
RetractionFailure
```

输出：

```text
Local Effect
Next Higher Level Effect
End Effect
```

并附：

```text
SysML structural path
Functional path
Flow/interface path
Failure knowledge
Evidence
```

---

## 10.3 必须自己编写（S）

这是核心研究阶段。

### S7-1 Propagation semantics

研究：

```text
Connection propagation
Flow propagation
Function propagation
Containment propagation
Interface propagation
State-dependent propagation
```

### S7-2 Propagation Graph

不要等同于 Neo4j 原始图。

应构造 FMEA-specific propagation view。

### S7-3 Path scoring

### S7-4 Effect level resolution

### S7-5 Conflict handling

例如：

```text
system structure says path exists
but
failure knowledge says propagation impossible under current state
```

---

## 10.4 可以直接复用（D）

### Neo4j path query

不用自己实现 graph database traversal engine。

### NetworkX

项目：

https://github.com/networkx/networkx

适合：

- 小规模算法原型；
- path algorithm；
- testing；
- in-memory graph experiments。

### SysML models

继续复用官方/开源模型。

---

## 10.5 Benchmark 复用

### SYSMOD Delivery Drone

项目：

https://github.com/MBSE4U/sysmod-sysmlv2

用途：

- functional architecture；
- logical architecture；
- product architecture；
- requirements；
- cross-level test。

复用等级：

**D/R**

---

### Open-MBEE SysML v2 Applications and Examples

项目：

https://github.com/Open-MBEE/SysML-v2-Applications-and-Examples

包括：

- CubeSat example；
- spacecraft examples；
- time/space modeling examples。

用途：

- Aerospace benchmark；
- research cases。

复用等级：

**D/R**

---

## 10.6 MCP 复用

本阶段不需要新的通用 MCP。

可以复用：

```text
SysML MCP
Neo4j MCP
```

但传播算法应保留在：

```text
fmea_agent.domain / knowledge / reasoning
```

不要把算法写进第三方 MCP。

---

## 10.7 MVP 7 验收标准

人工建立至少一组 propagation ground truth。

计算：

```text
Path Precision
Path Recall
Effect Level Accuracy
Unsupported Propagation Rate
```

---

# 11. Phase 8 — MCP Capability Ecosystem
## 将已经稳定的 FMEA 能力模块化输出

## 11.1 进入条件

只有当下面接口已经稳定：

```text
SystemModelTool
FailureKnowledgeTool
FMEAValidationTool
FMEAGenerationService
```

才开始 FMEA MCP 化。

---

## 11.2 MVP 8 功能

暴露第一组 MCP Tools：

```text
get_systems
get_component
get_functions
get_requirements

find_failure_modes
find_failure_causes
get_failure_evidence

generate_fmea_candidates
validate_fmea
get_review_status
```

---

## 11.3 必须自己编写（S）

### S8-1 FMEA MCP Tool Contract

领域语义必须自己定义。

### S8-2 Authorization / write boundary

例如：

```text
read system facts
read failure knowledge
generate candidate

≠

publish official FMEA
modify approved model
```

### S8-3 Tool response schema

### S8-4 MCP contract tests

---

## 11.4 可以直接复用（D）

### Official MCP Python SDK

项目：

https://github.com/modelcontextprotocol/python-sdk

用途：

- MCP Server；
- MCP Client；
- tools；
- resources；
- prompts；
- stdio；
- Streamable HTTP。

复用等级：

**D**

不要自己设计 RPC/tool discovery protocol。

---

### MCP Reference Servers

项目：

https://github.com/modelcontextprotocol/servers

用途：

学习：

- server structure；
- tool contract；
- filesystem；
- git；
- resources；
- security boundary。

复用等级：

**R/D**

---

## 11.5 可直接复用/包装的 MCP 清单

| MCP | URL | 本项目用途 | 建议 |
|---|---|---|---|
| SYSMOD SysML MCP | https://github.com/Open-MBEE/sysmod-sysmlv2-api | SysML model query reference | 包装/借鉴 |
| Neo4j MCP | https://github.com/neo4j/mcp | Graph query | 直接复用 |
| Qdrant MCP | https://github.com/qdrant/mcp-server-qdrant | Vector search | 直接复用 |
| Docling MCP | https://github.com/docling-project/docling-mcp | Document processing | 直接复用 |
| MCP Filesystem | https://github.com/modelcontextprotocol/servers | Dev/tooling | 直接复用 |
| MCP Git | https://github.com/modelcontextprotocol/servers | Dev/tooling | 直接复用 |
| LangChain MCP Adapter | https://github.com/langchain-ai/langchain-mcp-adapters | LangGraph 消费 MCP | 直接复用但锁版本 |

---

## 11.6 一个非常重要的原则

MCP 应该包裹：

```text
stable capability
```

而不是创造：

```text
domain capability
```

正确：

```text
FMEA Domain
   ↓
FMEA Service
   ↓
MCP Adapter
```

错误：

```text
MCP Server
   ↓
里面临时写所有 FMEA 业务逻辑
```

---

# 12. Phase 9 — Dynamic FMEA / Design Change
## 从静态分析升级到设计变更驱动的增量 FMEA

## 12.1 目标

输入：

```text
Model Version N
Model Version N+1
```

输出：

```text
Model Diff
Affected Elements
Affected Functions
Affected Failure Modes
Affected FMEA Rows
Re-analysis Tasks
```

---

## 12.2 MVP 9 功能

至少支持变化：

```text
component added
component removed
connection changed
function reallocated
requirement changed
interface changed
```

并找出受影响 FMEA。

---

## 12.3 必须自己编写（S）

### S9-1 Canonical Model Diff

### S9-2 Change Classification

### S9-3 Impact Rules

例如：

```text
function allocation changed
→ old component FMEA affected
→ new component FMEA required
```

### S9-4 FMEA dependency index

### S9-5 Incremental graph rerun

只重新执行：

```text
affected subgraph
```

而不是每次完整 FMEA。

---

## 12.4 可以直接复用（D/R）

### SysML v2 API Cookbook

https://github.com/Systems-Modeling/SysML-v2-API-Cookbook

尤其参考：

```text
Project
Commit
Branch
Tag
```

recipe。

### SysML v2 API Services

https://github.com/Systems-Modeling/SysML-v2-API-Services

提供 repository/version access 基础。

### Git diff 算法思想

只作为类比，不直接把文本 diff 等同模型 diff。

---

## 12.5 MCP 复用

未来可以暴露：

```text
get_model_diff
get_affected_fmea
reanalyze_affected_items
```

但 Diff Engine 和 Impact Engine 应属于自研 Domain/Application。

---

## 12.6 MVP 9 验收标准

准备一个模型：

```text
V1
→ controlled change
→ V2
```

Ground Truth 标注：

```text
affected FMEA rows
unaffected FMEA rows
```

计算：

```text
Affected-item Recall
Affected-item Precision
Update Omission Rate
```

---

# 13. 哪些阶段不需要“自主编程”大量基础设施

这是 Claude Code 最应该牢记的表。

| Phase | 能力 | 建议来源 | 类型 |
|---|---|---|---|
| 0 | Validation Schema | Pydantic | D |
| 0 | Test | pytest | D |
| 0 | Lint/Format | Ruff | D |
| 1 | SysML parser | OpenSysML | D/W |
| 1 | SysML source examples | OMG SysML-v2-Release | D |
| 1 | Repository API | SysML-v2-API-Services | D/W |
| 1 | API traversal examples | SysML-v2-API-Cookbook | R/D |
| 1 | SysML MCP reference | SYSMOD API MCP | W/R |
| 2 | Schema runtime | Pydantic | D |
| 3 | DataFrame | pandas | D |
| 3 | Excel | openpyxl | D |
| 4 | Graph DB | Neo4j | D |
| 4 | RDF/OWL | n10s / RDFLib | D |
| 4 | Document parse | Docling | D |
| 4 | Document MCP | Docling MCP | D/W |
| 4 | Vector DB | Qdrant | D |
| 4 | Vector MCP | Qdrant MCP | D/W |
| 4 | Graph MCP | Neo4j MCP | D/W |
| 5 | Agent Runtime | LangGraph | D |
| 5 | MCP → LangGraph | langchain-mcp-adapters | D/W |
| 6 | Interrupt/Persistence | LangGraph | D |
| 7 | Graph algorithms | Neo4j / NetworkX | D |
| 8 | MCP protocol | official MCP Python SDK | D |
| 8 | MCP examples | official servers | D/R |
| 9 | SysML project/version API | SysML API Services | D/W |

---

# 14. 哪些部分必须坚持自主设计

## 14.1 第一优先级核心资产

### Canonical System Model

理由：

这是未来：

```text
SysML
BOM
PLM
Capella
Simulink
```

等所有数据源进入 FMEA Agent 的统一桥梁。

---

### SysML → FMEA Semantic Mapping

这是：

```text
MBSE
 ↓
FMEA
```

之间的领域映射，不应该交给通用框架决定。

---

### FMEA Domain Model

决定：

```text
Item
Function
Mode
Cause
Effect
Control
Risk
Evidence
Review
```

真正语义。

---

### Evidence Model

未来系统的可信度核心。

---

### Cause–Mode–Effect Validator

属于领域正确性，不是通用 LLM 能力。

---

### Failure Propagation

项目重要研究点。

---

### Benchmark + Ground Truth

别人无法替你决定什么叫“正确 FMEA”。

---

### Dynamic FMEA Impact Logic

未来研究差异化的重要部分。

---

# 15. 复用项目总索引

以下项目在 2026-09-03 基线规划中建议持续关注。

## 15.1 SysML / MBSE

### OMG SysML v2 Release
https://github.com/Systems-Modeling/SysML-v2-Release

角色：

```text
standard
examples
model library
benchmark source
```

---

### SysML v2 Pilot Implementation
https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation

角色：

```text
reference implementation
semantic cross-check
```

---

### SysML v2 API Services
https://github.com/Systems-Modeling/SysML-v2-API-Services

角色：

```text
repository
REST API
project/commit access
```

---

### SysML v2 API Cookbook
https://github.com/Systems-Modeling/SysML-v2-API-Cookbook

角色：

```text
API recipes
traversal patterns
project/version patterns
```

---

### OpenSysML
https://github.com/Open-MBEE/OpenSysML

角色：

```text
file parser/runtime
Python integration
gRPC
```

---

### SYSMOD SysML v2
https://github.com/MBSE4U/sysmod-sysmlv2

角色：

```text
Delivery Drone
methodology-aware example
benchmark
```

---

### SYSMOD SysML v2 API / MCP
https://github.com/Open-MBEE/sysmod-sysmlv2-api

角色：

```text
SysML API wrapper
MCP pattern
methodology-specific agent interface
```

状态原则：

> 当前按研究/包装参考使用，不作为 Canonical System Model 的真源。

---

### SysML v2 Applications and Examples
https://github.com/Open-MBEE/SysML-v2-Applications-and-Examples

角色：

```text
CubeSat
Spacecraft
aerospace benchmark
```

---

## 15.2 Knowledge / RAG

### Neo4j Python Driver
https://github.com/neo4j/neo4j-python-driver

### neosemantics
https://github.com/neo4j-labs/neosemantics

### RDFLib
https://github.com/RDFLib/rdflib

### Qdrant
https://github.com/qdrant/qdrant

### Docling
https://github.com/docling-project/docling

---

## 15.3 Agent

### LangGraph
https://github.com/langchain-ai/langgraph

### LangChain MCP Adapters
https://github.com/langchain-ai/langchain-mcp-adapters

---

## 15.4 MCP

### MCP Python SDK
https://github.com/modelcontextprotocol/python-sdk

### Official MCP Reference Servers
https://github.com/modelcontextprotocol/servers

### Neo4j MCP
https://github.com/neo4j/mcp

### Neo4j Labs MCP
https://github.com/neo4j-contrib/mcp-neo4j

### Qdrant MCP
https://github.com/qdrant/mcp-server-qdrant

### Docling MCP
https://github.com/docling-project/docling-mcp

---

# 16. 复用依赖的治理规则

开源项目不能只写入 requirements 后就结束。

每个关键依赖建议维护：

```text
docs/research/dependency_inventory.md
```

至少记录：

| Field | 内容 |
|---|---|
| Name | 项目名 |
| URL | GitHub |
| Role | 在 FMEA Agent 中承担什么 |
| Reuse Type | D/W/R |
| Version | 实验版本 |
| Commit | 必要时记录 |
| License | 许可证 |
| Adapter | 是否有自己的 Adapter |
| Contract Test | 是否有 |
| Replacement | 如果项目失效如何替换 |
| Risk | 已知问题 |

---

# 17. 外部项目升级原则

对以下核心依赖：

```text
OpenSysML
SysML API
LangGraph
MCP SDK
langchain-mcp-adapters
Neo4j
Docling
Qdrant
```

不要自动追最新版。

升级流程：

```text
Read changelog
   ↓
Create branch
   ↓
Upgrade one dependency
   ↓
Run contract tests
   ↓
Run regression benchmark
   ↓
Record ADR if architecture affected
   ↓
Merge
```

尤其 MCP 当前需要锁版本。

---

# 18. Claude Code 每阶段开发模板

Claude Code 在开始一个 Phase/Epic 时使用：

```text
Read:
- CLAUDE.md
- FMEA_AGENT_FOUNDATION_GUIDE.md
- FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md
- PROGRESS.md
- relevant ADRs
- relevant dependency docs

For the current phase:

1. List the MVP acceptance criteria.
2. Separate work into:
   - SELF-BUILD
   - WRAP
   - DIRECT-REUSE
   - REFERENCE-ONLY
3. Search existing repository before adding dependencies.
4. Inspect upstream project APIs before writing adapters.
5. Do not implement next-phase features.
6. Write contract tests around external dependencies.
7. Implement core FMEA semantics inside our own domain layer.
8. Run verification and current-phase benchmark.
9. Update dependency_inventory.md and PROGRESS.md.
```

---

# 19. 每阶段完成报告模板

Claude Code 完成阶段时必须报告：

```text
# Phase Completion Report

## MVP
- What can the system do now?

## Self-built
- Which project-specific capabilities were implemented?

## Reused
- Which libraries/repos were directly reused?

## Wrapped
- Which external systems are behind adapters/MCP?

## Tests
- Unit:
- Integration:
- Contract:
- Benchmark:

## Metrics
- Relevant current-phase metrics

## Known Limitations

## Deferred to Next Phase

## Dependency Risks

## Recommendation
- Is the phase ready to close?
```

---

# 20. 推荐当前立即执行的 Epic

现在不要把任务命名为：

```text
Build FMEA Agent
```

应该拆为：

```text
Epic 00
Repository Engineering Foundation

Epic 01
SysML Fact Access

Epic 02
Canonical System Model

Epic 03
FMEA Domain Core
```

当前最值得第一个真正实现的技术 Epic 是：

> **Epic 01 — SysML-to-Canonical-System-Model Foundation**

但它应实际分成：

```text
01A
SysML File Access

01B
SysML Repository Access

01C
Canonical Mapping

01D
Cross-adapter Consistency Benchmark
```

---

# 21. 第一个大里程碑

## Milestone A — FMEA Agent Core Foundation

由：

```text
Phase 0
+
Phase 1
+
Phase 2
+
Phase 3
```

构成。

验收 Demo：

```text
真实 SysML v2 模型
      ↓
SysML Adapter
      ↓
Canonical System Model
      ↓
FMEA Item / Function Context
      ↓
Deterministic FMEA Domain
```

此时：

> **即使没有 LLM，也应该已经是一套结构良好的 FMEA 软件内核。**

如果做不到，不应该进入 Agent 推理阶段。

---

# 22. 第二个大里程碑

## Milestone B — Evidence-grounded FMEA Agent

由：

```text
Phase 4
+
Phase 5
+
Phase 6
```

构成。

验收：

```text
System Facts
   +
Failure Knowledge
   +
Evidence
   ↓
LLM Candidate
   ↓
Validation
   ↓
Human Review
```

这是第一个真正可以称作：

> **FMEA Agent**

的版本。

---

# 23. 第三个大里程碑

## Milestone C — MBSE-aware Failure Reasoning

Phase 7。

验收：

```text
Failure
  ↓
SysML/Function/Flow constrained propagation
  ↓
Local Effect
  ↓
Higher Effect
  ↓
End Effect
```

此阶段开始形成明显科研特色。

---

# 24. 第四个大里程碑

## Milestone D — FMEA Agent Platform

Phase 8–9。

做到：

```text
Other Agents
     ↓
MCP
     ↓
FMEA capabilities

and

Design Change
     ↓
Incremental FMEA
```

---

# 25. 最终技术思想

整个开发过程中，始终区分：

```text
Infrastructure
vs
Research Core
```

Infrastructure：

```text
OpenSysML
SysML API
Neo4j
Docling
Qdrant
LangGraph
MCP SDK
```

这些应尽可能复用。

Research Core：

```text
Canonical System Model
SysML → FMEA Mapping
Failure Ontology / Schema
Evidence Model
FMEA Workflow
KG/RAG Fusion Strategy
Cause–Mode–Effect Validation
Failure Propagation
Benchmark / Ground Truth
Dynamic FMEA
```

这些必须掌握在本项目自己的代码和文档中。

一句话：

> **不要通过重复开发基础设施证明能力；要通过设计正确的 FMEA 工程语义、证据链、推理流程和评测体系形成项目价值。**

---

# 26. Claude Code 的最终判断规则

当 Claude Code 准备创建一个新模块时，先问：

```text
Is this FMEA-specific?
```

如果答案是：

```text
No
```

优先搜索已有项目并复用。

如果答案是：

```text
Yes
```

继续问：

```text
Is this one of our core domain semantics?
```

如果是：

```text
Yes
→ self-build and test carefully
```

如果不是：

```text
Wrap an existing capability
```

这应成为整个 FMEA Agent 生命周期中的默认开发哲学。
