# Claude Code Session Template

> 新的正式开发 Session 的 Prompt 以本模板生成。
> 具体 Prompt 是 execution aid，不是历史事实；
> 真实执行历史以 Git + `docs/records/` 为准。

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

- CLAUDE.md / AGENTS.md
- PROGRESS.md
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
