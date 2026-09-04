# Canonical System Model Specification
## Architecture Contract v0.1

## 1. Purpose

The Canonical System Model (CSM) is the stable integration boundary between engineering-model sources and FMEA logic.

Upper layers must not depend directly on:

- OpenSysML runtime objects;
- SysML REST payloads;
- vendor MBSE objects;
- MCP response models.

The conversion pipeline is:

```text
External Model
  ↓
Adapter
  ↓
SysMLFactSnapshot / source-native snapshot
  ↓
Canonical Mapping
  ↓
Canonical System Model
  ↓
FMEA Domain
```

## 2. Important Boundary

### 2.1 SysMLFactSnapshot

Phase-1 object.

Purpose:

> Preserve what the parser/API returned with minimal semantic normalization.

It may contain:

```text
source element ID
source metatype
name
raw attributes
ownership
raw relationships
source version
```

It is **not** the Canonical System Model.

### 2.2 Canonical System Model

Phase-2 object.

Purpose:

> Express engineering concepts in a stable tool-independent form needed by FMEA.

## 3. MVP-0 Canonical Scope

To get the runnable skeleton working, MVP-0 only requires:

```text
System
Component
Function
SourceReference
Relationship(optional minimal)
```

Do not block MVP-0 on ports, interfaces, flows, states or allocations.

## 4. Target v1 Entity Set

```text
System
Subsystem
Component
Function
Requirement
Port
Interface
Connection
Flow
State
Allocation
Relationship
SourceReference
```

## 5. Shared Identity Types

Conceptual types:

```python
CanonicalId = str
SourceElementId = str
VersionId = str
```

### 5.1 ID Requirements

Canonical IDs should be:

- stable within a canonical model version;
- deterministic where practical;
- decoupled from display names;
- able to retain source IDs separately.

Do not finalize cross-commit identity logic in MVP-0.

### 5.2 SourceReference

Minimum fields:

```text
source_type
source_uri/path
source_element_id
source_version
adapter
```

Optional:

```text
repository
project
commit
branch
locator
```

## 6. MVP-0 Conceptual Models

### 6.1 System

```text
id
name
description?
source_refs[]
```

### 6.2 Component

```text
id
name
parent_id?
component_type?
source_refs[]
```

### 6.3 Function

```text
id
name
description?
allocated_to[]
requirement_ids[]
source_refs[]
```

### 6.4 Relationship

MVP-0 may use a generic edge:

```text
id
type
source_id
target_id
source_refs[]
```

Use only when needed by the vertical slice.

## 7. Target v1 Models

### Requirement

```text
id
name
text?
owner_id?
source_refs[]
```

### Port

```text
id
name
owner_id
direction?
type_ref?
source_refs[]
```

### Interface

```text
id
name
participant_ids[]
source_refs[]
```

### Connection

```text
id
source_element_id
target_element_id
kind?
source_refs[]
```

### Flow

```text
id
source_element_id
target_element_id
flow_item?
flow_kind?
source_refs[]
```

### State

```text
id
name
owner_id
source_refs[]
```

### Allocation

```text
id
source_id
target_id
allocation_type
source_refs[]
```

## 8. Repository Port

Upper layers should depend on a port similar to:

```python
class SystemModelRepository(Protocol):
    def get_system(self, system_id: str): ...
    def get_component(self, component_id: str): ...
    def list_components(self, system_id: str): ...
    def list_functions(self, element_id: str): ...
```

Do not expose parser/runtime classes through this interface.

## 9. Validation Rules

Minimum:

- IDs unique;
- relationship endpoints exist;
- parent references resolve where required;
- source references retain origin;
- unknown/unsupported source elements do not crash the full import;
- partial models are allowed and explicitly marked.

## 10. Mapping Status

Every SysML→Canonical semantic mapping should be classifiable:

```text
CONFIRMED
TENTATIVE
NEEDS_RESEARCH
REJECTED
```

Do not encode tentative semantic assumptions as irreversible schema rules.

## 11. MVP-1 SysMLFactSnapshot

规范契约（2026-09-04 起）：`docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md`
（实现：`src/fmea_agent/adapters/sysml/contracts.py`）。

Envelope：

```json
{
  "source": { },
  "elements": [],
  "relationships": [],
  "diagnostics": [],
  "load_status": "ok"
}
```

This is intentionally closer to source facts than FMEA semantics.

## 12. Cross-Adapter Consistency Goal

For the same source model:

```text
OpenSysML Adapter
      ↓
Canonical A

SysML Repository Adapter
      ↓
Canonical B
```

Expected:

```text
semantically equivalent(A, B)
```

Differences must be diagnosable as:

- source/model-version difference;
- source representation difference;
- adapter mapping bug;
- unsupported semantic.

## 13. Future Data Sources

Future adapters may include:

```text
BOM
PLM
Requirements database
Capella
Simulink
other MBSE
```

They should map into the Canonical System Model rather than modify the FMEA domain to suit each technology.

## 14. Non-goals

The CSM is not:

- a full replacement for SysML;
- a full digital twin;
- a CAD geometry model;
- a failure ontology;
- an LLM prompt format.

It is the minimum stable engineering-fact model needed by FMEA.

## 15. MVP-1D Canonical Mapping (2026-09-04)

First mapping implementation delivered (`src/fmea_agent/adapters/sysml/canonical_mapping.py`,
`CanonicalSystemMapper`):

- aggregate `CanonicalSystemModel` = `system` + `components` + `functions` +
  `notices` (in `src/fmea_agent/domain/system_model.py`); ids unique and
  component parents resolve (validation, §9);
- canonical ids are generated by the mapping layer (`system-1` /
  `component-N` / `function-N`, per-kind counters in snapshot order), never
  taken from source identity; cross-version stability is not claimed
  (Open Research Question #1); source identity is retained in
  `SourceReference.source_element_id`;
- root selection and per-concept mapping rules with CONFIRMED /
  TENTATIVE / NEEDS_RESEARCH / DEFERRED statuses:
  `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md`;
- `CanonicalMappingError` when no system root can be selected (0 or
  multiple candidates, invalid explicit root);
- unsupported / unmapped source elements produce `MappingNotice` records,
  never silently dropped; partial snapshots map observed facts plus a
  model-level NEEDS_RESEARCH notice.
