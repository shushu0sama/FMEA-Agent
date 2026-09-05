# 项目语言与术语规范
## 文档语言与术语政策 v0.1

MVP-1 已采用中文叙述与英文规范术语；G0A-L 将其扩展为项目自有文档的正式默认语言政策：

> **简体中文（zh-CN）叙述 + English Canonical Terminology**

规则：

1. 除非用户或当前任务明确要求英文，所有新建项目自有 Markdown 的正文必须以简体中文为主体；修改中文文档时，不得无理由改写为英文。范围包括 README、PROGRESS、AGENTS、CLAUDE、Spec、Plan、Architecture、ADR、Research Report、Benchmark Report、Stage Record、Release Record、Session Handoff、Coding Agent Prompt、Completion Report、Agent 记忆/交接文档与模板。
2. Python 类、函数、变量、Protocol、Enum、JSON field、API、CLI、Git branch、Git commit、目录名保持英文。
3. SysML metatype 原样保留，例如 `PartDefinition`、`PartUsage`、`ActionUsage`。
4. 第三方项目名不翻译，例如 `OpenSysML`、`LangGraph`、`Neo4j`、`MCP`。
5. 重要领域术语首次出现可使用“中文（English Canonical Term）”，例如“规范系统模型（Canonical System Model）”；后续按语境使用中文或 canonical term，不机械制作逐句双语。
6. FMEA 术语以 `docs/domain/FMEA_GLOSSARY.md` 为唯一真源。
7. 不创建中文代码对象或中英文双份镜像文档。
8. G0A-L 按用户授权集中中文化项目自有 Markdown，取代此前仅在修改时渐进翻译的安排。翻译只改变语言，不改变历史事实、Stage 状态、测试数量、commit SHA、基准结果、已知限制、当时计划与预测，不删除历史差异；非翻译事实问题另记后续任务。
9. source code、class/function/variable/enum/schema 标识符、JSON key、protocol/API/CLI 名称、file path、shell command、Cypher、URL、Git branch/tag/commit SHA/精确 commit message、technology/product/standard/library/package canonical name 和机器状态值保持英文或原始 canonical form。
10. 所有代码块、CLI/test/Git output、原始外部资料、原始导入证据、上游原文副本、vendor 文件、`LICENSE*` 与 `third_party/licenses/**` 保持原样。许可证必须逐字保留；短引用可保留原文，并用中文说明。
11. 不通过翻译重命名路径或生产类；不将 `NOT_STARTED` 等机器状态改成中文。不复制旧 importer 中的真实凭证。

本政策适用于 `docs/` 下全部项目自有文档（包括 `docs/foundation/` 的 REFERENCE 文档），
以及根目录与 Agent 配置目录内的项目自有 Markdown；第三方原文及任务明确禁止修改的文件除外。
正式 Documentation Language Gate 见
`docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` 第 14 节。
