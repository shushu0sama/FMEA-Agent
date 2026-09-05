# Demo V1 D1 — 固定案例与演示资料包

日期：2026-09-05
Stage status: ACCEPTED（独立审核，仅 D1）
Scope: Demo V1 / D1（A01、A02），不是正式 MVP-2 或完整 Demo 验收。

## 1. 目标与依据

按已接受的 [Demo Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md) §2/§9 和
[Implementation Plan](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md) D1 固定项目自有案例，
生成可追溯、确定性的资料包。前序 [D0 记录](D0_SPEC_AND_PLAN.md) 保留原规划及独立复审证据。
用户明确授权本会话完成 D1 实现、测试、适用验证、独立审核和记录更新，不重复问卷。

## 2. 范围与实际交付

- `examples/demo_v1/system.sysml`：所选夹具逐字节副本。
- `bom.csv`：Spec 指定六列；仅列真实映射的 motor Component，quantity 空、unit=UNKNOWN。
  parent_id 指向 CSM system-1；不把系统根伪造为采购物料，不从声明数推导数量。
- `design.md`：中文“演示派生资料”，逐项列结构/动作/CSM ID/来源元素 ID；工况与参数未知。
- `manifest.json`：固定来源仓库路径/hash、文件 hash 与派生关系、现有 CSM 和来源引用、
  BOM 行定位、parser/runtime、目标与排除项。不含自身 hash，函数/CLI 返回值另含其 hash。
- `README.md`：生成、验证、文件用途、身份/换行/工程验收限制。
- `scripts/build_demo_inputs.py`：`build_demo_inputs(source: Path, destination: Path) -> dict[str, str]`；
  入口只接受 `--source/--output` 及标准 `--help`，真实复用 adapter/mapper，无自建 SysML 解析器。
- `tests/test_demo_inputs_manifest.py`：真实生成与重读、重复生成/异地输入、hash/来源/未知量、
  CLI、源覆盖保护及 partial 拒绝。

不实现 D2 的输入/证据模型及旧导出修复、D3–D7 服务/图/LLM/工作流/报告/UI。
没有新增 scenario 假设文件、失效答案、工程评分、批准状态或外部资料副本。

## 3. Git 与防漂移

- 会话开始：`codex/demo-v1-spec-plan`，HEAD `740279c04a7842ef7c7c24cb87b2a3efeb46b3ae`，工作区干净。
- 从上述 HEAD 新建单目标实施分支 `codex/demo-v1-d1-input-pack`，在现有 checkout 顺序实现；
  复用现有 `.venv`，未从旧 master 创建分支，未额外创建 worktree。
- 实现过程中观察到 HEAD 新增 `9d5c0a7a9d6c67db799bb5b5ba4b8445c4b67534`
  （`docs: clarify Demo steps versus formal MVP milestones`）。此提交不是本实现 Agent 创建。
  已读取其完整差异：仅澄清 Demo 与正式 MVP 的对应/验收关系，不改变 D1。
  保留全部更新，收尾以此最新记录为依据；原 `740279c` 仍在祖先链中。
- D1 实现提交与审核基线：`d1868a12d6b774da83bd5e7b712bb8a6c3e189cd`
  （`feat: build traceable fixed SysML demo input pack`），12 个变更文件。
  实现验证后提交，状态 READY_FOR_REVIEW；独立审核通过后本次仅更新状态与证据。
- 分支已成功推送 `origin/codex/demo-v1-d1-input-pack`；审核后实查本地 HEAD 与 upstream
  均为 `d1868a1`，工作区干净。包含本节的后续文档收尾提交沿同一分支保存，具体 SHA 以 Git 历史为准。
- 不合并到 master，不创建或移动发布 tag；D2 尚未实现。

范围漂移：NO。新增 `.gitattributes` 是固定 A01 字节来源的必要支撑，未扩展功能阶段。
基线发生上述文档前移，明确记录，不把它写成 D1 自身实现。

## 4. 来源与复用决策

