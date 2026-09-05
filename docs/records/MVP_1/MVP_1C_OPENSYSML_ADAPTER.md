# MVP-1C — OpenSysML 适配器收尾记录

状态： COMPLETE
日期： 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. 目标

实现 `OpenSysMLFileAdapter`：

```text
.sysml file → OpenSysML public API → SysMLFactSnapshot
```

包含 dependency pin、exception translation、diagnostics retention、
contract tests。

## 2. 范围

范围内：

- `opensysml==0.4.0` 精确 pin + sysml-grpc v0.4.3（C2）
- 1C-0 Dependency Reproduction Gate（独立 throwaway venv 复现验证）
- 单文件子集 + 显式诊断（C1）
- exception 边界：`SysMLError` / `SysMLLoadError` / `SysMLParseError` /
  `UnsupportedSysMLElement`
- 真实 `.sysml` fixtures（含官方 Training Example 未修改副本）

范围外：

- Canonical Mapping / System / Component / Function（1D）
- KG / RAG / MCP / real LLM

## 3. Git

Branch: `feature/mvp1-real-system-facts`

起始 Commit： `bb9e44d`（1B closeout）

实现 Commit：

- `4d15bf0` docs: confirm OpenSysML PyPI dependency for MVP-1C（1C-0 Gate）
- `3cb02ef` feat: add MVP-1C OpenSysML file-mode adapter

收尾 Commit：

- `61c69d8` docs: close MVP-1C with F1 hash semantics correction
- `4f141dd` fix: preserve source traversal order and relax orphan check (MVP-1C)

最终 Commit： `4f141dd`

## 4. 交付内容

- `src/fmea_agent/adapters/sysml/open_sysml_file.py` —
  `load(file_path) -> SysMLFactSnapshot`；`expanduser().resolve(strict=True)`
  路径策略；显式 `opensysml.connect(version="v0.4.3")`；
  `Connection.load(strict=True)`；partial model → partial Snapshot；
  真实 `Symbol.children()` traversal；`type_facts` 空串→None、全 None→None（C4）；
  relationships 来自真实 `Symbol.specializations`；`Model.hash` 原样记录（F1）；
  Diagnostic 全字段翻译、span 不泄漏 protobuf
- `src/fmea_agent/adapters/sysml/exceptions.py`
- `pyproject.toml` — `opensysml==0.4.0` pin；`uv.lock` 更新
- fixtures：`perform_probe.sysml` / `invalid_syntax.sysml` /
  `unresolved_import.sysml`（官方 Training Example，EPL-2.0，
  溯源见 `tests/fixtures/sysml/README.md`）
- `tests/test_open_sysml_file_adapter.py` — 28 contract/integration tests
- 1C closeout fixes：sibling 遍历顺序 = 源文件顺序；orphan 检查 =
  PID 集合比对；新增 fixtures `sibling_roots_probe.sysml` /
  `no_usage_probe.sysml` + regression tests

## 5. 关键决策

- **1C-0 Dependency Reproduction Gate（新增 Gate，记录演化）**：
  原 1C 计划未含独立复现 Gate。证据触发：1A Spike 的 checkout 证据
  与 PyPI wheel 环境可能存在差异风险。结论 PYPI_PIN_CONFIRMED：
  PyPI wheel 在独立 venv 重跑 13 项 probe 与 checkout 证据逐项 MATCH；
  wheel 与 checkout client source 内容等价（28/28 文件）。
  不改变原 architecture，仅固化 C2 pin。
- **F1 — `Model.hash` 语义修正**：不是纯内容哈希，是 load-context
  fingerprint（SHA256(name + per-file content sha256)，按 name 排序；
  不同路径字符串 → 不同 hash）。正式语义写入 Snapshot 契约 §4：
  `model_hash` 不是 Canonical ID、不是跨路径稳定 identity、不得用于
  跨版本实体 identity 判断；adapter 原样记录，禁止重实现 hash 算法。
  此修正写入契约文档（v1.1），并成为 1C Adapter Profile 的一部分。
- C2 pin 确认（PyPI wheel sha256 + sysml-grpc 二进制 sha256 见
  Dependency Inventory）。
- orphan 检查：digest-link 进程名 `sysml-grpc-0b188ec140872c0f`，
  用通配符 `sysml-grpc*` 检查；不误伤已有合法进程（PID 集合比对）。

## 6. 证据

详细证据（不复制）：

- `docs/research/OPENSYSML_SPIKE_REPORT.md`（1A）
- `docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`（1C-0）
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` §4/§8（F1、Adapter Profile）
- `tests/fixtures/sysml/README.md`（fixture 溯源）

## 7. 验证

```text
opensysml==0.4.0 精确 pin                       PASS
uv lock --check / uv sync --frozen              PASS
runtime = sysml-grpc v0.4.3                     PASS（server_info 实测）
valid .sysml → ok Snapshot                      PASS
invalid model → partial + diagnostics           PASS（2 error 诊断保留）
unresolved import → 4 error 显式诊断            PASS
RootNamespace 不进入 elements                   PASS
owner_id 来自真实 traversal parent              PASS
type_facts 不推断（definitions/performed = None）PASS
performed ActionUsage 无 fabricated typing       PASS（C4）
Model.hash 原样记录 + 同路径可重复 + 路径上下文相关 PASS（F1）
Snapshot JSON round-trip 语义相等               PASS
无 protobuf/grpc object 泄漏（span=None）        PASS
success/partial/error 后连接正确关闭            PASS
无 sysml-grpc* orphan process                   PASS（通配符检查 0）
pytest 162 passed（134 基线 + 28 新增）          PASS（LOCAL，closeout commit 61c69d8）
pytest 164 passed（closeout fix 4f141dd 后）      PASS（LOCAL）
ruff / mypy（strict）                           PASS（LOCAL）
MVP-0 demo regression                           PASS
```

注：162 为 closeout commit 记录数；4f141dd 增加 traversal-order /
orphan regression 后为 164（1D 记录中的基线）。

## 8. 开发中发现的问题

- F1：hash 语义与直觉不符 → 契约修正（§5）。
- sibling 遍历顺序 bug（`_walk()` 顶层顺序）→ RED 固化 + 修复。
- orphan 进程检查误报风险（进程名带 digest 后缀）→ 通配符 + PID 集合。
- digest-link 自动下载回退：client 0.4.0 digest 表只 pin 到 v0.3.0
  （v0.4.3 不在表内，属已知限制）。

## 9. 已知限制

- 单文件子集；用户文件 import 不支持（C1）。
- `Model.hash` 为 load-context fingerprint（F1）。
- performed ActionUsage 无 typing facts（C4）。
- runtime provisioning 依赖本机缓存 / 环境变量。

## 10. 延后事项

- Repository API / MCP / 多文件 import。

## 11. 涉及文件 / 契约

```text
src/fmea_agent/adapters/sysml/open_sysml_file.py
src/fmea_agent/adapters/sysml/exceptions.py
src/fmea_agent/adapters/sysml/__init__.py
pyproject.toml / uv.lock
tests/test_open_sysml_file_adapter.py
tests/fixtures/sysml/README.md + models/*
docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md（v1.1）
docs/research/DEPENDENCY_INVENTORY.md
docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md
```

## 12. 最终评估

COMPLETE（含 1C-0 Gate PYPI_PIN_CONFIRMED）

## 13. 下一阶段

MVP-1D Canonical Mapping。
进入条件：Snapshot 契约稳定、Adapter 隔离、C1–C4/F1 语义固化。
