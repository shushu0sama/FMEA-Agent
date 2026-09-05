# Demo V1 D6 — 自包含候选报告与本机 Streamlit UI

日期：2026-09-05
Stage status: READY_FOR_REVIEW
Closeout status: READY_FOR_REVIEW
Scope: Demo V1 / D6（A09、A10、A12）；D7 NOT_STARTED。

## 1. 起点与范围

用户授权在当前 checkout 实施、测试、适用真实验证、独立审核、记录、提交与推送。
已读取 AGENTS、PROGRESS、导航、[Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Plan D6](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)、[D5](D5_CONTROLLED_WORKFLOW.md)、
D2–D4 记录及其治理、架构契约。沿用已接受设计，不重做问卷。

- 实际目录：`D:\code\FMEA Agent 2026.9.3 2.0\FMEA Agent 2026.9.3_READY`。
- 起点分支 `codex/demo-v1-d5-controlled-workflow`，HEAD `8a77ed9`；工作区干净。
- fetch 成功，D5 本地/远端左右差异 `0 0`；确认包含交接提交。
- 在相同 checkout 创建 `codex/demo-v1-d6-reports-ui`，不从旧 master 开始、不丢弃修改。
- D3 第 8 节最新真实 Neo4j 仍 PASS；历史 CONFIG_MISSING/AUTH_FAILED 保留为历史。
- 未改 D2–D5 实现、原 CLI/workflow、D1 资料、基准 gold、master 或发布 tag；不实施 D7。

## 2. 实际文件与复用

| 文件 | 变更与原因 |
|---|---|
| `adapters/reports/demo_report.py` | 仅依赖报告对象的 JSON / HTML / CSV；失败诊断单独导出 |
| `application/demo_settings.py` | 默认 live、SecretStr、缺失配置、fresh client 与资源装配 |
| `application/demo_uploads.py` | 应用层大小/类型检查、随机安全临时路径、文件名展示与重新计算清单摘要 |
| `adapters/llm/demo_mock.py` | 显式确定性教学模型与 FAKE_NO_MATCH，保留预算和模式审计 |
| `ui/demo_app.py`、`.streamlit/config.toml` | 四区入口、session_state 生命周期、显式提交、本机绑定 |
| `tests/test_demo_reports.py`、`test_demo_settings.py`、`test_demo_ui.py` | 导出/配置/AppTest 回归 |
| `docs/product/DEMO_V1_USER_GUIDE.md` | 中文操作、格式限制、状态、数据与恢复边界 |
| `pyproject.toml`、`uv.lock`、依赖清单与导航/Plan/PROGRESS | 固定依赖与阶段交接 |

上表源码路径以 `src/fmea_agent/` 为前缀。复用分类：Streamlit = D/W；html/csv/json/tempfile = D；
领域报告、D2 loader、D5 service/graph = D；候选展示/导出语义 = S。
没有引入新领域技术依赖或解析器。装配入口依 Plan 位于 application，具体提供方仍在 adapter。

## 3. 行为与安全边界

成功报告在 JSON 往返后独立导出，保留清单文件名/hash/parser/runtime、CSM、资料关联、来源链、
缺失项、字段证据/状态/限制、检索上下文、排除项与调用 usage。CSV 每候选一行，多值换行；
另保留 `field_provenance`、输入快照、完整 evidence registry、检索和 usage JSON 列。
既有控制与建议措施分列。UNKNOWN 三层影响不丢失；风险 NOT_EVALUATED，优化 SKIPPED。
DiagnosticReport 仅 FAILED JSON/HTML，不能交给候选导出器，也不提供 CSV。

HTML 所有动态文字经 `html.escape`；没有脚本/外链。CSV 带 UTF-8 BOM，危险公式前缀以单引号防护，
原始值保留在结构化字段来源。浏览器发现 `st.dataframe` 自带 CSV 下载绕过报告器，已通过失败回归
改为转义后的静态 `st.html` 表格，最终浏览器确认原生下载入口不存在。

UI 保存 `DemoService` 和 `DemoSession`，start/answer/analyze 仅由 form submit 触发。
下载使用预先生成 bytes 与 `on_click="ignore"`，重绘不调用模型。文件增加、删除、替换、改名、
资料源/模式变化立即清除旧输入与结果；重新载入时使用 fresh service/client，旧资源关闭。
随机目录/文件名只用于临时解析，原文件名取 basename 作报告展示；不传给写路径。
解析后清理临时目录，报告仍保留来源；资源上限复用 D2 并在应用入口重复检查。

