# Demo V1 D7 — 集成验收与演示交付

日期：2026-09-05
Stage status: ACCEPTED
Closeout status: PENDING_PUSH（技术已接受，远端保存核对中）
技术范围：Demo V1 / D7，A01–A12；人工工程质量 NOT_ACCEPTED。

## 1. 起点、范围与实际演化

用户明确授权本会话完成必要实现、测试、适用真实验证、独立审核、修复、记录、提交及推送。
已读取 AGENTS/PROGRESS/导航、[Spec](../../specs/DEMO_V1_END_TO_END_FMEA.md)、
[Plan](../../plans/DEMO_V1_IMPLEMENTATION_PLAN.md)、D6/用户指南、D2–D5 契约及治理/架构记录。
沿用已接受设计，没有重做需求问卷。

- 实际目录 `D:\code\FMEA Agent 2026.9.3 2.0\FMEA Agent 2026.9.3_READY`。
- 起点分支 `codex/demo-v1-d6-reports-ui`，HEAD `dadc36c`，工作区干净。
- fetch 成功，本地/远端左右差异 `0 0`，只有当前 checkout。
- 从此基线创建 `codex/demo-v1-d7-acceptance`；包含全部 D0–D6 记录，不从旧 master 开始。
- 主代理是唯一实现写入者；独立 reviewer 仅只读检查，未操作共享浏览器。
- 未改变 D2–D6 领域/服务契约、D1 资料、benchmark gold、依赖锁、master 或发布 tag。
  UI 仅去除阶段性 D6 标题；D7 新增集成测试与公开验收脚本。
- Scope change: NO。脚本是 Plan D7 三类场景的可重复执行入口，不扩展正式 MVP 能力。

## 2. 实际交付与原因

| 文件 | 变更与原因 |
|---|---|
| `tests/test_demo_e2e.py` | 12 项集成回归：真实 SysML→mock→自包含导出，空来源/错误引用/空输出、连接失败明确降级、输入身份、公开 smoke 数据边界与安全失败 |
| `scripts/demo_acceptance_smoke.py` | 固定公开 hash→真实 service 补问/未知继续→DeepSeek→脱离 session 三格式；只输出安全摘要，绝不装配真实图 |
| `src/fmea_agent/ui/demo_app.py` | 页面标题不再显示内部实施阶段 D6，行为不变 |
| `docs/evaluation/DEMO_V1_ACCEPTANCE_REPORT.md` | A01–A12 矩阵、三场景模式、真实证据、人工未验收、MVP-2/3 复用与差距 |
| 本记录、PROGRESS、Plan、README、导航、用户指南、依赖清单 | 交付/启动入口、状态与证据一致性 |

复用分类：D4 固定公开 hash loader、安全错误码，D5 service/graph，D6 mock/export = D；
stdlib runpy/contextlib/hashlib/json/pathlib = D；D7 验收断言与摘要 = S。
没有自建解析器、Agent runtime、HTTP、图/向量库或文档框架。无新增第三方依赖/许可证变化。

## 3. LOCAL 开发与验证

初版测试误引用不存在的 DemoServiceError 导致 collection error，随后按实际 DemoModelError 契约纠正；
身份测试误把 missing_files 的 `design` 写成 `document`，按 D2 既有规范纠正，未修改生产行为。
已有 7 项集成边界先通过；新公开 smoke 测试因缺少脚本失败后实现。
测试注入 client 最初未实现 close，补齐测试替身生命周期；未为测试给生产 mock 增加方法。
Ruff 初次发现 import 顺序/两处长行，限定新增文件修正。RED 未单独保存为 Git commit。

