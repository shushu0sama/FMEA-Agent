# Demo V1 实施计划

> **For agentic workers:** 使用 `superpowers:executing-plans` 逐任务执行；如选择代理分工，使用
> `superpowers:subagent-driven-development`。本计划默认当前会话顺序执行，独立审核按项目规则开展。
> 复选框只在对应执行证据存在后更新；本文件不代替 Stage Record。

**Goal:** 跑通一个小型系统从 SysML/产品资料到有来源标记的候选 FMEA 报告的本机 Demo。

**Architecture:** 复用 OpenSysML/CSM 与领域模型，新增来源知识、输入、生成和报告服务。
LangGraph 负责明确的 Demo 状态转换；Streamlit 仅作为应用入口。旧 CLI 路径继续回归。

**Tech Stack:** Python >=3.11、已有 Pydantic/LangGraph/OpenSysML，optional extra `demo` 见下方精确版本。

**Spec:** [Demo V1 规格](../specs/DEMO_V1_END_TO_END_FMEA.md)。执行前同时读取 AGENTS、PROGRESS 和上一阶段记录。

Lifecycle: ACTIVE
Status: ACCEPTED（D0 独立计划审查）
Implementation: D1–D7 技术 ACCEPTED；人工工程质量 NOT_ACCEPTED
起点与本次准备证据：[D0 记录](../records/DEMO_V1/D0_SPEC_AND_PLAN.md)。

