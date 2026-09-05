# 本机工程输入

请将原始 FMEA Excel / CSV 的副本放入 `local_data/fmea_inputs/excel/`。
保留原文件名、工作表及原内容，首次检查以只读方式进行；不运行宏、不重新保存原文件，也不自动导入 Neo4j。

本目录仅此说明文件进入 Git，其余内容由 `.gitignore` 排除。
`git add -f` 会绕过 ignore，不能用于提交工程输入。
Git 忽略不是文件备份；原始文件仍由用户保管。换机器或工作树时需要另行提供本机输入。

目标目录不存在时，可在仓库根目录执行：

```powershell
New-Item -ItemType Directory -Force -Path local_data/fmea_inputs/excel
```

放入文件后，后续只读核对文件身份、工作表、列名及少量行级来源。
文件存在不等于内容已审核、已获迁移授权或已被程序导入。
不要在工作簿或本目录说明中保存数据库口令。

当前已确认事实和待答问题见
[MVP-2 规划前信息对齐](../docs/product/MVP_2_PREPLANNING_ALIGNMENT.md)。
