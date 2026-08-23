"""Bridge the existing v1/v2 `ConversationEvent` sequence to an optional
`GenerationObserverPort`, without changing what is yielded, in what
order, or how (P3-F-WU-005, architecture §10 Existing Runtime
Compatibility).

`GenerationObservationTracker` is constructed fresh per stream (never
shared across requests) and is watched-only: callers still yield/persist
every `ConversationEvent` exactly as before; `observe()` is an additional,
side-effect-only call that never raises and never returns a value the
caller could branch on.
"""

from __future__ import annotations

import time

from margpa_runtime_llm.modules.audit_evidence.generation_observation import GenerationObserverPort
from margpa_runtime_llm.modules.conversation.public import ConversationEvent, ConversationEventType

_TERMINAL_EVENT_TYPES = frozenset(
    {
        ConversationEventType.COMPLETED,
        ConversationEventType.CANCELLED,
        ConversationEventType.ERROR,
    }
)


class GenerationObservationTracker:
    def __init__(self, observer: GenerationObserverPort | None, *, profile_key: str) -> None:
        self._observer = observer
        self._profile_key = profile_key
        self._started_at: float | None = None
        self._terminal_seen = False
        self._warning_count = 0

    def observe(self, event: ConversationEvent) -> None:
        if self._observer is None:
            return
        try:
            self._observe(event)
        except Exception:
            pass

    def _observe(self, event: ConversationEvent) -> None:
        observer = self._observer
        assert observer is not None
        if event.event is ConversationEventType.WARNING:
            self._warning_count += 1
            return
        if event.event is ConversationEventType.START:
            if self._started_at is not None:
                return
            self._started_at = time.monotonic()
            observer.observe_generation_started(
                request_id=_str_field(event, "request_id"),
                profile_key=self._profile_key,
            )
            return
        if event.event not in _TERMINAL_EVENT_TYPES or self._terminal_seen:
            return
        self._terminal_seen = True
        stop_reason, token_count, error_count = _terminal_fields(event)
        latency_ms = (
            max(0, round((time.monotonic() - self._started_at) * 1000))
            if self._started_at is not None
            else 0
        )
        observer.observe_generation_terminal(
            request_id=_str_field(event, "request_id"),
            stop_reason=stop_reason,
            token_count=token_count,
            latency_ms=latency_ms,
            warning_count=self._warning_count,
            error_count=error_count,
        )


def _str_field(event: ConversationEvent, key: str) -> str:
    value = event.data.get(key)
    return value if isinstance(value, str) and value else "unknown"


def _terminal_fields(event: ConversationEvent) -> tuple[str, int, int]:
    if event.event is ConversationEventType.COMPLETED:
        finish_reason = event.data.get("finish_reason")
        stop_reason = (
            finish_reason if isinstance(finish_reason, str) and finish_reason else "unknown"
        )
        token_count = 0
        usage = event.data.get("usage")
        if isinstance(usage, dict):
            total = usage.get("total_tokens")
            if isinstance(total, int) and total >= 0:
                token_count = total
        return stop_reason, token_count, 0
    if event.event is ConversationEventType.CANCELLED:
        return "cancelled", 0, 0
    code = event.data.get("code")
    return (code if isinstance(code, str) and code else "unknown_error"), 0, 1
