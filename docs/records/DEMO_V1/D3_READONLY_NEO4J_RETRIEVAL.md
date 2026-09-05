# Demo V1 D3 — 可独立验证的只读 Neo4j 知识检索

日期：2026-09-05
Stage status: READY_FOR_REVIEW
Closeout status: 待独立审核及最终远端保存
Scope: Demo V1 / D3（A05、A06）；不是完整 Demo 或正式 MVP-2 验收。

## 1. 依据与 Git 基线

本次用户明确授权实现、测试、适用验证、独立审核、记录、提交与推送。
已读取 AGENTS、PROGRESS、导航、[Demo Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Plan D3](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)、[D2 收尾](D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)，
以及治理政策、V1 架构、[图基线](../../research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md)、
[实际输入盘点](../../research/MVP_2_INPUT_DATA_INVENTORY_2026_09_05.md)、依赖清单和 C-1 最终记录。
未重复需求问卷，未运行旧 importer 或读取秘密配置文件。

- 起点：`codex/demo-v1-d2-input-contracts` / `f6d83d1`，工作区干净。
- `git fetch origin` 成功，远端 D2 HEAD 同为 `f6d83d1`。
- 从此 HEAD 创建 `codex/demo-v1-d3-readonly-neo4j`，复用当前 checkout 与 `.venv`。
  包含规划与 D1/D2 全部实现/收尾；没有从旧 master 开始。
- 未修改既有 D1 工件、基准/gold、D2 领域契约和旧 workflow；没有进入 D4–D7。
- 本次不合并 master、不创建或移动发布 tag；技术与 Git 收尾证据在后文分别记录。

## 2. 实际交付与接口

| 文件 | 交付 |
|---|---|
| `src/fmea_agent/adapters/neo4j/failure_knowledge.py` | 固定查询、只读事务、图记录到 D2 证据/命中契约、配置与安全错误 |
| `src/fmea_agent/adapters/neo4j/__init__.py` | 可选适配器包，不提前导入驱动 |
| `src/fmea_agent/application/demo_retrieval.py` | 目标/查询词来源检查、排序、显式排除、可用参考视图 |
| `scripts/demo_neo4j_smoke.py` | 真实图关注要素查回、定位核对、随机不存在词；只输出状态/计数 |
| `tests/test_demo_neo4j_contract.py` | fake driver/session/显式 transaction 契约 |
| `tests/test_demo_retrieval.py` | D2 输入复用、身份、查询词预算与排除审计 |
| `tests/test_demo_neo4j_smoke.py` | smoke 成败、跳过及脱敏输出 |

复用 `SourceKnowledgeRepository.search(KnowledgeQuery) -> RetrievalResult`，不改长期端口或
旧 `FailureKnowledgeRepository`；Neo4j 类型只在 adapter 出现。

`prepare_query(inputs, intake, terms)` 要求合法 READY 目标、无结构冲突，先取 CSM 的组件/功能原名，
再加额外词；额外词须是本次 user EvidenceRef 原文子串或目标原名。保留原词，仅按原样去重，
超过 D2 的 5 词/80 字符限制明确拒绝。不从名字推断跨案例身份，未实现 D4 LLM 查询词提议。

`retrieve(..., rejected_ids={hit_id: reason}, rejected_terms={name: reason})` 保留 HITS、truncated
与全部命中，将用户明确排除的当前命中 ID 或精确归一化模式名称标成 REJECTED。
空排除理由拒绝；不会按模糊子串连带排除其他名称。
`reference_hits(result)` 只返回未排除命中的深副本，作为 D4 后续生成的参考入口；本次没有生成器。

## 3. 查询、证据与范围细化

- 两个有界入口：focus/mode 名称；focus 的功能、下层部件、下层功能名称。
  固定标签/关系与参数化 `$terms/$fetch_limit/$mode_ids/$edge_limit`；不接受用户 Cypher。
- 每入口取 `limit+1`，在两组有限候选中按 graph element ID 合并，精确名称优先，再按原始 name/id。
  NFKC/strip/casefold 仅用于排序和显式名称排除，数据库匹配仍为原词的 toLower/CONTAINS。
  名字和 element ID 不被归一化为新身份；结果注明有界词法检索，不承诺全库最优排序或完整召回。
- 按选中模式分别查 focus 来源上下文与四类模式边；上下文包括 focus→mode、功能、下层部件、
  下层功能和上一高层次功能及要求。两条起因+两条影响产生四条独立边，不组合为四条 FMEA 行。
- 实施资源细化：context 和 associations 各最多 1000 条模式/边记录，分别读 1001 条检测截断。
  超过时全局 `truncated=true`，各命中明确提示上下文可能不全；模式自身仍有节点证据。
  此预算与候选上限一样是 Demo 保护，不是工程容量指标；不宣称数据库扫描成本也仅为此数量。
- 每条实际 edge 一个 EvidenceRef；共享边在本次检索内复用同一 ID 和内容，同名不同节点及平行边不合并。
  JSON locator 包含 database、节点/关系 elementId、UTC retrieved_at、retrieval_id。
  text 为节点或独立边的结构化原值，SHA-256 对应该 text；不伪造工作簿/工作表/行号。
- 命中 ID 与证据 ID 加本次 retrieval UUID；图 elementId 仅为本次定位，不成为永久知识主键。
  图缺来源行、模式边无法归属具体 focus/function/当前目标等限制逐条保留。
