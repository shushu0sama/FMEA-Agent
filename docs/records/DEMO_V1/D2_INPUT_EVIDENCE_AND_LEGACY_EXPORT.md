# Demo V1 D2 — 输入/证据契约与旧导出修复

日期：2026-09-05
Stage status: READY_FOR_REVIEW
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
- 实现验证与此送审记录一起提交；具体实现 SHA、推送和独立决定于后续收尾补记。
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
当前最终验证：`scripts/verify.py` → **325 passed in 17.88s**；Ruff PASS；mypy src PASS（32 files）。
新增 92 项 = 47 契约/目标测试 + 44 文件契约测试 + 1 原图导出回归。
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

当前 READY_FOR_REVIEW，独立 reviewer 尚未给出决定；在提交后补记审核基线、发现与复验。
不沿用 D1 的 ACCEPTED 代替 D2 审核。

## 8. 已知限制与下一步

- 结构性引用校验只证明引用存在，不证明原文支持工程结论；source 文件 hash 也不是真实性认证。
- 设计说明仅逐行/逐页保留，尚未自动做自然语言事实/冲突判断；没有把文档文本标为已确认模型事实。
- PDF 不做 OCR，空页/无文本页拒绝；不是页面布局还原。BOM 仅读 BOM 表，额外 worksheet 不参与分析。
- loader 不解决并发修改/解析器进程资源隔离；SysML 读取前后变化会拒绝，不声明对抗性原子快照。
- Pydantic 数据仍可被 Python 调用方修改；对外接入/导出须使用正常验证入口，不使用 model_construct
  或未验证 model_copy 晋升数据。D4 的生成语义/原文支持校验与 D6 导出尚未实现。
- 旧 JSON 来源缺失问题按 D2 清单补齐，但旧 CLI 不等于自包含的 CandidateReport。
- D2 审核通过后，下一主会话按 Plan 进入 D3 可独立验证的只读 Neo4j 检索。
