"""Phase 9-2 WU-E E1: Execution Trace / Model Call 0."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.trace import (
    CallZeroReason,
    ExecutionTraceProjection,
    TraceDisposition,
    TraceStage,
    TraceStageRecord,
)


def test_a_normal_stage_with_real_calls_needs_no_zero_reason() -> None:
    record = TraceStageRecord(stage=TraceStage.MAIN, call_count=1, latency_ms=500)
    assert record.call_zero_reason is CallZeroReason.NONE


def test_call_count_zero_requires_an_explicit_reason() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        TraceStageRecord(stage=TraceStage.MAIN, call_count=0)
    assert excinfo.value.code is ExperimentCoreErrorCode.CALL_ZERO_REASON_MISSING


def test_call_count_zero_with_an_explicit_reason_is_accepted() -> None:
    record = TraceStageRecord(
        stage=TraceStage.MAIN,
        call_count=0,
        call_zero_reason=CallZeroReason.MANUAL_URL_FAIL_CLOSED,
    )
    assert record.call_count == 0


def test_nonzero_call_count_cannot_carry_a_zero_reason() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        TraceStageRecord(
            stage=TraceStage.MAIN, call_count=2, call_zero_reason=CallZeroReason.STRICT_NO_HIT
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.CALL_ZERO_REASON_ON_NONZERO_CALL


def test_manual_url_fail_closed_trace_shape() -> None:
    trace = ExecutionTraceProjection(
        request_id="req-1",
        stages=(
            TraceStageRecord(
                stage=TraceStage.MANUAL_URL_FETCH,
                call_count=0,
                call_zero_reason=CallZeroReason.MANUAL_URL_FAIL_CLOSED,
            ),
            TraceStageRecord(
                stage=TraceStage.MAIN, call_count=0, call_zero_reason=CallZeroReason.NOT_APPLICABLE
            ),
        ),
        disposition=TraceDisposition.FAILED,
    )
    fetch_record = trace.stage_record(TraceStage.MANUAL_URL_FETCH)
    assert fetch_record is not None
    assert fetch_record.call_zero_reason is CallZeroReason.MANUAL_URL_FAIL_CLOSED
    assert trace.stage_record(TraceStage.JUDGE) is None


def test_guard_input_short_circuit_gives_judge_a_call_count_of_zero_with_reason() -> None:
    trace = ExecutionTraceProjection(
        request_id="req-2",
        stages=(
            TraceStageRecord(stage=TraceStage.GUARD, call_count=1),
            TraceStageRecord(
                stage=TraceStage.JUDGE,
                call_count=0,
                call_zero_reason=CallZeroReason.GUARD_INPUT_SHORT_CIRCUIT,
            ),
        ),
        disposition=TraceDisposition.BLOCKED,
    )
    judge_record = trace.stage_record(TraceStage.JUDGE)
    assert judge_record is not None
    assert judge_record.call_zero_reason is CallZeroReason.GUARD_INPUT_SHORT_CIRCUIT


def test_strict_no_hit_gives_main_a_call_count_of_zero_with_reason() -> None:
    trace = ExecutionTraceProjection(
        request_id="req-3",
        stages=(
            TraceStageRecord(
                stage=TraceStage.MAIN, call_count=0, call_zero_reason=CallZeroReason.STRICT_NO_HIT
            ),
        ),
        disposition=TraceDisposition.SAFE_FALLBACK,
    )
    assert trace.stage_record(TraceStage.MAIN).call_zero_reason is CallZeroReason.STRICT_NO_HIT  # type: ignore[union-attr]


def test_trace_rejects_duplicate_stage_entries() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        ExecutionTraceProjection(
            request_id="req-4",
            stages=(
                TraceStageRecord(stage=TraceStage.MAIN, call_count=1),
                TraceStageRecord(stage=TraceStage.MAIN, call_count=2),
            ),
            disposition=TraceDisposition.CANDIDATE_ACCEPTED,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER
