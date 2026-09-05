# Demo V1 D2 — 输入/证据契约与旧导出修复

日期：2026-09-05
Stage status: ACCEPTED（仅 D2 独立技术审核）
Closeout status: PENDING_PUSH（本地提交已保存；远端推送失败，未声明正式 COMPLETE）
Scope: Demo V1 / D2（A03、A08、A09 的基础），不是完整 Demo 或正式 MVP-2/3 验收。

## 1. 目标与依据

用户在 D1 完成后同意开始下一步。本轮按已接受的
[Demo Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Implementation Plan](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md) D2 和
[D1 记录](D1_FIXED_CASE_AND_INPUT_PACK.md) 执行，未重做需求问卷。
同时复核 AGENTS/PROGRESS/导航、治理规则、FMEA profile/术语以及现有领域、端口、adapter 和 workflow。

## 2. 范围与实际交付

- `domain/demo_evidence.py`：EvidenceRef/FieldValue/InputFileRecord/LoadedInputs，禁止额外字段、
  约束字段状态，校验 file/evidence ID、来源链、CSM 文件引用、缺失项及输入清单摘要。
- `domain/demo_knowledge.py`：KnowledgeQuery/Hit/RetrievalResult，限制查询词、返回量、scope，
  区分 HITS/NO_MATCH/ERROR；仅契约，没有数据库查询实现。
- `domain/demo_analysis.py`：IntakeResult/FailureRow/GenerationResult/CandidateReport/DiagnosticReport。
  成功报告携带完整 LoadedInputs，三层影响均存在，引用可定位；CANDIDATE/NOT_EVALUATED/SKIPPED 固定。
  失败诊断携带输入快照及非空错误列表。未实现 D6 导出器。
- `application/demo_ports.py`：提供方中立 SourceKnowledgeRepository/DemoLLMClient Protocol。
- `application/demo_intake.py`：只实现确定性的目标/引用/冲突检查；合法的未完整目标保留 WAITING_INPUT，
  不存在目标或结构冲突返回 BLOCKED。自然语言解析与工况事实提取留到 D4。
- `adapters/documents/demo_inputs.py` + `_demo_extract.py`：只读文件载入及有界文本/表格提取。
  复用现有 SysML adapter/mapper，MD/TXT 逐行、PDF 逐页、CSV/XLSX BOM 逐记录保留来源。
- `agents/workflow.py`：原结果增加 `item_id/function_id/source_refs`，保留原键；
  用既有 candidate.model_dump 保留关联、description、cause mechanism/evidence、effect status/evidence/affected_item_id。
  没有为 FailureModeCandidate 新增自身 id，没有改变七步状态转换。
- 3 个 D2 测试文件 + 既有 CLI 断言更新；README、Spec 细化、依赖清单、Plan、导航与 PROGRESS。

D1 工件/原夹具/benchmark gold 不变；D3–D7 图/LLM/新工作流/报告/UI 均未实现。

## 3. Git 与范围纪律

- 开始：`codex/demo-v1-d1-input-pack`，HEAD `35aa0666e0c687c19a76a985b0756f6120bee410`，工作区干净。
- 从该 HEAD 创建 `codex/demo-v1-d2-input-contracts`，复用当前 checkout/`.venv`。
  已确认包含原规划 `740279c`、路线澄清 `9d5c0a7` 与全部 D1 实现/收尾提交。
- 本阶段没有观察到其他并行提交/修改；范围限定 D2，不从旧 master 漏掉交接。
- 首次送审实现提交：`bdbdedea03429ff1aeeacbfca229a2a408b3a5f4`。
  当前远端推送因 GitHub TLS 握手/连接超时未成功；没有禁用证书验证或修改永久 Git 配置。
  修复提交：`dde80fda741602483e7f4a34e8572fa9d5af4841`，独立复审基线。
  后续治理提交只回填复审与保存状态，不改被审代码。
