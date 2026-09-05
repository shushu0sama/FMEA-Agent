# MVP-0 — 可运行纵向切片收尾记录

状态： COMPLETE
日期： 2026-09-04（回填自 Git history + PROGRESS.md MVP-0 Completion Record）

## 1. 目标

> 在集成真实 SysML、KG/RAG 或 MCP 基础设施之前，使用本地夹具和可替换的
> 内存适配器，运行具有 FMEA 流程形态的端到端工作流。

## 2. 范围

范围内：

- 可安装的 Python 包
- 最小规范系统模型（Canonical System Model）+ FMEA 领域模型
- 证据与来源引用（Evidence / SourceReference）
- LangGraph 工作流骨架（七阶段形态）
- 内存系统模型 / 故障知识仓库
- mock LLM 端口（默认路径不使用）+ NoOpRiskStrategy
- CLI demo + JSON 结构化输出
- 单元测试 / 冒烟测试 / 验证脚本

范围外：

```text
OpenSysML / SysML Repository API
Neo4j / Qdrant / Docling / MCP
full AIAG-VDA S/O/D/AP rules
production UI
multi-agent system
dynamic FMEA
failure-propagation research algorithm
```

## 3. Git

Branch: `master`

起始 Commit： `8629248` chore: initialize repository with project docs and rules
（前序规划 commit `f09504c` docs: align MVP-0 architecture contracts）

实现 Commit：

- `5826eb6` feat: add MVP-0 domain and application contracts
- `18b60d6` feat: add MVP-0 in-memory adapters and workflow skeleton
- `f7abadd` feat: add MVP-0 demo fixtures, CLI and verification entry

最终 Commit： `f7abadd`（tag `v0.0.1`）

## 4. 交付内容

- `src/fmea_agent/domain/` — fmea.py（candidate 模型、EffectLevel、
  Evidence）、system_model.py（System/Component/Function/SourceReference）
- `src/fmea_agent/application/ports.py` — SystemModelRepository /
  FailureKnowledgeRepository / LLMClient / RiskStrategy
- `src/fmea_agent/adapters/inmemory/` — InMemorySystemModelRepository /
  InMemoryFailureKnowledgeRepository / MockLLMClient / NoOpRiskStrategy
- `src/fmea_agent/agents/workflow.py` + `workflow_state.py` —
  LangGraph 七阶段骨架（Risk=NOT_EVALUATED、Optimization=SKIPPED）
- `src/fmea_agent/cli/` + `__main__.py` —
  `python -m fmea_agent demo <fixture>`（--failure-library / --output）
- `examples/simple_pump.json` + `examples/demo_failure_library.json`
- `scripts/verify.py` — pytest + ruff + mypy 一键验证

## 5. 关键决策

- LangGraph 为编排基线（ADR-001）。
- Canonical System Model 为工程模型适配器与 FMEA 逻辑的边界（ADR-002）。
- System Model 与 Failure Model 分离（ADR-004）。
- AIAG-VDA 七步流程为 workflow shape（ADR-006）；不实现 S/O/D/AP 规则。
- Runnable Vertical Slice First（ADR-007）。

## 6. 证据

- 契约：`docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md`
- 计划：`docs/plans/MVP_0_IMPLEMENTATION_PLAN.md`
- 测试：tests/test_fmea.py / test_ports.py / test_system_model.py /
  test_inmemory_adapters.py / test_workflow.py / test_workflow_state.py /
  test_cli_loading.py / test_smoke_cli.py / test_package_imports.py

## 7. 验证

```text
pytest 79 passed                PASS（LOCAL，Windows）
ruff check .                    PASS（LOCAL）
mypy src                        PASS（LOCAL）
demo run                        PASS（python -m fmea_agent demo examples/simple_pump.json）
no external services            PASS（offline by construction）
risk.status == NOT_EVALUATED    PASS
optimization == SKIPPED         PASS
evidence traceable to fixture   PASS
```

CI：GitHub Actions NOT CONFIGURED（无 CI evidence）。

## 8. 开发中发现的问题

- 数据契约澄清（2026-09-04）：`FailureModeCandidate.item_id` /
  `function_id` 持稳定领域 ID（Component.id / Function.id），不是显示名；
  fixture failure knowledge 保持 name-keyed lookup，workflow 填充 ID。
- 无其他记录在案的 major RED。

## 9. 已知限制

- 系统事实来自 synthetic JSON fixture，不是真实 SysML。
- 无真实风险规则、无 Human Review、无 failure propagation。
- `Component.component_type` 等字段未填充。

## 10. 延后事项

全部后续 MVP（见 PROGRESS Next MVPs）：

```text
MVP-1 Real System Facts（OpenSysML File Mode）
MVP-2 Real Failure Knowledge
MVP-3 Evidence-grounded LLM
MVP-4 AIAG-VDA Risk & Semantic Validation
MVP-5 Human Review
MVP-6 Failure Propagation
MVP-7 Aerospace Benchmark
MVP-8 MCP
MVP-9 Dynamic FMEA
```

## 11. 涉及文件 / 契约

主要文件见 §4；完整 diff 见 commit `5826eb6` / `18b60d6` / `f7abadd`。

## 12. 最终评估

COMPLETE（v0.0.1 tagged；MVP-0 验收标准全部验证通过）

## 13. 下一阶段

MVP-1A OpenSysML Feasibility Spike。
进入条件：MVP-1 Spec / Plan / ADR-008 就绪。
