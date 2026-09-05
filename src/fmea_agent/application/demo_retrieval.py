"""D3 bounded lexical retrieval policy; no database or generation dependency."""

import unicodedata

from fmea_agent.application.demo_intake import validate_intake
from fmea_agent.application.demo_ports import SourceKnowledgeRepository
from fmea_agent.domain.demo_analysis import IntakeResult
from fmea_agent.domain.demo_evidence import LoadedInputs
from fmea_agent.domain.demo_knowledge import KnowledgeHit, KnowledgeQuery, RetrievalResult


def _normalized(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def match_sort_key(
    name: str, identifier: str, terms: list[str], context_names: list[str]
) -> tuple[bool, str, str]:
    """Normalize for ranking only; original names and graph identities survive."""
    exact = bool(
        {_normalized(term) for term in terms}.intersection(
            _normalized(value) for value in [name, *context_names]
        )
    )
    return not exact, name, identifier


def prepare_query(inputs: LoadedInputs, intake: IntakeResult, terms: list[str]) -> KnowledgeQuery:
    inputs = LoadedInputs.model_validate(inputs)
    intake = validate_intake(inputs, IntakeResult.model_validate(intake))
    if intake.status != "READY":
        raise ValueError("retrieval requires a valid READY target")
    component = next(item for item in inputs.model.components if item.id == intake.component_id)
    function = next(item for item in inputs.model.functions if item.id == intake.function_id)
    names = [component.name, function.name]
    for term in terms:
        if term not in names and not any(
            ref.source_kind == "user" and term in ref.text for ref in inputs.evidence
        ):
            raise ValueError("additional query terms require recorded user evidence")
    return KnowledgeQuery(
        terms=list(dict.fromkeys([*names, *terms])),
        scope="TARGET_ANALYSIS",
        component_id=component.id,
        function_id=function.id,
    )


def retrieve(
    repository: SourceKnowledgeRepository,
    query: KnowledgeQuery,
    *,
    rejected_ids: dict[str, str] | None = None,
    rejected_terms: dict[str, str] | None = None,
) -> RetrievalResult:
    """Explicit ID/name exclusions preserve HITS and the original retrieval audit."""
    query = KnowledgeQuery.model_validate(query)
    result = RetrievalResult.model_validate(repository.search(query)).model_copy(deep=True)
    ids = rejected_ids or {}
    names = rejected_terms or {}
    if any(not reason.strip() for reason in [*ids.values(), *names.values()]):
        raise ValueError("an explicit exclusion requires a reason")
    for hit in result.hits:
        reasons = ([ids[hit.id]] if hit.id in ids else []) + [
            reason for term, reason in names.items() if _normalized(term) == _normalized(hit.name)
        ]
        if reasons:
            hit.applicability = "REJECTED"
            hit.reasons.extend(reasons)
    return RetrievalResult.model_validate(result)


def reference_hits(result: RetrievalResult) -> list[KnowledgeHit]:
    """The downstream generation boundary must use this filtered reference view."""
    return [hit.model_copy(deep=True) for hit in result.hits if hit.applicability != "REJECTED"]