- SOURCE_LOOKUP → SOURCE_CONTEXT_ONLY；TARGET_ANALYSIS → UNKNOWN。无自动批准、评分或写回路径。
  NO_MATCH 只表示本次两入口成功且无结果；任意读取/转换失败丢弃部分命中并返回 ERROR。

范围变化：**NO**（未进入其他 D 阶段或改变架构）。上述关系预算、精确排除接口与 UTC locator
是在已接受有界检索/来源契约内的实施细化，公开记录并纳入本次审核。

## 4. 只读配置、复用与依赖

从进程读取 `NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD/NEO4J_DATABASE`，database 默认 `neo4j`。
不自动读取 `.env`、Browser 会话、历史配置或 importer；配置缺失不切 mock。
通过 `Neo4jSourceKnowledgeRepository.from_env()` 构造并以 context manager 释放拥有的 driver；
构造器注入的 driver 生命周期属于调用者。

连接和连接池获取超时各 10 秒，显式 transaction timeout=10 秒；不使用 managed transaction 重试，
工厂同时固定 max_transaction_retry_time=0。只读 session、登记常量模板和无写接口共同形成边界；
READ 路由不是数据库授权，显式事务也不保证跨语句不可变快照。超时为驱动/服务器阶段约束，
不宣称进程、DNS 或整个 smoke 的硬性 10 秒截止。

安全代码包括 CONFIG_MISSING / CONFIG_INVALID / DEPENDENCY_MISSING / CLOSED、AUTH_FAILED、
TIMEOUT、CONNECTION_FAILED、QUERY_FAILED、INVALID_RECORD；不输出底层异常正文。
5.28 驱动没有公共 acquisition-timeout 子类型，先检查 TimeoutError cause 和明确服务器 code，
再在 ServiceUnavailable/SessionExpired 内部分类超时文本，仅返回安全 code。

复用：Neo4j driver = W；stdlib JSON/hash/UUID/Unicode = D；项目来源、排序与排除语义 = S。
执行 `uv add --optional demo neo4j==5.28.2` 和 `uv sync --extra demo`。
仅新增 neo4j 5.28.2 和 pytz 2026.3.post1，原锁定包版本无变化；许可证见
[依赖清单](../../research/DEPENDENCY_INVENTORY.md)。没有复制第三方源代码或私有工程记录。

上游核对：[官方 API](https://neo4j.com/docs/api/python-driver/current/api.html)、
[显式事务](https://neo4j.com/docs/python-manual/current/transactions/)，
并检查已安装 5.28.2 的公开 session.begin_transaction / driver configuration。
网页为当前版本，固定版本行为以本机安装源码/契约为依据；未因为上游有更新而升级计划 pin。

## 5. LOCAL 验证

- 开始基线：`scripts/verify.py` → 334 passed in 19.05s；Ruff PASS；mypy src PASS（32 files）。
- 首批 22 项测试因缺 adapter/application 模块失败；实现后 22 passed。
  另 6 项 smoke 用例先因脚本缺失失败，实现后通过。后续 14 项强化覆盖通过。
  RED 为本机执行证据，未独立保存在 Git commit 中。
- D3：42 passed in 0.28s。覆盖多起因/影响、共享 focus/边、全部上下文路径和控制类型、同名不同 ID、
  重复候选、scope、参数化/无写模板、NO_MATCH、部分读取失败、认证/超时/连接/非法记录、
  两类关系截断、查询词来源与预算、全排除保留 HITS、smoke 定位失败与安全输出。
- 全套 `scripts/verify.py` → **376 passed in 19.42s**；Ruff PASS；mypy src PASS（35 files）。
  包含原 CLI、SysML、D1/D2、B0/B1 和 orphan 回归；gold/基准度量没有修改，没有已观察退化。
- `mypy src scripts/demo_neo4j_smoke.py` PASS（36 files）；`uv lock --check --offline` PASS（78 packages）。
- 本机进程拦截 Neo4j import 后，application/adapter 模块导入与原 CLI 成功；
  这是可选依赖边界模拟，不是新建无 extra 环境。

真实 smoke：`python scripts/demo_neo4j_smoke.py` 于 `2026-09-05T10:07:32.578903+00:00`
返回 **SKIPPED / CONFIG_MISSING**。未建立真实 Neo4j 连接，未验证真实 Cypher 执行或工程知识正确性。
历史 Browser 查询通过不替代本 adapter smoke。CI=NOT_CONFIGURED；DeepSeek/UI/D4–D7 未实现或调用。

## 6. EXTERNAL_REVIEW 与收尾

待独立 reviewer 对固定实现提交复核，并在此追加实际结论与验证证据。

## 7. 已知限制与下一步

- 当前验证主体为 fake driver 契约与既有回归；真实 smoke 因配置缺失跳过。
  配置后须重跑 smoke，不以 mock PASS 宣称真实连接 PASS。
- 原图缺行级来源，共享模式的关系不能可靠归属案例；仅提供参考上下文，跨案例适用性未知。
- 有界词法检索无语义召回、别名库、全库最优排序、行级还原或知识写回。
- 10 秒事务超时需服务器执行；不提供进程级时间/内存沙箱，图在读取期间变化不形成永久快照。
- D4 接入生成时必须使用未排除 reference_hits，并保留原始检索审计；D5–D7 集成/报告/UI 留待后续。
- 正式 MVP-2/3 尚未单独验收，Demo D3 不改变 MVP-1 发布 tag 或包版本。

下一项开发任务：按既有 Plan 进入 Demo V1 / D4 DeepSeek 与生成校验；本会话止于 D3 收尾。
