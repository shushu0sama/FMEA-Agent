# MVP-1A — OpenSysML Feasibility Spike Closeout Record

Status: COMPLETE（gate 结论 CONDITIONAL_GO）
Date: 2026-09-04（回填自 Git history + PROGRESS.md）

## 1. Objective

验证 OpenSysML 能否作为 MVP-1 的 SysML v2 File Mode 事实源：

```text
commit/release、Windows Python client、sysml-grpc、
load/parse、diagnostics、query/traversal、IDs、ownership
```

自建 minimal model + 至少一个官方 Training example。

## 2. Scope

In Scope:

- OpenSysML public API 实证（只读，不修改第三方 repo）
- Windows 11 + Python client + sysml-grpc runtime
- 生成 `docs/research/OPENSYSML_SPIKE_REPORT.md`
- Gate：GO / CONDITIONAL_GO / NO_GO

Out of Scope:

- production Adapter 实现
- 修改 FMEA Agent production code
- 修改第三方 OpenSysML repo

## 3. Git

Branch: `feature/mvp1-real-system-facts`

Start Commit: `c520586` docs: prepare MVP-1 real system facts development

Implementation Commit(s):

- `8a50850` docs: align MVP-1 progress with file-mode scope
- `41be670` docs: add MVP-1A OpenSysML feasibility spike report

Closeout Commit(s): `94b618f` docs: close MVP-1A with CONDITIONAL_GO

Final Commit: `94b618f`

## 4. Delivered

- `docs/research/OPENSYSML_SPIKE_REPORT.md`（详细实证证据）
- `docs/research/OPENSYSML_FEASIBILITY_SPIKE.md`（spike 设计）
- `docs/adr/ADR-008-opensysml-file-mode-first.md`（ACCEPTED）
- 1A 结论与 binding conditions C1–C4 写入 PROGRESS.md

## 5. Key Decisions

- Gate 结论：**CONDITIONAL_GO**（不是无条件 GO）。
- ADR-008：File Mode first；Repository API / MCP 延后。
- C1 — standalone 单文件子集；用户文件 import 不支持；
  unresolved import 必须产出显式 `SysMLDiagnostic`。
- C2 — pin `opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3`
  windows-amd64（SHA-256 记录于 Spike 报告）。
- C3 — source identity 为 name-derived FQN；rename 改变 source ID；
  不得宣称为跨版本稳定 Canonical identity。
- C4 — performed ActionUsage public facts 不足以推导 function typing；
  禁止发明类型关系；Mapping 按 UNKNOWN / NEEDS_RESEARCH 处理。

## 6. Evidence

Detailed evidence（不复制）:

- `docs/research/OPENSYSML_SPIKE_REPORT.md`
- `docs/research/OPENSYSML_FEASIBILITY_SPIKE.md`
- `docs/adr/ADR-008-opensysml-file-mode-first.md`

## 7. Verification

```text
Spike probes（OpenSysML checkout，真实 runtime） PASS（LOCAL，Windows）
官方 Training example 单文件 standalone 名单     PASS（5 个，见 Spike 报告）
```

本阶段未修改 production code；无 pytest 增量。

## 8. Problems Found During Development

- OpenSysML `Symbol.children` 为方法（非属性）— 记录于 adapter 阶段采用。
- performed ActionUsage typing 链接缺失（C4 来源）。

## 9. Known Limitations

- 单文件子集（C1）；跨版本 identity 不稳定（C3）。

## 10. Deferred

- SysML Repository API、MCP（ADR-008）。

## 11. Files / Contracts Affected

```text
docs/research/OPENSYSML_SPIKE_REPORT.md
docs/research/OPENSYSML_FEASIBILITY_SPIKE.md
docs/adr/ADR-008-opensysml-file-mode-first.md
docs/architecture/SYSML_TO_CANONICAL_MAPPING.md（初始矩阵）
PROGRESS.md
```

## 12. Final Assessment

COMPLETE — 结论 CONDITIONAL_GO（binding conditions C1–C4）

## 13. Next Stage

MVP-1B Snapshot Contracts。
进入条件：C1–C4 纳入 1B 契约设计。
