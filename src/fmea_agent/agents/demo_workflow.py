"""Finite Demo graph; each invocation ends instead of waiting on a live connection."""

from collections.abc import Callable
from typing import Any, Protocol

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from fmea_agent.agents.demo_state import DemoGraphState, DemoSession
from fmea_agent.application.demo_generation import generate_analysis
from fmea_agent.application.demo_intake import (
    WORKING_CONDITIONS,
    analyze_intake,
    record_user_input,
    validate_intake,
)
from fmea_agent.application.demo_ports import (
    DemoLLMClient,
    DemoModelError,
    SourceKnowledgeRepository,
)
from fmea_agent.application.demo_retrieval import prepare_query, retrieve
from fmea_agent.domain.demo_analysis import CandidateReport, DiagnosticReport, target_is_valid
from fmea_agent.domain.demo_evidence import FieldValue
from fmea_agent.domain.demo_knowledge import RetrievalResult


class _DemoNode(Protocol):
    def __call__(self, state: DemoGraphState) -> dict[str, DemoSession]: ...


def fail_session(session: DemoSession, code: str, client: DemoLLMClient) -> DemoSession:
    """Use only safe application codes, never raw exception messages."""
    session.phase = "FAILED"
    session.report = None
    session.generation = None
    session.errors = list(dict.fromkeys([*session.errors, code]))
    session.diagnostic = DiagnosticReport(
        schema_version="demo-v1-diagnostic",
        run_id=session.id,
        status="FAILED",
        input_snapshot=session.inputs.model_copy(deep=True),
        errors=session.errors,
        usage=client.usage(),
    )
    return DemoSession.model_validate(session)


