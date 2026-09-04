# FMEA Agent V1 Product Boundary

Status: ACTIVE

## 1. Primary User

The primary V1 user is an FMEA engineer.

## 2. V1 Mission

FMEA Agent V1 is an evidence-grounded semi-autonomous DFMEA assistant. Given
engineering design context, historical failure knowledge and reviewed source
evidence, it should help produce a complete Candidate FMEA for engineering
review.

The system is an engineering assistant, not an engineering authority. Final
engineering decisions remain subject to human review.

## 3. Inputs

Currently implemented:

- JSON fixture input for MVP-0 regression.
- SysML v2 File Mode for MVP-1 real system facts.

Planned for V1:

- Existing Neo4j Failure Knowledge Base, read-only for MVP-2.
- Historical FMEA Excel / CSV as source evidence where explicitly imported.
- FMEA reports and reviewed failure, test and maintenance knowledge.
- Product design documentation and Product Design Manual sources after document
  ingestion is scoped.

Long-term extension:

- MBSE repositories, BOM, PLM and requirements databases.
- Document-derived knowledge lifecycle and approved write-back.
- External tools through API / MCP capability boundaries.

## 4. Outputs

V1 targets a structured Candidate FMEA containing:

- analyzed item / component;
- function / requirement context;
- failure mode;
- failure cause;
- optional failure mechanism;
- local effect;
- next-higher-level effect;
- end effect;
- prevention control;
- detection control;
- recommended action;
- improvement recommendation;
- evidence and provenance;
- knowledge origin and analysis status;
- risk fields only where authorized rules exist.

Current MVP output is narrower. MVP-1 produces structured candidate output using
System / Component / Function / SourceReference and fixture failure knowledge.
It does not produce real Neo4j-backed failure knowledge, real LLM generation,
human-reviewed approvals or authorized AIAG-VDA risk fields.

## 5. Workflow Shape

V1 follows the AIAG-VDA seven-step workflow shape:

1. Planning and Preparation
2. Structure Analysis
3. Function Analysis
4. Failure Analysis
5. Risk Analysis
6. Optimization
7. Results Documentation

Early MVPs may explicitly output `NOT_EVALUATED` or `SKIPPED` for stages whose
rules are not yet implemented.

## 6. Automation Boundary

The agent may automate retrieval, mapping, candidate generation, evidence
linking, consistency checks and report assembly.

The agent must not silently approve engineering results, invent missing facts,
invent S/O/D/AP values or overwrite conflicting evidence. Review and approval
remain explicit workflow boundaries.

## 7. Evidence Requirement

Every non-trivial candidate should retain traceable evidence. The source of each
field should distinguish system facts, retrieved failure knowledge, inference,
candidate analysis and human-reviewed decisions.

When evidence conflicts, preserve the conflict and escalate when material.

## 8. Capability Status

Currently implemented:

- MVP-0 runnable offline vertical slice.
- MVP-1 real SysML v2 File Mode path through `SysMLFactSnapshot` into the
  Canonical System Model.
- Implemented CSM subset: `System`, `Component`, `Function`, `SourceReference`.
- LangGraph workflow skeleton with explicit `NOT_EVALUATED` risk and `SKIPPED`
  optimization.

Planned for V1:

- MVP-2 real failure knowledge retrieval from existing Neo4j, read-only.
- MVP-3 evidence-grounded LLM generation through provider-neutral boundaries.
- MVP-4 authorized risk strategy and semantic validation.
- MVP-5 human review workflow and future knowledge lifecycle boundary.

Long-term extension:

- Requirement / Port / Interface / Connection / Flow / State / Allocation in
  the Canonical System Model.
- Failure propagation.
- Aerospace benchmark expansion.
- MCP capability layer.
- Dynamic FMEA and approved knowledge write-back.

## 9. Non-goals

V1 does not make the agent an engineering authority.

V1 does not copy proprietary AIAG-VDA rating tables or Action Priority matrices.

V1 does not bind the FMEA domain model directly to SysML, Neo4j, Qdrant, MCP,
OpenSysML, LangGraph, LangChain, any LLM provider or a UI framework.

V1 does not treat unreviewed candidates as approved results.

## 10. V1 Completion Boundary

V1 is complete only when the system can produce an evidence-grounded Candidate
DFMEA over real engineering context and real failure knowledge, preserve
provenance, avoid unsupported risk values, and hand results to human review.

MVP-2 through MVP-5 are the minimum planned route to that V1 boundary.
