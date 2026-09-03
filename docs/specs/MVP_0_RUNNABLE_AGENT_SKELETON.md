# MVP-0 Specification — Runnable FMEA Agent Skeleton

## 1. Goal

Create the first runnable FMEA Agent vertical slice.

The purpose is **not** to achieve engineering-quality FMEA intelligence.

The purpose is to prove:

```text
input
→ domain models
→ workflow
→ replaceable repositories
→ candidate analysis
→ structured output
```

with correct architecture boundaries.

## 2. User Story

As a developer/researcher, I can run:

```bash
python -m fmea_agent demo examples/simple_pump.json
```

and receive a structured candidate FMEA output without requiring:

- network access;
- SysML server;
- Neo4j;
- vector DB;
- external LLM;
- MCP.

## 3. Example Input

```json
{
  "system": {
    "id": "hydraulic-system",
    "name": "Hydraulic System"
  },
  "components": [
    {
      "id": "hydraulic-pump",
      "name": "Hydraulic Pump",
      "functions": [
        {
          "id": "provide-pressure",
          "name": "Provide Hydraulic Pressure"
        }
      ]
    }
  ]
}
```

## 4. Example Fixture Failure Knowledge

```json
{
  "item_name": "Hydraulic Pump",
  "function_name": "Provide Hydraulic Pressure",
  "failure_modes": [
    {
      "name": "Loss of hydraulic pressure",
      "cause": "Demo mechanical failure",
      "local_effect": "Required outlet pressure is unavailable",
      "evidence_id": "demo-failure-library:001"
    }
  ]
}
```

## 5. Workflow

The graph should expose the AIAG-VDA-shaped stages:

```text
Planning & Preparation
Structure Analysis
Function Analysis
Failure Analysis
Risk Analysis
Optimization
Results Documentation
```

MVP behavior:

| Stage | MVP-0 behavior |
|---|---|
| Planning & Preparation | create AnalysisContext |
| Structure Analysis | load fixture system/component |
| Function Analysis | load function |
| Failure Analysis | retrieve fixture candidate |
| Risk Analysis | explicit `NOT_EVALUATED` |
| Optimization | explicit `SKIPPED` |
| Results Documentation | serialize candidate JSON |

## 6. Architecture

Required concepts:

```text
domain/
application/ports/
adapters/inmemory/
agents/
cli/
```

Required ports:

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

`LLMClient` may not be invoked in the default demo.

## 7. Minimal Domain Models

System:

```text
System
Component
Function
SourceReference
```

FMEA:

```text
AnalysisContext
FMEAItem
FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
Evidence
RiskAssessment
```

## 8. Output

Example semantic shape:

```json
{
  "analysis_id": "...",
  "method": "AIAG_VDA",
  "item": "Hydraulic Pump",
  "function": "Provide Hydraulic Pressure",
  "failure_mode": {
    "value": "Loss of hydraulic pressure",
    "status": "CANDIDATE"
  },
  "cause": {
    "value": "Demo mechanical failure",
    "status": "CANDIDATE"
  },
  "effects": [
    {
      "level": "LOCAL",
      "value": "Required outlet pressure is unavailable"
    }
  ],
  "risk": {
    "status": "NOT_EVALUATED"
  },
  "evidence": [
    {
      "source": "demo-failure-library:001"
    }
  ]
}
```

## 9. Non-goals

Do not implement in MVP-0:

- OpenSysML;
- SysML API;
- full Canonical System Model;
- Neo4j;
- Qdrant;
- Docling;
- MCP;
- full AIAG-VDA risk rules;
- PDF/Excel UI;
- autonomous multi-agent behavior;
- human-review persistence;
- failure propagation.

## 10. Tests

Required:

### Unit

- domain model validation;
- in-memory repository behavior;
- risk `NOT_EVALUATED`;
- output serialization.

### Workflow

- fixture flows through all stages;
- each stage has an explicit status.

### Smoke

```text
CLI demo exits 0
output JSON exists
output validates
```

## 11. Acceptance Criteria

```text
[ ] fresh environment can install project
[ ] all configured verification checks pass
[ ] default demo requires no external service
[ ] output is structured, not free-form text
[ ] workflow uses replaceable ports
[ ] no external framework leaks into domain models
[ ] risk is not fabricated
[ ] evidence points to fixture
[ ] PROGRESS.md updated
```

## 12. Definition of Success

MVP-0 is successful when:

> The project has a small but correctly layered executable FMEA workflow that can later replace each stub with a real engineering integration.
