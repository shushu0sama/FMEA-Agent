# ADR-001: LangGraph as the Orchestration Baseline

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

FMEA requires explicit workflow state, controlled routing, future persistence and human review. A generic one-shot agent loop would make the analysis process harder to test and audit.

## Decision

Use LangGraph as the default workflow/orchestration framework. Keep domain logic independent of LangGraph.

## Consequences

Workflow structure is explicit and testable. The project accepts a dependency on LangGraph at the orchestration layer, while preserving the ability to replace it by keeping domain/application ports independent.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
