"""Execution Trace Projection / Model Call 0 (Phase 9-2, WU-E E1).

WU-E E1: "Call 0を表示文言だけで捏造しない -- 実Adapter Call Counter
または実行Evidenceで裏付ける". `TraceStageRecord` makes this mechanical
rather than a documentation promise: a genuine `call_count=0` MUST carry
an explicit, non-`NONE` `call_zero_reason` (never silently unexplained),
and a `call_count>0` record can never carry a Call-0 reason at all (so a
`call_zero_reason` field is never present merely as a decorative string
on a normal Run)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import require_safe_identifier


class TraceStage(StrEnum):
    MANUAL_URL_FETCH = "manual_url_fetch"
    MAIN = "main"
    JUDGE = "judge"
    REPAIR = "repair"
    GUARD = "guard"


class CallZeroReason(StrEnum):
    NONE = "none"
    MANUAL_URL_FAIL_CLOSED = "manual_url_fail_closed"
    STRICT_NO_HIT = "strict_no_hit"
    GUARD_INPUT_SHORT_CIRCUIT = "guard_input_short_circuit"
    NOT_APPLICABLE = "not_applicable"


class TraceDisposition(StrEnum):
    CANDIDATE_ACCEPTED = "candidate_accepted"
    REPAIR_ACCEPTED = "repair_accepted"
    SAFE_FALLBACK = "safe_fallback"
    FAILED = "failed"
    BLOCKED = "blocked"


class TraceStageRecord(ImmutableContract):
    stage: TraceStage
    call_count: int = Field(ge=0)
    call_zero_reason: CallZeroReason = CallZeroReason.NONE
    latency_ms: int | None = None

    @model_validator(mode="after")
    def _validate_zero_reason_consistency(self) -> TraceStageRecord:
        if self.call_count == 0 and self.call_zero_reason is CallZeroReason.NONE:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.CALL_ZERO_REASON_MISSING,
                safe_message=(
                    f"stage {self.stage.value!r} reports call_count=0 without an explicit "
                    "call_zero_reason -- Call 0 is never left unexplained"
                ),
            )
        if self.call_count > 0 and self.call_zero_reason is not CallZeroReason.NONE:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.CALL_ZERO_REASON_ON_NONZERO_CALL,
                safe_message=(
                    f"stage {self.stage.value!r} reports call_count={self.call_count} but also "
                    f"a call_zero_reason ({self.call_zero_reason.value!r}) -- a reason for zero "
                    "calls is never attached to a stage that genuinely made calls"
                ),
            )
        return self


class ExecutionTraceProjection(ImmutableContract):
    request_id: str
    stages: tuple[TraceStageRecord, ...] = Field(min_length=1)
    disposition: TraceDisposition

    @model_validator(mode="after")
    def _validate_id_and_unique_stages(self) -> ExecutionTraceProjection:
        require_safe_identifier(self.request_id, field_name="request_id")
        stage_keys = [item.stage for item in self.stages]
        if len(stage_keys) != len(set(stage_keys)):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                safe_message=f"trace {self.request_id!r} reports the same stage more than once",
            )
        return self

    def stage_record(self, stage: TraceStage) -> TraceStageRecord | None:
        for item in self.stages:
            if item.stage is stage:
                return item
        return None
