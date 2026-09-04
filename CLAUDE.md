# CLAUDE.md — FMEA Agent Project Instructions

> This file is the primary operating instruction for Claude Code.
> Keep it short enough to read every session.
> Long-term principles live under `docs/foundation/`.

## 1. Mission

Build a maintainable, evidence-grounded, MBSE-aware FMEA Agent.

The project must evolve from a runnable vertical-slice MVP into an extensible engineering analysis system.

The system is an **engineering assistant**, not an autonomous authority.

Final engineering decisions remain subject to human review.

## 2. Current FMEA Profile

The project baseline is:

**AIAG-VDA FMEA**

Use the seven-step process as the workflow shape:

1. Planning and Preparation
2. Structure Analysis
3. Function Analysis
4. Failure Analysis
5. Risk Analysis
6. Optimization
7. Results Documentation

Do not reproduce or invent proprietary AIAG-VDA rating tables or Action Priority matrices.
Risk-rule implementation requires a licensed/user-provided rule source or an independently authorized rule definition.

## 3. Core Architecture Decisions

Treat these as project constraints unless an accepted ADR changes them:

- LangGraph is the orchestration baseline.
- LangChain is optional integration/adapter infrastructure, not the domain core.
- SysML/MBSE is a primary system-fact source.
- Canonical System Model is the boundary between engineering-model adapters and FMEA logic.
- System Model and Failure Model are separate.
- Evidence / provenance is first-class data.
- MCP is an external capability interface, not the domain core.
- Neo4j is the current graph-storage baseline, behind an interface.
- Human review is a formal workflow boundary.
- Workflow-first; autonomous multi-agent behavior is deferred.
- Runnable vertical slice first; replace stubs incrementally.

## 4. Development Strategy

### 4.1 Minimum functionality, correct boundaries

The first implementation may have very little intelligence.

It must still have correct module boundaries.

Prefer:

```text
small capability
+ stable interfaces
+ tests
+ replaceable adapters
```

over:

```text
large demo
+ coupled code
+ hidden prompt logic
```

### 4.2 Vertical Slice First

The first runnable MVP should use:

- JSON fixture input;
- minimal Canonical System Model;
- minimal FMEA domain model;
- in-memory repositories;
- mock or optional LLM;
- LangGraph workflow skeleton;
- structured output;
- tests.

The first runnable MVP must NOT be blocked by:

- OpenSysML;
- Neo4j;
- Qdrant;
- Docling;
- MCP;
- production UI;
- complete AIAG-VDA risk rules;
- multi-agent orchestration.

Those replace stubs later.

## 5. Source-of-Truth Hierarchy

For system facts:

```text
approved engineering model / SysML
> approved structured engineering data
> reviewed engineering documents
> retrieval result
> LLM inference
```

For failure knowledge:

```text
approved FMEA / official standard / approved engineering record
> failure / test / maintenance record
> reviewed technical literature
> unreviewed document
> LLM inference
```

Never silently overwrite conflicting evidence.
Preserve conflict and escalate when material.

## 6. Domain Dependency Rules

`domain/` MUST NOT depend directly on:

- LangGraph;
- LangChain;
- Neo4j driver;
- Qdrant client;
- MCP SDK;
- OpenSysML runtime;
- any specific LLM provider;
- CLI/UI frameworks.

External technology belongs behind ports/adapters.

## 7. Preferred Code Shape

Target architecture:

```text
domain/
application/
adapters/
agents/
evaluation/
cli/
```

Target ports (long-term architecture):

```text
SystemModelRepository
FailureKnowledgeRepository
EvidenceRepository
LLMClient
RiskStrategy
ReviewRepository
```

Current MVP required ports (controlled by the current spec):

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

Deferred until needed:

```text
EvidenceRepository — until real Evidence / KG-RAG capabilities are needed
ReviewRepository   — until the Human Review stage
```

The current spec controls what must be implemented in the current MVP.

Initial implementations may be:

```text
InMemorySystemModelRepository
InMemoryFailureKnowledgeRepository
MockLLMClient
NoOpRiskStrategy
```

Later replacements may include:

```text
OpenSysMLSystemModelRepository
SysMLAPIRepository
Neo4jFailureKnowledgeRepository
QdrantEvidenceRepository
ProviderLLMClient
AIAGVDARiskStrategy
```

Upper layers should not require redesign when adapters change.

## 8. Required Reading

Always read:

1. `CLAUDE.md`
2. `PROGRESS.md`

Read when relevant:

- architecture/boundaries:
  `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md`
- phases/MVP/reuse:
  `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md`
- FMEA semantics:
  `docs/domain/FMEA_PROFILE_V1.md`
