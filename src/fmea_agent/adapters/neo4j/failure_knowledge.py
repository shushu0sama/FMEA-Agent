"""Fixed, parameterized reads of legacy graph associations, never original FMEA rows."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self
from uuid import uuid4

from fmea_agent.application.demo_retrieval import match_sort_key
from fmea_agent.domain.demo_evidence import EvidenceRef
from fmea_agent.domain.demo_knowledge import KnowledgeHit, KnowledgeQuery, RetrievalResult

if TYPE_CHECKING:
    from neo4j import Driver, Transaction


MODE_QUERY = """
MATCH (focus:`关注要素层次`)-[:`故障模式`]->(mode:`故障模式`)
WHERE any(term IN $terms WHERE toLower(focus.name) CONTAINS toLower(term)
                           OR toLower(mode.name) CONTAINS toLower(term))
RETURN elementId(mode) AS mode_id, mode.name AS mode_name,
       collect(DISTINCT focus.name) AS matched_names
ORDER BY mode_name, mode_id LIMIT $fetch_limit
"""

CONTEXT_ENTRY_QUERY = """
MATCH (focus:`关注要素层次`)-[:`故障模式`]->(mode:`故障模式`)
CALL {
  WITH focus
  MATCH (focus)-[:`功能`]->(lookup:`功能`) RETURN lookup
  UNION
  WITH focus
  MATCH (focus)-[:`下一低分析层次`]->(lookup:`下一低分析层次`) RETURN lookup
  UNION
  WITH focus
  MATCH (focus)-[:`下一低分析层次`]->(:`下一低分析层次`)
              -[:`下一低层次功能`]->(lookup:`下一低层次功能`) RETURN lookup
}
WITH mode, lookup
WHERE any(term IN $terms WHERE toLower(lookup.name) CONTAINS toLower(term))
RETURN elementId(mode) AS mode_id, mode.name AS mode_name,
       collect(DISTINCT lookup.name) AS matched_names
ORDER BY mode_name, mode_id LIMIT $fetch_limit
"""

FOCUS_CONTEXT_QUERY = """
MATCH (focus:`关注要素层次`)-[link:`故障模式`]->(mode:`故障模式`)
WHERE elementId(mode) IN $mode_ids
CALL {
  WITH focus, mode, link
  RETURN focus AS start, link AS edge, mode AS target
  UNION
  WITH focus, mode, link
  MATCH (focus)-[edge:`功能`]->(target:`功能`) RETURN focus AS start, edge, target
  UNION
  WITH focus, mode, link
  MATCH (focus)-[edge:`下一低分析层次`]->(target:`下一低分析层次`)
  RETURN focus AS start, edge, target
  UNION
  WITH focus, mode, link
  MATCH (focus)-[:`下一低分析层次`]->(start:`下一低分析层次`)
               -[edge:`下一低层次功能`]->(target:`下一低层次功能`) RETURN start, edge, target
  UNION
  WITH focus, mode, link
  MATCH (focus)-[edge:`上一高层次功能及要求`]->(target:`上一高层次功能及要求`)
  RETURN focus AS start, edge, target
}
RETURN DISTINCT elementId(mode) AS mode_id, elementId(start) AS start_id,
       start.name AS start_name, elementId(edge) AS edge_id, type(edge) AS relation,
       elementId(target) AS end_id, target.name AS end_name
ORDER BY mode_id, edge_id LIMIT $edge_limit
"""

ASSOCIATION_QUERY = """
MATCH (mode:`故障模式`)-[edge:`故障起因`|`故障影响`|`预防控制措施`|`探测措施`]->(target)
WHERE elementId(mode) IN $mode_ids
  AND ((type(edge) = '故障起因' AND target:`故障起因`)
    OR (type(edge) = '故障影响' AND target:`故障影响`)
    OR (type(edge) = '预防控制措施' AND target:`预防控制措施`)
    OR (type(edge) = '探测措施' AND target:`探测控制措施`))
RETURN elementId(mode) AS mode_id, elementId(mode) AS start_id,
       mode.name AS start_name, elementId(edge) AS edge_id, type(edge) AS relation,
       elementId(target) AS end_id, target.name AS end_name
