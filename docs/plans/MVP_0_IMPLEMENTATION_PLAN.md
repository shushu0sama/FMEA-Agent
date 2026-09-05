# MVP-0 实施计划

> 每次实施一个任务。不要开始后续集成。

## 任务 0 — 检查与搭建骨架

目标：
创建/对齐 Python 包结构。

预期目录：

```text
src/fmea_agent/
  domain/
  application/
  adapters/
  agents/
  cli/
tests/
examples/
```

验证：
包可成功导入。

## 任务 1 — 最小领域契约

实现：

```text
SourceReference
System
Component
Function
AnalysisContext
FMEAItem
Evidence
FailureModeCandidate
FailureCauseCandidate
FailureEffectCandidate
RiskAssessment
```

使用带类型的 Pydantic 模型。

`FMEAItem` 在 MVP-0 中保持最小化：它表示规范系统元素在当前
`AnalysisContext` 中的分析对象身份。不要将 `Component` 和 `FMEAItem`
永久合并为同一个领域对象。

先写测试：

- 有效构造；
- 缺少必填 ID 时无效；
- enum/status 校验；
- 序列化。

## 任务 2 — 应用层端口

定义：

```text
SystemModelRepository
FailureKnowledgeRepository
LLMClient
RiskStrategy
```

端口定义中不得导入外部实现。

测试：
简单 fake 类满足预期行为。

## 任务 3 — 内存适配器

实现：

```text
InMemorySystemModelRepository
InMemoryFailureKnowledgeRepository
NoOpRiskStrategy
MockLLMClient
```

默认路径应不需要 `MockLLMClient`。

测试：
fixture 查找与数据缺失时的行为。

## 任务 4 — 工作流状态

定义结构化图状态。

建议字段：

```text
analysis_context
system
selected_component
function
failure_candidates
risk
stage_status
output
errors
```

不要使用非结构化聊天记录作为状态模型。

## 任务 5 — LangGraph 骨架

实现以下阶段：

```text
planning
structure_analysis
function_analysis
failure_analysis
risk_analysis
optimization
results_documentation
```

预期 MVP 状态：

```text
risk_analysis = NOT_EVALUATED
optimization = SKIPPED
```

测试：
状态流转到 END。

## 任务 6 — 演示夹具

新增：

```text
examples/simple_pump.json
examples/demo_failure_library.json
```

确保夹具明显为合成数据。

## 任务 7 — CLI

目标：

```bash
python -m fmea_agent demo examples/simple_pump.json
```

行为：

- 读取夹具；
- 运行图；
- 保存或打印结构化输出；
- 输入无效时返回非零退出码。

## 任务 8 — 冒烟测试

通过子进程或等效测试运行 CLI。

断言：

```text
exit code == 0
valid output JSON
risk.status == NOT_EVALUATED
evidence exists
```

## 任务 9 — 验证脚本

创建适合当前平台的验证入口。

至少包含以下逻辑检查：

```text
pytest
ruff check .
mypy src
```

如有工具尚未配置，在 MVP-0 收尾前补齐。

## 任务 10 — 文档交接

更新：

```text
PROGRESS.md
README.md
```

报告：

- 修改的文件；
- 测试；
- 已知限制；
- 下一个 MVP 建议。

## 完成门禁

MVP-0 通过验收标准之前，不得开始 OpenSysML 集成。
