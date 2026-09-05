# ADR-008: MVP-1 优先采用 OpenSysML File Mode

**Status:** ACCEPTED

## 背景

MVP-0 已完成。下一步只需把合成系统事实替换为真实 SysML v2。

本地已有 OpenSysML 检出目录，且长期架构仍保留 File Mode / Repository Mode / MCP Tool Mode。

## 决策

MVP-1 优先：

```text
.sysml
→ OpenSysML
→ SysMLFactSnapshot
→ Canonical System Model
```

Repository Mode（Systems Modeling API）继续保留，但不进入 MVP-1 第一版。

MCP 不进入解析层。

## 约束

1. 先做可行性 Spike。
2. 生产代码只依赖公开 API。
3. OpenSysML 经适配器隔离。
4. Windows 11 为参考环境。
5. MVP-0 回归必须保持。
6. 不删除未来 Repository Mode。

## 验收

Spike 为 `GO` / `CONDITIONAL_GO` 后再将状态改为 `ACCEPTED`。

## Spike 结果

MVP-1A 可行性 Spike（2026-09-04）结论：**CONDITIONAL_GO**。

报告：`docs/research/OPENSYSML_SPIKE_REPORT.md`。

条件（MVP-1B 之前必须接受并写入 Snapshot 契约）：

- **C1** — MVP-1 第一版限定独立单文件子集（标准库 import 允许；用户文件 import 不支持）。unresolved import 必须产出显式 `SysMLDiagnostic`，不得静默降级。
- **C2** — 验证版本固定值：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（GitHub release，SHA-256 已记录于 Spike 报告）。
- **C3** — OpenSysML 来源身份当前为由名称派生的 FQN；重命名会改变来源 ID。不得把该 ID 宣称为跨版本稳定的 Canonical 身份。
- **C4** — performed ActionUsage 当前公开事实不足以可靠推导功能类型信息。禁止发明类型关系；Mapping 阶段按 UNKNOWN / NEEDS_RESEARCH 处理。
