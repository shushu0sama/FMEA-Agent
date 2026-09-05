# Demo V1 技术演示验收报告

Lifecycle: ACTIVE
日期：2026-09-05
技术演示状态：ACCEPTED（独立最终审核，仅受限 Demo V1 / D7 技术范围）
人工工程质量状态：NOT_ACCEPTED（没有人工关键结论抽查）

依据：[已接受 Spec](../specs/DEMO_V1_END_TO_END_FMEA.md) A01–A12、
[Plan D7](../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)。
Git 起点 `dadc36c`，分支 `codex/demo-v1-d7-acceptance`；提交、审查和修复演化见
[D7 阶段记录](../records/DEMO_V1/D7_DEMO_RELEASE.md)。
本报告验收受限 Demo，不等于正式 MVP-2/3/5 发布，更不等于 MVP-7 航空基准。

## 1. 三类独立场景与数据边界

| 场景 | SysML / 输入 | 检索 | 模型 | 服务 / 导出 | 实际结果与范围 |
|---|---|---|---|---|---|
| S1 确定性成功 | REAL_FILE，固定公开 SysML/MD/CSV | mock，FAKE_NO_MATCH | deterministic-demo-mock | 真实 LangGraph/DemoService/三格式导出 | LOCAL PASS；真实浏览器另从演示资料包操作成功；不提供工程 gold |
| S2 图来源查回 | 不使用 SysML | LIVE_NEO4J，SOURCE_LOOKUP | NOT_USED | 真实只读 adapter/smoke | LOCAL PASS，20 hits、locator_verified=true、随机不存在词 NO_MATCH、truncated=true |
| S3 无可用参考推断 | REAL_FILE，三文件固定公开 hash | FAKE_NO_MATCH；未构造 Neo4j adapter | LIVE_DEEPSEEK | 真实补问/未知继续/服务/独立三格式导出 | LOCAL PASS，8 条候选、2 次请求；工程质量 NOT_ACCEPTED |

三者不能拼写为“全 live 完整集成”。S2 的私有工程正文不进入 S3，不提交私有图结果。
S3 的 NO_MATCH 是明确构造的无参考场景，不能证明真实图对 motor/spin 无适用知识。
默认 live UI 的图与模型装配已存在，但本次**未运行私有图正文 → 外部模型**链路；
未来验证须先具备允许外发的知识资料及对应工程依据，不能为补齐标记突破数据边界。

## 2. A01–A12 验收矩阵

路径中 `src/` 表示 `src/fmea_agent/`；下列测试文件均在 `tests/`。
LOCAL 全套和真实服务结果见第 3 节；独立审核结果单独见第 5 节。