- 多次标准 push 与一次仅命令级 schannel/HTTP 1.1 尝试均失败；GitHub HTTPS HEAD 探测也超时。
  最后标准推送仍返回 `TLS connect error: unexpected eof while reading`。
  按治理 §3.2 `Push complete` 条件，远端收尾保持 PENDING_PUSH；技术审核通过不代替远端保存。
- 不合并到 master，不创建或移动发布 tag。

范围变化：没有进入其他 D 阶段。Spec §3.1 本轮记录以下实施细化，随本次独立审查：
总提取字符按一次输入累计；XLSX ZIP 目录声明的展开总大小限制 25 MiB；CSV 行为逻辑记录序号；
仅读取 BOM 表，宏类型文件改名也拒绝。这些是资源/定位规则，不扩展工程能力或替换已接受架构。

## 4. 复用与依赖

| 能力 | 分类 | 实际采用与边界 |
|---|---|---|
| SysML/CSM | D | 现有 OpenSysMLFileAdapter/CanonicalSystemMapper；不扩展解析器 |
| 模型校验 | D/S | 已有 Pydantic + 项目证据/状态规则；Demo 边界拒绝旧 CSM 会忽略的额外字段 |
| 来源链检查 | D | stdlib graphlib.TopologicalSorter 检测 derived_from 循环 |
| PDF | W | pypdf==6.17.0；PdfReader/逐页 extract_text；无 OCR/布局推断 |
| BOM XLSX | W | openpyxl==3.1.5；read_only=True/data_only=False/keep_links=False，显式 close |
| CSV/hash/文件与 ZIP | D | stdlib csv/hashlib/pathlib/zipfile；不自建 Office/PDF 解析器 |

执行 `uv add --optional demo pypdf==6.17.0 openpyxl==3.1.5`、`uv sync --extra demo`。
仅新增上述两包及传递依赖 et-xmlfile==2.0.0；对比前后 lock，全部既有包版本相同。
安装时 uv 因 C:/D: 跨卷硬链接失败自动改为复制，安装成功，没有降低验证要求。
实际许可证元数据和文件位置已登记到[依赖清单](../../research/DEPENDENCY_INVENTORY.md)。

