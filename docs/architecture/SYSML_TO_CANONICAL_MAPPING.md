# SysML → Canonical System Model Mapping Matrix
## MVP-1 v0.1

状态：

```text
CONFIRMED
TENTATIVE
NEEDS_RESEARCH
REJECTED
DEFERRED
```

## Initial Matrix

| SysML Source Concept | Canonical Target | Status | MVP-1 Rule |
|---|---|---|---|
| `Package` | source context | TENTATIVE | namespace/context，不直接等同 `System`；1D：产出 TENTATIVE notice |
| `PartDefinition` | type metadata | NEEDS_RESEARCH | **不得直接映射 `Component`**；1D：产出 NEEDS_RESEARCH notice |
| named `PartUsage` | `Component` | **CONFIRMED**（1D） | selected root 子树内的 named `PartUsage` → `Component` |
| selected root/top `PartUsage` | `System` | **CONFIRMED**（1D） | root-selection policy v1（见下） |
| nested `PartUsage` | `Component` + parent | **CONFIRMED**（1D） | parent = 最近的已映射 partUsage 祖先（root → `System.id`） |
| unnamed `PartUsage` | not mapped | NEEDS_RESEARCH | `System`/`Component` 要求 name；1D：产出 notice，不伪造 |
| `PartUsage` outside selected root subtree | not mapped | DEFERRED | 多系统模型延后；1D：产出 DEFERRED notice |
| `ActionDefinition` | behavior/type metadata | NEEDS_RESEARCH | MVP-1 不直接等同 `Function`；1D：产出 notice |
| named `ActionUsage`（typed → actionDef） | `Function` | **CONFIRMED**（1D） | 需 `type_facts.resolved_id` + `resolved_kind == "actionDef"` 证据 |
| performed action usage | `Function` candidate | NEEDS_RESEARCH | MVP-1A Spike：public facts 中 typing 链接缺失（C4），禁止发明类型关系；1D：产出 notice，不映射 |
| unnamed `ActionUsage` | not mapped | NEEDS_RESEARCH | `Function` 要求 name；1D：产出 notice |
| other metatypes（`attributeUsage` 等） | not mapped | DEFERRED | 1D：产出 DEFERRED notice，不静默丢弃 |
| `RequirementUsage` | `Requirement` | DEFERRED | MVP-1 不实现 |
| `PortUsage` | `Port` | DEFERRED | MVP-1 不实现 |
| `InterfaceUsage` | `Interface` | DEFERRED | MVP-1 不实现 |
| `ConnectionUsage` | `Connection` | DEFERRED | MVP-1 不实现 |
| flow-related usage | `Flow` | DEFERRED | MVP-1 不实现 |
| `StateUsage` | `State` | DEFERRED | MVP-1 不实现 |
| `AllocationUsage` | `Allocation` | DEFERRED | MVP-1 不实现 |

## Mandatory Rules

禁止：

```text
PartDefinition == Component
every ActionDefinition == Function
display name == stable source ID
first PartUsage == System
```

System root 必须有显式 policy。

## Root Selection Policy v1（1D 已实现，2026-09-04）

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

## Canonical Identity Policy v1（1D 已实现，2026-09-04）

- Canonical ID 由 Mapping 层生成：`system-1` / `component-N` / `function-N`
  （per-kind 计数器，按 Snapshot 元素顺序分配；同一 Snapshot 重复映射结果
  确定、相等）。
- 禁止把 OpenSysML `Symbol.id` 直接当作 Canonical ID。
- v1 Canonical ID 不承诺跨版本稳定（跨模型版本 identity 仍是 Open Research
  Question #1）。
- source identity 原样保留于 `SourceReference.source_element_id`（追溯链：
  Canonical → SourceReference → Snapshot `SysMLSource`，含 `model_hash`
  load-context fingerprint）。

## Mapping Notice Semantics（1D 已实现，2026-09-04）

每个 Snapshot 元素要么映射为 `System` / `Component` / `Function`，要么产出
一条 `MappingNotice`（`source_id` + `status` + `message`），不静默丢弃：

- `source_id = None` 表示 model-level notice（当前仅 partial load 一条，
  status NEEDS_RESEARCH）；
- partial Snapshot（`load_status == "partial"`）仍映射已观察事实，并附
  model-level notice。

## 1D Implementation Record（TENTATIVE → CONFIRMED 证据）

| Rule | source repo / commit | source model path | observed OpenSysML representation | expected canonical output | test case |
|---|---|---|---|---|---|
| selected root `PartUsage` → `System` | PyPI `opensysml==0.4.0`（Apache-2.0）+ `sysml-grpc v0.4.3`（`99e02003…`） | `tests/fixtures/sysml/models/perform_probe.sysml` | `Symbol.kind='partUsage'`，`id='PerformProbe::hydraulicPump'`（FQN），`owner_id='PerformProbe'` | `System(id='system-1', name='hydraulicPump')` + SourceReference | `test_perform_probe_maps_end_to_end` |
| nested `PartUsage` → `Component` + parent | 同上 | 同上 | `…::hydraulicPump::motor`，owner 经 traversal = `…::hydraulicPump` | `Component(id='component-1', name='motor', parent_id='system-1')` | `test_perform_probe_maps_end_to_end` / `test_nested_part_usage_maps_to_component_with_parent` |
| named `ActionUsage`（typed → actionDef）→ `Function` | 同上 | 同上 | `…::spin`：`TypeFacts(declared='Spin', resolved_id='PerformProbe::Spin', resolved_kind='actionDef')` | `Function(id='function-1', name='spin', allocated_to=[])` | `test_typed_action_usage_maps_to_function` / E2E |
| 多候选 / 无候选 → `CanonicalMappingError` | 同上 | `tests/fixtures/sysml/models/sibling_roots_probe.sysml` / `no_usage_probe.sysml` | 三个 top-level partUsage（`alphaPump`/`alphaMotor`/`betaPump`）；defs only | `CanonicalMappingError`（列出候选 / no candidate） | `test_sibling_roots_model_requires_explicit_root` / `test_no_usage_model_raises_canonical_mapping_error` |

1D 实现：`src/fmea_agent/adapters/sysml/canonical_mapping.py`
（`CanonicalSystemMapper`）；aggregate 与 `MappingNotice`：
`src/fmea_agent/domain/system_model.py`；`CanonicalMappingError`：
`src/fmea_agent/adapters/sysml/exceptions.py`。
