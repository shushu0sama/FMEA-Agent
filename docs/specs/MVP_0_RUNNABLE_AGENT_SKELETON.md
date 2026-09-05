# MVP-0 规格说明 — 可运行的 FMEA Agent 骨架

## 1. 目标

创建首个可运行的 FMEA Agent 纵向切片。

目的**不是**达到工程质量的 FMEA 智能水平。

目的是验证以下链路：

```text
input
→ domain models
→ workflow
→ replaceable repositories
→ candidate analysis
→ structured output
```

并确保架构边界正确。

## 2. 用户故事

作为开发者 / 研究人员，我可以运行：

```bash
python -m fmea_agent demo examples/simple_pump.json
```

并获得结构化候选 FMEA 输出，而无需：

- 网络访问；
- SysML server；
- Neo4j；
- 向量数据库；
- 外部 LLM；
- MCP。

## 3. 输入示例

```json
{
  "system": {
    "id": "hydraulic-system",
    "name": "Hydraulic System"
  },
  "components": [
    {
      "id": "hydraulic-pump",
      "name": "Hydraulic Pump",
      "functions": [
        {
          "id": "provide-pressure",
          "name": "Provide Hydraulic Pressure"
        }
      ]
    }
  ]
}
```

## 4. Fixture 故障知识示例

```json
{
  "item_name": "Hydraulic Pump",
  "function_name": "Provide Hydraulic Pressure",
  "failure_modes": [
    {
      "name": "Loss of hydraulic pressure",
      "cause": "Demo mechanical failure",
      "local_effect": "Required outlet pressure is unavailable",
      "evidence_id": "demo-failure-library:001"
    }
  ]
}
```

## 5. 工作流

图应暴露符合 AIAG-VDA 形态的步骤：

```text
Planning & Preparation
Structure Analysis
Function Analysis
Failure Analysis
Risk Analysis
Optimization
Results Documentation
```

MVP 行为：

| 步骤 | MVP-0 行为 |
|---|---|
| 策划和准备 | 创建 AnalysisContext |
| 结构分析 | 加载 fixture 系统 / 组件 |
| 功能分析 | 加载功能 |
| 失效分析 | 检索 fixture 候选项 |
| 风险分析 | 显式为 `NOT_EVALUATED` |
| 优化 | 显式为 `SKIPPED` |
| 结果文件化 | 序列化候选 JSON |

## 6. 架构

必需概念：

```text
domain/
application/ports/
adapters/inmemory/
agents/
cli/
```

必需端口：

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

默认演示可以不调用 `LLMClient`。

## 7. 最小领域模型

系统：

```text
System
Component
Function
SourceReference
```

FMEA：

```text
AnalysisContext
FMEAItem
FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
Evidence
RiskAssessment
```

## 8. 输出

语义结构示例：

```json
{
  "analysis_id": "...",
  "method": "AIAG_VDA",
  "item": "Hydraulic Pump",
  "function": "Provide Hydraulic Pressure",
  "failure_mode": {
    "value": "Loss of hydraulic pressure",
    "status": "CANDIDATE"
  },
  "cause": {
    "value": "Demo mechanical failure",
    "status": "CANDIDATE"
  },
  "effects": [
    {
      "level": "LOCAL",
      "value": "Required outlet pressure is unavailable"
    }
  ],
  "risk": {
    "status": "NOT_EVALUATED"
  },
  "evidence": [
    {
      "source": "demo-failure-library:001"
    }
  ]
}
```

## 9. 非目标

MVP-0 不实现：

- OpenSysML；
- SysML API；
- 完整 Canonical System Model；
- Neo4j；
- Qdrant；
- Docling；
- MCP；
- 完整 AIAG-VDA 风险规则；
- PDF/Excel UI；
- 自主多 Agent 行为；
- 人工审查持久化；
- 失效传播。

## 10. 测试

必需测试：

### 单元测试

- 领域模型校验；
- 内存仓库行为；
- 风险为 `NOT_EVALUATED`；
- 输出序列化。

### 工作流测试

- Fixture 流经所有步骤；
- 每一步都有显式状态。

### 冒烟测试

```text
CLI demo exits 0
output JSON exists
output validates
```

## 11. 验收标准

```text
[ ] fresh environment can install project
[ ] all configured verification checks pass
[ ] default demo requires no external service
[ ] output is structured, not free-form text
[ ] workflow uses replaceable ports
[ ] no external framework leaks into domain models
[ ] risk is not fabricated
[ ] evidence points to fixture
[ ] PROGRESS.md updated
```

## 12. 成功定义

MVP-0 成功的条件是：

> 项目具有一个小型但分层正确、可执行的 FMEA 工作流，后续可以用真实工程集成逐一替换各个桩。
