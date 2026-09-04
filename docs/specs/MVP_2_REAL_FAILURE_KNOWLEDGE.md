# MVP-2 Specification — Real Failure Knowledge

Status: ACTIVE SPEC / PLANNING ONLY

## 1. Goal

Replace MVP-0 fixture failure knowledge with read-only retrieval from real
failure knowledge sources, starting with the existing Neo4j Failure Knowledge
Base, while preserving MVP-0/MVP-1 behavior and architecture boundaries.

MVP-2 production implementation is `NOT_STARTED`.

## 2. Problem Statement

The current `FailureKnowledgeRepository` is keyed by exact display-name pairs:

```text
(item_name, function_name) → list[FailureModeCandidate]
```

That is sufficient for a fixture, but it is not a stable long-term query
contract for real engineering knowledge. The existing Neo4j graph also does not
directly encode full row-level `Component + Function + FailureMode` context.

MVP-2 must define and implement a source-knowledge retrieval boundary that can
support entity resolution, ambiguity and evidence without binding the domain to
Neo4j or returning analysis-side candidates directly from storage.

## 3. Current Baseline

Implemented baseline:

- MVP-0 fixture failure library and in-memory lookup.
- MVP-1 real SysML v2 File Mode into the Canonical System Model.
- Implemented CSM subset: `System`, `Component`, `Function`,
  `SourceReference`.
- No real Neo4j adapter.
- No Neo4j Python driver dependency.
- No Qdrant / RAG / real LLM / Human Review / risk scoring.

External baseline evidence:

- Existing Neo4j 5.26.0 Legacy Failure Knowledge Graph.
- Primary graph strength: FailureMode to Cause, Effect, Prevention Control and
  Detection Control.
- Detailed baseline: `docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md`.

## 4. Stage Capability Decomposition

2A Existing Knowledge Compatibility Baseline:

- verify current implementation contracts and fixture behavior;
- preserve MVP-0/MVP-1 regressions;
- record compatibility constraints before changing interfaces.

2B Failure Knowledge Contracts:

- define project-owned query and hit/source-knowledge contracts;
- keep source knowledge distinct from analysis-side candidates;
- define evidence and provenance requirements.

2C Neo4j Read Adapter:

- read from existing Neo4j through an adapter behind a project-owned port;
- do not expose Neo4j driver types outside the adapter;
- do not mutate the database.

2D Entity Resolution & Context Reconstruction:

- connect CSM item/function context to source knowledge;
- preserve ambiguity and confidence/evidence;
- reconstruct usable context from the existing graph without rebuilding it.

2E Workflow Integration:

- map source knowledge hits into `FailureModeCandidate` analysis output;
- keep workflow statuses explicit;
- preserve risk as `NOT_EVALUATED` unless authorized rules exist.

2F Benchmark & Release:

- evaluate Level 3 Failure Knowledge Retrieval;
- run MVP-0/MVP-1 regression;
- update records and current-state docs after implementation review.

This spec defines WHAT. It does not create `docs/plans/MVP_2_IMPLEMENTATION_PLAN.md`.

## 5. In Scope

- Real Failure Knowledge source contracts.
- Read-only Neo4j retrieval adapter behind a port.
- Entity resolution between CSM context and failure knowledge.
- Context reconstruction from the existing graph.
- Evidence and provenance for retrieved source knowledge.
- Mapping from retrieved source knowledge to candidate analysis objects.
- Backward compatibility with MVP-0 fixture behavior where needed for tests.
- Level 3 benchmark design and release evidence.

## 6. Out of Scope

- Modifying `src/` or tests during this governance baseline session.
- Rebuilding the Neo4j database.
- Running legacy importer against production.
- Installing Neo4j driver before an implementation plan is reviewed.
- Schema migration.
- Knowledge write-back.
- Candidate to Approved write flow.
- Real LLM generation.
- RAG / Qdrant integration.
- MCP integration.
- AIAG-VDA S/O/D/AP or Action Priority implementation.
- Human Review implementation.
- Failure Propagation.
- Changing MVP-1 SysML capability.

## 7. Domain Semantics

MVP-2 must preserve distinctions among:

- Failure Mode;
- Failure Cause;
- Failure Mechanism;
- Failure Effect;
- Prevention Control;
- Detection Control;
- Recommended Action;
- Evidence.

Historical controls retrieved from source knowledge must be distinguishable from
agent-generated recommendations.

Missing information remains `UNKNOWN` or absent with explicit status. It must
not be fabricated.

