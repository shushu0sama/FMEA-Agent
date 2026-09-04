# MVP-1C DEPENDENCY REPRODUCTION REPORT

> 1C-0 Dependency Reproduction Gate — 2026-09-04
> 目标：证明 PyPI `opensysml==0.4.0` 的 MVP-1C 所需 API 与 runtime 行为与 MVP-1A Spike（checkout 安装）逐项一致，允许进入 Adapter implementation。
> 证据等级沿用 Spike 报告约定：`CONFIRMED_RUNTIME`（本机实际执行）/ `CONFIRMED_SOURCE`（官方 source 明确支持）/ `DOCUMENTED`。

## 结论（先行）

**PYPI_PIN_CONFIRMED**

PyPI `opensysml==0.4.0` 与 MVP-1A checkout（commit `ef03da889285a9a5c71bcec9dd7b67b8b3e1a599`）安装的 client 在全部 13 项 MVP-1C probe 上行为一致；PyPI wheel 内容与 checkout client source 内容等价（0 个真实差异）。允许进入 1C Adapter implementation。

附带一项必须在 1C Adapter Profile 记录的语义修正：**`Model.hash` 不是纯内容哈希**（见 F1）。

## Tested Source

| 项 | 值 | 证据 |
|---|---|---|
| 包 | `opensysml==0.4.0`，**PyPI 官方 wheel** | CONFIRMED_RUNTIME |
| wheel 文件名 | `opensysml-0.4.0-py3-none-any.whl` | CONFIRMED_RUNTIME |
| wheel SHA-256 | `d3a9cfea481818656ec2f30f432c85ac74c41ab22adb51c5d9095c7cc1da3fca`（与 PyPI JSON API `digests.sha256` 一致） | CONFIRMED_RUNTIME |
| 下载 URL | `https://files.pythonhosted.org/packages/57/75/5291a2faa445148c7e0eb43839c5e1629521f76f087aace02e95d5b489cb/opensysml-0.4.0-py3-none-any.whl`（uv 缓存 `.http` 元数据记录） | CONFIRMED_RUNTIME |
| 安装后 `opensysml.__version__` | `0.4.0` | CONFIRMED_RUNTIME |
| Requires-Python | `>=3.10` | CONFIRMED_SOURCE（wheel METADATA） |
| License | Apache-2.0（`License-Expression: Apache-2.0`） | CONFIRMED_SOURCE |
| 依赖集合 | 34 包；grpcio 1.83.1 / protobuf 7.36.1（与 Spike 记录一致） | CONFIRMED_RUNTIME |
| 安装方式 | `uv pip install opensysml==0.4.0`（`INSTALLER: uv`；无 `direct_url.json` = 普通 index 安装） | CONFIRMED_RUNTIME |

实验目录（throwaway，位于本地研究 workspace）：

```text
D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace\99_experiments\opensysml_pypi_040_reproduction
```

参考环境（与 MVP-1A Spike 一致）：

| 项 | 值 |
|---|---|
| OS | Microsoft Windows NT 10.0.26200.0（Windows 11 Pro），AMD64 |
| Python | CPython 3.13.9（独立 venv，与 FMEA production 环境隔离） |
| uv | 0.11.7 |
| 夹具 | 复用 MVP-1A Spike 的 6 个 probe 脚本与全部 `.sysml` 夹具（逐字节复制；文件 SHA-256 与 spike 原件一致） |
| 新增 probe | 显式 connect/close + 孤儿检查、C1 unresolved-import 夹具、包内容对比脚本 |
| 原始输出 | 全部留存于实验目录 `output/`（local evidence，不入库） |

## Runtime（sysml-grpc）

| 项 | 值 | 证据 |
|---|---|---|
| 实际运行版本 | **v0.4.3** | CONFIRMED_RUNTIME（`sysml-grpc --version`） |
| commit | `99e02003c9c49358828b1c491a75de61745646ce` | CONFIRMED_RUNTIME |
| 来源 | 本机缓存 `~/.opensysml/bin/sysml-grpc.exe`（digest-link `sysml-grpc-0b188ec140872c0f.exe`），sidecar `.json` 记录 `version v0.4.3` / `sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe` / repo `Open-MBEE/OpenSysML` | CONFIRMED_RUNTIME |
| discovery | PyPI client 与 Spike 一致：命中缓存 digest-link，`ServerInfo.origin = '…\sysml-grpc-0b188ec140872c0f.exe, started by this client'`；未设置 `OPENSYSML_BINARY` / `OPENSYSML_GRPC_VERSION` | CONFIRMED_RUNTIME |
| capabilities | 17 项（`parse_sources` / `query` / `type_facts` / `strict_conformance` / …），与 Spike 报告一致 | CONFIRMED_RUNTIME |

