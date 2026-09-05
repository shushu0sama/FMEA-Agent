# Demo V1 固定演示资料包

此目录提供项目自有 SysML 教学夹具及演示派生资料，仅用于技术演示准备。
后续上传选 `system.sysml`、`design.md`、`bom.csv`；D1 尚无上传 UI 或候选报告。

| 文件 | 用途 |
|---|---|
| system.sysml | D0 固定来源的原样字节副本 |
| bom.csv | UTF-8 部件清单；quantity 空，unit=UNKNOWN |
| design.md | 中文结构、动作、范围及未知工况说明 |
| manifest.json | 文件 SHA-256、派生关系、CSM 来源、解析版本和范围 |

在仓库根目录使用已安装项目依赖的 Python 运行：

```bash
python scripts/build_demo_inputs.py --source tests/fixtures/sysml/models/typed_inside_probe.sysml --output examples/demo_v1
python -m pytest tests/test_demo_inputs_manifest.py -q
```

入口只接受 --source 和 --output（以及 argparse 标准 --help）。重新生成会覆盖这五个输出文件；
来源与输出重叠时拒绝。仅接受 D0 固定 hash 的输入，可使用字节相同的异地副本。
manifest.source.path 表示固定仓库来源，不是调用者机器上的绝对读取路径。
manifest 不含自身 hash；函数返回值和 CLI JSON 另含 manifest.json 的 hash。
不要手改派生文件；修改生成器后重新生成，并运行一致性测试。

源夹具的 .gitattributes 固定 checkout 为 CRLF，与 D0 hash 一致；模型副本按原字节保存，
其他生成文本固定 LF。无生成时间戳；在固定解析器/运行时下重复生成逐字一致。
Git archive 等未应用 checkout 换行规则的输入若 hash 不符会被拒绝，不静默归一化。

CSM 引用使用包内 system.sysml + 原始 source_element_id，并与文件 SHA-256 联用。
CSM ID 与 source ID 不承诺跨版本稳定；Model.hash 仅为 load-context fingerprint，
本可移植包不保存该路径相关值，也不以其替代文件 SHA-256。解析时的内存快照保持原语义。
canonical_model 复用现有 CSM；本 manifest 是 D1 资料清单，不是 D2/D6 候选报告契约。

首个目标为 hydraulicPump 下 motor/spin；根动作 pumpSpin 在 CSM 中保留、明确未纳入分析。
额定参数、数量、材料及工况保持 UNKNOWN；无虚构故障答案或评分。
模型、BOM 与设计说明同源，不能相互充当工程 gold；技术通过不等于工程质量验收。
未调用 DeepSeek/Neo4j，没有跨案例适用性或已批准工程结果。
