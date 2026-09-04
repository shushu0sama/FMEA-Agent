# MVP-0 — Runnable Vertical Slice Closeout Record

Status: COMPLETE
Date: 2026-09-04（回填自 Git history + PROGRESS.md MVP-0 Completion Record）

## 1. Objective

> Run an end-to-end FMEA-shaped workflow using local fixtures and replaceable
> in-memory adapters before integrating real SysML, KG/RAG or MCP
> infrastructure.

## 2. Scope

In Scope:

- installable Python package
- minimal Canonical System Model + FMEA Domain Model
- Evidence / SourceReference
- LangGraph workflow skeleton（七阶段形态）
- in-memory system / failure-knowledge repositories
- mock LLM port（默认路径不使用）+ NoOpRiskStrategy
- CLI demo + JSON 结构化输出
- unit tests / smoke tests / verification script

Out of Scope:

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

Start Commit: `8629248` chore: initialize repository with project docs and rules
（前序规划 commit `f09504c` docs: align MVP-0 architecture contracts）

Implementation Commit(s):

- `5826eb6` feat: add MVP-0 domain and application contracts
- `18b60d6` feat: add MVP-0 in-memory adapters and workflow skeleton
- `f7abadd` feat: add MVP-0 demo fixtures, CLI and verification entry

Final Commit: `f7abadd`（tag `v0.0.1`）

## 4. Delivered

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

## 5. Key Decisions

- LangGraph 为编排基线（ADR-001）。
- Canonical System Model 为工程模型适配器与 FMEA 逻辑的边界（ADR-002）。
- System Model 与 Failure Model 分离（ADR-004）。
- AIAG-VDA 七步流程为 workflow shape（ADR-006）；不实现 S/O/D/AP 规则。
- Runnable Vertical Slice First（ADR-007）。

## 6. Evidence

- 契约：`docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md`
- 计划：`docs/plans/MVP_0_IMPLEMENTATION_PLAN.md`
- 测试：tests/test_fmea.py / test_ports.py / test_system_model.py /
  test_inmemory_adapters.py / test_workflow.py / test_workflow_state.py /
  test_cli_loading.py / test_smoke_cli.py / test_package_imports.py

## 7. Verification

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

## 8. Problems Found During Development

- 数据契约澄清（2026-09-04）：`FailureModeCandidate.item_id` /
  `function_id` 持稳定领域 ID（Component.id / Function.id），不是显示名；
  fixture failure knowledge 保持 name-keyed lookup，workflow 填充 ID。
- 无其他记录在案的 major RED。

## 9. Known Limitations

- 系统事实来自 synthetic JSON fixture，不是真实 SysML。
- 无真实风险规则、无 Human Review、无 failure propagation。
- `Component.component_type` 等字段未填充。

## 10. Deferred

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

## 11. Files / Contracts Affected

主要文件见 §4；完整 diff 见 commit `5826eb6` / `18b60d6` / `f7abadd`。

## 12. Final Assessment

COMPLETE（v0.0.1 tagged；MVP-0 acceptance criteria 全部验证通过）

## 13. Next Stage

MVP-1A OpenSysML Feasibility Spike。
进入条件：MVP-1 Spec / Plan / ADR-008 就绪。
