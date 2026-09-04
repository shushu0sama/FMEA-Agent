# MVP-1F — Benchmark & Release Closeout Record

Status: READY_FOR_REVIEW
Date: 2026-09-04

## 1. Objective

1F 是 validation + release readiness，不是 new feature stage：

```text
B0 project-owned exact benchmark
B1 官方外部 SysML 模型 benchmark
Benchmark Report + Release Gate 全项验证
MVP-1 Release Record + 文档治理（Part A）
```

## 2. Scope

In Scope:

- B0：复用 `typed_inside_probe.sysml`（满足 Benchmark Spec 的 minimal
  fixture 要求），人工撰写 gold expected data
- B1：官方 SysML-v2-Release `Parts Example-2.sysml`（固定 commit +
  SHA256 + EPL-2.0），显式 root=vehicle
- Benchmark Report（`docs/evaluation/MVP_1_BENCHMARK_REPORT.md`）
- Release Gate 全项验证
- 文档治理基线（见 §4 与独立 commit）
- MVP-1 Release Record

Out of Scope:

- 新 feature / 新 Mapping 语义
- 修改 gold expected 迎合 bug
- merge master / tag / MVP-2

## 3. Git

Branch: `feature/mvp1-real-system-facts`

Start Commit: `30aee28`（1E closeout fix，1F 基线）

Implementation Commit(s):

- `389f216` docs: establish development records and session governance
  （Part A 治理）
- `4f73d22` test/docs: complete MVP-1F benchmark and release candidate
  （Part B：benchmark + release records）
- `5da0f11` docs: add per-item release gate evidence to MVP-1F record
  （review evidence amendment）

Final Commit: `5da0f11`（Review Baseline；其后的 docs-only consistency
amendments 以 git log 为准，最终发布锚点为 Release Review 通过后的
merge commit 或 release tag）

## 4. Delivered

- `tests/test_mvp1_benchmark.py` — 11 benchmark tests（B0 ×4 + B1 ×7）
- `tests/fixtures/sysml/models/parts_example_2_official.sysml` —
  官方模型字节级副本（SHA256 测试固化）
- `docs/evaluation/MVP_1_BENCHMARK_REPORT.md`
- `docs/records/MVP_1/MVP_1_RELEASE.md`
- 治理：`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`、
  `docs/records/`（MVP-0/1A–1F Stage Records + templates）、
  `docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md`、
  PROGRESS.md 精简、CLAUDE.md / AGENTS.md 治理章节、
  `MVP_1_CLAUDE_CODE_SESSIONS.md` 标记 historical
- README.md 更新（MVP-1 release candidate 状态）
- `docs/research/SYSML_SOURCE_CATALOG.md` + fixtures README 溯源记录

## 5. Key Decisions

- **B0 复用而非新建**：`typed_inside_probe.sysml` 已满足 Benchmark Spec
  的 minimal-fixture 要求（System/Component/Function/parent/allocation/
  notices 全覆盖），不为文件名好看重复创建 fixture。
- **B1 root policy**：官方模型含 3 个 top-level PartUsage；不依赖 auto
  first root；显式选择 `vehicle`，root source id 从真实 Snapshot 获取；
  auto-root 失败并列出候选的行为由测试固化。
- **B1 functions = []**：模型无符合 MVP-1 Mapping Contract 的 Function；
  Function Precision/Recall 记为 N/A，不为 benchmark 丰富度添加 Function。
- **Benchmark gold 为 human-authored**：基于 runtime probe 观察事实
  （OpenSysML 0.4.0 + sysml-grpc v0.4.3）人工撰写；不调用 Mapper 生成
  expected。
- **F1 hash 处理**：benchmark 不断言 `model_hash` 值（load-context
  fingerprint）；B1 用 SHA256 固化外部文件字节不变性。

## 6. Evidence

- Benchmark 报告：`docs/evaluation/MVP_1_BENCHMARK_REPORT.md`
- Benchmark 测试：`tests/test_mvp1_benchmark.py`
- runtime probe（1F 观察）：Parts Example-2 与 typed_inside_probe 的
  Snapshot facts（本 Session 实测，结果记录于 Benchmark Report 与测试
  gold 注释）
- 契约/回归：1C/1D/1E tests（不变，作为回归基线）

## 7. Verification

