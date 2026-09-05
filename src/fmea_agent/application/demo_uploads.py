"""Untrusted upload names are labels; only generated paths reach the D2 loader."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fmea_agent.adapters.documents.demo_inputs import load_inputs
from fmea_agent.domain.demo_evidence import LoadedInputs, input_digest


@dataclass(frozen=True)
class UploadedInput:
    name: str
    data: bytes


class UploadError(ValueError):
    """Safe upload diagnostics with no underlying exception text."""


def load_uploaded_inputs(
    sysml: UploadedInput | None,
    design: UploadedInput | None = None,
    bom: UploadedInput | None = None,
) -> LoadedInputs:
    if sysml is None:
        raise UploadError("必须提供一个 SysML 模型文件。")
    uploads = [sysml, design, bom]
    allowed = [{".sysml"}, {".md", ".txt", ".pdf"}, {".csv", ".xlsx"}]
    for upload, suffixes in zip(uploads, allowed, strict=True):
        if upload is None:
            continue
        if len(upload.data) > 5 * 1024 * 1024:
            raise UploadError("输入文件超过 5 MiB。")
        if not upload.name or len(upload.name) > 512 or "\x00" in upload.name:
            raise UploadError("文件名无效。")
        if Path(upload.name).suffix.lower() not in suffixes:
            raise UploadError("文件类型不支持。")
    with TemporaryDirectory(prefix="fmea-demo-") as directory:
        paths: list[Path | None] = []
        for upload in uploads:
            if upload is None:
                paths.append(None)
                continue
            path = Path(directory) / (uuid4().hex + Path(upload.name).suffix.lower())
            path.write_bytes(upload.data)
            paths.append(path)
        assert paths[0] is not None
        loaded = load_inputs(paths[0], paths[1], paths[2])
    originals = {
        kind: Path(upload.name.replace("\\", "/")).name
        for kind, upload in zip(("sysml", "document", "bom"), uploads, strict=True)
        if upload is not None
    }
    for record in loaded.files:
        record.filename = originals[record.kind]
    loaded.input_digest = input_digest(loaded.files)
    return LoadedInputs.model_validate(loaded.model_dump(mode="json"))
