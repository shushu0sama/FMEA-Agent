# ADR-002: Canonical System Model as the Integration Boundary

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

FMEA must consume engineering facts from multiple possible sources without binding domain logic to OpenSysML, REST payloads, PLM or other vendor models.

## Decision

Introduce a project-owned Canonical System Model. External model sources map through adapters into this model.

## Consequences

Additional engineering sources can be integrated by adapters. The project must invest in canonical semantic design and mapping tests.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
