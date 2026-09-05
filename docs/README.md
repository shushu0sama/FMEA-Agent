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

当前进行 MVP-2 规划前信息对齐，尚未进入 G0B。读完 `AGENTS.md` 与 `PROGRESS.md` 后，
优先读取[信息对齐台账](product/MVP_2_PREPLANNING_ALIGNMENT.md)，确认最新用户事实和待答问题，
再按需要读取 [MVP-2 草案](specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md)与
[最近收尾记录](records/G0A_R_FINAL_C1_REVIEW.md)。草案、旧记录和旧 Prompt 都不自动构成开工授权。

先运行以下只读检查：

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log -5 --oneline
```

当前恢复预期分支见 `PROGRESS.md`；本轮起点和本地分支差异见信息对齐台账第 5 节。
若实际分支/提交不一致，先查明是否在旧 master、新 worktree 或未同步副本中；
不要自动切换、reset 或把旧文档当成当前状态。确认 checkout 含最新文档提交后再继续。
同一工作区切换聊天不会自动删除文件，但新工作树、换机器或只读取已发布 tag 不保证拥有最新本地收尾。

本次对齐结束并进入正式规划时，同步更新本节入口，避免留下第二份过期状态快照。

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
- [MVP-2 规划前信息对齐](product/MVP_2_PREPLANNING_ALIGNMENT.md) — 已确认事实、待答问题与恢复依据；不是 Spec 或 Plan。
- `docs/architecture/FMEA_AGENT_V1_ARCHITECTURE.md` — V1 架构边界。
- `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md` — CSM 契约。
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` — SysML 快照契约。
- `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md` — SysML 映射矩阵。
- `docs/domain/FMEA_PROFILE_V1.md` — FMEA 语义配置。
- `docs/domain/FMEA_GLOSSARY.md` — 术语权威来源。
- `docs/evaluation/BENCHMARK_SPEC.md` — 长期基准模型。
- `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` — 治理规则。
- `docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md` — 语言与术语政策。
- `docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md` — 当前 MVP-2 草案；信息对齐与审查尚未完成，ACTIVE 不等于批准。

## REFERENCE

- `CLAUDE.md` — Claude Code 兼容指令；在正式简化工具加载行为之前，
  保持与 `AGENTS.md` 一致。
- `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md` — 长篇架构地基指南。
- `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md` — 长篇阶段与复用指南。
- `docs/research/DEPENDENCY_INVENTORY.md` — 依赖与复用清单。
- `docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md` — 供 MVP-2 规划使用的现有 Neo4j 故障知识基线。
- [FMEA 智能化参考项目](research/FMEA_INTELLIGENCE_REFERENCE_REVIEW_2026_09_05.md) — 2026-09-05 外部调研；仅供现有 Neo4j + SysML 数据后续讨论。
- `docs/research/OPENSYSML_SPIKE_REPORT.md` — MVP-1 OpenSysML 探索证据。
- `docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md` — OpenSysML 固定版本的复现证据。
- `docs/research/SYSML_SOURCE_CATALOG.md` — SysML 来源目录。
- `docs/adr/` — 已接受的架构决策记录。
- `docs/records/templates/` — 收尾、发布与会话交接模板。

## HISTORICAL

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
