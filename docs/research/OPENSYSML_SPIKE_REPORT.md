# OpenSysML Feasibility Spike Report
## MVP-1A — 2026-09-04

> 证据等级：`CONFIRMED_RUNTIME`（本机实际执行成功）/ `CONFIRMED_SOURCE`（当前 checkout 官方 source/tests 明确支持）/ `DOCUMENTED`（官方文档明确说明，未实际运行）/ `OBSERVED_INTERNAL`（仅内部实现可见，禁止 production 依赖）/ `UNKNOWN`。

# Environment

| 项 | 值 |
|---|---|
| OS | Microsoft Windows NT 10.0.26200.0（Windows 11 Pro） |
| Architecture | AMD64 (x64) |
| PowerShell | 5.1.26100.9168 |
| Python | 3.13.9（系统）；Spike venv 用 uv 以 3.13.9 创建 |
| uv | 0.11.7 |
| Go | not installed（本轮未需要：直接使用 release 二进制） |
| 实验目录 | `D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\99_experiments\opensysml_mvp1_spike` |

# OpenSysML Version

| 身份 | 值 | 证据 |
|---|---|---|
| Git commit（本地 checkout） | `ef03da889285a9a5c71bcec9dd7b67b8b3e1a599`（`main`，与 origin/main 一致；shallow clone，grafted） | CONFIRMED_RUNTIME（git rev-parse + ls-remote） |
| Python package version | `opensysml` **0.4.0**（`clients/python/opensysml/_version.py`；安装后 `opensysml.__version__` 实测 0.4.0） | CONFIRMED_RUNTIME |
| 最新 `opensysml-v*` release tag | `opensysml-v0.4.0`（peeled `91f595c…`）；另有 legacy `pysysml-v0.2.1` 与 plain `v0.4.3` 等 tag | CONFIRMED_SOURCE（git ls-remote --tags） |
| 实际运行的 sysml-grpc | **v0.4.3**（`sysml-grpc --version` → `commit 99e02003c9c49358828b1c491a75de61745646ce`，与 plain tag `v0.4.3` 一致） | CONFIRMED_RUNTIME |
| License | Apache-2.0（根 `LICENSE`；pyproject `license = "Apache-2.0"`） | CONFIRMED_SOURCE |

三者关系：本地 checkout = remote main tip，晚于 `opensysml-v0.4.0` tag（版本号仍为 0.4.0 的开发状态）；缓存的 v0.4.3 服务二进制来自 GitHub release `v0.4.3`。本地 checkout 与 opensysml-v0.4.0 之间的精确提交距离因 shallow clone 为 UNKNOWN（不影响本轮结论）。

# Installation

以当前 checkout 为唯一来源（未使用 PyPI 的 `pip install opensysml`）：

```powershell
uv venv .venv --python 3.13      # CPython 3.13.9
uv pip install --python .venv\Scripts\python.exe "<checkout>\clients\python"
```

结果：**成功**（CONFIRMED_RUNTIME）。`opensysml==0.4.0` 以非 editable 方式装入 spike venv（34 个包，grpcio 1.83.1 / protobuf 7.36.1 等）。安装后 OpenSysML checkout `git status` 保持 clean —— 非 editable 安装不会污染第三方仓库。

- package name / import name：`opensysml`（legacy `pysysml` 为 PyPI 占位包，导入即报错并提示改名） — DOCUMENTED + CONFIRMED_SOURCE
- requires-python：`>=3.10`；classifiers 声明 3.10–3.13 — CONFIRMED_SOURCE
- editable 安装官方支持（`pip install -e clients/python/`），但会向第三方 checkout 写入 egg-info —— 违反 READ-ONLY 约束，production 应使用非 editable 安装或 PyPI 安装 — DOCUMENTED
- PyPI 上 `opensysml==0.4.0` 可解析（`uv pip install --dry-run` 通过）— CONFIRMED_RUNTIME
- 未修改 FMEA-Agent `pyproject.toml` — 事实陈述

# sysml-grpc Runtime

