"""One in-process session per service/client; snapshots are data, not write authority.

Keep the service in the UI's session storage. New inputs require a new service with
a fresh client. Process restart starts a new session; no durable exactly-once claim.
Adapter lifetimes remain the caller's responsibility.
"""

import hashlib
import json
from threading import Lock
from typing import Literal
from uuid import uuid4

from fmea_agent.agents.demo_state import DemoGraphState, DemoSession
from fmea_agent.agents.demo_workflow import build_demo_workflow_graph, fail_session
from fmea_agent.application.demo_ports import (
    DemoLLMClient,
    DemoModelError,
    SourceKnowledgeRepository,
)
from fmea_agent.domain.demo_evidence import LoadedInputs


class DemoService:
    def __init__(self, knowledge_repo: SourceKnowledgeRepository, llm: DemoLLMClient) -> None:
        self._llm = llm
        self._graph = build_demo_workflow_graph(knowledge_repo, llm)
        self._lock = Lock()
        self._session: DemoSession | None = None
        self._requests: dict[str, str] = {}
        self._input_fingerprint: str | None = None

    @staticmethod
    def _fingerprint(inputs: LoadedInputs) -> str:
        data = inputs.model_dump(mode="json")
        # Dialogue evidence is appended by D4; immutable input facts remain bound to this service.
        data["evidence"] = [ref for ref in data["evidence"] if ref["source_kind"] != "user"]
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _check_snapshot(self, session: DemoSession) -> None:
        if self._session is None or session.id != self._session.id:
            raise DemoModelError("UNKNOWN_SESSION")
        if (
            session.input_digest != self._session.input_digest
            or self._fingerprint(session.inputs) != self._input_fingerprint
        ):
            raise DemoModelError("NEW_SESSION_REQUIRED")

    def _execute(
        self,
        operation: Literal["start", "answer", "analyze"],
        message: str,
        request_id: str,
        *,
        continue_unknown: bool = False,
        allow_without_retrieval: bool = False,
    ) -> DemoSession:
        assert self._session is not None
        if not request_id.strip():
            raise DemoModelError("INVALID_REQUEST_ID")
        signature = hashlib.sha256(
            json.dumps(
                [operation, message, continue_unknown, allow_without_retrieval],
            ).encode()
        ).hexdigest()
        if request_id in self._requests:
            if self._requests[request_id] != signature:
                raise DemoModelError("REQUEST_ID_CONFLICT")
            return self._session.model_copy(deep=True)
        if (
            operation == "answer"
            and self._session.retrieval is not None
            and self._session.phase
            not in {
                "COMPLETE",
                "FAILED",
            }
        ):
            # Once retrieval begins, target/context are frozen for that analysis.
            raise DemoModelError("ANALYSIS_ALREADY_STARTED")
        # Reserve before any adapter call; terminal/interrupted requests are never auto-retried.
        self._requests[request_id] = signature
        self._session.handled_request_ids.append(request_id)
        if self._session.phase in {"COMPLETE", "FAILED"}:
            return self._session.model_copy(deep=True)
        state = DemoGraphState(
            session=self._session,
            operation="analyze" if operation == "analyze" else "intake",
            message=message,
            continue_unknown=continue_unknown,
            allow_without_retrieval=allow_without_retrieval,
        )
        try:
            for update in self._graph.stream(state, stream_mode="values"):
                self._session = DemoSession.model_validate(update["session"]).model_copy(deep=True)
        except BaseException as exc:
            self._session = fail_session(
                self._session,
                "WORKFLOW_FAILED" if isinstance(exc, Exception) else "REQUEST_INTERRUPTED",
                self._llm,
            )
            if not isinstance(exc, Exception):
                raise
        return self._session.model_copy(deep=True)

    def start(self, inputs: LoadedInputs, message: str, request_id: str) -> DemoSession:
        with self._lock:
            if not request_id.strip():
                raise DemoModelError("INVALID_REQUEST_ID")
            if self._session is not None:
                if (
                    self._fingerprint(inputs) != self._input_fingerprint
                    or request_id not in self._requests
                ):
                    raise DemoModelError("NEW_SESSION_REQUIRED")
            else:
                if self._llm.usage().get("request_count", 0) != 0:
                    raise DemoModelError("FRESH_CLIENT_REQUIRED")
                inputs = LoadedInputs.model_validate(inputs).model_copy(deep=True)
                self._input_fingerprint = self._fingerprint(inputs)
                self._session = DemoSession(
                    id=uuid4().hex, input_digest=inputs.input_digest, inputs=inputs
                )
            return self._execute("start", message, request_id)

    def answer(
        self,
        session: DemoSession,
        message: str,
        request_id: str,
        continue_unknown: bool = False,
    ) -> DemoSession:
        with self._lock:
            self._check_snapshot(session)
            return self._execute("answer", message, request_id, continue_unknown=continue_unknown)

    def analyze(
        self,
        session: DemoSession,
        request_id: str,
        allow_without_retrieval: bool = False,
    ) -> DemoSession:
        with self._lock:
            self._check_snapshot(session)
            return self._execute(
                "analyze", "", request_id, allow_without_retrieval=allow_without_retrieval
            )
