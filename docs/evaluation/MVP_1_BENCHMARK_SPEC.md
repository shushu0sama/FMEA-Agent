# MVP-1 Benchmark Specification

MVP-1 只评测：

> 真实 SysML → System Facts → Canonical System Model。

## B0 — Project-owned Minimal Fixture

建议：

```text
tests/fixtures/sysml/minimal_hydraulic.sysml
```

由本项目自行编写，人工精确标注：

```text
expected System
expected Components
expected Functions
expected parent relations
expected source identifiers
```

## B1 — OMG Training Example

从本地 `SysML-v2-Release` 选择小型 Training example。

用途：外部官方语法兼容。

## B2 — Vehicle Example

候选：

```text
VehicleUsages.sysml
SimpleVehicleModel.sysml
```

用途：

```text
definition/usage distinction
hierarchy
larger model
function semantics
```

## Metrics

```text
Component Extraction Precision/Recall
Function Extraction Precision/Recall
Parent/Containment Accuracy
SourceReference Completeness
Unsupported Element Reporting
```

小数据集优先 exact expected set。

## Contract Test

至少验证：

```text
valid file
invalid file
IDs
metatypes
names
ownership
diagnostics
```

## Regression Gate

MVP-0 全部 79 tests 继续通过。

Release Gate：

```text
MVP-0 regression                 PASS
B0 exact mapping                 PASS
OpenSysML contract tests         PASS
>=1 external SysML integration   PASS
source trace                     PASS
pytest / ruff / mypy             PASS
```