D0–D7 是 Demo V1 的内部工作步骤，保留原 MVP 能力路线；对应关系与收尾归入原则以
[Demo Spec 第 1.1 节](../specs/DEMO_V1_END_TO_END_FMEA.md#11-mvp-路线与-demo-步骤的对应关系)为准。
新会话使用 `Demo V1 / Dn` 标识任务，不把 Dn 当成 MVP-n，也不将其混同于 FMEA 方法七步法。

## 全局约束

- 首例 `hydraulicPump / motor / spin`；根动作 `pumpSpin` 明确排除。
- 一个 `.sysml` 必需，可选一个设计说明与一个 BOM；输入类型/资源上限严格执行 Spec §3。
- 中文 UI/文档；标识符/协议保持 canonical form。
- 固定 DeepSeek `deepseek-v4-pro`，现有 Neo4j `neo4j` 库只读；无凭据不静默切 mock。
- FACT、RETRIEVED_KNOWLEDGE、INFERENCE、UNKNOWN 的字段含义不可混淆；新报告始终 CANDIDATE。
- 不自动恢复原始行、不做评分/批准/知识写回/模型训练；报告风险 NOT_EVALUATED、优化 SKIPPED。
- `domain/` 不得引入 HTTP、Neo4j、LangGraph、Streamlit；端口中无提供方类型。
- `neo4j==5.28.2`、`httpx==0.28.1`、`pypdf==6.17.0`、`openpyxl==3.1.5`、`streamlit==1.63.0`。
- 每任务加其所需 optional dependency 并更新锁文件，不同时升级现有核心依赖。
- 正式执行另建单目标 `codex/` 分支/工作树，包含本次规划提交；不从旧 master 丢失规划上下文。

## 文件与接口地图

下列路径为计划新增，除标明“现有”外尚不存在；不得据此宣称已经实现。

| 路径（相对仓库） | 职责 | 阶段 |
|---|---|---|
| `examples/demo_v1/`、`scripts/build_demo_inputs.py` | 来源固定的演示资料与确定性生成 | D1 |
| `domain/demo_evidence.py`* | 字段证据、来源和文件结果 | D2 |
| `domain/demo_analysis.py`* | intake/报告/会话中立契约 | D2 |
| `application/demo_ports.py`* | 来源检索与模型统计的协议 | D2 |
| `adapters/documents/demo_inputs.py`* | SysML/BOM/PDF/文本载入 | D2 |
| `application/demo_intake.py`* | 目标验证、工况与冲突处理 | D2/D4 |
| `adapters/neo4j/failure_knowledge.py`* | 固定 Cypher、结果转换、只读连接 | D3 |
| `application/demo_retrieval.py`* | 查询词、排序与适用性展示规则 | D3 |
| `adapters/llm/deepseek.py`*、`application/demo_generation.py`* | HTTP 与生成校验分别实现 | D4 |
| `agents/demo_state.py`*、`agents/demo_workflow.py`* | 图状态及补问/生成流程 | D5 |
| `application/demo_service.py`* | UI 可调用的会话协调接口 | D5 |
| `adapters/reports/demo_report.py`* | JSON/HTML/CSV 导出 | D6 |
| `ui/demo_app.py`*、`application/demo_settings.py`* | 最小前端、配置与依赖装配 | D6 |
| `agents/workflow.py`*（现有） | 原结果导出补齐来源字段，保留旧字段 | D2 |
| `tests/test_demo_*.py`、`tests/fixtures/demo_v1/` | 分层契约与场景回归 | 各阶段 |
| `docs/records/DEMO_V1/Dn_*.md` | 当阶段实际工作与验证 | 各阶段 |

带 * 的路径以 `src/fmea_agent/` 为前缀。新包加入 `__init__.py`，遵守现有项目导入方式。

## D1 — 固定案例与演示资料（A01、A02）

**Files:** 新增 `examples/demo_v1/{system.sysml,bom.csv,design.md,manifest.json,README.md}`，
`scripts/build_demo_inputs.py`、`tests/test_demo_inputs_manifest.py`。
参考现有 `tests/fixtures/sysml/models/typed_inside_probe.sysml`、`tests/test_mvp1_benchmark.py`。
**Interface:** `build_demo_inputs(source: Path, destination: Path) -> dict[str, str]` 返回输出文件名到 SHA-256，
实现放在脚本，测试通过 `runpy.run_path` 获取函数；脚本入口只接受 `--source` 和 `--output`。

- [x] 先写下面的内容一致性测试，并运行 `python -m pytest tests/test_demo_inputs_manifest.py -q` 验证缺失实现导致失败。

```python
from pathlib import Path
import runpy

def test_pack_preserves_model_and_unknown_quantity(tmp_path):
    build = runpy.run_path("scripts/build_demo_inputs.py")["build_demo_inputs"]
    src = Path("tests/fixtures/sysml/models/typed_inside_probe.sysml")
    result = build(src, tmp_path)
    assert (tmp_path / "system.sysml").read_bytes() == src.read_bytes()
    assert "bom.csv" in result
    assert "motor" in (tmp_path / "bom.csv").read_text(encoding="utf-8")
    assert ",,UNKNOWN," in (tmp_path / "bom.csv").read_text(encoding="utf-8")
```

- [x] 生成器调用现有 adapter/mapper 获取真实部件，输出 CSV 表头按 Spec，quantity 空，unit 为 UNKNOWN。
  manifest 存来源路径（仓库相对）、hash、派生关系、CSM source IDs，禁止绝对路径作为可移植主键。
- [x] `design.md` 使用中文列出已知结构/动作及未知工况，声明“演示派生资料”；不填参数或原始失效答案。
  manifest 排除自己的 hash，不形成自引用；无时间戳参与内容，重复生成逐字一致。
- [x] 加入第二次生成字节相同、源 hash 不符时拒绝、source==output 不能覆盖原模型的测试。
- [x] 执行 `python scripts/build_demo_inputs.py --source tests/fixtures/sysml/models/typed_inside_probe.sysml --output examples/demo_v1`。
  用真实 adapter 重读 `system.sysml`；断言 system=hydraulicPump、motor/spin 可定位，pumpSpin 排除。
- [x] 运行目标测试及 `python scripts/verify.py`；记录 D1 来源/hash/真实 parser 证据并提交。

D1 执行与审核证据见 [D1 记录](../records/DEMO_V1/D1_FIXED_CASE_AND_INPUT_PACK.md)。

## D2 — 输入/证据契约与旧导出修复（A03、A08、A09 的基础）

**Files:** 地图中 D2 文件，`domain/demo_knowledge.py`、
`tests/test_demo_contracts.py`、`tests/test_demo_document_inputs.py`、`tests/test_demo_legacy_export.py`。
**Dependencies:** `uv add --optional demo pypdf==6.17.0 openpyxl==3.1.5`，检查只新增所需依赖。

**Interfaces:** 全部 Pydantic 模型 `extra="forbid"`；集合使用 default_factory。
以下为字段的完整最小清单，可用别名提高可读性，但下游名称不变：

```text
EvidenceRef:
  id:str, source_kind:Literal[sysml,document,bom,user,neo4j], locator:str,
  text:str, content_sha256:str|None, derived_from:list[str], limitations:list[str]
FieldValue:
  value:str|None, status:Literal[FACT,RETRIEVED_KNOWLEDGE,INFERENCE,UNKNOWN],
  evidence_ids:list[str], limitations:list[str]
InputFileRecord:
  id:str, filename:str, kind:Literal[sysml,document,bom], sha256:str,
  size_bytes:int, derived_from:list[str], parser:str|None,
  parser_version:str|None, runtime_version:str|None
LoadedInputs:
  files:list[InputFileRecord], model:CanonicalSystemModel, evidence:list[EvidenceRef],
  missing_files:list[str], conflicts:list[str], input_digest:str
IntakeResult:
  component_id:str|None, function_id:str|None, context:dict[str,FieldValue],
  questions:list[str], status:Literal[WAITING_INPUT,READY,BLOCKED]
KnowledgeQuery:
  terms:list[str], scope:Literal[SOURCE_LOOKUP,TARGET_ANALYSIS],
  component_id:str|None, function_id:str|None, limit:int=20
KnowledgeHit:
  id:str, name:str, context:list[EvidenceRef], associations:list[EvidenceRef],
  applicability:Literal[UNKNOWN,REJECTED,SOURCE_CONTEXT_ONLY], reasons:list[str]
RetrievalResult:
  status:Literal[HITS,NO_MATCH,ERROR], hits:list[KnowledgeHit],
  terms:list[str], truncated:bool, error_code:str|None
FailureRow:
  mode:FieldValue, causes:list[FieldValue], mechanism:FieldValue,
  effects:dict[Literal[LOCAL,NEXT_HIGHER_LEVEL,END_EFFECT],FieldValue],
  existing_controls:list[FieldValue], suggested_actions:list[FieldValue],
  validation_suggestions:list[str]
GenerationResult:
  rows:list[FailureRow], assumptions:list[str], missing_information:list[str]
CandidateReport:
  schema_version:Literal[demo-v1], run_id:str, input_digest:str,
  input_snapshot:LoadedInputs,
  status:Literal[CANDIDATE], component_id:str, function_id:str,
  context:dict[str,FieldValue], evidence:list[EvidenceRef],
  retrieval:RetrievalResult, generation:GenerationResult,
  exclusions:list[str], risk_status:Literal[NOT_EVALUATED],
  optimization_status:Literal[SKIPPED], usage:dict[str,int|str|None]
DiagnosticReport:
  schema_version:Literal[demo-v1-diagnostic], run_id:str, status:Literal[FAILED],
  input_snapshot:LoadedInputs, errors:list[str], usage:dict[str,int|str|None]
```

`demo_evidence.py` 放 EvidenceRef/FieldValue/InputFileRecord/LoadedInputs；
`demo_knowledge.py` 放 KnowledgeQuery/Hit/RetrievalResult；其余放 `demo_analysis.py`。
InputFileRecord 的 filename 为用户文件名而非本机绝对路径；model.source_refs 在可导出副本中用
文件记录 ID/原始元素 ID 关联，保留原始引用语义；loaded运行上下文中的绝对路径不作为永久身份。
CandidateReport.input_snapshot 包含完整结构/功能/来源及冲突，导出时不得另访问会话文件；
report.input_digest 必须与其快照一致，report.evidence 包含输入证据加允许展示的图证据。
无默认 FACT/APPROVED；value=None 必须 UNKNOWN，FACT/RETRIEVED 必须有 evidence_ids。
引用必须属于 registry、无重复 evidence ID、effects 三层均存在；UNKNOWN 层可空。
`HITS` 必须有 hits，`NO_MATCH` 必须空且无 error_code，`ERROR` 必须有 error_code 且无 hits；
KnowledgeQuery 限制 1–5 非空词、80 字符/词、1–20 limit；SOURCE_LOOKUP 不能宣称目标适用。

```python
from pydantic import ValidationError
import pytest
from fmea_agent.domain.demo_evidence import FieldValue
from fmea_agent.domain.demo_knowledge import RetrievalResult

def test_fact_requires_evidence():
    with pytest.raises(ValidationError):
        FieldValue(value="rated speed", status="FACT", evidence_ids=[], limitations=[])

def test_empty_hit_result_is_invalid():
    with pytest.raises(ValidationError):
        RetrievalResult(status="HITS", hits=[], terms=["motor"], truncated=False, error_code=None)
```

- [x] 写字段/状态/引用负例，运行 `python -m pytest tests/test_demo_contracts.py -q` 看失败，再实现 validators。
- [x] `load_inputs(sysml_path: Path, design_path: Path|None, bom_path: Path|None) -> LoadedInputs`：
  复用 SysML adapter，partial 拒绝；文本逐行定位，PDF 用 pypdf 逐页提取，空页/扫描件给明确错误；
  XLSX 用 openpyxl `read_only=True,data_only=False` 检测 formula；CSV 用 stdlib csv，拒绝缺列/重复 item_id。
  source_element_id 只映射已存在模型元素；BOM 名称不一致保留冲突，不用名字覆盖 CSM。
- [x] 文件载入抛 `DemoInputError(code: str, message: str)`，code 限定
  UNSUPPORTED_FORMAT / LIMIT_EXCEEDED / NO_TEXT / ENCRYPTED / INVALID_BOM / PARTIAL_MODEL / INVALID_MODEL。
- [x] 添加入参越界、超量、伪扩展名、公式、未知引用、独立资料误配、用户路径穿越测试。
  无文件保存副作用的 loader 只读；UI 保存路径检查在 D6 另测。
- [x] 修复现有 `results_documentation` 的输出，保留现有键并新增 item/function ID、source_refs、
  模式的 item_id/function_id 关联、cause mechanism/evidence、effect status/evidence/affected_item_id。
  现有 FailureModeCandidate 没有自身 id，本次不新增其自身 ID。
  `tests/test_demo_legacy_export.py` 构建带嵌套来源的候选，经原图执行后逐字段比对，不能只测新 serializer。
- [x] 运行 D2 测试、全套 `python scripts/verify.py` 和 B0/B1；审查/记录 D2 并提交。

D2 执行证据与实现细化见 [D2 记录](../records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)。
独立复审已接受 D2；GitHub TLS 连接失败在最终重试时恢复，实施及审核记录已推送。

## D3 — 可独立验证的只读检索（A05、A06）

**Files:** D3 文件、`application/demo_ports.py`、`tests/test_demo_retrieval.py`、
`tests/test_demo_neo4j_contract.py`、`scripts/demo_neo4j_smoke.py`。
**Dependency:** `uv add --optional demo neo4j==5.28.2`。
**Interfaces:** `SourceKnowledgeRepository.search(query: KnowledgeQuery) -> RetrievalResult`；
`prepare_query(inputs: LoadedInputs, intake: IntakeResult, terms: list[str]) -> KnowledgeQuery`；
`Neo4jSourceKnowledgeRepository(driver, database: str)` 只在适配器内接受 driver。

- [x] 先用假的 driver/session 返回固定 records，测试同模式的两条起因和两条影响仍为四条独立关系证据，
  不能变四条原始 FMEA 行；测试 scope/NO_MATCH/ERROR/多关注要素/截断。
- [x] 实现固定模板。入口模式候选查询结构如下；实际 code 使用常量模板并为补充上下文分别查询：

```cypher
MATCH (focus:`关注要素层次`)-[:`故障模式`]->(mode:`故障模式`)
WHERE any(term IN $terms WHERE toLower(focus.name) CONTAINS toLower(term)
                           OR toLower(mode.name) CONTAINS toLower(term))
RETURN DISTINCT elementId(mode) AS mode_id, mode.name AS mode_name
ORDER BY mode_name, mode_id LIMIT $fetch_limit
```

  另一个固定入口从 focus 的 `功能` 或 `下一低分析层次`/`下一低层次功能` 路径匹配 name，再取 mode；
  两组结果汇总、精确名称优先、按 name/id 排序，取 limit+1 检测截断；上限内有界结果可不保证全库最优排名，
  报告注明有界词法检索。不要把截断结果描述为完整召回。
  按选中 mode IDs 获取 `(mode)-[edge]->(target)` 的四类固定关系及 focus 来源关联；
  一条 edge 产生一个 EvidenceRef，locator 含库名、节点/关系 elementId、检索时间（报告元数据）。
- [x] 值只作为参数；query文本不含用户/模型字符串。fake driver 断言只出现登记模板，
  不运行 APOC/write/schema 命令；控制连接/查询超时为 10 秒、禁用无限事务重试。
- [x] SOURCE_LOOKUP 命中仅 SOURCE_CONTEXT_ONLY；TARGET_ANALYSIS 命中默认 UNKNOWN。
  明确用户排除的词/对象记录 REJECTED 并不传给生成器；无跨案例自动批准路径。
- [x] 读取进程 `NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD/NEO4J_DATABASE`，后者默认 neo4j；
  未配返回 CONFIG_MISSING，认证/超时分别 AUTH_FAILED/TIMEOUT，均是 ERROR，不能空列表假装成功。
- [x] `demo_neo4j_smoke.py` 从实际图读一条关注要素名称再用 SOURCE_LOOKUP 查回，记录存在性与定位；
  随机不存在标识测无结果；只输出计数/状态，不打印密钥/全量工程正文。未配置明确 skip reason。
- [x] 运行 D3 契约、完整验证，保留本机 smoke 的真实状态；记录 D3，不写入原图或提交私有记录。

D3 实际验证及资源/排除接口细化见 [D3 记录](../records/DEMO_V1/D3_READONLY_NEO4J_RETRIEVAL.md)。
D3 最初真实 smoke 因 CONFIG_MISSING 跳过；用户配置后最新真实验证已 PASS，见 D3 第 8 节。
首审提出的 smoke 子 logger 脱敏问题已修复，独立复审 `059b6ee` ACCEPTED；真实演化见 D3 记录。

## D4 — DeepSeek 与生成校验（A04、A07、A08）

**Files:** D4 文件、`tests/test_demo_deepseek.py`、`tests/test_demo_generation.py`、
`scripts/demo_model_smoke.py`。
**Dependency:** `uv add --optional demo httpx==0.28.1`（固定已锁版本）。
**Interfaces:** `DeepSeekLLMClient(api_key: str, http_client: httpx.Client|None=None)` 实现现有 LLMClient。
`DemoLLMClient` Protocol 扩展 `generate(prompt: str)->str` 与 `usage()->dict[str,int|str|None]`；
每会话创建独立 client，累积请求预算/usage，不记录密钥或原始响应错误正文。
`parse_intake(raw: str, inputs: LoadedInputs) -> IntakeResult`；
`validate_generation(raw: str, allowed_evidence: list[EvidenceRef]) -> GenerationResult`。

- [x] 用 HTTPX MockTransport 写成功、401、429一次重试、超时、空 content、finish_reason=length、非法 JSON 测试。
  最小 transport 契约：

```python
import httpx
from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient

def test_provider_uses_json_mode():
    import json
    def reply(request):
        body = json.loads(request.content)
        assert body["model"] == "deepseek-v4-pro"
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop",
            "message": {"content": '{"rows": []}'}}]})
    http = httpx.Client(transport=httpx.MockTransport(reply))
    client = DeepSeekLLMClient(api_key="test-token", http_client=http)
    assert client.generate("Return json") == '{"rows": []}'
```

- [x] 请求 body 按 Spec §6。用 `httpx.Timeout(60.0, connect=10.0)`；该设置为读/连接阶段超时，
  不是整个会话时限。单次非流式响应大小限制 1 MiB，超过报 INVALID_RESPONSE。
  API 原始错误转安全 code，不把 Authorization/header/输入资料输出到 UI/log。
- [x] 只在 429/502/503/504 重试一次，delay 最多 2 秒；认证/不合法输出直接报错。
  第 7 次请求报 CALL_BUDGET_EXCEEDED，防 UI rerun 的幂等由 D5 控制。
- [x] intake prompt 输入实际 component/function ID 清单，输出必须属于该清单；不能修改 CSM。
  模型从文档提出的 FACT 字段必须有原文引用和精确子串校验；校验失败转为待确认，不标 FACT。
  用户补充记录为 user EvidenceRef，不自动当成审核知识。
- [x] analysis prompt 限定 context/evidence ID 列表与目标，要求 GenerationResult JSON；
  每次最多 8 个候选模式，UNKNOWN 层空值允许，所有新增字段 INFERENCE。
  对既有控制 FACT 需要精确原文及已有证据；拒绝额外 score/AP/approved 字段。
  不接受带不存在引用的结果；不做无限二次“修复”调用。
- [x] mock 场景分别验证：无匹配仍生成 INFERENCE、有相关历史仅作参考、REJECTED 不进 prompt、
  图故障保留错误、恶意文件指令不能生成工具执行、重复候选不静默丢来源。
- [x] `demo_model_smoke.py` 只用公开项目演示数据，首测通用 JSON响应，再测1个目标的完整 schema。
  key 从 DEEPSEEK_API_KEY 读取；未配置明确未验证，不切别的模型；记录模型标识/时间/token计数。
- [x] 运行目标测试和完整验证；记录 D4 是否仅 mock PASS 或另有真实 API PASS；提交。

D4 实际验证及实施细化见 [D4 记录](../records/DEMO_V1/D4_DEEPSEEK_AND_GENERATION_VALIDATION.md)。
真实 DeepSeek smoke 因 CONFIG_MISSING 跳过；勾选代表已执行检查，不表示真实 API 通过。首审 HTTP 原生日志问题已修复，独立复审 `dafbe82` ACCEPTED；真实演化见 D4 记录。

## D5 — 可补问、可恢复的受控工作流（A04、A07、A10）

**Files:** D5 文件、`tests/test_demo_workflow.py`、`tests/test_demo_service.py`。
**Interfaces:** `DemoSession` 在 `agents/demo_state.py` 定义：

```text
id:str, input_digest:str, phase:Literal[NEW,WAITING_INPUT,READY,RUNNING,COMPLETE,FAILED],
inputs:LoadedInputs, intake:IntakeResult|None, retrieval:RetrievalResult|None,
generation:GenerationResult|None, report:CandidateReport|None, diagnostic:DiagnosticReport|None,
question_rounds:int, handled_request_ids:list[str], errors:list[str]
DemoService(knowledge_repo:SourceKnowledgeRepository, llm:DemoLLMClient)
start(inputs:LoadedInputs, message:str, request_id:str) -> DemoSession
answer(session:DemoSession, message:str, request_id:str, continue_unknown:bool=False) -> DemoSession
analyze(session:DemoSession, request_id:str, allow_without_retrieval:bool=False) -> DemoSession
```

- [x] 用实现 `generate/usage` 的顺序 fake client，准备 intake 与 generation JSON；
  先测 WAITING_INPUT 不调用检索、同 request_id 重提不增加调用次数，再写图实现。
- [x] LangGraph 节点 `intake -> needs_input? -> retrieve -> generate -> document`；
  WAITING_INPUT 以类型化状态结束该次 invoke，answer 后从 intake/ready 恢复，不保存长运行阻塞等待。
  CLOSED 的 HTTP/Neo4j 连接不放入 state；服务持有适配器，state 只放中立数据。
- [x] 2轮补问后未知保持问题清单，用户选择 continue_unknown 时允许按缺失事实生成；
  CSM冲突/partial/不存在ID始终BLOCKED。retrieval ERROR 需显式 allow_without_retrieval 才能降级，且报告保留ERROR。
- [x] 失效生成/验证失败时 phase=FAILED，构建DiagnosticReport保存输入快照/安全错误和usage，
  report=None，可导出诊断摘要，不输出“成功 FMEA”；
  完成但无候选时显示“未生成候选”，不宣称系统无失效。
- [x] 文件 input_digest 变化后要求新session；预算和已有处理 request ID 不跨会话复用。
  空回答不生成新事实，取消/重试后不得重复提交分析副作用。
- [x] 运行 D5 场景及原 workflow/CLI/benchmark；确认原 `build_workflow_graph` 行为除D2附加字段外一致。
  写 D5 记录并提交。

D5 当前实现与接口细化见 [D5 记录](../records/DEMO_V1/D5_CONTROLLED_WORKFLOW.md)。
LOCAL 498 项测试/Ruff/mypy 通过；真实 DeepSeek 公开资料补问/恢复 smoke 通过，检索为显式 fake。
独立审核 `c9878bb` ACCEPTED，未解决发现为 0；EXTERNAL_REVIEW 498 项测试及 12 组边界探查通过。
该结论不代表真实图与模型完整集成或 D7 验收，详细范围及 Git 演化保留在 D5 记录。

## D6 — 报告与本机 UI（A09、A10、A12）

**Files:** D6 文件、`tests/test_demo_reports.py`、`tests/test_demo_ui.py`、
`tests/test_demo_settings.py`、`docs/product/DEMO_V1_USER_GUIDE.md`。
**Dependency:** `uv add --optional demo streamlit==1.63.0`。
**Interfaces:** `export_report(report: CandidateReport, format: Literal[json,html,csv]) -> bytes`；
`export_diagnostics(report: DiagnosticReport, format: Literal[json,html]) -> bytes`，
失败诊断标题与schema明确区分成功候选报告，失败时不开放候选CSV下载；
`load_demo_settings() -> DemoSettings` 包含 model/Neo4j 参数和显式 `mode: Literal[live,mock]`，
密钥采用 SecretStr，repr/异常不得有值；默认 live，缺少配置显示缺失项。
`create_demo_service(settings: DemoSettings) -> DemoService` 位于 settings 模块做装配；
UI 的 `main()` 在 import 时不做模型/图调用，启动脚本位于地图指定路径。

- [x] 先为完整证据往返、HTML转义、CSV公式前缀、中文编码、三层影响UNKNOWN写测试。
  CandidateReport JSON序列化/反序列化后清除原session，只用恢复后的对象导出HTML/CSV，
  核对文件名/hash/parser/runtime、系统结构、资料关联、冲突和证据均保留。
  DiagnosticReport单独往返后导出失败诊断，断言标题不含成功状态且没有候选表。
  exporter 保留字段级 provenance；CSV至少列 mode/cause/effect/actions/status/evidence_ids/limitations，
  多值以换行显示，不用笛卡尔积生成新分析行。
- [x] HTML使用 stdlib html.escape，自包含样式，完整报告章节按Spec；不允许未转义外部文本。
  新增现有控制与建议措施不同列、风险未评估说明、原始引用详情。
- [x] Streamlit四区：上传、摘要/补问、候选表/证据、下载。通过 `st.session_state` 保存 DemoSession 和服务；
  调用只由 submit 按钮触发，以 request_id 控制；重绘/下载不调用模型。
  文件名仅显示，存盘用随机安全名；5 MiB等限制在应用层再次检查，避免只靠扩展名控件。
- [x] AppTest 用显式mock设置运行，测试无文件提示、加载演示包、补问及continue_unknown、
  生成失败显示、报告下载准备；文件上传控件不支持自动操作的部分在浏览器复核，不能假称 AppTest覆盖。
- [x] 在本机用以下规划命令启动，并用浏览器实际操作完整流程和下载：

```powershell
uv sync --extra demo
uv run --extra demo streamlit run src/fmea_agent/ui/demo_app.py --server.address 127.0.0.1
```

- [x] 验证页面无私钥/堆栈，原始输入与生成内容转义；doc-only上传提示需要SysML；
  断开图时显示失败，不能用预填文本冒充实时成功。
- [x] 更新用户指南：启动、支持格式/限制、mock/live区别、报告意义和环境变量名（无值）。
  全套验证，记录 D6 并提交。

D6 执行证据见 [D6 记录](../records/DEMO_V1/D6_REPORTS_AND_LOCAL_UI.md)。
当前 D6 ACCEPTED（独立复审基线 `4ead6fc`）；AppTest 1.63.0 实际支持上传，
浏览器另验证实际保存与视觉行为；D7 状态见下方。

## D7 — 集成验收与演示交付（A01–A12）

**Files:** `tests/test_demo_e2e.py`、`docs/evaluation/DEMO_V1_ACCEPTANCE_REPORT.md`、
`docs/records/DEMO_V1/D7_DEMO_RELEASE.md`、PROGRESS、README、依赖清单。

- [x] 建立3条独立端到端场景：真实SysML+mock模型/图的确定性成功，真实图来源查回，
  真实SysML+真实DeepSeek的无可用知识参考推断。人工关键结论抽查另记录，不混成自动化gold。
- [x] 输入副本改名/改路径只验证身份与hash边界，不当作独立案例泛化。
  保留空来源、错误引用、无结果和连接故障的集成回归；不要求生成文本逐字相同。
- [x] 执行 `python scripts/verify.py`、`uv lock --check --offline`、Demo全套、B0/B1、两个live smoke，
  在验收矩阵中逐项登记 LOCAL / EXTERNAL_REVIEW，未运行不填PASS。
- [x] 独立审查者从用户入口运行/核对报告、无匹配和故障，所有IMPORTANT问题修复后复验。
- [x] 分开报告“技术演示状态”和“人工工程质量状态”；无人工抽查时后者未验收，
  无真实接口配置时前者仅离线演示，不称真实端到端通过。
- [x] 更新真实能力、已知限制、启动命令、实际依赖许可证与 lock；仅对Demo创建收尾，
  不移动 MVP-1 tag，不自动宣称 MVP-2/3/5已发布。
- [x] 在同一验收报告中列出 MVP-2/3 已实现能力、对应代码/测试证据、已知限制与正式验收差距；
  后续依当期正式 MVP Spec 复用、补齐和独立验收，不另起重复实现，不把 D7 当成 MVP-7。

D7 当前技术 ACCEPTED（独立审核 f550a0d，0 未解决发现）；LOCAL 与真实场景证据见[验收报告](../evaluation/DEMO_V1_ACCEPTANCE_REPORT.md)，
独立最终审查与提交推送见[D7 记录](../records/DEMO_V1/D7_DEMO_RELEASE.md)。工程质量 NOT_ACCEPTED。

## D7 后修复 — UX1 用户流程（A10）

这是用户试用后的新增有限修复，不回写 D7 计划为已预先包含 UX1。
依据 Spec §7.1 和用户批准的第一批设计，在包含 D7 最终提交的当前 checkout 建立单目标分支。

1. 先增加用户入口回归：阶段提示、空白提交、未知继续、故障明确降级、输入拒绝及异常恢复。
2. 仅调整现有 UI；复用 D2 loader、D5 service、D6 exporter/Streamlit，不更换解析器或运行时。
3. 运行 UI/E2E、全套 verify、离线 lock、B0/B1，并以独立浏览器会话验证实际操作。
4. 独立审核并修复发现后，记录技术修复状态；用户使用验收和工程质量验收单独保留。
5. 更新指南、导航和 PROGRESS，提交推送，不合并 master 或移动发布 tag。

执行证据和当前状态见 [UX1 记录](../records/DEMO_V1/UX1_USER_FLOW_FIX.md)。

## 排期与交接

D1–D2 是输入与证据基础；D3/D4 可在接口稳定后各自验证；D5依赖二者；D6依赖D5；D7最终集成。
约一周目标只用于控制范围，不分配未经验证的精确工时。配置缺失时先完成确定性测试，
但live验证不以mock替代；不要为了赶日期扩展复杂模型或取消错误/来源检查。

自审：Spec §2→D1；§3→D2/D5/D6；§4→D2/D6；§5→D3；§6→D4；§7→D5/D6；
§8→逐阶段依赖/锁文件；§9→D7。D0 时所有实现阶段均未执行；实际执行状态以上方
Implementation、PROGRESS 和各阶段记录为准，不将本段规划自审当作当前完成证据。
