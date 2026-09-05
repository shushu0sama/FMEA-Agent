# Canonical System Model 规格说明
## 架构契约 v0.1

## 1. 目的

规范系统模型（Canonical System Model，CSM）是工程模型来源与 FMEA 逻辑之间的稳定集成边界。

上层不得直接依赖：

- OpenSysML runtime 对象；
- SysML REST payload；
- 供应商 MBSE 对象；
- MCP 响应模型。

转换链路如下：

```text
External Model
  ↓
Adapter
  ↓
SysMLFactSnapshot / source-native snapshot
  ↓
Canonical Mapping
  ↓
Canonical System Model
  ↓
FMEA Domain
```

## 2. 重要边界

### 2.1 SysMLFactSnapshot

第 1 阶段对象。

目的：

> 以最小语义规范化保留解析器 / API 返回的内容。

可以包含：

```text
source element ID
source metatype
name
raw attributes
ownership
raw relationships
source version
```

它**不是** Canonical System Model。

### 2.2 Canonical System Model

第 2 阶段对象。

目的：

> 以 FMEA 所需的、稳定且独立于工具的形式表达工程概念。

## 3. MVP-0 规范模型范围

为使可运行骨架工作，MVP-0 仅要求：

```text
System
Component
Function
SourceReference
Relationship(optional minimal)
```

不得让端口、接口、流、状态或分配阻碍 MVP-0。

## 4. v1 目标实体集

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

## 5. 共享身份类型

概念类型：

```python
CanonicalId = str
SourceElementId = str
VersionId = str
```

### 5.1 ID 要求

Canonical ID 应：

- 在同一规范模型版本内稳定；
- 在可行时具有确定性；
- 与显示名称解耦；
- 能单独保留来源 ID。

MVP-0 不最终确定跨 commit 身份逻辑。

### 5.2 SourceReference

最小字段：

```text
source_type
source_uri/path
source_element_id
source_version
adapter
```

可选字段：

```text
repository
project
commit
branch
locator
```

## 6. MVP-0 概念模型

### 6.1 System

```text
id
name
description?
source_refs[]
```

### 6.2 Component

```text
id
name
parent_id?
component_type?
source_refs[]
```

### 6.3 Function

```text
id
name
description?
allocated_to[]
requirement_ids[]
source_refs[]
```

### 6.4 Relationship

MVP-0 可以使用通用边：

```text
id
type
source_id
target_id
source_refs[]
```

仅在纵向切片需要时使用。

## 7. v1 目标模型

### Requirement

```text
id
name
text?
owner_id?
source_refs[]
```

### Port

```text
id
name
owner_id
direction?
type_ref?
source_refs[]
```

### Interface

```text
id
name
participant_ids[]
source_refs[]
```

### Connection

```text
id
source_element_id
target_element_id
kind?
source_refs[]
```

### Flow

```text
id
source_element_id
target_element_id
flow_item?
flow_kind?
source_refs[]
```

### State

```text
id
name
owner_id
source_refs[]
```

### Allocation

```text
id
source_id
target_id
allocation_type
source_refs[]
```

## 8. 仓库端口

上层应依赖类似以下形式的端口：

```python
class SystemModelRepository(Protocol):
    def get_system(self, system_id: str): ...
    def get_component(self, component_id: str): ...
    def list_components(self, system_id: str): ...
    def list_functions(self, element_id: str): ...
```

不得通过该接口暴露解析器 / 运行时类。

## 9. 校验规则

最低要求：

- ID 唯一；
- 关系端点存在；
- 在必要处能解析父引用；
- 来源引用保留来源信息；
- 未知 / 不支持的来源元素不导致整个导入崩溃；
- 允许部分模型，并明确标记。

## 10. 映射状态

每条 SysML→Canonical 语义映射都应能归入以下状态：

```text
CONFIRMED
TENTATIVE
NEEDS_RESEARCH
REJECTED
```

不得将暂定语义假设编码为不可逆的 schema 规则。

## 11. MVP-1 SysMLFactSnapshot

规范契约（2026-09-04 起）：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
（实现：`src/fmea_agent/adapters/sysml/contracts.py`）。

封装结构：

```json
{
  "source": { },
  "elements": [],
  "relationships": [],
  "diagnostics": [],
  "load_status": "ok"
}
```

该结构有意更贴近来源事实，而不是 FMEA 语义。

## 12. 跨适配器一致性目标

对于同一来源模型：

```text
OpenSysML Adapter
      ↓
Canonical A

SysML Repository Adapter
      ↓
Canonical B
```

预期：

```text
semantically equivalent(A, B)
```

差异必须能够诊断为：

- 来源 / 模型版本差异；
- 来源表示差异；
- 适配器映射缺陷；
- 不支持的语义。

## 13. 未来数据来源

未来适配器可以包括：

```text
BOM
PLM
Requirements database
Capella
Simulink
other MBSE
```

它们应映射到 Canonical System Model，而不是为适配各项技术修改 FMEA 领域层。

## 14. 非目标

CSM 不是：

- SysML 的完整替代；
- 完整数字孪生；
- CAD 几何模型；
- 失效本体；
- LLM 提示词格式。

它是 FMEA 所需的最小稳定工程事实模型。

## 15. MVP-1D 规范映射（2026-09-04）

已交付首个映射实现（`src/fmea_agent/adapters/sysml/canonical_mapping.py`、
`CanonicalSystemMapper`）：

- 聚合 `CanonicalSystemModel` = `system` + `components` + `functions` +
  `notices`（位于 `src/fmea_agent/domain/system_model.py`）；ID 唯一且组件父引用可解析（校验见 §9）；
- Canonical ID 由映射层生成（`system-1` / `component-N` / `function-N`，按快照顺序使用分类型计数器），绝不直接取自来源身份；不声称跨版本稳定（开放研究问题 #1）；来源身份保留在 `SourceReference.source_element_id`；
- 根选择和各概念映射规则，以及 CONFIRMED / TENTATIVE / NEEDS_RESEARCH / DEFERRED 状态：
  `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`；
- 无法选择系统根时（0 个或多个候选、无效显式根）抛出 `CanonicalMappingError`；
- 不支持 / 未映射的来源元素生成 `MappingNotice` 记录，绝不静默丢弃；部分快照映射已观察事实，并附加模型级 NEEDS_RESEARCH 通知。
