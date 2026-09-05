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
Current branch:        codex/demo-v1-d2-input-contracts
MVP-1 Review Baseline: 369f09d
C-1 Review Baseline:   70052a0（ACCEPTED，2026-09-05）
Current MVP:           MVP-1 Real System Facts（stable） /
                       Demo V1 End-to-End FMEA（D2 input/evidence contracts）
MVP status:            RELEASED（v0.1.0 = original capability release；
                       v0.1.1 = current stable docs-only patch）
Current Stage:         Demo D2 输入/证据契约与旧导出修复（ACCEPTED）
Post-Release Patch:    DONE（Independent Patch Review = ACCEPTED；
                       annotated tag v0.1.1）
```

## 总体路线图

MVP 是正式能力里程碑；Demo V1 / D0–D7 是近期演示的内部实施步骤。
Demo 不替代或重编号 MVP，也不等同于 FMEA 方法七步法。当前先集成受限 MVP-2/3 能力供演示，
随后核对正式 MVP 差距、复用已有实现并分别验收。
详细对应关系见 [Demo Spec 第 1.1 节](docs/specs/DEMO_V1_END_TO_END_FMEA.md#11-mvp-路线与-demo-步骤的对应关系)。

```text
MVP-0 COMPLETE（v0.0.1 tagged）
MVP-1 Real System Facts       — RELEASED（v0.1.0 capability；v0.1.1 stable patch）
Demo V1 End-to-End FMEA       — D0/D1/D2 ACCEPTED；D3–D7 NOT_STARTED
MVP-2 Real Failure Knowledge  — NOT_STARTED（PLANNING ONLY；
                                  原草案作为完整检索阶段参考）
MVP-3 Evidence-grounded LLM
MVP-4 AIAG-VDA Risk & Semantic Validation
MVP-5 Human Review
MVP-6 Failure Propagation
MVP-7 Aerospace Benchmark
MVP-8 MCP
MVP-9 Dynamic FMEA
```

上表 MVP-2 的 NOT_STARTED 指正式独立阶段尚未开工，不要求未来忽略 Demo 中已实现的检索工作。
Demo 开工后应分别记录实际能力和正式验收状态，不能用任何单一状态隐藏部分完成情况。

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
Standalone MVP-2 G0B: NOT_STARTED（完整检索阶段未单独开工）。
Demo D0: ACCEPTED；新增 Demo Spec / Plan，复审决定见 D0 记录。
Demo D1/D2: ACCEPTED；D3–D7: NOT_STARTED。
```

## 当前已知限制

- 单文件子集；用户文件 import 不支持（C1，unresolved import 显式诊断）。
- `Model.hash` = load-context fingerprint（F1），非跨路径/跨版本稳定 identity。
- performed ActionUsage 无 typing facts（C4），禁止推断。
- `Component.component_type` 保持 `None`（无证据规则）。
- system-level Function 暂不被 workflow 分析目标使用。
- partial Snapshot 的 workflow 接入行为未单独覆盖。
- D2 已补齐旧 JSON 的 item/function ID、source_refs、候选关联 ID、起因机理/证据和影响状态/证据；
  原 CLI 仍不是自包含的完整 Demo 报告，D6 的报告导出尚未实现。
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

## 当前 D2 验证与审核状态

- [D2 记录](docs/records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)：范围、接口细化、验证与审核。
- LOCAL：修复后 `scripts/verify.py` → 334 passed in 18.87s；Ruff PASS；mypy src PASS（32 files）。
  新增 101 项 D2 测试；既有 CLI、SysML、B0/B1、D1 及 orphan 回归通过。
- 新增 optional extra `demo`：pypdf 6.17.0、openpyxl 3.1.5，传递 et-xmlfile 2.0.0；
  既有锁定版本未升级，`uv lock --check --offline` PASS。
- EXTERNAL_REVIEW：首次 CHANGES_REQUIRED 的两项发现已关闭；复审 `dde80fd` → 技术范围 ACCEPTED，
  0 CRITICAL / 0 IMPORTANT / 0 MINOR；334 passed in 20.14s，Ruff/mypy/lock/diff 及独立行列/ZIP 边界通过。
- Git：实现 `bdbdede`、修复 `dde80fd` 和审核记录 `ec83bba` 已提交并推送。
  此前 TLS 握手/连接超时在最终重试时恢复；远端已创建并跟踪同名实施分支。
- D3–D7 未实现；本次没有调用 DeepSeek/Neo4j，也不宣布完整 Demo 或工程质量通过。

## D1 验证与审核基线（已接受）

- D1 来源与收尾证据：[D1 记录](docs/records/DEMO_V1/D1_FIXED_CASE_AND_INPUT_PACK.md)。
- LOCAL：`scripts/verify.py` → 233 passed in 13.62s；Ruff PASS；mypy src PASS。
  其中新增 10 项 D1 测试，真实重读演示模型通过；既有 B0/B1 与 orphan 回归包含在全套中。
