# FMEA Domain Rules

- Baseline profile: AIAG-VDA FMEA.
- Failure Mode, Failure Cause, Failure Mechanism and Failure Effect are distinct concepts.
  - Failure Mechanism is an independent domain concept.
  - MVP-0 does not require a dedicated FailureMechanismCandidate model.
  - Missing an explicit model must not cause mechanism to be mislabeled as cause/mode/effect.
  - An explicit Failure Mechanism model is deferred to a Failure-Knowledge-related MVP.
- Missing risk data remains NOT_EVALUATED/UNKNOWN.
- Do not invent proprietary S/O/D/AP rules.
- Every important candidate should retain evidence/provenance and review status.