公开 API 核对：
[pypdf extract_text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、
[加密检测](https://pypdf.readthedocs.io/en/stable/user/encryption-decryption.html)、
[openpyxl 只读模式](https://openpyxl.readthedocs.io/en/stable/optimized.html)与
[load_workbook](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html)。
openpyxl stable 文档标题为 3.1.3，实际安装/测试 3.1.5；重设 worksheet dimensions 后读取，
负例证明错误的 dimension 声明不能隐藏公式。没有复制第三方工程数据或修改许可原文。

## 5. 输入、来源与冲突的实际边界

- 只接受调用者明确给出的本地文件；不读取 sidecar manifest、外部链接、宏、公式或文中指令。
  Path 是本地服务调用参数；禁止 `..` 路径分量，导出 filename 只保留 basename。
  D6 仍须使用服务端生成的上传路径；本 loader 没有写文件副作用。
- 每文件 5 MiB；总提取文本 30,000 字符（SysML 原文、设计文本和 BOM 内容合计）；PDF 20 页；BOM 200 行。
  XLSX 解压前增加目录声明的总展开 25 MiB 保护，不声明进程级内存/时间沙箱。
- 首次独立审核发现稀疏坐标绕过非空行数量限制后，增加 BOM 物理扫描预算：10,000 行、64 列。
  空行也计入扫描，不以 `iter_rows(max_row/max_col)` 静默截断；正常稀疏行保留物理 locator。
  复用 openpyxl 公开迭代接口，无自建 XLSX 解析器或私有 API。列限制在 openpyxl 产出一行时检查，
  不宣称在单行解析前隔离内存；固定依赖对更长的非法列名称抛出错误，由适配器封装。
- 文件 ID 是输入内的角色标识 `file-sysml/file-document/file-bom`；与文件 SHA-256 联用。
  `input_digest` 为按 SysML/设计/BOM 顺序的完整 InputFileRecord JSON 摘要（排序 key、紧凑 UTF-8），
  包括 basename 和 parser/runtime；改名会改变清单摘要，内容 SHA-256 不变，不包含本地绝对路径。
- CSM source_uri 替换为对应文件 ID，source_element_id 原样保留；保存一份 SysML 原文及元素定位。
  Model.hash 仍只表示 load-context fingerprint，没有将其变成跨路径身份。
- `EvidenceRef.derived_from` 记录本次提取来源文件/证据；不根据相似文件名臆断文档作者或派生关系。
  不自动读取 D1 sidecar；D1 设计原文中的同源声明完整保留，原 manifest 仍是 D1 固定来源的权威记录。
- BOM source_element_id 必须指向现有 CSM Component；item_id 保留外部 BOM 原值。
  parent_id 可指向 BOM item 或 CSM system/component；无法定位时报错，已知对象的名称/父级不一致保存 conflict。
  模型事实不被 BOM 覆盖；候选成功报告与 intake 不能绕过未解决 conflict。
- MD/TXT 保留非空行原文（空行只影响行号）；PDF 保留每页提取文本；CSV/XLSX 用 JSON 保留六个原始字段值。
  数量未填继续空值，不从部件声明数计算；XLSX 普通数值单元格转成文本，formula 类型及公式前缀拒绝。

## 6. LOCAL 验证与开发发现

基线：233 passed in 13.22s；Ruff PASS；mypy src PASS（24 files）。
首次送审验证：`scripts/verify.py` → **325 passed in 17.88s**；Ruff PASS；mypy src PASS（32 files）。
首次送审新增 92 项 = 47 契约/目标测试 + 44 文件契约测试 + 1 原图导出回归。
原 B0/B1、D1 字节固定、CLI 与 orphan 回归包含在全套；benchmark/gold/度量未修改，无已观察退化。
`uv lock --check --offline` PASS（76 packages）；`git diff --check` PASS。

实际 RED→GREEN：

1. 39 契约测试先因模块缺失失败；实现后通过。
2. 37 文件测试先因适配器缺失失败；真实 PDF/XLSX/CSV/SysML 实现后通过。
3. 原图来源回归先因 `item_id` 缺失失败；补齐完整导出后通过。
4. 补充嵌套 CSM 额外字段、循环来源链、缺少必需 SysML 负例，复现 4 项失败后修复。
5. CSV 含跨行字段时定位误用结束物理行，负例失败后修复为逻辑记录序号。
6. 全套第一次 318 passed/1 failed：旧 CLI 断言要求 effect 只有原两键。保留原值并明确增加
   status/affected_item_id/evidence 期望，未删掉断言来掩盖回归。
7. 补问边界补测发现已选合法组件或功能的部分目标误被 BLOCKED，修复后保留 WAITING_INPUT；
   不存在的部分目标仍 BLOCKED。后续全套通过。

上述 RED 为本机执行证据，未独立保存 RED Git commit。
Ruff/mypy 初次指出长行/导入及局部变量类型复用，限定新增文件修复，不改全库格式或屏蔽检查。

其他 LOCAL 证据：使用进程导入拦截模拟 pypdf/openpyxl 不可用时，SysML/MD/CSV 载入与原 CLI 成功。
这证明可选依赖导入边界，不冒称重新创建了一个完全未安装 extra 的环境。
真实服务状态：DeepSeek/Neo4j = NOT_RUN；UI = NOT_IMPLEMENTED；CI = NOT_CONFIGURED。

## 7. EXTERNAL_REVIEW

首次独立 reviewer：`/root/d2_independent_review`；范围 `35aa066` → `bdbdede`。
决定 **CHANGES_REQUIRED**；CRITICAL=0 / IMPORTANT=1 / MINOR=1。

- IMPORTANT：约 4,966 bytes 的 XLSX 使用第 1,000,000,000 行，openpyxl 补空行导致公共载入入口
  在独立子进程 3 秒超时；200 非空行和 ZIP 展开大小限制均不能防止该问题。
- MINOR：ZIP 预检查未封装加密条目的 RuntimeError，调用者无法按 DemoInputError 分类。
- EXTERNAL_REVIEW：325 passed in 18.02s、Ruff PASS、mypy 32 files PASS、uv lock 76 packages PASS、
  diff PASS；真实包 CandidateReport JSON 往返保留 39 条证据，可选依赖延迟导入通过。
  审核没有修改工作树、index 或 Git；未发现其他阻塞问题。

修复过程：新增 9 项回归，首次 7 failed / 2 passed；巨大行号在测试子进程 5 秒超时，
未知压缩方法和损坏压缩数据也复现底层异常外泄。增加扫描预算及 ZIP 安全异常边界后，
文件契约测试 **53 passed in 6.09s**。另覆盖第 10,000 行成功、第 10,001 行拒绝、
超宽/非法列名拒绝、加密条目返回 ENCRYPTED。修复后重新送独立复审，不沿用首次全套通过作为验收。

修复后 LOCAL 全套：`scripts/verify.py` → **334 passed in 18.87s**，Ruff PASS、mypy 32 files PASS；
新增共 101 项（47 契约/目标 + 53 文件 + 1 旧导出）。`uv lock --check --offline` 与 `git diff --check` PASS。

最终独立复审：同一 reviewer，基线 `dde80fda741602483e7f4a34e8572fa9d5af4841`；
总范围 `35aa066` → `dde80fd`，重点 `bdbdede` → `dde80fd`。
决定 **ACCEPTED（仅 D2 技术范围）**；未解决 CRITICAL=0 / IMPORTANT=0 / MINOR=0，首次两项均关闭。

EXTERNAL_REVIEW 复审证据：

- 全套 **334 passed in 20.14s**，包含 B0/B1、CLI、SysML、D1、orphan 和新增负例。
- Ruff `--no-cache` PASS；mypy src PASS（32 files，临时缓存）；uv lock 76 packages PASS；总范围 diff PASS。
- 独立公共入口：第 10,000 行成功且物理定位不变；第 10,001 / 1,000,000,000 行返回 LIMIT_EXCEEDED，
  分别约 2.60 / 2.61 秒。第 64 列空白允许，BM/ZZZ 超限、AAAA 非法列安全拒绝。
- 原 ZIP 加密标志负例改为 ENCRYPTED；未知压缩方法和损坏压缩数据安全拒绝。
- 审核前后 branch/HEAD/index 一致、工作区干净，reviewer 未修改仓库；来源往返、旧导出和领域边界结论仍适用。

收尾 LOCAL 文档/范围检查：7 份 Markdown 围栏和 55 条本地链接通过；
原规划 `740279c` 与 D1 收尾 `35aa066` 均为祖先；D1 工件/夹具/benchmark 未改变。
本次治理回填没有扩大技术验收至 D3–D7、真实服务、UI、工程正确率或远端保存。

## 8. 已知限制与下一步

- 结构性引用校验只证明引用存在，不证明原文支持工程结论；source 文件 hash 也不是真实性认证。
- 设计说明仅逐行/逐页保留，尚未自动做自然语言事实/冲突判断；没有把文档文本标为已确认模型事实。
- PDF 不做 OCR，空页/无文本页拒绝；不是页面布局还原。BOM 仅读 BOM 表，额外 worksheet 不参与分析。
- loader 不解决并发修改/解析器进程资源隔离；SysML 读取前后变化会拒绝，不声明对抗性原子快照。
- Pydantic 数据仍可被 Python 调用方修改；对外接入/导出须使用正常验证入口，不使用 model_construct
  或未验证 model_copy 晋升数据。D4 的生成语义/原文支持校验与 D6 导出尚未实现。
- 旧 JSON 来源缺失问题按 D2 清单补齐，但旧 CLI 不等于自包含的 CandidateReport。
- 下一步先在网络恢复后推送 `codex/demo-v1-d2-input-contracts` 并更新保存状态；随后在新主会话
  按 Plan 进入 D3 可独立验证的只读 Neo4j 检索，不重复 D2 实现或需求问卷。
