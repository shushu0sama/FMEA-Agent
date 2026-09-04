# FMEA Agent V1 Architecture

Status: ACTIVE

## 1. Purpose

This document defines the long-lived V1 architecture boundary. It does not
describe every implemented feature as current capability.

## 2. Layering

```text
User / API
  ↓
Agent Orchestration (LangGraph)
  ↓
Domain Services
  ↓
Canonical System Model + Failure Knowledge Model
  ↓
Ports
  ↓
Adapters
  ↓
Engineering / Knowledge / External Sources
```

LangGraph is the orchestration baseline. The FMEA domain model remains
project-owned and framework-independent.

## 3. Dependency Rule

`domain/` must not depend directly on:

- Neo4j driver;
- LangGraph;
- LangChain;
- Qdrant client;
- OpenSysML runtime;
- MCP SDK;
- any specific LLM provider;
- CLI or UI frameworks.

External technologies belong behind ports and adapters.

## 4. Engineering Context Boundary

Engineering Context adapters convert external engineering sources into
project-owned facts and then into the Canonical System Model.

Current implemented source:

- SysML v2 File Mode through OpenSysML into `SysMLFactSnapshot`.

Planned / future sources:

- SysML Repository API;
- MBSE repositories;
- BOM;
- Product Design Manual and design documentation;
- PLM and requirements databases.

The Canonical System Model is the long-term boundary between engineering-model
adapters and FMEA logic. The domain must not become SysML-specific.

## 5. Failure Knowledge Boundary

Failure Knowledge adapters convert external failure knowledge into
project-owned source-knowledge records.

Current implemented source:

- MVP-0 fixture / in-memory knowledge for regression.

MVP-2 source:

- Existing Neo4j Failure Knowledge Base, read-only.

Future sources:

- historical FMEA Excel / CSV;
- FMEA reports;
- reviewed failure, test and maintenance records;
- document-derived knowledge.

Neo4j is an adapter/storage baseline, not the domain boundary.

## 6. Source Knowledge vs Candidate Analysis

Failure knowledge retrieval and FMEA candidate construction are separate steps.

The target chain is:

```text
CSM / Engineering Context
→ FailureKnowledgeQuery
→ FailureKnowledgeRepository
→ FailureKnowledgeHit / source knowledge
→ applicability / entity resolution / evidence
→ mapping
→ FailureModeCandidate
```

The repository contract should not permanently require exact display-name pairs
such as `(item_name, function_name)`, and a Neo4j adapter should not be forced
to return analysis-side `FailureModeCandidate` objects directly.

## 7. Evidence and Provenance

Evidence and provenance are first-class data. The architecture must retain:

- engineering source references;
- failure knowledge source references;
- retrieval evidence;
- mapping / entity-resolution evidence;
- analysis status;
- review / approval metadata when that stage exists.

Unsupported claims must remain explicit as `UNKNOWN`, `NOT_EVALUATED` or
candidate-only content.

## 8. Entity Resolution

Entity Resolution connects engineering context to failure knowledge when source
schemas do not share stable identifiers.

MVP-2 must account for the known Neo4j gap: the existing graph strongly links
FailureMode to Cause, Effect, Prevention Control and Detection Control, but it
does not directly encode full row-level `Component + Function + FailureMode`
analysis context.

Entity resolution must preserve ambiguity rather than silently selecting a
single source hit.

## 9. LLM Boundary

LLMs are provider-neutral behind `LLMClient` or future equivalent ports.

MVP-2 does not call a real LLM. MVP-3 introduces evidence-grounded LLM
generation only after real failure knowledge retrieval exists.

LLM output is candidate or inference unless reviewed and approved.

## 10. RiskStrategy

Risk evaluation remains behind `RiskStrategy`.

MVP-2 does not implement AIAG-VDA S/O/D/AP or Action Priority logic. Authorized
risk rules require a licensed or independently authorized source.

## 11. Human Review Boundary

Human review is a formal workflow boundary. Candidate content can be generated,
retrieved and checked automatically, but approval requires explicit review
state.

Review persistence and future knowledge lifecycle are planned after the real
failure knowledge and evidence-grounded generation stages.

## 12. External Capability Boundary

API, MCP and external tools are capability boundaries, not domain models.

The project may expose or consume tools later, but the domain should remain
usable without MCP-specific request/response classes.

## 13. Future KnowledgeWriter Boundary

Knowledge write-back is not part of MVP-2.

The long-term architecture may add a `KnowledgeWriter` or equivalent boundary
after Human Review defines how a Candidate becomes reviewed or approved source
knowledge. MVP-2 remains read-only.
