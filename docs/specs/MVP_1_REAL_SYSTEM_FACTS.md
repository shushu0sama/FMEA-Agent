# MVP-1 规格说明 — 真实系统事实

## 1. 目标

唯一主要目标：

> 使用真实 SysML v2 File Mode 替换 MVP-0 的合成系统 fixture，同时尽量不修改现有 FMEA Workflow。

目标链路：

```text
.sysml
→ OpenSysML
→ SysMLFactSnapshot
→ SysML → Canonical Mapping
→ Canonical System Model
→ SystemModelRepository
→ Existing LangGraph Workflow
```

## 2. 范围

第一版只要求：

```text
System
Component
Function
SourceReference
```

允许新增解析器层契约：

```text
SysMLSource
SysMLElementFact
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

## 3. 明确延后

```text
SysML Repository API
Requirement
Port
Interface
Connection
Flow
State
Allocation
Neo4j
Qdrant
Docling
MCP
real LLM
AIAG-VDA S/O/D/AP
Human Review
Failure Propagation
Dynamic FMEA
```

## 4. 参考环境

```text
Windows 11
VS Code
PowerShell
uv
```

本地研究工作区：

```text
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace
```

OpenSysML 检出目录：

```text
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML
```

绝对路径只用于本地 Spike，不得进入生产代码。

## 5. SysMLFactSnapshot 边界

`SysMLFactSnapshot` 是 parser/API 事实快照，不是 `Canonical System Model`。

建议：

```text
SysMLSource
- source_type
- source_path
- source_version?
- parser
- parser_version?
- model_hash?

SysMLElementFact
- source_id
- metatype
- name?
- owner_id?
- properties

SysMLRelationshipFact
- type
- source_id
- target_id

SysMLDiagnostic
- severity
- message
- locator?
```

Snapshot 不得包含 FMEA 字段。

## 6. OpenSysML 边界

生产代码只依赖 OpenSysML 公开接口。

禁止把以下类型泄漏到 domain/application：

```text
OpenSysML internal AST
gRPC generated types
Go internal packages
runtime-specific objects
```

推荐：

```text
OpenSysMLFileAdapter
→ SysMLFactSnapshot
→ project-owned mapping
→ Canonical System Model
```

## 7. 映射

所有 SysML → Canonical 规则必须在 `SYSML_TO_CANONICAL_MAPPING.md` 登记：

```text
CONFIRMED
TENTATIVE
NEEDS_RESEARCH
REJECTED
DEFERRED
```

禁止为完成 Demo 简化为：

```text
PartDefinition == Component
```

## 8. 错误处理

至少保留项目自有错误边界：

```text
SysMLLoadError
SysMLParseError
UnsupportedSysMLElement
CanonicalMappingError
```

OpenSysML 异常在适配器内转换。

## 9. 回归

MVP-0 的 79 个测试是回归基线。

MVP-1 不得破坏：

```text
demo workflow
Failure Knowledge fixture
Risk = NOT_EVALUATED
Optimization = SKIPPED
```

## 10. 验收标准

```text
[ ] Windows reference environment 可重复运行
[ ] 真实 .sysml 可被 OpenSysML 读取
[ ] Snapshot 不泄漏 OpenSysML internal types
[ ] 至少提取 System / Component / Function
[ ] SourceReference 可追溯
[ ] unsupported concept 有 diagnostics
[ ] Canonical mapping 有状态记录
[ ] existing upper workflow 不被重写
[ ] no KG/RAG/MCP/real LLM
[ ] pytest / ruff / mypy / diff-check 全通过
```
