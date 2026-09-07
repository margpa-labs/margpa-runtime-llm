"""Strict Buffer / Progressive Presentation (Phase 9-2, WU-E E2/E3).

WU-E E2: a Strict Buffer Variant never emits a non-Final event -- an
unverified Candidate is never shown at all, only the eventual Final.
WU-E E3: a Progressive Variant's own States (`started -> retrieving ->
generating -> evaluating -> repairing -> finalized`) are strictly
one-way and never repeat; only the terminal `finalized` event may be
marked `is_verified=True` -- every earlier one is mechanically forced
`is_verified=False`, so an intermediate Chunk can never be mislabeled as
already-checked. `validate_progressive_sequence()` additionally
mechanizes "既表示Tokenを回収できるとは主張しない": once emitted, an
event's own position in this one-way sequence can never be revisited by
a later event in the same sequence."""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode


class PresentationMode(StrEnum):
    STRICT_BUFFER = "strict_buffer"
    PROGRESSIVE = "progressive"


class ProgressiveState(StrEnum):
    STARTED = "started"
    RETRIEVING = "retrieving"
    GENERATING = "generating"
    EVALUATING = "evaluating"
    REPAIRING = "repairing"
    FINALIZED = "finalized"


_PROGRESSIVE_ORDER: tuple[ProgressiveState, ...] = tuple(ProgressiveState)


class PresentationEvent(ImmutableContract):
    mode: PresentationMode
    state: ProgressiveState
    is_final: bool = False
    is_verified: bool = False

    @model_validator(mode="after")
    def _validate(self) -> PresentationEvent:
        if self.mode is PresentationMode.STRICT_BUFFER and not self.is_final:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.STRICT_BUFFER_EMITTED_NON_FINAL_EVENT,
                safe_message=(
                    "a Strict Buffer PresentationEvent must always be is_final=True -- "
                    "an unverified Candidate is never shown at all"
                ),
            )
        if self.is_final != (self.state is ProgressiveState.FINALIZED):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.PROGRESSIVE_STATE_NOT_MONOTONIC,
                safe_message="is_final must be True if and only if state is FINALIZED",
            )
        if self.is_verified and not self.is_final:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.UNVERIFIED_CONTENT_MARKED_VERIFIED,
                safe_message=(
                    f"state {self.state.value!r} is not Final but is marked is_verified=True -- "
                    "only the terminal Finalized event may ever be verified"
                ),
            )
        return self


def validate_progressive_sequence(events: tuple[PresentationEvent, ...]) -> None:
    """Fail-closed: raises unless `events` is a strictly increasing walk
    through `ProgressiveState`'s own declared order, ending in exactly
    one `is_final=True` event and nothing emitted after it."""

    last_index = -1
    for event in events:
        index = _PROGRESSIVE_ORDER.index(event.state)
        if index <= last_index:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.PROGRESSIVE_STATE_NOT_MONOTONIC,
                safe_message=(
                    f"state {event.state.value!r} does not strictly follow the prior state "
                    "in this sequence -- Progressive States never repeat or move backward"
                ),
            )
        last_index = index
    if not events or not events[-1].is_final:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.PROGRESSIVE_SEQUENCE_MISSING_FINAL,
            safe_message="a Progressive sequence must end with exactly one is_final=True event",
        )
