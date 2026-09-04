# FMEA Agent Progress

> CURRENT PROJECT STATE — 不是完整历史。
> 历史执行记录：`docs/records/`（Stage Closeout / Release Record）。
> 治理规则：`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`。

## Project

```text
Architecture baseline: v0.1
Development mode:      Runnable Vertical Slice First
FMEA profile:          AIAG-VDA FMEA（七步 workflow shape）
Current branch:        feature/mvp1-real-system-facts
Expected HEAD:         1F release-candidate commit（git log 为准）
Current MVP:           MVP-1 Real System Facts
MVP status:            RELEASE_CANDIDATE
Current Stage:         1F Benchmark & Release（READY_FOR_REVIEW）
```

## Overall Roadmap

```text
MVP-0 COMPLETE（v0.0.1 tagged）
MVP-1 Real System Facts       — RELEASE_CANDIDATE（1A–1F 完成，待独立 review）
MVP-2 Real Failure Knowledge  — 未开始（MVP-1 Release Review 之后另开 Session）
MVP-3 Evidence-grounded LLM
MVP-4 AIAG-VDA Risk & Semantic Validation
MVP-5 Human Review
MVP-6 Failure Propagation
MVP-7 Aerospace Benchmark
MVP-8 MCP
MVP-9 Dynamic FMEA
```

## Current MVP — MVP-1 Real System Facts

Goal:

> 用真实 SysML v2 File Mode 替换 MVP-0 的 synthetic system fixture，
> 同时保持 MVP-0 的 Failure Knowledge、Risk、Optimization 和上层
> Workflow 尽量不变。

Pipeline（已实现）:

```text
真实 .sysml
→ OpenSysML（opensysml==0.4.0 + sysml-grpc v0.4.3）
→ SysMLFactSnapshot
→ Canonical System Model
→ CanonicalSystemModelRepository
→ 现有 LangGraph Workflow
```

In Scope:

```text
System / Component / Function / SourceReference
OpenSysML File Mode（单文件子集）
minimal mapping + notices
minimal benchmark（1F）
```

Out of Scope（MVP-1 明确延后）:

```text
SysML Repository API
Requirement / Port / Interface / Connection / Flow / State / Allocation
Neo4j / Qdrant / Docling / MCP
real LLM
AIAG-VDA S/O/D/AP
Human Review
Failure Propagation
Dynamic FMEA
```

## Stage Status

```text
1A Feasibility Spike          — COMPLETE（CONDITIONAL_GO）
1B Snapshot Contracts         — COMPLETE
1C-0 Dependency Reproduction  — COMPLETE（PYPI_PIN_CONFIRMED，2026-09-04）
1C OpenSysML Adapter          — COMPLETE（2026-09-04）
1D Canonical Mapping          — COMPLETE（2026-09-04）
1E Workflow Integration       — ACCEPTED（2026-09-04）
1F Benchmark & Release        — READY_FOR_REVIEW（2026-09-04）
```

关键文档：

- Spec：`docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
- Plan：`docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`
- Spike：`docs/research/OPENSYSML_SPIKE_REPORT.md`
- 1C-0 复现：`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`
- Mapping：`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`
- Snapshot 契约：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- Benchmark：`docs/evaluation/MVP_1_BENCHMARK_SPEC.md`
- ADR-008：`docs/adr/ADR-008-opensysml-file-mode-first.md`

## Current Blockers

No architectural blocker. Release 流程阻塞点：等待 Independent Release
Review（不 merge master、不 tag、不开 MVP-2）。

## Current Known Limitations

- 单文件子集；用户文件 import 不支持（C1，unresolved import 显式诊断）。
- `Model.hash` = load-context fingerprint（F1），非跨路径/跨版本稳定 identity。
- performed ActionUsage 无 typing facts（C4），禁止推断。
- `Component.component_type` 保持 `None`（无证据规则）。
- system-level Function 暂不被 workflow 分析目标使用。
- partial Snapshot 的 workflow 接入行为未单独覆盖。

## Current Open Research Questions

1. Exact canonical identity strategy across SysML commits.
2. Final SysML-v2 → FMEA semantic mapping rules.
3. Ground-truth construction process for aerospace examples.
4. Evidence-confidence formulation.
5. Licensed/authorized source for AIAG-VDA risk tables and AP rules.
6. Best KG/vector fusion strategy after MVP-1/2.
7. Propagation semantics across flow, interface, state and function.

## Current Acceptance Baseline

```text
pytest:          223 passed（LOCAL，Windows；212 基线 + 11 benchmark）
ruff:            check . PASS（LOCAL）
mypy:            src strict PASS（LOCAL）
real E2E:        typed_inside_probe.sysml → workflow PASS（suite 内）
benchmark:       B0 PASS / B1 PASS（docs/evaluation/MVP_1_BENCHMARK_REPORT.md）
sysml-grpc:      0 orphan processes（LOCAL）
CI:              GitHub Actions NOT CONFIGURED
```

## Next Action

Independent Release Review（MVP-1 RELEASE_CANDIDATE）：

```text
review: docs/records/MVP_1/MVP_1_RELEASE.md
        docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md
        docs/evaluation/MVP_1_BENCHMARK_REPORT.md
decision: merge / release baseline（通过后才允许 merge master / tag）
之后:     另开 Session 规划 MVP-2（禁止本 Session 开始）
```

## Historical Records

```text
docs/records/MVP_0/MVP_0_CLOSEOUT.md
docs/records/MVP_1/MVP_1A_OPENSYSML_SPIKE.md
docs/records/MVP_1/MVP_1B_SNAPSHOT_CONTRACTS.md
docs/records/MVP_1/MVP_1C_OPENSYSML_ADAPTER.md
docs/records/MVP_1/MVP_1D_CANONICAL_MAPPING.md
docs/records/MVP_1/MVP_1E_WORKFLOW_INTEGRATION.md
docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md
docs/records/MVP_1/MVP_1_RELEASE.md
```
