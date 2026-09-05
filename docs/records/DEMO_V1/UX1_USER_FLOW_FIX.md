# Demo V1 / UX1 用户流程修复

日期：2026-09-05。Lifecycle: ACTIVE。当前技术状态：READY_FOR_REVIEW。
用户使用复验：PENDING（此前用户明确反馈不能完成使用与交互）；人工工程质量：NOT_ACCEPTED。

## 1. 起点、范围与原因

实际目录为当前 `_READY` checkout，Git 起点 `a914f463fa3237e3958be654c8dd786637f5dccf`，
原分支 `codex/demo-v1-d7-acceptance` 与 upstream 无本地差异，工作区干净。
沿用 checkout 创建 `codex/demo-v1-ux-flow`，主代理唯一写入，独立审核只读。
D7 技术 ACCEPTED 历史保留，不等于用户可独立使用或人工工程质量已通过。

用户已批准第一批交互修复；Spec §7.1 与 Plan 的 UX1 补充登记当前范围。
实际发现：WAITING_INPUT 同时展示空报告区；空目标可触发模型；空补充缺少下一步反馈；
未知继续需组合勾选与提交；意外异常后旧页面仍可能提供提交入口。
本次仅修复当前 UI 流程，没有修改 D2–D6 领域、解析、检索、模型或 service 契约。
范围变化：相对用户批准设计 NO；相对原 D7，新增独立 UX1 修复记录，不回写历史。

## 2. 实现与复用

- 阶段相关提示和报告/下载可见性；模型与可分析对象计数；可选文件不阻塞。
- 演示包不展示上传控件；输入拒绝给出安全 code/诊断和重新载入建议。
- 空目标/补充在 UI 拦截，不创建调用或消耗轮次；“按未知继续”独立显式提交。
- 检索 ERROR 后，只有再次点击“确认降级并生成候选报告”才允许参考推断，保留 ERROR。
- 意外操作异常停止当前会话提交，保留新建入口，不自动重放；成功引导看依据并下载。
- 原始英文名称和 canonical ID、来源、状态、未知值完整保留，中文化仅限界面解释。

文件：`src/fmea_agent/ui/demo_app.py`、既有 UI 测试、新 `tests/test_demo_ui_flow.py`、
Spec/Plan 补充、用户指南、README/导航、PROGRESS 和本记录。
复用：Streamlit 表单/按钮/AppTest = D；D2 上传/loader、D5 service、D6 exporter = D；
FMEA 用户操作映射与文案 = S。无新依赖、版本/许可证变更、解析器重写或服务端口扩展。

## 3. LOCAL 验证

先运行新增 8 项 AppTest 回归，原代码 8 failed；随后实施通过 8 项。
失败包含阶段错误显示、空目标仍创建 service、空补充改变请求记录、缺少直接操作按钮、
真实无功能/超限输入缺少恢复指引，以及意外异常仍允许重提。RED 未独立保存为 Git commit。
既有测试迁移到直接按钮，保留原补问、输入身份、错误降级、下载和重绘断言。
初次 lint 检出 5 处长行，限定本次 UI 修改修正。

| 验证 | 结果 |
|---|---|
| UI + UX1 + D7 E2E | 30 passed in 6.95s |
| `uv run --no-sync --offline python scripts/verify.py` | 547 passed in 29.44s；Ruff PASS；mypy src 50 files PASS |
| `uv lock --check --offline` | PASS，104 packages |
| B0/B1 `tests/test_mvp1_benchmark.py` | 11 passed in 1.09s |
| `git diff --check` | PASS |

确定性 mock/fake 用于常规验证；真实 SysML parser、service、exporter 仍实际执行。
基准 gold 和指标未变，无观察到 B0/B1 回归退化。
本次真实 DeepSeek/Neo4j smoke：NOT_RUN（修改仅在 UI，未改变服务契约；D7 历史结果不冒充本轮结果）。
未读取、修改或输出 `.env.local`，未发送私有 Neo4j 正文给模型。

## 4. 浏览器与独立审核

LOCAL 浏览器在现有 `127.0.0.1:8501` 服务上使用独立新标签/会话，不替用户提交原会话。
已确认真实 parser + mock LLM + FAKE_NO_MATCH；加载包、目标摘要、空白补充、未知继续和生成提示通过。
最终生成/下载及故障浏览器结果在实际完成后追加。
EXTERNAL_REVIEW：待独立审查；不得提前标记 ACCEPTED。
CI：NOT_CONFIGURED。人工用户使用复验与工程质量验收不由技术审查代理替代。

## 5. 限制与下一步

中文名称映射、完整可读来源卡片、报告后持续对话/版本修订尚未实施。
只支持单文件 SysML 子集；入口提示不能让复杂 imports 或无功能模型变成有效输入。
运行提示覆盖真实操作范围，不提供虚构百分比或细分节点进度。
单进程会话，异常/重启需新建，未增加持久恢复；不承诺跨进程 exactly-once。
所有报告仍 CANDIDATE/INFERENCE，风险 NOT_EVALUATED、优化 SKIPPED；无评分、批准或知识写回。
下一步：完成技术独立复审后，请用户独立跑一个支持案例，记录使用阻塞；再按反馈推进第二批。
不合并 master、不创建或移动发布 tag；提交和推送结果完成后记录。
