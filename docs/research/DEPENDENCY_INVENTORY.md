# Dependency Inventory v0.1

> This file tracks important external dependencies and research repositories.
> Exact versions/commits must be filled in when the dependency is actually integrated.

## Classification

Reuse:

```text
S = Self-build
W = Wrap
D = Direct reuse
R = Reference only
```

Maturity:

```text
STABLE
CANDIDATE
EXPERIMENTAL
WIP
DEFERRED
```

## Core Development Dependencies

| Project | URL | Role | Reuse | Maturity | Current decision |
|---|---|---|---|---|---|
| Pydantic | https://github.com/pydantic/pydantic | Domain/data contracts | D | STABLE | Use |
| pytest | https://github.com/pytest-dev/pytest | Testing | D | STABLE | Use |
| Ruff | https://github.com/astral-sh/ruff | Lint/format | D | STABLE | Use |
| mypy | https://github.com/python/mypy | Static type checking | D | STABLE | Use |
| LangGraph | https://github.com/langchain-ai/langgraph | Stateful workflow orchestration | D/W | STABLE/CANDIDATE | Baseline orchestrator |
| MCP Python SDK | https://github.com/modelcontextprotocol/python-sdk | MCP protocol | D | STABLE | Phase 8; do not reimplement |
| langchain-mcp-adapters | https://github.com/langchain-ai/langchain-mcp-adapters | Consume MCP from LangChain/LangGraph | D/W | CANDIDATE | Pin and contract-test when adopted |

## SysML / MBSE

| Project | URL | Role | Reuse | Maturity | Current decision |
|---|---|---|---|---|---|
| SysML-v2-Release | https://github.com/Systems-Modeling/SysML-v2-Release | Official models/examples/spec artifacts | D/R | STABLE/CANDIDATE | Benchmark/reference |
| SysML-v2-Pilot-Implementation | https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation | Reference implementation | R | CANDIDATE | Semantic cross-check |
| SysML-v2-API-Services | https://github.com/Systems-Modeling/SysML-v2-API-Services | Repository/REST access | D/W | CANDIDATE | Repository Mode |
| SysML-v2-API-Cookbook | https://github.com/Systems-Modeling/SysML-v2-API-Cookbook | API recipes | D/R | CANDIDATE | Reuse traversal patterns |
| OpenSysML | https://github.com/Open-MBEE/OpenSysML | `.sysml` runtime/parser/Python-gRPC integration | D/W | STABLE (pinned) | Active — MVP-1C File Mode adapter（record 见下） |
| SYSMOD SysML v2 | https://github.com/MBSE4U/sysmod-sysmlv2 | Delivery Drone/model examples | D/R | CANDIDATE | Benchmark |
| SYSMOD SysML v2 API/MCP | https://github.com/Open-MBEE/sysmod-sysmlv2-api | SysML API + MCP pattern | W/R | WIP | Architecture/MCP reference; do not bind core domain |
| SysML-v2 Applications and Examples | https://github.com/Open-MBEE/SysML-v2-Applications-and-Examples | CubeSat/spacecraft examples | D/R | CANDIDATE | Aerospace benchmark |

## Knowledge / Retrieval / Documents

| Project | URL | Role | Reuse | Maturity | Current decision |
|---|---|---|---|---|---|
| Neo4j Python Driver | https://github.com/neo4j/neo4j-python-driver | Graph persistence/query | D/W | STABLE | Graph-storage baseline |
| neosemantics | https://github.com/neo4j-labs/neosemantics | RDF/OWL/SKOS/SHACL bridge | D/W | CANDIDATE | Use when ontology integration needs it |
| RDFLib | https://github.com/RDFLib/rdflib | RDF/Turtle/SPARQL processing | D | STABLE | Utility |
| Qdrant | https://github.com/qdrant/qdrant | Vector retrieval | D/W | STABLE | Candidate; not required for MVP-0 |
| Docling | https://github.com/docling-project/docling | PDF/Office structured parsing | D/W | STABLE/CANDIDATE | Candidate; add when document ingestion is required |
| pandas | https://github.com/pandas-dev/pandas | Tabular FMEA processing | D | STABLE | Use when needed |
| openpyxl | https://openpyxl.readthedocs.io/ | Excel I/O | D | STABLE | Use; source repository is linked from official docs |

## MCP Implementations

