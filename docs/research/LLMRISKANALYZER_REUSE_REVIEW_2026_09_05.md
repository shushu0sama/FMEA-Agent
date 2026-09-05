# LLMRiskAnalyzer 复用评估

Lifecycle: REFERENCE
日期：2026-09-05
结论：R — Reference only。可参考字段建议交互；当前不复制代码、提示词、样例数据或 UI 资产。
本记录不是新的 Demo Spec，也不表示 D1–D7 已开工。

## 1. 核查范围与可复现来源

用户提供[作者仓库](https://github.com/YuchenXia/LLMRiskAnalyzer)，本次通过 GitHub API 解析 main，
固定提交为 `03dfd4cf3e6095d71f6b78317f333911016a65e3`（提交时间 2026-06-18T09:59:20Z）。
读取该提交的目录树、README、模型/服务/提示代码、当前前端 script.js 与依赖清单。
仅静态检查；未安装、启动上游服务、访问在线 Demo、提交本地工程资料或调用上游模型。

GitHub API 的 license 为 null；完整文件树中未发现 LICENSE/COPYING 文件，
README 未给出许可证声明。当前未获得代码再利用的明确许可依据。
公开可读不等于允许直接纳入本项目；如需复制，先确认作者许可及代码/数据/资产适用范围。
依据：[GitHub 许可证说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。
本次未联系作者，也不需要因许可未知阻塞本项目自有实现。

主要核查文件 SHA-256：

| 文件（source_code/ 下） | SHA-256 |
|---|---|
| FEMA_data_model.py | `557db9c92c6f10e41208a44827bf95f5eef80c65b83d3795f0fd2f9472016092` |
| agents.py | `7e95d177a1d51f16f0d0256a05930f2c1fbf210254d9b711c5ae7bc252a633b9` |
| app.py | `05d20564b4f50081d5147ff700d1b29d637898f371f745fe500d01e793268d8c` |
| llm.py | `7474a09bef177a055c9a50f45896a48ee18310cfe00ba70b494dc42fca103c1a` |

上述文件按下载 UTF-8 文本重新编码计算；requirements.txt 为 UTF-16 BOM 文本，初次 UTF-8 读取失败，
识别编码后成功读取 51 条固定版本依赖。未将读取失败误判为上游程序运行失败。

## 2. 可参考的能力与采用边界

| 能力 | 源码依据 | 本项目判断 |
|---|---|---|
| 单元格保留当前值与 AI 多条建议，建议含理由/说明 | FEMA_data_model.py:14–53 | R；支持候选与当前值分开呈现，但理由不等于外部证据 |
| 结合整表、当前行、目标字段及用户文字生成局部建议 | agents.py:5–53 | R；可启发提示任务拆分，项目应自行编写并加入来源与未知约束 |
| 编辑、选择建议、显示说明及 CSV 下载 | static/script.js、app.py | R；候选说明可用于 D6；完整单元格编辑/采纳工作流未在本次加进 Demo |
| JSON/CSV 表格转换 | FEMA_data_model.py:92–157 | R；直接复用标准库及既有 Pydantic 更符合当前契约，无需搬入另一套表格模型 |
| Flask 服务与 OpenAI/Together 模型调用 | app.py、llm.py、requirements.txt | R；保留既定 Streamlit、DeepSeek 端口和 LangGraph，不替换架构 |
| S/O/D/RPN 字段、示例 FMEA | FEMA_data_model.py:78–84、dataset/ | 不作评分规则来源或工程 gold；未确认样例审核、许可和适用性 |

固定版本源码：[数据模型](https://github.com/YuchenXia/LLMRiskAnalyzer/blob/03dfd4cf3e6095d71f6b78317f333911016a65e3/source_code/FEMA_data_model.py)、
[建议生成](https://github.com/YuchenXia/LLMRiskAnalyzer/blob/03dfd4cf3e6095d71f6b78317f333911016a65e3/source_code/agents.py)、
[服务](https://github.com/YuchenXia/LLMRiskAnalyzer/blob/03dfd4cf3e6095d71f6b78317f333911016a65e3/source_code/app.py)、
[前端](https://github.com/YuchenXia/LLMRiskAnalyzer/blob/03dfd4cf3e6095d71f6b78317f333911016a65e3/source_code/static/script.js)。

## 3. 直接移植前需要处理的差异

以下为静态代码判断，不是已复现的线上事故：

- agents.py 仅 JSON 解析，不验证领域 schema/证据引用；app.py:66–71 直接取五项，
  模型返回 None、少项或错误字段时缺少此处的防护。
- app.py:57 在后续范围检查之前读取行；输入需先校验。
- agents.py:51/100 与 app.py:97 使用固定输出文件；同时请求存在覆盖风险。
- static/script.js:259/267/322 将生成字段拼接至 innerHTML，迁移时需要改为安全文本渲染。
- CSV 导出只保留单元格 value，不保留 AI 建议、理由及来源；也未见公式前缀转义。
- 已读源码/目录树未见 SysML→CSM、Neo4j 检索、适用性判断或本项目所需的来源身份契约；
  不应把该原型当成本项目端到端证据分析的实现。
- 目录树未见自动化测试套件；未复现实验或确认工程准确率。51 条依赖不能整体导入当前锁文件。

即使后续获得许可，也应按模块核对收益、隔离适配并添加契约测试，不能原样运行其整个应用替代现有工程。

## 4. 对当前推进的影响

本次采用决策只限研究分类 R；新增依赖 NONE，复制第三方代码/数据/资产 NONE。
保留 [Demo Spec](../specs/DEMO_V1_END_TO_END_FMEA.md) 与
[Demo Plan](../plans/DEMO_V1_IMPLEMENTATION_PLAN.md) 的 D1–D7 顺序。
近期重点仍是固定演示资料、真实检索、生成校验和可追溯导出。

现有外部 SysML 工作区继续作为只读来源库；首例仍为项目自有 typed_inside_probe.sysml，
后续 D1 按计划生成 examples/demo_v1 包。本次没有迁移外部案例，也没有生成该包。
若将来选择外部案例，只复制选定模型及必要依赖，记录仓库/commit/原路径/hash/许可证，
保留许可证原文与 THIRD_PARTY_NOTICES；不将整个资料库或绝对 D 盘路径变成运行依赖。

会话恢复说明与启动语已补入 [文档导航](../README.md)，
Stage 内交接扩展沿用[既有模板](../records/templates/SESSION_HANDOFF_TEMPLATE.md)，避免创建第二份长期进度台账。

## 5. 本地验证与范围

本项目核查起点为 `648009ba5a571a15bb9706dabb95afb3f6db8bbd`，
分支 `codex/demo-v1-spec-plan`，起始工作区干净。
本次仅修改本报告、DEPENDENCY_INVENTORY、docs/README、既有交接模板与 PROGRESS。
不修改源码、测试、依赖锁、基准 gold 或已接受的 Spec/Plan；不推送、合并或移动 tag。

LOCAL：`.venv/Scripts/python.exe scripts/verify.py` 通过：223 passed in 12.23s、
Ruff PASS、mypy PASS（24 source files）。现有 SysML 与 benchmark 回归包含在套件内。
这验证本项目既有基线，不验证上游原型、Demo 实现或真实工程分析质量；本次未开展独立审核。
LOCAL 文档检查：5 份文档围栏与 29 个相对链接目标有效；`git diff --check` 通过。