ORDER BY mode_id, edge_id LIMIT $edge_limit
"""

SMOKE_FOCUS_QUERY = """
MATCH (focus:`关注要素层次`)-[:`故障模式`]->(:`故障模式`)
WHERE focus.name IS NOT NULL AND trim(focus.name) <> '' AND size(focus.name) <= 80
RETURN DISTINCT elementId(focus) AS focus_id, focus.name AS focus_name
ORDER BY focus_id LIMIT 1
"""

READ_QUERIES = frozenset(
    {MODE_QUERY, CONTEXT_ENTRY_QUERY, FOCUS_CONTEXT_QUERY, ASSOCIATION_QUERY, SMOKE_FOCUS_QUERY}
)
EDGE_LIMIT = 1000
LIMITATIONS = [
    "图无工作簿、工作表及行号，关联不是原始 FMEA 行或已批准结果。",
    "模式级关联不能归属到特定关注要素/功能或当前对象，适用性未知。",
    "elementId 仅用于本次检索定位，不能作为永久知识主键。",
]


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _text(record: dict[str, Any], key: str) -> str:
    value = record[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError("invalid graph string")
    return value


def _error_code(error: Exception) -> str:
    from neo4j.exceptions import AuthError, Neo4jError, ServiceUnavailable, SessionExpired

    if isinstance(error, AuthError):
        return "AUTH_FAILED"
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, TimeoutError):
            return "TIMEOUT"
        current = current.__cause__
    if isinstance(error, Neo4jError):
        if error.code in {
            "Neo.ClientError.Transaction.TransactionTimedOut",
            "Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration",
        }:
            return "TIMEOUT"
        return "QUERY_FAILED"
    if isinstance(error, (ServiceUnavailable, SessionExpired)):
        # Driver 5.28 has no public acquisition-timeout subtype.
        if "timeout" in str(error).lower() or "timed out" in str(error).lower():
            return "TIMEOUT"
        return "CONNECTION_FAILED"
    if isinstance(error, (ValueError, KeyError, TypeError)):
        return "INVALID_RECORD"
    return "QUERY_FAILED"


class Neo4jSourceKnowledgeRepository:
    def __init__(self, driver: Driver | None, database: str):
        self._driver = driver
        self._database = database
        self._config_error: str | None = "CONFIG_MISSING" if driver is None else None
        self._owns_driver = False

    @classmethod
    def from_env(cls) -> Self:
        """Read process configuration only; never inspect local secrets files."""
        uri = os.environ.get("NEO4J_URI", "")
        username = os.environ.get("NEO4J_USERNAME", "")
        password = os.environ.get("NEO4J_PASSWORD", "")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        repo = cls(None, database)
        if not all(value.strip() for value in (uri, username, password)):
            return repo
        if not database.strip():
            repo._config_error = "CONFIG_INVALID"
            return repo
        try:
            from neo4j import GraphDatabase

            repo._driver = GraphDatabase.driver(
                uri,
                auth=(username, password),
                connection_timeout=10.0,
                connection_acquisition_timeout=10.0,
                max_transaction_retry_time=0.0,
                telemetry_disabled=True,
            )
        except ImportError:
            repo._config_error = "DEPENDENCY_MISSING"
        except Exception:
            repo._config_error = "CONFIG_INVALID"
        else:
            repo._config_error = None
            repo._owns_driver = True
        return repo

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_driver and self._driver is not None:
            self._driver.close()
            self._driver = None
            self._config_error = "CLOSED"

    @staticmethod
    def _read(tx: Transaction, template: str, parameters: dict[str, Any]) -> list[dict[str, Any]]:
        if template not in READ_QUERIES:
            raise ValueError("unregistered query")
        return [dict(record) for record in tx.run(template, parameters)]

    def search(self, query: KnowledgeQuery) -> RetrievalResult:
        query = KnowledgeQuery.model_validate(query)
        if self._config_error:
            return RetrievalResult(status="ERROR", terms=query.terms, error_code=self._config_error)
        assert self._driver is not None
        try:
            # Explicit transaction: no execute_read/execute_query automatic retries.
            with self._driver.session(
                database=self._database, default_access_mode="READ"
            ) as session:
                with session.begin_transaction(timeout=10.0) as tx:
                    return self._search(tx, query)
        except Exception as error:
            return RetrievalResult(status="ERROR", terms=query.terms, error_code=_error_code(error))

    def _search(self, tx: Transaction, query: KnowledgeQuery) -> RetrievalResult:
        parameters = {"terms": query.terms, "fetch_limit": query.limit + 1}
        batches = [
            self._read(tx, template, parameters) for template in (MODE_QUERY, CONTEXT_ENTRY_QUERY)
        ]
        modes: dict[str, tuple[str, list[str]]] = {}
        for record in [row for batch in batches for row in batch]:
            identifier, name = _text(record, "mode_id"), _text(record, "mode_name")
            matched = record["matched_names"]
            if not isinstance(matched, list) or any(not isinstance(item, str) for item in matched):
                raise ValueError("invalid matched names")
            if identifier in modes:
                old_name, old_matched = modes[identifier]
                if name != old_name:
                    raise ValueError("conflicting mode name")
                matched = [*old_matched, *matched]
            modes[identifier] = name, matched
        if not modes:
            return RetrievalResult(status="NO_MATCH", terms=query.terms)
        truncated = len(modes) > query.limit or any(len(batch) > query.limit for batch in batches)
        selected = sorted(
            modes, key=lambda key: match_sort_key(modes[key][0], key, query.terms, modes[key][1])
        )[: query.limit]
        params = {"mode_ids": selected, "edge_limit": EDGE_LIMIT + 1}
        contexts = self._read(tx, FOCUS_CONTEXT_QUERY, params)
        associations = self._read(tx, ASSOCIATION_QUERY, params)
        edge_truncated = len(contexts) > EDGE_LIMIT or len(associations) > EDGE_LIMIT
        stamp = datetime.now(UTC).isoformat()
        retrieval_id = uuid4().hex
        hits = {}
        for identifier in selected:
            name, matched = modes[identifier]
            mode_ref = self._evidence({"node_id": identifier, "name": name}, stamp, retrieval_id)
            reasons = [
                "有界词法检索；只在两个入口的有限候选中排序，不保证全库最优或完整召回。",
                "查询词（原样）：" + _json(query.terms),
                "匹配入口名称：" + _json(sorted(set(matched))),
                "词法命中不证明适用于当前工程对象。",
            ]
            if truncated or edge_truncated:
                reasons.append("结果已截断：模式或关系上下文达到查询上限。")
            hits[identifier] = KnowledgeHit(
                id=f"neo4j-{retrieval_id}-mode-{identifier}",
                name=name,
                context=[mode_ref],
                applicability="SOURCE_CONTEXT_ONLY"
                if query.scope == "SOURCE_LOOKUP"
                else "UNKNOWN",
                reasons=reasons,
            )
        for records, destination in ((contexts, "context"), (associations, "associations")):
            for record in records[:EDGE_LIMIT]:
                identifier = _text(record, "mode_id")
                if identifier not in hits:
                    raise ValueError("unexpected mode association")
                data = {
                    key: _text(record, key)
                    for key in (
                        "start_id",
                        "start_name",
                        "edge_id",
                        "relation",
                        "end_id",
                        "end_name",
                    )
                }
                ref = self._evidence(data, stamp, retrieval_id)
                refs = getattr(hits[identifier], destination)
                existing = next((item for item in refs if item.id == ref.id), None)
                if existing is None:
                    refs.append(ref)
                elif existing != ref:
                    raise ValueError("conflicting relationship evidence")
        return RetrievalResult(
            status="HITS",
            terms=query.terms,
            hits=list(hits.values()),
            truncated=truncated or edge_truncated,
        )

    def _evidence(self, data: dict[str, str], stamp: str, retrieval_id: str) -> EvidenceRef:
        text = _json(data)
        locator = {key: value for key, value in data.items() if key.endswith("_id")}
        locator.update(database=self._database, retrieved_at=stamp, retrieval_id=retrieval_id)
        kind = "edge" if "edge_id" in data else "node"
        identifier = data[f"{kind}_id"]
        return EvidenceRef(
            id=f"neo4j-{retrieval_id}-{kind}-{identifier}",
            source_kind="neo4j",
            locator=_json(locator),
            text=text,
            content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            limitations=list(LIMITATIONS),
        )

    def smoke_focus(self) -> tuple[str | None, str | None, str | None]:
        """Return one source locator/name for local smoke only; caller must not print it."""
        if self._config_error:
            return None, None, self._config_error
        assert self._driver is not None
        try:
            with self._driver.session(
                database=self._database, default_access_mode="READ"
            ) as session:
                with session.begin_transaction(timeout=10.0) as tx:
                    records = self._read(tx, SMOKE_FOCUS_QUERY, {})
                    if not records:
                        return None, None, "NO_SOURCE_FOCUS"
                    return _text(records[0], "focus_id"), _text(records[0], "focus_name"), None
        except Exception as error:
            return None, None, _error_code(error)