两轮补问、空回答、continue_unknown、检索 ERROR 后显式 allow_without_retrieval 都通过真实 D5 服务。
未产生第三轮集中问题或失败自动重放。缺失配置列变量名并禁用提交；配置具备不等于连接通过。
SecretStr 遮蔽密钥；未将配置值放在 UI 或异常中。只展示 UploadError / DemoInputError 的安全消息，
其余 parser/装配异常统一安全错误，避免原文异常被 Markdown 当外部资源解释。

## 4. LOCAL 开发与自动验证

基线：498 passed in 20.22s，Ruff PASS，mypy 43 files PASS。
测试先行：报告 13 项缺模块失败后通过；配置 4 项失败后通过；首批 UI 7 项缺入口失败后逐项通过。
首个上传路径测试误要求报告保存路径串，D2 basename 契约拒绝；改为保留原 basename，安全写路径不变。
后续补测无结果语义、异常 Markdown 泄漏与原生 CSV 旁路，先复现失败再修复。
RED 未独立保存为 Git commit。

首审前新增 26 项（报告 13、配置 4、UI/上传 9）；当时全套 524 passed in 24.31s。
该次随后 Ruff 检出一个新增 import 空行顺序问题，已修复。
最终提交前 `scripts/verify.py`：524 passed in 24.20s，Ruff PASS、mypy src 50 files PASS；
`uv lock --check --offline` PASS（104 packages）、`git diff --check` PASS。
既有 B0/B1、原 CLI、SysML、orphan 和 D1–D5 回归均在全套内，gold/度量未修改。
CI = NOT_CONFIGURED。独立审核证据与 LOCAL 分开见第 7 节。

依赖实际引入 streamlit 1.63.0 与 25 个新传递包；最初 NumPy 类型声明不兼容 Python 3.11
检查目标，仅将这个新传递依赖约束至 2.3.5。最终 104 locked packages，既有 name/version 未改变。
streamlit wheel 元数据 Apache-2.0、上游 1.63.0 LICENSE 已核对；本机 wheel 未附 LICENSE，
其他包安装原文及 NumPy 二进制声明另记录。详见[依赖清单](../../research/DEPENDENCY_INVENTORY.md)。

## 5. LOCAL 浏览器操作与 AppTest 覆盖边界

真实浏览器：Codex in-app browser，服务监听 `127.0.0.1:8501`，明确 `FMEA_DEMO_MODE=mock`。
真实本机 SysML/MD/CSV loader + D5 服务/图 + mock LLM + FAKE_NO_MATCH + 真实 Streamlit。

- 实际文件选择器上传 design.md，单文档载入明确提示必须 SysML。
- 实际上传 system.sysml / design.md / bom.csv，确认 motor/spin，显式提交 → WAITING_INPUT。
- 明确按未知继续 → READY，再显式生成 → COMPLETE；显示 CANDIDATE/NOT_EVALUATED/SKIPPED、
  NO_MATCH 有界含义、既有控制/建议措施和原始引用入口。
- 生成过程中开发热重绘曾因新增 UploadError 的旧模块缓存出现安全隐藏的 ImportError；
  停止并重启进程后完整重新上传与操作通过，没有将开发期失败改写为首次成功。
- 最终移除原生 dataframe CSV 入口后，浏览器分别下载 candidate.json/html/csv。
  下载在 `C:/Users/shushu/Downloads`；三份 bytes 均与下载 JSON 恢复后的 exporter 输出完全相同，
  CSV BOM 通过；run_id `80088101ce694038a22334c2d0ccde55`，1 条 mock 候选、2 次请求。
  下载/重绘不新增调用；随后移除 SysML，旧候选与下载立即撤销。
- 另用只绑定 127.0.0.1 的临时静态服务打开第 6 节的独立 HTML，中文表格目视可读；
  DOM 检查 8 条候选，script=0，外链/图片/iframe=0。不是独立 PDF 排版验收。

固定 1.63.0 的 AppTest 实际支持 `file_uploader.upload` 和 `download_button.click`，
因此本阶段没有沿用旧“上传控件不支持”的假设。AppTest 覆盖模拟上传到真实应用入口、
两轮补问、空回答、未知继续、错误/降级、下载 bytes 准备、点击后请求不增和文件替换。
它不覆盖 OS 文件选择器、真实 multipart 网络、浏览器保存文件或下载视觉反馈；上述部分由真实浏览器补充。
图断连/模型失败路径用确定性 fake 触发 AppTest；未停止本机真实 Neo4j，也未以 fake 冒充真实断连验证。

