# FMEA Agent Benchmark Specification v0.1

## 1. Purpose

Every new capability must be evaluated against the layer it is intended to improve.

The benchmark system prevents:

> "the system has more features, therefore it must be better."

## 2. Evaluation Layers

```text
L0 Software / Contract
L1 System Fact Extraction
L2 Canonical Mapping
L3 Failure Knowledge Retrieval
L4 FMEA Candidate Quality
L5 Verification / Human Review
L6 Failure Propagation
L7 Dynamic Update
```

## 3. MVP-0 Benchmark

MVP-0 is a software architecture benchmark, not an AI-quality benchmark.

### Required

1. Fresh install succeeds.
2. Unit tests pass.
3. Demo command exits successfully.
4. All seven AIAG-VDA-shaped workflow stages produce an explicit status.
5. Structured JSON output validates.
6. Risk may be `NOT_EVALUATED`.
7. Optimization may be `SKIPPED`.
8. Evidence points to demo fixture source.
9. No external service is required.

### Pass/Fail

MVP-0 passes only if the end-to-end vertical slice is repeatable offline.

## 4. Level 1 — SysML Fact Extraction

Primary datasets:

```text
OMG SysML v2 Training examples
OMG/Simple Vehicle
```

Measure:

- element extraction precision;
- element extraction recall;
- relationship extraction precision;
- relationship extraction recall;
- source-reference completeness.

First implementation may use exact expected fixture counts and IDs before larger statistical evaluation.

## 5. Level 2 — Canonical Mapping

Evaluate:

```text
source fact
→ expected canonical concept
```

Metrics:

- mapping accuracy;
- reference integrity;
- canonical relationship correctness;
- cross-adapter consistency.

Important test:

```text
OpenSysML canonical output
vs
Repository API canonical output
```

for the same model/version.

## 6. Level 3 — Failure Knowledge Retrieval

Datasets:

- curated historical FMEA;
- curated failure records;
- selected technical documents.

Metrics:

```text
Recall@K
Precision@K
MRR (optional)
Evidence Coverage
Entity Resolution Accuracy
Source Trace Completeness
```

## 7. Level 4 — FMEA Candidate Quality

Ground truth should be human-verified.

Metrics:

```text
Failure Mode Precision
Failure Mode Recall
Cause Correctness
Effect Correctness
Cause–Mode–Effect Consistency
Unsupported Claim Rate
Evidence Coverage
```

Prefer separate evaluation for:

```text
local_effect
next_higher_level_effect
end_effect
```

## 8. Level 5 — Verification / Human Collaboration

Metrics:

```text
Accept Rate
Modify Rate
Reject Rate
Evidence Request Rate
Review Time
Reviewer Agreement
Validator True-positive/False-positive rates
```

## 9. Level 6 — Failure Propagation

Primary systems:

```text
Delivery Drone
CubeSat / Spacecraft
```

Metrics:

```text
Path Precision
Path Recall
Effect-Level Accuracy
Unsupported Propagation Rate
```

## 10. Level 7 — Dynamic FMEA

Controlled model-change experiments.

Metrics:

```text
Affected-item Precision
Affected-item Recall
Update Omission Rate
Version Trace Completeness
Unnecessary Reanalysis Rate
```

## 11. Benchmark Dataset Levels

Recommended progression:

### Dataset A — Unit semantic fixtures

Tiny hand-crafted models.

### Dataset B — Simple Vehicle

First end-to-end engineering-model benchmark.

### Dataset C — Delivery Drone

Cross-level structure/function/interface benchmark.

### Dataset D — CubeSat / spacecraft

Aerospace-domain benchmark.

### Dataset E — larger heterogeneous system

Scalability only after earlier levels are stable.

## 12. Ground Truth Format

Every benchmark case should record:

```text
case_id
source_model_version
input
expected_output
evidence
reviewer
review_status
notes
```

FMEA ground truth should preserve uncertainty.
Do not force one answer when multiple engineering answers are defensible.

## 13. Regression Policy

Every accepted benchmark becomes a regression case unless explicitly retired.

An architecture/dependency upgrade must not silently reduce benchmark performance.

## 14. Threshold Policy

Do not invent arbitrary research thresholds too early.

Use three states:

```text
BASELINE_MEASURED
TARGET_PROPOSED
RELEASE_GATE
```

A numerical `RELEASE_GATE` becomes mandatory only after sufficient benchmark data exists and the team has explicitly accepted it.

## 15. Experiment Record

Important AI changes should record:

```text
Hypothesis
Baseline
Variant
Dataset
Metrics
Result
Conclusion
Decision
```