| ID | 实现 / 契约依据 | 自动验证证据（LOCAL） | 真实验证 / 用户入口 | 未覆盖边界 |
|---|---|---|---|---|
| A01 | `scripts/build_demo_inputs.py`、`examples/demo_v1/manifest.json`、D1 来源 | `test_demo_inputs_manifest.py`，固定 hash、重复生成、未知数量 | S1/S3 真实重读公开原文与派生资料 | 同源派生资料不是独立工程 gold |
| A02 | `src/adapters/sysml/`、`src/adapters/documents/demo_inputs.py`、`src/agents/demo_workflow.py` | `test_demo_e2e.py::test_real_sysml_mock_service_to_standalone_three_formats`；B0/B1 | S1/S3 定位 motor/spin，报告保留 pumpSpin 排除 | 单文件子集；未扩展 import/接口/流/系统级功能分析 |
| A03 | D2 输入契约、`src/adapters/documents/`、`src/application/demo_uploads.py` | `test_demo_document_inputs.py`、`test_demo_contracts.py`、`test_demo_ui.py` | 真实 SysML/MD/CSV 载入；独立 AppTest 三文件上传 | 本次浏览器不重测 OS 文件选择器；PDF/XLSX 定位由自动契约验证，不声称浏览器覆盖 |
| A04 | `src/application/demo_intake.py`、`demo_service.py`、`src/agents/demo_workflow.py` | `test_demo_service.py`、`test_demo_ui.py`、D7 ready_service 场景 | S3 真实补问/未知继续；浏览器 WAITING_INPUT→READY | 多目标身份另由确定性夹具验证；无自然语言准确率结论 |
| A05 | `src/adapters/neo4j/failure_knowledge.py`、D3 固定只读查询 | `test_demo_neo4j_contract.py`、`test_demo_neo4j_smoke.py`、D7 连接故障参数回归 | S2 真实来源定位/HITS/NO_MATCH；浏览器故障使用明确 fake 注入 | 未中断真实数据库；有界截断不等于完整召回 |
| A06 | `src/application/demo_retrieval.py`、`src/domain/demo_knowledge.py` | `test_demo_retrieval.py`、`test_demo_neo4j_contract.py`、`test_demo_workflow.py` | S2 仅来源查回，SOURCE_CONTEXT_ONLY | 没有跨案例批准；独立关系不是原始 FMEA 行；适用性/实体解析未正式验收 |
| A07 | `src/application/demo_generation.py`、D5 服务 | `test_demo_generation.py`、D7 S1 与显式降级回归 | S3 真实 DeepSeek 8 个 INFERENCE 模式；无可用知识仍生成 | 不以生成文本逐字一致或模型自评验证工程正确性 |
| A08 | D2 严格 schema、D4 transport/intake/generation 校验 | `test_demo_contracts.py`、`test_demo_deepseek.py`、`test_demo_generation.py`；D7 空 FACT 来源/错误引用/空候选→FAILED | 真实模型输出通过当前 schema；独立入口负例见第 5 节 | 引用存在、原文子串和 hash 不能证明结论获语义支持 |
| A09 | `src/adapters/reports/demo_report.py`、CandidateReport.input_snapshot | `test_demo_reports.py`；D7 删除会话后 JSON 往返/HTML/CSV，来源/未知/状态保留 | S3 独立导出；浏览器真实三格式下载与恢复后导出逐字节一致 | 不含原始二进制；CSV 大 JSON 单元格可能超过表格应用显示容量；无 PDF 排版验收 |
| A10 | `src/ui/demo_app.py`、D5 幂等/输入摘要 | `test_demo_ui.py`、`test_demo_service.py`、D7 改名/改路径/重复请求回归 | 浏览器补问、生成、来源、下载；故障显式降级分别记录 | AppTest 不替代真实下载；幂等仅同进程同 service，无跨进程持久恢复 |
| A11 | 领域/端口/adapter 边界与既有原 CLI/workflow | `scripts/verify.py`；B0/B1 11 项；既有 orphan/CLI 回归 | 真实 parser 纳入自动套件 | CI 未配置；不新增航空工程 benchmark 或改变 gold |
| A12 | 候选/推断、未评分、未优化的契约及 UI/报告文案 | schema 负例、报告/UI 断言、独立入口审核 | 浏览器 CANDIDATE/INFERENCE、NOT_EVALUATED/SKIPPED 可见 | 无概率校准、人工批准、措施实施、知识写回或模型训练 |

## 3. LOCAL 自动验证与真实服务结果

环境：Windows，本地 `.venv`；固定依赖与版本见[依赖清单](../research/DEPENDENCY_INVENTORY.md)。
不依赖外部服务的常规测试均为确定性 fake/mock；真实 SysML parser 属于本机验证。

| 命令 | 实际结果 |
|---|---|
| `.venv/Scripts/python.exe scripts/verify.py` | 539 passed in 25.42s（标题文案收尾后复验；此前 32.51s）；Ruff PASS；mypy src 50 files PASS |
| `uv lock --check --offline` | PASS，104 packages |
| `.venv/Scripts/python.exe -m pytest tests -k demo -q` | 325 passed / 214 deselected in 25.33s |
| `.venv/Scripts/python.exe -m pytest tests/test_mvp1_benchmark.py -q` | 11 passed in 1.15s；B0/B1 原 gold 未改，无观察到退化 |
| `.venv/Scripts/python.exe -m mypy src scripts/demo_acceptance_smoke.py` | PASS，51 source files |
| `git diff --check` | PASS |