## 6. LOCAL 真实 DeepSeek 与独立导出补充验证

2026-09-05T11:53:57.911536+00:00 开始，通过
`uv run --no-sync --offline --env-file .env.local python -` 显式注入环境。
复用 `scripts/demo_model_smoke.py` 的固定公开文件 hash 验证、安全日志/输出封装；
stdin 临时将 `_run` 替换为 D5 start → unknown answer → analyze，再清除 service/session、
CandidateReport JSON 往返并导出三格式。未新增 D7 验收器，未读取或输出配置文件。

结果 PASS：8 条候选，2 次请求，prompt_tokens=13102、completion_tokens=2471、total_tokens=15573。
model=response_model=`deepseek-v4-pro`，called_at=`2026-09-05T11:54:01.767746+00:00`。
脱离会话导出大小：JSON 57277、HTML 76688、CSV 389474 bytes。
之后仅在本机产物 usage 补充 `mode=LIVE_DEEPSEEK`、`retrieval_mode=FAKE_NO_MATCH`、
`graph_used=false` 的实际验证模式，再离线重导出，没有新增模型调用。
公开产物保存在 ignored `outputs/d6-public-smoke/`，不作为已批准工程知识提交。

实际模式：真实本机 SysML + LIVE_DEEPSEEK + **FAKE_NO_MATCH**；graph_used=false。
完全没有构造 Neo4j adapter，未读取/发送私有图正文。通用 JSON smoke 未重跑；
此结果证明 D6 导出能承接真实模型校验后的候选，不是完整图与模型集成或工程正确率验收。
D3 最新真实图验证仍引用 D3 第 8 节，本阶段不重复图 smoke。

另外显式注入 `.env.local` 后，默认 live 配置缺失项为零，真实适配器延迟装配并关闭成功；
该只读配置检查没有 API 调用或图查询，不将“配置具备”写作“服务连通”。

## 7. EXTERNAL_REVIEW 与 Git 保存

实施提交 `932a4d4e42eee0ef7420222b597a280b7a3d800b`，验证后进入 READY_FOR_REVIEW。
独立 reviewer `/root/d6_independent_review` 正在对 `8a77ed9..932a4d4` 运行全套检查和边界探查；
实现方不自封 ACCEPTED。审核后的发现、修复、复验与推送结果在本节追加，保留真实演化。

实施分支首次标准 push 成功，远端已建立同名 upstream，`932a4d4` 已保存；未 force push。

初审决定 **CHANGES_REQUIRED**：CRITICAL=0 / IMPORTANT=1 / MINOR=0。
I-1：mock 客户端仅看最后一条用户消息选择目标，非首个组件/功能在补问“仍未知”后退回首个目标。
reviewer 在真实 service 与 AppTest UI（仅 loader 注入两目标 CSM）均复现最终报告对象错误。
EXTERNAL_REVIEW：524 passed in 23.96s；Ruff、mypy 50 files、lock 104、diff PASS。
另 8 组独立探查通过：完整往返、跨字段 HTML inert、非 mode CSV 危险值/来源、格式拒绝、
诊断转义、随机上传路径/清理、预解析限额、live 部分装配失败的关闭与安全异常。

修复仅限新增 mock：反向扫描完整用户证据，保留最近明确 ID 对；按标识符边界匹配，
防止 c1/f1 误匹配 c10/f10。新增 2 项 service 配置回归及 1 项实际 UI 多目标回归。
前两项在原实现均失败；UI 回归通过在独立进程加载 `932a4d4` 原 generate 方法再次复现失败，
恢复修复方法后通过。没有更改 D2–D5 或真实模型行为。等待固定修复提交的独立复验。

修复后 LOCAL：`scripts/verify.py` → **527 passed in 24.16s**，Ruff PASS，mypy src 50 files PASS；
lock offline 104 packages PASS、diff PASS。累计新增 29 项（报告 13、配置 6、UI/上传 10）。

## 8. 已知限制与下一步

单用户本机 UI，内存 session，重启重新运行；不提供生产认证、持久幂等、多人审查。
CSV 完整 JSON 列可能超过电子表格单单元格显示容量；JSON/HTML 是完整核对入口，
不能以表格应用显示截断判断来源丢失。导出不含原始二进制文件，包含完整已解析快照/证据与文件 hash。
语义引用有效不代表支持结论；真实模型多数未知保持未知，未作人工工程质量验收。
下一阶段仅为 D7 集成验收；本次止于 D6，不宣布整个 Demo 或正式 MVP-2/3/5 完成。