| 问题 | 结论 | 证据 |
|---|---|---|
| sysml-grpc 是什么 | Go 编写的 SysML v2 parser/runtime 服务；Python client 的每个调用都经 gRPC 到达它 | DOCUMENTED（docs/guide/09-python.md）+ CONFIRMED_RUNTIME |
| Python client 如何找到它 | 解析顺序：`$OPENSYSML_BINARY` → `~/.opensysml/bin/sysml-grpc(.exe)` → 被请求的 release download 进缓存 → `$PATH` | DOCUMENTED（clients/python/README.md） |
| 是否自动启动 | **是**。未命名服务的 connection 启动 private child（port 0，内核分配端口，stdout 报告地址）；同解释器共享一个 child，随最后一个 connection 关闭或解释器退出而停止 | CONFIRMED_RUNTIME（ServerInfo.origin 显示 `started by this client`，运行后无孤儿进程） |
| 是否自动下载 | 仅当显式请求 release（`ensure_binary(version=…)` 或 `$OPENSYSML_GRPC_VERSION`）；默认不下载，缺失时 `ConnectionError` 列出所有查找位置 | DOCUMENTED（未实际触发下载，因缓存已命中） |
| 是否 bundled | 否。独立二进制，SHA-256 校验下载（client 0.4.0 的 digest 表只 pin 到 v0.3.0，含 `sysml-grpc-windows-amd64.exe`） | CONFIRMED_SOURCE（release-digests.json） |
| Windows x64 binary | **有**。缓存中 v0.4.3 windows-amd64 二进制可直接运行；v0.0.5–v0.3.0 每个 release 都有 windows-amd64 asset 且 digest 已 pin | CONFIRMED_RUNTIME（v0.4.3）+ CONFIRMED_SOURCE（pin 表） |
| transport | gRPC over loopback（port 0）；`cmd/sysml-grpc/stdio.go` 亦存在 stdio transport 实现 | CONFIRMED_RUNTIME（连接成功）+ CONFIRMED_SOURCE |
| process lifecycle | stdin-pipe 归属模型：client 持有 child stdin 写端，进程退出内核关闭管道 → child 退出；两轮全新进程运行后 `Get-Process sysml-grpc` 计数为 0 | CONFIRMED_RUNTIME |
| failure behavior | 无二进制时 `ConnectionError` 列出查找位置；release 不匹配时 `StaleServiceError`；能力缺失时 `MissingCapabilityError` | DOCUMENTED |
| 缓存现状 | `~/.opensysml/bin/sysml-grpc.exe`（v0.4.3）+ 同名 `.json` 元数据（version/sha256/repo）+ digest 链接 `sysml-grpc-0b188ec140872c0f.exe`；client 从 digest 链接启动 | CONFIRMED_RUNTIME（ServerInfo.origin） |

# Confirmed Public API

仅列本轮实际执行验证或官方 source 明确支持的 public interface。未运行验证的一律不列。

