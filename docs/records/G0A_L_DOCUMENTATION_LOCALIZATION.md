# G0A-L — 文档中文化与语言治理记录

Status: READY_FOR_REVIEW
日期：2026-09-05
证据分类：LOCAL；独立文档复核另行记录为 EXTERNAL_REVIEW。

## 1. 目标与授权范围

本任务是 Pre-MVP-2 Governance Baseline 的补充治理任务。按用户已批准的 G0A-L 要求，
将项目自有 Markdown 的正文统一为简体中文（zh-CN），同时保留英文技术标识符、原始代码块和历史事实。
本次只修改文档，不开发生产能力，不创建 MVP-2 Implementation Plan，不安装依赖、不访问或修改数据库，
不 push、不 tag、不 release。

## 2. Repository 基线与 Git 锚点

- Branch：`master`。
- 起始 HEAD：`4d38489f92c41ffa906c6d0b79a4fd34d6ecb422`。
- 上一治理提交：`docs: establish pre-MVP-2 governance baseline`，完整保留，不 amend、squash 或改写。
- 起始工作区：干净；本地比 `origin/master` 提前 1 个 commit。
- 稳定发布 tag 保持 `v0.1.1`；本次不创建或移动 tag。
- 本次 Commit：由包含本记录的独立文档提交锚定，可用下方命令取得完整 SHA；最终报告列出该 SHA。

```bash
git log -1 --format=%H -- docs/records/G0A_L_DOCUMENTATION_LOCALIZATION.md
```

开始前已执行并核对 `git status`、`git branch --show-current`、`git rev-parse HEAD`、
`git log --oneline --decorate -8`。用户提供的 G0A-L 请求是本次范围依据；本次没有 MVP-2 Plan。

## 3. 语言治理变更

- `AGENTS.md` 与 `CLAUDE.md` 保留原完整结构及各自加载入口；新增第 19 节文档语言政策。
- Governance 第 14 节加入正式 Documentation Language & Terminology Policy 和六项 Documentation Language Gate。
- 现有 `LANGUAGE_AND_TERMINOLOGY_POLICY.md` 扩展到全部项目自有文档，按本次授权取代仅在修改时渐进翻译的安排。
- `FMEA_GLOSSARY.md` 增加 13 项中文名称与 English Canonical Term 对照及书写规则，明确失效模式、起因、机理、影响的区别。
- 新建 Spec / Plan / Record / Session Handoff / Coding Agent Prompt / Completion Report 默认使用中文；保留用户或当前任务明确要求英文的例外。
- 修改中文文档时，不得无理由改写为英文；代码、schema、API、状态、路径、命令、Git 标识符及精确 commit message 保持原形。

## 4. P0 / P1 / P2 与模板

P0（15 份）：根目录治理入口、文档导航、V1 Product、V1 Architecture、当前 MVP-2 Spec、Neo4j Baseline、
FMEA Profile / Glossary、Governance 与当前记录模板均已中文化。

P1（34 份）：其余架构、ADR、评估、MVP-0/1 Spec、已有 Plan、研究及历史记录逐篇翻译；原本中文主体的文档仅补齐英文叙述和标题。

P2（2 份）：两篇 Foundation 本来已是中文主体，本次补齐少量英文叙述与通用标题，REFERENCE 地位和原有路线预测保持不变。

模板：Stage Closeout、MVP Release 和 Session Handoff 的正文标题与说明为中文。
`docs/prompts/` 当前没有 ACTIVE 文件：MVP-1 提示词仍为 HISTORICAL，旧 Coding Agent 模板仍为 SUPERSEDED。
旧模板的原始 fenced 样例保持不变；外围增加中文生成结构及当前授权优先的说明，不重新启用其旧推送规则。

额外项目自有文档：`.claude/rules/` 三份规则、`CLAUDE.local.example.md` 和
`THIRD_PARTY_NOTICES.md` 的项目叙述已中文化；未改变第三方归属、许可证名称、来源 URL、SHA 或原始材料。

## 5. 历史完整性与技术事实

翻译保留历史状态、测试数量、基准结果、Git 标识符、原计划、预测、限制与已记录差异。
所有既有 fenced blocks、inline code 和 URL 均与起始基线比较，详情见验证结果。