LOCAL：12 项 D7 测试通过；全套 539 passed in 32.51s、Ruff PASS、mypy src50 PASS；
Demo 专项 325 passed / 214 deselected in 25.33s；B0/B1 11 passed in 1.15s；
src+新 smoke mypy 51 files PASS；离线 lock104 PASS；diff PASS。
UI 标题文案收尾后再次全套 539 passed in 25.42s、Ruff/mypy PASS；93 个 Markdown 本地链接与围栏 PASS。
新增检查没有改变 gold/基准指标，没有观察到既有 B0/B1、原 CLI、SysML 或 orphan 回归退化。
实际真实服务/摘要/候选文件 hash 统一见[验收报告第 3 节](../../evaluation/DEMO_V1_ACCEPTANCE_REPORT.md#3-local-自动验证与真实服务结果)。

三场景：S1 REAL_FILE + mock LLM/FAKE_NO_MATCH；S2 LIVE_NEO4J、无模型；
S3 REAL_FILE + LIVE_DEEPSEEK/FAKE_NO_MATCH。两个原有 smoke 与新的服务 smoke 均实际 PASS。
真实服务显式 `uv --env-file .env.local` 注入，不读取/打印/覆盖/提交配置。
图 smoke 只输出计数/定位状态；私有图正文未发送外部模型。工程 gold/人工抽查未建立。

## 4. 用户入口与报告验证

LOCAL 标准浏览器 UI 绑定 `127.0.0.1:8501`；演示包真实载入、补问、未知继续、生成、来源展开、
三格式下载均通过。下载 JSON 恢复后的独立导出与实际三份文件逐字节一致。
run_id、文件字节数和 AppTest 覆盖边界见[验收报告第 4 节](../../evaluation/DEMO_V1_ACCEPTANCE_REPORT.md#4-local-浏览器与-apptest-分开记录)。
初次仅点下载尚未取得磁盘保存证据，改用明确 download event 等待后核对实际文件；没有将点击冒充保存。
本次浏览器未重复 D6 已记录的 OS 三文件选择器上传；本次三文件上传另由独立 AppTest 覆盖。

故障验证 wrapper 放 ignored `outputs/d7-validation/browser_fault.py`，只注入确定性 ERROR，
复用原 UI 并标明 FAKE_CONNECTION_FAILED，监听 `127.0.0.1:8502`；不停止真实数据库。
浏览器实际 ERROR 阻停/无下载→明确降级→COMPLETE 且保留 ERROR；实际下载 JSON 核验通过，
新建会话撤销旧候选/下载。wrapper 的故障注入身份与默认 mock 客户端标签边界在验收报告明确，
不以其 FAKE_NO_MATCH 默认 usage 标签表示故障实际状态。临时服务/页面在验证后清理，公开输出保留本机 ignored 目录。

## 5. 独立审核、修复与 Git 保存

审查者 `/root/d7_independent_review`，只读检查；初步未发现 CRITICAL/IMPORTANT。
EXTERNAL_REVIEW：539 passed in 28.83s；Ruff/mypy src50/lock104/diff PASS。
另 6 组真实 UI 三文件上传 AppTest 探查通过，详见验收报告第 5 节；不访问真实服务或 `.env.local`。
实施提交 `f550a0dff52b68c035c266f7205eb3330c7b4f01`，送审范围 `dadc36c..f550a0d`，11 文件。
独立最终结论 **ACCEPTED（仅受限 Demo V1 / D7 技术范围）**；未解决 CRITICAL=0 / IMPORTANT=0 / MINOR=0。
无需审核后代码修复；新增脚本/测试与首轮全套验证版本 hash 一致，现有 UI 唯一修改为标题文案。
固定 HEAD 另复验 E2E + UI **22 passed in 4.08s**，Ruff、mypy src+smoke51、lock104、总范围 diff PASS；
三份 LOCAL 脱敏真实摘要与矩阵记录一致。审核结束分支正确、工作区/index 干净。
最终治理回填只改状态/审核证据，不扩大工程质量或正式 MVP 验收。

Git：首次标准 push 返回 SSL_read unexpected EOF / sideband disconnect（输出含 Everything up-to-date，
但退出码为 1，不能据此认定成功）；随后 ls-remote 和仅命令级 HTTP/1.1 push 也遇到 TLS EOF。
未禁用 TLS 验证、修改永久 Git 配置或 force push。远端保存仍需实际查回确认。
本机公开工件 hash 与摘要一致；变更文件凭证形态扫描 0 hits；中文/术语/原文边界检查通过。
浏览器临时页面关闭；8501/8502 测试进程已停止，监听检查为空。

## 6. 限制与下一步

技术演示与人工工程质量分别验收：本次无人抽查，工程质量 NOT_ACCEPTED。
引用存在不等于支持结论；教学模型及同源资料不构成独立工程 gold。
未验证私有真实图→外部模型完整链路，未授权外发的工程正文不参与该验证。
正式 MVP-2/3 的能力/证据/限制/验收差距已登记在同一验收报告，不宣布正式 MVP-2/3/5 发布或 D7=MVP-7。
后续建议先按正式当期 Spec 核对差距、建立可审核且允许使用的独立知识/工程样例，复用 Demo 后补齐验收。
当前分支不合并 master、不创建或移动发布 tag；原 MVP-1 稳定发布保持 v0.1.1。
