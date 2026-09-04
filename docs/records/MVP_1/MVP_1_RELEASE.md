# MVP-1 — Real System Facts Release Record

Status: RELEASED（annotated release tag: v0.1.0）
Date: 2026-09-04

Commit 锚点（不可变历史基线；Markdown 不保存自身 SHA——自引用问题，
最终发布锚点是 release tag v0.1.0 所指向的 release-closeout commit）：

```text
Implementation Baseline:   30aee28  fix: prevent dangling function allocation
                                    and component parent ids（1E closeout fix）
Governance:                389f216  docs: establish development records and
                                    session governance
Benchmark RC:              4f73d22  test/docs: complete MVP-1F benchmark and
                                    release candidate
Review Evidence Amendment: 5da0f11  docs: add per-item release gate evidence
                                    to MVP-1F record
Release Gate Semantics:    d2c1767  docs: clarify release gate semantics,
                                    status vocabulary and commit anchors
Release Hygiene Closeout:  369f09d  docs: fix SysML provenance and
                                    third-party license notices
Review Baseline:           369f09d
Feature Release Baseline:  d0f091f  docs: accept MVP-1 independent release
                                    review
Master Before Merge:       f7abadd
Master Merge Commit:       2871b23c Merge branch
                                    'feature/mvp1-real-system-facts'
Merge Strategy:            --no-ff
Release Tag:               v0.1.0    annotated；最终不可变发布锚点
```

> Independent Release Review 已通过（ACCEPTED @ `369f09d`）。merge
> master 与 annotated tag v0.1.0 已完成；执行记录见 §Release Execution。

## MVP

MVP-1 Real System Facts

## Objective

> 用真实 SysML v2 File Mode 替换 MVP-0 的 synthetic system fixture，
> 同时保持 MVP-0 的 Failure Knowledge、Risk、Optimization 和上层
> Workflow 尽量不变。

Spec：`docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
Plan：`docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`

## Delivered Capabilities

```text
真实 .sysml
→ OpenSysML File Mode（opensysml==0.4.0 + sysml-grpc v0.4.3）
→ SysMLFactSnapshot（parser-neutral contracts）
→ Canonical System Model（System / Component / Function / SourceReference）
→ CanonicalSystemModelRepository
→ 现有 LangGraph Workflow（七阶段形态，未重写）
```

- 显式 root-selection policy（auto 唯一候选或显式 root_source_id；
  0/多候选 → CanonicalMappingError 列出候选）
- MappingNotice 体系：不静默丢弃任何 Snapshot 元素
- Function scope & allocation policy v1.1（真实 owner traversal 证据，
  禁止 name/FQN 匹配）
- 域层 invariant：Function.allocated_to / Component.parent_id 必须可解析
- diagnostics 一等公民；partial Snapshot 显式表达
- B0 + B1 benchmark（exact gold + metrics）

## Architecture Boundaries

- 外部技术全部位于 ports/adapters 之后：
  `domain/` 不依赖 opensysml / grpc / protobuf（AST 级测试固化）。
- SysMLFactSnapshot 不含 FMEA / Canonical 字段。
- Canonical ID 由 Mapping 层生成；source identity 保留于
  `SourceReference.source_element_id`。
- 契约文档：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`、
  `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`、
  `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`。
- 关键决策：ADR-008（File Mode first）。

## Stage Summary

```text
1A Feasibility Spike          COMPLETE（CONDITIONAL_GO）
1B Snapshot Contracts         COMPLETE
1C OpenSysML Adapter          COMPLETE（含 1C-0 PYPI_PIN_CONFIRMED）
1D Canonical Mapping          COMPLETE
1E Workflow Integration       ACCEPTED（含 closeout fix）
1F Benchmark & Release        ACCEPTED
```

Stage Records：见 §Historical Records。

## Benchmark

B0（project-owned exact）PASS；B1（官方外部模型，root=vehicle）PASS。
详情：`docs/evaluation/MVP_1_BENCHMARK_REPORT.md`。

## Regression

```text
MVP-0 全部历史 tests + 1B/1C/1D/1E tests 继续通过（223 passed 的一部分）
MVP-0 demo 运行无退化（risk=NOT_EVALUATED，optimization=SKIPPED）
```

## Dependency Baseline

```text
opensysml==0.4.0（PyPI，Apache-2.0，wheel sha256 见 Dependency Inventory）
sysml-grpc v0.4.3 windows-amd64（commit 99e02003…，sha256 0b188ec…）
pydantic 2.13.5 / pytest 8.4.2 / ruff 0.16.6 / mypy 1.20.2（uv.lock）
```

详见 `docs/research/DEPENDENCY_INVENTORY.md` 与
`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`。

## Known Limitations

- 单文件子集；用户文件 import 不支持（C1，显式诊断）。
- `Model.hash` = load-context fingerprint（F1），非跨路径/跨版本 identity。
- performed ActionUsage 无 typing facts（C4），禁止推断。
- `Component.component_type` 保持 `None`。
- system-level Function 暂不被 workflow 分析目标使用。
- B1 无 Function；Function metrics N/A。
- 无 CI（GitHub Actions NOT CONFIGURED；建议 release review 评估）。