当前技术边界保持：真实 SysML v2 File Mode → `SysMLFactSnapshot` → Canonical System Model → 现有工作流。
已实现 CSM 子集仍为 `System`、`Component`、`Function`、`SourceReference`。
外部基线仍为 Neo4j 5.26.0 Legacy Failure Knowledge Graph，MVP-2 只读；已知 relationship properties 仍为 `NONE`。
Knowledge Write-back 不属于 MVP-2；LLM 不属于 MVP-2，规划在 MVP-3。

旧 importer 只作参考证据。保留硬编码凭证、`graph.delete_all()` 和
DO NOT RUN AGAINST PRODUCTION DATABASE 的风险含义，不复制真实凭证。

## 6. 验证证据

已在现有 `.venv` 中运行以下回归命令。使用 UV_NO_SYNC 与 UV_OFFLINE 禁止依赖同步及网络下载；未安装依赖。

```powershell
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
uv run python scripts/verify.py
```

| 检查 | 本次结果 | 分类 |
|---|---|---|
| pytest | 223 passed in 11.74s | LOCAL |
| ruff check . | All checks passed! | LOCAL |
| mypy src | 24 个源文件，未发现问题 | LOCAL |
| GitHub CI | NOT CONFIGURED；未运行 CI | CI |

文档检查使用临时 Python 命令，不新增仓库语言检查脚本。基线为 `4d38489f92c41ffa906c6d0b79a4fd34d6ecb422`。

| 文档检查 | 结果 | 分类 |
|---|---|---|
| `git diff --check` | PASS | LOCAL |
| Markdown 围栏平衡 | PASS；新增记录也单独检查 | LOCAL |
| 既有 fenced blocks | 585 个按 Git 文本行尾归一后逐块一致 | LOCAL |
| 既有 inline code、URL | 无丢失、无误译 | LOCAL |
| 原有日期、版本、测试数量与历史计数 | 历史数值无丢失；逐篇对照历史事实，术语 E2E 的中文化不计作数值变化 | LOCAL |
| 路径引用 | 原有引用保留，未引入失效链接 | LOCAL |
| 英文正文扫描 | 范围内无英文主体文件；排除代码块及受保护技术术语 | LOCAL |
| 凭证扫描 | 新增文本中私钥、URL 内凭证、常见令牌和秘密赋值模式均无命中 | LOCAL |
| 生产、测试、示例、依赖、第三方与许可证差异 | NONE | LOCAL |
| MVP-2 Plan 文件存在性 | 不存在 | LOCAL |

范围核验命令：

```bash
git diff --check
git diff --exit-code 4d38489 -- src tests examples pyproject.toml uv.lock third_party LICENSE LICENSE.md LICENSE.txt
```

检查代码块时只归一 Git 的文本行尾，不修改代码块内容。秘密信息扫描只输出命中类别和数量，不输出疑似秘密值。
既有路径包含规划占位路径和历史外部研究环境路径，保留其原义；不将这些引用误报为新失效仓库路径。

基准影响：本次未修改基准数据、gold 或生产行为；223 项回归包含既有 11 项 benchmark 测试。
依赖新增/变更：NONE。生产源代码、`tests/`、`examples/`、`pyproject.toml`、`uv.lock`、
`third_party/` 和许可证内容变更：NONE。

## 7. 保留英文与排除项

本次范围内未留下以英文正文为主体的项目自有文档；代码块、CLI/test/Git output、
canonical terms、标识符与短原始引用按要求保留英文，不能将其误计为翻译欠项。

- `tests/fixtures/sysml/README.md`：仍以英文为主体；用户明确禁止修改 `tests/`，原样保留并列为本次范围排除项。不能声称仓库内全部项目自有 Markdown 均已中文化。
- `CLAUDE.local.md`：被 Git 忽略的本机私有文件，不属于可提交项目文档；本次未读写或提交。
- `LICENSE*`、`third_party/licenses/**`、第三方源文件、原始外部资料及导入证据：任务明确要求保留原文。
- `THIRD_PARTY_NOTICES.md`：仅翻译项目自有说明，原始来源和许可证相关代码块原样保留。

## 8. 已知限制与独立后续项

- 语言启发式扫描不能替代语义复核，因此结合逐篇翻译审阅和独立文档复核。
- 秘密信息扫描是新增文本的模式检查，不能证明任意格式秘密均可被识别；本次未读取旧 importer 或复制凭证。
- 既有历史记录存在不同时间段的旧叙述，例如 MVP-1 Release 中“独立审核尚未进行”，
  与后续已接受/已发布状态并列；本次保留原事实与差异。若需解释其时间范围，另立历史说明任务，不在翻译中修正。
