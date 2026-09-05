# MVP-1B — Snapshot 契约收尾记录

状态： COMPLETE
日期： 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. 目标

实现 parser-neutral `SysMLFactSnapshot` 契约模型：

```text
SysMLSource
SysMLElementFact（含 SysMLTypeFacts）
SysMLRelationshipFact
SysMLDiagnostic
SysMLFactSnapshot
```

不依赖 `opensysml` / gRPC / internal AST；不包含 FMEA 字段。

## 2. 范围

范围内：

- 六个契约模型（pydantic v2，`extra="forbid"`，严格 JSON-safe）
- 校验规则 V1–V10
- 规范性文档 `SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- contract tests + `snapshot_minimal.json` fixture

范围外：

- OpenSysML Adapter 实现（1C）
- Canonical Mapping（1D）

## 3. Git

Branch: `feature/mvp1-real-system-facts`

起始 Commit： `94b618f`（1A closeout）

实现 Commit： `8cb98a7` feat: add MVP-1B parser-neutral SysML fact snapshot contracts

收尾 Commit： `bb9e44d` docs: add MVP-1B snapshot contract doc and close out progress

最终 Commit： `bb9e44d`

## 4. 交付内容

- `src/fmea_agent/adapters/sysml/contracts.py` — 契约模型
- `tests/test_sysml_contracts.py` — 55 tests
- `tests/fixtures/sysml/snapshot_minimal.json`
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- `CANONICAL_SYSTEM_MODEL_SPEC.md` §11 指向新契约

## 5. 关键决策

- Snapshot 是 parser/API 事实快照，不是 Canonical System Model；
  不生成 Canonical ID、不做 Mapping。
- Identity honesty：source identity 语义 parser-neutral；
  OpenSysML-specific 事实归 adapter profile。
- Facts-absence 用 `None` 表达，不推断（C4）。
- diagnostics first-class；partial Snapshot 必须能表达不完整原因。
- relationship `target_id` open-world；containment 由 `owner_id` 承载。
- 契约层不验证 `source_id` 格式（不要求 FQN 形状）。

## 6. 证据

- 契约：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
- 测试：`tests/test_sysml_contracts.py`
- C1–C4 覆盖表：契约文档 §9

## 7. 验证

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

## 8. 开发中发现的问题

无记录在案的 major RED。

## 9. 已知限制

- 不承诺 byte-identical JSON dump（canonical deterministic
  serialization 延后）。

## 10. 延后事项

- Adapter extraction scope / traversal / 排序（属 adapter policy，1C）。
- Repository API / 多文件 import。

## 11. 涉及文件 / 契约

```text
src/fmea_agent/adapters/sysml/contracts.py
tests/test_sysml_contracts.py
tests/fixtures/sysml/snapshot_minimal.json
docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md
docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md
```

## 12. 最终评估

COMPLETE

## 13. 下一阶段

MVP-1C OpenSysML Adapter。
进入条件：1C-0 Dependency Reproduction Gate（PyPI pin 确认）。