固定来源：`tests/fixtures/sysml/models/typed_inside_probe.sysml`，项目自有教学夹具。
来源文件最近修改提交：`657a892bb42ca15c1728ebe8aa8e6ea5e8bde97a`（Git 实查）。
D0 与 D1 实际读取文件的 SHA-256 均为：

```text
fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5
```

实查 `git ls-files --eol` 原为 `i/lf w/crlf`，`core.autocrlf=true`。
因此 D0 的 hash 指向 checkout CRLF 字节，不是仓库 LF blob。新增限定属性：
原夹具 `text eol=crlf`；包内模型 `-text` 原字节；其他包文本 `text eol=lf`。
包内模型另设 `whitespace=cr-at-eol`，让 Git 正确认识已固定的 CRLF，不把 CR 误报为尾随空白。
原夹具内容及其 Git blob 未改，既有官方 B1 夹具和许可原文不受影响。
Git archive 等未经 checkout 换行处理的 LF 输入会被拒绝，不能静默改 hash 或归一化后冒充原文件。

复用分类：

| 能力 | 分类 | 实际采用 |
|---|---|---|
| SysML 读取 | D | 现有 OpenSysMLFileAdapter；opensysml 0.4.0 / sysml-grpc v0.4.3 |
| CSM | D | 现有 CanonicalSystemMapper 与 CanonicalSystemModel，接口/生产代码不改 |
| CSV/JSON/hash/CLI | D | Python stdlib csv/json/hashlib/argparse/pathlib |
| 固定案例派生规则 | S | D1 脚本内的范围声明、未知量、来源清单与中文模板 |

已检索既有代码、契约、mapper 来源引用规则和 benchmark；复用既有公开接口并真实执行，
未新增外部基础设施，不需要新增依赖/上游 API 设计。依赖版本和许可证基线保持不变。

manifest 的 source.path 是已固定的仓库来源，允许内容相同的异地副本作为实际读取输入。
导出 CSM 引用 source_uri 用包内 `system.sysml`；保留 source_element_id 与其他 CSM 字段/通知。
文件内容 hash 与源元素 ID 联用；Model.hash 仍仅是 load-context fingerprint，
路径相关值不写入确定性资料包。原始 adapter 快照语义不改，不承诺跨版本身份。

## 5. LOCAL — 实际解析与验证

环境：Windows，既有项目 `.venv`。真实 adapter 生成与重读副本均为 load_status=ok、0 diagnostics；
parser=opensysml 0.4.0，runtime=v0.4.3。

| 类型 | ID | 名称 | 归属 | source_element_id |
|---|---|---|---|---|
| System | system-1 | hydraulicPump | — | TypedInsideProbe::hydraulicPump |
| Component | component-1 | motor | system-1 | TypedInsideProbe::hydraulicPump::motor |
| Function | function-1 | pumpSpin | system-1 | TypedInsideProbe::hydraulicPump::pumpSpin |
| Function | function-2 | spin | component-1 | TypedInsideProbe::hydraulicPump::motor::spin |

首个目标 component-1/function-2；function-1 在 CSM 中完整保留，manifest/design 明确排除。
原始映射还保留 4 条 notices（package、Pump/Motor/Spin 类型定义）；不伪造 Component 类型。

已运行：

```text
基线 scripts/verify.py：223 passed in 12.45s；Ruff PASS；mypy src PASS（24 files）。
D1 目标测试：10 passed in 1.44s。
最终 scripts/verify.py：233 passed in 13.62s；Ruff PASS；mypy src PASS（24 files）。
扩展 mypy src scripts/build_demo_inputs.py：PASS（25 source files）。
uv lock --check --offline：PASS（73 packages）。
git diff --check：PASS。
checkout-index（core.autocrlf=false）：原夹具 + 5 个包文件均与本次字节完全相同。
Markdown：6 份文档围栏配对、38 个本地链接目标通过；中文主体与术语人工检查通过。
```