真实验证全部用 `uv run --no-sync --offline --env-file .env.local python scripts/<脚本>`。
`--offline` 仅限制 uv 包管理，脚本仍访问已授权真实服务；配置不被打印、覆盖或提交。

| 脚本 | 开始时间 UTC | 实际结果 |
|---|---|---|
| `demo_neo4j_smoke.py` | 2026-09-05T12:38:35.226304 | PASS；HITS 20，context_count=1020，association_count=192，locator_verified=true，absent=NO_MATCH，truncated=true；只读 |
| `demo_model_smoke.py` | 2026-09-05T12:38:36.830677 | PASS；generic_json/generation_schema PASS；6 候选，2 请求，prompt=6799、completion=2754、total=9553 tokens；graph_used=false |
| `demo_acceptance_smoke.py` | 2026-09-05T12:39:49.480479 | PASS；完整服务、补问、未知继续、重复请求不增调用、独立导出；8 候选，2 请求，prompt=13071、completion=2132、total=15203 tokens；FAKE_NO_MATCH |

两次模型验证均请求/响应 `deepseek-v4-pro`；名称为服务别名，不声称权重永久固定。
S2 的证据计数是每个 hit 列表长度之和，含共享引用，不是唯一关系数量。
最新真实图 PASS 与 D3 第 8 节一致，历史 CONFIG_MISSING/AUTH_FAILED 不被改写。
本机安全摘要在 ignored `outputs/d7-validation/`；公开候选在 ignored `outputs/d7-public-smoke/`。

S3 独立导出：JSON 55790 bytes、HTML 73904 bytes、CSV 385724 bytes。
对应 SHA-256：

```text
JSON 99fcdd2ae0eaf9d13a5dcd4d3123fabfcbfb08e7a6cd30515bad63b71c450cc3
HTML 3f7432b8da1ee459e847cc988a72d1bdc0868e00e25c4b845fdde58e8a8f4100
CSV  e043a0052eaaa9ce059d0e4fbe7a1646e6344fe7c01d11401e939cba263cbacb
```

这些 hash 固定本次运行工件，不要求下次真实模型生成文本或 run_id 一致。
人工关键结论抽查 NOT_RUN；工程准确率/覆盖率/适用性 NOT_EVALUATED。

## 4. LOCAL 浏览器与 AppTest 分开记录

