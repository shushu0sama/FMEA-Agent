"""Bounded strict JSON decoding shared by the untrusted model boundaries."""

import json
from typing import Any

MAX_JSON_BYTES = 1024 * 1024


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError("non-finite JSON number")


def json_object(raw: str) -> dict[str, Any]:
    if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
        raise ValueError("JSON size limit")
    value = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value
