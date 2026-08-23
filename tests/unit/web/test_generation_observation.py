"""`GenerationObservationTracker` unit tests (P3-F-WU-005).

Covers the field-extraction and once-only guarantees the tracker alone is
responsible for: Terminal called at most once, a Start seen twice never
double-fires, and the tracker itself never lets an observer failure
propagate.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.audit_evidence.generation_observation import (
    GenerationObserverStatus,
)
from margpa_runtime_llm.modules.conversation.public import ConversationEvent, ConversationEventType
from margpa_runtime_llm.web.generation_observation import GenerationObservationTracker


class _RecordingObserver:
    def __init__(self) -> None:
        self.started_calls: list[dict[str, object]] = []
        self.terminal_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def status(self) -> GenerationObserverStatus:
        return GenerationObserverStatus()

    def observe_generation_started(self, *, request_id: str, profile_key: str) -> None:
        self.started_calls.append({"request_id": request_id, "profile_key": profile_key})

    def observe_generation_terminal(
        self,
        *,
        request_id: str,
        stop_reason: str,
        token_count: int,
        latency_ms: int,
        warning_count: int,
        error_count: int,
    ) -> None:
        self.terminal_calls.append(
            {
                "request_id": request_id,
                "stop_reason": stop_reason,
                "token_count": token_count,
                "latency_ms": latency_ms,
                "warning_count": warning_count,
                "error_count": error_count,
            }
        )


class _RaisingObserver:
    def is_active(self) -> bool:
        return True

    def status(self) -> GenerationObserverStatus:
        return GenerationObserverStatus()

    def observe_generation_started(self, *, request_id: str, profile_key: str) -> None:
        raise RuntimeError("boom")

    def observe_generation_terminal(self, **kwargs: object) -> None:
        raise RuntimeError("boom")


def _start_event(request_id: str = "req-1") -> ConversationEvent:
    return ConversationEvent(
        event=ConversationEventType.START,
        data={"request_id": request_id, "state": "generating"},
    )


def _completed_event(*, finish_reason: str = "stop", total_tokens: int = 42) -> ConversationEvent:
    return ConversationEvent(
        event=ConversationEventType.COMPLETED,
        data={
            "request_id": "req-1",
            "finish_reason": finish_reason,
            "usage": {"total_tokens": total_tokens},
        },
    )


def test_observer_none_is_a_pure_no_op() -> None:
    tracker = GenerationObservationTracker(None, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(_completed_event())


def test_start_fires_observe_generation_started_exactly_once_even_if_seen_twice() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(_start_event())
    assert observer.started_calls == [{"request_id": "req-1", "profile_key": "local.macos-arm64"}]


def test_completed_reports_finish_reason_and_token_count_from_usage() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(_completed_event(finish_reason="length", total_tokens=99))
    assert len(observer.terminal_calls) == 1
    call = observer.terminal_calls[0]
    assert call["stop_reason"] == "length"
    assert call["token_count"] == 99
    assert call["error_count"] == 0


def test_cancelled_reports_cancelled_stop_reason_and_zero_errors() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(
        ConversationEvent(
            event=ConversationEventType.CANCELLED,
            data={"request_id": "req-1", "state": "cancelled"},
        )
    )
    call = observer.terminal_calls[0]
    assert call["stop_reason"] == "cancelled"
    assert call["error_count"] == 0


def test_error_reports_the_error_code_and_one_error() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(
        ConversationEvent(
            event=ConversationEventType.ERROR,
            data={
                "request_id": "req-1",
                "code": "generation_failed",
                "message": "x",
                "retryable": False,
            },
        )
    )
    call = observer.terminal_calls[0]
    assert call["stop_reason"] == "generation_failed"
    assert call["error_count"] == 1


def test_warnings_are_counted_and_included_in_the_terminal_call() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(
        ConversationEvent(
            event=ConversationEventType.WARNING,
            data={"request_id": "req-1", "code": "w", "message": "m"},
        )
    )
    tracker.observe(
        ConversationEvent(
            event=ConversationEventType.WARNING,
            data={"request_id": "req-1", "code": "w2", "message": "m2"},
        )
    )
    tracker.observe(_completed_event())
    assert observer.terminal_calls[0]["warning_count"] == 2


def test_terminal_fires_at_most_once_even_if_a_second_terminal_arrives() -> None:
    observer = _RecordingObserver()
    tracker = GenerationObservationTracker(observer, profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(_completed_event())
    tracker.observe(
        ConversationEvent(
            event=ConversationEventType.CANCELLED,
            data={"request_id": "req-1", "state": "cancelled"},
        )
    )
    assert len(observer.terminal_calls) == 1


def test_a_raising_observer_never_propagates_out_of_observe() -> None:
    tracker = GenerationObservationTracker(_RaisingObserver(), profile_key="local.macos-arm64")
    tracker.observe(_start_event())
    tracker.observe(_completed_event())