AppTest：真实 UI、上传控件、parser、service、export；仅模型/图可替换。
覆盖两轮补问/空回答/未知继续、错误诊断、检索故障/明确降级、下载准备/点击不增调用、
上传增加/替换/移除/改名失效；它不证明 OS 文件选择器、浏览器网络或磁盘保存。
D6 历史真实上传证据仍见 [D6 第 5 节](../records/DEMO_V1/D6_REPORTS_AND_LOCAL_UI.md#5-local-浏览器操作与-apptest-覆盖边界)。

本次真实浏览器为 Codex in-app browser，标准 UI 仅监听 `127.0.0.1:8501`，明确 mock。
选择演示资料包→真实载入三文件→motor/spin→提交→WAITING_INPUT→明确未知继续→READY→生成→COMPLETE。
浏览器显示 NO_MATCH 的有界含义、候选/风险/优化状态；展开证据可查文档行、BOM 行、hash、来源限制。
run_id=`97076d53430442869b73d126dbcf57c3`，1 候选、2 请求。
实际下载 JSON/HTML/CSV 后，分别为 47754 / 61138 / 47966 bytes，均与下载 JSON 恢复后的导出逐字节相同；
下载事件和页面重绘没有新模型调用。未把仅点击按钮当作磁盘保存证据。

故障浏览器验证单独使用 ignored 临时 wrapper，绑定 `127.0.0.1:8502`：
复用原 UI，标题注明 `FAKE_CONNECTION_FAILED`，仅把 mock repository 返回值改为 ERROR/CONNECTION_FAILED。
浏览器实际 ERROR/CONNECTION_FAILED 阻停且没有下载，明确勾选降级后 COMPLETE，仍显示实际检索 ERROR。
实际下载 JSON 验证 error_code、缺失知识说明、2 次模型调用；run_id=`31e7cb21008746a3854866638e33f4bd`。
新建会话后旧候选/下载撤销，PASS。wrapper 仅改变 fake 仓库，客户端 mock 标签不证明 NO_MATCH，
故障实际模式以显式注入标记和 report.retrieval.ERROR 为准；不是停止真实 Neo4j 或真实网络故障。

## 5. EXTERNAL_REVIEW

独立 reviewer：`/root/d7_independent_review`，只读检查，不共享实现写入、不读取 `.env.local`、不调用真实服务。
首轮工作区探查：539 passed in 28.83s，Ruff/mypy src50/lock104/diff PASS。
另 6 组真实上传 AppTest 入口检查通过：NO_MATCH/三格式/改名失效、错误引用、FACT 空来源、空生成、
仓库异常/无自动重查/明确降级/保留 ERROR；下载与重绘不增调用，内部异常不泄漏。
另用真实 Neo4j adapter + fake driver/LLM 验证 HITS、四条独立关系、UNKNOWN 适用性与无虚构表行。
固定最终审核范围 `dadc36c..f550a0dff52b68c035c266f7205eb3330c7b4f01`，11 文件；结论 **ACCEPTED**。
未解决 CRITICAL=0 / IMPORTANT=0 / MINOR=0。首轮全套验证的新增脚本/测试 hash 与送审版本一致；
固定 HEAD 另复验 D7 E2E + UI 共 22 passed in 4.08s，Ruff、mypy src+smoke51、lock104、完整范围 diff PASS。
A01–A12、MVP-2/3 差距及三份 LOCAL 脱敏真实摘要与记录一致；工作区/index 干净。
这些独立自动验证不属于人工工程质量抽查。最终仅治理回填，未改变被审代码。
CI：NOT_CONFIGURED。EXTERNAL_REVIEW 不替代 LOCAL 真实服务证据。

## 6. 正式 MVP-2/3 的复用能力与验收差距

| 正式里程碑 | Demo 已实现能力 / 证据 | 限制与正式验收差距 |
|---|---|---|
| MVP-2 Real Failure Knowledge | D2 来源/查询/命中契约；D3 固定双入口只读 Neo4j、来源定位、独立关系、截断/排除/错误；D5 接入；A05/A06、S2、检索契约测试 | 正式 Spec 仍为 REFERENCE/ORIGINAL DRAFT，独立阶段未开工；缺经审核的实体解析/跨案例适用性依据、歧义处置与来源覆盖、Level 3 独立检索 gold/召回与精确率评估、正式里程碑复审与发布；不把来源命中当工程适用 |
| MVP-3 Evidence-grounded LLM | D4 provider 中立端口、DeepSeek 预算/脱敏/schema/来源检查；D5 有界补问与幂等；D6 自包含报告；A04/A07/A08/A09、S3、传输/生成/会话测试 | 仅字段状态/引用存在/部分精确原文支持校验；缺独立工程 gold、人工语义审查、工程正确率/完整性/跨案例泛化评估；允许外发的真实知识与模型联合验证尚缺；正式当期 Spec/Plan 与独立验收仍需建立 |

后续先核对正式当期 Spec 与上述差距，直接复用已通过验证的端口、adapter、service、测试，
补齐所缺证据和能力，不重复重写 Demo。MVP-4/5/6/7/8/9 仍按正式路线，
补问按钮不等于 Human Review，D7 不等于 Aerospace Benchmark。

## 7. 技术与工程质量结论边界

技术结论只覆盖既定 Demo 输入、错误处理、状态、可追溯导出和三类独立场景。
未提供人工工程抽查，因此结果始终 CANDIDATE，新增判断 INFERENCE，未知保持 UNKNOWN，
风险 NOT_EVALUATED、优化 SKIPPED；没有未经授权的评分、批准或知识写回。
教学液压泵模型不是已审航空产品；本报告不声明概率校准、完整图与模型集成或正式工程质量通过。
