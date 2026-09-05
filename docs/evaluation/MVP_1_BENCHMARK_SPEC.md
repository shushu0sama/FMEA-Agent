# MVP-1 基准规格说明

MVP-1 只评测：

> 真实 SysML → System Facts → Canonical System Model。

## B0 — 项目自有最小 Fixture

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

## B1 — OMG 训练示例

从本地 `SysML-v2-Release` 选择小型训练示例。

用途：外部官方语法兼容。

## B2 — 车辆示例

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

## 指标

```text
Component Extraction Precision/Recall
Function Extraction Precision/Recall
Parent/Containment Accuracy
SourceReference Completeness
Unsupported Element Reporting
```

小数据集优先使用精确预期集合。

## 契约测试

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

## 回归门禁

MVP-0 全部 79 个测试继续通过。

发布门禁：

```text
MVP-0 regression                 PASS
B0 exact mapping                 PASS
OpenSysML contract tests         PASS
>=1 external SysML integration   PASS
source trace                     PASS
pytest / ruff / mypy             PASS
```
