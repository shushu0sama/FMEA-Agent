"""Read-only D2 loader: local files -> bounded evidence and an existing CSM."""

import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from fmea_agent.adapters.documents._demo_extract import (
    MAX_FILE_BYTES,
    DemoInputError,
    TextBudget,
    decode_text,
    extract_bom,
    extract_design,
)
from fmea_agent.adapters.sysml import CanonicalSystemMapper, OpenSysMLFileAdapter
from fmea_agent.adapters.sysml.exceptions import (
    CanonicalMappingError,
    SysMLLoadError,
    SysMLParseError,
    UnsupportedSysMLElement,
)
from fmea_agent.domain.demo_evidence import EvidenceRef, InputFileRecord, LoadedInputs, input_digest
from fmea_agent.domain.system_model import Component, Function, System

__all__ = ["DemoInputError", "load_inputs"]


def _read_file(path: Path, suffixes: set[str]) -> bytes:
    if ".." in path.parts or path.suffix.lower() not in suffixes:
        raise DemoInputError("UNSUPPORTED_FORMAT", "文件类型或路径不支持。")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
    except OSError as exc:
        code: Literal["INVALID_MODEL", "UNSUPPORTED_FORMAT"] = (
            "INVALID_MODEL" if suffixes == {".sysml"} else "UNSUPPORTED_FORMAT"
        )
        raise DemoInputError(code, "输入文件不可读取。") from exc
    if len(raw) > MAX_FILE_BYTES:
        raise DemoInputError("LIMIT_EXCEEDED", "输入文件超过 5 MiB。")
    return raw


def _record(
    path: Path,
    raw: bytes,
    kind: Literal["sysml", "document", "bom"],
    parser: str,
    parser_version: str | None = None,
    runtime_version: str | None = None,
) -> InputFileRecord:
    return InputFileRecord(
        id=f"file-{kind}",
        filename=path.name,
        kind=kind,
        sha256=hashlib.sha256(raw).hexdigest(),
        size_bytes=len(raw),
        parser=parser,
        parser_version=parser_version,
        runtime_version=runtime_version,
    )


