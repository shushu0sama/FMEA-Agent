# OpenSysML Feasibility Spike
## MVP-1A

目的：在生产 Adapter 编码前，用当前 Windows 11 + 本地 OpenSysML checkout 验证真实 API。

## Local checkout

```text
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML
```

第三方仓库保持只读。

## Step 1 — 记录版本

```powershell
git -C "D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML" status
git -C "D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML" remote -v
git -C "D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\04_parsers_and_runtimes\OpenSysML" log -1 --oneline
```

记录 branch / commit / remote / license。

## Step 2 — 阅读当前真实文档

优先检查：

```text
README
python/
python/INSTALL.md
docs/
examples/
testdata/
cmd/sysml-grpc/
api/proto/
```

## Step 3 — 独立实验

推荐：

```text
FMEA-Agent-SysML-Workspace\99_experiments\opensysml_mvp1_spike
```

不要在 OpenSysML repo 内写自研实验。

## Step 4 — 必须验证

1. Python client 的实际安装方式。
2. `sysml-grpc` 是否自动启动、如何解析 binary、Windows x64 是否可重复运行。
3. 当前 public API 的最小 load/parse 调用。
4. 合法/非法模型 diagnostics。
5. public query/traversal 能否获得：
   - `PartDefinition`
   - `PartUsage`
   - `ActionDefinition`
   - `ActionUsage`
6. element identity 语义。
7. ownership / children / metatype / name。
8. single-file 与 multi-file/import 的实际行为。

不要根据记忆猜 API；以当前 checkout、文档、测试和真实运行结果为准。

## Spike Output

必须生成：

```text
docs/research/OPENSYSML_SPIKE_REPORT.md
```

至少记录：

```text
Environment
OpenSysML commit/release
Python client install method
sysml-grpc resolution
first successful load
public API used
ID semantics
ownership semantics
diagnostics
Windows issues
recommended dependency pin
known limitations
GO / CONDITIONAL_GO / NO_GO
```

## GO Gate

允许继续生产实现的最低条件：

```text
Windows 可重复启动
合法 .sysml 可解析
public API 能获得足够 Part/Action facts
diagnostics 可处理
不需要修改 OpenSysML 源码
```

Spike 阶段禁止写大规模 production Adapter、修改 Domain、接 Neo4j/RAG/MCP/LLM。
