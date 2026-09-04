# MVP-1 Claude Code 分 Session 提示词

> **Historical Planning Artifact**（2026-09-04 标记）
>
> 这是 MVP-1 开始前的 Session 规划。
> 真实执行历史以 Git + `docs/records/MVP_1/` 为准。
> 后续 Session 使用 `docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md`。
> 本文件保留原规划内容，不用于判断项目当前状态。


## Session 0 — Read-only planning

```text
这是新的 FMEA Agent MVP-1 Session。

读取：
CLAUDE.md
PROGRESS.md
MVP-1 Spec
MVP-1 Plan
OpenSysML Spike
SysML Mapping Matrix
MVP-1 Benchmark
Language Policy
ADR-008

检查 git status / git log。

本地：
Windows 11 + VS Code + PowerShell
SysML Workspace:
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace
OpenSysML:
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML

路径只用于本地研究，不得硬编码。

只确认 scope、baseline、Spike steps。
不要安装依赖，不要编码。
```

## Session 1 — Feasibility Spike

```text
开始 MVP-1A OpenSysML Feasibility Spike。

禁止修改 FMEA Agent production code。
禁止修改第三方 OpenSysML repo。

所有 API 结论必须来自当前 checkout、当前文档、当前测试和真实运行。

验证：
commit/release
Python client install
sysml-grpc
Windows
load/parse
diagnostics
query/traversal
IDs
ownership
PartDefinition / PartUsage
ActionDefinition / ActionUsage

实验写入 99_experiments。

最终只生成：
docs/research/OPENSYSML_SPIKE_REPORT.md

输出 GO / CONDITIONAL_GO / NO_GO。

不要开始 production Adapter。
```

## Session 2 — Snapshot Contracts

```text
新的 MVP-1B Session。

读取 Spike Report 和当前 Spec/Plan。
运行 baseline tests。

只实现 SysMLFactSnapshot contracts。
不得依赖 opensysml/grpc/internal AST。

测试优先。
完成后 pytest / ruff / mypy / diff-check。
不要开始 Adapter。
```

## Session 3 — OpenSysML Adapter

```text
新的 MVP-1C Session。

只实现 OpenSysML File Adapter。
必须严格使用 Spike 验证过的 public API。

职责：
.sysml → OpenSysML → SysMLFactSnapshot

必须：
dependency pin
exception translation
diagnostics
contract tests

禁止 Canonical mapping / workflow rewrite / KG/RAG/MCP。
```

## Session 4 — Canonical Mapping

```text
新的 MVP-1D Session。

只实现最小 Mapping：

selected root PartUsage → System
named nested PartUsage → Component
selected ActionUsage/performed behavior → Function candidate

禁止：
PartDefinition == Component
all ActionDefinition == Function

必须有 root-selection policy。
使用 project-owned minimal fixture 做 exact expected tests。
更新 Mapping Matrix。
```

## Session 5 — E2E Integration

```text
新的 MVP-1E Session。

目标：
real .sysml
→ OpenSysML
→ Snapshot
→ Canonical
→ existing workflow
→ FMEA Candidate

Failure Knowledge / Risk / Optimization 保持原状。
禁止 KG/RAG/MCP/real LLM。

完成后跑全量回归。
```

## Session 6 — Release Review

```text
不要新增功能。

执行：
B0 exact mapping
>=1 official external model test
MVP-0 regression
dependency inventory review
mapping matrix review
README / PROGRESS review
git diff / diff-check

检查：
no hard-coded D:\ path
no OpenSysML type leakage
no KG/RAG/MCP
MVP-0 demo still runs
diagnostics retained
source refs traceable

输出：
MVP1_RELEASE_READY
或 CHANGES_REQUIRED
```
