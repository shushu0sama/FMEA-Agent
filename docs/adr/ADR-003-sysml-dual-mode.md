# ADR-003: Keep SysML File Mode and Repository Mode

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

Offline benchmarks and research need file-based models, while engineering scenarios need repository/version-aware access.

## Decision

Keep both File Mode and Repository Mode behind a common system-model port.

## Consequences

Two adapters must be maintained and cross-adapter consistency becomes a benchmark concern.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
