# MVP-1 基准报告

Status: PASS
日期： 2026-09-04

提交（完整锚点表见 `docs/records/MVP_1/MVP_1_RELEASE.md`）:

```text
Benchmark RC:      4f73d22  test/docs: complete MVP-1F benchmark and release candidate
Review Evidence:   5da0f11  docs: add per-item release gate evidence to MVP-1F record
Review Baseline:   369f09d  docs: fix SysML provenance and third-party license notices
```

> 发布后修正（v0.1.1 文档补丁）：`5da0f11` 保留为历史
> 审查证据修订提交，最终独立发布审查基线
> 为 `369f09d`（与发布门禁一致）。

规格说明： `docs/evaluation/MVP_1_BENCHMARK_SPEC.md`
基准测试： `tests/test_mvp1_benchmark.py`（11 个测试）

## 环境

```text
OS:              Windows 11（LOCAL）
Python:          项目 .venv（pyproject pinned）
Parser client:   opensysml==0.4.0（PyPI，Apache-2.0）
Parser runtime:  sysml-grpc v0.4.3 windows-amd64
                 （Open-MBEE/OpenSysML @ commit 99e02003c9c49358828b1c491a75de61745646ce，
                   sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe）
Mapping:         src/fmea_agent/adapters/sysml/canonical_mapping.py（1D/1E）
```

证据分类：全部验证为本机执行（LOCAL）；GitHub Actions
NOT CONFIGURED（无 CI 证据）；基准与发布门禁已通过独立
发布审查（EXTERNAL_REVIEW — ACCEPTED，审查基线 369f09d）。

## B0 — 项目自有最小 Fixture（精确映射）

来源：

```text
tests/fixtures/sysml/models/typed_inside_probe.sysml
（project-owned，1E runtime-probe fixture；符合 Benchmark Spec 的
 minimal fixture 要求，复用而非重复创建）
```

预期（人工编写的参考真值，基于 OpenSysML 0.4.0 + sysml-grpc v0.4.3
运行时探针观察事实，非 Mapper 生成）：

```text
System:      hydraulicPump（system-1）src: TypedInsideProbe::hydraulicPump
Components:  motor（component-1，parent system-1）
             src: TypedInsideProbe::hydraulicPump::motor
Functions:   pumpSpin（function-1 → system-1）
             spin（function-2 → component-1）
Notices:     package → TENTATIVE
             Pump/Motor partDef → NEEDS_RESEARCH
             Spin actionDef → NEEDS_RESEARCH
```

实际：与预期完全一致（test_b0_exact_mapping_matches_gold）。

指标：

```text
Component Precision        1.0
Component Recall           1.0
Function Precision         1.0
Function Recall            1.0
Parent/Containment Accuracy 1.0（exact pairs）
SourceReference Completeness 1.0（全部 mapped entity 的
                           source_element_id 与 gold 精确一致）
Unsupported Element Reporting exact match（4/4 notices）
```

## B1 — 外部官方 SysML 模型

来源追踪：

```text
repository: https://github.com/Systems-Modeling/SysML-v2-Release
commit:     29a3d2acdd49600cff872e7a55962a40400f3335（tag 2026-07）
model:      sysml/src/training/07. Parts/Parts Example-2.sysml
license:    EPL-2.0
sha256:     F3CD762F65D6D51E970CAC2FD597D0785949A3566066FE8B7D6C9679A9D8E491
```

仓库内副本 `tests/fixtures/sysml/models/parts_example_2_official.sysml`
字节级一致（测试内 sha256 断言固化，防 fixture 被“修复”）。

预期（人工编写的参考真值，运行时探针证据）：

```text
System:      vehicle（system-1）src: Parts Example-2::vehicle
Components:  eng（component-1，parent system-1）
             cyl（component-2，parent component-1）
Functions:   []（模型无符合 MVP-1 Mapping Contract 的 Function）
Notices:     package → TENTATIVE
             Vehicle/Engine/Cylinder partDef → NEEDS_RESEARCH（3）
             smallVehicle 子树（3 个 partUsage）→ DEFERRED
             bigVehicle 子树（3 个 partUsage）→ DEFERRED
```

根选择策略：该官方模型含 3 个顶层 PartUsage（vehicle /
smallVehicle / bigVehicle）。不依赖自动选择首个根；显式选择 `vehicle`
为 System 根，根来源 ID 从真实 Snapshot 获取（禁止从字符串猜 FQN）。
自动根选择必须失败并列出全部候选（test_b1_auto_root_rejected_with_candidate_list）。

实际：与预期完全一致（test_b1_explicit_root_mapping_matches_gold）。

指标：

```text
Component Precision         1.0
Component Recall            1.0
Function Precision          N/A（gold 与 actual 均为空；denominator=0，不伪造 100%）
Function Recall             N/A（同上）
Parent/Containment Accuracy 1.0（exact pairs）
SourceReference Completeness 1.0
Unsupported Element Reporting exact match（10/10 notices）
```

## 契约测试

OpenSysML 适配器契约测试（1C/1D，回归基线的一部分）：

```text
tests/test_open_sysml_file_adapter.py
tests/test_sysml_contracts.py
tests/test_canonical_mapping.py
tests/test_canonical_repository.py
```

覆盖：有效文件 / 无效文件 / ID / metatype / 名称 / 所属关系 /
诊断 / 遍历顺序 / 孤儿进程。

## 回归

```text
MVP-0 demo（python -m fmea_agent demo examples/simple_pump.json） PASS
  risk = NOT_EVALUATED / optimization = SKIPPED
全量 pytest（含 MVP-0 全部历史 tests）PASS（见 Release Gate）
```

## 不支持元素的报告

- 未静默丢弃任何 Snapshot 元素：每个元素要么映射，要么产出
  `MappingNotice`（B0 4 条、B1 10 条，均与参考真值精确一致）。
- partDef / actionDef / package / 其他 metatype 不映射（映射矩阵）。

## 已知局限

- 单文件子集（C1）；unresolved import 显式诊断。
- `Model.hash` 为 load-context fingerprint（F1），B1 副本在仓库路径
  加载的 hash 与工作区路径加载不同（预期行为，测试不断言 hash 值）。
- `Component.component_type` 保持 `None`（无证据规则）。
- B1 无 Function：Function Precision/Recall 记为 N/A，不伪造数值。

## 失败 / 偏差

NONE — B0/B1 均一次通过，未暴露生产缺陷，未修改参考真值。

## 发布门禁

门禁分两层：

```text
Implementation / Verification Gate — PASS 16/16（LOCAL evidence）
    逐项 [x] 与证据：docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md §8.1

Independent Release Review      — [x] EXTERNAL_REVIEW — ACCEPTED
    Review baseline: 369f09d

Release execution（已执行，见 docs/records/MVP_1/MVP_1_RELEASE.md）:

    master merge:      2871b23c（--no-ff）
    release closeout:  9c59b4b
    annotated tag:     v0.1.0
```