## Compatibility Matrix

逐项：checkout 结果（MVP-1A Spike 报告证据）vs PyPI 结果（本轮实测）。

| # | Probe | Checkout 结果（Spike） | PyPI 0.4.0 结果（本轮） | 判定 |
|---|---|---|---|---|
| 1 | import / version | `opensysml.__version__` = 0.4.0 | 0.4.0 | **MATCH** |
| 2 | sysml-grpc discovery/start | 缓存 v0.4.3 digest-link，client 自动启动 | 相同（origin 字符串一致） | **MATCH** |
| 3 | connect / `server_info()` | `ServerInfo(version='v0.4.3', capabilities={…17 项…})` | 相同，`answered=True` | **MATCH** |
| 4 | minimal valid model load | ok=True，0 diagnostics，0.09–0.12 s | ok=True，0 diagnostics，0.085–0.086 s | **MATCH** |
| 5 | invalid model diagnostics | 2 条 error：`expected '{' or ';' after declaration` / `expected '}'`，带 file:line:col；strict 抛 `ModelError`（`.diagnostics`+`.model`） | 逐字相同（消息、位置、ModelError 形态） | **MATCH** |
| 6 | `Symbol.children()` | 方法（非属性），完整符号树遍历 | 相同；树结构与 Spike 报告逐字节一致 | **MATCH** |
| 7 | PartDefinition / PartUsage | query 命中 `PerformProbe::Pump`/`Motor`、`hydraulicPump`/`hydraulicPump::motor` | 相同 | **MATCH** |
| 8 | ActionDefinition / ActionUsage | 命中 `Spin`、顶层 `spin`、performed `hydraulicPump::motor::spin` | 相同 | **MATCH** |
| 9 | `Symbol.id` / `kind` / `name` | FQN id（`PerformProbe::…`）、小驼峰 kind、短名 name | 相同（两次独立进程输出逐字节一致） | **MATCH** |
| 10 | `type_facts` | partUsage→partDef 链接可获取；**performed usage 空**（C4） | 相同：`TypeFacts(declared='Pump', resolved_id='PerformProbe::Pump', resolved_kind='partDef')` 等；performed `motor::spin` 三项全空 | **MATCH** |
| 11 | `specializations` / typing | `Specialization(kind='typing', target_id, target_kind)` | 相同（hydraulicPump→Pump、motor→Motor、顶层 spin→Spin；performed 无） | **MATCH** |
| 12 | `Model.hash` | 同路径跨进程一致 | 同路径+同内容下 **checkout client 与 PyPI client 产出相同值**（`9bedeff4…`）；语义澄清见 F1 | **MATCH**（附语义注记） |
| 13 | connection close / no orphan | 运行后无孤儿进程 | 通配符 `sysml-grpc*` 检查：连接打开时 1 个进程，close 后 0；全流程结束后 0 | **MATCH**（检查更强，见 F3） |

补充验证（非 13 项之外，1C 将直接使用）：

- `Model.find`/`Model.get`/`Model[name]`：短名/FQN 查找、未命中返回 None —— 与 Spike 一致。
- `QueryElement(id, type, properties, as_dict())`：形态一致。
- Diagnostic 完整 locator：`severity/message/file/start_line/start_column/end_line/end_column/span` 全部可用。
- C1 夹具（`Action Performance Example.sysml`，用户文件 import）：4 条 error（`unresolved reference: Action Decomposition` + 级联 takePicture/focus/shoot），与 Spike 记录一致；strict 抛 `ModelError` 且携带 partial model。

## Differences / Findings

**F1（必须进入 1C Adapter Profile）— `Model.hash` 不是纯内容哈希，而是 load context 下的 fingerprint。**

- 实测：字节完全相同的文件（SHA-256 一致），以不同路径字符串加载 → 不同 hash（`9bedeff4…` vs `b1f6264c…`；改名副本 → `5ff73545…`）；同一路径字符串 + 同内容 → 跨进程、跨 client 稳定。
- 源码确证（CONFIRMED_SOURCE）：服务端 `internal/core/libs/loader.go` `setDigest`/`digestOf` —— `SHA256(name₁ \0 sha256(content₁) \0 name₂ \0 …)`，按 name 排序。**hash 覆盖 model/file name/path context 与 per-file content hash**。
- Spike 报告"内容哈希"表述不精确（其跨进程一致性测试只用了同一路径字符串，故未暴露）。

`model_hash` 正式语义（1C 及后续必须遵守）：