| API | Evidence | Execution result | Classification |
|---|---|---|---|
| `opensysml.load(path)` | spike `scripts/01_first_load.py` | 成功返回 `Model`（0.09–0.12 s） | CONFIRMED_RUNTIME |
| `opensysml.load(path, strict=True)` | spike `scripts/02_diagnostics.py` | 语法错误模型 raise `ModelError`（带 `.diagnostics` + `.model`） | CONFIRMED_RUNTIME |
| `opensysml.load(path, strict_conformance=True)` | spike 运行 | 纯 SysML v2 模型 `ok=True` | CONFIRMED_RUNTIME |
| `opensysml.loads(content, language=…)` | README + guide 示例 | 未运行（inline 内容加载） | DOCUMENTED |
| `opensysml.connect()` / `Connection.server_info()` | spike 运行 | `ServerInfo(version='v0.4.3', capabilities={…17 项…}, origin=…)` | CONFIRMED_RUNTIME |
| `Connection.close()` / context manager | spike 运行 | 正常关闭，无孤儿进程 | CONFIRMED_RUNTIME |
| `Model.hash` | spike 运行 | 内容哈希，同文件跨进程一致 | CONFIRMED_RUNTIME |
| `Model.ok` / `Model.errors` / `Model.diagnostics` / `Model.raise_for_errors()` | spike 运行 | 合法 0 条；非法 2 条 error | CONFIRMED_RUNTIME |
| `Model.root`（`Symbol`, kind=`RootNamespace`, id=`''`） | spike 运行 | 根命名空间 | CONFIRMED_RUNTIME |
| `Model[name]` / `Model.find(name)` / `Model.get(fqn)` | spike 运行 | 短名/FQN 查找；`find` 未命中返回 None | CONFIRMED_RUNTIME |
| `Model.query(payload \| scope/select/where)` | spike 运行 | 按 `@type` 过滤 PartDefinition/PartUsage/ActionDefinition/ActionUsage 全部命中；返回 `QueryElement(id, type, properties)` | CONFIRMED_RUNTIME |
| `Model.eval(expr)` / `Model.execute_action` / `verify_*` / `instantiate` | guide 文档 | 未运行（MVP-1 不需要 execution/verification） | DOCUMENTED |
| `Symbol.id` | spike 运行 | **fully-qualified name**（如 `PerformProbe::hydraulicPump::motor`） | CONFIRMED_RUNTIME |
| `Symbol.kind` | spike 运行 | 小驼峰 metatype：`package`/`partDef`/`partUsage`/`actionDef`/`actionUsage`/`attributeUsage` | CONFIRMED_RUNTIME |
| `Symbol.name` | spike 运行 | 短名 | CONFIRMED_RUNTIME |
| `Symbol.children()` | spike 运行 | 完整符号树遍历成功（注意：是方法不是属性） | CONFIRMED_RUNTIME |
| `Symbol.attributes()` / `parts()` / `get_attr()` | guide 文档 + dir 确认存在 | 分类子元素访问；未逐项运行 | DOCUMENTED |
| `Symbol.type_facts` / `Symbol.specializations` / `Symbol.multiplicity` / `Symbol.facts()` | spike 运行 | `TypeFacts(declared, resolved_id, resolved_kind, …)`；`Specialization(kind='typing', target_id, target_kind)` | CONFIRMED_RUNTIME |
| `Symbol.metadata` | spike 运行 | dict（`visibility`, `type` 等） | CONFIRMED_RUNTIME |
| `Diagnostic.severity / message / file / start_line / start_column / end_line / end_column / span` | spike 运行 | 完整 locator | CONFIRMED_RUNTIME |
| `opensysml.ModelError`（`.diagnostics`, `.model`） | spike 运行 | strict load 异常携带 partial model | CONFIRMED_RUNTIME |
| 异常层级（`OpenSysMLError` → `ConnectionError/ServiceError/ModelError/SymbolNotFoundError/…`） | guide 文档 | 未逐项触发 | DOCUMENTED |

注意：`Symbol.children` 是方法（`children()`），直接迭代属性会 `TypeError` —— Adapter 需写对调用形式。

# Load / Parse

- 最小合法模型（自建，语法取自官方 Training Examples）首轮即被解析；两处真实语法错误（bare `Real`、无 visibility 的 `import`）分别被精确诊断为 `unresolved reference: Real — did you mean ScalarValues::Real?` 与 `import without a visibility indicator`（带 file:line:col）—— parser 诊断质量高（CONFIRMED_RUNTIME）。
- 修复后 `model.ok=True`，0 diagnostics（CONFIRMED_RUNTIME）。
- `perform action spin;`（performed action usage）解析正常（CONFIRMED_RUNTIME）。
- 首次加载耗时 0.09–0.12 s（含服务已启动状态；首个 connection 启动服务约 7 ms 量级，见官方 benchmark —— DOCUMENTED）。

# Diagnostics

| 场景 | 结果 |
|---|---|
| 非法语法模型 | `model.ok=False`；2 条 error：`expected '{' or ';' after declaration`、`expected '}'`，str 形式含 `file:line:col: severity: message`（CONFIRMED_RUNTIME） |
| diagnostic 对象字段 | `severity`（`error`）、`message`、`file`、`start_line`、`start_column`、`end_line`、`end_column`、`span`（CONFIRMED_RUNTIME） |
| strict 加载 | `ModelError` 携带 `.diagnostics` 与 `.model`（partial model 可继续检查）（CONFIRMED_RUNTIME） |
| 合法模型 | 0 diagnostics（CONFIRMED_RUNTIME） |
| partial result 行为 | 非法模型仍返回 `Model`（缺失声明可被查询），由调用方决定是否接受 —— Adapter 翻译为 `SysMLParseError`/`SysMLDiagnostic` 的素材充分（CONFIRMED_RUNTIME） |

