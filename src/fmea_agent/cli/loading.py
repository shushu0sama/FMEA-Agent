"""Load demo fixtures into domain models and in-memory repositories.

Data plumbing only: JSON decoding and model validation. No FMEA semantics.
"""

import json
from pathlib import Path
from typing import Any

from fmea_agent.adapters.inmemory import (
    FailureKnowledgeEntry,
    InMemoryFailureKnowledgeRepository,
    InMemorySystemModelRepository,
)
from fmea_agent.agents.workflow_state import WorkflowRequest
from fmea_agent.domain.fmea import FailureModeCandidate
from fmea_agent.domain.system_model import Component, Function, System


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"fixture {path} must contain a JSON object")
    return data


def load_system_fixture(
    path: Path,
) -> tuple[InMemorySystemModelRepository, WorkflowRequest]:
    """Load system facts and the analysis request from a system fixture JSON."""
    data = _read_json(path)
    try:
        system = System.model_validate(data["system"])
        components = [Component.model_validate(c) for c in data["components"]]
        functions = [Function.model_validate(f) for f in data["functions"]]
        request = WorkflowRequest.model_validate(data["analysis_request"])
    except KeyError as exc:
        raise ValueError(f"fixture {path} is missing required key {exc.args[0]!r}") from exc
    return (
        InMemorySystemModelRepository(
            system=system, components=components, functions=functions
        ),
        request,
    )


def load_failure_library(path: Path) -> InMemoryFailureKnowledgeRepository:
    """Load name-keyed demo failure knowledge from a library fixture JSON."""
    data = _read_json(path)
    try:
        raw_entries = data["entries"]
    except KeyError as exc:
        raise ValueError(f"failure library {path} is missing required key 'entries'") from exc
    entries = []
    for raw in raw_entries:
        try:
            entries.append(
                FailureKnowledgeEntry(
                    item_name=raw["item_name"],
                    function_name=raw["function_name"],
                    failure_modes=[
                        FailureModeCandidate.model_validate(fm) for fm in raw["failure_modes"]
                    ],
                )
            )
        except KeyError as exc:
            raise ValueError(
                f"failure library {path} entry is missing required key {exc.args[0]!r}"
            ) from exc
    return InMemoryFailureKnowledgeRepository(entries)
