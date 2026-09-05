# MVP-1E — 工作流集成收尾记录

状态： ACCEPTED
日期： 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. 目标

实现 OpenSysML/canonical-backed `SystemModelRepository`，接入现有
LangGraph workflow：

```text
真实 .sysml → OpenSysML → Snapshot → Canonical → Repository → Workflow
```

不改变 Failure Knowledge / Risk / Optimization。

## 2. 范围

范围内：

- `CanonicalSystemModelRepository`（实现 `SystemModelRepository`
  Protocol 四方法，不重新解析 SysML）
- Function scope & allocation policy v1.1（1E-0 Gate 触发）
- 真实 `.sysml` → workflow E2E

范围外：

- Failure Knowledge / Risk / Optimization 改动
- workflow 结构修改
- KG / RAG / MCP / real LLM

## 3. Git

Branch: `feature/mvp1-real-system-facts`

起始 Commit： `ce37780`（1D）

实现 Commit： `657a892` feat: add MVP-1E workflow integration via canonical-backed repository

收尾 Commit： `30aee28` fix: prevent dangling function allocation and component parent ids

最终 Commit： `30aee28`

## 4. 交付内容

- `src/fmea_agent/adapters/inmemory/system_model.py` —
  `CanonicalSystemModelRepository`
- Function scope & allocation policy v1.1（`canonical_mapping.py`）：
  typed named ActionUsage 的最近 partUsage 祖先在 selected root 子树内 →
  `Function.allocated_to = [该祖先 canonical id]`；package-level →
  NEEDS_RESEARCH notice；其他 part 子树 → DEFERRED notice；
  unnamed 祖先 → NEEDS_RESEARCH notice。禁止 name/FQN 匹配（C4）。
- 新 fixture `typed_inside_probe.sysml`（runtime probe 证据）
- 真实 E2E：`tests/test_canonical_repository.py`（8 tests）
- mapping matrix Function policy v1.1 + 证据行
- **Closeout fix（30aee28）**：dangling allocation —— 预生成
  `component-N` id 曾作为分配证据；改为 `mapped_component_ids`
  （Component 实际创建后登记）作为唯一证据；域层 invariant：
  `Function.allocated_to` target 必须解析到 `System.id` 或已存在的
  `Component.id`。3 个 regression tests。

## 5. 关键决策

- **1E-0 Integration Gate（新增 Gate，记录演化）**：原计划未含此 Gate。
  证据触发：1D 的 `allocated_to=[]` 无法满足
  `list_functions(element_id)` 契约（9 个 RED 测试先行固化接口缺口，
  runtime probe 证实 typing + owner traversal evidence 存在后实现）。
  不改变原 architecture 边界；修正 Function 映射政策（v1.0 → v1.1）。
- perform_probe 的 package-level `spin` 按 v1.1 不再映射为 Function
  （归属无法确认，notice 记录）。
- system-level Function（`allocated_to=[System.id]`）现 workflow 只按
  component 查函数，系统级函数暂不被任何分析目标使用（未改 workflow）。

## 6. 证据

- 映射契约：`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`
  （Function Scope & Allocation Policy v1.1）
- runtime probe：`tests/fixtures/sysml/models/typed_inside_probe.sysml`
  （ok=True，真实 type_facts + owner traversal）
- 测试：`tests/test_canonical_repository.py`、
  `tests/test_canonical_mapping.py`（1E 增补）

## 7. 验证

```text
1E-0 Gate（allocated_to 缺口 RED 固化）      PASS
runtime probe（typing + owner traversal）    PASS（ok=True）
Function scope（package-level / 其他子树）   PASS（notice，不静默加入）
Function.allocated_to（System / Component）  PASS（真实 + synthetic）
canonical-backed repository 契约             PASS（Protocol 四方法）
真实 .sysml → workflow E2E                  PASS（motor/spin 候选输出）
Failure Knowledge fixture（name-keyed）      PASS（未改机制）
Risk = NOT_EVALUATED / Optimization = SKIPPED PASS
MVP-0 demo regression                       PASS
pytest 209 passed（196 基线 + 13 新增）      PASS（LOCAL，closeout 657a892）
pytest 212 passed（closeout fix 30aee28 后）  PASS（LOCAL）
ruff / mypy（strict）                       PASS（LOCAL）
无 workflow 结构修改（零 diff）              PASS
```

注：212 为 closeout fix 后的最终基线（当前 verify.py 输出 212 passed）。

## 8. 开发中发现的问题

- 1E-0 Gate：`allocated_to=[]` 契约缺口（§5）。
- Closeout fix：dangling allocation / dangling parent —— unnamed 祖先
  导致 named PartUsage 无法映射时，其下 typed ActionUsage 仍被分配
  悬空 `component-N` id；深层链条使 Component.parent_id 悬空并触发
  validator 崩溃。3 个 regression tests 固化。

## 9. 已知限制

- `Component.component_type` 保持 `None`（无证据规则）。
- system-level Function 暂不被 workflow 分析目标使用。
- partial Snapshot 的 workflow 接入行为未单独覆盖。

## 10. 延后事项

- Requirement / Port / Interface / Connection / Flow / State / Allocation。
- 多系统模型 workflow 接入。

## 11. 涉及文件 / 契约

```text
src/fmea_agent/adapters/inmemory/system_model.py
src/fmea_agent/adapters/inmemory/__init__.py
src/fmea_agent/adapters/sysml/canonical_mapping.py
src/fmea_agent/domain/system_model.py（invariant）
tests/test_canonical_repository.py
tests/test_canonical_mapping.py
tests/fixtures/sysml/models/typed_inside_probe.sysml
docs/architecture/SYSML_TO_CANONICAL_MAPPING.md
```

## 12. 最终评估

ACCEPTED（含 closeout fix `30aee28`）

## 13. 下一阶段

MVP-1F Benchmark & Release。
进入条件：1E 基线稳定（212 passed）；B0/B1 benchmark 与 Release Gate
按 `docs/evaluation/MVP_1_BENCHMARK_SPEC.md` 执行。
