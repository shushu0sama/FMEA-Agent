# MVP-1 实施计划

执行顺序：

```text
Spike
→ Snapshot Contracts
→ OpenSysML Adapter
→ Canonical Mapping
→ Workflow Integration
→ Benchmark / Release
```

## 阶段 1 — MVP-1A 可行性探查

- 记录 OpenSysML commit/release。
- 验证 Windows Python client / sysml-grpc。
- 验证 load/parse、diagnostics、query/traversal、IDs、ownership。
- 运行自建 minimal model + 一个官方 Training example。
- 生成 `OPENSYSML_SPIKE_REPORT.md`。
- Gate：`GO` 或 `CONDITIONAL_GO`。

## 阶段 2 — MVP-1B Snapshot 契约

实现：

```text
SysMLSource
SysMLElementFact
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

要求：这些 contracts 不依赖 `opensysml` / gRPC / internal AST。

## 阶段 3 — MVP-1C OpenSysML 适配器

- 根据 Spike 决定 dependency pin。
- 实现 `OpenSysMLFileAdapter`。
- 文件 → OpenSysML 公共 API → Snapshot。
- 异常转换。
- 诊断信息保留。
- 契约测试。

## 阶段 4 — MVP-1D 规范映射

第一版只处理：

```text
selected root PartUsage → System
named nested PartUsage → Component
selected ActionUsage/performed behavior → Function candidate
```

必须有显式 root-selection policy。

更新 Mapping Matrix 状态。

## 阶段 5 — MVP-1E 集成

- 实现 OpenSysML/canonical-backed `SystemModelRepository`。
- 接入现有 workflow。
- 不改变 Failure Knowledge / Risk / Optimization。
- 增加真实 `.sysml` E2E。

## 阶段 6 — 基准测试与文档

- B0 最小夹具。
- 至少一个外部官方模型。
- 更新 PROGRESS / README / Dependency Inventory / Mapping Matrix。
- 完整验证。

## 完成验收

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
