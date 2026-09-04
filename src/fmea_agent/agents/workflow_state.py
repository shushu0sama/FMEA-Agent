"""Structured workflow state for the MVP-0 FMEA graph.

The state is a typed Pydantic model, not a chat transcript. LangGraph only
appears in the graph builder; the state itself depends on domain models alone.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from fmea_agent.domain.fmea import (
    AnalysisContext,
    FailureModeCandidate,
    FMEAItem,
    RiskAssessment,
)
from fmea_agent.domain.system_model import Component, Function, System


class StageStatus(StrEnum):
    """Explicit per-stage workflow status."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_EVALUATED = "NOT_EVALUATED"
    SKIPPED = "SKIPPED"


class WorkflowRequest(BaseModel):
    """Targets for one analysis run; supplied by the caller (CLI/fixture loader)."""

    system_id: str
    component_id: str
    function_id: str
    title: str


class WorkflowState(BaseModel):
    """All data carried between the seven AIAG-VDA-shaped stages."""

    request: WorkflowRequest | None = None
    analysis_context: AnalysisContext | None = None
    system: System | None = None
    selected_component: Component | None = None
    selected_function: Function | None = None
    selected_item: FMEAItem | None = None
    failure_candidates: list[FailureModeCandidate] = Field(default_factory=list)
    risk: RiskAssessment | None = None
    stage_status: dict[str, StageStatus] = Field(default_factory=dict)
    output: dict[str, Any] | None = None
    errors: list[str] = Field(default_factory=list)
