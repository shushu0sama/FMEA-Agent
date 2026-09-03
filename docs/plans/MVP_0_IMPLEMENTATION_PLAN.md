# MVP-0 Implementation Plan

> Implement one task at a time. Do not start later integrations.

## Task 0 — Inspect and Scaffold

Goal:
Create/align the Python package structure.

Expected directories:

```text
src/fmea_agent/
  domain/
  application/
  adapters/
  agents/
  cli/
tests/
examples/
```

Verification:
package imports successfully.

## Task 1 — Minimal Domain Contracts

Implement:

```text
SourceReference
System
Component
Function
AnalysisContext
Evidence
FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
RiskAssessment
```

Use typed Pydantic models.

Tests first:

- valid construction;
- invalid missing required IDs;
- enum/status validation;
- serialization.

## Task 2 — Application Ports

Define:

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

No external implementation imports in port definitions.

Tests:
simple fake class satisfies expected behavior.

## Task 3 — In-Memory Adapters

Implement:

```text
InMemorySystemModelRepository
InMemoryFailureKnowledgeRepository
NoOpRiskStrategy
MockLLMClient
```

The default path should not need `MockLLMClient`.

Tests:
fixture lookup and missing-data behavior.

## Task 4 — Workflow State

Define structured graph state.

Suggested fields:

```text
analysis_context
system
selected_component
function
failure_candidates
risk
stage_status
output
errors
```

Do not use an unstructured chat transcript as the state model.

## Task 5 — LangGraph Skeleton

Implement stages:

```text
planning
structure_analysis
function_analysis
failure_analysis
risk_analysis
optimization
results_documentation
```

Expected MVP statuses:

```text
risk_analysis = NOT_EVALUATED
optimization = SKIPPED
```

Tests:
state traverses to END.

## Task 6 — Demo Fixture

Add:

```text
examples/simple_pump.json
examples/demo_failure_library.json
```

Keep fixtures obviously synthetic.

## Task 7 — CLI

Target:

```bash
python -m fmea_agent demo examples/simple_pump.json
```

Behavior:

- read fixture;
- run graph;
- save or print structured output;
- return non-zero on invalid input.

## Task 8 — Smoke Test

Run CLI through subprocess or an equivalent test.

Assert:

```text
exit code == 0
valid output JSON
risk.status == NOT_EVALUATED
evidence exists
```

## Task 9 — Verification Script

Create platform-appropriate verification entry.

Minimum logical checks:

```text
pytest
ruff check .
mypy src
```

If a tool is not configured yet, add it before closing MVP-0.

## Task 10 — Documentation Handoff

Update:

```text
PROGRESS.md
README.md
```

Report:

- changed files;
- tests;
- known limitations;
- next MVP recommendation.

## Completion Gate

Do NOT start OpenSysML integration until MVP-0 passes its acceptance criteria.