结论：未来 Adapter 可以把 `Diagnostic` 直接翻译为项目自有的 `SysMLDiagnostic`，把 strict 加载的 `ModelError` 翻译为 `SysMLLoadError`/`SysMLParseError` 边界。

# Query / Traversal

对 `02_perform_probe.sysml`（含 2 part def、1 action def、root part usage + nested part usage、top-level action usage、performed action usage）：

```
RootNamespace
└─ PerformProbe (package)
   ├─ Pump (partDef)
   ├─ Motor (partDef)
   ├─ Spin (actionDef) └─ speed (attributeUsage)
   ├─ hydraulicPump (partUsage) └─ motor (partUsage) └─ spin (actionUsage)
   └─ spin (actionUsage)
```

- `model.query` 按 `@type` 过滤四种 metatype 全部命中；`QueryElement` 提供 `id`（FQN）、`type`（metamodel type）、`properties`（name/qualifiedName 等）、`as_dict()`（标准 JSON 形式）—— CONFIRMED_RUNTIME
- 标准 query model **无图遍历/传递闭包**（`scope` 表达子树，无法表达 "specializing 此定义的所有元素"）—— DOCUMENTED；全树遍历靠 `Symbol.children()` 递归 —— CONFIRMED_RUNTIME

# PartDefinition

- 查询得到：`PerformProbe::Pump`、`PerformProbe::Motor`（type `PartDefinition`）（CONFIRMED_RUNTIME）
- `Symbol.kind='partDef'`；`Symbol.facts()` 给出 `attributes`（如无）；无 typing specialization（定义本身不 typed）—— CONFIRMED_RUNTIME
- 官方示例 `Part Definition Example.sysml`、`Parts Example-1/2.sysml` 全部 `ok=True` —— CONFIRMED_RUNTIME

# PartUsage

- 查询得到：`PerformProbe::hydraulicPump`、`PerformProbe::hydraulicPump::motor`（type `PartUsage`）；嵌套关系体现于 FQN —— CONFIRMED_RUNTIME
- `type_facts`：`TypeFacts(declared='Pump', resolved_id='PerformProbe::Pump', resolved_kind='partDef')`；`specializations=[Specialization(kind='typing', target_id='PerformProbe::Pump')]` —— usage→definition 类型链接可获取 —— CONFIRMED_RUNTIME
- `multiplicity=None`（未声明 multiplicity）—— CONFIRMED_RUNTIME

# ActionDefinition

- 查询得到：`PerformProbe::Spin`（type `ActionDefinition`）；`Symbol.kind='actionDef'`；`facts().attributes` 含 `in speed : ScalarValues::Real` 参数 —— CONFIRMED_RUNTIME
- 官方示例 `Action Definition Example.sysml`、`Action Decomposition.sysml` 均 `ok=True` —— CONFIRMED_RUNTIME

# ActionUsage

- 查询得到两个 ActionUsage：顶层 `PerformProbe::spin` 与 performed `PerformProbe::hydraulicPump::motor::spin` —— CONFIRMED_RUNTIME
- 顶层 usage：`type_facts(declared='Spin', resolved_id='PerformProbe::Spin', resolved_kind='actionDef')` + typing specialization —— 可获取 —— CONFIRMED_RUNTIME
- **performed action usage**（`perform action spin;`）：parser 层作为嵌套 ActionUsage 出现在 part 之下（FQN `…::motor::spin`），但其 `type_facts` 为空（`declared=''`、无 resolved_id）、`specializations=[]` —— 与所引用 behavior 的链接在 public Symbol facts 中不可见 —— CONFIRMED_RUNTIME（**Mapping 阶段关键约束：performed action 的类型链接需另行研究或按 UNKNOWN 处理**）

