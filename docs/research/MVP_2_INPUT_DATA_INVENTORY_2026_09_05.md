# MVP-2 输入数据只读盘点（2026-09-05）

Lifecycle: REFERENCE
Evidence: LOCAL（文件读取、Git 检查、Neo4j Browser 查询）

本次是规划前输入盘点，不是检索适配器验收。需求确认和待答问题统一见
[信息对齐台账](../product/MVP_2_PREPLANNING_ALIGNMENT.md)。
工作起点：`fix/pre-mvp2-review-remediation` / `f98238fe29d4428fdbe1b214701b7f447a279a6b`。

## 1. 原始 Excel

用户提供于 `local_data/fmea_inputs/excel/`，本次只读；未转换、清洗、执行宏或导入数据库。
用户确认原始 Excel 经过工程师审核；这是用户确认的来源状态，未独立核查签审记录，
也不表示由此生成的新候选或跨案例应用已经获批。

| 文件 | 工作表 | 读取范围 | 非空数据行（不含表头） | 合并区域 | 观察 |
|---|---|---|---:|---:|---|
| data1014.xls | 机身主梁 | A1:M355 | 354 | 0 | E157、E158 为空；无完全重复数据行 |
| data617.xls | 机身主梁 | A1:M95 | 18 | 0 | 数据在第 2–19 行；第 20–95 行为空；第 10、11 行 A:M 完全相同 |

两文件合计 372 条非空数据行；按完整 13 列比较，有 371 条不同记录。
两文件之间没有完全相同的 13 列记录。**这项程序比较本身不能证明案例关系**；
用户在盘点后另行确认：两表是不同分析层次／案例，应同时保留。这与 SysML/Neo4j 独立性分别记录。
相同非评分字段、不同 S/O/D 的分组本次未检出；这不是评分正确性验证。

两表 A1:M1 表头一致：关注要素层次、下一低分析层次、上一高层次功能及要求、功能、
下一低层次功能、故障影响、严重度(S)、故障模式、故障起因、发生度(O)、探测度(D)、
预防控制措施、探测控制措施。
这些字段和抽查内容支持“设计/产品结构语义”的初步判断；正式 DFMEA/PFMEA 分类、
评分方法和版本仍未确认。历史 S/O/D 只可作为来源原值，不能当作当前项目 AIAG-VDA 规则或新候选评分。
原表中没有专门的失效机理列；不得把故障起因自动改名为机理。

SHA-256：

```text
data1014.xls  945696614f349a3fba657aad083befa07afbeedaa53e41d9f5eeb7cf11d2d5f4
data617.xls   669293f3f29693ecd260fb4a112e4c8dc57bfe5c84bed9005b4199911fc99730
```

读取方法：bundled Python 3.12.14 + `xlrd==2.0.2` 的 `open_workbook(..., formatting_info=True)`。
因环境原先无 XLS 读取器，将 xlrd 临时安装在被 Git 忽略的 `local_data/audit_tools/`；
未修改项目依赖或锁文件。结构盘点保存在本机 `local_data/audit/excel_inventory.json`，不纳入 Git。
上述非空判定为任意单元格去空白后非空；重复按原始 13 列值比较，不做术语归一化或合并。
首次控制台输出发生编码显示乱码，随后以 UTF-8 输出复核中文及单元格值；工作簿读取值未出现替代字符。

## 2. 当前 Neo4j

用户在 Codex 内置浏览器完成登录后查询：

```text
Browser:  http://localhost:7474/browser/
Connect:  neo4j://localhost:7687
Database: neo4j
Version:  5.26.0 Community
Nodes:    878
Edges:    1365
```

本次仅执行下列只读语句。节点/关系类别数量与
[既有图基线](NEO4J_FAILURE_KNOWLEDGE_BASELINE.md) 一致。
当前 10 类节点的实际属性集合均为 `[name]`，9 类关系实际属性集合均为空。
Browser 侧栏列出了历史 property keys（包括评分等），但当前节点/关系查询没有这些属性；
不能用侧栏 token 名称推断当前数据拥有评分或 provenance。

| 检查 | 结果 |
|---|---|
| 索引 | 13 个，全部 ONLINE：10 个领域标签的 name RANGE 索引、2 个 LOOKUP、1 个 Resource.uri RANGE |
| 约束 | 仅 `n10s_unique_uri`：Resource.uri UNIQUENESS；无领域 name 唯一约束 |
| 空名称节点 | 0 |
| 同标签集合、同 name 的重复组 | 0；本次观察不等于数据库约束保证 |
| 失效模式 | 120 个，其中 9 个连接多个关注要素 |
| 同时具有多个起因和多个影响的失效模式 | 3 个 |

**主要适用性限制：**图没有工作簿/工作表/行号，且存在共享失效模式。
沿同名失效模式展开多个起因、影响和控制措施，可能组合出原 Excel 未表达的记录。
只能将查询结果称为图中的关联，不能默认称为已审核的完整原始 FMEA 行。
原始表现在可用于进一步核对，但本次没有完成全部图节点、边与 372 行的逐项对账，
也尚不能确认两份表覆盖整个数据库。

