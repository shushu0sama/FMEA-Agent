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
| `Package` | source context | TENTATIVE | namespace/context，不直接等同 `System` |
| `PartDefinition` | type metadata | NEEDS_RESEARCH | **不得直接映射 `Component`** |
| named `PartUsage` | `Component` | TENTATIVE | MVP-1 重点验证 |
| selected root/top `PartUsage` | `System` | TENTATIVE | 必须有 root-selection policy |
| nested `PartUsage` | `Component` + parent | TENTATIVE | owner/containment 需真实验证 |
| `ActionDefinition` | behavior/type metadata | NEEDS_RESEARCH | MVP-1 不直接等同 `Function` |
| named `ActionUsage` | `Function` candidate | TENTATIVE | 验证 intended/performed semantics |
| performed action usage | `Function` candidate | TENTATIVE | 优先研究 |
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

System root 必须有显式 policy，例如：

```text
CLI-selected root usage
single validated top-level usage
explicit configuration
```

每条 `TENTATIVE → CONFIRMED` 至少记录：

```text
source repo
source commit
source model path
observed OpenSysML representation
expected canonical output
test case
```
