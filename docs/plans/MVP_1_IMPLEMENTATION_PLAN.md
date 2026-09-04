# MVP-1 Implementation Plan

执行顺序：

```text
Spike
→ Snapshot Contracts
→ OpenSysML Adapter
→ Canonical Mapping
→ Workflow Integration
→ Benchmark / Release
```

## Stage 1 — MVP-1A Spike

- 记录 OpenSysML commit/release。
- 验证 Windows Python client / sysml-grpc。
- 验证 load/parse、diagnostics、query/traversal、IDs、ownership。
- 运行自建 minimal model + 一个官方 Training example。
- 生成 `OPENSYSML_SPIKE_REPORT.md`。
- Gate：`GO` 或 `CONDITIONAL_GO`。

## Stage 2 — MVP-1B Snapshot Contracts

实现：

```text
SysMLSource
SysMLElementFact
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

要求：这些 contracts 不依赖 `opensysml` / gRPC / internal AST。

## Stage 3 — MVP-1C OpenSysML Adapter

- 根据 Spike 决定 dependency pin。
- 实现 `OpenSysMLFileAdapter`。
- file → public OpenSysML API → Snapshot。
- exception translation。
- diagnostics retention。
- contract tests。

## Stage 4 — MVP-1D Canonical Mapping

第一版只处理：

```text
selected root PartUsage → System
named nested PartUsage → Component
selected ActionUsage/performed behavior → Function candidate
```

必须有显式 root-selection policy。

更新 Mapping Matrix 状态。

## Stage 5 — MVP-1E Integration

- 实现 OpenSysML/canonical-backed `SystemModelRepository`。
- 接入现有 workflow。
- 不改变 Failure Knowledge / Risk / Optimization。
- 增加真实 `.sysml` E2E。

## Stage 6 — Benchmark & Docs

- B0 minimal fixture。
- 至少一个 external official model。
- 更新 PROGRESS / README / Dependency Inventory / Mapping Matrix。
- 完整验证。

## Completion

> 计划期验收清单（快照，不代表当前验收状态）。
> 实际执行与验收结果以 Git + `docs/records/MVP_1/` 为准。

```text
[ ] Spike GO
[ ] Snapshot stable
[ ] Adapter isolated
[ ] System/Component/Function mapping works
[ ] source trace retained
[ ] B0 PASS
[ ] external model PASS
[ ] MVP-0 regression PASS
[ ] no KG/RAG/MCP/real LLM
```