生成命令实际执行：

```bash
python scripts/build_demo_inputs.py --source tests/fixtures/sysml/models/typed_inside_probe.sysml --output examples/demo_v1
```

完整 suite 包含原 B0/B1 的 11 个 benchmark 测试、MVP-0/1 回归及 no-new-orphan regression；
基准数据/gold/指标算法未变，不以派生资料对自身做工程准确率验证。
CI = NOT_CONFIGURED；DeepSeek/Neo4j live = NOT_RUN（D1 不涉及）；UI = NOT_IMPLEMENTED。

## 6. 开发中发现与修正

- 按 Plan 先写测试，缺少生成器时 8 项失败；首次硬链接测试还暴露 C:/D: 跨卷不支持。
  改为在同一个临时卷复制输入后建硬链接，重跑仍为 8 项缺少实现导致失败，再实现生成器。
  该 RED→GREEN 为本机执行证据，未独立保存为 RED Git commit。
- 8 项初始测试通过后补充异地输入与 partial 拒绝测试，最终 10 项。
- Ruff 报告 3 处超长行，限定在新增脚本修正；没有全库格式化。
- 单独 mypy 脚本时把 editable package 视为无 py.typed 的安装包，改为同 `src` 一起检查；
  随后发现混合 CSM 列表推断为 BaseModel，增加 `System | Component | Function` 明确注解。
  扩展检查通过，不改已有 domain 类型或工具配置来隐藏问题。

## 7. EXTERNAL_REVIEW

独立 reviewer：`/root/d1_independent_review`。未继承实现会话推理历史，按明确的 Spec/Plan/Git
范围独立只读审核；未修改工作树、index、HEAD、分支或文档。

审核范围：`9d5c0a7a9d6c67db799bb5b5ba4b8445c4b67534` →
`d1868a12d6b774da83bd5e7b712bb8a6c3e189cd`，12 个变更文件。
决定：**ACCEPTED**；CRITICAL=0 / IMPORTANT=0 / MINOR=0，无待修复发现。

EXTERNAL_REVIEW 本机实际证据：

- pytest：233 passed in 13.09s；Ruff `--no-cache` PASS；mypy src + 新脚本 25 files PASS；
  range `git diff --check` PASS。
- `core.autocrlf=false/true/input` 三种设置，每种原夹具与五个包工件 checkout 全部逐字一致。
- 修改源、LF 源、源路径/父目录覆盖、五个输出位置分别硬链接至源、warning 诊断均拒绝，
  原文件与已有资料包保持不变。
- 真实 adapter/mapper 重读 hydraulicPump → motor/spin，0 diagnostics；pumpSpin 保留并明确排除。
  临时目录重新生成与提交工件逐字一致；数量/工况保持未知，hash/CSM/source IDs 可追溯。
- 既有 src/依赖/原夹具/benchmark/gold 无变化；全套包含已有回归。

此决定只接受 Demo V1 / D1 的 A01/A02 实现，不扩展为完整 Demo、正式 MVP-2/3 或工程质量验收。
未测试跨操作系统、并发写入或崩溃原子性；未调用 DeepSeek/Neo4j 或运行 UI。
本次后续收尾只更新治理记录/状态，不修改被审实现与资料包，不将独立审核重复计作 CI。

## 8. 限制与下一步

- 只处理一个已固定 hash 的教学案例，非通用导入器。新模型须单独选择/审查，不放宽 D1 hash gate。
- 文件正常重复生成会覆盖五个指定工件；源重叠（含硬链接）拒绝，未设计并发写入/崩溃原子事务。
  一个 checkout/输出目录保持单写入者；I/O 中断后应重新生成并验证。
- 同源 BOM/说明只用于演示资料准备；无独立工程审核或失效分析质量验收。
- 包是输入资料，不是 CandidateReport；报告/输入契约及来源导出修复属于 D2 以后。
- 下一项建议任务：D1 已独立审核通过，在新主会话按既有 Plan 开始 D2。