可复现的只读查询（顺序执行）：

```cypher
MATCH (n)
RETURN labels(n) AS labels, count(*) AS count,
       collect(DISTINCT keys(n)) AS property_sets ORDER BY count DESC;

MATCH (a)-[r]->(b)
RETURN labels(a) AS from_labels, type(r) AS relation,
       labels(b) AS to_labels, count(*) AS count,
       collect(DISTINCT keys(r)) AS property_sets ORDER BY count DESC;

SHOW INDEXES YIELD name, type, entityType, labelsOrTypes, properties, state
RETURN name, type, entityType, labelsOrTypes, properties, state;

SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties
RETURN name, type, entityType, labelsOrTypes, properties;

MATCH (n) WITH labels(n) AS labels, n.name AS name, count(*) AS c
RETURN sum(CASE WHEN name IS NULL OR trim(name) = '' THEN c ELSE 0 END) AS blank_name_nodes,
       sum(CASE WHEN c > 1 THEN 1 ELSE 0 END) AS duplicate_label_name_groups;

MATCH (f:`故障模式`)
OPTIONAL MATCH (i:`关注要素层次`)-[:`故障模式`]->(f)
WITH f, count(DISTINCT i) AS focus_count
OPTIONAL MATCH (f)-[:`故障起因`]->(c)
WITH f, focus_count, count(DISTINCT c) AS cause_count
OPTIONAL MATCH (f)-[:`故障影响`]->(e)
WITH f, focus_count, cause_count, count(DISTINCT e) AS effect_count
RETURN count(f) AS modes,
       sum(CASE WHEN focus_count > 1 THEN 1 ELSE 0 END) AS shared_modes,
       sum(CASE WHEN cause_count > 1 AND effect_count > 1 THEN 1 ELSE 0 END) AS multi_cause_and_effect_modes;
```

## 3. SysML 目录及是否复制

授权读取根目录：`D:\code\SysML 2026.9.3\FMEA-Agent-SysML-Workspace`。
本次聚焦三个模型来源仓库及既有 benchmark 目录；不是对所有工具和实验的完整复审。
三个来源仓库的 `git status --short` 均为空：

| 仓库 | 当前 commit | 本次文件清单 | 许可文件 |
|---|---|---|---|
| SysML-v2-Release | `29a3d2acdd49600cff872e7a55962a40400f3335` | 310 个 .sysml | EPL-2.0（既有来源记录） |
| sysmod-sysmlv2 | `c7216922272b42a9a5935156569478949234136f` | 11 个 .sysml | Apache-2.0 |
| SysML-v2-Applications-and-Examples | `3efe7727a5ebcae92cdb398e420076b3902ff56a` | 0 个独立 .sysml，6 个 Notebook | Apache-2.0 |

无人机产品/功能模型抽查可见 `SYSMOD::*` 导入、跨包类型引用、特化/重定义等；
不能据目录存在就认为已通过 MVP-1 单文件子集适配。
航天 Notebook 本次只列目录，未执行 Notebook 或证明模型可解析。
`07_fmea_benchmark/` 有 11 个预处理来源文件、2 个 normalized JSON，
但 `ground_truth/` 和 `evaluation/` 均无文件。这些实验资产不是已验收的工程基准。

建议暂不复制整库。项目已保存两份来源固定的官方 SysML 样例，详见
[SysML 来源目录](SYSML_SOURCE_CATALOG.md)。本次核对项目样例 hash，其中 Parts Example-2 与既有记录一致。
MVP-2 当前验收重心是知识检索，现有模型足以继续验证系统事实边界。
需要新模型回归时，再按具体测试选择少量文件，保存上游 URL、commit、相对路径、
SHA-256、许可和明确的预期解析结果；不把预处理副本冒充原始工程事实。
本次未新增或复制任何 SysML 样例。

## 4. 规划含义与剩余边界

用户已明确 MVP-2 先证明真实检索可靠、无适用知识时正确返回无匹配。
建议验收区分：应命中、明确不适用、上下文不足/歧义，以及查询/连接故障。
其中“信息不足”和“查询失败”不能伪装为“已成功检索且无适用知识”。
这些是待 Spec 明确的验收建议，本次没有选算法、阈值或宣布指标达标。

用户已确认两表同时保留，并负责协调小组检索样例的人工核对；参考答案尚未建立。
下一步核对原表与图的来源覆盖，
再修订并审查 MVP-2 Spec。最终产品能力以既有 V1 产品边界为讨论基础，避免将全产品功能压入 MVP-2。

本次生产代码、测试、基准和项目依赖均未改变；没有执行检索适配器或重新运行 pytest / ruff / mypy。
LOCAL 文档与输入完整性验证记录在信息对齐台账本次增补中，历史 223 项验证不作为本次新执行证据。
