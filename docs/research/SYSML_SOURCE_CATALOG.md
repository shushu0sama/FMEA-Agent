# SysML Source Catalog

## Local Workspace

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

Role: File Mode parser/runtime, Python/gRPC integration.

### SysML-v2-Release

Expected logical location:

```text
01_official_sysml_v2\SysML-v2-Release
```

Role in MVP-1:

```text
Training examples
Vehicle examples
semantic reference
```

### API Services / API Cookbook

MVP-1: REFERENCE ONLY. Repository Mode deferred.

### Delivery Drone / Aerospace

MVP-1 primary implementation: DEFERRED.

## Policy

第三方仓库：

```text
read-only research sources
```

Production code 不得硬编码本地 D 盘路径。

使用 external model 时记录：

```text
repository URL
commit hash
relative model path
license
```