- terminology:
  `docs/domain/FMEA_GLOSSARY.md`
- system-model schema:
  `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md`
- benchmark/evaluation:
  `docs/evaluation/BENCHMARK_SPEC.md`
- third-party dependencies:
  `docs/research/DEPENDENCY_INVENTORY.md`
- important decisions:
  `docs/adr/`
- current feature:
  relevant file under `docs/specs/` and `docs/plans/`
- stage history / release state:
  `docs/records/` + `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`

Do not read every long document for every trivial change.

## 9. Development Records & Session Recovery

Governance policy (full rules):

```text
docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md
```

- Before starting a non-trivial Stage, read:
  `CLAUDE.md` / `PROGRESS.md`, current Spec, current Plan,
  previous Stage Record (`docs/records/`).
- One formal Stage ≈ one main session. On session switch, recover state
  from Git + PROGRESS + Spec + Plan + Stage Records — never from chat memory.
- `PROGRESS.md` is current state only; execution history lives in
  `docs/records/` (one Closeout Record per Stage, one Release Record per MVP).
- Plan ≠ execution record; prompt ≠ source of truth. Record real evolution
  in Stage Records; never rewrite history to match today's state.
- Anti-drift: check branch/HEAD/scope before a Stage and before declaring
  it done; report scope drift explicitly.
- Stage status: IMPLEMENTED → independent review → ACCEPTED.
  Do not claim COMPLETE/ACCEPTED/PASS without running verification.
- Mark verification evidence as LOCAL / CI / EXTERNAL_REVIEW
  (no CI is configured yet).

## 10. Task Classification

For non-trivial work:

```text
Explore
→ Spec
→ Plan
→ Test
→ Implement
→ Verify
→ Review
→ Update PROGRESS
```

Do not start implementation before understanding existing code and the current phase.

## 11. Reuse Policy

Before writing infrastructure:

1. Search the repository.
2. Search existing selected dependencies.
3. Inspect the upstream API.
4. Classify the capability:

```text
S = Self-build
W = Wrap
D = Direct reuse
R = Reference only
```

Self-build FMEA-specific semantics.
Reuse generic infrastructure.

Never rewrite a SysML parser, graph database, vector database, MCP protocol, agent runtime, or document parser without a documented reason.

## 12. External Dependency Policy

For important third-party projects:

- pin versions;
- record important commit hashes when reproducibility matters;
- record license;
- keep them behind adapters;
- add contract tests;
- do not upgrade several major dependencies at once;
- run regression tests before accepting upgrades.

If upstream documentation and executable behavior disagree, record the discrepancy and trust reproducible test evidence.

## 13. Testing

At minimum:

```bash
pytest
ruff check .
mypy src
```

when these tools are configured.

Test types:

- unit;
- integration;
- contract;
- regression;
- benchmark.

External adapters require contract tests.

LLM-dependent functionality requires deterministic fixtures/mocks for normal tests.

## 14. Definition of Done

Do not claim a task is complete unless relevant items are satisfied:

- scope/spec is clear;
- implementation respects architecture;
- tests were added/updated;
- tests pass;
- lint/type checks pass;
- relevant benchmark does not regress;
- no unrelated changes;
- evidence/provenance is preserved;
- documentation is updated;
- `PROGRESS.md` is updated;
- unresolved risks are explicitly reported.

## 15. FMEA Safety Rules

Never present an unreviewed candidate as an approved engineering result.

Always distinguish:

```text
FACT
RETRIEVED_KNOWLEDGE
INFERENCE
CANDIDATE
REVIEWED
APPROVED
UNKNOWN
```

Do not invent S/O/D/AP values when evidence/rules are missing.

Do not conflate:

- Failure Mode;
- Failure Cause;
- Failure Mechanism;
- Failure Effect.

## 16. Phase Discipline

Do not implement later-phase infrastructure merely because it is interesting.

Current implementation priority is defined in `PROGRESS.md`.

The immediate strategy is:

```text
Runnable MVP first
→ real SysML
→ real failure knowledge
→ evidence-grounded LLM
→ risk/verification
→ human review
→ propagation
→ aerospace benchmark
→ MCP
→ dynamic FMEA
```

## 17. Git Discipline

- one clear purpose per branch/worktree;
- small commits;
- no unrelated formatting;
- do not modify third-party Git history;
- keep experiments separate from production code;
- verification before commit.

## 18. Completion Report

When finishing a task, report:

```text
What changed
Why
Files changed
Tests run
Verification results
Benchmark impact
Dependencies added/changed
Known limitations
Next recommended task
```

Never state "complete" if verification was not run.