# Element Identity

| 问题 | 结论 | 证据 |
|---|---|---|
| source ID 从哪里来 | `Symbol.id` = **fully-qualified name**（`rdf.EncodeElementID` 派生的 qualified name 编码）；textual notation 本身不携带 identity | CONFIRMED_RUNTIME + CONFIRMED_SOURCE（docs/project/element-identity-annotations.md） |
| 与 display name 独立？ | **否**。id 由 qualified name 派生；改名/移动 = id 改变（官方文档明言 "A rename is a delete plus a create"） | CONFIRMED_SOURCE |
| 同一次 load 内稳定 | 是 | CONFIRMED_RUNTIME |
| 重复 load（同进程）稳定 | 是（相同 id 集合与 hash） | CONFIRMED_RUNTIME |
| 跨进程稳定 | 是（两次独立进程输出逐字节一致） | CONFIRMED_RUNTIME |
| definition / usage 各有 identity | 是（`PerformProbe::Pump` vs `PerformProbe::hydraulicPump` 是不同 id） | CONFIRMED_RUNTIME |
| 模型级 identity | `model.hash`（内容哈希）跨进程一致，可作 source-version 快照字段 | CONFIRMED_RUNTIME |
| 跨 version 稳定性 | 文件内容不变则稳定；改名/移动则变。跨模型版本的身份延续 UNKNOWN（官方提供可选 in-band `@ElementId` metadata 注释机制，属 repository-bound identity 设计，File Mode 下是否采用由 Mapping/Adapter 阶段决策） | CONFIRMED_SOURCE |

**禁止把 display name 当 ID** 在本 public 表示下天然满足：`id` 是 FQN 字符串、`name` 是短名字段，两者分离，但 id 的稳定性耦合于名字不改变。

# Ownership / Containment

构造 root part usage + nested part usage + nested（performed）action usage 的模型后验证：

- ownership 在 public representation 中通过 **FQN 前缀** 表达（`PerformProbe::hydraulicPump::motor` 的 owner 可推出为 `PerformProbe::hydraulicPump`），并通过 **`Symbol.children()` 树** 显式遍历 —— CONFIRMED_RUNTIME
- 没有独立的 `owner` 字段；owner 需从 id 前缀推导或自上而下遍历 —— CONFIRMED_RUNTIME
- namespace/package 是符号树中的普通节点（kind=`package`）—— CONFIRMED_RUNTIME

本轮只回答 "OpenSysML 返回什么"；不做 System/Component 映射。

# Official Training Example Results

本地 `SysML-v2-Release`（`master @ 29a3d2a`，tag `2026-07`）：

| Example | 单文件加载 |
|---|---|
| `02. Part Definitions/Part Definition Example.sysml` | **PASS**（ok=True，0 diagnostics） |
| `07. Parts/Parts Example-1.sysml` | **PASS** |
| `07. Parts/Parts Example-2.sysml` | **PASS** |
| `14. Action Definitions/Action Definition Example.sysml` | **PASS** |
| `15. Actions/Action Decomposition.sysml` | **PASS** |
| `18. Action Performance/Action Performance Example.sysml` | **FAIL**（4 条 error：`unresolved reference: Action Decomposition` 及级联的 takePicture/focus/shoot） |

失败原因：该文件含 `private import 'Action Decomposition'::*;` 用户文件 import（见下节）。官方文件未被修改。

# Single-file / Multi-file / Import

| 场景 | 行为 | 证据 |
|---|---|---|
| standalone 单文件 | 完全可用（自建模型 + 5 个官方示例） | CONFIRMED_RUNTIME |
| 标准库 import（`ScalarValues::*`、`SI`、`ISQ` 等） | 可用（标准库内嵌于服务，`OPENSYSML_LIBRARY_PATH` 可替换来源） | CONFIRMED_RUNTIME + DOCUMENTED |
| 用户文件 import（quoted name） | **不可解析**。将依赖文件复制到同目录仍失败；Python client 只暴露单文档 `load`/`load_from_content`，没有多文件加载方法 | CONFIRMED_RUNTIME |
| 服务层多文档能力 | wire 层存在 `ParseSources`（`SourceDocument[]`），ServerInfo capabilities 含 `parse_sources`，Go client 暴露 `ParseFiles`；**Python client 未暴露** | CONFIRMED_SOURCE（proto + capabilities） |
| 官方定位 | Python bindings 设计文档将 "Support multi-file projects with imports" 列入 **Future Work (Post-Initial Release)** | CONFIRMED_SOURCE（docs/internals/design/python-grpc-bindings.md） |

