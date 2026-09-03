# ADR-007: Runnable Vertical Slice Before Full Integrations

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

Building all SysML, KG/RAG and MCP integrations before seeing an end-to-end runnable system creates long integration delays and encourages overengineering.

## Decision

Build MVP-0 as a runnable end-to-end vertical slice using fixtures, in-memory repositories and stubbed replaceable adapters. Replace stubs incrementally in later MVPs.

## Consequences

The project gets early executable feedback. Interfaces must be designed carefully enough that later real integrations do not require rewriting the workflow.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
