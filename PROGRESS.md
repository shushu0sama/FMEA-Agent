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

Status: **1A CONDITIONAL_GO；1B Snapshot Contracts COMPLETE；1C OpenSysML Adapter COMPLETE；1D Canonical Mapping COMPLETE（2026-09-04）**

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
1C OpenSysML Adapter          — COMPLETE（2026-09-04）
1D Canonical Mapping          — COMPLETE（2026-09-04）
1E Workflow Integration       — NEXT（not started）
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

Status: **1A CONDITIONAL_GO；1B Snapshot Contracts COMPLETE；1C OpenSysML Adapter COMPLETE；1D Canonical Mapping COMPLETE（2026-09-04）；1E Workflow Integration NEXT**

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

MVP-1D 已 COMPLETE。执行 MVP-1E Workflow Integration（见
`docs/plans/MVP_1_IMPLEMENTATION_PLAN.md` Stage 5）：

```text
OpenSysML/canonical-backed SystemModelRepository
→ 接入现有 workflow
→ 真实 .sysml E2E
```

1E 要点：

- 不改变 Failure Knowledge / Risk / Optimization；
- 不重写现有上层 workflow；
- 1D 的 `CanonicalSystemModel`（`system`/`components`/`functions`）为
  repository 输入；
- `Function.allocated_to` / `Component.component_type` 填充规则尚未实现
  （1D 置空），1E 如需使用需先补 Mapping 规则并登记矩阵。

不得开始 Benchmark & Release（1F）。

## MVP-1D Completion Record (2026-09-04)

Delivered per TDD（RED → GREEN → REFACTOR，先测试后实现）：

- `src/fmea_agent/adapters/sysml/canonical_mapping.py` —
  `CanonicalSystemMapper.map_snapshot(snapshot, *, root_source_id=None)`
  → `CanonicalSystemModel`；显式 root-selection policy（显式
  `root_source_id` 或唯一 named top-level partUsage 候选；0/多候选 →
  `CanonicalMappingError` 列出候选）；subtree 内的 named PartUsage →
  `Component`（parent = 最近已映射 partUsage 祖先）；typed（`resolved_id`
  + `resolved_kind == "actionDef"`）named ActionUsage → `Function`；
  performed/untyped ActionUsage 不映射（C4，NEEDS_RESEARCH notice）；
  partDef/actionDef/package/其他 metatype 一律 notice，不静默丢弃
- `src/fmea_agent/domain/system_model.py` —
  `CanonicalSystemModel` aggregate（id 唯一、parent 可解析校验）+
  `MappingNotice`（CONFIRMED/TENTATIVE/NEEDS_RESEARCH/REJECTED/DEFERRED）
- `src/fmea_agent/adapters/sysml/exceptions.py` — `CanonicalMappingError`
- Canonical ID 由 Mapping 层生成（`system-1`/`component-N`/`function-N`，
  per-kind 计数器按 Snapshot 顺序；同 Snapshot 映射确定相等）；禁止把
  `Symbol.id` 当 Canonical ID；source identity 保留于
  `SourceReference.source_element_id`
- partial Snapshot 映射已观察事实 + model-level NEEDS_RESEARCH notice
- `tests/test_canonical_mapping.py` — 32 tests（unit 用 parser-neutral
  synthetic snapshots；integration 经真实 sysml-grpc v0.4.3 加载
  perform_probe / sibling_roots_probe / no_usage_probe / invalid_syntax）
- 新 fixtures：`sibling_roots_probe.sysml`（多顶层 package + 多候选 root）、
  `no_usage_probe.sysml`（defs only）
- 1C 小修正：`_walk()` 顶层 sibling 顺序修正为 `root.children()` 源顺序 +
  regression tests；orphan 检查改为 PID 集合比对（不误伤已有合法进程）
- 文档：`SYSML_TO_CANONICAL_MAPPING.md`（root-selection / canonical
  identity / notice 语义 + TENTATIVE→CONFIRMED 证据记录）、
  `CANONICAL_SYSTEM_MODEL_SPEC.md` §15、fixtures README

Acceptance verified:

```text
真实 .sysml → Snapshot → Canonical E2E         PASS（perform_probe 实测输出）
System / Component / Function 提取              PASS
SourceReference 可追溯                          PASS（source_element_id + 绝对路径）
Canonical ID ≠ source identity                 PASS（测试固化）
performed ActionUsage 不伪造 typing            PASS（C4）
unsupported concept 有 notice                   PASS（package/defs/attribute）
0 / 多候选 root → CanonicalMappingError        PASS
partial Snapshot → 已观察事实 + notice         PASS
Snapshot 遍历顺序 = 源文件顺序                 PASS（1C 修正 + regression）
orphan 检查 = PID 集合比对                     PASS
MVP-0 demo regression                          PASS（NOT_EVALUATED / SKIPPED）
pytest 196 passed（164 基线 + 32 新增）        PASS
ruff / mypy（strict）                          PASS
无 SystemModelRepository / workflow 修改       PASS
无 Neo4j/Qdrant/MCP/real LLM                   PASS
```

## MVP-1C Completion Record (2026-09-04)

Delivered per TDD（RED → GREEN，先测试后实现）：

- `src/fmea_agent/adapters/sysml/open_sysml_file.py` —
  `OpenSysMLFileAdapter.load(file_path) -> SysMLFactSnapshot`：
  `expanduser().resolve(strict=True)` 路径策略；显式
  `with opensysml.connect(version="v0.4.3")`；`Connection.load(strict=True)`；
  `ModelError` + partial model → partial Snapshot；真实 `Symbol.children()`
  traversal（RootNamespace 排除、owner_id 来自真实 parent）；
  `type_facts` 只取 declared/resolved_id/resolved_kind，空串 → None，
  全 None → `type_facts=None`（C4 不推断）；
  relationships 来自真实 `Symbol.specializations`（target open-world）；
  `Model.hash` 原样记录（F1）；Diagnostic 全字段翻译、`span=None` 不泄漏 protobuf
- `src/fmea_agent/adapters/sysml/exceptions.py` —
  `SysMLError` / `SysMLLoadError` / `SysMLParseError` / `UnsupportedSysMLElement`；
  exception chaining（`raise ... from exc`）；不依赖 grpc status code
- `pyproject.toml` — `opensysml==0.4.0` 精确 pin；`uv.lock` 经 `uv lock` 更新
  （grpcio 1.83.1 / protobuf 7.36.1 与 Spike 记录一致）
- 真实 `.sysml` fixtures（`tests/fixtures/sysml/models/`，Spike/1C-0 验证内容
  字节级复用）：`perform_probe.sysml` / `invalid_syntax.sysml` /
  `unresolved_import.sysml`（官方 Training Example 未修改，EPL-2.0，溯源见
  `tests/fixtures/sysml/README.md`）
- `tests/test_open_sysml_file_adapter.py` — 28 个 contract/integration tests

Acceptance verified:

```text
opensysml==0.4.0 精确 pin                       PASS
uv lock --check / uv sync --frozen              PASS
runtime = sysml-grpc v0.4.3                     PASS（server_info 实测）
valid .sysml → ok Snapshot                      PASS
invalid model → partial + diagnostics           PASS（2 error 诊断保留）
unresolved import → 4 error 显式诊断            PASS
RootNamespace 不进入 elements                   PASS
owner_id 来自真实 traversal parent              PASS
type_facts 不推断（definitions/performed = None）PASS
performed ActionUsage 无 fabricated typing       PASS（C4）
specializations 来自真实 OpenSysML facts         PASS（含 ScalarValues::Real 外部 target）
Model.hash 原样记录 + 同路径可重复 + 路径上下文相关 PASS（F1）
Snapshot JSON round-trip 语义相等               PASS
无 protobuf/grpc object 泄漏（span=None）        PASS
success/partial/error 后连接正确关闭            PASS
无 sysml-grpc* orphan process                   PASS（通配符检查 0）
无 Canonical Mapping / System / Component / Function PASS
无 KG/RAG/MCP/real LLM                          PASS
无硬编码本地路径                                 PASS
pytest 162 passed（134 基线 + 28 新增）          PASS
ruff / mypy（strict）                           PASS
MVP-0 demo regression（NOT_EVALUATED/SKIPPED）   PASS
```

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
