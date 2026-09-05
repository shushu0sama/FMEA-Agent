# FMEA Agent 当前进度

> 当前项目状态快照，不是完整历史。
> 历史执行记录：`docs/records/`（Stage Closeout / Release Record）。
> 治理规则：`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`。

## 项目

```text
Architecture baseline: v0.1
Development mode:      Runnable Vertical Slice First
FMEA profile:          AIAG & VDA FMEA Handbook（First Edition, 2019；
                       Seven-Step Approach）
Current branch:        fix/pre-mvp2-review-remediation
Review Baseline:       369f09d
Current MVP:           MVP-1 Real System Facts（stable） /
                       Pre-MVP-2 Governance Baseline（planning docs）
MVP status:            RELEASED（v0.1.0 = original capability release；
                       v0.1.1 = current stable docs-only patch）
Current Stage:         1F Benchmark & Release（ACCEPTED）
Post-Release Patch:    DONE（Independent Patch Review = ACCEPTED；
                       annotated tag v0.1.1）
```

## 总体路线图

```text
MVP-0 COMPLETE（v0.0.1 tagged）
MVP-1 Real System Facts       — RELEASED（v0.1.0 capability；v0.1.1 stable patch）
MVP-2 Real Failure Knowledge  — NOT_STARTED（PLANNING ONLY；
                                  Spec baseline prepared for review）
MVP-3 Evidence-grounded LLM
MVP-4 AIAG-VDA Risk & Semantic Validation
MVP-5 Human Review
MVP-6 Failure Propagation
MVP-7 Aerospace Benchmark
MVP-8 MCP
MVP-9 Dynamic FMEA
```

## 当前 MVP — MVP-1 Real System Facts

目标：

> 用真实 SysML v2 File Mode 替换 MVP-0 的 synthetic system fixture，
> 同时保持 MVP-0 的 Failure Knowledge、Risk、Optimization 和上层
> Workflow 尽量不变。

链路（已实现）：

```text
真实 .sysml
→ OpenSysML（opensysml==0.4.0 + sysml-grpc v0.4.3）
→ SysMLFactSnapshot
→ Canonical System Model
→ CanonicalSystemModelRepository
→ 现有 LangGraph Workflow
```

范围内：

```text
System / Component / Function / SourceReference
OpenSysML File Mode（单文件子集）
minimal mapping + notices
minimal benchmark（1F）
```

范围外（MVP-1 明确延后）：

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

## Stage 状态

```text
1A Feasibility Spike          — COMPLETE（CONDITIONAL_GO）
1B Snapshot Contracts         — COMPLETE
1C-0 Dependency Reproduction  — COMPLETE（PYPI_PIN_CONFIRMED，2026-09-04）
1C OpenSysML Adapter          — COMPLETE（2026-09-04）
1D Canonical Mapping          — COMPLETE（2026-09-04）
1E Workflow Integration       — ACCEPTED（2026-09-04）
1F Benchmark & Release        — ACCEPTED（2026-09-04，Independent Release
                                 Review @ 369f09d）
Release Closeout              — DONE（2026-09-04，master merge 2871b23c
                                 --no-ff + annotated tag v0.1.0）
Post-Release Patch            — DONE（2026-09-04，annotated tag v0.1.1；
                                 docs-only consistency correction）
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

## 当前阻塞项

无阻塞项。MVP-1 = RELEASED，发布流程已全部完成：

```text
merge master（2871b23c，--no-ff）
→ master verification（PASS，LOCAL）
→ final release closeout
→ annotated tag v0.1.0（original capability release）

