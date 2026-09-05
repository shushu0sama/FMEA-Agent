# Demo V1 本机候选分析用户指南

Lifecycle: ACTIVE
范围：Demo V1 / D6 用户入口与导出；D7 集成验收尚未开展。

## 启动

在项目根目录执行（Windows PowerShell）：

```powershell
uv sync --extra demo
uv run --extra demo --env-file .env.local streamlit run src/fmea_agent/ui/demo_app.py --server.address 127.0.0.1
```

打开终端显示的本机地址，默认 `http://127.0.0.1:8501`。
项目 `.streamlit/config.toml` 固定本机绑定、关闭使用统计、隐藏内部异常详情。
不要修改为公网监听。开发时新增或改名被导入的类后，应停止并重新启动进程；普通页面重绘不等于重新导入整个应用。

默认 `live`，使用真实 DeepSeek 和只读 Neo4j。配置由进程环境读取，不自动读取 `.env.local`；
必须通过上面的 `--env-file` 显式注入。配置文件仅保留本机，不上传、截图或提交。
需要的变量名：`DEEPSEEK_API_KEY`、`NEO4J_URI`、`NEO4J_USERNAME`、`NEO4J_PASSWORD`；
`NEO4J_DATABASE` 默认 `neo4j`，`FMEA_DEMO_MODE` 默认 `live`。
模型固定 `deepseek-v4-pro`，官方端点固定在既有 D4 适配器。
缺配置会列出缺失变量名并禁用提交，不会自动切成 mock；“配置已具备”不表示连接已验证。

确定性离线演示请明确设置：

```powershell
$env:FMEA_DEMO_MODE = "mock"
uv run --extra demo streamlit run src/fmea_agent/ui/demo_app.py --server.address 127.0.0.1
```

mock 使用真实本机文件解析、D5 工作流和报告导出；模型是确定性教学实现，检索为 `FAKE_NO_MATCH`。
其报告调用审计明确记录 `mode=mock`，不代表真实服务或工程质量通过。
回到 live 前从当前 PowerShell 删除本次覆盖：`Remove-Item Env:FMEA_DEMO_MODE`，重新启动服务。

## 四区操作

1. **上传与载入**：选“上传文件”，提供一个 SysML，可选设计说明和 BOM，再点击“载入资料”。
   也可明确选“演示资料包”，从项目 `examples/demo_v1` 读取三个公开教学文件。
   SysML 通过真实 OpenSysML 解析；原文件名仅显示，实际临时路径由服务端随机生成，解析后清理。
2. **摘要与补问**：检查文件 hash、解析器/运行时版本、系统结构和来源，再选择组件/功能。
   提交自然语言分析目标和工况后查看模型确认的目标。最多两轮集中补问；空回答不会新建事实或调用模型。
   无法确认时勾选“仍未知，明确按未知继续”并提交。结构冲突、无效目标、解析错误不能绕过。
3. **候选与证据**：明确点击“生成候选报告”才检索和生成。字段详情可查看模式、起因、机理、
   三层影响、既有控制、建议措施、来源及验证建议。引用 ID 有效只证明能定位，不证明原文支持结论。
   `HITS` 是相关知识、适用性待确认；`NO_MATCH` 只描述本次有界查询。图关联不是原始 FMEA 行。
4. **报告下载**：成功提供 JSON / HTML / CSV；失败仅提供 FAILED 诊断 JSON / HTML。
   下载与页面重绘不调用模型。HTML 可离线打开或浏览器打印；JSON 保存完整结构；CSV 是候选表，
   附字段来源、完整输入快照和审计 JSON 列，多值以换行分隔，单候选不会展开成笛卡尔积。

每次重新载入、增删替换文件或更改资料来源，旧分析都会失效；需要新建 service、fresh client 和会话预算。
单独导出的报告可脱离原 session 使用；会话运行恢复仅限原进程/同一个 service，重启后重新载入并分析。
每会话最多 6 次 HTTP 请求（含重试）；失败会话不自动重放生成。检索 ERROR 后，需另行明确选择
“检索失败时，明确仅按已知资料推理”并提交，保留原 ERROR，不重查或冒充 NO_MATCH。

## 格式与资源限制

| 输入 | 接受范围 | 限制 |
|---|---|---|
| 模型 | 一个 `.sysml` 单文件子集 | 必需；不支持用户文件 imports、partial 或无合法组件/功能对 |
| 设计说明 | UTF-8 `.md` / `.txt` 或文本 `.pdf` | 可选一个；PDF ≤20 页，不支持扫描/OCR、加密或无文本页 |
| BOM | UTF-8 `.csv` / `.xlsx` 的 `BOM` 表 | 可选一个；≤200 非空数据行；固定六列 |

BOM 列：`item_id,parent_id,name,quantity,unit,source_element_id`。
数量可空，不从声明数量推算。拒绝公式和宏工作簿；XLSX ZIP 展开声明总量 ≤25 MiB，
BOM 表扫描 ≤10,000 物理行、≤64 列。每文件 ≤5 MiB，本次提取文本合计 ≤30,000 字符，
应用层重复检查；超限拒绝，不静默截断。对话文本也受应用层累计上限约束。
不支持 DOCX、CAD、压缩包、旧 XLS、自动从文档重建模型或外部资源执行。

## 报告含义与数据边界

所有结果始终为 `CANDIDATE`，新增判断为 `INFERENCE`；未知层保持 `UNKNOWN`。
风险固定 `NOT_EVALUATED`、优化固定 `SKIPPED`；没有 S/O/D/AP 评分、正式批准、措施实施确认、
知识写回或自我训练。既有控制与建议措施分列，不能将建议误认为已存在的控制。
HTML 对外部文字转义，不含脚本或外链；CSV 使用 UTF-8 BOM，并为危险公式前缀添加单引号，
原值仍在结构化字段来源中保留。Excel 打开后若手动删除防护前缀，需自行判断内容。

live 的显式提交会将本次必要资料及可用检索上下文发送给 DeepSeek。仅在资料已获允许外发时使用。
本阶段验证使用公开演示资料；不会把私有 Neo4j 工程正文送入外部模型。
首例 hydraulicPump / motor / spin 是教学夹具；根动作 pumpSpin 与其他未选功能列在排除项中。
报告不是工程认证；D6 技术验证不代表 D7、正式 MVP-2/3 或整个 Demo 已验收。
