"""Phase 9-2 WU-E E2/E3: Strict Buffer / Progressive Presentation."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.presentation import (
    PresentationEvent,
    PresentationMode,
    ProgressiveState,
    validate_progressive_sequence,
)


def test_strict_buffer_final_event_is_accepted() -> None:
    event = PresentationEvent(
        mode=PresentationMode.STRICT_BUFFER,
        state=ProgressiveState.FINALIZED,
        is_final=True,
        is_verified=True,
    )
    assert event.is_verified is True


def test_strict_buffer_rejects_any_non_final_event() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        PresentationEvent(
            mode=PresentationMode.STRICT_BUFFER, state=ProgressiveState.GENERATING, is_final=False
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.STRICT_BUFFER_EMITTED_NON_FINAL_EVENT


def test_is_final_must_match_finalized_state_exactly() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        PresentationEvent(
            mode=PresentationMode.PROGRESSIVE, state=ProgressiveState.GENERATING, is_final=True
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.PROGRESSIVE_STATE_NOT_MONOTONIC


def test_intermediate_progressive_content_can_never_be_marked_verified() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        PresentationEvent(
            mode=PresentationMode.PROGRESSIVE,
            state=ProgressiveState.GENERATING,
            is_final=False,
            is_verified=True,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.UNVERIFIED_CONTENT_MARKED_VERIFIED


def _event(state: ProgressiveState) -> PresentationEvent:
    return PresentationEvent(
        mode=PresentationMode.PROGRESSIVE,
        state=state,
        is_final=state is ProgressiveState.FINALIZED,
        is_verified=state is ProgressiveState.FINALIZED,
    )


def test_a_full_forward_progressive_sequence_is_valid() -> None:
    sequence = (
        _event(ProgressiveState.STARTED),
        _event(ProgressiveState.RETRIEVING),
        _event(ProgressiveState.GENERATING),
        _event(ProgressiveState.EVALUATING),
        _event(ProgressiveState.REPAIRING),
        _event(ProgressiveState.FINALIZED),
    )
    validate_progressive_sequence(sequence)  # must not raise


def test_a_sequence_may_skip_states_but_never_go_backward() -> None:
    sequence = (_event(ProgressiveState.STARTED), _event(ProgressiveState.FINALIZED))
    validate_progressive_sequence(sequence)  # must not raise


def test_a_repeated_state_is_rejected() -> None:
    sequence = (
        _event(ProgressiveState.GENERATING),
        _event(ProgressiveState.GENERATING),
        _event(ProgressiveState.FINALIZED),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_progressive_sequence(sequence)
    assert excinfo.value.code is ExperimentCoreErrorCode.PROGRESSIVE_STATE_NOT_MONOTONIC


def test_a_backward_state_is_rejected() -> None:
    sequence = (
        _event(ProgressiveState.GENERATING),
        _event(ProgressiveState.RETRIEVING),
        _event(ProgressiveState.FINALIZED),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_progressive_sequence(sequence)
    assert excinfo.value.code is ExperimentCoreErrorCode.PROGRESSIVE_STATE_NOT_MONOTONIC


def test_a_sequence_missing_a_final_event_is_rejected() -> None:
    sequence = (_event(ProgressiveState.STARTED), _event(ProgressiveState.GENERATING))
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_progressive_sequence(sequence)
    assert excinfo.value.code is ExperimentCoreErrorCode.PROGRESSIVE_SEQUENCE_MISSING_FINAL


def test_an_empty_sequence_is_rejected() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_progressive_sequence(())
    assert excinfo.value.code is ExperimentCoreErrorCode.PROGRESSIVE_SEQUENCE_MISSING_FINAL