- Spike 的旧 hash 解释及后续修正链保持原样；不将后来的结论回填成早期已知事实。
- 本次工作未替代用户对 G0A Spec 的审查，也不代表 G0A 或 MVP-2 已获工程批准。

## 9. 范围与下一步

范围漂移：NO。仅翻译项目自有 Markdown，并增加用户要求的语言治理规则、导航与本记录。

MVP-2 production implementation：`NOT_STARTED`。
MVP-2 Implementation Plan：`NOT_STARTED pending spec review`。

下一步：Independent Review of G0A + G0A-L → G0B MVP-2 Implementation Planning。
本任务提交后停止，不编写 MVP-2 Plan，不开始 MVP-2A，不 push。

## 10. 文件清单

本次修改 59 份既有 Markdown，新增本记录 1 份；移动/重命名文件：NONE。

| 操作 | 文件 |
|---|---|
| 修改 | `.claude/rules/architecture.md` |
| 修改 | `.claude/rules/fmea-domain.md` |
| 修改 | `.claude/rules/testing.md` |
| 修改 | `AGENTS.md` |
| 修改 | `CLAUDE.local.example.md` |
| 修改 | `CLAUDE.md` |
| 修改 | `PROGRESS.md` |
| 修改 | `README.md` |
| 修改 | `THIRD_PARTY_NOTICES.md` |
| 修改 | `docs/README.md` |
| 修改 | `docs/adr/ADR-001-langgraph-orchestrator.md` |
| 修改 | `docs/adr/ADR-002-canonical-system-model.md` |
| 修改 | `docs/adr/ADR-003-sysml-dual-mode.md` |
| 修改 | `docs/adr/ADR-004-system-failure-model-separation.md` |
| 修改 | `docs/adr/ADR-005-mcp-boundary.md` |
| 修改 | `docs/adr/ADR-006-aiag-vda-profile.md` |
| 修改 | `docs/adr/ADR-007-vertical-slice-first.md` |
| 修改 | `docs/adr/ADR-008-opensysml-file-mode-first.md` |
| 修改 | `docs/architecture/CANONICAL_SYSTEM_MODEL_SPEC.md` |
| 修改 | `docs/architecture/FMEA_AGENT_V1_ARCHITECTURE.md` |
| 修改 | `docs/architecture/SYSML_FACT_SNAPSHOT_CONTRACTS.md` |
| 修改 | `docs/architecture/SYSML_TO_CANONICAL_MAPPING.md` |
| 修改 | `docs/domain/FMEA_GLOSSARY.md` |
| 修改 | `docs/domain/FMEA_PROFILE_V1.md` |
| 修改 | `docs/evaluation/BENCHMARK_SPEC.md` |
| 修改 | `docs/evaluation/MVP_1_BENCHMARK_REPORT.md` |
| 修改 | `docs/evaluation/MVP_1_BENCHMARK_SPEC.md` |
| 修改 | `docs/foundation/FMEA_AGENT_FOUNDATION_GUIDE.md` |
| 修改 | `docs/foundation/FMEA_AGENT_STAGED_DEVELOPMENT_AND_REUSE_GUIDE.md` |
| 修改 | `docs/governance/DEVELOPMENT_WORKFLOW_AND_RECORDS_POLICY.md` |
| 修改 | `docs/governance/LANGUAGE_AND_TERMINOLOGY_POLICY.md` |
| 修改 | `docs/plans/MVP_0_IMPLEMENTATION_PLAN.md` |
| 修改 | `docs/plans/MVP_1_IMPLEMENTATION_PLAN.md` |
| 修改 | `docs/product/FMEA_AGENT_V1.md` |
| 修改 | `docs/prompts/CLAUDE_CODE_SESSION_TEMPLATE.md` |
| 修改 | `docs/prompts/MVP_1_CLAUDE_CODE_SESSIONS.md` |
| 修改 | `docs/records/MVP_0/MVP_0_CLOSEOUT.md` |
| 修改 | `docs/records/MVP_1/MVP_1A_OPENSYSML_SPIKE.md` |
| 修改 | `docs/records/MVP_1/MVP_1B_SNAPSHOT_CONTRACTS.md` |
| 修改 | `docs/records/MVP_1/MVP_1C_OPENSYSML_ADAPTER.md` |
| 修改 | `docs/records/MVP_1/MVP_1D_CANONICAL_MAPPING.md` |
| 修改 | `docs/records/MVP_1/MVP_1E_WORKFLOW_INTEGRATION.md` |
| 修改 | `docs/records/MVP_1/MVP_1F_BENCHMARK_RELEASE.md` |
| 修改 | `docs/records/MVP_1/MVP_1_POST_RELEASE_PATCH.md` |
| 修改 | `docs/records/MVP_1/MVP_1_RELEASE.md` |
| 修改 | `docs/records/README.md` |
| 修改 | `docs/records/bootstrap/PROJECT_CLEANUP_REPORT.md` |
| 修改 | `docs/records/templates/MVP_RELEASE_TEMPLATE.md` |
| 修改 | `docs/records/templates/SESSION_HANDOFF_TEMPLATE.md` |
| 修改 | `docs/records/templates/STAGE_CLOSEOUT_TEMPLATE.md` |
| 修改 | `docs/research/DEPENDENCY_INVENTORY.md` |
| 修改 | `docs/research/NEO4J_FAILURE_KNOWLEDGE_BASELINE.md` |
| 修改 | `docs/research/OPENSYSML_DEPENDENCY_REPRODUCTION_REPORT.md` |
| 修改 | `docs/research/OPENSYSML_FEASIBILITY_SPIKE.md` |
| 修改 | `docs/research/OPENSYSML_SPIKE_REPORT.md` |
| 修改 | `docs/research/SYSML_SOURCE_CATALOG.md` |
| 修改 | `docs/specs/MVP_0_RUNNABLE_AGENT_SKELETON.md` |
| 修改 | `docs/specs/MVP_1_REAL_SYSTEM_FACTS.md` |
| 修改 | `docs/specs/MVP_2_REAL_FAILURE_KNOWLEDGE.md` |
| 新增 | `docs/records/G0A_L_DOCUMENTATION_LOCALIZATION.md` |

## 11. 独立文档复核与修正

EXTERNAL_REVIEW：独立只读 Agent 审阅起始基线对工作区的全部 59 份既有文档差异，
以及新增本记录；未修改工作区或重复执行生产回归。

结论：Critical = NONE，Important = NONE。两项 Minor 已由主任务读取原文后修正：

1. 将测试夹具 README 的原语言说明改为“英文主体，因 tests/ 禁改而排除”，明确剩余英文文件。
2. 将“无数字 token 丢失”收窄为历史数值无漂移；`E2E` 翻译为“端到端”不属于历史数值变化。

复核确认 P0、语言政策、模板、术语、历史完整性、代码块、范围和凭证保护满足本次要求；
完成上述措辞修正后可提交为 READY_FOR_REVIEW。本复核不批准 G0A 产品 Spec 或 MVP-2 Plan，
联合 Independent Review of G0A + G0A-L 仍是下一步。

## 12. 提交前自检

- [x] P0 文档全部以中文为主体；P1 / P2 可修改范围已处理，剩余英文排除项已列明。
- [x] AGENTS / CLAUDE 有相同核心语言政策，完整指令结构及加载入口不变。
- [x] Governance 有语言政策与六项 Documentation Language Gate。
- [x] 记录模板已中文化；旧提示词生命周期与原 fenced 样例保留。
- [x] 当前 MVP-2 Spec、V1 Product、V1 Architecture、Neo4j Baseline 均以中文为主体。
- [x] Glossary 含 13 项术语约定；代码标识符未被误译。
- [x] 代码块、历史事实、状态、路径、命令、commit SHA 与精确 commit message 保留。
- [x] 第三方原文、许可证和原始证据未被修改，新增文本凭证模式扫描无命中。
- [x] LOCAL 回归及文档验证通过；没有将 LOCAL 结果表述为 GitHub CI。
- [x] Production source changes = NONE；依赖、测试、示例与数据库无变更。
- [x] MVP-2 implementation = NOT_STARTED；MVP-2 Plan = NOT_STARTED pending spec review。

本记录由独立 docs-only commit 持久化；以 Git 为恢复锚点，不另建重复 Session Handoff。
