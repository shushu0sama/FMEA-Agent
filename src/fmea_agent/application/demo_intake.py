"""D2 deterministic intake boundary; model-driven dialogue is implemented in D4."""

from fmea_agent.domain.demo_analysis import IntakeResult, target_is_valid
from fmea_agent.domain.demo_evidence import LoadedInputs


def validate_intake(inputs: LoadedInputs, intake: IntakeResult) -> IntakeResult:
    """Block invalid targets, unresolved conflicts and fabricated references."""
    issues = list(inputs.conflicts)
    component_ids = {component.id for component in inputs.model.components}
    function_ids = {
        function.id
        for function in inputs.model.functions
        if component_ids.intersection(function.allocated_to)
    }
    if intake.component_id is not None and intake.component_id not in component_ids:
        issues.append("组件 ID 不存在于当前模型中。")
    if intake.function_id is not None and intake.function_id not in function_ids:
        issues.append("功能 ID 不存在于当前模型的可分析功能中。")
    if intake.component_id is not None and intake.function_id is not None:
        if not target_is_valid(inputs, intake.component_id, intake.function_id):
            issues.append("分析目标不属于当前模型的合法组件/功能对。")
    ids = {ref.id for ref in inputs.evidence}
    if any(not set(value.evidence_ids) <= ids for value in intake.context.values()):
        issues.append("工况引用不存在于本次输入证据中。")
    if issues:
        return IntakeResult(
            **{
                **intake.model_dump(),
                "status": "BLOCKED",
                "questions": [*intake.questions, *issues],
            }
        )
    return IntakeResult.model_validate(intake)
