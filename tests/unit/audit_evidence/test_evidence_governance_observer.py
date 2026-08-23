"""`EvidenceGovernanceObserver` unit tests (P4-EVD-001, P4-CODEX-003
Rework, mirrors `test_evidence_generation_observer.py`'s established
pattern).

Covers what this adapter alone is responsible for: `is_active()` reflects
the live Mode (`observe` or `enforce`, unlike Generation's `observe`-only
gate) and fails closed on a raising `mode_provider`; once
`observe_point_started`/`observe_point_terminal` are actually called they
always attempt a write (no further per-call Mode re-check); Store
construction is lazy; and non-intervention (a raising store, or an
invalid payload, never propagates, only degrades `status()`)."""

from __future__ import annotations

from typing import TypedDict, cast

from margpa_runtime_llm.adapters.audit_evidence.evidence_governance_observer import (
    EvidenceGovernanceObserver,
)
from margpa_runtime_llm.modules.audit_evidence.application import InMemoryEvidenceStore
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventKind,
    AuditRunId,
    CanonicalAuditEvent,
    EvidenceStoreError,
    EvidenceStoreErrorCode,
    SafeExecutedActionRecord,
    SafeObservationRecord,
    SafeRecommendedActionRecord,
)
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceReceipt, EvidenceStoreStatus


class _TerminalKwargs(TypedDict):
    selected_descriptor_ids: tuple[str, ...]
    observations: tuple[SafeObservationRecord, ...]
    recommended_actions: tuple[SafeRecommendedActionRecord, ...]
    executed_actions: tuple[SafeExecutedActionRecord, ...]
    unavailable_reason_code: str | None
    degraded_reason_code: str | None
    binding_digest_sha512: str | None
    source_plan_id: str | None
    source_plan_digest_sha512: str | None
    capability_snapshot_digest_sha512: str | None
    authority_snapshot_digest_sha512: str | None
    policy_snapshot_digest_sha512: str | None
    budget_snapshot_digest_sha512: str | None
    action_registry_digest_sha512: str | None
    latency_ms: int
    call_count: int


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
) -> EvidenceGovernanceObserver:
    calls = store_factory_calls if store_factory_calls is not None else []

    def factory() -> object:
        calls.append(1)
        return store

    return EvidenceGovernanceObserver(
        store_factory=factory,  # type: ignore[arg-type]
        run_id=AuditRunId(value="run-1"),
        source_component="test.runtime_governance",
        mode_provider=lambda: mode,
    )


def _terminal_kwargs(**overrides: object) -> _TerminalKwargs:
    base: dict[str, object] = {
        "selected_descriptor_ids": (),
        "observations": (),
        "recommended_actions": (),
        "executed_actions": (),
        "unavailable_reason_code": None,
        "degraded_reason_code": None,
        "binding_digest_sha512": None,
        "source_plan_id": None,
        "source_plan_digest_sha512": None,
        "capability_snapshot_digest_sha512": None,
        "authority_snapshot_digest_sha512": None,
        "policy_snapshot_digest_sha512": None,
        "budget_snapshot_digest_sha512": None,
        "action_registry_digest_sha512": None,
        "latency_ms": 0,
        "call_count": 0,
    }
    base.update(overrides)
    return cast(_TerminalKwargs, base)


def test_is_active_reflects_observe_and_enforce_but_not_off() -> None:
    assert _observer(InMemoryEvidenceStore(), mode="observe").is_active() is True
    assert _observer(InMemoryEvidenceStore(), mode="enforce").is_active() is True
    assert _observer(InMemoryEvidenceStore(), mode="off").is_active() is False
    assert _observer(InMemoryEvidenceStore(), mode="not_a_real_mode").is_active() is False


def test_is_active_fails_closed_to_false_when_mode_provider_raises() -> None:
    observer = EvidenceGovernanceObserver(
        store_factory=lambda: InMemoryEvidenceStore(),
        run_id=AuditRunId(value="run-1"),
        source_component="test.runtime_governance",
        mode_provider=_RaisingModeProvider(),
    )
    assert observer.is_active() is False


def test_store_factory_is_not_called_until_the_first_actual_write() -> None:
    calls: list[int] = []
    observer = _observer(InMemoryEvidenceStore(), mode="off", store_factory_calls=calls)

    observer.is_active()
    assert calls == []  # is_active() alone must never construct the Store

    observer.observe_point_started(
        invocation_id="inv-1", point_id="main_model.post", stage="post", mode="enforce"
    )
    assert calls == [1]

    observer.observe_point_terminal(
        invocation_id="inv-1",
        point_id="main_model.post",
        stage="post",
        mode="enforce",
        execution_state="evaluated",
        severity="high",
        **_terminal_kwargs(selected_descriptor_ids=("argd.rule-1",), latency_ms=1),
    )
    assert calls == [1]  # constructed once, reused for the second write


def test_observe_point_started_and_terminal_always_write_once_called() -> None:
    store = InMemoryEvidenceStore()
    observer = _observer(store, mode="off")  # mode flipped after binding
    observer.observe_point_started(
        invocation_id="inv-1", point_id="main_model.post", stage="post", mode="enforce"
    )
    observer.observe_point_terminal(
        invocation_id="inv-1",
        point_id="main_model.post",
        stage="post",
        mode="enforce",
        execution_state="evaluated",
        severity="high",
        **_terminal_kwargs(
            selected_descriptor_ids=("argd.rule-1", "argd.rule-2", "argd.rule-3"),
            recommended_actions=(
                SafeRecommendedActionRecord(
                    action_id="reject_output", reason_descriptor_id="argd.rule-1", severity="high"
                ),
            ),
            executed_actions=(
                SafeExecutedActionRecord(
                    action_id="reject_output",
                    executed=True,
                    intervening=True,
                    not_executed_reason_code=None,
                ),
            ),
            latency_ms=2,
        ),
    )
    events = store.read_all(AuditRunId(value="run-1"))
    assert [event.envelope.event_kind for event in events] == [
        AuditEventKind.GOVERNANCE_POINT_STARTED,
        AuditEventKind.GOVERNANCE_POINT_TERMINAL,
    ]
    assert all(ref.value == "inv-1" for event in events for ref in event.envelope.correlation_refs)


def test_a_store_write_failure_never_propagates_and_marks_degraded() -> None:
    observer = _observer(_RaisingStore(), mode="observe")
    observer.observe_point_started(
        invocation_id="inv-1", point_id="main_model.pre", stage="pre", mode="observe"
    )
    observer.observe_point_terminal(
        invocation_id="inv-1",
        point_id="main_model.pre",
        stage="pre",
        mode="observe",
        execution_state="evaluated",
        severity="none",
        **_terminal_kwargs(),
    )
    status = observer.status()
    assert status.degraded is True
    assert status.degraded_event_count == 2
    assert status.degraded_reason_code == "evidence_write_failed"


def test_an_invalid_point_id_never_propagates() -> None:
    store = InMemoryEvidenceStore()
    observer = _observer(store, mode="observe")
    observer.observe_point_started(invocation_id="inv-1", point_id="", stage="pre", mode="observe")
    assert store.status().event_count == 0
    assert observer.status().degraded is True
