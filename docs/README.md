# FMEA Agent Documentation Index

> Lifecycle navigation for coding-agent sessions. Keep this file short and use
> linked documents as the detailed source of truth.

## New Session Minimum Reading

For a normal development session, read only:

1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/README.md`
4. Current Spec under `docs/specs/`
5. Current Plan under `docs/plans/` when one exists
6. Previous Stage Record under `docs/records/`

Do not read the full foundation guides every session. Read them when changing
long-lived architecture, phase strategy, or source-of-truth rules.

## Lifecycle States

`ACTIVE` = current operational source of truth.

`REFERENCE` = useful long-lived background or evidence; read when relevant.

`HISTORICAL` = records what happened or what was planned at the time; do not
treat as current state.

`SUPERSEDED` = retained for traceability but replaced by a newer document.

## ACTIVE

- `AGENTS.md` — canonical cross-coding-agent project instructions.
- `PROGRESS.md` — current project state, roadmap and next action.
- `README.md` — root project overview and current runnable capability.
- `docs/README.md` — documentation lifecycle and navigation.
- `docs/product/FMEA_AGENT_V1.md` — V1 product and capability boundary.
- `docs/architecture/FMEA_AGENT_V1_ARCHITECTURE.md` — V1 architecture boundary.
- `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md` — CSM contract.
- `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` — SysML snapshot contract.
- `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md` — SysML mapping matrix.
- `docs/domain/FMEA_PROFILE_V1.md` — FMEA semantic profile.
- `docs/domain/FMEA_GLOSSARY.md` — terminology source of truth.
- `docs/evaluation/BENCHMARK_SPEC.md` — long-lived benchmark model.
- `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` — governance rules.
- `docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md` — language and term policy.
- `docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md` — current MVP-2 planning spec.

## REFERENCE

- `CLAUDE.md` — Claude Code compatibility instructions; keep aligned with
  `AGENTS.md` until tool-loading behavior is formally simplified.
- `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md` — long-form architecture
  foundation.
- `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md` — long-form
  phase and reuse guide.
- `docs/research/DEPENDENCY_INVENTORY.md` — dependency and reuse inventory.
- `docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md` — existing Neo4j failure
  knowledge baseline for MVP-2 planning.
- `docs/research/OPENSYSML_SPIKE_REPORT.md` — MVP-1 OpenSysML spike evidence.
- `docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md` — OpenSysML pin
  reproduction evidence.
- `docs/research/SYSML_SOURCE_CATALOG.md` — SysML source catalog.
- `docs/adr/` — accepted architecture decision records.
- `docs/records/templates/` — closeout, release and session handoff templates.

## HISTORICAL

- `docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md`
- `docs/specs/MVP_1_REAL_SYSTEM_FACTS.md`
- `docs/plans/MVP_0_IMPLEMENTATION_PLAN.md`
- `docs/plans/MVP_1_IMPLEMENTATION_PLAN.md`
- `docs/prompts/MVP_1_CLAUDE_CODE_SESSIONS.md`
- `docs/records/MVP_0/`
- `docs/records/MVP_1/`
- `docs/records/bootstrap/PROJECT_CLEANUP_REPORT.md`

## SUPERSEDED

- `docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md` — superseded by
  `docs/records/templates/SESSION_HANDOFF_TEMPLATE.md` for intra-stage handoff
  and by the New Session Minimum Reading list above for normal sessions.

## Current Stable Release

`v0.1.1` is the current stable release tag. It is a docs-only patch on top of
MVP-1 Real System Facts; no MVP-2 production implementation has started.
