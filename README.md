# FMEA Agent

当前仓库已整理为 **FMEA Agent Bootstrap v0.1 / Architecture Baseline v0.1**，可直接作为 Claude Code 的项目根目录使用。

## 当前开发目标

当前只开发：

> **MVP-0 — Runnable Vertical Slice**

目标是先用 JSON fixture、InMemory Repository、可替换 Port 和 LangGraph 骨架跑通一个可执行的 AIAG-VDA 形态 FMEA 流程，再逐步替换为真实 SysML、故障知识、LLM、验证、MCP 与动态 FMEA 能力。

## Claude Code 每次新 Session 首先读取

1. `CLAUDE.md`
2. `PROGRESS.md`
3. 当前 Spec / Plan

MVP-0 当前文件：

- `docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md`
- `docs/plans/MVP_0_IMPLEMENTATION_PLAN.md`

## 第一次启动建议

先进行只读体检，不要立即编码：

```text
Read CLAUDE.md and PROGRESS.md.
Then read:
- docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md
- docs/plans/MVP_0_IMPLEMENTATION_PLAN.md

Do not modify files yet.
Inspect repository structure, git status, current Python/project state,
and confirm whether the repository is ready for MVP-0 Tasks 0-2.
Do not add OpenSysML, Neo4j, Qdrant, Docling or MCP.
```

## 本地 Claude Code 配置

`.claude/settings.local.json` 属于本机私有配置，不应提交到 Git，也不随本项目包分发。请使用你的 Claude Code 全局配置或在本地重新创建该文件。

## 重要入口

- 长期架构原则：`docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md`
- 分阶段开发与复用：`docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md`
- FMEA 方法：`docs/domain/FMEA_PROFILE_V1.md`
- Canonical Model：`docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`
- Benchmark：`docs/evaluation/BENCHMARK_SPEC.md`
- 依赖清单：`docs/research/DEPENDENCY_INVENTORY.md`
- ADR：`docs/adr/`
