"""Comparison Report (Phase 9-2, WU-F F1; R1-WU-04 Hard Assert #7).

Design §11 F1: same Case Revision, Variant differences, Runtime state,
Metric, Human/LLM evaluation, Failure, and a Raw Evidence pointer, all in
one Report. Design §4.3 Truthful Comparison is enforced structurally
here too: `ComparisonRow.runtime_state` is the authoritative outcome
field, and it is never possible to attach a `MetricObservation`/
`EvaluationObservation` claiming success to a row whose `runtime_state`
is not `COMPLETED` (`_validate_no_success_claim_on_non_completed_state`)
-- a `NOT_RUN`/`FAILED`/`CANCELLED` Row can carry `None` Metrics/no
Observations, but never ones asserting a PASS outcome.

R1-WU-04 (Handoff R1 9.1 Hard Assert #7, "ComparisonがRun/Case/
Observationの不一致を拒否する"): a `ComparisonRow` also rejects an
attached `MetricObservation`/`EvaluationObservation` whose own `run_id`
does not match this Row's `run_id` -- `comparison_service.
build_comparison_report()` looks Observations up from a caller-supplied
`observations_by_run_id` mapping keyed by `run_id`, and nothing upstream
of this Contract guaranteed the Observation's own `run_id` field actually
matches the key it was filed under until this validator existed."""

from __future__ import annotations

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .dataset import ObservationOutcome
from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .evaluation import EvaluationObservation, MetricObservation, RuntimeOutcomeState
from .identity import require_safe_identifier


class ComparisonRow(ImmutableContract):
    variant_id: str
    run_id: str
    runtime_state: RuntimeOutcomeState
    metric: MetricObservation | None = None
    observations: tuple[EvaluationObservation, ...] = ()
    failure_reason: str | None = None
    raw_evidence_pointer: str

    @model_validator(mode="after")
    def _validate(self) -> ComparisonRow:
        require_safe_identifier(self.variant_id, field_name="variant_id")
        require_safe_identifier(self.run_id, field_name="run_id")
        if self.metric is not None and self.metric.run_id != self.run_id:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH,
                safe_message=(
                    f"row run_id {self.run_id!r} does not match its own metric.run_id "
                    f"{self.metric.run_id!r}"
                ),
            )
        for observation in self.observations:
            if observation.run_id != self.run_id:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH,
                    safe_message=(
                        f"row run_id {self.run_id!r} carries an Observation for a different "
                        f"run_id {observation.run_id!r}"
                    ),
                )
            if self.metric is not None and observation.case_id != self.metric.case_id:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH,
                    safe_message=(
                        f"row {self.run_id!r} carries an Observation for case_id "
                        f"{observation.case_id!r} that does not match its own metric.case_id "
                        f"{self.metric.case_id!r}"
                    ),
                )
        if self.runtime_state is not RuntimeOutcomeState.COMPLETED:
            claims_pass = any(
                observation.outcome is ObservationOutcome.PASS for observation in self.observations
            )
            if claims_pass:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
                    safe_message=(
                        f"run {self.run_id!r} has runtime_state="
                        f"{self.runtime_state.value!r} but carries a PASS Observation -- "
                        "a non-completed Run is never credited with a passing outcome"
                    ),
                )
        return self


class ComparisonReport(ImmutableContract):
    experiment_id: str
    case_revision: str
    rows: tuple[ComparisonRow, ...] = ()

    @model_validator(mode="after")
    def _validate_id(self) -> ComparisonReport:
        require_safe_identifier(self.experiment_id, field_name="experiment_id")
        require_safe_identifier(self.case_revision, field_name="case_revision")
        # R2-WU-03 (Handoff R2 SS6 last line): an Observation's own
        # `rubric_revision` is checked here, at Report level, against
        # this SAME Report's `case_revision` -- `ComparisonRow` itself
        # carries no `case_revision` field of its own (Live is singular
        # per Report, not per Row), so the Rubric-Revision half of "Run
        # ID/Case ID/Rubric Revision不一致をTyped Rejectする" belongs
        # here rather than duplicating `case_revision` onto every Row.
        for row in self.rows:
            for observation in row.observations:
                if observation.rubric_revision != self.case_revision:
                    raise ExperimentCoreError(
                        code=ExperimentCoreErrorCode.RUBRIC_REVISION_MISMATCH,
                        safe_message=(
                            f"run {row.run_id!r} carries an Observation with rubric_revision "
                            f"{observation.rubric_revision!r} that does not match this Report's "
                            f"own case_revision {self.case_revision!r}"
                        ),
                    )
        return self

    def row(self, run_id: str) -> ComparisonRow | None:
        for item in self.rows:
            if item.run_id == run_id:
                return item
        return None
