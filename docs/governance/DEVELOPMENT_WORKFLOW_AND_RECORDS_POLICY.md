# Development Workflow & Records Policy

> 长期工程治理规范。CLAUDE.md / AGENTS.md 引用本文件；细节以此为准。
> 建立于 2026-09-04（MVP-1F 治理升级）。

## 1. 文档职责模型

同一事实只应有一个详细来源；其他文档使用链接。

```text
Spec        = WHAT（目标、范围、Acceptance Criteria）
Plan        = HOW（阶段顺序、Gate）
Architecture= LONG-LIVED CONTRACT（模型契约、映射规则、identity/provenance 语义）
ADR         = WHY（长期决策；普通 bugfix 不创建 ADR）
Research    = RESEARCH / SPIKE / EXTERNAL EVIDENCE（一次性实证证据）
Record      = WHAT HAPPENED（真实执行历史；docs/records/）
PROGRESS    = WHERE WE ARE NOW（当前状态快照，不是完整历史）
Prompt      = HOW TO START A SESSION（execution aid，不是历史事实）
Git         = 实际实现历史（最底层事实）
CLAUDE/AGENTS= 开发时必须遵守的规则
```

文档 lifecycle 状态：

```text
ACTIVE      当前 operational source of truth
REFERENCE   长期背景 / evidence，按需读取
HISTORICAL  历史计划或执行记录，不代表当前状态
SUPERSEDED  保留追溯，但已被新文档取代
```

`docs/README.md` 是文档 lifecycle 与最小读取集的导航入口。

原则：

```text
Plan ≠ Execution Record
Prompt ≠ Source of Truth
PROGRESS ≠ Full History
```

- Plan 是计划。真实执行与 Plan 不一致时，不重写 Plan 假装计划从未变化，
  由 Stage Record 记录真实演化。
- 旧 Prompt 保留原样，但必须标明 historical planning artifact。
- 一次性实验结论不进入 architecture。

## 2. Dual Source-of-Truth Policy

### 2.1 Implementation Truth（现在实际上实现了什么）

优先级：

```text
1. current Git code + tests
2. reproducible runtime / benchmark evidence
3. Git commit history
4. Stage Closeout Records
5. PROGRESS.md
6. old plans / prompts / chat reports
```

代码存在并不自动意味着代码正确。若 code 与 architecture/spec 冲突，
必须报告 discrepancy；不能说“代码优先所以规范作废”。

若 Git、tests、文档三者矛盾：不要猜、不要静默修正文档来迎合实现、
必须明确记录 discrepancy。

### 2.2 Normative Project Truth（项目应该遵守什么）

主要来源：

```text
CLAUDE.md / AGENTS.md
Accepted ADRs
当前 approved Spec
Architecture contracts
当前 Plan
Governance policies
```

发生冲突时：不得自行挑选最方便实现的版本；必须明确报告并解决冲突。

## 3. Stage 生命周期

### 3.1 状态词汇

```text
NOT_STARTED
IN_PROGRESS
IMPLEMENTED        ← 实现 Agent 完成实现 + 验证后可声明
READY_FOR_REVIEW   ← 实现 Agent 完成 Stage Record / Release Record，
                     正式进入独立 review 队列
CHANGES_REQUIRED   ← reviewer 提出修改要求，回到实现方
BLOCKED
ACCEPTED           ← 由独立 review 决定，不由实现 Agent 自封
COMPLETE           ← 已满足 release/acceptance gate 的阶段（历史用法保留）
```

推荐流程：

```text
Claude / Codex implementation finished
        ↓
IMPLEMENTED → READY_FOR_REVIEW
        ↓
independent reviewer（人 / 独立 Agent）
        ↓
ACCEPTED 或 CHANGES_REQUIRED
```

实现 Agent 可声明 `IMPLEMENTED` / `READY_FOR_REVIEW`；
最终 Acceptance 由独立 review 决定。
`READY_FOR_REVIEW` 只说明实现验证完成、等待审核，不隐含 Acceptance。

### 3.2 Stage Definition of Done

正式 Stage 不得声明 COMPLETE / IMPLEMENTED，除非：

```text
[ ] Scope clear
[ ] Tests added/updated
[ ] Tests pass
[ ] Ruff pass
[ ] Mypy pass
[ ] Relevant integration pass
[ ] Relevant regression pass
[ ] Relevant benchmark pass or N/A explained
[ ] No unrelated changes
[ ] Architecture boundaries preserved
[ ] Evidence/provenance preserved
[ ] Known limitations recorded
[ ] Stage Record complete
[ ] PROGRESS updated
[ ] Git commit complete
[ ] Push complete
```

没有运行验证时，禁止使用 `COMPLETE` / `ACCEPTED` / `PASS`。

## 4. Anti-Drift Gate

### 4.1 每个正式 Stage 开始前