def load_inputs(
    sysml_path: Path,
    design_path: Path | None = None,
    bom_path: Path | None = None,
) -> LoadedInputs:
    """Load only the named files; never save uploads, follow embedded links or execute data.

    Absolute paths are trusted caller locations, not uploaded filenames. Parent
    traversal components are rejected; exported filenames are basenames. D6 must
    separately assign server-generated upload paths. No arbitrary sidecars are read.
    """
    if not isinstance(sysml_path, Path):
        raise DemoInputError("INVALID_MODEL", "必须提供一个本地 SysML 文件。")
    raw = _read_file(sysml_path, {".sysml"})
    design_raw = _read_file(design_path, {".md", ".txt", ".pdf"}) if design_path else None
    bom_raw = _read_file(bom_path, {".csv", ".xlsx"}) if bom_path else None
    budget = TextBudget()
    source_text = decode_text(raw)
    budget.add(source_text)
    try:
        snapshot = OpenSysMLFileAdapter().load(sysml_path)
        if snapshot.load_status != "ok":
            raise DemoInputError("PARTIAL_MODEL", "SysML 解析不完整，不能继续分析。")
        model = CanonicalSystemMapper().map_snapshot(snapshot)
    except (SysMLLoadError, SysMLParseError, UnsupportedSysMLElement, CanonicalMappingError) as exc:
        raise DemoInputError("INVALID_MODEL", "SysML 无法解析或没有可用的系统根。") from exc
    if _read_file(sysml_path, {".sysml"}) != raw:
        raise DemoInputError("INVALID_MODEL", "SysML 在读取过程中发生变化，请重新载入。")
    if not any(c.id in f.allocated_to for c in model.components for f in model.functions):
        raise DemoInputError("INVALID_MODEL", "SysML 没有可分析的组件/功能对。")
    source = _record(
        sysml_path,
        raw,
        "sysml",
        snapshot.source.parser,
        snapshot.source.parser_version,
        snapshot.source.runtime_version,
    )
    files = [source]
    evidence = [
        EvidenceRef(
            id="ev-sysml-text",
            source_kind="sysml",
            locator=f"{source.id}#text",
            text=source_text,
            content_sha256=source.sha256,
            derived_from=[source.id],
            limitations=["模型原文不是工程审核结论。"],
        )
    ]
    entities: list[System | Component | Function] = [
        model.system,
        *model.components,
        *model.functions,
    ]
    for entity in entities:
        for ref in entity.source_refs:
            ref.source_uri = source.id
            evidence.append(
                EvidenceRef(
                    id=f"ev-sysml-{entity.id}",
                    source_kind="sysml",
                    locator=f"{source.id}#element={quote(ref.source_element_id, safe='')}",
                    text=entity.name,
                    content_sha256=source.sha256,
                    derived_from=["ev-sysml-text"],
                    limitations=["按既有 adapter/mapper 定位模型元素；不承诺跨版本稳定身份。"],
                )
            )
    missing: list[Literal["design", "bom"]] = []
    if design_path is not None and design_raw is not None:
        suffix = design_path.suffix.lower()
        pieces = extract_design(design_raw, suffix, budget)
        parser = "pypdf" if suffix == ".pdf" else "utf-8"
        document = _record(
            design_path,
            design_raw,
            "document",
            parser,
            version("pypdf") if suffix == ".pdf" else None,
        )
        files.append(document)
        for index, (locator, text) in enumerate(pieces, 1):
            evidence.append(
                EvidenceRef(
                    id=f"ev-design-{index}",
                    source_kind="document",
                    locator=f"{document.id}#{locator}",
                    text=text,
                    content_sha256=document.sha256,
                    derived_from=[document.id],
                    limitations=["文档原文仅是来源数据；与模型的一致性及工程适用性尚未确认。"],
                )
            )
    else:
        missing.append("design")
    conflicts = []
    if bom_path is not None and bom_raw is not None:
        suffix = bom_path.suffix.lower()
        rows = extract_bom(bom_raw, suffix, budget)
        bom = _record(
            bom_path,
            bom_raw,
            "bom",
            "openpyxl" if suffix == ".xlsx" else "csv",
            version("openpyxl") if suffix == ".xlsx" else None,
        )
        files.append(bom)
        component_by_source = {
            ref.source_element_id: c for c in model.components for ref in c.source_refs
        }
        row_targets = {}
        for _, row in rows:
            component = component_by_source.get(row["source_element_id"])
            if component is None:
                raise DemoInputError("INVALID_BOM", "BOM source_element_id 未指向当前 CSM 部件。")
            row_targets[row["item_id"]] = component.id
        canonical_ids = {model.system.id, *(c.id for c in model.components)}
        for index, (locator, row) in enumerate(rows, 1):
            component = component_by_source[row["source_element_id"]]
            if row["name"] != component.name:
                conflicts.append(
                    f"BOM {locator} 名称 {row['name']} 与 SysML {component.name} 不一致。"
                )
            parent = row["parent_id"]
            if parent in row_targets:
                parent = row_targets[parent]
            elif parent and parent not in canonical_ids:
                raise DemoInputError("INVALID_BOM", "BOM parent_id 未指向当前模型或 BOM 行。")
            if (parent or None) != component.parent_id:
                conflicts.append(f"BOM {locator} 父级与 SysML 的 {component.parent_id} 不一致。")
            evidence.append(
                EvidenceRef(
                    id=f"ev-bom-{index}",
                    source_kind="bom",
                    locator=f"{bom.id}#{locator}",
                    text=json.dumps(row, ensure_ascii=False),
                    content_sha256=bom.sha256,
                    derived_from=[bom.id],
                    limitations=[
                        f"通过 source_element_id 关联 CSM {component.id}；不代表物料或数量已审核。"
                    ],
                )
            )
    else:
        missing.append("bom")
    return LoadedInputs(
        files=files,
        model=model,
        evidence=evidence,
        missing_files=missing,
        conflicts=conflicts,
        input_digest=input_digest(files),
    )