**结论：MVP-1 File Mode（经 Python client）当前只能可靠支持 restricted single-file subset（标准库 import 允许，用户文件 import 不支持）。** 不隐藏此限制。

# Windows Issues

- 未遇到 Windows 特有故障：binary 启动、gRPC loopback、stdin-pipe 生命周期、异常翻译均正常（CONFIRMED_RUNTIME）。
- PowerShell 5.1 调用 uv 时其进度输出经 stderr 呈现（`NativeCommandError` 外观），命令本身成功 —— 只是展示噪音，非功能问题。
- 官方 latency 数据为 Linux 实测；Windows 首连接耗时未单独 benchmark（本轮非性能目标），量级约 0.1 s 内完成 load —— CONFIRMED_RUNTIME（观察值，非基准）。

# Known Limitations

1. **无用户文件 import / multi-file**：Python public API 单文档；`parse_sources` 未暴露。这是 MVP-1 最大范围约束。
2. **identity 为 name-derived FQN**：rename/move 改变 id；无跨版本稳定 identity（可选 `@ElementId` metadata 机制存在，未在本轮验证 File Mode 下的可用性）。
3. **performed action usage 无 typing facts**：public Symbol facts 中 performed usage 的类型链接为空（见 ActionUsage 节）。
4. **标准 query model 无图遍历/传递闭包**；全树遍历需 `children()` 递归（可行，已验证）。
5. **client 0.4.0 的 digest pin 表只到 v0.3.0**：自动校验下载最新只能到 v0.3.0；v0.4.3 二进制需手动放置或 `OPENSYSML_ALLOW_UNPINNED_DOWNLOAD` 显式接受（下载时 sidecar `.json` 记录 sha256）。
6. 服务缓存 LRU（100 models）：跨进程/长时间运行后旧 `model.hash` 可能被逐出（`ModelNotFoundError`）—— Adapter 应把 load 结果物化为 Snapshot，不依赖服务端缓存长期持有模型。
7. `Symbol.children` 为方法（非属性）—— 容易写错的 API 形态，contract test 应覆盖。

# Recommended Dependency Pin

```text
opensysml==0.4.0          （PyPI；已确认可解析；Apache-2.0）
sysml-grpc v0.4.3         （GitHub release Open-MBEE/OpenSysML @ tag v0.4.3，
                            asset sysml-grpc-windows-amd64.exe，
                            commit 99e02003c9c49358828b1c491a75de61745646ce，
                            sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe
                            —— 记录自本机缓存 .json 元数据）
```

备选（全自动校验下载路径）：`opensysml==0.4.0` + `sysml-grpc v0.3.0`（digest 已在 client pin 表中，`OPENSYSML_GRPC_VERSION=v0.3.0` 可自动校验下载；本机缓存另存有 v0.3.0 二进制 `sysml-grpc-f50f1b53008154c1.exe`）。本轮运行验证基于 v0.4.3，推荐主 pin v0.4.3 并把 v0.3.0 记为回退选项。

外部模型引用记录（SYSML_SOURCE_CATALOG 要求）：SysML-v2-Release `https://github.com/Systems-Modeling/SysML-v2-Release.git` @ `29a3d2acdd49600cff872e7a55962a40400f3335`（tag `2026-07`），使用文件为 training 目录下 5 个 PASS 示例（相对路径见上表）。

# Production Adapter Implications

（只描述未来 Adapter 必须遵守的边界，不写 Adapter 实现。）