```text
[ ] 当前 branch 正确
[ ] HEAD 与预期一致
[ ] working tree 状态已知
[ ] Current Spec 已读
[ ] Current Plan 已读
[ ] Previous Stage Record 已读
[ ] 本 Stage In Scope 明确
[ ] Out of Scope 明确
[ ] 未偷偷进入未来 MVP
```

### 4.2 完成 Stage 前

```text
[ ] 实际 diff 与目标一致
[ ] 无 unrelated changes
[ ] tests pass
[ ] lint/type pass
[ ] benchmark/regression pass
[ ] provenance preserved
[ ] known limitations documented
[ ] Stage Record updated
[ ] PROGRESS updated
[ ] next stage explicitly stated
```

## 5. Scope Drift Detection

每次 Stage closeout 必须回答：

```text
Did scope change?

NO
YES — justified by evidence
YES — architectural change requiring ADR/spec update
```

允许增加 Gate（例：1E-0 Integration Gate），但必须记录：

```text
为什么原计划不足
什么 evidence 触发新 Gate
是否改变原 architecture
```

不要偷偷扩大 Scope。

## 6. Session 切换制度

原则：

```text
一个正式开发 Stage ≈ 一个主 Claude Code / Codex Session
```

推荐流程：

```text
开始 Stage
→ 恢复 Git + Docs 状态
→ 开发
→ verify
→ commit
→ Stage Record
→ push
→ independent review
→ 关闭 Session
→ 新 Stage 开新 Session
```

以下情况建议提前换 Session：

```text
上下文明显过长
模型开始重复已解决问题
忘记阶段边界
出现与 repo 不一致的描述
连续发生无关修改
Stage 内出现新的独立 Gate
```

换 Session 时不依赖聊天记忆。必须依赖：

```text
Git
PROGRESS
Spec
Plan
Previous Stage Record
```

## 7. Stage Record 粒度

以下需要 Stage Record（一个正式 Stage 一个）：

```text
MVP-1A / 1B / 1C / 1D / 1E / 1F ...（每个正式 Stage）
```

以下不单独建立 Record，写入所属 Stage Record 的 Closeout Fixes：

```text
单个 regression fix
小测试补充
普通重构
顺序修正 / orphan 检查修正等
```

## 8. Records 卫生规则

Stage Record 不应大量记录：

```text
临时 absolute path
个人用户名
缓存目录
无关 terminal noise
完整聊天内容
```

影响可复现性的环境信息可以写（Windows 11、Python version、
OpenSysML version、sysml-grpc version、dependency SHA）。
本地路径只有作为历史研究证据必要时才保留，并明确：

```text
reference environment only
must not be hard-coded
```

复制进仓库的第三方 source/test fixtures 必须保留精确 provenance：

```text
upstream repository + exact commit
license identity
license 文本副本（third_party/licenses/，verbatim，不修改）
THIRD_PARTY_NOTICES.md 登记（fixture 路径 + license text path）
```

## 9. CI Evidence 分类

当前仓库没有独立 CI status。所有验证记录区分：

```text
LOCAL             ← 本机执行（如 pytest 212 passed — LOCAL Windows）
CI                ← 独立 CI 执行（当前：GitHub Actions NOT CONFIGURED）
EXTERNAL_REVIEW   ← 独立人工/Agent review
```

不要把本地测试写成 GitHub CI PASS。

## 10. Git 是永久记录的一部分

- Markdown Record 不是 Git 的替代品。
- 真实历史基础是 small meaningful commits。
- Commit message 表达 What + Why。
- Stage Record 引用 commit。
- 禁止一个巨大 commit 横跨多个 Stage。
- 禁止修改第三方 Git 历史。

## 11. 回填历史记录规则

从 Git history / tests / existing docs 回填 Record 时：

```text
禁止凭记忆编造历史
禁止根据当前代码反推不存在的历史过程
每个 Commit 必须从 git log 真实确认
```

若某个历史 RED test 没有 commit 保存，如实记录：

```text
reported local RED→GREEN evidence
not independently preserved as Git commit
```

不要伪称 Git 可验证。

## 12. 记录状态与更新义务

- 每个正式 Stage 完成：更新 Stage Closeout Record + PROGRESS。
- 每个完整 MVP 完成：MVP Release Record（汇总 + 链接，不复制 Stage Record）。
- 详细证据只在一处（Single Source of Detailed Evidence）：
  Stage Record 引用 research/architecture 文档，不复制内容。

## 13. Pre-1.0 Release Version Policy

版本形态：`v0.x.y`

```text
minor（x）:  new accepted MVP capability
patch（y）:  release/baseline correction without major capability
             expansion
```

历史：

```text
v0.0.1 = MVP-0 Runnable Skeleton
v0.1.0 = MVP-1 Real System Facts
```

规则：

- Release tag 必须 annotated；禁止 lightweight tag。
- 禁止覆盖或移动任何已有 tag（禁止 `git tag -f`）。
- Tag 只指向已通过 Independent Release Review、完成 merge 与 master
  verification 的 commit（release-closeout commit）。
- MVP Release Record 记录 tag 名与 merge commit 锚点。
