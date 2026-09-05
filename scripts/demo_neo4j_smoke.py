"""Read-only local smoke. Output only statuses/counts; never graph text or credentials."""

import json
import logging
from datetime import UTC, datetime
from uuid import uuid4

from fmea_agent.adapters.neo4j.failure_knowledge import Neo4jSourceKnowledgeRepository
from fmea_agent.domain.demo_knowledge import KnowledgeQuery


def main() -> int:
    # A locally configured debug logger must not expose parameters in smoke output.
    logging.getLogger("neo4j").setLevel(logging.CRITICAL)
    summary: dict[str, object] = {
        "evidence": "LOCAL",
        "checked_at": datetime.now(UTC).isoformat(),
        "read_only": True,
    }
    with Neo4jSourceKnowledgeRepository.from_env() as repo:
        identifier, name, error = repo.smoke_focus()
        if error:
            summary.update(
                status="SKIPPED"
                if error == "CONFIG_MISSING"
                else ("FAILED" if error == "NO_SOURCE_FOCUS" else "ERROR"),
                reason=error,
            )
        else:
            assert identifier is not None and name is not None
            lookup = repo.search(KnowledgeQuery(terms=[name], scope="SOURCE_LOOKUP"))
            absent = repo.search(
                KnowledgeQuery(terms=["demo-no-match-" + uuid4().hex], scope="SOURCE_LOOKUP")
            )
            located = any(
                json.loads(ref.locator).get("start_id") == identifier
                and json.loads(ref.locator).get("edge_id")
                and json.loads(ref.locator).get("database")
                and json.loads(ref.locator).get("retrieved_at")
                for hit in lookup.hits
                for ref in hit.context
            )
            passed = lookup.status == "HITS" and located and absent.status == "NO_MATCH"
            summary.update(
                status="PASS" if passed else "FAILED",
                lookup_status=lookup.status,
                lookup_error=lookup.error_code,
                hit_count=len(lookup.hits),
                context_count=sum(len(hit.context) for hit in lookup.hits),
                association_count=sum(len(hit.associations) for hit in lookup.hits),
                locator_verified=bool(located),
                truncated=lookup.truncated,
                absent_status=absent.status,
                absent_error=absent.error_code,
            )
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if summary["status"] in {"PASS", "SKIPPED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
