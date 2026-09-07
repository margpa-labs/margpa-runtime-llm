"""Evaluation Observations and Metrics (Phase 9-2, WU-B B2/B3).

`EvaluatorKind` distinguishes exactly who/what produced an
`EvaluationObservation` -- Deterministic Metric, Human Review, a Self
Judge (the same Provider Family as the Main being evaluated), or an
Independent Judge. WU-B B3's "Human未実施をLLM結果で代替しない" is
enforced structurally, not by convention: `build_human_observation()` is
the ONLY constructor that can produce `EvaluatorKind.HUMAN`, requires a
real `reviewer_id`, and always prefixes `evaluator_identity` with
`"human:"`; `build_automated_observation()` (used for Deterministic/
Self-Judge/Independent-Judge) raises a Typed error outright if a caller
passes `EvaluatorKind.HUMAN` to it -- there is no code path in this
module that can construct a `HUMAN`-kind Observation from an LLM
result."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .dataset import ObservationOutcome
from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import require_safe_identifier

_HUMAN_IDENTITY_PREFIX = "human:"


class EvaluatorKind(StrEnum):
    DETERMINISTIC = "deterministic"
    HUMAN = "human"
    SELF_JUDGE = "self_judge"
    INDEPENDENT_JUDGE = "independent_judge"


class EvaluationObservation(ImmutableContract):
    run_id: str
    case_id: str
    evaluator_kind: EvaluatorKind
    evaluator_identity: str = Field(min_length=1)
    rubric_revision: str
    outcome: ObservationOutcome
    score: float | None = None
    reason: str | None = None
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_human_identity_shape(self) -> EvaluationObservation:
        require_safe_identifier(self.run_id, field_name="run_id")
        require_safe_identifier(self.case_id, field_name="case_id")
        is_human_identity = self.evaluator_identity.startswith(_HUMAN_IDENTITY_PREFIX)
        if self.evaluator_kind is EvaluatorKind.HUMAN and not is_human_identity:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY,
                safe_message=(
                    "evaluator_kind=human requires an evaluator_identity prefixed "
                    f"{_HUMAN_IDENTITY_PREFIX!r} -- use build_human_observation()"
                ),
            )
        if self.evaluator_kind is not EvaluatorKind.HUMAN and is_human_identity:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY,
                safe_message=(
                    f"an evaluator_identity prefixed {_HUMAN_IDENTITY_PREFIX!r} requires "
                    "evaluator_kind=human"
                ),
            )
        return self


def build_human_observation(
    *,
    run_id: str,
    case_id: str,
    reviewer_id: str,
    rubric_revision: str,
    outcome: ObservationOutcome,
    score: float | None = None,
    reason: str | None = None,
    evidence_refs: tuple[str, ...] = (),
) -> EvaluationObservation:
    """The only constructor that may produce `EvaluatorKind.HUMAN` -- a
    real `reviewer_id` is required (never empty, never a placeholder), so
    an Observation this function returns is always evidence that an
    actual Human Review event happened."""

    require_safe_identifier(reviewer_id, field_name="reviewer_id")
    return EvaluationObservation(
        run_id=run_id,
        case_id=case_id,
        evaluator_kind=EvaluatorKind.HUMAN,
        evaluator_identity=f"{_HUMAN_IDENTITY_PREFIX}{reviewer_id}",
        rubric_revision=rubric_revision,
        outcome=outcome,
        score=score,
        reason=reason,
        evidence_refs=evidence_refs,
    )


def build_automated_observation(
    *,
    run_id: str,
    case_id: str,
    evaluator_kind: EvaluatorKind,
    provider_identity: str,
    rubric_revision: str,
    outcome: ObservationOutcome,
    score: float | None = None,
    reason: str | None = None,
    evidence_refs: tuple[str, ...] = (),
) -> EvaluationObservation:
    """For `DETERMINISTIC`/`SELF_JUDGE`/`INDEPENDENT_JUDGE` only --
    `evaluator_kind=HUMAN` is rejected outright (WU-B B3: never a
    substitute path to a `HUMAN`-kind Observation)."""

    if evaluator_kind is EvaluatorKind.HUMAN:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY,
            safe_message="build_automated_observation() cannot produce evaluator_kind=human",
        )
    require_safe_identifier(provider_identity, field_name="provider_identity")
    return EvaluationObservation(
        run_id=run_id,
        case_id=case_id,
        evaluator_kind=evaluator_kind,
        evaluator_identity=provider_identity,
        rubric_revision=rubric_revision,
        outcome=outcome,
        score=score,
        reason=reason,
        evidence_refs=evidence_refs,
    )


class RuntimeOutcomeState(StrEnum):
    """Project-wide P9-REQ-003 applied to Phase 9-2 Metrics specifically:
    `NOT_RUN`/`UNAVAILABLE`/`UNSUPPORTED`/`CANCELLED` are distinct,
    real states -- `is_successful_runtime_state()` below is the ONE place
    that decides which states count as a genuine success, so a
    Comparison Report (WU-F) can never accidentally treat one of these as
    a zero-scored success by reimplementing that check differently."""

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_RUN = "not_run"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"


def is_successful_runtime_state(state: RuntimeOutcomeState) -> bool:
    return state is RuntimeOutcomeState.COMPLETED


class MetricObservation(ImmutableContract):
    """WU-B B2's minimum Metric set. Every field beyond `run_id`/
    `case_id`/`runtime_state` is Optional and `None` (never `0`/`False`)
    when not meaningful for this Run's `runtime_state` -- e.g.
    `deviation_count` stays `None` for a `NOT_RUN` Metric, never `0`
    (which would misreport "ran cleanly with zero Deviations")."""

    run_id: str
    case_id: str
    runtime_state: RuntimeOutcomeState
    latency_ms: int | None = None
    call_count: int | None = None
    """R3-WU-02 (IR-P9-2-R2-04 fix): a lower bound only -- the count of
    Components CONFIRMED Called (`called=True`). Never incremented for a
    `called=None` (not_observed) Component, and never itself set to
    `None` just because some Components are unknown -- `unknown_
    component_count` below carries that fact instead, so a genuine "0
    Components confirmed called, N unknown" is never displayed identically
    to a genuine "0 Components called, 0 unknown"."""
    unknown_component_count: int | None = None
    """R3-WU-02 (IR-P9-2-R2-04 fix): how many Components this Run's own
    Evidence reports `called=None` for -- kept separate from `call_count`
    so a reader never has to guess whether Unknown was silently folded
    into a total."""
    deviation_count: int | None = None
    repair_adopted: bool | None = None
    false_positive: bool | None = None
    false_grounding: bool | None = None
    correction_acceptance: bool | None = None

    @model_validator(mode="after")
    def _validate_ids(self) -> MetricObservation:
        require_safe_identifier(self.run_id, field_name="run_id")
        require_safe_identifier(self.case_id, field_name="case_id")
        return self
