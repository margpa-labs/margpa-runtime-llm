"""Phase 9-2 WU-A A3: VariantRun one-way State Machine."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.run import (
    RunState,
    VariantRun,
    is_terminal,
    validate_transition,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (RunState.PLANNED, RunState.RUNNING),
        (RunState.PLANNED, RunState.CANCELLED),
        (RunState.RUNNING, RunState.COMPLETED),
        (RunState.RUNNING, RunState.FAILED),
        (RunState.RUNNING, RunState.CANCELLED),
    ],
)
def test_validate_transition_permits_every_forward_edge(
    current: RunState, target: RunState
) -> None:
    validate_transition(current, target)  # must not raise


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (RunState.PLANNED, RunState.COMPLETED),
        (RunState.PLANNED, RunState.FAILED),
        (RunState.RUNNING, RunState.PLANNED),
    ],
)
def test_validate_transition_rejects_non_adjacent_edges(
    current: RunState, target: RunState
) -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_transition(current, target)
    assert excinfo.value.code is ExperimentCoreErrorCode.INVALID_STATE_TRANSITION


@pytest.mark.parametrize(
    "terminal_state", [RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED]
)
@pytest.mark.parametrize("target", [RunState.RUNNING, RunState.COMPLETED, RunState.FAILED])
def test_validate_transition_rejects_any_move_away_from_terminal(
    terminal_state: RunState, target: RunState
) -> None:
    """WU-A A3: 'a Run's Terminal result is never double-published' --
    this includes a *different* terminal outcome overwriting a prior one."""
    with pytest.raises(ExperimentCoreError) as excinfo:
        validate_transition(terminal_state, target)
    assert excinfo.value.code is ExperimentCoreErrorCode.TERMINAL_ALREADY_PUBLISHED


def test_is_terminal_reports_exactly_the_three_terminal_states() -> None:
    assert not is_terminal(RunState.PLANNED)
    assert not is_terminal(RunState.RUNNING)
    assert is_terminal(RunState.COMPLETED)
    assert is_terminal(RunState.FAILED)
    assert is_terminal(RunState.CANCELLED)


def test_variant_run_rejects_empty_or_unsafe_ids() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        VariantRun(
            run_id="",
            experiment_id="exp-1",
            variant_id="variant-a",
            request_id="req-1",
            execution_mode="fixture",
            state=RunState.PLANNED,
            generation=1,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.EMPTY_IDENTIFIER