| Project | URL | Role | Reuse | Maturity | Current decision |
|---|---|---|---|---|---|
| Official MCP Reference Servers | https://github.com/modelcontextprotocol/servers | MCP patterns/reference | D/R | STABLE/CANDIDATE | Reference |
| Neo4j MCP | https://github.com/neo4j/mcp | Generic graph MCP | D/W | CANDIDATE | Reuse rather than build generic Neo4j MCP |
| Neo4j Labs MCP | https://github.com/neo4j-contrib/mcp-neo4j | Experimental graph MCP examples | R | EXPERIMENTAL | Secondary reference |
| Qdrant MCP | https://github.com/qdrant/mcp-server-qdrant | Vector-search MCP | D/W | CANDIDATE | Reuse if MCP vector access needed |
| Docling MCP | https://github.com/docling-project/docling-mcp | Document-processing MCP | D/W | CANDIDATE | Reuse if agent-facing doc processing needed |
| SYSMOD SysML MCP | https://github.com/Open-MBEE/sysmod-sysmlv2-api | SysML/SYSMOD agent tools | W/R | WIP | Study/wrap; methodology-specific |

## Active Dependency Records (MVP-0, integrated 2026-09-04)

Locked by `uv.lock`. Build backend: hatchling (via `uv`).

| Package | Selected version | License | Role |
|---|---|---|---|
| pydantic | 2.13.5 | MIT | Domain/data contracts |
| pytest | 8.4.2 | MIT | Testing |
| ruff | 0.16.6 | MIT | Lint/format |
| mypy | 1.20.2 | MIT | Type checking |

## Active Dependency Record — OpenSysML (MVP-1C, integrated 2026-09-04)

Pin rationale and reproduction evidence:
`docs/research/OPENSYSML_SPIKE_REPORT.md`（1A）+
`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`（1C-0，PYPI_PIN_CONFIRMED）。

```text
Python client:  opensysml==0.4.0（PyPI wheel，精确 pin；Apache-2.0）
                wheel sha256 d3a9cfea481818656ec2f30f432c85ac74c41ab22adb51c5d9095c7cc1da3fca
                依赖集合与 Spike 记录一致（grpcio 1.83.1 / protobuf 7.36.1）

Runtime:        sysml-grpc v0.4.3 windows-amd64（非 Python dependency）
                GitHub release Open-MBEE/OpenSysML @ tag v0.4.3
                asset: sysml-grpc-windows-amd64.exe
                commit 99e02003c9c49358828b1c491a75de61745646ce
                sha256 0b188ec140872c0f93618602d5aa880daa864a84c00d4a8806cf97c80e8333fe

Adapter path:       src/fmea_agent/adapters/sysml/open_sysml_file.py
Contract test path: tests/test_open_sysml_file_adapter.py
Known limitations:
  - single-file subset；用户文件 import 不支持（C1，unresolved import 显式诊断）
  - Model.hash = load-context fingerprint（F1），非跨路径/跨版本稳定 identity
  - performed ActionUsage 无 typing facts（C4），禁止推断
  - runtime provisioning：本机缓存 ~/.opensysml/bin；备选 $OPENSYSML_BINARY /
    $OPENSYSML_GRPC_VERSION；client 0.4.0 digest 表只 pin 到 v0.3.0（自动下载回退）
Replacement option: sysml-grpc v0.3.0（digest 已在 client pin 表内，可自动校验下载）
Upgrade policy:    一次只升级一个 major integration；contract tests + MVP-0 regression
                   通过后才接受（见本文件 Upgrade Policy）

Upgrade policy: one dev-dependency major at a time; run `pytest` + `ruff check .` + `mypy src` before accepting.
```

## Reference Baseline — Existing Neo4j Failure Knowledge (Pre-MVP-2, 2026-09-04)

Detailed baseline:
`docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md`.

```text
Neo4j version: 5.26.0
Role:          existing Legacy Failure Knowledge Graph
MVP-2 status:  planning baseline only; future read-only adapter
Driver:        not installed in current project dependencies
Write-back:    out of scope for MVP-2
Security:      legacy importer is reference evidence only; do not copy secrets
               or run destructive import behavior against production
```

## Integration Record Template

When a dependency becomes active, fill:

```text
Selected version:
Selected commit:
License:
Adapter path:
Contract test path:
Known limitations:
Replacement option:
Upgrade policy:
```

## Upgrade Policy

For:

```text
OpenSysML
SysML API
LangGraph
MCP SDK
langchain-mcp-adapters
Neo4j
Qdrant
Docling
```

upgrade one major integration at a time:

```text
read changelog
→ upgrade branch
→ contract tests
→ regression benchmark
→ ADR if architecture changes
→ merge
```

Do not bulk-upgrade the entire stack.

## MCP Compatibility Note

The MCP ecosystem evolves quickly.
Always verify the exact SDK/protocol compatibility of:

```text
MCP Python SDK
LangChain MCP adapters
third-party MCP servers
```

at integration time and pin working versions.
