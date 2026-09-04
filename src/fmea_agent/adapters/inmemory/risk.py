"""MVP-0 risk strategies: never invent S/O/D/AP values."""

from fmea_agent.domain.fmea import (
    AnalysisContext,
    FailureModeCandidate,
    FMEAItem,
    RiskAssessment,
    RiskStatus,
)


class NoOpRiskStrategy:
    """Declares NOT_EVALUATED for every candidate; no risk rules are applied."""

    def evaluate(
        self,
        context: AnalysisContext,
        item: FMEAItem,
        failure_mode: FailureModeCandidate,
    ) -> RiskAssessment:
        return RiskAssessment(status=RiskStatus.NOT_EVALUATED, strategy="noop")
