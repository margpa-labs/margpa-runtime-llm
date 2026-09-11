"""Typed semantic Evidence carried by deterministic Fixture Runs.

The values here are persisted with Raw Evidence and copied into the
Comparison artifact.  ``execution_mode`` is structurally fixed to
``fixture`` so none of these deterministic oracles can be presented as a
real Production/Model observation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .belief_revision import BeliefRevisionObservation, BeliefRevisionOutcome
from .composition import GovernanceCompositionResult, RepairOrigin
from .dataset import ObservationOutcome
from .freshness import FreshnessOutcome
from .identity import require_safe_identifier
from .presentation import PresentationEvent, PresentationMode, validate_progressive_sequence
from .retrieval_case import GroundingOutcome
from .trace import ExecutionTraceProjection, TraceStage


class CaseSemanticEvidence(ImmutableContract):
    execution_mode: Literal["fixture"] = "fixture"
    case_id: str
    case_revision: str
    assistant_content: str | None = None
    answer_adopts_current_value: bool | None = None
    historical_turn_citation_digest_after_answer: str | None = None
    answer_claims_citation: bool | None = None
    belief_revision: BeliefRevisionObservation | None = None
    runtime_repair_accepted: bool | None = None
    repair_requested_by: RepairOrigin | None = None
    fixture_semantic_outcome: ObservationOutcome | None = None
    freshness_outcome: FreshnessOutcome | None = None
    grounding_outcome: GroundingOutcome | None = None
    belief_revision_outcome: BeliefRevisionOutcome | None = None
    governance_composition: GovernanceCompositionResult | None = None
    execution_trace: ExecutionTraceProjection | None = None
    presentation_events: tuple[PresentationEvent, ...] = ()

    @model_validator(mode="after")
    def _validate_identity_and_presentation(self) -> CaseSemanticEvidence:
        require_safe_identifier(self.case_id, field_name="case_id")
        require_safe_identifier(self.case_revision, field_name="case_revision")
        if self.answer_adopts_current_value is True and not self.assistant_content:
            raise ValueError("Current-Value adoption Evidence requires observed Answer content")
        if (
            self.freshness_outcome is FreshnessOutcome.CURRENT_FACT_USED
            and self.answer_adopts_current_value is not True
        ):
            raise ValueError("CURRENT_FACT_USED requires explicit Current-Value adoption Evidence")
        if self.runtime_repair_accepted is True and self.repair_requested_by is None:
            raise ValueError("an accepted Fixture Repair requires an observed requester")
        if self.execution_trace is not None and self.runtime_repair_accepted is not None:
            repair_stage = self.execution_trace.stage_record(TraceStage.REPAIR)
            if repair_stage is None or (repair_stage.call_count > 0) != bool(
                self.runtime_repair_accepted
            ):
                raise ValueError(
                    "Fixture Repair adoption must match the observed Repair-stage call count"
                )
        if (
            self.governance_composition is not None
            and self.governance_composition.repair_propagation
            is not self.repair_requested_by
        ):
            raise ValueError(
                "governance repair propagation must match the observed Fixture requester"
            )
        if self.presentation_events:
            mode = self.presentation_events[0].mode
            if any(event.mode is not mode for event in self.presentation_events):
                raise ValueError("one semantic Evidence sequence cannot mix Presentation modes")
            if mode is PresentationMode.PROGRESSIVE:
                validate_progressive_sequence(self.presentation_events)
        return self


def semantic_metric_truth(
    evidence: CaseSemanticEvidence,
) -> tuple[bool | None, bool | None, bool | None]:
    """Return false-positive, false-grounding, correction-acceptance.

    ``None`` is preserved whenever the corresponding semantic signal was
    not observed.  A negative value is produced only when the Fixture
    Evidence actually resolved that classifier to a non-failure result.
    The false-positive signal is derived from the explicitly labelled
    Fixture oracle and runtime adoption; it never masquerades as the
    separate Human Review, which remains a NOT_RUN observation.
    """

    false_positive = None
    if (
        evidence.runtime_repair_accepted is not None
        and evidence.fixture_semantic_outcome
        in (ObservationOutcome.PASS, ObservationOutcome.FAIL)
    ):
        false_positive = bool(
            evidence.runtime_repair_accepted
            and evidence.fixture_semantic_outcome is ObservationOutcome.FAIL
        )
    false_grounding = (
        evidence.grounding_outcome is GroundingOutcome.FALSE_GROUNDING
        if evidence.grounding_outcome is not None
        else None
    )
    correction_acceptance = (
        evidence.belief_revision_outcome is BeliefRevisionOutcome.CORRECTION_ACCEPTED
        if evidence.belief_revision_outcome is not None
        else None
    )
    return false_positive, false_grounding, correction_acceptance
