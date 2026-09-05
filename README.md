# FMEA Agent

可维护、证据可溯、MBSE 感知的 FMEA Agent。

**当前版本：MVP-1 Real System Facts — RELEASED（当前稳定发布 tag： v0.1.1，2026-09-04）**
（v0.1.0 = 原始 MVP-1 能力发布；v0.1.1 = 发布后的文档一致性补丁，无能力变化。
MVP-0 Runnable Vertical Slice 已完成并作为回归基线保留）

## 当前能做什么

MVP-0 已跑通一个 AIAG-VDA 七阶段形态的端到端可执行工作流：

```text
Input Fixture
  → Planning & Preparation
  → Structure Analysis
  → Function Analysis
  → Failure Analysis
  → Risk Analysis (NOT_EVALUATED)
  → Optimization (SKIPPED)
  → Results Documentation
  → Structured Candidate Output
```

- 使用 JSON fixture + in-memory repositories + LangGraph 骨架，全流程离线，
  不需要网络、SysML server、Neo4j、向量库、外部 LLM 或 MCP
- 输出结构化 JSON（非自由文本）：`analysis_id` / `method` / `item` /
  `function` / `failure_modes` / `risk` / `stage_status`
- Risk 明确输出 `NOT_EVALUATED`，不编造 S/O/D/AP 值
- Optimization 明确输出 `SKIPPED`
- 每个候选带 Evidence，指向 demo fixture（`demo-failure-library:001`）
- 候选 `item_id` / `function_id` 使用稳定领域 ID，绝不使用显示名
- 领域模型不依赖 LangGraph / Neo4j / LLM provider；外部技术全部位于
  ports/adapters 之后

MVP-1 已把系统事实来源替换为真实 SysML v2：

```text
真实 .sysml
→ OpenSysML（opensysml==0.4.0 + sysml-grpc v0.4.3，File Mode）
→ SysMLFactSnapshot（parser-neutral contracts）
→ Canonical System Model（System / Component / Function / SourceReference）
→ CanonicalSystemModelRepository
→ 现有 LangGraph Workflow
```

- 显式 root-selection policy；多候选 root 报错并列出候选
- 不静默丢弃任何元素：未映射元素产出 `MappingNotice`
- Function 分配基于真实 owner traversal 证据（禁止 name/FQN 匹配）
- B0/B1 benchmark 通过（`docs/evaluation/MVP_1_BENCHMARK_REPORT.md`）

Demo V1 已具备固定资料包及 D2 输入基础（当前审核状态见 PROGRESS）：

- [固定案例包](examples/demo_v1/README.md)：SysML 原样副本、BOM、中文设计说明和来源清单。
- 只读载入一个 SysML、可选设计说明（MD/TXT/文本 PDF）与 BOM（CSV/XLSX 的 BOM 表）。
  保留文件 hash、行/页/模型元素定位、冲突与缺失项；不把文档断言自动提升为模型事实。
- 新增严格输入/证据/候选及失败诊断契约，可脱离文件会话进行 JSON 往返。
- 原 CLI JSON 补齐 item/function ID、source_refs，以及候选起因机理/证据和影响状态/证据。
  原字段名称和值保留；这些新增字段不是完整 Demo 报告导出或工程批准。

安装 D2 可选文件解析依赖，并在 Python 中载入固定资料：

```bash
uv sync --extra demo
uv run --extra demo python scripts/verify.py
```

```python
from pathlib import Path
from fmea_agent.adapters.documents.demo_inputs import load_inputs

inputs = load_inputs(
    Path("examples/demo_v1/system.sysml"),
    Path("examples/demo_v1/design.md"),
    Path("examples/demo_v1/bom.csv"),
)
print(inputs.input_digest, inputs.missing_files, inputs.conflicts)
```

每文件 5 MiB、PDF 20 页、BOM 200 数据行、所有输入提取文本合计 30,000 字符；
XLSX 总展开大小上限 25 MiB，BOM 表扫描最多 10,000 物理行、64 列（含空白间隔）。
超限、公式、加密/损坏文件、无文本 PDF、partial 模型或无合法目标明确拒绝。
loader 不保存文件或执行链接；UI 上传存储与模型交互尚未实现。

## 当前不能做什么

