# FMEA Agent Progress

> Update this file at the end of every meaningful development session.

## Project Status

**Architecture baseline:** v0.1  
**Development mode:** Runnable Vertical Slice First  
**FMEA profile:** AIAG-VDA FMEA  
**Current software target:** FMEA Agent v0.0.1

## Current Milestone

### Milestone 0 — Runnable Agent Skeleton

Status: **COMPLETE (2026-09-04)**

Goal:

> Run an end-to-end FMEA-shaped workflow using local fixtures and replaceable in-memory adapters before integrating real SysML, KG/RAG or MCP infrastructure.

## Current Epic

### Epic 00 — Bootstrap & Runnable MVP

Status: **COMPLETE — Tasks 0–10 complete; MVP-0 acceptance criteria verified (2026-09-04)**

Data contract clarified (2026-09-04):

> `FailureModeCandidate.item_id` / `function_id` hold stable domain IDs
> (e.g. `Component.id` / `Function.id`) — never display names.
> Fixture failure knowledge stays name-keyed for lookup; the workflow fills
> IDs from the loaded elements. Ports/adapters must not match names against
> `*_id` fields.

## Current MVP

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

Replace fixture/in-memory system facts with:

```text
OpenSysML / SysML API
→ SysMLFactSnapshot
→ Canonical System Model
```

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

Plan MVP-1 (`Real System Facts`): OpenSysML / SysML API → SysMLFactSnapshot
→ Canonical System Model. Do not start MVP-1 implementation without a
spec/plan. OpenSysML and SysML API remain unintegrated.
