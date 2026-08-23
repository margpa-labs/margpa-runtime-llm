"""`EvidenceGenerationObserver` unit tests (P3-F-WU-005, P3-CODEX-002
rework).

Covers what this adapter alone is responsible for: `is_active()` reflects
the live Mode and fails closed on a raising `mode_provider` (the *only*
Mode gate left here — the caller decides whether to bind at generation
start, see web/generation_observation.py); once
`observe_generation_started`/`observe_generation_terminal` are actually
called they always attempt a write (no more per-call Mode re-check);
Store construction is lazy (no `store_factory()` call until the first
real write); and non-intervention (a raising store, or an invalid
payload, never propagates)."""

from __future__ import annotations

from margpa_runtime_llm.adapters.audit_evidence.evidence_generation_observer import (
    EvidenceGenerationObserver,
)
from margpa_runtime_llm.modules.audit_evidence.application import InMemoryEvidenceStore
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventKind,
    AuditRunId,
    CanonicalAuditEvent,
    EvidenceStoreError,
    EvidenceStoreErrorCode,
)
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceReceipt, EvidenceStoreStatus


class _RaisingStore:
    def append(self, canonical: CanonicalAuditEvent) -> EvidenceReceipt:
        del canonical
        raise EvidenceStoreError(
            code=EvidenceStoreErrorCode.APPEND_FAILED,
            safe_message="simulated write failure",
        )

    def read_all(self, run_id: AuditRunId) -> tuple[CanonicalAuditEvent, ...]:
        del run_id
        return ()

    def status(self) -> EvidenceStoreStatus:
        return EvidenceStoreStatus(event_count=0, degraded=True)


class _RaisingModeProvider:
    def __call__(self) -> str:
        raise RuntimeError("simulated mode read failure")


def _observer(
    store: object, *, mode: str = "observe", store_factory_calls: list[int] | None = None
) -> EvidenceGenerationObserver:
    calls = store_factory_calls if store_factory_calls is not None else []

    def factory() -> object:
        calls.append(1)
        return store

    return EvidenceGenerationObserver(
        store_factory=factory,  # type: ignore[arg-type]
        run_id=AuditRunId(value="run-1"),
        source_component="test.generation_lifecycle",
        mode_provider=lambda: mode,
    )


def test_is_active_reflects_the_live_mode() -> None:
    assert _observer(InMemoryEvidenceStore(), mode="observe").is_active() is True
    assert _observer(InMemoryEvidenceStore(), mode="off").is_active() is False
    assert _observer(InMemoryEvidenceStore(), mode="enforce").is_active() is False
    assert _observer(InMemoryEvidenceStore(), mode="not_a_real_mode").is_active() is False


def test_is_active_fails_closed_to_false_when_mode_provider_raises() -> None:
    observer = EvidenceGenerationObserver(
        store_factory=lambda: InMemoryEvidenceStore(),
        run_id=AuditRunId(value="run-1"),
        source_component="test.generation_lifecycle",
        mode_provider=_RaisingModeProvider(),
    )
    assert observer.is_active() is False


def test_store_factory_is_not_called_until_the_first_actual_write() -> None:
    calls: list[int] = []
    observer = _observer(InMemoryEvidenceStore(), mode="off", store_factory_calls=calls)

    observer.is_active()
    assert calls == []  # is_active() alone must never construct the Store

    observer.observe_generation_started(request_id="req-1", profile_key="local.macos-arm64")
    assert calls == [1]

    observer.observe_generation_terminal(
        request_id="req-1",
        stop_reason="stop",
        token_count=1,
        latency_ms=1,
        warning_count=0,
        error_count=0,
    )
    assert calls == [1]  # constructed once, reused for the second write


def test_observe_generation_started_and_terminal_always_write_once_called() -> None:
    """The Mode gate lives in `is_active()` only now — once these methods
    are actually invoked (i.e. the caller already bound at generation
    start), they write regardless of what `mode_provider` reports, so a
    generation bound under `observe` completes its pair even if Mode
    later flips (P3-CODEX-002)."""

    store = InMemoryEvidenceStore()
    observer = _observer(store, mode="off")  # mode flipped after binding
    observer.observe_generation_started(request_id="req-1", profile_key="local.macos-arm64")
    observer.observe_generation_terminal(
        request_id="req-1",
        stop_reason="stop",
        token_count=10,
        latency_ms=5,
        warning_count=1,
        error_count=0,
    )
    events = store.read_all(AuditRunId(value="run-1"))
    assert [event.envelope.event_kind for event in events] == [
        AuditEventKind.GENERATION_STARTED,
        AuditEventKind.GENERATION_TERMINAL,
    ]
    assert all(ref.value == "req-1" for event in events for ref in event.envelope.correlation_refs)


def test_a_store_write_failure_never_propagates() -> None:
    observer = _observer(_RaisingStore(), mode="observe")
    observer.observe_generation_started(request_id="req-1", profile_key="local.macos-arm64")
    observer.observe_generation_terminal(
        request_id="req-1",
        stop_reason="stop",
        token_count=0,
        latency_ms=0,
        warning_count=0,
        error_count=0,
    )


def test_an_invalid_profile_key_never_propagates() -> None:
    store = InMemoryEvidenceStore()
    observer = _observer(store, mode="observe")
    observer.observe_generation_started(request_id="req-1", profile_key="")
    assert store.status().event_count == 0
