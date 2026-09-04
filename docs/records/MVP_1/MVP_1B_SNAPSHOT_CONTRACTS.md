# MVP-1B — Snapshot Contracts Closeout Record

Status: COMPLETE
Date: 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. Objective

实现 parser-neutral `SysMLFactSnapshot` 契约模型：

```text
SysMLSource
SysMLElementFact（含 SysMLTypeFacts）
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

不依赖 `opensysml` / gRPC / internal AST；不包含 FMEA 字段。

## 2. Scope

In Scope:

- 六个契约模型（pydantic v2，`extra="forbid"`，严格 JSON-safe）
- 校验规则 V1–V10
- 规范性文档 `SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- contract tests + `snapshot_minimal.json` fixture

Out of Scope:

- OpenSysML Adapter 实现（1C）
- Canonical Mapping（1D）

## 3. Git

Branch: `feature/mvp1-real-system-facts`

Start Commit: `94b618f`（1A closeout）

Implementation Commit(s): `8cb98a7` feat: add MVP-1B parser-neutral SysML fact snapshot contracts

Closeout Commit(s): `bb9e44d` docs: add MVP-1B snapshot contract doc and close out progress

Final Commit: `bb9e44d`

## 4. Delivered

- `src/fmea_agent/adapters/sysml/contracts.py` — 契约模型
- `tests/test_sysml_contracts.py` — 55 tests
- `tests/fixtures/sysml/snapshot_minimal.json`
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- `CANONICAL_SYSTEM_MODEL_SPEC.md` §11 指向新契约

## 5. Key Decisions

- Snapshot 是 parser/API 事实快照，不是 Canonical System Model；
  不生成 Canonical ID、不做 Mapping。
- Identity honesty：source identity 语义 parser-neutral；
  OpenSysML-specific 事实归 adapter profile。
- Facts-absence 用 `None` 表达，不推断（C4）。
- diagnostics first-class；partial Snapshot 必须能表达不完整原因。
- relationship `target_id` open-world；containment 由 `owner_id` 承载。
- 契约层不验证 `source_id` 格式（不要求 FQN 形状）。

## 6. Evidence

- 契约：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- 测试：`tests/test_sysml_contracts.py`
- C1–C4 覆盖表：契约文档 §9

## 7. Verification

```text
pytest 134 passed（79 MVP-0 + 55 MVP-1B） PASS（LOCAL，Windows）
ruff check .                              PASS（LOCAL）
mypy src                                  PASS（LOCAL）
无 opensysml/grpc/protobuf import         PASS（AST 级测试固化）
无 FMEA/Canonical 字段                    PASS（schema 白名单测试固化）
JSON round-trip 语义相等                   PASS
pyproject.toml 未修改                      PASS
MVP-0 regression                          PASS
```

## 8. Problems Found During Development

无记录在案的 major RED。

## 9. Known Limitations

- 不承诺 byte-identical JSON dump（canonical deterministic
  serialization 延后）。

## 10. Deferred

- Adapter extraction scope / traversal / 排序（属 adapter policy，1C）。
- Repository API / 多文件 import。

## 11. Files / Contracts Affected

```text
src/fmea_agent/adapters/sysml/contracts.py
tests/test_sysml_contracts.py
tests/fixtures/sysml/snapshot_minimal.json
docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md
docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md
```

## 12. Final Assessment

COMPLETE

## 13. Next Stage

MVP-1C OpenSysML Adapter。
进入条件：1C-0 Dependency Reproduction Gate（PyPI pin 确认）。