Post-Release Audit 已完成（唯一 blocker：benchmark report 两处
current-state drift）→ v0.1.1 docs-only patch → Independent Patch
Review ACCEPTED → annotated tag v0.1.1（current stable patch）
```

MVP-2 实现的前置阻塞项：

```text
Implementation Plan NOT_STARTED pending independent review of
docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md.
Production implementation NOT_STARTED.
```

## 当前已知限制

- 单文件子集；用户文件 import 不支持（C1，unresolved import 显式诊断）。
- `Model.hash` = load-context fingerprint（F1），非跨路径/跨版本稳定 identity。
- performed ActionUsage 无 typing facts（C4），禁止推断。
- `Component.component_type` 保持 `None`（无证据规则）。
- system-level Function 暂不被 workflow 分析目标使用。
- partial Snapshot 的 workflow 接入行为未单独覆盖。

## 当前开放研究问题

1. 跨 SysML commit 的精确规范标识策略。
2. 最终的 SysML-v2 → FMEA 语义映射规则。
3. 航空航天示例的 Ground Truth 构建流程。
4. 证据置信度的定义方式。
5. AIAG-VDA 风险表与 AP 规则的许可或授权来源。
6. MVP-1/2 之后的最优 KG/向量融合策略。
7. 流、接口、状态与功能之间的传播语义。
8. MVP-2 针对现有仅有名称的 Neo4j 图的实体解析策略。
9. 未来只读 Neo4j 适配器的凭证与配置政策。

## 当前验收基线

```text
pytest:          223 passed（LOCAL，Windows；212 基线 + 11 benchmark）
ruff:            check . PASS（LOCAL）
mypy:            src strict PASS（LOCAL）
real E2E:        typed_inside_probe.sysml → workflow PASS（suite 内）
benchmark:       B0 PASS / B1 PASS（docs/evaluation/MVP_1_BENCHMARK_REPORT.md）
sysml-grpc:      0 orphan processes（LOCAL）
master verification:
                 PASS（LOCAL，release closeout @ v0.1.0）
CI:              GitHub Actions NOT CONFIGURED
```

## 当前补充治理状态

- G0A 基线：`4d38489f92c41ffa906c6d0b79a4fd34d6ecb422`，完整保留。
- G0A + G0A-L Independent Review：`CHANGES_REQUIRED`；发现 C-1、I-1、I-2、I-3。
- Pre-MVP-2 Governance：`READY_FOR_FINAL_RE_REVIEW`；repository-side blocker 已修复；
  用户已于 2026-09-05 确认 provider-side credential 状态为
  `USER_CONFIRMED_REVOKED_OR_ROTATED`。该状态仅基于用户确认，未由 Codex、API 或
  provider 独立验证。
- G0A-L 状态与本次验证证据：`docs/records/G0A_L_DOCUMENTATION_LOCALIZATION.md`。
- G0A-R 记录：`docs/records/G0A_R_PRE_MVP_2_REVIEW_REMEDIATION.md`。
- Credential 处置记录：
  `docs/records/security/2026-09-05_CREDENTIAL_EXPOSURE_REMEDIATION.md`。
- 文档默认语言：zh-CN，保留英文技术标识符及原始代码块。
- MVP-2 production implementation：`NOT_STARTED`。
- MVP-2 Implementation Plan：`NOT_STARTED pending spec review`；本次不创建 Plan。

## 下一步

MVP-1 = RELEASED（v0.1.0 = 原始能力发布；
v0.1.1 = 当前稳定文档补丁）。发布后补丁状态为
DONE（独立补丁审核 ACCEPTED；附注 tag 为 v0.1.1）。

下一步先执行 **Final Independent Re-review of C-1 only**。只有复审 `ACCEPTED` 后，
才可进入 **G0B MVP-2 Implementation Planning**。原规划顺序保留如下：

```text
1. Final independent re-review of C-1 credential remediation only:
   - `docs/records/security/2026-09-05_CREDENTIAL_EXPOSURE_REMEDIATION.md`
   - `docs/records/G0A_R_PRE_MVP_2_REVIEW_REMEDIATION.md`
2. After review acceptance, create `docs/plans/MVP_2_IMPLEMENTATION_PLAN.md`.
禁止:     开始 MVP-2 production implementation before spec review
```

Patch 详情：`docs/records/MVP_1/MVP_1_POST_RELEASE_PATCH.md`。

## 历史记录

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
