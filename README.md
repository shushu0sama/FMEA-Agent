# FMEA Agent

可维护、证据可溯、MBSE 感知的 FMEA Agent。

**当前版本：MVP-0 Runnable Vertical Slice — 已完成（2026-09-04）**

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

## 当前不能做什么

- 不读取真实 SysML：OpenSysML / SysML Repository API **未接入**
- 不使用真实故障知识库：Neo4j / Qdrant **未接入**
- 不调用真实 LLM（默认路径不经过 `LLMClient`）
- 不计算真实 AIAG-VDA S/O/D/AP 风险等级
- 没有生产 UI、Human Review、Failure Propagation、Dynamic FMEA、
  多智能体编排

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

## 下一步 — MVP-1 Real System Facts

用真实系统事实替换 fixture：

```text
OpenSysML / SysML API
→ SysMLFactSnapshot
→ Canonical System Model
```

尚未开始；实现前需要先完成 MVP-1 的 spec/plan。

## Claude Code 每次新 Session 首先读取

1. `CLAUDE.md`
2. `PROGRESS.md`
3. 当前 Spec / Plan

## 本地 Claude Code 配置

`.claude/settings.local.json` 属于本机私有配置，不应提交到 Git，也不随本
项目包分发。请使用你的 Claude Code 全局配置或在本地重新创建该文件。

## 重要入口

- 长期架构原则：`docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md`
- 分阶段开发与复用：`docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md`
- FMEA 方法：`docs/domain/FMEA_PROFILE_V1.md`
- Canonical Model：`docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`
- Benchmark：`docs/evaluation/BENCHMARK_SPEC.md`
- 依赖清单：`docs/research/DEPENDENCY_INVENTORY.md`
- ADR：`docs/adr/`
