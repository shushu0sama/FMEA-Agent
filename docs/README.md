# FMEA Agent 文档导航

> 本文件为 Coding Agent 会话提供文档生命周期导航。保持精简，
> 详细事实以链接指向的文档为准。

## 新会话最小读取集

常规开发会话只需先读取：

1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/README.md`
4. `docs/specs/` 下的当前 Spec
5. `docs/plans/` 下的当前 Plan（存在时）
6. `docs/records/` 下的上一阶段记录

无需每次会话完整读取地基指南；修改长期架构、阶段策略或事实来源规则时再读。

## 当前会话恢复入口

当前入口为 Demo V1：读完 `AGENTS.md` 与 `PROGRESS.md` 后，读取
[Demo 规格](specs/DEMO_V1_END_TO_END_FMEA.md)、[实施计划](plans/DEMO_V1_IMPLEMENTATION_PLAN.md)
及最近的 [D3 记录](records/DEMO_V1/D3_READONLY_NEO4J_RETRIEVAL.md)；
[D2 记录](records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)保留输入/证据契约，
[D1 记录](records/DEMO_V1/D1_FIXED_CASE_AND_INPUT_PACK.md)保留固定资料的来源与审核，
[D0 记录](records/DEMO_V1/D0_SPEC_AND_PLAN.md)保留规划与审查来源。
D1–D7 的实际完成情况仍以 PROGRESS 和阶段记录为准。
MVP 能力路线继续保留；D1–D7 是 Demo 内部步骤，不是 MVP 编号替换。
新会话先核对 [Demo Spec 第 1.1 节对应表](specs/DEMO_V1_END_TO_END_FMEA.md#11-mvp-路线与-demo-步骤的对应关系)，
任务命名使用 `Demo V1 / Dn`，Demo 通过不等于正式 MVP-2/3/5/7 通过。
[信息对齐台账](product/MVP_2_PREPLANNING_ALIGNMENT.md)保存历史问答，
[原 MVP-2 草案](specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md)为完整检索阶段参考，不是当前全部 Demo 范围。

先运行以下只读检查：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log -5 --oneline
```

当前恢复预期分支见 `PROGRESS.md`；最近起点与分支来源见 D3 记录第 1 节。
若实际分支/提交不一致，先查明是否在旧 master、新 worktree 或未同步副本中；
不要自动切换、reset 或把旧文档当成当前状态。确认 checkout 含最新文档提交后再继续。
同一工作区切换聊天不会自动删除文件，但新工作树、换机器或只读取已发布 tag 不保证拥有最新本地收尾。

后续阶段切换时同步更新本节入口，避免留下第二份过期状态快照。

### 可直接复制的新会话启动语

```text
请继续当前 FMEA Agent 项目。先读取 AGENTS.md、PROGRESS.md、docs/README.md，
再按当前入口读取 Spec、Plan、上一阶段记录及有效的 Stage 内交接记录。
先核对实际仓库路径、branch、HEAD、工作区差异，简要报告：
当前已实现能力、当前 Stage、下一项未完成任务、范围边界、所依据的文件。
核对一致后，执行 PROGRESS 指定的下一阶段；不要重复已接受的需求问卷。
出现分支或记录差异时先追查来源，不自动 reset、丢弃修改或把旧 master 当成最新状态。
完成后运行适用验证，更新 Stage Record 与 PROGRESS，区分实现完成和独立审核通过。
```

这段启动语只提供恢复流程，不保存另一份阶段或 HEAD 快照。下一阶段若已推进，
按最新 PROGRESS 执行，不能长期照抄旧聊天中的“从 D1 开始”。

### 顺序切换与并行开发

- 顺序切换：旧会话结束写入后，新会话可在同一 checkout 继续；仍需执行上述核对。
- 同一 Stage 中断：使用[交接模板](records/templates/SESSION_HANDOFF_TEMPLATE.md)，
  保存到该 Stage 的 records 目录，并在 PROGRESS 链接唯一有效交接；恢复/收尾后标记历史状态。
- 同一 checkout 同时只保留一个实现写入者。其他会话可只读评审；独立实现任务使用各自 worktree/分支，
  明确范围，集成后重新验证。不能在另一个会话仍写入时替它切分支或提交所有差异。
- 新 worktree 必须包含当前规划及收尾提交；检查实际起点，不默认旧 master 已包含它们。
  `.venv`、ignored 本地输入、环境变量和服务连接需要独立核对；只记录配置变量名和资料位置，
  不读取或复制密钥到交接文档，也不把缺少配置悄悄改成 mock 成功。