```text
uv lock --check                 PASS（LOCAL）
uv sync --frozen                PASS（LOCAL）
pytest 223 passed               PASS（LOCAL，Windows；212 基线 + 11 benchmark）
ruff check .                    PASS（LOCAL）
mypy src（strict）              PASS（LOCAL）
MVP-0 demo run                  PASS（risk=NOT_EVALUATED，optimization=SKIPPED）
B0 exact mapping                PASS（4 tests）
B1 external model               PASS（7 tests）
real SysML E2E（typed_inside）  PASS（test_canonical_repository.py，suite 内）
sysml-grpc orphan check         PASS（0 进程）
git diff --check                PASS
```

CI：GitHub Actions NOT CONFIGURED。全部为 LOCAL evidence。

## 8. Release Gate

Gate 语义拆为两层：Implementation / Verification Gate 由实现方在本阶段
完成并逐项验证；Independent Release Review 是尚未完成的独立审核，
不因实现验证通过而自动满足。

### 8.1 Implementation / Verification Gate（LOCAL evidence，PASS 16/16）

```text
[x] MVP-0 regression PASS            — demo run + 历史 tests 全通过
[x] B0 exact mapping PASS            — tests/test_mvp1_benchmark.py（4 tests）
[x] OpenSysML contract tests PASS    — test_open_sysml_file_adapter.py 等（suite 内）
[x] >=1 official external SysML PASS — B1 Parts Example-2（7 tests）
[x] source trace PASS                — source_element_id 与 gold 精确一致（B0/B1）
[x] Canonical invariants PASS        — domain validator + mapping regression tests
[x] real SysML → workflow E2E PASS   — test_canonical_repository.py（suite 内）
[x] pytest PASS                      — 223 passed（LOCAL，Windows）
[x] ruff PASS                        — check .（LOCAL）
[x] mypy strict PASS                 — src 24 files（LOCAL）
[x] no orphan sysml-grpc regression  — 0 进程（LOCAL 实测）
[x] no OpenSysML type leakage        — 1B AST 级 import 测试固化（suite 内）
[x] no hard-coded local paths        — 生产代码无 D:\ 路径；本地工作区仅
                                       存在于历史研究记录（reference only）
[x] no KG/RAG/MCP/real LLM leakage   — 本阶段零生产代码改动（仅 tests/docs）
[x] documentation governance complete — Part A commit 389f216
[x] MVP-1 Stage Records complete     — docs/records/（MVP_0 + 1A–1F + Release）
```

### 8.2 Independent Release Review（未完成）

```text
[ ] EXTERNAL_REVIEW — 独立 reviewer（人 / 独立 Agent）审查：

    docs/records/MVP_1/MVP_1_RELEASE.md
    docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md
    docs/evaluation/MVP_1_BENCHMARK_REPORT.md
```

通过后：merge master / release tag 作为真正不可变的发布锚点；
未通过：CHANGES_REQUIRED，回到实现方修改。

## 9. Problems Found During Development

- README.md 漂移（发现并修复）：README 仍称 "MVP-1 尚未开始"，与
  Git/tests 实际状态（1A–1E 完成）矛盾 —— 按 Implementation Truth 原则
  记录 discrepancy 并在 1F release documentation 中更新 README。
- 无 production bug 暴露；无 benchmark RED。

## 10. Known Limitations

见 Benchmark Report §Known Limitations：

- 单文件子集（C1）；F1 hash 语义；`component_type=None`；
  B1 Function metrics N/A。

## 11. Deferred

- B2 Vehicle Example（定义/用法区分、更大模型）—— 延后。
- GitHub Actions 最小 CI —— 建议在 Independent Release Review 中评估
  （本任务不擅自新增 CI）。

## 12. Files / Contracts Affected

```text
tests/test_mvp1_benchmark.py（新增）
tests/fixtures/sysml/models/parts_example_2_official.sysml（新增）
tests/fixtures/sysml/README.md
docs/evaluation/MVP_1_BENCHMARK_REPORT.md（新增）
docs/research/SYSML_SOURCE_CATALOG.md
docs/records/**（新增）
docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md（新增）
docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md（新增）
docs/prompts/MVP_1_CLAUDE_CODE_SESSIONS.md（historical 标记）
PROGRESS.md（精简重写）
CLAUDE.md / AGENTS.md（治理章节）
README.md
```

## 13. Final Assessment

READY_FOR_REVIEW（最终 Acceptance 由独立 release review 决定）

## 14. Next Stage

Independent Release Review（MVP-1）。
进入条件：本 Record + MVP-1 Release Record + Benchmark Report 就绪；
review 通过后才允许 merge master / tag / 规划 MVP-2。
