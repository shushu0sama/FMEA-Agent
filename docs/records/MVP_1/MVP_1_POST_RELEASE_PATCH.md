# MVP-1 — Post-Release Documentation Patch Record

Status: PATCH_READY_FOR_REVIEW（v0.1.1 candidate；tag 未创建）
Date: 2026-09-04

## Context

MVP-1 = RELEASED（annotated tag v0.1.0 → release-closeout commit
`9c59b4b6ddb0ee78de211eb86aa635297342880f`）。v0.1.0 是不可变发布锚点，
本 patch 不修改、不移动、不覆盖该 tag。

本 patch 是 Post-Release Audit 的唯一 blocker（current-state
documentation drift）的修正，属于治理 §13 定义的：

```text
patch（y）: release/baseline correction without major capability expansion
```

不引入任何新 MVP capability。

## Post-Release Audit 结果

```text
Git identity:       PASS
Git history:        PASS
Verification:       PASS
Benchmark:          PASS
Provenance:         PASS
Scope boundary:     PASS
Current-state docs: FAIL — docs/evaluation/MVP_1_BENCHMARK_REPORT.md 两处
                    stale current-state text
```

## 修正内容（docs-only）

1. **Review Baseline anchor**（Benchmark Report 顶部 commit 表）：
   原标注 `Review Baseline: 5da0f11` 是 stale value。
   真实 Independent Release Review baseline = `369f09d`。
   修正后：`5da0f11` 保留为历史 Review Evidence amendment，
   `369f09d` 为最终 Review Baseline（与 Release Gate 一致）。
   历史不被删除，仅重新标注角色。
2. **Release execution state**（Benchmark Report Release Gate 段）：
   原文"merge master / release tag（不可变发布锚点）尚未执行"与实际
   Git 状态矛盾。更新为已执行事实：
   master merge `2871b23c`（--no-ff）/ release closeout `9c59b4b` /
   annotated tag `v0.1.0`。

Benchmark 历史结果（B0/B1 gold、metrics、11 benchmark tests）未重写。

## 版本状态

```text
v0.1.0 = original MVP-1 release（不可变）
v0.1.1 = documentation / current-state consistency correction
         （PATCH_READY_FOR_REVIEW；tag 待独立 Post-Release Patch
         Review 通过后另行创建）
```

保持不变：

```text
MVP-1  = RELEASED
MVP-1F = ACCEPTED
MVP-2  = NOT_STARTED
```

## Known Follow-up / Observation（不阻塞本 patch）

- `pyproject.toml` 仍为 `version = "0.0.1"`（Post-Release Audit
  observation）。当前治理只定义 Git release tag version policy
  （§13），Python package metadata version 与 Git tag 的同步策略尚未
  定义。本 patch 不改 `pyproject.toml` / `uv.lock`；该同步策略需在
  任何 package publication 之前另行决策。

## 修改文件

```text
docs/evaluation/MVP_1_BENCHMARK_REPORT.md（两处 current-state 修正）
docs/records/MVP_1/MVP_1_RELEASE.md（版本历史 + follow-up 记录）
docs/records/MVP_1/MVP_1_POST_RELEASE_PATCH.md（本 Record）
PROGRESS.md（current state 同步）
README.md（current state 同步）
```

Production code / tests / benchmark gold / pyproject.toml / uv.lock：
零修改。

## Verification — LOCAL

```text
uv lock --check:   PASS
uv sync --frozen:  PASS
pytest:            223 passed（212 基线 + 11 benchmark；无数量变化）
ruff check .:      PASS
mypy src strict:   PASS
MVP-0 demo:        PASS（Risk=NOT_EVALUATED，Optimization=SKIPPED）
git diff --check:  PASS
```

CI：GitHub Actions NOT CONFIGURED（全部 LOCAL evidence）。

## Release Gate — Patch

```text
Independent Post-Release Patch Review  — NOT_YET_EXECUTED
```

本 Session 不创建 tag v0.1.1；待 patch review 通过后另开 Session 创建。

## Next Stage

```text
1. 独立 Post-Release Patch Review（本 patch candidate）
2. review 通过后：annotated tag v0.1.1（另开 Session）
3. MVP-2 Read-only Planning（另开 Session；MVP-2 = NOT_STARTED）
```
