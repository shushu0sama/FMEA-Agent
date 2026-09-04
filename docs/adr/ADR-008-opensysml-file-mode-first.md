# ADR-008: MVP-1 优先采用 OpenSysML File Mode

**Status:** PROPOSED

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
