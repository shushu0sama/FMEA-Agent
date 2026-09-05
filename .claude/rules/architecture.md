# 架构规则

- 领域模型必须独立于 LangGraph、Neo4j、MCP 和 LLM 提供方。
- 外部技术通过适配器与端口接入。
- 工程事实不得绕过 Canonical System Model。
- System Model 与 Failure Model 保持分离。
- MVP-0 优先采用桩实现和内存适配器，避免过早集成。
