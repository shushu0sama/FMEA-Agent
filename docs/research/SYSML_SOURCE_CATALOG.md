# SysML 来源目录

## 本地工作区

```text
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace
```

逻辑目录：

```text
00_docs                 → research notes
01_official_sysml_v2    → OMG / Systems-Modeling official repos
02_sysml_examples       → Delivery Drone / examples
03_agent_interfaces     → API / MCP research
04_parsers_and_runtimes → OpenSysML
05_aerospace_examples   → CubeSat / Spacecraft
06_legacy_mbse_optional → later
07_fmea_benchmark       → benchmark assets
99_experiments          → temporary spikes
```

## MVP-1 P0

### OpenSysML

```text
04_parsers_and_runtimes\OpenSysML
https://github.com/Open-MBEE/OpenSysML
```

作用：File Mode 解析器/运行时，Python/gRPC 集成。

### SysML-v2-Release

预期逻辑位置：

```text
01_official_sysml_v2\SysML-v2-Release
```

在 MVP-1 中的作用：

```text
Training examples
Vehicle examples
semantic reference
```

MVP-1 使用的外部来源记录（MVP-1F，2026-09-04）：

```text
repository: https://github.com/Systems-Modeling/SysML-v2-Release
commit:     29a3d2acdd49600cff872e7a55962a40400f3335 (tag 2026-07)
license:    EPL-2.0

model 1 (1C contract fixture, unmodified copy):
  sysml/src/training/18. Action Performance/Action Performance Example.sysml
  → tests/fixtures/sysml/models/unresolved_import.sysml

model 2 (1F B1 benchmark fixture, unmodified copy):
  sysml/src/training/07. Parts/Parts Example-2.sysml
  → tests/fixtures/sysml/models/parts_example_2_official.sysml
  sha256: F3CD762F65D6D51E970CAC2FD597D0785949A3566066FE8B7D6C9679A9D8E491
```

### API Services / API Cookbook

MVP-1：REFERENCE ONLY。Repository Mode 延后。

### Delivery Drone / Aerospace

MVP-1 主要实现：DEFERRED。

## 政策

第三方仓库：

```text
read-only research sources
```

生产代码不得硬编码本地 D 盘路径。

使用外部模型时记录：

```text
repository URL
commit hash
relative model path
license
```
