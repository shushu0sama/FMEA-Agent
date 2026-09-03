# AIAG-VDA FMEA Profile v1
## FMEA Agent Domain Baseline

## 1. Purpose

This document defines the project-specific FMEA semantic profile used by FMEA Agent v1.

The baseline methodology is:

> **AIAG-VDA FMEA**

This file defines the data and workflow concepts needed by the software.
It does **not** reproduce proprietary rating tables, Action Priority matrices, handbook text, or copyrighted scoring content.

Before implementing production-grade S/O/D/AP logic, the project must obtain an authorized rule source.

## 2. Seven-Step Workflow Shape

The software workflow should be able to represent:

1. Planning and Preparation
2. Structure Analysis
3. Function Analysis
4. Failure Analysis
5. Risk Analysis
6. Optimization
7. Results Documentation

For early MVPs, a step may be `NOT_EVALUATED` or `SKIPPED`, provided this is explicit.

## 3. Core Analysis Objects

### 3.1 AnalysisContext

Represents:

- analysis ID;
- title;
- scope;
- system/model version;
- assumptions;
- exclusions;
- analysis status;
- method profile;
- created/updated metadata.

### 3.2 FMEAItem

Represents the analyzed item.

Required baseline fields:

```text
id
name
canonical_system_element_id
parent_item_id
source_refs
```

### 3.3 Function

Represents intended behavior or function.

Baseline fields:

```text
id
name
description
item_id
requirement_refs
source_refs
```

### 3.4 FailureMode

Definition:

> The manner in which a function/item fails to meet the intended function or requirement.

Keep distinct from cause and effect.

Baseline fields:

```text
id
item_id
function_id
name
description
status
evidence_refs
```

### 3.5 FailureCause

Definition:

> A condition, mechanism, event or lower-level reason that can lead to the failure mode.

Baseline fields:

```text
id
failure_mode_id
name
description
mechanism_id?
evidence_refs
```

### 3.6 FailureMechanism

Optional explicit mechanism concept.

Examples of semantic category only:

```text
wear
fatigue
corrosion
software logic defect
electrical degradation
```

Do not force every cause to have a mechanism in MVP-0.

### 3.7 FailureEffect

Effects must support level.

```text
LOCAL
NEXT_HIGHER_LEVEL
END_EFFECT
```

Baseline fields:

```text
id
failure_mode_id
level
affected_item_id?
description
evidence_refs
```

### 3.8 Control

Support at least semantic categories:

```text
PREVENTION
DETECTION
```

### 3.9 RecommendedAction

Represents a candidate or approved optimization action.

### 3.10 Evidence

Every non-trivial candidate may link to evidence.

Evidence can support:

- item/function fact;
- failure mode;
- cause;
- effect;
- risk recommendation;
- optimization recommendation.

## 4. Risk Model

Risk is implemented through a strategy interface.

```python
class RiskStrategy(Protocol):
    def evaluate(self, context: RiskContext) -> RiskAssessment:
        ...
```

Possible implementations:

```text
NoOpRiskStrategy
AIAGVDARiskStrategy
FutureCriticalityStrategy
CustomEnterpriseRiskStrategy
```

### 4.1 MVP-0

Allowed result:

```text
risk_status = NOT_EVALUATED
```

### 4.2 Future AIAG-VDA Implementation

Future authorized implementation may support:

```text
Severity
Occurrence
Detection
Action Priority
```

Rules must not be invented by the LLM.

## 5. Field Authority

Recommended status types:

```text
FACT
RETRIEVED
INFERRED
CANDIDATE
REVIEWED
APPROVED
UNKNOWN
```

Example policy:

| Field | May be auto-populated | LLM may suggest | Human confirmation |
|---|---:|---:|---:|
| Item | yes, from model | no | when model ambiguity exists |
| Function | yes, from model | yes | important functions |
| Failure Mode | retrieved/candidate | yes | required before approval |
| Failure Cause | retrieved/candidate | yes | required before approval |
| Failure Effect | candidate | yes | required before approval |
| S/O/D | only with rules/data | limited | required for formal release |
| AP | derived from authorized strategy | no free-form | required for formal release |
| Evidence | retrieved | summarize only | evidence relevance may be reviewed |

## 6. Semantic Validation Rules

Minimum rules:

1. An FMEA row requires an item and function context.
2. Failure Mode must describe failure of intended function/requirement, not merely repeat a cause.
3. Cause and Effect must not be silently merged.
4. Effects should identify an effect level when possible.
5. A risk value must declare its source/strategy.
6. Missing information must remain `UNKNOWN` / `NOT_EVALUATED`, not be fabricated.
7. Approved results must retain evidence and review metadata.

## 7. MVP-0 Minimum Schema

MVP-0 only needs:

```text
AnalysisContext
FMEAItem
Function
FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
Evidence
RiskAssessment(status=NOT_EVALUATED)
```

Optimization controls/actions can remain optional.

## 8. Future Extensions

Later phases may add:

- richer structure trees;
- function networks;
- prevention/detection controls;
- authorized AIAG-VDA AP rules;
- action tracking;
- responsibility/due dates;
- revision history;
- special characteristics;
- enterprise extensions;
- additional FMEA/FMECA profiles through strategy/profile separation.

## 9. Non-goal

Do not hard-code the whole FMEA methodology into LangGraph prompts.

The domain model and validators remain authoritative.
