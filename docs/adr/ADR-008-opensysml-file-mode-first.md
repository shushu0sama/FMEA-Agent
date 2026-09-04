# ADR-008: MVP-1 优先采用 OpenSysML File Mode

**Status:** ACCEPTED

## Context

MVP-0 已完成。下一步只需把 synthetic System Facts 替换为真实 SysML v2。

本地已有 OpenSysML checkout，且长期架构仍保留 File Mode / Repository Mode / MCP Tool Mode。

## Decision

MVP-1 优先：

```text
.sysml
→ OpenSysML
→ SysMLFactSnapshot
→ Canonical System Model
```

Repository Mode（Systems Modeling API）继续保留，但不进入 MVP-1 第一版。

MCP 不进入解析层。

## Constraints

1. 先做 Feasibility Spike。
2. production code 只依赖 public API。
3. OpenSysML 经 Adapter 隔离。
4. Windows 11 为 reference environment。
5. MVP-0 regression 必须保持。
6. 不删除未来 Repository Mode。

## Acceptance

Spike 为 `GO` / `CONDITIONAL_GO` 后再将状态改为 `ACCEPTED`。

## Spike Outcome

MVP-1A Feasibility Spike（2026-09-04）结论：**CONDITIONAL_GO**。

报告：`docs/research/OPENSYSML_SPIKE_REPORT.md`。

Conditions（MVP-1B 之前必须接受并写入 Snapshot 契约）：

- **C1** — MVP-1 第一版限定 standalone 单文件子集（标准库 import 允许；用户文件 import 不支持）。unresolved import 必须产出显式 `SysMLDiagnostic`，不得静默降级。
- **C2** — 验证版本 pin：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（GitHub release，SHA-256 已记录于 Spike 报告）。
- **C3** — OpenSysML source identity 当前为 name-derived FQN；rename 会改变 source ID。不得把该 ID 宣称为跨版本稳定 Canonical identity。
- **C4** — performed ActionUsage 当前 public facts 不足以可靠推导 function typing。禁止发明类型关系；Mapping 阶段按 UNKNOWN / NEEDS_RESEARCH 处理。