- 不读取多文件 / import 模型（单文件子集，unresolved import 显式诊断）
- 不使用真实故障知识库：Neo4j / Qdrant **未接入**
- 不调用真实 LLM（默认路径不经过 `LLMClient`）
- 不计算真实 AIAG-VDA S/O/D/AP 风险等级
- 没有生产 UI、Human Review、Failure Propagation、Dynamic FMEA、
  多智能体编排、SysML Repository API

## 如何运行 Demo

环境要求：Python >= 3.11；安装项目依赖（uv 或 pip）。

```bash
python -m fmea_agent demo examples/simple_pump.json
```

可选参数：

```bash
# 输出写入文件而不是 stdout
python -m fmea_agent demo examples/simple_pump.json --output out.json

# 指定 failure library（默认取 fixture 同目录下的 demo_failure_library.json）
python -m fmea_agent demo examples/simple_pump.json \
    --failure-library examples/demo_failure_library.json
```

无效输入（文件缺失 / JSON 非法 / 缺必需字段）会输出错误并返回非零退出码。

## 如何运行测试与验证

```bash
pytest

# 或者一次性执行全部检查（pytest + ruff + mypy，跨平台）
python scripts/verify.py
```

## 下一步

MVP-1 已 **RELEASED**：

```text
Independent Release Review ACCEPTED（review baseline 369f09d）
→ merge master（2871b23c，--no-ff）
→ master verification（PASS，LOCAL）
→ final release closeout
→ annotated tag v0.1.0（original capability release）

Post-Release Audit（唯一发现：benchmark report 两处 current-state
drift）→ docs-only patch → Independent Patch Review ACCEPTED
→ annotated tag v0.1.1（current stable patch；无 capability 变化）
```

下一步：按已同意方向推进 Demo V1，从现有 SysML 派生演示资料，接入只读知识检索、DeepSeek 和最小 UI/候选报告。
已实现输入资料与契约基础；真实知识检索、LLM、UI 和完整候选报告尚未接入。
MVP-1 稳定发布 tag 不变，当前开发阶段以 PROGRESS 和阶段记录为准。

- [Demo 规格](docs/specs/DEMO_V1_END_TO_END_FMEA.md)
- [Demo 实施计划](docs/plans/DEMO_V1_IMPLEMENTATION_PLAN.md)
- [D0 记录](docs/records/DEMO_V1/D0_SPEC_AND_PLAN.md)
- [D2 记录](docs/records/DEMO_V1/D2_INPUT_EVIDENCE_AND_LEGACY_EXPORT.md)

当前阶段以 [PROGRESS.md](PROGRESS.md) 为准；[信息对齐](docs/product/MVP_2_PREPLANNING_ALIGNMENT.md)
保留历史问答。SysML 与 Neo4j 案例独立，不强行配对。

尚未实现（MVP-1 明确延后，不宣传为已有能力）：

```text
Neo4j / RAG / real LLM / AIAG-VDA real S/O/D/AP
MCP / Human Review / Failure Propagation / Dynamic FMEA
```

发布状态与历史：

```text
docs/records/MVP_1/MVP_1_RELEASE.md
docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md
docs/records/MVP_1/MVP_1_POST_RELEASE_PATCH.md（v0.1.1 docs patch release）
```

## 每次新 Session 首先读取

1. `AGENTS.md`（规范入口）/ `CLAUDE.md`（Claude Code 兼容入口）
2. `PROGRESS.md`
3. `docs/README.md`
4. 当前 Spec / Plan（存在时）/ 上一阶段记录（`docs/records/`）

## 本地 Claude Code 配置

`.claude/settings.local.json` 属于本机私有配置，不应提交到 Git，也不随本
项目包分发。请使用你的 Claude Code 全局配置或在本地重新创建该文件。

## 重要入口

- 文档导航：`docs/README.md`
- V1 产品边界：`docs/product/FMEA_AGENT_V1.md`
- V1 架构边界：`docs/architecture/FMEA_AGENT_V1_ARCHITECTURE.md`
- MVP-2 Spec：`docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md`
- Neo4j baseline：`docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md`
- 长期架构原则（REFERENCE）：`docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md`
- 分阶段开发与复用（REFERENCE）：`docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md`
- FMEA 方法：`docs/domain/FMEA_PROFILE_V1.md`
- Canonical Model：`docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`
- Benchmark：`docs/evaluation/BENCHMARK_SPEC.md`
- 依赖清单：`docs/research/DEPENDENCY_INVENTORY.md`
- ADR：`docs/adr/`
- 治理规则：`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`
- 执行历史：`docs/records/`
