# SysML → Canonical System Model 映射矩阵
## MVP-1 v0.1

状态：

```text
CONFIRMED
TENTATIVE
NEEDS_RESEARCH
REJECTED
DEFERRED
```

## 初始矩阵

| SysML 来源概念 | Canonical 目标 | Status | MVP-1 规则 |
|---|---|---|---|
| `Package` | 来源上下文 | TENTATIVE | namespace/context，不直接等同 `System`；1D：产出 TENTATIVE notice |
| `PartDefinition` | 类型元数据 | NEEDS_RESEARCH | **不得直接映射 `Component`**；1D：产出 NEEDS_RESEARCH notice |
| 具名 `PartUsage` | `Component` | **CONFIRMED**（1D） | selected root 子树内的 named `PartUsage` → `Component` |
| 选定根 / 顶层 `PartUsage` | `System` | **CONFIRMED**（1D） | root-selection policy v1（见下） |
| 嵌套 `PartUsage` | `Component` + parent | **CONFIRMED**（1D） | parent = 最近的已映射 partUsage 祖先（root → `System.id`） |
| 未命名 `PartUsage` | 不映射 | NEEDS_RESEARCH | `System`/`Component` 要求 name；1D：产出 notice，不伪造 |
| 选定根子树之外的 `PartUsage` | 不映射 | DEFERRED | 多系统模型延后；1D：产出 DEFERRED notice |
| `ActionDefinition` | 行为 / 类型元数据 | NEEDS_RESEARCH | MVP-1 不直接等同 `Function`；1D：产出 notice |
| 具名 `ActionUsage`（typed → actionDef，最近 partUsage 祖先位于 selected root 子树） | `Function`（`allocated_to` = 该祖先的 canonical id） | **CONFIRMED**（1E） | typing 证据 + 真实 owner traversal；禁止 name/FQN 匹配 |
| typed `ActionUsage`（无 partUsage 祖先，package/file-level） | 不映射 | NEEDS_RESEARCH | 归属 selected System 无法确认；1E：产出 notice，不静默加入 |
| typed `ActionUsage`（位于其他 part 子树） | 不映射 | DEFERRED | 不归属 selected System；1E：产出 notice |
| performed action usage | `Function` candidate | NEEDS_RESEARCH | MVP-1A Spike：public facts 中 typing 链接缺失（C4），禁止发明类型关系；1D：产出 notice，不映射 |
| 未命名 `ActionUsage` | 不映射 | NEEDS_RESEARCH | `Function` 要求 name；1D：产出 notice |
| 其他 metatype（`attributeUsage` 等） | 不映射 | DEFERRED | 1D：产出 DEFERRED notice，不静默丢弃 |
| `RequirementUsage` | `Requirement` | DEFERRED | MVP-1 不实现 |
| `PortUsage` | `Port` | DEFERRED | MVP-1 不实现 |
| `InterfaceUsage` | `Interface` | DEFERRED | MVP-1 不实现 |
| `ConnectionUsage` | `Connection` | DEFERRED | MVP-1 不实现 |
| 与流相关的 usage | `Flow` | DEFERRED | MVP-1 不实现 |
| `StateUsage` | `State` | DEFERRED | MVP-1 不实现 |
| `AllocationUsage` | `Allocation` | DEFERRED | MVP-1 不实现 |

## 强制规则

禁止：

```text
PartDefinition == Component
every ActionDefinition == Function
display name == stable source ID
first PartUsage == System
```

System 根必须有显式策略。

## 根选择策略 v1（1D 已实现，2026-09-04）

```text
root_source_id 显式提供时：
    必须指向 Snapshot 中的 named partUsage，否则 CanonicalMappingError。
    该 partUsage 即为 System root。

未提供时（auto）：
    candidates = named partUsage 且无 partUsage 祖先
                 （沿 owner_id 链向上；链断裂/未知 owner 视为祖先不可确认，
                   保守地仍算 candidate）
    exactly 1 candidate  → 即 System root
    0 candidates         → CanonicalMappingError
    >1 candidates        → CanonicalMappingError（消息列出全部候选，
                           提示用 root_source_id 显式选择）
```

禁止 `first_part_usage` 或依赖 Snapshot 偶然顺序。

## Canonical 身份策略 v1（1D 已实现，2026-09-04）

- Canonical ID 由 Mapping 层生成：`system-1` / `component-N` / `function-N`
  （分类型计数器，按 Snapshot 元素顺序分配；同一 Snapshot 重复映射结果
  确定、相等）。
- 禁止把 OpenSysML `Symbol.id` 直接当作 Canonical ID。
- v1 Canonical ID 不承诺跨版本稳定（跨模型版本身份仍是开放研究问题 #1）。
- 来源身份原样保留于 `SourceReference.source_element_id`（追溯链：
  Canonical → SourceReference → Snapshot `SysMLSource`，含 `model_hash`
  load-context fingerprint）。

## 映射通知语义（1D 已实现，2026-09-04）

每个 Snapshot 元素要么映射为 `System` / `Component` / `Function`，要么产出
一条 `MappingNotice`（`source_id` + `status` + `message`），不静默丢弃：

- `source_id = None` 表示 模型级通知（当前仅 partial load 一条，
  状态 NEEDS_RESEARCH）；