## Deferred Capabilities

```text
SysML Repository API
Requirement / Port / Interface / Connection / Flow / State / Allocation
Neo4j / Qdrant / Docling / MCP
real LLM / AIAG-VDA S/O/D/AP
Human Review / Failure Propagation / Dynamic FMEA
```

## Open Research Questions

1. Exact canonical identity strategy across SysML commits.
2. Final SysML-v2 → FMEA semantic mapping rules.
3. Ground-truth construction process for aerospace examples.
4. Evidence-confidence formulation.
5. Licensed/authorized source for AIAG-VDA risk tables and AP rules.
6. Best KG/vector fusion strategy after MVP-1/2.
7. Propagation semantics across flow, interface, state and function.

## Release Gate

Gate 分两层：实现验证在本阶段完成（Implementation / Verification Gate）；
独立审核尚未进行（Independent Release Review）。

### Implementation / Verification Gate — PASS 16/16（LOCAL evidence）

```text
[x] MVP-0 regression PASS
[x] B0 exact mapping PASS
[x] OpenSysML contract tests PASS
[x] >=1 official external SysML integration PASS
[x] source trace PASS
[x] Canonical invariants PASS
[x] real SysML → workflow E2E PASS
[x] pytest PASS
[x] ruff PASS
[x] mypy strict PASS
[x] no orphan sysml-grpc regression
[x] no OpenSysML type leakage into domain
[x] no hard-coded local workspace paths
[x] no KG/RAG/MCP/real LLM scope leakage
[x] documentation governance complete
[x] MVP-1 Stage Records complete
```

逐项证据：`docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md` §8.1 与
`docs/evaluation/MVP_1_BENCHMARK_REPORT.md`。

### Independent Release Review — PASS

```text
[x] EXTERNAL_REVIEW — ACCEPTED
Review baseline: 369f09d

结论：
MVP-1A ACCEPTED
MVP-1B ACCEPTED
MVP-1C ACCEPTED
MVP-1D ACCEPTED
MVP-1E ACCEPTED
MVP-1F ACCEPTED
MVP-1 Real System Facts = RELEASE_READY

Production blocker:      NONE
Architecture blocker:    NONE
Benchmark blocker:       NONE
Release hygiene blocker: NONE
```

Review 通过后的执行步骤（已完成，证据见 §Release Execution）：

```text
merge feature/mvp1-real-system-facts → master  — 2871b23c（--no-ff）
master verification                             — PASS（LOCAL）
final release closeout                          — 本 Record
tag v0.1.0                                      — annotated
```

未通过：CHANGES_REQUIRED（本次未发生）。

## Release Execution

```text
Feature Release Baseline:    d0f091fc616ce6a9498250d78e49c384ae6d85ff
Independent Review Baseline: 369f09dc2d77a53ebd9f05c792abad66ccc488f5
Independent Release Review:  ACCEPTED
Master Before Merge:         f7abaddc53be2d1216e797aa68a5958eb735164b
Master Merge Commit:         2871b23c30f3b937b7b79b555672a4b009c27938
Merge Strategy:              --no-ff
Merge Tree Check:            merge tree == feature HEAD tree（git diff 无输出）
Release Tag:                 v0.1.0（annotated；指向 release-closeout commit）
Release Closeout Scope:      仅 release documentation + 最小 version policy；
                             零 production code / benchmark 语义改动
```

### Master Verification Evidence — LOCAL

```text
uv lock --check:   PASS
uv sync --frozen:  PASS
pytest:            223 passed
ruff check .:      PASS
mypy src strict:   PASS
MVP-0 demo:        PASS（Risk=NOT_EVALUATED，Optimization=SKIPPED）

B0: PASS
B1: PASS
real SysML E2E: PASS
OpenSysML contract regression: PASS
Canonical invariants: PASS
provenance hygiene: PASS

GitHub CI:
NOT CONFIGURED（全部 evidence 为 LOCAL，非 CI PASS）
```

## Recommended Next MVP

MVP-2 Real Failure Knowledge —— MVP-1 已 RELEASED。下一 Session：
MVP-1 Post-Release Audit；之后另开 Session 进行 MVP-2 Read-only
Planning。feature/mvp1-real-system-facts 分支暂不删除。

## Historical Records

```text
docs/records/MVP_1/MVP_1A_OPENSYSML_SPIKE.md
docs/records/MVP_1/MVP_1B_SNAPSHOT_CONTRACTS.md
docs/records/MVP_1/MVP_1C_OPENSYSML_ADAPTER.md
docs/records/MVP_1/MVP_1D_CANONICAL_MAPPING.md
docs/records/MVP_1/MVP_1E_WORKFLOW_INTEGRATION.md
docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md
docs/records/MVP_0/MVP_0_CLOSEOUT.md（MVP-0 基线）
```
