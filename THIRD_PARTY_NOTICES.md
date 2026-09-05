# 第三方声明

本文件记录被复制进本仓库的第三方 source/test fixtures 的
来源署名与许可证保留情况。

FMEA-Agent 项目本身不因此声明为任何第三方 license；本项目 license
以仓库根目录声明为准。

## SysML-v2-Release 测试夹具（EPL-2.0）

上游来源：

```text
repository: https://github.com/Systems-Modeling/SysML-v2-Release
commit:     29a3d2acdd49600cff872e7a55962a40400f3335 (tag 2026-07)
license:    EPL-2.0
```

复制的测试夹具（与上游逐字节一致，不得修改）：

```text
tests/fixtures/sysml/models/unresolved_import.sysml
    ← sysml/src/training/18. Action Performance/Action Performance Example.sysml

tests/fixtures/sysml/models/parts_example_2_official.sysml
    ← sysml/src/training/07. Parts/Parts Example-2.sysml
```

许可证文本（逐字复制自上述 commit 的上游 LICENSE）：

```text
third_party/licenses/EPL-2.0.txt
```

各测试夹具的补充来源追踪：
`tests/fixtures/sysml/README.md`；
来源目录：`docs/research/SYSML_SOURCE_CATALOG.md`。
