# ADR-005: MCP as an External Capability Boundary

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

MCP is valuable for exposing/querying tools across agents, but protocol concerns should not become domain concerns.

## Decision

Use MCP at external capability boundaries. Domain and canonical models must not import MCP SDK types.

## Consequences

The project can reuse existing MCP servers and expose stable FMEA capabilities later without making MCP a mandatory runtime for core logic.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
