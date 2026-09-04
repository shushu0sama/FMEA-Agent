# MVP-1D — Canonical Mapping Closeout Record

Status: COMPLETE
Date: 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. Objective

实现 `CanonicalSystemMapper`：

```text
SysMLFactSnapshot → Canonical System Model
```

第一版只处理 selected root PartUsage → System、named nested PartUsage →
Component、typed ActionUsage → Function；必须有显式 root-selection policy。

## 2. Scope

In Scope:

- root-selection policy v1（显式 `root_source_id` 或唯一候选；0/多候选 → error）
- Canonical Identity policy v1（`system-1`/`component-N`/`function-N`，
  source identity 保留于 SourceReference）
- MappingNotice（CONFIRMED/TENTATIVE/NEEDS_RESEARCH/REJECTED/DEFERRED）
- `CanonicalSystemModel` aggregate（id 唯一、parent 可解析校验）
- `CanonicalMappingError`
- mapping matrix 更新（TENTATIVE → CONFIRMED 证据）

Out of Scope:

- SystemModelRepository / workflow 接入（1E）
- Requirement / Port / Interface / Connection / Flow / State / Allocation

## 3. Git

Branch: `feature/mvp1-real-system-facts`

Start Commit: `4f141dd`（1C closeout fix）

Implementation Commit(s): `ce37780` feat: add MVP-1D SysML-to-Canonical mapping with explicit root policy

Closeout Commit(s): `ce37780`（同 commit，closeout 记录写入 PROGRESS）

Final Commit: `ce37780`

## 4. Delivered

- `src/fmea_agent/adapters/sysml/canonical_mapping.py` —
  `CanonicalSystemMapper.map_snapshot(snapshot, *, root_source_id=None)`
- `src/fmea_agent/domain/system_model.py` — `CanonicalSystemModel`
  aggregate + `MappingNotice`
- `src/fmea_agent/adapters/sysml/exceptions.py` — `CanonicalMappingError`
- `tests/test_canonical_mapping.py` — 32 tests（unit 用 parser-neutral
  synthetic snapshots；integration 经真实 sysml-grpc v0.4.3）
- 新 fixtures：`sibling_roots_probe.sysml` / `no_usage_probe.sysml`
- 文档：`SYSML_TO_CANONICAL_MAPPING.md`（root-selection / canonical
  identity / notice 语义）、`CANONICAL_SYSTEM_MODEL_SPEC.md` §15

## 5. Key Decisions

- **Root Selection Policy v1**：显式 `root_source_id` 或唯一 named
  top-level partUsage 候选；0/多候选 → `CanonicalMappingError` 列出候选。
  禁止 `first_part_usage` / 依赖 Snapshot 偶然顺序。
- **Canonical Identity Policy v1**：Canonical ID 由 Mapping 层生成，
  禁止把 `Symbol.id` 当 Canonical ID；v1 不承诺跨版本稳定；
  source identity 保留于 `SourceReference.source_element_id`。
- **Notice 语义**：每个 Snapshot 元素要么映射，要么产出 notice，
  不静默丢弃；partial Snapshot 仍映射已观察事实 + model-level notice。
- performed/untyped ActionUsage 不映射（C4，NEEDS_RESEARCH notice）。
- partDef/actionDef/package/其他 metatype 一律 notice。

## 6. Evidence

- 映射契约：`docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`
  （Implementation Record：TENTATIVE → CONFIRMED 证据表）
- 测试：`tests/test_canonical_mapping.py`

## 7. Verification

```text
真实 .sysml → Snapshot → Canonical E2E         PASS（perform_probe 实测输出）
System / Component / Function 提取              PASS
SourceReference 可追溯                          PASS（source_element_id + 绝对路径）
Canonical ID ≠ source identity                 PASS（测试固化）
performed ActionUsage 不伪造 typing            PASS（C4）
unsupported concept 有 notice                   PASS（package/defs/attribute）
0 / 多候选 root → CanonicalMappingError        PASS
partial Snapshot → 已观察事实 + notice         PASS
Snapshot 遍历顺序 = 源文件顺序                 PASS（1C 修正 + regression）
orphan 检查 = PID 集合比对                     PASS
MVP-0 demo regression                          PASS
pytest 196 passed（164 基线 + 32 新增）        PASS（LOCAL，Windows）
ruff / mypy（strict）                          PASS（LOCAL）
无 SystemModelRepository / workflow 修改       PASS
无 Neo4j/Qdrant/MCP/real LLM                   PASS
```

## 8. Problems Found During Development

- 多候选 root 模型（sibling_roots_probe）暴露 auto-root 歧义 →
  显式 root-selection policy 已按计划处理。

## 9. Known Limitations

- Function 初版映射为 `allocated_to=[]`（v1.0）——1E 发现无法满足
  `list_functions(element_id)` workflow 契约（见 1E-0 Gate）。
- `Component.component_type` 保持 `None`（无证据规则）。
- partial Snapshot 的 workflow 接入行为未覆盖（映射层已支持）。

## 10. Deferred

- Requirement / Port / Interface / Connection / Flow / State / Allocation。
- 多系统模型（多 root）的自动处理。

## 11. Files / Contracts Affected

```text
src/fmea_agent/adapters/sysml/canonical_mapping.py
src/fmea_agent/adapters/sysml/exceptions.py
src/fmea_agent/domain/system_model.py
tests/test_canonical_mapping.py
tests/fixtures/sysml/models/{sibling_roots,no_usage}_probe.sysml
docs/architecture/SYSML_TO_CANONICAL_MAPPING.md
docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md
```

## 12. Final Assessment

COMPLETE

## 13. Next Stage

MVP-1E Workflow Integration。
进入条件：canonical-backed `SystemModelRepository` 满足现有
`SystemModelRepository` Protocol 四方法；真实 .sysml E2E。