Codex 的项目指令加载和 worktree 隔离机制参见
[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)与
[官方 worktree 文档](https://learn.chatgpt.com/docs/environments/git-worktrees)。
文件恢复流程能降低漂移并使差异可检查，不能保证模型永不误读；测试和独立审核仍是必要关口。

## 生命周期状态

`ACTIVE` = 当前操作依据。

`REFERENCE` = 长期背景或证据，按需读取。

`HISTORICAL` = 记录当时的实际情况或计划，不代表当前状态。

`SUPERSEDED` = 已由新文档取代，为追溯而保留。

## ACTIVE

- `AGENTS.md` — 跨 Coding Agent 的规范项目指令。
- `PROGRESS.md` — 当前项目状态、路线图与下一步。
- `README.md` — 项目总览与当前可运行能力。
- `docs/README.md` — 文档生命周期与导航。
- `docs/product/FMEA_AGENT_V1.md` — V1 产品与能力边界。
- [Demo V1 规格](specs/DEMO_V1_END_TO_END_FMEA.md) — 当前端到端演示范围及验收契约。
- [Demo V1 实施计划](plans/DEMO_V1_IMPLEMENTATION_PLAN.md) — D1–D7 任务、文件、接口及验证步骤。
- `docs/architecture/FMEA_AGENT_V1_ARCHITECTURE.md` — V1 架构边界。
- `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md` — CSM 契约。
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` — SysML 快照契约。
- `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md` — SysML 映射矩阵。
- `docs/domain/FMEA_PROFILE_V1.md` — FMEA 语义配置。
- `docs/domain/FMEA_GLOSSARY.md` — 术语权威来源。
- `docs/evaluation/BENCHMARK_SPEC.md` — 长期基准模型。
- `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` — 治理规则。
- `docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md` — 语言与术语政策。

## REFERENCE

- [原 MVP-2 草案](specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md) — 完整检索阶段参考，当前 Demo 范围以 Demo Spec 为准。
- [Demo D0 记录](records/DEMO_V1/D0_SPEC_AND_PLAN.md) — 规划起点、真实准备核查和独立审核。
- [Demo D1 记录](records/DEMO_V1/D1_FIXED_CASE_AND_INPUT_PACK.md) — 固定资料包、生成器、验证与独立审核。
- [Demo D3 记录](records/DEMO_V1/D3_READONLY_NEO4J_RETRIEVAL.md) — 只读检索、关系证据、验证与审核。
- [Demo D2 记录](records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md) — 输入/证据契约、文件载入、旧导出与审核。

- `CLAUDE.md` — Claude Code 兼容指令；在正式简化工具加载行为之前，
  保持与 `AGENTS.md` 一致。
- `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md` — 长篇架构地基指南。
- `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md` — 长篇阶段与复用指南。
- `docs/research/DEPENDENCY_INVENTORY.md` — 依赖与复用清单。
- `docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md` — 供 MVP-2 规划使用的现有 Neo4j 故障知识基线。
- [MVP-2 输入数据盘点](research/MVP_2_INPUT_DATA_INVENTORY_2026_09_05.md) — 原始 Excel、当前 Neo4j 查询及 SysML 目录实查；包含查询复现与来源限制。
- [FMEA 智能化参考项目](research/FMEA_INTELLIGENCE_REFERENCE_REVIEW_2026_09_05.md) — 2026-09-05 外部调研；仅供现有 Neo4j + SysML 数据后续讨论。
- [LLMRiskAnalyzer 复用评估](research/LLMRISKANALYZER_REUSE_REVIEW_2026_09_05.md) — 固定提交的源码与许可证检查；当前仅参考，不引入代码或改变 Demo 范围。
- `docs/research/OPENSYSML_SPIKE_REPORT.md` — MVP-1 OpenSysML 探索证据。
- `docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md` — OpenSysML 固定版本的复现证据。
- `docs/research/SYSML_SOURCE_CATALOG.md` — SysML 来源目录。
- `docs/adr/` — 已接受的架构决策记录。
- `docs/records/templates/` — 收尾、发布与会话交接模板。

## HISTORICAL

- [规划前信息对齐](product/MVP_2_PREPLANNING_ALIGNMENT.md) — 用户确认、未知事项与范围演化；已转入 Demo Spec。

- `docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md`
- `docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
- `docs/plans/MVP_0_IMPLEMENTATION_PLAN.md`
- `docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`
- `docs/prompts/MVP_1_CLAUDE_CODE_SESSIONS.md`
- `docs/records/MVP_0/`
- `docs/records/MVP_1/`
- `docs/records/bootstrap/PROJECT_CLEANUP_REPORT.md`

## SUPERSEDED

- `docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md` — Stage 内交接用途已由
  `docs/records/templates/SESSION_HANDOFF_TEMPLATE.md` 取代；
  常规会话启动采用上方最小读取集。

## 当前稳定发布

当前稳定发布 tag 为 `v0.1.1`，它是 MVP-1 Real System Facts 之上的文档补丁；
当前治理、Spec 审查及 Implementation Plan 状态统一见 [PROGRESS.md](../PROGRESS.md)。

## 文档语言与当前治理任务

项目自有文档以简体中文（zh-CN）为主体，技术标识符、状态、命令、路径和原始代码块保持 canonical form。
语言规则及检查关口见 `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` 第 14 节。
G0A-L 语言治理的范围、文件清单及验证证据见
`docs/records/G0A_L_DOCUMENTATION_LOCALIZATION.md`；该记录记载本次工作，不替代 `PROGRESS.md` 的当前状态职责。

G0A + G0A-L 的原审核、G0A-R 修复与后续 C-1 最终复审形成以下追踪链；
历史交付状态不替代 `PROGRESS.md` 的当前状态：

- [原修复记录](records/G0A_R_PRE_MVP_2_REVIEW_REMEDIATION.md)。
- [凭证处置记录](records/security/2026-09-05_CREDENTIAL_EXPOSURE_REMEDIATION.md)。
- [最终 C-1 复审与 MVP-1 状态复核](records/G0A_R_FINAL_C1_REVIEW.md)。