## 8. Source Knowledge vs Candidate

Failure knowledge source records are not the same thing as analysis-side FMEA
candidates.

The intended chain is:

```text
CSM / Engineering Context
→ FailureKnowledgeQuery
→ FailureKnowledgeRepository
→ FailureKnowledgeHit / source knowledge
→ applicability / entity resolution / evidence
→ mapping
→ FailureModeCandidate
```

The final contract names may be frozen in 2B. This spec intentionally avoids
over-implementing class names.

## 9. Evidence and Provenance Requirements

Each source hit should retain:

- source system identity;
- source record or graph locator where available;
- matched entities;
- relationship path or source structure;
- retrieval rationale;
- entity-resolution status;
- confidence or applicability metadata when defined;
- limitations when provenance is unavailable.

When the legacy graph lacks row-level provenance, the adapter must represent
that absence explicitly rather than inventing a source row.

## 10. Entity Resolution Requirements

Entity resolution must support:

- matching CSM item/component/function context to Neo4j labels and names;
- ambiguity preservation;
- no silent overwrite of conflicting matches;
- no dependence on display names as the only long-term identity strategy;
- traceable evidence for each accepted match.

Exact display-name matching may remain as a compatibility baseline or fallback,
but it must not be the long-term canonical query contract.

## 11. Repository Semantic Contract Requirements

The `FailureKnowledgeRepository` contract must evolve from fixture-specific
candidate lookup toward source-knowledge retrieval.

The repository should not be required to return `FailureModeCandidate` directly
from storage. Candidate construction belongs in an application/domain mapping
step that can attach analysis context and evidence.

## 12. Neo4j Read-only Boundary

MVP-2 Neo4j behavior is read-only.

The adapter must not:

- call destructive graph operations;
- run production write queries;
- execute schema migrations;
- import Excel into Neo4j;
- copy legacy credentials;
- expose driver-specific types outside the adapter.

## 13. Excel and Ontology Roles

Historical Excel / CSV can be a source of failure knowledge when explicitly
ingested through governed contracts. The legacy Excel importer is reference
evidence only and must not become the production path as-is.

Ontology / n10s presence may inform future semantics, but MVP-2 must not depend
on ontology migration or RDF rebuild to retrieve the existing baseline graph.

## 14. Backward Compatibility

MVP-2 must preserve:

- MVP-0 demo behavior unless explicitly changed by a reviewed spec/plan;
- MVP-1 real SysML pipeline;
- `RiskAssessment(status=NOT_EVALUATED)` behavior without authorized risk rules;
- explicit `SKIPPED` optimization when no optimization capability exists;
- architecture rule that `domain/` does not depend on Neo4j.

## 15. Regression Requirements

Implementation stages must run the configured verification suite:

```text
pytest
ruff check .
mypy src
git diff --check
```

Where full production verification is not relevant to docs-only work, the
report must say so explicitly.

## 16. Benchmark Expectations

MVP-2 adds Level 3 Failure Knowledge Retrieval evaluation:

```text
Recall@K
Precision@K
MRR (optional)
Evidence Coverage
Entity Resolution Accuracy
Source Trace Completeness
```

Numerical release gates should not be invented until the team accepts benchmark
data and thresholds.

## 17. Acceptance Criteria

- Existing Neo4j baseline is documented and treated as read-only.
- Source-knowledge contracts distinguish retrieval hits from candidates.
- Repository contract no longer depends solely on exact display-name pair
  lookup as the long-term canonical interface.
- Entity resolution preserves ambiguity and evidence.
- Workflow integration maps source knowledge into candidates without making
  unreviewed content approved.
- MVP-0/MVP-1 regressions remain green.
- No real LLM / RAG / MCP / risk scoring / Human Review implementation enters
  MVP-2.
- Documentation and records accurately state MVP-2 implementation status.

## 18. Known Risks

- Legacy graph lacks row-level provenance.
- Domain labels are Chinese and mostly name-only.
- Relationship properties are absent.
- Function/component context may require reconstruction from indirect paths.
- Exact names may not align with CSM names.
- n10s infrastructure exists but may not encode the needed FMEA semantics.
- Driver/version and credential handling must be planned before implementation.

## 19. Deferred Capabilities

- Knowledge write-back.
- Candidate to Approved persistence.
- Real LLM evidence-grounded generation.
- Qdrant / KG-RAG fusion.
- AIAG-VDA risk strategy and AP rules.
- Human Review workflow.
- Failure Propagation.
- MCP tools and external capability exposure.
