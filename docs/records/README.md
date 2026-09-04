# Development Records

唯一职责：

```text
记录“实际发生了什么”
```

即：

```text
Execution History
Stage Closeout
Release Record
```

## 结构

```text
docs/records/
├── README.md                        ← 本文件
├── bootstrap/
│   └── PROJECT_CLEANUP_REPORT.md
├── MVP_0/
│   └── MVP_0_CLOSEOUT.md
├── MVP_1/
│   ├── MVP_1A_OPENSYSML_SPIKE.md
│   ├── MVP_1B_SNAPSHOT_CONTRACTS.md
│   ├── MVP_1C_OPENSYSML_ADAPTER.md
│   ├── MVP_1D_CANONICAL_MAPPING.md
│   ├── MVP_1E_WORKFLOW_INTEGRATION.md
│   ├── MVP_1F_BENCHMARK_RELEASE.md
│   └── MVP_1_RELEASE.md
└── templates/
    ├── SESSION_HANDOFF_TEMPLATE.md
    ├── STAGE_CLOSEOUT_TEMPLATE.md
    └── MVP_RELEASE_TEMPLATE.md
```

## 规则

- 一个正式 Stage 一个 Closeout Record；一个完整 MVP 一个 Release Record。
- 小任务（单个 regression fix、小测试补充、普通重构）写入所属
  Stage Record 的 Closeout Fixes，不单独建文件。
- 详细证据只在一处：Stage Record 引用 `docs/research/` /
  `docs/architecture/` 报告，不复制内容。
- 记录真实演化：Plan 与执行不一致时记录演化，不重写历史。
- Session handoff 仅用于同一正式 Stage 因上下文过长需要换 Session；
  Stage 完成后以 Closeout Record 为正式历史。
- 治理规则见：
  `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md`。
