# Neo4j Failure Knowledge Baseline

Status: REFERENCE

## 1. Purpose

This document records the existing Legacy Failure Knowledge Graph baseline for
MVP-2 planning. It is research / baseline evidence, not production adapter
implementation.

MVP-2 must treat the existing Neo4j graph as read-only.

## 2. Database Baseline

```text
Neo4j version: 5.26.0
Graph role:    Legacy Failure Knowledge Graph
MVP-2 role:    read-only retrieval source
```

MVP-2 does not rebuild this database.

## 3. Node Labels and Counts

| Label | Count |
|---|---:|
| 故障起因 | 337 |
| 故障模式 | 120 |
| 下一低分析层次 | 111 |
| 预防控制措施 | 100 |
| 下一低层次功能 | 64 |
| 探测控制措施 | 58 |
| 故障影响 | 46 |
| 功能 | 23 |
| 关注要素层次 | 15 |
| 上一高层次功能及要求 | 4 |

Approximate domain node total: 878.

## 4. Relationship Schema and Counts

| Source | Relationship | Target | Count |
|---|---|---|---:|
| 故障模式 | 故障起因 | 故障起因 | 413 |
| 故障模式 | 预防控制措施 | 预防控制措施 | 273 |
| 故障模式 | 探测措施 | 探测控制措施 | 168 |
| 故障模式 | 故障影响 | 故障影响 | 135 |
| 关注要素层次 | 故障模式 | 故障模式 | 129 |
| 关注要素层次 | 下一低分析层次 | 下一低分析层次 | 111 |
| 下一低分析层次 | 下一低层次功能 | 下一低层次功能 | 109 |
| 关注要素层次 | 功能 | 功能 | 23 |
| 关注要素层次 | 上一高层次功能及要求 | 上一高层次功能及要求 | 4 |

Approximate relationship total: 1365.

## 5. Properties and Indexes

Current main domain node properties are limited primarily to:

```text
name
```

Relationship properties:

```text
NONE
```

Known infrastructure:

- name indexes for corresponding domain labels;
- n10s infrastructure is present;
- `n10s__Resource.uri` unique constraint is present.

Detailed `SHOW INDEXES` / `SHOW CONSTRAINTS` output is not present in this
repository baseline. Therefore exact index names, index type, owning label,
properties, state and full constraint inventory are `UNKNOWN` here rather than
invented.

Minimum index / constraint evidence required before MVP-2 implementation:

| Category | Known baseline | Missing from repo evidence | MVP-2A capture requirement |
|---|---|---|---|
| Domain node indexes | name indexes exist for corresponding domain labels | exact names, labels, properties, type and state | sanitized `SHOW INDEXES` table |
| n10s constraint | `n10s__Resource.uri` unique constraint exists | exact name/type/state and any related constraints | sanitized `SHOW CONSTRAINTS` table |
| Relationship indexes | none reported | whether any exist | sanitized `SHOW INDEXES` table |

The capture must be read-only and must not include connection strings,
usernames, passwords or other secrets.

## 6. Source Excel Relationship

The legacy import path was:

```text
Excel
→ unique values per column become nodes
→ relationships are created per row
→ Neo4j
```

The graph therefore contains useful column-value co-occurrence structure, but it
does not preserve complete source-row provenance as a first-class model.

Source workbook identity is not present in this repository baseline:

```text
workbook path/name: UNKNOWN
sheet name:         UNKNOWN
file hash:          UNKNOWN
source version:     UNKNOWN
import timestamp:   UNKNOWN
```

The user-provided legacy importer evidence indicates column-value nodes and
row-created relationships for the labels and relationship types listed above.
The original source row ID is not retained in the graph baseline.

MVP-2A must capture sanitized source-file identity or explicitly confirm that it
is unavailable before production adapter work begins.

## 7. Legacy Import Script Behavior

The historical importer is LEGACY / REFERENCE EVIDENCE only.

Known behavior:

- uses `py2neo`;
- connects to local Neo4j in the old implementation;
- includes `graph.delete_all()` during initialization;
- contains historical hard-coded credentials;
- creates nodes mainly with `name`;
- does not preserve provenance, source row or source version;
- has a semantic mismatch in the `rel5` comment: the comment resembles
  "Function to Failure Mode", while the actual relationship created is
  `关注要素层次 → 故障模式`.

The importer should not be used as executable production code. If future work
needs to inspect it, inspect it only as legacy reference evidence and redact all
credential material from notes and commits.

## 8. Known Strengths

The graph is strongest for:

```text
FailureMode
→ Cause
→ Effect
→ Prevention Control
→ Detection Control
```

These relationships are directly relevant to MVP-2 failure knowledge retrieval.

## 9. Known Limitations

The graph does not directly encode the complete original FMEA row-level analysis
context:

```text
Component + Function + FailureMode
```

Known missing generic direct relationships include:

```text
下一低分析层次 → 故障模式
功能 → 故障模式
下一低层次功能 → 故障模式
```

MVP-2 must address this through adapter contracts, context reconstruction and
entity resolution. This limitation is not a reason to rebuild the database for
MVP-2.

## 10. Security Warning

Do not copy secrets from the legacy script into this repository.

Do not run the legacy importer against a production database.

The legacy script contains hard-coded credential material and `delete_all()`.
It must not be added to the production path as-is.

## 11. MVP-2 Decision

MVP-2 Neo4j integration is read-only.

Out of scope for MVP-2:

- schema migration;
- data rebuild;
- production import script;
- knowledge write-back;
- Candidate to Approved write flow;
- real LLM / RAG / Qdrant integration;
- AIAG-VDA S/O/D/AP implementation.

## 12. Baseline Capture Method for MVP-2A

Before MVP-2 implementation starts, collect read-only baseline evidence from the
existing database:

- Neo4j version;
- label counts;
- relationship schema and counts;
- sampled node properties per label;
- sampled relationship properties per type;
- sanitized index inventory;
- sanitized constraint inventory;
- n10s component presence and version when available;
- source workbook identity or explicit `UNKNOWN` status.

Do not run destructive importer code. Do not include secrets in the record.
