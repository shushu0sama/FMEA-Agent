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
MVP-1 Review Baseline: 369f09d
C-1 Review Baseline:   70052a0（ACCEPTED，2026-09-05）
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

MVP-1 发布无阻塞项。MVP-1 = RELEASED，既有发布流程已全部完成：

```text
merge master（2871b23c，--no-ff）
→ master verification（PASS，LOCAL）
→ final release closeout
→ annotated tag v0.1.0（original capability release）

Post-Release Audit 已完成（唯一 blocker：benchmark report 两处
current-state drift）→ v0.1.1 docs-only patch → Independent Patch
Review ACCEPTED → annotated tag v0.1.1（current stable patch）
```

MVP-2 规划与实现边界：

```text
C-1 final re-review: ACCEPTED（仅限 credential remediation）。
G0B / Implementation Plan: NOT_STARTED；先完成独立数据源的信息对齐，
并明确 docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md 的 Spec 审查决定。
Production implementation: NOT_STARTED；不得在 Spec / Plan 门禁前实现。
```

## 当前已知限制

- 单文件子集；用户文件 import 不支持（C1，unresolved import 显式诊断）。
- `Model.hash` = load-context fingerprint（F1），非跨路径/跨版本稳定 identity。
- performed ActionUsage 无 typing facts（C4），禁止推断。
- `Component.component_type` 保持 `None`（无证据规则）。
- system-level Function 暂不被 workflow 分析目标使用。
- partial Snapshot 的 workflow 接入行为未单独覆盖。
- 最终 JSON 未完整保留内部来源引用、候选关联 ID、起因机理/证据和影响状态/证据；
  当前导出不能作为完整工程证据档案。需在真实知识输出契约及集成前明确修复。
- Python 包元数据仍为 `0.0.1`；原发布审核已将其列为非阻塞观察，包发布前需明确同步政策。
- 后续事项及适用边界：`docs/records/G0A_R_FINAL_C1_REVIEW.md` 第 5 节。

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

2026-09-05 在 `70052a0` 重新执行下列本地验证；生产代码、测试和依赖与 `v0.1.1` 无差异。

```text
pytest:          223 passed in 11.78s（LOCAL，Windows；212 基线 + 11 benchmark）
ruff:            check . PASS（LOCAL）
mypy:            src strict PASS（LOCAL）
real E2E:        typed_inside_probe.sysml → workflow PASS（suite 内）
benchmark:       B0 PASS / B1 PASS（docs/evaluation/MVP_1_BENCHMARK_REPORT.md）
sysml-grpc:      no-new-orphan regression PASS（suite 内，LOCAL）
uv lock:         --check --offline PASS（LOCAL）
master verification:
                 历史 PASS（LOCAL，release closeout @ v0.1.0；本次未重新运行 master）
CI:              GitHub Actions NOT CONFIGURED
```

## 当前补充治理状态

- G0A 基线：`4d38489f92c41ffa906c6d0b79a4fd34d6ecb422`，完整保留。
- G0A + G0A-L 原 Independent Review：`CHANGES_REQUIRED`；发现 C-1、I-1、I-2、I-3，历史保留。
- G0A-R 最终 C-1 独立复审：`ACCEPTED`（CRITICAL = 0 / IMPORTANT = 0 / MINOR = 0）；
  reviewer 为独立 Agent `/root/c1_final_review`，基线 `70052a0`。
- C-1 已关闭；该结论仅适用于凭证处置，不等于整个 MVP-2 Spec 获得批准。
  用户已于 2026-09-05 确认 provider-side credential 状态为
  `USER_CONFIRMED_REVOKED_OR_ROTATED`。该状态仅基于用户确认，未由 Codex、API 或
  provider 独立验证。
- G0A-L 历史状态与当时验证证据：`docs/records/G0A_L_DOCUMENTATION_LOCALIZATION.md`。
- G0A-R 记录：`docs/records/G0A_R_PRE_MVP_2_REVIEW_REMEDIATION.md`。
- 最终复审与本次 MVP-1 状态复核：`docs/records/G0A_R_FINAL_C1_REVIEW.md`。
- Credential 处置记录：
  `docs/records/security/2026-09-05_CREDENTIAL_EXPOSURE_REMEDIATION.md`。
- 文档默认语言：zh-CN，保留英文技术标识符及原始代码块。
- MVP-2 production implementation：`NOT_STARTED`。
- G0B / MVP-2 Implementation Plan：`NOT_STARTED`；后续先明确 Spec 审查决定与实施范围。

## 下一步

MVP-1 = RELEASED（v0.1.0 = 原始能力发布；
v0.1.1 = 当前稳定文档补丁）。发布后补丁状态为
DONE（独立补丁审核 ACCEPTED；附注 tag 为 v0.1.1）。

**C-1 最终复审已通过，MVP-1 按既有发布范围收尾。** 当前先完成 MVP-2 规划前的信息对齐。
用户最新进一步明确：近期希望有设计文档/BOM/SysML 输入、自然语言交互、自动检索与参考性推理、
前端 UI 和 FMEA 报告的端到端 Demo；目标约一周，允许放缓。
该目标超出现有仅检索的 MVP-2 草案。当前进行范围重对齐，阶段重排与 Demo 设计仍待确认，
详见[信息对齐第 9 节](docs/product/MVP_2_PREPLANNING_ALIGNMENT.md#9-完整问卷答复与-demo-目标澄清)。
用户已明确：**现有 SysML 与 Neo4j 数据独立，案例没有关系与重合**，不得假设同一案例配对。
已确认事实、待答问题及本轮文档盘点集中在
[规划前信息对齐](docs/product/MVP_2_PREPLANNING_ALIGNMENT.md)；Alignment status 为 `IN_PROGRESS`。

既有 MVP-2 检索目标仍保留：**真实知识检索可靠，无适用知识时正确返回无匹配**；
后续参考性推理须与检索结果区分，不能以生成内容伪装命中。
已完成本机 Neo4j、两份经用户确认由工程师审核的 Excel 及主要 SysML 来源目录的只读盘点，见
[输入数据盘点](docs/research/MVP_2_INPUT_DATA_INVENTORY_2026_09_05.md)。两表属不同分析层次／案例，同时保留；
用户进一步说明仅知道来源可信，不清楚具体审核范围；早先工程师审核陈述不构成逐字段签审证明。
希望利用 SysML 自动准备测试以减少人工工作，样例尚未建立。图表逐行对账、方法分类/评分版本、
验收样例和输出细节仍待对齐。

讨论参考：`docs/research/FMEA_INTELLIGENCE_REFERENCE_REVIEW_2026_09_05.md`（REFERENCE；
不替代 Spec / Plan，不表示已采用外部项目或已验证两组数据的工程对应关系）。

```text
1. 先对齐端到端 Demo 与检索阶段的范围，选择首个输入资料包并核查可行性。
2. 区分知识检索、身份解析和跨案例适用性；未回答的需求保持待定。
3. 信息对齐后修订和审查 MVP-2 Spec，再进入 G0B 并创建 Implementation Plan。
禁止: 开始 MVP-2 production implementation before spec / plan gates。
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