def build_demo_workflow_graph(
    knowledge_repo: SourceKnowledgeRepository,
    llm: DemoLLMClient,
) -> CompiledStateGraph[DemoGraphState, Any, DemoGraphState, Any]:
    """Internal graph. DemoService owns request deduplication and authoritative snapshots."""

    def guarded(
        action: Callable[[DemoSession, DemoGraphState], None],
    ) -> _DemoNode:
        def node(state: DemoGraphState) -> dict[str, DemoSession]:
            session = state.session.model_copy(deep=True)
            try:
                action(session, state)
                session = DemoSession.model_validate(session)
            except DemoModelError as exc:
                session = fail_session(session, exc.code, llm)
            except Exception:
                session = fail_session(session, "WORKFLOW_FAILED", llm)
            return {"session": session}

        return node

    def intake(session: DemoSession, state: DemoGraphState) -> None:
        if session.inputs.conflicts:
            raise DemoModelError("INPUT_CONFLICT")
        if state.message.strip():
            session.inputs = record_user_input(session.inputs, state.message)
            previous_questions = session.intake.questions if session.intake else []
            session.intake = analyze_intake(llm, session.inputs)
            if session.question_rounds == 2 and session.intake.status == "WAITING_INPUT":
                # Accept voluntary new information, but do not open a third question round.
                session.intake.questions = previous_questions
        elif session.intake is None:
            # No invented user evidence; the model can still identify missing target/conditions.
            session.intake = analyze_intake(llm, session.inputs)
        parsed = validate_intake(session.inputs, session.intake)
        session.intake = parsed
        if parsed.status == "BLOCKED":
            raise DemoModelError("INTAKE_BLOCKED")
        if state.continue_unknown:
            if not target_is_valid(
                session.inputs,
                parsed.component_id or "",
                parsed.function_id or "",
            ):
                raise DemoModelError("INVALID_TARGET")
            for name in WORKING_CONDITIONS:
                parsed.context.setdefault(name, FieldValue(value=None, status="UNKNOWN"))
            for name, value in list(parsed.context.items()):
                if value.status != "FACT":
                    parsed.context[name] = FieldValue(
                        value=None,
                        status="UNKNOWN",
                        evidence_ids=value.evidence_ids,
                        limitations=[
                            *value.limitations,
                            "用户明确选择按未知工况继续，未确认模型推断。",
                        ],
                    )
            parsed.status = "READY"
        if parsed.status == "READY":
            session.phase = "READY"
        else:
            session.phase = "WAITING_INPUT"
            if state.message.strip() or session.question_rounds == 0:
                session.question_rounds = min(2, session.question_rounds + 1)

    def retrieval(session: DemoSession, state: DemoGraphState) -> None:
        assert session.intake is not None
        query = prepare_query(session.inputs, session.intake, [])
        if session.retrieval is None:
            try:
                session.retrieval = retrieve(knowledge_repo, query)
            except Exception:
                session.retrieval = RetrievalResult(
                    status="ERROR",
                    terms=query.terms,
                    error_code="RETRIEVAL_FAILED",
                )
        if session.retrieval.status == "ERROR" and not state.allow_without_retrieval:
            session.phase = "READY"
            session.errors = ["RETRIEVAL_ERROR"]
        else:
            session.phase = "RUNNING"

    def generation(session: DemoSession, state: DemoGraphState) -> None:
        assert session.intake is not None and session.retrieval is not None
        session.generation = generate_analysis(
            llm,
            session.inputs,
            session.intake,
            session.retrieval,
            allow_retrieval_error=state.allow_without_retrieval,
        )
        for name, value in session.intake.context.items():
            if value.status != "FACT":
                session.generation.missing_information.append("未确认工况：" + name)
        session.generation.missing_information.extend(session.intake.questions)
        session.generation.missing_information = list(
            dict.fromkeys(
                session.generation.missing_information,
            )
        )

    def document(session: DemoSession, state: DemoGraphState) -> None:
        assert session.intake is not None and session.retrieval is not None
        assert session.generation is not None
        registry = {ref.id: ref for ref in session.inputs.evidence}
        for hit in session.retrieval.hits:
            for ref in [*hit.context, *hit.associations]:
                if ref.id in registry and registry[ref.id] != ref:
                    raise DemoModelError("INVALID_GENERATION_INPUT")
                registry[ref.id] = ref
        exclusions = [
            "未分析功能：" + f.name + " (" + f.id + ")"
            for f in session.inputs.model.functions
            if f.id != session.intake.function_id
        ]
        exclusions.extend(
            "未分析组件：" + c.name + " (" + c.id + ")"
            for c in session.inputs.model.components
            if c.id != session.intake.component_id
        )
        exclusions.extend(
            "排除参考：" + hit.id + "；" + "；".join(hit.reasons)
            for hit in session.retrieval.hits
            if hit.applicability == "REJECTED"
        )
        session.report = CandidateReport(
            schema_version="demo-v1",
            run_id=session.id,
            input_digest=session.input_digest,
            input_snapshot=session.inputs.model_copy(deep=True),
            status="CANDIDATE",
            component_id=session.intake.component_id or "",
            function_id=session.intake.function_id or "",
            context=session.intake.context,
            evidence=list(registry.values()),
            retrieval=session.retrieval,
            generation=session.generation,
            exclusions=exclusions,
            risk_status="NOT_EVALUATED",
            optimization_status="SKIPPED",
            usage=llm.usage(),
        )
        session.phase = "COMPLETE"

    def route(state: DemoGraphState) -> str:
        if state.session.phase in {"COMPLETE", "FAILED"}:
            return END
        if state.operation == "intake":
            return "intake"
        return "retrieve" if state.session.phase == "READY" else END

    graph = StateGraph(DemoGraphState)
    graph.add_node("intake", guarded(intake))
    graph.add_node("retrieve", guarded(retrieval))
    graph.add_node("generate", guarded(generation))
    graph.add_node("document", guarded(document))
    graph.set_conditional_entry_point(route, ["intake", "retrieve", END])
    graph.add_edge("intake", END)
    graph.add_conditional_edges(
        "retrieve",
        lambda s: "generate" if s.session.phase == "RUNNING" else END,
        ["generate", END],
    )
    graph.add_conditional_edges(
        "generate",
        lambda s: "document" if s.session.phase == "RUNNING" else END,
        ["document", END],
    )
    graph.add_edge("document", END)
    return graph.compile()
