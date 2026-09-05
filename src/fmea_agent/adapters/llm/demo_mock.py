"""Explicit offline teaching client; deterministic inferences, never live evidence."""

import json

from fmea_agent.application.demo_ports import DemoModelError
from fmea_agent.domain.demo_knowledge import KnowledgeQuery, RetrievalResult


class MockSourceKnowledgeRepository:
    def search(self, query: KnowledgeQuery) -> RetrievalResult:
        return RetrievalResult(status="NO_MATCH", terms=query.terms)


class DemoMockLLMClient:
    def __init__(self) -> None:
        self._count = 0

    def usage(self) -> dict[str, int | str | None]:
        return {
            "request_count": self._count,
            "model": "deterministic-demo-mock",
            "mode": "mock",
            "retrieval_mode": "FAKE_NO_MATCH",
            "total_tokens": None,
        }

    def generate(self, prompt: str) -> str:
        if self._count >= 6:
            raise DemoModelError("CALL_BUDGET_EXCEEDED")
        self._count += 1
        data = json.loads(prompt.split("\n", 1)[1])
        if "allowed_targets" in data:
            targets = data["allowed_targets"]
            # UI's explicit selection is recorded in the last user message.
            messages = [
                ref["text"]
                for ref in data["untrusted_data"]["evidence"]
                if ref["source_kind"] == "user"
            ]
            target = next(
                (
                    t
                    for t in targets
                    if messages
                    and t["component_id"] in messages[-1]
                    and t["function_id"] in messages[-1]
                ),
                targets[0],
            )
            result = dict(data["example"])
            result.update(component_id=target["component_id"], function_id=target["function_id"])
        else:
            result = dict(data["example"])
            result["rows"][0]["mode"]["value"] = "模拟候选：功能未按预期实现"
            result["assumptions"] = ["显式 mock 教学输出，不是实时模型或历史知识结论。"]
        return json.dumps(result, ensure_ascii=False)
