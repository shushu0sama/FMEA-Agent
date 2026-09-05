"""Build the pinned D1 teaching pack using the existing SysML adapter and mapper.

Run from a checkout with the project's existing dependencies installed. This is
a fixed-case generator, not a general document loader or an FMEA analysis service.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from fmea_agent.adapters.sysml import CanonicalSystemMapper, OpenSysMLFileAdapter
from fmea_agent.domain.system_model import Component, Function, System

SOURCE_PATH = "tests/fixtures/sysml/models/typed_inside_probe.sysml"
SOURCE_SHA256 = "fb1637c8ae7ec620d77a10f65efa7d4e5a352523de8b110046c0b3043447f6e5"
OUTPUT_NAMES = ("system.sysml", "bom.csv", "design.md", "README.md", "manifest.json")
UNKNOWN_FIELDS = (
    "额定电压", "转速", "材料", "数量", "运行环境", "运行阶段", "工作循环", "主要负载",
)


def build_demo_inputs(source: Path, destination: Path) -> dict[str, str]:
    """Return output filename -> SHA-256, including manifest's hash externally.

    Accept only the D0 byte baseline (including byte-identical relocated copies).
    All input checks, real parsing and rendering precede output writes. Source
    overlap, including existing output hardlinks, is rejected. Repository origin
    and portable local references replace machine-specific load paths in the pack.
    """
    source = source.expanduser().resolve(strict=True)
    destination = destination.expanduser().resolve()
    if destination == source or destination == source.parent:
        raise ValueError("source/output overlap is forbidden")
    for name in OUTPUT_NAMES:
        target = destination / name
        if target.resolve() == source or (target.exists() and target.samefile(source)):
            raise ValueError("source/output overlap is forbidden")
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError("output must be a regular file, not a link or directory")
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA256:
        raise ValueError("source SHA-256 does not match the accepted D0 baseline")

    snapshot = OpenSysMLFileAdapter().load(source)
    if snapshot.load_status != "ok" or snapshot.diagnostics:
        raise ValueError("the fixed demo requires a complete parse with zero diagnostics")
    model = CanonicalSystemMapper().map_snapshot(snapshot)
    # Content is pinned, but a changed parser/mapper must not silently alter scope.
    motors = [c for c in model.components if c.name == "motor"]
    if model.system.name != "hydraulicPump" or len(motors) != 1:
        raise ValueError("fixed demo system/component mapping changed")
    motor = motors[0]
    targets = [f for f in model.functions if f.name == "spin" and f.allocated_to == [motor.id]]
    excluded = [f for f in model.functions if f.allocated_to == [model.system.id]]
    if len(targets) != 1 or [f.name for f in excluded] != ["pumpSpin"]:
        raise ValueError("fixed demo function mapping changed")
    if source.read_bytes() != original:
        raise ValueError("source SHA-256 changed during parsing")

    entities: list[System | Component | Function] = [
        model.system, *model.components, *model.functions,
    ]
    for entity in entities:
        for ref in entity.source_refs:
            ref.source_uri = "system.sysml"
    source_ids = [ref.source_element_id for entity in entities for ref in entity.source_refs]

    bom = io.StringIO(newline="")
    writer = csv.writer(bom, lineterminator="\n")
    writer.writerow(["item_id", "parent_id", "name", "quantity", "unit", "source_element_id"])
    bom_rows = []
    for row, component in enumerate(model.components, start=2):
        source_id = component.source_refs[0].source_element_id
        writer.writerow([
            component.id, component.parent_id, component.name, "", "UNKNOWN", source_id,
        ])
        bom_rows.append({
            "row": row, "item_id": component.id, "source_element_id": source_id,
            "unknown_fields": ["quantity", "unit"],
        })

    design = [
        "# hydraulicPump 演示设计说明", "",
        "本文件为演示派生资料，仅从固定 SysML 教学夹具提取结构与动作。",
        "它不是真实航空产品或经工程验证的液压系统设计，不构成工程批准或独立证据。", "",
        "## 来源与已知结构", "",
        f"来源：`{SOURCE_PATH}` 的原样副本 `system.sysml`。",
        f"SHA-256：`{SOURCE_SHA256}`。",
        "以下 FACT 仅指模型已表达的事实，不表示产品设计已审核。", "",
        "| 类别 | 名称 | CSM ID | 归属 CSM ID | source_element_id |",
        "|---|---|---|---|---|",
        f"| System | {model.system.name} | {model.system.id} | — | "
        f"{model.system.source_refs[0].source_element_id} |",
    ]
    for component in model.components:
        design.append(
            f"| Component | {component.name} | {component.id} | {component.parent_id} | "
            f"{component.source_refs[0].source_element_id} |"
        )
    for function in model.functions:
        design.append(
            f"| Function | {function.name} | {function.id} | {', '.join(function.allocated_to)} | "
            f"{function.source_refs[0].source_element_id} |"
        )
    design.extend([
        "", "## 演示分析范围", "",
        f"首个目标：`{motor.name}`（`{motor.id}`）/ `{targets[0].name}`（`{targets[0].id}`）。",
        "根动作 `pumpSpin` 在 CSM 中保留，但未纳入分析：当前 workflow 只分析组件功能。",
        "这只是后续分析的范围声明；本资料包未执行失效生成。", "",
        "## 未知信息", "",
        *[f"- {field}：UNKNOWN（模型未表达，不填数值或演示假设）。" for field in UNKNOWN_FIELDS],
        "", "BOM 只列实际映射的 Component；系统根以 parent_id 关联，不作为采购物料行。",
        "quantity 留空、unit 为 UNKNOWN；一条部件声明不能推导物料数量。",
        "类型定义不直接变成 Component，component_type 保持未知；映射通知保存在 manifest。", "",
        "## 使用限制", "",
        "不提供原始失效答案、已有控制、S/O/D/AP 或标准符合性结论。",
        "Neo4j 历史案例与本模型独立；派生 BOM/设计说明不是工程正确率的独立 gold。",
        "工况需在后续交互阶段补充或明确保留 UNKNOWN。", "",
    ])
    readme = """# Demo V1 固定演示资料包

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
python scripts/build_demo_inputs.py --source {source_path} --output examples/demo_v1
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
"""
    payloads = {
        "system.sysml": original,
        "bom.csv": bom.getvalue().encode("utf-8"),
        "design.md": "\n".join(design).encode("utf-8"),
        "README.md": readme.format(source_path=SOURCE_PATH).encode("utf-8"),
    }
    manifest = {
        "schema_version": "demo-v1-input-pack",
        "source": {
            "path": SOURCE_PATH, "sha256": SOURCE_SHA256,
            "ownership": "PROJECT_OWNED_TEACHING_FIXTURE",
        },
        "files": {
            name: {
                "sha256": hashlib.sha256(content).hexdigest(),
                "derived_from": [SOURCE_PATH] if name == "system.sysml" else ["system.sysml"],
            }
            for name, content in payloads.items()
        },
        "parser": {
            "name": snapshot.source.parser, "version": snapshot.source.parser_version,
            "runtime_version": snapshot.source.runtime_version, "adapter": snapshot.source.adapter,
            "load_status": snapshot.load_status, "diagnostics_count": len(snapshot.diagnostics),
        },
        "canonical_model": model.model_dump(mode="json"),
        "source_element_ids": source_ids,
        "bom_rows": bom_rows,
        "analysis_scope": {
            "component_id": motor.id, "function_id": targets[0].id,
            "excluded_function_ids": [f.id for f in excluded],
            "exclusion_reason": "根动作 pumpSpin 未纳入分析；当前 workflow 只分析组件功能。",
        },
        "limitations": [
            "教学夹具及同源派生资料，不是经工程审核的产品或独立 gold。",
            "文件 SHA-256 与 source_element_id 联用；不提供跨版本稳定身份。",
            "未表达的数量、参数与工况为 UNKNOWN；不从名称或声明数量推断。",
            "不生成失效答案或 S/O/D/AP；未执行工程分析或批准。",
        ],
    }
    payloads["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        (destination / name).write_bytes(content)
    return {name: hashlib.sha256(content).hexdigest() for name, content in payloads.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the fixed D1 demo input pack")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_demo_inputs(args.source, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
