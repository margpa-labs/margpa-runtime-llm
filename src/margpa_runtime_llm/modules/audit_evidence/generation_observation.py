"""Non-intervening Observation Port for the existing Generation Lifecycle
(P3-F-WU-005, P3-CODEX-002 rework, architecture §1/§4.5/§10).

`GenerationObserverPort` is a fire-and-forget side channel: a caller in
`web/generation_observation.py` watches the same `ConversationEvent`
sequence the SSE response already yields and reports Start/Terminal
metadata here. An implementation MUST NOT raise, MUST NOT block the
caller beyond a small bounded local write, and a failure inside it MUST
NEVER alter, delay, or interrupt Model generation or the SSE stream
(architecture §4.5 Failure Policy, §10 Existing Runtime Compatibility).

`is_active()` is the *binding-time* gate: a caller must check it once,
before a generation starts, and only construct a
`GenerationObservationTracker` at all when it returns True. This is what
makes "Governance Hook Call 0 while off" literal — zero calls to
`observe_generation_started`/`observe_generation_terminal`, not merely
zero Evidence Store writes — and it also means a generation bound at
start (because Mode was `observe`) completes its Start/Terminal pair even
if Mode changes mid-stream, while a generation that started under `off`
is never retroactively observed (P3-CODEX-002).

`status()` is the Safe Status Surface for P3-CODEX-009: a Write/Store
failure inside `observe_generation_started`/`observe_generation_terminal`
never alters Model/SSE behavior (architecture §4.5), but it must not be
*invisible* either — it becomes visible only through this aggregate,
Process-local, reason-code-only snapshot. Never a raw exception, message,
path, or count of a specific kind of failure beyond a total tally.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class GenerationObserverStatus(ImmutableContract):
    degraded: bool = False
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )
    degraded_event_count: int = Field(default=0, ge=0)


@runtime_checkable
class GenerationObserverPort(Protocol):
    def is_active(self) -> bool: ...

    def status(self) -> GenerationObserverStatus: ...

    def observe_generation_started(self, *, request_id: str, profile_key: str) -> None: ...

    def observe_generation_terminal(
        self,
        *,
        request_id: str,
        stop_reason: str,
        token_count: int,
        latency_ms: int,
        warning_count: int,
        error_count: int,
    ) -> None: ...
