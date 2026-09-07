"""Source Authority / Provenance / Belief Revision (Phase 9-2, WU-D D3).

Design §5's Canonical Domain Candidate `BeliefRevisionObservation`:
Historical Claim, Current Source, User Correction, and Final Claim are
always four separate fields -- `classify_belief_revision()` compares
them directly rather than inferring "was this corrected" from Final
Claim text alone."""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identity import require_safe_identifier


class BeliefRevisionObservation(ImmutableContract):
    case_id: str
    historical_claim: str
    current_source: str | None = None
    user_correction: str | None = None
    final_claim: str

    @model_validator(mode="after")
    def _validate_id(self) -> BeliefRevisionObservation:
        require_safe_identifier(self.case_id, field_name="case_id")
        return self


class BeliefRevisionOutcome(StrEnum):
    CORRECTION_ACCEPTED = "correction_accepted"
    CORRECTION_IGNORED = "correction_ignored"
    OVERCORRECTED = "overcorrected"
    NO_CORRECTION_NEEDED = "no_correction_needed"


def classify_belief_revision(observation: BeliefRevisionObservation) -> BeliefRevisionOutcome:
    if observation.user_correction is None:
        return BeliefRevisionOutcome.NO_CORRECTION_NEEDED
    if observation.user_correction in observation.final_claim:
        return BeliefRevisionOutcome.CORRECTION_ACCEPTED
    if observation.historical_claim in observation.final_claim:
        return BeliefRevisionOutcome.CORRECTION_IGNORED
    return BeliefRevisionOutcome.OVERCORRECTED