- LOCAL：`mypy src scripts/build_demo_inputs.py` PASS（25 source files）；
  `uv lock --check --offline` PASS。src、依赖与既有基准 gold 未改动。
- EXTERNAL_REVIEW：独立 Agent `/root/d1_independent_review` 于 `d1868a1` 判定 D1 ACCEPTED，
  CRITICAL=0 / IMPORTANT=0 / MINOR=0；独立 pytest 233 passed、Ruff/mypy PASS。
  额外三种 Git 换行配置及源覆盖保护验证通过，详情见 D1 记录。后续实际阶段见当前 D2 专节。
- 真实 DeepSeek/Neo4j/UI 与工程质量验收不在 D1 完成范围，本次未调用或验收。

## MVP-1 验收基线（既有发布能力）

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

2026-09-05 补充复核（起点 `648009ba5a571a15bb9706dabb95afb3f6db8bbd`）：

- [LLMRiskAnalyzer 核查](docs/research/LLMRISKANALYZER_REUSE_REVIEW_2026_09_05.md)：固定上游提交，
  分类 R；未发现许可证声明，不复制代码/数据或引入依赖，不改变 Demo Spec。
- [新会话启动说明](docs/README.md)补充实际 Git/阶段核对、顺序交接与并行写入边界；
  扩展既有 Stage 内交接模板，不另建长期状态台账。
- LOCAL 重新执行 `.venv/Scripts/python.exe scripts/verify.py`：223 passed in 12.23s；
  Ruff PASS；mypy PASS（24 source files）。包括现有 SysML/benchmark 回归，非 Demo live 验收。
- `740279c` 补充文档当时未创建 D1 资料包；当前 D1 状态与证据见上方 D1 专节及阶段记录。
  独立 D0 结论不扩展为补充文档或 D1 的新审核。

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
- 独立 MVP-2 G0B 未开工；当前工作入口转为 Demo D0 Spec/Plan 及其复审记录。

## 下一步

MVP-1 = RELEASED（v0.1.0 = 原始能力发布；
v0.1.1 = 当前稳定文档补丁）。发布后补丁状态为
DONE（独立补丁审核 ACCEPTED；附注 tag 为 v0.1.1）。

**C-1 最终复审已通过，MVP-1 按既有发布范围收尾。用户已同意端到端 Demo 方向。**
当前操作依据：

- [Demo 规格](docs/specs/DEMO_V1_END_TO_END_FMEA.md)：输入/分析/来源/报告/验收边界。
- [Demo 实施计划](docs/plans/DEMO_V1_IMPLEMENTATION_PLAN.md)：D1–D7 文件、接口与验证步骤。
- [D0 记录](docs/records/DEMO_V1/D0_SPEC_AND_PLAN.md)：准备核查、初审问题与后续复验。
- [D1 记录](docs/records/DEMO_V1/D1_FIXED_CASE_AND_INPUT_PACK.md)：固定资料、测试、基线变化与独立审核。
- [D2 记录](docs/records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)：输入/证据契约、文件载入及旧导出修复。

首例选定项目自有 `typed_inside_probe.sysml`，分析 hydraulicPump 下 motor 的 spin 功能；
资料包位于 [examples/demo_v1](examples/demo_v1/README.md)，真实解析及副本重读成功（0 diagnostics）；
生成器保留来源 SHA-256、CSM source IDs、未知数量/工况及根动作排除项。
D0 已核实 DeepSeek 官方接口 `deepseek-v4-pro`；D1 未调用 API 或检查凭据配置。
真实接入前在本机配置，不在聊天/Git记录密钥。

SysML 与 Neo4j 案例仍独立；无匹配、相关但适用性待确认、推理建议及查询失败分别展示。
两份 Excel 同时保留，审核范围只知来源可信；方法版本/来源覆盖与工程gold仍未核实。
Demo 可用自动测试减少人工准备，但不以同源派生资料或模型自己生成的答案验证工程正确率。
历史讨论见 [信息对齐台账](docs/product/MVP_2_PREPLANNING_ALIGNMENT.md)，现为 HISTORICAL。

下一步：在新主会话按既有 Plan 进入 D3 可独立验证的只读检索，不重复规划前问卷。
D2 实现、独立审核和远端保存已通过；D3–D7 仍未实现。
实施基线包含 `740279c`、路线澄清 `9d5c0a7`、D1 实现 `d1868a1`、D1 收尾 `35aa066` 及后续 D2 提交；
按实际 Git 最新记录恢复，不从旧 master 遗漏这些提交。
约一周为可放宽目标窗口；真实API/图/前端接入状态分别记录，不能以mock通过替代live验收。

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
