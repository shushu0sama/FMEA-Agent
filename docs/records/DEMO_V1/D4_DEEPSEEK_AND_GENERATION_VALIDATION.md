# Demo V1 D4 — DeepSeek、输入解析与生成校验

日期：2026-09-05
Stage status: READY_FOR_REVIEW（仅 Demo V1 / D4 技术范围）
Closeout status: READY_FOR_REVIEW
Scope: Demo V1 / D4（A04、A07、A08），不包括 D5–D7 或正式 MVP-3 验收。

## 1. 依据与 Git 基线

用户明确授权本会话实现、测试、适用验证、独立审核、记录、提交与推送；
不重复需求问卷，不提前实现工作流、报告/UI 或完整端到端验收。
已读取 AGENTS、PROGRESS、文档导航、[Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Plan D4](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)、
[D3 收尾](D3_READONLY_NEO4J_RETRIEVAL.md)、[D2 契约记录](D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)、
[治理政策](../../governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md)、
[V1 架构](../../architecture/FMEA_AGENT_V1_ARCHITECTURE.md)、FMEA profile/术语及依赖清单。

- 起点分支 `codex/demo-v1-d3-readonly-neo4j`，HEAD `9643c371e755e606ca198cf23403a8f7bb562e35`。
- 工作区干净；`git fetch origin` 成功，远端 D3 同为 `9643c37`，无交接漂移。
- 从该 HEAD 新建 `codex/demo-v1-d4-deepseek-validation`，沿用当前 checkout / `.venv`。
  包含 D0–D3 规划、实现、修复和接受记录，没有从旧 master 起步。
- D3 独立复审 `059b6ee` ACCEPTED 的范围和真实图未验证限制不变。
- 不合并 master，不变更发布 tag、D1 工件、旧 workflow、领域契约或 benchmark gold。

## 2. 实际实现与复用

| 文件 | 交付 |
|---|---|
| `adapters/llm/deepseek.py` | 官方 JSON API、连接/读取超时、一次重试、六次请求预算、有限响应读取、安全错误与 usage |
| `adapters/llm/__init__.py` | 可选适配器包；导入时不加载 HTTPX |
| `application/_demo_json.py` | 1 MiB 严格 JSON object 解码，拒绝重复 key、非有限常量及非 object |
| `application/demo_ports.py` | 在既有 DemoLLMClient 之外增加中立 DemoModelError；错误只携安全 code |
| `application/demo_intake.py` | 用户 EvidenceRef、合法目标清单/prompt、自然语言结果解析、原文支持与工况补问 |
| `application/demo_generation.py` | 受限目标/prompt、reference_hits 视图、生成 schema/状态/引用/原文校验 |
| `scripts/demo_model_smoke.py` | 固定公开 D1 资料 hash 检查、通用 JSON 与完整候选 schema 的真实调用入口 |
| 三个 `tests/test_demo_*.py` | HTTPX MockTransport、应用语义和 smoke 入口确定性测试 |

上表 `adapters/`、`application/` 均以 `src/fmea_agent/` 为前缀。
接口遵循既有 `LLMClient.generate(prompt)->str`、`DemoLLMClient.usage()`，
以及 Plan 指定 `parse_intake(raw, inputs)` / `validate_generation(raw, allowed_evidence)`。
另提供 `record_user_input`、`build_intake_prompt`、`analyze_intake`、
`build_generation_prompt`、`generate_analysis`，供 D5 装配，不实现会话状态机。

复用分类：HTTPX = W；Pydantic、JSON/hash/UUID/时间 = D；FMEA 字段语义与证据检查 = S。
先检索旧 MockLLMClient/LLMClient、D2 模型与 D3 检索入口；不引入新的 Agent runtime、
HTTP 库、图框架或提供商 SDK，domain 与 HTTP/提供方保持隔离。

## 3. 官方 API 与传输边界