```text
model_hash = OpenSysML 当前模型 load context 下的 fingerprint。

它：
- 不是 Canonical ID；
- 不是跨路径稳定 identity（路径字符串变化 ⇒ hash 变化）；
- 不是跨机器永久稳定 identity（跨机器/环境稳定性未验证、不作承诺）；
- 不得用于判断工程实体跨版本 identity。
```

1C 要求：

- adapter 必须定义 **documented deterministic path normalization / load policy**（例如固定 resolve 策略 + 统一路径形式），以提高同一 reference environment 内的可重复性；
- **禁止为了得到所谓"稳定 hash"自行重新实现 hash 算法**——`model_hash` 一律取 OpenSysML 返回值原样记录；
- `model_hash` 只标识"该次加载的 name+content fingerprint"，不承担跨版本 identity（与 1B 契约语义一致）。

**F2 — Spike 归档 run1/run2 的 hash（`e38d22b6…`）与本轮值不同，原因已查明：夹具文件在 Spike 期间被迭代编辑，非 client 差异。**

- 决定性证据：spike venv（checkout client，0.4.0）**现在**加载同路径同文件也得 `9bedeff4…`，与 PyPI client 完全一致；且与 Spike 归档 run1 逐字节 diff 仅 hash 行不同、元素树逐字节相同。
- 结论：checkout client 与 PyPI client 在 hash 行为上无差异。

**F3 — 孤儿进程检查方法学修正。**

- `Get-Process sysml-grpc`（精确名）匹配不到 digest-link 进程名 `sysml-grpc-0b188ec140872c0f`；Spike 的 0 计数检查可能低估了存活进程。
- 本轮改用通配符 `sysml-grpc*`：连接打开时 1 个进程、close 后 0、全流程结束后 0 —— 无孤儿进程的结论在更强检查下成立。

**F4 — PyPI wheel 与 checkout client source 内容等价。**

- 28/28 文件同数、无缺失/多余；2 个文件字节相同；26 个文件仅行尾差异（wheel 内 LF vs checkout 工作树 CRLF，git autocrlf 效应）；**0 个真实内容差异**；`release-digests.json` 相同（只含 `Open-MBEE/OpenSysML` 表，仍只 pin 到 v0.3.0）。
- uv 缓存中 checkout 构建的 wheel（`f9197104…`）与 PyPI wheel（`d3a9cfea…`）是不同的打包产物，但内容等价。

**F5 — 依赖集合一致**：34 包、grpcio 1.83.1、protobuf 7.36.1，与 Spike 记录相同。

## Known Limitations

1. 结论证据基于 Windows 11 AMD64 reference environment（与 Spike 相同）；跨平台未验证，不作承诺。
2. runtime 为本地缓存中的 sysml-grpc v0.4.3 二进制；自动校验下载路径（client digest 表只 pin 到 v0.3.0）未在本 gate 重新触发。v0.4.3 的 provisioning 方式（缓存路径 or `$OPENSYSML_BINARY` / `OPENSYSML_ALLOW_UNPINNED_DOWNLOAD`）需写进 1C Adapter 运维说明（C2）。
3. F1 的 hash 语义验证覆盖单文件 load；多文件/其他 load 形式不在 MVP-1 范围（C1）。
4. 本轮未把 `opensysml==0.4.0` 写入 production dependency（pyproject.toml 未改）；正式 pin 在 1C Adapter 实现时随 Dependency Inventory 登记落地。

## Production Pin Recommendation

**PYPI_PIN_CONFIRMED**

```text
opensysml==0.4.0          （PyPI wheel，sha256 d3a9cfea481818656ec2f30f432c85ac74c41ab22adb51c5d9095c7cc1da3fca，Apache-2.0）
sysml-grpc v0.4.3         （GitHub release Open-MBEE/OpenSysML @ tag v0.4.3，
                            asset sysml-grpc-windows-amd64.exe，
                            commit 99e02003c9c49358828b1c491a75de61745646ce，
                            sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe）
```

理由：

1. 13 项 MVP-1C probe 全部 MATCH；checkout 与 PyPI client 内容等价（F4）——MVP-1A 的全部 runtime 证据可转移到 PyPI pin。
2. 无需 `CHECKOUT_COMMIT_PIN_REQUIRED`（checkout 安装要求依赖 git clone + 本地构建，与 production dependency hygiene 不符，且本轮证明其行为与 PyPI 无差异）。
3. 无阻塞项，不进 `DEPENDENCY_PIN_BLOCKED`。

进入 Adapter implementation 前的记录义务：

- 1C Adapter Profile / 契约文档登记 F1（`Model.hash` = name+content digest；规范化加载路径策略）；
- Dependency Inventory 登记上表（tag/commit/asset/sha256/license，C2）；
- 保留 Spike 报告的 v0.3.0 回退选项（digest 已在 client pin 表内）。
