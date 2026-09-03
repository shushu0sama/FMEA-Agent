# FMEA Agent Glossary

This glossary is the default terminology source for code, prompts, schemas and documentation.

| Term | Project meaning |
|---|---|
| Item | System, subsystem, component or analysis object under FMEA |
| Function | Intended behavior/performance expected from an item |
| Functional Requirement | Requirement constraining an intended function/performance |
| Failure Mode | Manner in which an item/function fails to fulfill intent |
| Failure Cause | Condition/event/reason that can lead to a failure mode |
| Failure Mechanism | Physical/logical mechanism through which degradation/failure occurs |
| Local Effect | Effect at or immediately around the analyzed item |
| Next Higher Level Effect | Effect at the next containing/system level |
| End Effect | Highest relevant system/mission/user consequence considered by the analysis |
| Prevention Control | Existing control intended to prevent/reduce cause or occurrence |
| Detection Control | Existing control intended to detect cause/failure before consequence |
| Evidence | Traceable source supporting a fact, candidate or decision |
| SourceReference | Locator back to the originating engineering model/document/record |
| Candidate | Machine-generated or retrieved analysis content not yet approved |
| Reviewed | Content examined by a reviewer but not necessarily formally approved |
| Approved | Content explicitly accepted for the applicable engineering workflow |
| Unknown | Information that is genuinely unavailable/undetermined |
| Canonical System Model | Tool-independent normalized model used by upper FMEA layers |
| SysMLFactSnapshot | Parser/API-level capture of SysML facts before canonical semantic mapping |
| Failure Knowledge | Historical/structured evidence about modes, causes, effects, mechanisms and controls |
| RiskStrategy | Replaceable algorithm/policy for FMEA risk evaluation |
| Adapter | Integration layer converting an external technology to an internal port/model |
| Port | Project-owned interface between core/application logic and external implementation |
| MCP | External tool/resource protocol layer; not a domain model |
| Ground Truth | Human-verified reference answer used for evaluation |
| Unsupported Claim | Output claim lacking sufficient supporting system fact, rule, evidence or approved inference path |

## Mandatory Distinctions

```text
Failure Mode ≠ Failure Cause
Failure Cause ≠ Failure Mechanism
Failure Mode ≠ Failure Effect
Evidence confidence ≠ failure probability
SysML fact ≠ LLM inference
Candidate ≠ Approved result
```

## Naming Guidance

Prefer stable domain names in code.

Good:

```text
failure_mode
failure_cause
local_effect
next_higher_level_effect
end_effect
```

Avoid ambiguous generic names such as:

```text
fault
problem
impact
reason
result
```

unless a source format explicitly uses them and an adapter performs mapping.
