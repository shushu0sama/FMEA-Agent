# FMEA Agent Progress

> Update this file at the end of every meaningful development session.

## Project Status

**Architecture baseline:** v0.1  
**Development mode:** Runnable Vertical Slice First  
**FMEA profile:** AIAG-VDA FMEA  
**Released baseline:** FMEA Agent v0.0.1 — MVP-0 COMPLETE
**Current target:** MVP-1 — Real System Facts

## Current Milestone

### Milestone 1 — Real System Facts

Status: **1A Feasibility Spike: COMPLETE — CONDITIONAL_GO（2026-09-04）**

Goal:

> 用真实 SysML v2 File Mode 替换 MVP-0 的 synthetic system fixture，同时保持 MVP-0 的 Failure Knowledge、Risk、Optimization 和上层 Workflow 尽量不变。

MVP-1 第一版范围：

```text
OpenSysML File Mode
SysMLFactSnapshot
System / Component / Function / SourceReference
minimal mapping
minimal benchmark
```

MVP-1 明确延后：

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

MVP-1 阶段：

```text
1A Feasibility Spike
1B Snapshot Contracts
1C OpenSysML Adapter
1D Canonical Mapping
1E Workflow Integration
1F Benchmark & Release
```

关键文档：

- Spec：`docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
- Plan：`docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`
- Spike：`docs/research/OPENSYSML_FEASIBILITY_SPIKE.md`
- Mapping：`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`
- Benchmark：`docs/evaluation/MVP_1_BENCHMARK_SPEC.md`
- ADR-008：`docs/adr/ADR-008-opensysml-file-mode-first.md`（已 ACCEPTED）
- 语言规范：`docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md`

### MVP-1A Spike 结果

结论：**CONDITIONAL_GO**（报告：`docs/research/OPENSYSML_SPIKE_REPORT.md`）。

Conditions（MVP-1B Snapshot Contracts 必须纳入）：

- **C1** — standalone 单文件子集；用户文件 import 不支持；unresolved import 必须产出显式 `SysMLDiagnostic`。
- **C2** — pin `opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（SHA-256 记录于 Spike 报告）。
- **C3** — source identity 为 name-derived FQN；rename 改变 source ID；不得宣称为跨版本稳定 Canonical identity。
- **C4** — performed ActionUsage public facts 不足以推导 function typing；禁止发明类型关系；Mapping 按 UNKNOWN / NEEDS_RESEARCH 处理。

### Milestone 0 — Runnable Agent Skeleton

Status: **COMPLETE (2026-09-04)**

Goal:

> Run an end-to-end FMEA-shaped workflow using local fixtures and replaceable in-memory adapters before integrating real SysML, KG/RAG or MCP infrastructure.

## Current Epic

### Epic 01 — MVP-1 Real System Facts

Status: **1A COMPLETE — CONDITIONAL_GO（2026-09-04）；1B Snapshot Contracts NEXT**

### Epic 00 — Bootstrap & Runnable MVP

Status: **COMPLETE — Tasks 0–10 complete; MVP-0 acceptance criteria verified (2026-09-04)**

Data contract clarified (2026-09-04):

> `FailureModeCandidate.item_id` / `function_id` hold stable domain IDs
> (e.g. `Component.id` / `Function.id`) — never display names.
> Fixture failure knowledge stays name-keyed for lookup; the workflow fills
> IDs from the loaded elements. Ports/adapters must not match names against
> `*_id` fields.

## Current MVP

### MVP-1 — Real System Facts

只替换 System Facts 来源；Failure Knowledge / Risk / Optimization / 上层 Workflow 保持 MVP-0 状态：

```text
真实 .sysml
→ OpenSysML
→ SysMLFactSnapshot
→ Canonical System Model
→ SystemModelRepository
→ 现有 LangGraph Workflow
```

### MVP-0 — Runnable Vertical Slice

Status: **COMPLETE (2026-09-04)**

Expected command shape:

```bash
python -m fmea_agent demo examples/simple_pump.json
```

Expected high-level flow:

```text
Input Fixture
  ↓
Planning & Preparation
  ↓
Structure Analysis
  ↓
Function Analysis
  ↓
Failure Analysis
  ↓
Risk Analysis (NOT_EVALUATED allowed)
  ↓
Optimization (SKIPPED allowed)
  ↓
Results Documentation
  ↓
Structured Candidate Output
```

## MVP-0 Required

- [x] installable Python package
- [x] minimal Canonical System Model
- [x] minimal FMEA Domain Model
- [x] Evidence / SourceReference
- [x] LangGraph workflow skeleton
- [x] in-memory system repository
- [x] in-memory failure-knowledge repository
- [x] mock/optional LLM interface (port + MockLLMClient; unused on default path)
- [x] `RiskStrategy` interface (port + NoOpRiskStrategy)
- [x] no-op / not-evaluated risk implementation
- [x] CLI demo
- [x] JSON output
- [x] unit tests
- [x] smoke test
- [x] verification script

