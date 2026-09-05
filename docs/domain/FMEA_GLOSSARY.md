# FMEA Agent 术语表

本术语表是代码、提示词、schema 和文档的默认术语来源。

| 术语 | 项目含义 |
|---|---|
| Item | FMEA 分析中的系统、子系统、组件或分析对象 |
| Function | 对分析对象预期的行为 / 性能 |
| Functional Requirement | 约束预期功能 / 性能的需求 |
| Failure Mode | 分析对象 / 功能未能满足预期的方式 |
| Failure Cause | 可能导致失效模式的条件、事件或原因 |
| Failure Mechanism | 退化 / 失效发生所经过的物理 / 逻辑机理 |
| Local Effect | 分析对象本身或其紧邻范围内的影响 |
| Next Higher Level Effect | 对下一个包含层级 / 系统层级的影响 |
| End Effect | 分析所考虑的最高相关系统 / 任务 / 用户后果 |
| Prevention Control | 旨在预防 / 减少起因或发生的现有控制 |
| Detection Control | 旨在后果发生前探测起因 / 失效的现有控制 |
| Evidence | 支撑事实、候选项或决策的可追踪来源 |
| SourceReference | 回溯到原始工程模型 / 文档 / 记录的定位信息 |
| Candidate | 机器生成或检索到、尚未批准的分析内容 |
| Reviewed | 已经审查人员检查、但不一定正式批准的内容 |
| Approved | 已明确接受用于相应工程工作流的内容 |
| Unknown | 确实无法获得 / 尚未确定的信息 |
| Canonical System Model | 上层 FMEA 使用的、独立于工具的规范化模型 |
| SysMLFactSnapshot | 在规范语义映射之前，对解析器 / API 层 SysML 事实的捕获 |
| Failure Knowledge | 关于模式、起因、影响、机理和控制的历史 / 结构化证据 |
| RiskStrategy | 用于 FMEA 风险评估的可替换算法 / 策略 |
| Adapter | 将外部技术转换到内部端口 / 模型的集成层 |
| Port | 核心 / 应用逻辑与外部实现之间的项目自有接口 |
| MCP | 外部工具 / 资源协议层；不是领域模型 |
| Ground Truth | 用于评估的、经人工验证的参考答案 |
| Unsupported Claim | 缺乏足够系统事实、规则、证据或经批准推断路径支撑的输出断言 |

## 必须区分的概念

```text
Failure Mode ≠ Failure Cause
Failure Cause ≠ Failure Mechanism
Failure Mode ≠ Failure Effect
Evidence confidence ≠ failure probability
SysML fact ≠ LLM inference
Candidate ≠ Approved result
```

## 命名指引

代码中优先使用稳定的领域名称。

推荐：

```text
failure_mode
failure_cause
local_effect
next_higher_level_effect
end_effect
```

避免使用以下含义模糊的通用名称：

```text
fault
problem
impact
reason
result
```

除非来源格式明确使用这些名称，并由适配器执行映射。

## 中文文档术语书写约定

项目自有文档以简体中文（zh-CN）为主体。重要术语首次出现时可以使用“中文名称（English Canonical Term）”；后续按语境使用中文或规范英文术语，无需逐句中英双语。

| 中文名称 | English Canonical Term |
|---|---|
| 失效模式 | Failure Mode |
| 失效起因 | Failure Cause |
| 失效机理 | Failure Mechanism |
| 失效影响 | Failure Effect |
| 预防控制 | Prevention Control |
| 探测控制 | Detection Control |
| 推荐措施 | Recommended Action |
| 证据 | Evidence |
| 来源追踪 | Provenance |
| 实体解析 | Entity Resolution |
| 规范系统模型 | Canonical System Model |
| 故障知识 | Failure Knowledge |
| 候选 FMEA | Candidate FMEA |

中文名称用于文档叙述，不替换代码标识符。类名、函数名、变量名、enum 值、schema 标识符、API / 协议名、技术 / 产品 / 标准 / 包的规范名称必须保持原形；例如 `FailureKnowledgeRepository`、`FailureModeCandidate`、`Evidence`、`SourceReference` 和 `RiskStrategy` 不改名。

状态 token（如 `NOT_STARTED`、`READY_FOR_REVIEW`、`ACCEPTED`）、路径、URL、命令、Git branch / tag / SHA 和精确 commit message 保持原形。代码块、CLI / 测试 / Git 输出、Cypher、JSON 及原始证据和第三方原文不因中文化而改写。

失效模式、失效起因、失效机理和失效影响须保持语义区分；从历史来源检索的预防 / 探测控制不得混同于 Agent 生成的推荐措施。
