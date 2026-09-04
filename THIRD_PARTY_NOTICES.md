# Third-Party Notices

本文件记录被复制进本仓库的第三方 source/test fixtures 的
attribution 与 license preservation。

FMEA-Agent 项目本身不因此声明为任何第三方 license；本项目 license
以仓库根目录声明为准。

## SysML-v2-Release fixtures (EPL-2.0)

Upstream:

```text
repository: https://github.com/Systems-Modeling/SysML-v2-Release
commit:     29a3d2acdd49600cff872e7a55962a40400f3335 (tag 2026-07)
license:    EPL-2.0
```

Copied fixtures (byte-identical to upstream; do not modify):

```text
tests/fixtures/sysml/models/unresolved_import.sysml
    ← sysml/src/training/18. Action Performance/Action Performance Example.sysml

tests/fixtures/sysml/models/parts_example_2_official.sysml
    ← sysml/src/training/07. Parts/Parts Example-2.sysml
```

License text (verbatim copy of upstream LICENSE @ the commit above):

```text
third_party/licenses/EPL-2.0.txt
```

Additional provenance per fixture:
`tests/fixtures/sysml/README.md`；
source catalog：`docs/research/SYSML_SOURCE_CATALOG.md`。
