# AIAG-VDA FMEA 语义配置 v1
## FMEA Agent 领域基线

## 1. 目的

本文档定义 FMEA Agent v1 使用的项目专用 FMEA 语义配置。

项目方法基线为：

```text
AIAG & VDA FMEA Handbook
First Edition, 2019
Seven-Step Approach
```

即《AIAG & VDA FMEA Handbook》第一版（First Edition，2019）所定义的
七步法（Seven-Step Approach）工作流形态。这里的“七”描述步骤数量，
不表示版本序号。

本文档定义软件需要的数据和工作流概念，**不**复制专有 S/O/D 评分表、
Action Priority 矩阵、手册长篇内容或其他受版权保护的评分内容。

实现生产级 S/O/D/AP 逻辑之前，项目必须取得授权规则来源。

## 2. 七步工作流形态

软件工作流应能够表达：

1. 策划和准备
2. 结构分析
3. 功能分析
4. 失效分析
5. 风险分析
6. 优化
7. 结果文件化

早期 MVP 的某一步可以为 `NOT_EVALUATED` 或 `SKIPPED`，但必须明确表示。

## 3. 核心分析对象

### 3.1 AnalysisContext

表达：

- 分析 ID；
- 标题；
- 范围；
- 系统 / 模型版本；
- 假设；
- 排除项；
- 分析状态；
- 方法配置；
- 创建 / 更新元数据。

### 3.2 FMEAItem

表示被分析的对象。

必需的基线字段：

```text
id
name
canonical_system_element_id
parent_item_id
source_refs
```

### 3.3 Function

表示预期行为或功能。

基线字段：

```text
id
name
description
item_id
requirement_refs
source_refs
```

### 3.4 FailureMode

定义：

> 功能 / 分析对象未能满足预期功能或需求的方式。

须与起因和影响区分。

基线字段：

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

定义：

> 可能导致失效模式的条件、机理、事件或较低层级原因。

基线字段：

```text
id
failure_mode_id
name
description
mechanism_id?
evidence_refs
```

### 3.6 FailureMechanism

可选的显式机理概念。

以下仅为语义类别示例：

```text
wear
fatigue
corrosion
software logic defect
electrical degradation
```

MVP-0 不强制每个起因都有机理。

### 3.7 FailureEffect

影响必须支持层级。

```text
LOCAL
NEXT_HIGHER_LEVEL
END_EFFECT
```

基线字段：

```text
id
failure_mode_id
level
affected_item_id?
description
evidence_refs
```

### 3.8 Control

至少支持以下语义类别：

```text
PREVENTION
DETECTION
```

从来源记录检索到的历史控制必须能与 Agent 生成的建议区分。

### 3.9 RecommendedAction

表示候选或已批准的优化措施。

推荐措施是分析输出。除非来源证据明确支持相应解释，否则不得将其与历史预防控制或探测控制混淆。

### 3.10 Evidence

每个非简单候选项都可以关联证据。

证据可以支撑：

- 分析对象 / 功能事实；
- 失效模式；
- 起因；
- 影响；
- 风险建议；
- 优化建议。

## 4. 风险模型

通过策略接口实现风险评估。

```python
class RiskStrategy(Protocol):
    def evaluate(self, context: RiskContext) -> RiskAssessment:
        ...
```

可能的实现：

```text
NoOpRiskStrategy
AIAGVDARiskStrategy
FutureCriticalityStrategy
CustomEnterpriseRiskStrategy
```

### 4.1 MVP-0

允许的结果：

```text
risk_status = NOT_EVALUATED
```

### 4.2 未来 AIAG-VDA 实现

未来经授权的实现可以支持：

```text
Severity
Occurrence
Detection
Action Priority
```

规则不得由 LLM 编造。

## 5. 字段权威性

当前实现使用 `KnowledgeStatus` 值显式表示无依据的断言。长期语义应区分三个维度，而不是将其合并到一个字段：

```text
Origin axis:
FACT
RETRIEVED_KNOWLEDGE
INFERENCE
UNKNOWN

Analysis lifecycle axis:
CANDIDATE
NOT_EVALUATED

Review lifecycle axis:
REVIEWED
APPROVED
```

当前 enum / 代码在后续实现阶段之前无需改变。语义要求是：文档和输出不得将检索知识、推断、候选分析和批准视为等价。

推荐的状态词汇：

```text
FACT
RETRIEVED_KNOWLEDGE
INFERENCE
CANDIDATE
REVIEWED
APPROVED
UNKNOWN
```

示例政策：

| 字段 | 是否可自动填充 | LLM 是否可建议 | 人工确认 |
|---|---:|---:|---:|
| Item | 可以，来自模型 | 不可以 | 模型存在歧义时 |
| Function | 可以，来自模型 | 可以 | 重要功能 |
| Failure Mode | 检索所得 / 候选 | 可以 | 批准前必须确认 |
| Failure Cause | 检索所得 / 候选 | 可以 | 批准前必须确认 |
| Failure Effect | 候选 | 可以 | 批准前必须确认 |
| S/O/D | 仅在有规则 / 数据时 | 有限 | 正式发布必须确认 |
| AP | 从授权策略推导 | 不允许自由生成 | 正式发布必须确认 |
| Evidence | 检索所得 | 仅可总结 | 可审查证据相关性 |

## 6. 语义校验规则

最低规则：

1. FMEA 行需要分析对象和功能上下文。
2. Failure Mode 必须描述预期功能 / 需求的失效，不能仅重复起因。
3. Cause 和 Effect 不得静默合并。
4. 在可能的情况下，影响应标明影响层级。
5. 风险值必须声明其来源 / 策略。
6. 缺失信息必须保持为 `UNKNOWN` / `NOT_EVALUATED`，不得编造。
7. 已批准结果必须保留证据和审查元数据。

## 7. MVP-0 最小 Schema

MVP-0 只需要：

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

优化控制 / 措施可以保持可选。

## 8. 未来扩展

后续阶段可以增加：

- 更丰富的结构树；
- 功能网络；
- 预防 / 探测控制；
- 经授权的 AIAG-VDA AP 规则；
- 措施跟踪；
- 责任人 / 截止日期；
- 修订历史；
- 特殊特性；
- 企业扩展；
- 通过策略 / 配置分离支持其他 FMEA/FMECA 配置。

## 9. 非目标

不得将完整 FMEA 方法硬编码到 LangGraph 提示词中。

领域模型和校验器保持权威性。