- partial Snapshot（`load_status == "partial"`）仍映射已观察事实，并附
  模型级通知。

## 功能范围与分配策略 v1.1（1E 已实现，2026-09-04）

v1.0 曾把所有 typed actionUsage 映射为 `Function`（`allocated_to=[]`）——
无法满足 `SystemModelRepository.list_functions(element_id)`（依赖
`allocated_to`）的现有 workflow 契约（1E-0 Gate 失败证据见 PROGRESS.md）。

v1.1 规则（运行时探针证据：`tests/fixtures/sysml/models/typed_inside_probe.sysml`，
named typed ActionUsage 嵌于 PartUsage 内，OpenSysML 0.4.0 + sysml-grpc
v0.4.3 实测 ok=True，owner 经真实 traversal）：

```text
named typed ActionUsage（type_facts.resolved_id + resolved_kind == "actionDef"）
├─ 无 partUsage 祖先（package/file-level）
│     → NEEDS_RESEARCH notice（归属无法确认，不映射）
├─ 最近 partUsage 祖先位于 selected root 子树
│     ├─ 祖先 = root              → Function.allocated_to = [System.id]
│     ├─ 祖先已映射为 Component   → Function.allocated_to = [Component.id]
│     └─ 祖先无法表示（unnamed）  → NEEDS_RESEARCH notice
└─ 最近 partUsage 祖先在其他 part 子树
      → DEFERRED notice（不归属 selected System，不映射）
```

禁止：

```text
按名字匹配 Function 和 Component
按 FQN 字符串猜 owner
把 package-level action 自动分配给 part
补全 performed ActionUsage 的缺失 typing（C4）
```

`CanonicalSystemModel` 只包含能归属 selected System 的 Function。

不变量（2026-09-04 收尾修正，由领域校验器强制）：`Function.allocated_to`
的每个 target 必须解析到 `System.id` 或实际存在于 `components` 的
`Component.id`。Mapper 只以“Component 已实际创建”为分配证据——预生成的
`component-N` id 不作为证据（如 unnamed 祖先导致 named PartUsage 无法映射时，
其下的 typed ActionUsage 产出 NEEDS_RESEARCH notice，不分配）。

## 实现记录（TENTATIVE → CONFIRMED 证据）

| 规则 | 来源仓库 / commit | 来源模型路径 | 观察到的 OpenSysML 表示 | 预期 Canonical 输出 | 测试案例 |
|---|---|---|---|---|---|
| selected root `PartUsage` → `System` | PyPI `opensysml==0.4.0`（Apache-2.0）+ `sysml-grpc v0.4.3`（`99e02003…`） | `tests/fixtures/sysml/models/perform_probe.sysml` | `Symbol.kind='partUsage'`，`id='PerformProbe::hydraulicPump'`（FQN），`owner_id='PerformProbe'` | `System(id='system-1', name='hydraulicPump')` + SourceReference | `test_perform_probe_maps_end_to_end` |
| nested `PartUsage` → `Component` + parent | 同上 | 同上 | `…::hydraulicPump::motor`，owner 经 traversal = `…::hydraulicPump` | `Component(id='component-1', name='motor', parent_id='system-1')` | `test_perform_probe_maps_end_to_end` / `test_nested_part_usage_maps_to_component_with_parent` |
| 具名 `ActionUsage`（typed → actionDef）→ `Function` | 同上 | 同上 | `…::spin`：`TypeFacts(declared='Spin', resolved_id='PerformProbe::Spin', resolved_kind='actionDef')` | `Function(id='function-1', name='spin', allocated_to=[])`（v1.0，已由 1E 修订为 scope+allocated_to 规则） | `test_typed_action_usage_maps_to_function`（1D） |
| named typed `ActionUsage`（subtree 内）→ `Function` + `allocated_to` | 同上 | `tests/fixtures/sysml/models/typed_inside_probe.sysml`（runtime probe：ok=True） | `…::hydraulicPump::motor::spin`：`TypeFacts(declared='Spin', resolved_id='TypedInsideProbe::Spin', resolved_kind='actionDef')` + owner traversal = `…::motor`（partUsage） | `Function(name='spin', allocated_to=['component-1'])`；`pumpSpin` → `allocated_to=['system-1']` | `test_typed_inside_probe_maps_allocation_end_to_end` / `test_workflow_runs_end_to_end_on_real_sysml_model` |
| 多候选 / 无候选 → `CanonicalMappingError` | 同上 | `tests/fixtures/sysml/models/sibling_roots_probe.sysml` / `no_usage_probe.sysml` | 三个 top-level partUsage（`alphaPump`/`alphaMotor`/`betaPump`）；defs only | `CanonicalMappingError`（列出候选 / no candidate） | `test_sibling_roots_model_requires_explicit_root` / `test_no_usage_model_raises_canonical_mapping_error` |

实现：`src/fmea_agent/adapters/sysml/canonical_mapping.py`
（`CanonicalSystemMapper`）；aggregate 与 `MappingNotice`：
`src/fmea_agent/domain/system_model.py`；`CanonicalMappingError`：
`src/fmea_agent/adapters/sysml/exceptions.py`；以 Canonical 模型为来源的
仓库：`src/fmea_agent/adapters/inmemory/system_model.py`
（`CanonicalSystemModelRepository`，1E）。
