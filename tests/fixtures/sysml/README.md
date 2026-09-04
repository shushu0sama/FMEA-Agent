# SysML fixture provenance (MVP-1C)

All three `.sysml` fixtures are byte-for-byte copies of files already
verified against OpenSysML 0.4.0 + sysml-grpc v0.4.3 during the MVP-1A
spike and the 1C-0 dependency reproduction gate
(see `docs/research/OPENSYSML_SPIKE_REPORT.md` and
`docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md`).

Do not "fix" or prettify these files: the adapter contract tests assert
the exact diagnostic messages and element trees they produce.

| File | Origin | Expected behavior |
|---|---|---|
| `models/perform_probe.sysml` | self-built during MVP-1A spike (syntax from official Training Examples) | valid model; `load_status == "ok"`; full element tree including a performed action usage without typing facts (C4) |
| `models/invalid_syntax.sysml` | self-built during MVP-1A spike | 2 error diagnostics; partial snapshot with extractable elements |
| `models/unresolved_import.sysml` | official SysML-v2-Release training example `sysml/src/training/18. Action Performance/Action Performance Example.sysml`, unmodified (SHA-256 `0dc8639f…`, byte-identical to the upstream file) | 4 error diagnostics from the unresolved user-file import (C1); partial snapshot |
| `models/sibling_roots_probe.sysml` | self-built during MVP-1D (syntax from official Training Examples); verified against OpenSysML 0.4.0 + sysml-grpc v0.4.3 | valid model; two top-level packages (multiple root children) for traversal-order regression and multi-candidate root selection |
| `models/no_usage_probe.sysml` | self-built during MVP-1D; verified against OpenSysML 0.4.0 + sysml-grpc v0.4.3 | valid model with definitions only; no PartUsage candidate for system root |
| `models/typed_inside_probe.sysml` | self-built during MVP-1E; verified against OpenSysML 0.4.0 + sysml-grpc v0.4.3 (runtime probe: named typed ActionUsages nested in PartUsages carry real `type_facts` and real owner traversal) | valid model; typed ActionUsages directly under the root partUsage and under a nested partUsage — allocation evidence for `Function.allocated_to` |

External source record for `unresolved_import.sysml`
(see `docs/research/SYSML_SOURCE_CATALOG.md`):

```text
repository: https://github.com/Systems-Modeling/SysML-v2-Release
commit:     29a3d2acdd96cff872e7a55962a40400f3335 (tag 2026-07)
model:      sysml/src/training/18. Action Performance/Action Performance Example.sysml
license:    EPL-2.0
```

`snapshot_minimal.json` (MVP-1B) is a project-owned synthetic snapshot
fixture, not a parser output.
