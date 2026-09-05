# FMEA Agent 基准规格说明 v0.1

## 1. 目的

每项新能力都必须针对其预期改进的层级进行评估。

基准体系旨在避免以下判断：

> “系统功能更多，所以一定更好。”

## 2. 评估层级

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

## 3. MVP-0 基准

MVP-0 是软件架构基准，不是 AI 质量基准。

### 必需项

1. 全新安装成功。
2. 单元测试通过。
3. 演示命令成功退出。
4. 符合 AIAG-VDA 形态的七个工作流步骤均产出显式状态。
5. 结构化 JSON 输出通过校验。
6. 风险可以为 `NOT_EVALUATED`。
7. 优化可以为 `SKIPPED`。
8. 证据指向演示 fixture 来源。
9. 不需要外部服务。

### 通过 / 失败

只有端到端纵向切片可离线重复运行时，MVP-0 才通过。

## 4. Level 1 — SysML 事实提取

主要数据集：

```text
OMG SysML v2 Training examples
OMG/Simple Vehicle
```

测量项：

- 元素提取精确率；
- 元素提取召回率；
- 关系提取精确率；
- 关系提取召回率；
- 来源引用完整性。

首次实现可以先使用 fixture 的精确预期数量和 ID，再进行更大规模的统计评估。

## 5. Level 2 — 规范映射

评估：

```text
source fact
→ expected canonical concept
```

指标：

- 映射准确率；
- 引用完整性；
- 规范关系正确性；
- 跨适配器一致性。

重要测试：

```text
OpenSysML canonical output
vs
Repository API canonical output
```

针对同一模型 / 版本。

## 6. Level 3 — 故障知识检索

数据集：

- 经整理的历史 FMEA；
- 经整理的失效记录；
- 选定的技术文档。

指标：

```text
Recall@K
Precision@K
MRR (optional)
Evidence Coverage
Entity Resolution Accuracy
Source Trace Completeness
```

## 7. Level 4 — FMEA 候选质量

参考真值应经过人工验证。

指标：

```text
Failure Mode Precision
Failure Mode Recall
Cause Correctness
Effect Correctness
Cause–Mode–Effect Consistency
Unsupported Claim Rate
Evidence Coverage
```

优先分别评估：

```text
local_effect
next_higher_level_effect
end_effect
```

## 8. Level 5 — 验证 / 人机协作

指标：

```text
Accept Rate
Modify Rate
Reject Rate
Evidence Request Rate
Review Time
Reviewer Agreement
Validator True-positive/False-positive rates
```

## 9. Level 6 — 失效传播

主要系统：

```text
Delivery Drone
CubeSat / Spacecraft
```

指标：

```text
Path Precision
Path Recall
Effect-Level Accuracy
Unsupported Propagation Rate
```

## 10. Level 7 — Dynamic FMEA

受控的模型变更实验。

指标：

```text
Affected-item Precision
Affected-item Recall
Update Omission Rate
Version Trace Completeness
Unnecessary Reanalysis Rate
```

## 11. 基准数据集层级

推荐递进顺序：

### 数据集 A — 单元语义 fixture

人工构建的微型模型。

### 数据集 B — Simple Vehicle

首个端到端工程模型基准。

### 数据集 C — Delivery Drone

跨层级的结构 / 功能 / 接口基准。

### 数据集 D — CubeSat / 航天器

航空航天领域基准。

### 数据集 E — 更大的异构系统

只有在前面层级稳定后才评估可扩展性。

## 12. 参考真值格式

每个基准案例应记录：

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

FMEA 参考真值应保留不确定性。
当多个工程答案均有合理依据时，不应强制只保留一个答案。

## 13. 回归政策

每个已接受的基准都成为回归案例，除非明确退役。

架构 / 依赖升级不得静默降低基准表现。

## 14. 阈值政策

不要过早编造任意研究阈值。

使用三个状态：

```text
BASELINE_MEASURED
TARGET_PROPOSED
RELEASE_GATE
```

只有在已有充分基准数据且团队明确接受后，数值 `RELEASE_GATE` 才成为强制要求。

## 15. 实验记录

重要 AI 变更应记录：

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
