# Coding Agent 会话模板

> 生命周期：SUPERSEDED，不再用于常规会话启动。
> 新的正式开发 Session 优先使用 `docs/README.md` 的最小读取集。
> 同一 Stage 因上下文过长需要交接时使用
> `docs/records/templates/SESSION_HANDOFF_TEMPLATE.md`。
> 具体 Prompt 是执行辅助材料，不是历史事实；
> 真实执行历史以 Git + `docs/records/` 为准。

## 中文文档生成约定

本模板的 SUPERSEDED 状态不变。若经当前任务选用其中的说明，生成的项目文档须以简体中文（zh-CN）为主体。
新会话仍按 `docs/README.md` 读取；同一 Stage 中断交接使用 `docs/records/templates/SESSION_HANDOFF_TEMPLATE.md`。
技术标识符、Status、Branch、HEAD、Commit、路径、命令和原始输出保持原形。
下方既有代码块作为原始模板样例保留，不因中文化改写；它不覆盖当前任务的范围或 Git 授权。

生成会话材料时，采用以下中文正文结构：

1. **仓库、分支与预期 HEAD**：填写实际仓库、Branch、预期 Commit，核对 Git 状态；发现不一致先报告差异。
2. **必读材料**：列出 Agent 指令、PROGRESS、文档导航、治理政策、当前 Spec、已有 Plan 与上一阶段记录。
3. **当前状态**：根据 PROGRESS 与 Git 填写 MVP / Stage 状态，不依赖记忆。
4. **本阶段目标**：只说明本会话授权完成的 Stage。
5. **范围内**：列明允许交付的内容。
6. **范围外**：列明禁止事项和不可提前实现的后续 MVP 内容。
7. **上一阶段约束**：保留已形成的约束、决策与已知限制。
8. **测试与实现顺序**：适用时先测试后实现；需要运行证据时，先探测再写预期。
9. **验证**：列明适用的测试、lint、类型检查、集成、基准与回归；证据分类保持 LOCAL / CI / EXTERNAL_REVIEW。
10. **文档要求**：以中文编写阶段记录、更新 PROGRESS 和受影响文档；计划与执行不一致时在 Record 中记录真实演化。
11. **提交与推送政策**：明确当前任务授权，commit message 保持原始英文；推送、合并和 tag 以当前授权及审核条件为准。
12. **最终报告**：以中文报告变更、原因、文件、测试、验证结果、基准影响、依赖变化、已知限制及下一步；未验证不得声称完成。

## 保留的原始模板样例

---

```text
# FMEA Agent Session — <Stage ID>: <Stage Name>

## 1. Repository / branch / expected HEAD

repository:
branch:
expected HEAD commit:

检查 git status / git branch --show-current / git log。
若与预期不一致，先停下来报告 discrepancy。

## 2. Required Reading

- AGENTS.md / CLAUDE.md
- PROGRESS.md
- docs/README.md
- docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md
- 当前 Spec：docs/specs/...
- 当前 Plan：docs/plans/...
- Previous Stage Record：docs/records/...

## 3. Current State

当前 MVP / Stage 状态（来自 PROGRESS.md，不凭记忆）。

## 4. Current Stage Goal

本 Session 只完成这一个 Stage。

## 5. In Scope

## 6. Out of Scope

（明确写出禁止做什么，包括禁止提前实现的未来 MVP 内容）

## 7. Previous Stage Constraints

上一个 Stage 形成的 binding 条件 / 决策 / 已知限制。

## 8. TDD / implementation order

先测试后实现的顺序；需要 runtime evidence 的地方先 probe 再写预期。

## 9. Verification

- uv run python scripts/verify.py（pytest + ruff + mypy）
- 相关 integration / benchmark / regression
- 验证分类：LOCAL / CI / EXTERNAL_REVIEW（当前无 CI）

## 10. Documentation requirements

- Stage Closeout Record（docs/records/...，用模板）
- PROGRESS.md 更新
- 受影响 architecture / research 文档更新
- 禁止改写历史（Plan 与执行不一致时在 Record 中记录演化）

## 11. Commit / push policy

- small meaningful commits，一个 Stage 不塞进一个巨型 commit
- commit message 表达 What + Why
- 完成后 push；不 merge master / 不打 tag（除非独立 review 已批准）

## 12. Final report format

What changed / Why / Files changed / Tests run / Verification results /
Benchmark impact / Dependencies added/changed / Known limitations /
Next recommended task

Never state "complete" if verification was not run.
```
