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

Status: **1A COMPLETE — CONDITIONAL_GO；1B Snapshot Contracts: COMPLETE（2026-09-04）**

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
1A Feasibility Spike          — COMPLETE（CONDITIONAL_GO）
1B Snapshot Contracts         — COMPLETE
1C-0 Dependency Reproduction — COMPLETE（PYPI_PIN_CONFIRMED，2026-09-04）
1C OpenSysML Adapter          — NEXT（implementation not started）
1D Canonical Mapping
1E Workflow Integration
1F Benchmark & Release
```

关键文档：

- Spec：`docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
- Plan：`docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`
- Spike：`docs/research/OPENSYSML_FEASIBILITY_SPIKE.md`
- 1C-0 复现报告：`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`
- Mapping：`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`
- Snapshot 契约：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
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

### 1C-0 Dependency Reproduction Gate 结果（2026-09-04）

结论：**PYPI_PIN_CONFIRMED**（报告：`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`）。

- PyPI `opensysml==0.4.0`（wheel sha256 `d3a9cfea…`，Apache-2.0）在独立 throwaway venv 重跑全部 13 项 MVP-1C probe，与 MVP-1A checkout 证据逐项 **MATCH**。
- PyPI wheel 与 checkout client source 内容等价（28/28 文件，0 真实差异，仅 26 个 EOL 差异）。
- C2 pin 确认：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（commit `99e02003…`，sha256 `0b188ec…`）。
- **F1（1C Adapter Profile 必须记录）**：`Model.hash` 不是纯内容哈希 —— 服务端 `digestOf` = SHA256(name + per-file content sha256)；同一文件以不同路径字符串加载得到不同 hash。正式语义：`model_hash` = 当前模型 load context 下的 fingerprint；不是 Canonical ID、不是跨路径稳定 identity、不是跨机器永久稳定 identity、不得用于判断工程实体跨版本 identity。adapter 必须定义 documented deterministic path normalization / load policy；禁止自行重新实现 hash 算法以获取"稳定 hash"（一律原样记录 OpenSysML 返回值）。
- 孤儿进程检查修正：digest-link 进程名为 `sysml-grpc-0b188ec140872c0f`，须用通配符 `sysml-grpc*` 检查；本轮验证连接打开 1 进程、close 后 0、全流程后 0。
- 未修改 OpenSysML repo、未修改 FMEA production code、未修改 pyproject.toml。

### Milestone 0 — Runnable Agent Skeleton

Status: **COMPLETE (2026-09-04)**

Goal:

> Run an end-to-end FMEA-shaped workflow using local fixtures and replaceable in-memory adapters before integrating real SysML, KG/RAG or MCP infrastructure.

## Current Epic

### Epic 01 — MVP-1 Real System Facts

Status: **1A COMPLETE — CONDITIONAL_GO；1B Snapshot Contracts COMPLETE（2026-09-04）；1C OpenSysML Adapter NEXT**

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

1C-0 Dependency Reproduction Gate 已通过（PYPI_PIN_CONFIRMED），允许开始 1C。

执行 MVP-1C OpenSysML Adapter（见 `docs/plans/MVP_1_IMPLEMENTATION_PLAN.md` Stage 3）：

```text
OpenSysMLFileAdapter
→ public OpenSysML API（load/Model/Symbol/query/Diagnostic）
→ SysMLFactSnapshot（MVP-1B 契约，见 docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md）
```

1C 必须遵守：

- 契约不变：`src/fmea_agent/adapters/sysml/contracts.py` 为 parser-neutral 稳定契约；
- dependency pin：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（C2，1C-0 已复现确认）；
- `Model.hash` 语义（F1）：hash = load context fingerprint（name+content digest），随加载路径字符串变化；adapter 定义 documented deterministic load/path policy；禁止自行重实现 hash 算法；
- 单文件子集 + unresolved-import 显式诊断（C1）；
- owner_id 经真实 traversal/parent context 建立，禁止 FQN 前缀字符串推导；
- performed ActionUsage typing 缺失 → `type_facts=None`，不推断（C4）；
- exception 边界：`SysMLLoadError` / `SysMLParseError` / `UnsupportedSysMLElement`；
- contract tests 覆盖版本 pin、`children()` 方法形态、unresolved-import 夹具。

不得开始 Canonical Mapping（1D）。

## MVP-1B Completion Record (2026-09-04)

Delivered per TDD（RED → GREEN）：

- `src/fmea_agent/adapters/sysml/contracts.py` — 六个 parser-neutral 契约模型：
  `SysMLSource` / `SysMLElementFact`（含 `SysMLTypeFacts`）/ `SysMLRelationshipFact` /
  `SysMLDiagnostic` / `SysMLFactSnapshot`；`extra="forbid"`；必填字符串 `min_length=1`；
  `JsonValue` 严格 JSON-safe；`load_status: Literal["ok","partial"]`
- 校验规则 V1–V10（唯一 source_id、relationship source 可解析 / target open-world、
  ok⇒无 error 诊断、file mode 必填 path、owner 不强制解析）
- `tests/test_sysml_contracts.py`（55 tests）+ `tests/fixtures/sysml/snapshot_minimal.json`
- 规范性文档 `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
  （parser-neutral identity/diagnostic 语义；OpenSysML evidence 归 adapter profile）
- `CANONICAL_SYSTEM_MODEL_SPEC.md` §11 更新指向新契约

Acceptance verified:

```text
pytest 134 passed（79 MVP-0 + 55 MVP-1B）   PASS
ruff check .                                PASS
mypy src                                    PASS
无 opensysml/grpc/protobuf import           PASS（AST 级测试固化）
无 FMEA/Canonical 字段                      PASS（schema 白名单测试固化）
JSON round-trip 语义相等                     PASS
pyproject.toml 未修改                        PASS
MVP-0 regression                            PASS
```

C1–C4 覆盖见 `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` §9。
