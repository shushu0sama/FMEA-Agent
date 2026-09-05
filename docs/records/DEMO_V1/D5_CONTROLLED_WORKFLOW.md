# Demo V1 D5 — 可补问、可恢复及请求幂等的受控工作流

日期：2026-09-05
Stage status: READY_FOR_REVIEW
Closeout status: READY_FOR_REVIEW
Scope: Demo V1 / D5（A04、A07、A10 的服务基础）；D6 UI/导出、D7 验收未实现。

## 1. 依据、起点与范围

用户授权在本会话实现、测试、适用验证、独立审核、记录、提交与推送。
读取 AGENTS、PROGRESS、文档导航、[Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Plan D5](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)、
[D4](D4_DEEPSEEK_AND_GENERATION_VALIDATION.md)、[D3](D3_READONLY_NEO4J_RETRIEVAL.md)、
[D2 契约记录](D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)、
[治理规则](../../governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md)与
[V1 架构](../../architecture/FMEA_AGENT_V1_ARCHITECTURE.md)。沿用已接受需求，不重复问卷。

- 起点 `codex/demo-v1-d4-deepseek-validation` / `90ef7d15c0472398c762595236282a4a8f82104e`。
- `git fetch origin` 成功，本地与远端 D4 一致，工作区干净。
- 从此 HEAD 创建 `codex/demo-v1-d5-controlled-workflow`，沿用当前 checkout 和 `.venv`。
  包含 D0–D4 全部交接记录，没有从旧 master 开始。
- 已核对 D3/D4 第 8 节最新真实服务均 PASS；历史 CONFIG_MISSING/AUTH_FAILED 未覆盖或误判。
- 不改 D2–D4 能力、原 workflow/CLI、基准 gold、依赖、master 或发布 tag。

## 2. 实际文件与调用接口

| 文件 | 职责 |
|---|---|
| `src/fmea_agent/agents/demo_state.py` | DemoSession / DemoGraphState 中立数据及状态约束 |
| `src/fmea_agent/agents/demo_workflow.py` | LangGraph intake、retrieve、generate、document 节点与失败诊断 |
| `src/fmea_agent/application/demo_service.py` | start/answer/analyze、会话隔离、权威快照、请求签名和串行执行 |
| `tests/test_demo_service.py` | 补问、幂等、并发、失败、中断、输入变更及错误时序 |
| `tests/test_demo_workflow.py` | 状态往返、报告来源、排除项、适配器预算及未知工况 |

构造与三个公开方法保留 Plan 签名。一次 UI 会话保存一个 `DemoService(repo, fresh_client)`，
新文件或新分析创建新 service 和独立 client；不重置旧 client 的 HTTP 预算。
连接的构造/关闭由调用者负责，session 没有连接、锁、图对象或凭据。

