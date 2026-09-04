# 项目语言与术语规范
## Language and Terminology Policy v0.1

从 MVP-1 起采用：

> **中文叙述 + English Canonical Terminology**

规则：

1. Spec / Plan / ADR / Research / Benchmark / PROGRESS 的正文默认使用中文。
2. Python 类、函数、变量、Protocol、Enum、JSON field、API、CLI、Git branch、Git commit、目录名保持英文。
3. SysML metatype 原样保留，例如 `PartDefinition`、`PartUsage`、`ActionUsage`。
4. 第三方项目名不翻译，例如 `OpenSysML`、`LangGraph`、`Neo4j`、`MCP`。
5. 领域术语首次出现使用“中文（English Canonical Term）”，例如“规范系统模型（Canonical System Model）”。
6. FMEA 术语以 `docs/domain/FMEA_GLOSSARY.md` 为唯一真源。
7. 不创建中文代码对象或中英文双份镜像文档。
8. 旧英文文档不一次性翻译，采用渐进式规范化：修改时再逐步中文化。