1. 只依赖 `opensysml` public API（`load`/`Model`/`Symbol`/`query`/`Diagnostic`/异常层级）；禁止使用 `connection._stub`、gRPC generated types、`OBSERVED_INTERNAL` 面。
2. 单文件输入限制必须成为 Adapter 显式契约：带用户文件 import 的模型必须产生明确的 `SysMLDiagnostic`（unresolved reference），而不是静默部分导入或崩溃。
3. `Symbol.id`（FQN）作为 `SysMLElementFact.source_id`；`Symbol.kind` 作为 metatype；`Symbol.name` 作为 name；owner 从 id 前缀/树遍历得出，记录到 `owner_id`。
4. `Model.hash` + 文件路径 + OpenSysML/sysml-grpc 版本组合构成 `SysMLSource.source_version` 素材；rename ⇒ 新 identity 的语义限制要写进 Snapshot/映射文档。
5. `Diagnostic`（severity/message/start_line/start_column/…）直接翻译为 `SysMLDiagnostic`；strict load 的 `ModelError` 翻译为 `SysMLLoadError`/`SysMLParseError` 边界（本轮未实现这些 production 类，仅确认翻译素材充分）。
6. 加载成功后立即物化为 `SysMLFactSnapshot`（服务缓存 LRU，勿依赖远端缓存存活）。
7. performed action usage 在 public facts 中无 typing 链接 —— 映射阶段不得据此发明类型关系；按 facts 缺失处理或列为 UNKNOWN。

# Gate Evaluation

| Gate 项 | 判定 | 证据 |
|---|---|---|
| Windows 可重复启动 | **PASS** | v0.4.3 binary + client auto-start 两轮全新进程重复成功，无孤儿进程 |
| 合法 .sysml 可解析 | **PASS** | 自建模型 + 5/6 官方 Training Examples `ok=True`；非法模型产出精确 diagnostics |
| public API 可获得足够 Part/Action facts | **PASS** | query/traversal 得到 PartDefinition/PartUsage/ActionDefinition/ActionUsage 的 id/kind/name/owner 结构/typing facts |
| diagnostics 可处理 | **PASS** | severity/message/full locator + ModelError(partial model) |
| 不需要修改 OpenSysML source | **PASS** | 非 editable 安装后 checkout 保持 clean；全部能力来自 release 二进制 + public API |

# Final Verdict

**CONDITIONAL_GO**

Conditions（MVP-1B 之前必须书面接受，或纳入 MVP-1B Snapshot 契约）：

1. **C1 — Single-file subset**：MVP-1 第一版只支持 standalone 单文件 `.sysml`（标准库 import 允许）。用户文件 import / multi-file 模型明确排除；Adapter 对 unresolved import 必须产出显式 `SysMLDiagnostic`，不得静默降级。官方 Training Example 选择限于可单文件加载者（本轮已列出 5 个 PASS 示例）。
2. **C2 — Dependency pin**：`opensysml==0.4.0`（PyPI）+ `sysml-grpc v0.4.3` windows-amd64（SHA-256 已记录）；dependency inventory 登记 tag/commit/asset/sha256/license。服务二进制 provisioning 方式（缓存路径 or `$OPENSYSML_BINARY`）写进 Adapter 运维说明。
3. **C3 — Identity semantics 声明**：source_id = FQN、rename ⇒ 新 identity、跨版本稳定 identity 不在 MVP-1 范围 —— 必须写入 Snapshot/契约文档；禁止任何把 name 当独立稳定 ID 的实现。
4. **C4 — Performed action 限制**：performed ActionUsage 的 typing facts 在 public 表示中缺失；Mapping 阶段不得为它发明类型关系，按 UNKNOWN/缺失事实处理，并在 mapping matrix 中登记为 NEEDS_RESEARCH（不改 SYSML_TO_CANONICAL_MAPPING.md 的 TENTATIVE 状态）。

若 C1 不可接受（即 MVP-1 必须支持多文件），最小替代方向：a) 等 opensysml Python client 暴露 `parse_sources`（Future Work 已列入）；b) 改用 Go client `ParseFiles`（引入 Go 运行时）；c) 经 Repository API（MVP-1 明确 defer）。三者均超出当前 MVP-1 scope，故在 C1 成立的前提下按上述 conditions 推进。