复用分类：LangGraph = W；Pydantic、threading.Lock、JSON/hash/UUID = D；会话状态/幂等规则 = S。
复用 D4 `analyze_intake`、`record_user_input`、`generate_analysis` 与 D3 `prepare_query/retrieve`。
已检索原 graph/端口/领域契约，核对已安装 LangGraph 1.2.11 的 StateGraph、compile、stream API，
以及[官方图 API](https://docs.langchain.com/oss/python/langgraph/graph-api)。未更换运行时或升级依赖。
回调采用具名参数 Protocol 兼容固定版本类型声明；stream 传入类型化状态。

## 3. 实施细化与恢复边界

- `start/answer` 只运行 intake，结束于 WAITING_INPUT / READY / FAILED。
  `analyze` 才进入 retrieve → generate → document；WAITING_INPUT 无检索和生成调用。
- 首轮集中列出工况缺失项；第二轮仍未知时保留清单。轮数最大 2，不开启第三轮问题。
  之后用户主动提交非空信息仍可调用 intake 解析（受 D4 总预算限制），没有新增集中补问轮次。
  空回答不追加 user EvidenceRef、不调用模型、不增加轮数。
- `continue_unknown` 是明确的接口动作；只有合法目标可继续。未确认的模型字段转为 UNKNOWN/null，
  保留引用、限制及问题，生成结果和最终报告补齐未确认字段及缺失问题。
  输入冲突在模型调用前失败；非法目标、解析/引用错误失败后不能靠未知继续恢复。
  partial/解析错误由 D2 loader 在产生 LoadedInputs 前拒绝，D5 不另写解析器。
- 检索 ERROR 保持 READY 并提供安全错误；显式新请求设置 `allow_without_retrieval=True` 后继续。
  恢复复用同一原始 ERROR，不重查或改成 NO_MATCH。意外仓库异常转换为 ERROR/RETRIEVAL_FAILED，
  不暴露底层连接信息。已开始检索后冻结目标和工况，改变分析须新会话。
- 完成报告为 CANDIDATE / NOT_EVALUATED / SKIPPED；携带完整输入、context、原始检索和所有图证据。
  REJECTED 证据及理由保留用于审计，D4 过滤视图保证它们不进入生成 prompt。
  明确列出其他组件/功能（包括 pumpSpin）与拒绝参考的排除项。
- 生成/schema/引用/报告组装失败：FAILED DiagnosticReport、generation=None、report=None。
  复用 D4 空候选拒绝规则，不将空结果称为成功或“系统无失效”。

幂等范围是**当前进程中同一个 service/session**，不是跨进程、持久事务或分布式 exactly-once。
服务保存权威快照；调用者传入的旧快照只用于验证会话/输入身份，不能修改 phase 绕过门禁。
返回深副本，可序列化再交回同一 service。进程重启后新建会话重新运行，符合 Spec §7；
不会将单独的 JSON 快照导入新 service 后假称恢复了旧预算。

请求 ID 与操作/消息/显式选项的摘要绑定；同 ID 同内容返回当前权威状态，不再调用外部服务。
同 ID 改内容返回 REQUEST_ID_CONFLICT，变更选项须新 ID。每会话有独立请求记录；
Lock 覆盖请求登记到图结束，重复并发请求也不会重复分析。
在外部调用前登记请求，节点更新逐步保存；KeyboardInterrupt/SystemExit 等中断形成安全失败状态后重抛，
重提返回诊断，不重复不确定的外部副作用。失败会话不自动重试生成。
文件摘要或非对话输入快照变化返回 NEW_SESSION_REQUIRED；原始 CSM 与证据不被来回传递的快照覆盖。

上述为已接受 D5 的内存会话/显式动作接口细化，未进入 D6/D7 或正式人工审核。

## 4. LOCAL 测试与开发证据

- 基线：473 passed in 20.38s；Ruff PASS；mypy src 40 files PASS。
- 首批 15 项 service 测试因缺少模块失败，最小实现后 15 passed。
  增补图/报告/真实 transport budget 的 8 项行为检查，23 passed。
- 另两项时序回归先 2 failed：空 start 请求先创建状态导致后续合法 start 被阻断；
  检索后 answer 先登记再拒绝导致重提表现不同。校验前移，保留真实失败历史。
- 当前全套：`python scripts/verify.py` → **498 passed in 20.74s**；
  Ruff PASS；mypy src PASS（43 files）。D5 共新增 25 项。
- `uv lock --check --offline` PASS（78 packages）；`git diff --check` PASS；D4 祖先关系确认。
- 上述 RED→GREEN 为本机执行记录，RED 没有独立保存为 Git commit。
- 全套包含 B0/B1、原 CLI/workflow、SysML 和 orphan 回归；gold 与度量未改，无观察到的退化。
  新测试使用确定性 fake / HTTPX MockTransport，没有外部服务调用。
- CI = NOT_CONFIGURED。独立审核结果单独见第 6 节。

## 5. LOCAL 真实 DeepSeek 的 D5 补充验证

2026-09-05T11:20:55.508470+00:00 开始，显式通过
`uv run --no-sync --offline --env-file .env.local python -` 注入环境。
未读取、打印、改写或提交配置文件。验证程序经 stdin 执行，没有新增生产 smoke 或 D7 验收器。

复现方式：复用 `scripts/demo_model_smoke.py` 的 `_public_inputs`（三个固定公开文件 hash 检查）和
`main` 安全日志/输出封装，将 `_run` 临时换为 D5 服务调用。只装配 `DeepSeekLLMClient.from_env()`
和显式 fake `PublicNoMatch.search(query) -> RetrievalResult(NO_MATCH, terms=query.terms)`；
完全不构造 Neo4j adapter。公开起始消息选择 hydraulicPump/motor/spin，说明三类工况均未知。

调用序列及断言：

```text
start(public_inputs, public_message, public-start) → WAITING_INPUT，question_rounds=1
start(相同参数) → 相同状态，request_count 不增加
answer(session, "", public-continue, continue_unknown=True) → READY
analyze(ready, public-analyze) → COMPLETE / CANDIDATE
analyze(旧 ready 快照, public-analyze) → 同一报告，request_count 不增加
fake repository calls == 1
```

结果：PASS；3 条候选；request_count=2，usage_response_count=2；
prompt_tokens=13093、completion_tokens=1738、total_tokens=14831；
model=response_model=`deepseek-v4-pro`，called_at=`2026-09-05T11:20:58.121820+00:00`。
safe_errors=[]；generation_schema=PASS；generic_json=NOT_RUN（本次不重复 D4 通用 JSON smoke）。

验证边界：真实本地 SysML/输入载入 + 真实 DeepSeek + D5 图/服务 + **FAKE_NO_MATCH**。
graph_used=false，未读取或发送私有工程图正文。不是 Neo4j 与外部模型的真实完整集成，
不是 UI/导出验收或工程正确率验收。D3 独立真实 Neo4j PASS 仍以 D3 第 8 节为准，本次未重跑。

## 6. EXTERNAL_REVIEW 与 Git 收尾

当前状态 READY_FOR_REVIEW，尚无本次独立接受结论。
代码与本记录验证后提交，独立 reviewer 将检查固定 `90ef7d1..实施提交` 范围，
重要发现修复并复验后再回填 ACCEPTED；不能将 LOCAL PASS 代替独立审核。

## 7. 限制与下一步

内存会话只在原 service 生命周期内恢复，单独快照不含适配器预算或持久幂等账本；
客户端使用独立新实例，真实 HTTP 请求上限继续由 D4 执行。无跨进程事务保证或自动失败重放。
补问解析仍是 LLM 输出，精确来源校验不证明工程语义真实性；所有生成内容待工程审核。
没有新增依赖、评分、批准、知识写回、UI 或导出器，正式 MVP-2/3/5 尚未因此验收。
下一任务在 D5 独立接受后进入 D6 报告与本机 UI，不提前宣布 D7 或整个 Demo 完成。