## Explicitly Deferred from MVP-0

Do NOT block MVP-0 on:

- [ ] OpenSysML
- [ ] SysML Repository API
- [ ] Neo4j
- [ ] Qdrant
- [ ] Docling
- [ ] MCP
- [ ] full AIAG-VDA S/O/D/AP rules
- [ ] production UI
- [ ] multi-agent system
- [ ] dynamic FMEA
- [ ] failure-propagation research algorithm

## Next MVPs

### MVP-1 — Real System Facts

**当前里程碑（2026-09-04 起）。**

Replace fixture/in-memory system facts with:

```text
OpenSysML File Mode
→ SysMLFactSnapshot
→ Canonical System Model
```

SysML Repository API deferred to a later MVP-1.x iteration.

### MVP-2 — Real Failure Knowledge

Replace fixture failure knowledge with:

```text
Historical FMEA
+ structured graph/retrieval
```

### MVP-3 — Evidence-grounded LLM Generation

Use real LLM through `LLMClient` while preserving structured candidate output.

### MVP-4 — AIAG-VDA Risk & Semantic Validation

Implement authorized/verified risk rules and stronger FMEA validators.

### MVP-5 — Human Review

Formal interrupt/review/audit workflow.

### MVP-6 — Failure Propagation

SysML-aware propagation reasoning.

### MVP-7 — Aerospace Benchmark

Delivery Drone / CubeSat / spacecraft validation.

### MVP-8 — MCP Capability Layer

Expose stable capabilities through MCP.

### MVP-9 — Dynamic FMEA

Design-change impact and incremental re-analysis.

## Completed Planning Artifacts

- [x] FMEA Agent Foundation Guide
- [x] Staged Development & Reuse Guide
- [x] Bootstrap Pack v0.1
- [x] AIAG-VDA profile decision
- [x] Canonical model design direction
- [x] Benchmark specification baseline
- [x] dependency inventory baseline
- [x] ADR initialization
- [x] MVP-1 Development Pack（Spec / Plan / ADR-008 / Mapping / Benchmark / Spike / 语言规范）

## Open Research Questions

1. Exact canonical identity strategy across SysML commits.
2. Final SysML-v2 → FMEA semantic mapping rules.
3. Ground-truth construction process for aerospace examples.
4. Evidence-confidence formulation.
5. Licensed/authorized source for AIAG-VDA risk tables and AP rules.
6. Best KG/vector fusion strategy after MVP-1/2.
7. Propagation semantics across flow, interface, state and function.

## Current Blockers

No architectural blocker for MVP-1.

## MVP-0 Completion Record (2026-09-04)

Delivered in Tasks 6–10:

- `examples/simple_pump.json` — synthetic system fixture (stable IDs, display
  names separate, `source_refs` pointing at the fixture file)
- `examples/demo_failure_library.json` — name-keyed demo failure knowledge
  with evidence `demo-failure-library:001`
- `src/fmea_agent/cli/` — `python -m fmea_agent demo <fixture>` with
  `--failure-library` / `--output`; non-zero exit on invalid input
- smoke tests via subprocess (`tests/test_smoke_cli.py`) and CLI loader tests
- `scripts/verify.py` — cross-platform entry running pytest / ruff / mypy

Acceptance verified:

```text
demo run                      PASS  (python -m fmea_agent demo examples/simple_pump.json)
pytest 79 passed              PASS
ruff check .                  PASS
mypy src (strict)             PASS
no external services          PASS  (offline by construction)
risk.status == NOT_EVALUATED  PASS
optimization == SKIPPED       PASS
evidence traceable to fixture PASS
README run instructions       PASS
PROGRESS.md updated           PASS
```

## Next Action

执行 MVP-1B Snapshot Contracts（见 `docs/plans/MVP_1_IMPLEMENTATION_PLAN.md` Stage 2）：

```text
SysMLSource
SysMLElementFact
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

前置：MVP-1A 的 C1–C4 已写入本文件与 ADR-008，MVP-1B 契约必须显式覆盖：

- C1 single-file subset 与 unresolved-import diagnostic 契约；
- C2 版本 pin 的 source-version 字段设计；
- C3 source_id（FQN）与跨版本 identity 限制声明；
- C4 performed action 事实缺失的表达方式。

MVP-1B 之前不得实现 production Adapter / Mapping / Domain 修改。
Snapshots 不依赖 `opensysml` / gRPC / internal AST（Spike 已验证素材充分）。