接入当日核对 [DeepSeek 官方 Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)。
当前文档支持计划指定 `deepseek-v4-pro`、`response_format={type:json_object}`、
`thinking={type:disabled}`、非流式请求和 `max_tokens=4096`。
**未发现要求修改计划的实质差异，没有改用别名或扩大能力范围。**
独立 JSON Output 指南页面本次两次读取返回工具 Internal Error；请求格式、JSON 指令及
length 截断约束由可读取的官方 API 页面交叉核对，不声称读取了失败页面。
文档支持不等于当前账号 live 成功，真实结果见第 5 节。

HTTPX 0.28.1 上游核对：[超时](https://www.python-httpx.org/advanced/timeouts/)、
[流式读取](https://www.python-httpx.org/quickstart/#streaming-responses)，以及本机固定版本的契约执行。

- 官方固定端点 `https://api.deepseek.com/chat/completions`；无自定义端点或工具调用入口。
- `httpx.Timeout(60.0, connect=10.0)` 为连接及读取/写入/连接池阶段约束，不是总会话时限。
- HTTP 使用流式**读取传输体**以实施大小限制，但提供商请求 `stream=false`，不是 token/SSE 流式生成。
- 正常响应最多 1 MiB；Content-Length 与实际读入字节都检查；拒绝非 identity 压缩响应，
  避免先完整解压后才检查；不读取错误响应正文。
- 只对 429/502/503/504 重试一次，固定等待 1 秒，不采用不可信的超长 Retry-After。
  所有尝试（包括失败和重试）计入六次预算；第七次在本机拒绝，没有无限输出修复调用。
- 只接收单 choice、finish_reason=stop、非空 JSON object 内容；拒绝工具/函数调用输出。
- 安全错误：CONFIG_MISSING / CONFIG_INVALID / DEPENDENCY_MISSING / CLOSED、AUTH_FAILED、
  TIMEOUT、CONNECTION_FAILED、REQUEST_FAILED、RATE_LIMITED、CALL_BUDGET_EXCEEDED、INVALID_RESPONSE。
  异常不链接底层正文，repr 不含密钥；不写模型输入/输出日志。
- API key 仅由 `from_env()` 读取进程 `DEEPSEEK_API_KEY`；不读 `.env`、旧 importer 或私有记录。
  密钥存于 SecretStr；缺失不切 mock。自建 HTTP client 禁止 redirects、ambient proxy 配置；
  没有额外传输层重试。注入 client 由调用者管理，适配器仍逐请求禁止 redirects。
- 每同步会话独立 client，记录请求数、UTC 调用时间、请求模型及服务响应模型标识，
  token 为服务报告的累积数，缺失保持 None；usage_response_count 表明报告次数。
  缺失/失败请求的费用没有估算，模型服务别名不等于永久权重版本。

## 4. 输入与生成语义

- intake 的合法目标来自实际 CSM 组件/功能 allocation；非法 ID、根功能、错误组件/功能对、
  未解决结构冲突与不存在的引用阻断。调用方原 CSM 不被修改。
- 文档/输入 FACT 的值须是每个引用文本的精确非空子串；支持不足降为 INFERENCE，
  保留模型提议、证据和待确认说明。该检查仅证明原文包含，不证明语义正确或工程真实性。
- context 使用 environment / operating_phase / load，可附 analysis_focus。
  未知工作状况补问；用户自由文本作为带 hash 的 user EvidenceRef 追加在副本，不自动成为批准知识。
  最多两轮补问、continue_unknown 以及 UI 幂等在 D5 实现，本阶段没有自行跳过这些工作流边界。
- 生成前再次校验 READY 目标、引用和 FACT 支持。仅把 D3 `reference_hits` 与输入证据交给模型；
  原始查询词、REJECTED 名称/正文/理由不放入生成 prompt，原 RetrievalResult 完整保留给调用方。
  全排除仍保留 HITS；提示 NO_USABLE_REFERENCE，不伪造 NO_MATCH。
- 图 ERROR 默认抛 RETRIEVAL_ERROR，不调用模型；显式 `allow_retrieval_error=True` 才可继续，
  生成缺失项追加检索失败说明，原审计仍为 ERROR。不自动填充成功报告。
- 1–8 行，模式必须是非空 INFERENCE；其他新增字段仅 INFERENCE 或 UNKNOWN/null。
  当前对象的字段不能把历史原文升级为 RETRIEVED_KNOWLEDGE/FACT；历史原文保留在参考证据中。
- 既有控制 FACT 只接受非 Neo4j 的输入原文及合法证据；模型建议不能宣称已实施。
  非法/重复 evidence ID、虚构目标/source/score/AP/approved、额外字段、空结果或畸形 JSON 均拒绝。
- 重复候选保留为独立行及各自引用，不静默合并或丢弃来源；三层影响契约沿用 D2。
- 资料和模型输出仅作数据，无 shell、链接抓取、文件执行或 tools dispatcher。
  提示词强调边界，确定性 schema/语义校验负责最终接收；不宣称解决所有自然语言提示注入。

范围变化：**NO**（不进入 D5–D7，不改变长期架构）。响应压缩拒绝、1 秒重试、
固定 context 名称、空候选拒绝、smoke 公开资料 hash 白名单属于已接受边界内的实施细化。

## 5. LOCAL 验证与真实 smoke

- 开始基线 `scripts/verify.py`：378 passed in 19.91s；Ruff PASS；mypy 35 files PASS。
- 首批 55 项测试因缺 D4 功能失败，实现后通过；9 项 smoke 测试因缺脚本失败，实现后通过。
  RED 为真实本机执行，未独立保存在 Git commit 中。
- 后续增加 25 项传输、预算、全排除、字段状态、目标关联和 intake 回归；D4 共 **89 passed**。
- 全套 `scripts/verify.py`：**467 passed in 19.83s**；Ruff PASS；mypy src 39 files PASS。
  包含原 CLI、SysML、D1–D3、B0/B1 与 orphan 回归；gold/度量未变，无已观察退化。
- `mypy src scripts/demo_model_smoke.py`：40 files PASS。
- `uv lock --check --offline`：78 packages PASS；diff whitespace PASS。
- `uv add --optional demo httpx==0.28.1` / `uv sync --extra demo`：仅增加直接依赖声明，
  已有包版本不变；HTTPX 的安装元数据许可证为 BSD-3-Clause。

真实 smoke：`python scripts/demo_model_smoke.py` 于 `2026-09-05T10:39:38.534122+00:00`
返回 **SKIPPED / CONFIG_MISSING**，generic_json 与 generation_schema 都为 NOT_RUN。
没有建立真实 DeepSeek 连接，没有验证账号模型可用性、真实 JSON 输出或 token/工程质量。
脚本只允许固定 D1 公开教学资料的三份 hash，载入后复核；通用 JSON 与 motor/spin 完整 schema
为两次逻辑调用，共享六次预算；不访问真实 Neo4j。
smoke 同步运行期间抑制标准 logging 并恢复原门槛，stdout/stderr 只允许最终安全摘要。

CI = NOT_CONFIGURED。真实 Neo4j 仍沿用 D3 的 SKIPPED / CONFIG_MISSING 状态，
没有用 D4 mock 验证替代真实图或模型验证。

## 6. 独立审核与 Git 收尾

待实施提交/推送后开展独立只读审核，当前不宣称 ACCEPTED。
审核结论、发现、修复与复验在本节追加，保留真实演化。

## 7. 已知限制与下一步

- 工程正确率、完整性、风险评分和批准未验收；所有新内容仍属候选/推断。
- 精确原文子串、引用存在及文件 hash 不证明结论得到语义支持，也不认证来源真实性。
- 公开资料同源派生，仅用于接口演示，不是独立工程 gold。
- 超时不是进程/整个会话硬截止；client 面向单同步会话，D5 负责串行调用与幂等。
- 注入 HTTP client/transport 是受信任测试/集成设施，其自定义 hooks/重试需调用者治理；
  本阶段 smoke 的临时全局日志抑制不是 D6 UI/服务日志策略。
- 没有真实 API 配置，live 接入仍待验证；不自动读取配置文件或切换模型。
- 下一建议任务：D4 被独立接受后进入 D5 受控工作流，复用本次应用服务与 D3 审计，
  实现两轮补问/未知继续、会话预算与 request_id 幂等；本会话不提前实现。
