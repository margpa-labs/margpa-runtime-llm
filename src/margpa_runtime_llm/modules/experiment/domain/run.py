"""VariantRun Lifecycle (Phase 9-2, WU-A A3).

`planned -> running -> completed|failed|cancelled` is strictly one-way:
once a Run reaches any terminal state, `validate_transition` rejects
every further transition -- including a second, different terminal
publish for the same Run (WU-A A3 "同一RunのTerminal結果を二重Publish
しない"). Late-Result rejection (a stale in-flight Call finishing after
a Run was already Cancelled/completed) is enforced by the Application
layer's own monotonic generation counter (`application/experiment_
service.py`), not by this module -- this module only enforces the
State Machine shape itself.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import require_safe_identifier


class RunState(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


_TERMINAL_STATES: frozenset[RunState] = frozenset(
    {RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED}
)

_ALLOWED_TRANSITIONS: dict[RunState, frozenset[RunState]] = {
    RunState.PLANNED: frozenset({RunState.RUNNING, RunState.CANCELLED}),
    RunState.RUNNING: frozenset({RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED}),
    RunState.COMPLETED: frozenset(),
    RunState.FAILED: frozenset(),
    RunState.CANCELLED: frozenset(),
}


def is_terminal(state: RunState) -> bool:
    return state in _TERMINAL_STATES


def validate_transition(current: RunState, target: RunState) -> None:
    """Fail-closed: raises `ExperimentCoreError` for any transition not
    explicitly in `_ALLOWED_TRANSITIONS`, including any transition at all
    away from an already-terminal `current` state."""

    if is_terminal(current):
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.TERMINAL_ALREADY_PUBLISHED,
            safe_message=(
                f"run is already terminal ({current.value}); "
                f"cannot transition to {target.value}"
            ),
        )
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
            safe_message=f"{current.value} -> {target.value} is not a permitted transition",
        )


class VariantRun(ImmutableContract):
    """WU-A A1/A3: Experiment, Run, Variant, and Request are always
    distinct IDs on this Contract -- never collapsed into one field.

    R1-WU-01 (IR-P9-2-02 fix): `request_id` is required, never `None` --
    the Controller's own Probe found the Web route constructing a Run
    with `request_id=None` because the field was Optional with no real
    caller obligation to supply one. `ExperimentService.start_run()` and
    the Web route now always resolve a real `request_id` (client-supplied
    or server-generated) before a Run can exist at all.

    R2-WU-04 (IR-P9-2-R1-07 fix): `execution_mode` is Frozen Identity,
    decided and persisted at `start_run()` time -- never something a
    reader (`experiment_routes.py`) infers after the fact from whether
    Raw Evidence happens to exist yet. A `running` Production Run (no
    Raw Evidence saved yet) must keep reporting `execution_mode=
    "production"`, never fall back to looking like a Fixture Run just
    because its real Evidence has not arrived."""

    run_id: str
    experiment_id: str
    variant_id: str
    request_id: str
    execution_mode: Literal["fixture", "production"]
    state: RunState
    generation: int = Field(ge=1)
    started_at: str | None = None
    completed_at: str | None = None
    failure_reason: str | None = None

    @field_validator("run_id", "experiment_id", "variant_id", "request_id")
    @classmethod
    def _validate_ids(cls, value: str) -> str:
        return require_safe_identifier(value, field_name="VariantRun field")
