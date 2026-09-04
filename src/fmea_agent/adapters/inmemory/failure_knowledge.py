"""In-memory FailureKnowledgeRepository for name-keyed fixture failure knowledge."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from fmea_agent.domain.fmea import FailureModeCandidate


@dataclass(frozen=True)
class FailureKnowledgeEntry:
    """Name-keyed failure-knowledge record, mirroring the fixture library shape.

    The lookup key uses display names because MVP-0 fixture knowledge is
    name-keyed; candidate `item_id`/`function_id` stay stable domain IDs and
    are filled by the workflow when the corresponding elements are known.
    """

    item_name: str
    function_name: str
    failure_modes: list[FailureModeCandidate] = field(default_factory=list)


class InMemoryFailureKnowledgeRepository:
    """Returns candidate failure knowledge for an exact (item, function) name pair."""

    def __init__(self, entries: Iterable[FailureKnowledgeEntry] = ()) -> None:
        self._index: dict[tuple[str, str], list[FailureModeCandidate]] = {}
        for entry in entries:
            self._index.setdefault((entry.item_name, entry.function_name), []).extend(
                entry.failure_modes
            )

    def find_failure_modes(
        self, item_name: str, function_name: str
    ) -> list[FailureModeCandidate]:
        return list(self._index.get((item_name, function_name), []))
