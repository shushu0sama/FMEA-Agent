# ADR-004: Separate System Model and Failure Model

**Status:** ACCEPTED  
**Baseline:** Bootstrap v0.1

## Context

Engineering structure/function facts and failure-analysis knowledge have different lifecycles, semantics and evidence requirements.

## Decision

Keep System Model and Failure Model logically separate and connect them through explicit mappings/references.

## Consequences

The schema remains clearer and multiple failure-analysis methods can evolve without corrupting engineering-model semantics.

## Revisit When

Revisit only when experiments, standards, compatibility constraints or engineering requirements demonstrate that the current decision materially blocks project goals.
