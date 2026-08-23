"""P4-CODEX-007/011 Rework: `mode_unavailable` Last Result/Evidence
visibility, and Observer-interaction Degraded Status tracking.

Both slices were previously silent gaps: a raising/unreadable Mode
Provider always Fail-closed the Stop/Reject decision correctly, but left
`composition.last_result_for(...)` and Evidence completely untouched;
and a raising `GovernanceObserverPort.is_active()`/`observe_*` call was
only logged, never reflected in any Process-local Degraded Status the
Composition itself exposes.

`test_mode_unavailable_records_a_degraded_last_result_and_evidence`
below uses an independent Fake Observer for a focused, controlled check
of the Last Result/Evidence-shape behavior alone.
`test_mode_failure_evidence_survives_the_actual_shared_mode_provider_wiring`
is the Closure Evidence for P4-CODEX-011 §1.2 specifically: it uses the
real `EvidenceGovernanceObserver` with the *same* raising `mode_provider`
Callable the real Composition Root actually shares between the Hook and
the Observer — the scenario the independent Fake could not represent."""

from __future__ import annotations

from margpa_runtime_llm.adapters.audit_evidence.evidence_governance_observer import (
    EvidenceGovernanceObserver,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
)
from margpa_runtime_llm.modules.audit_evidence.application import InMemoryEvidenceStore
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventKind,
    AuditRunId,
    SafeExecutedActionRecord,
    SafeObservationRecord,
    SafeRecommendedActionRecord,
)
from margpa_runtime_llm.modules.audit_evidence.governance_observation import (
    GovernanceObserverStatus,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.runtime_governance.domain import (
    EvaluationMethod,
    ExecutionDescriptor,
    ExecutionState,
    RuntimeCapabilitySnapshot,
)


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor() -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


class _RecordingObserver:
    """A real (non-raising) Observer whose own `mode_provider` is
    independent of the Hook's — realistic when the Composition Root
    wires each from the same underlying Mode Controller, but exercised
    here as two distinct Callables so `is_active()` can succeed even
    while the Hook's own Mode read fails."""

    def __init__(self) -> None:
        self.started_calls: list[dict[str, object]] = []
        self.terminal_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def status(self) -> GovernanceObserverStatus:
        return GovernanceObserverStatus()

    def observe_point_started(
        self, *, invocation_id: str, point_id: str, stage: str, mode: str
    ) -> None:
        self.started_calls.append(
            {"invocation_id": invocation_id, "point_id": point_id, "stage": stage, "mode": mode}
        )

    def observe_point_terminal(
        self,
        *,
        invocation_id: str,
        point_id: str,
        stage: str,
        mode: str,
        execution_state: str,
        severity: str,
        selected_descriptor_ids: tuple[str, ...],
        observations: tuple[SafeObservationRecord, ...],
        recommended_actions: tuple[SafeRecommendedActionRecord, ...],
        executed_actions: tuple[SafeExecutedActionRecord, ...],
        unavailable_reason_code: str | None,
        degraded_reason_code: str | None,
        binding_digest_sha512: str | None,
        source_plan_id: str | None,
        source_plan_digest_sha512: str | None,
        capability_snapshot_digest_sha512: str | None,
        authority_snapshot_digest_sha512: str | None,
        policy_snapshot_digest_sha512: str | None,
        budget_snapshot_digest_sha512: str | None,
        action_registry_digest_sha512: str | None,
        latency_ms: int,
        call_count: int,
    ) -> None:
        self.terminal_calls.append(
            {
                "invocation_id": invocation_id,
                "point_id": point_id,
                "stage": stage,
                "mode": mode,
                "execution_state": execution_state,
                "severity": severity,
                "degraded_reason_code": degraded_reason_code,
            }
        )


class _RaisingIsActiveObserver:
    def is_active(self) -> bool:
        raise RuntimeError("boom")

    def status(self) -> GovernanceObserverStatus:
        return GovernanceObserverStatus()

    def observe_point_started(
        self, *, invocation_id: str, point_id: str, stage: str, mode: str
    ) -> None:  # pragma: no cover - never reached, is_active() gates this
        raise AssertionError("must not be called when is_active() itself raised")

    def observe_point_terminal(self, **kwargs: object) -> None:  # pragma: no cover
        raise AssertionError("must not be called when is_active() itself raised")


def test_mode_unavailable_records_a_degraded_last_result_and_evidence() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    observer = _RecordingObserver()

    def _explode() -> str:
        raise RuntimeError("mode provider is down")

    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=_explode, governance_observer=observer
    )

    should_stop, reason = pre_hook(_request())
    assert should_stop is True
    assert reason == "governance_mode_unavailable"

    result = composition.last_result_for(point_id="main_model.pre")
    assert result is not None
    assert result.execution_state is ExecutionState.DEGRADED
    assert result.degraded_reason_code == "mode_provider_unavailable"

    assert len(observer.terminal_calls) == 1
    terminal = observer.terminal_calls[0]
    assert terminal["execution_state"] == "degraded"
    assert terminal["degraded_reason_code"] == "mode_provider_unavailable"
    assert terminal["point_id"] == "main_model.pre"

    should_reject, post_reason = post_hook("")
    assert should_reject is True
    assert post_reason == "governance_mode_unavailable"
    post_result = composition.last_result_for(point_id="main_model.post")
    assert post_result is not None
    assert post_result.execution_state is ExecutionState.DEGRADED
    assert len(observer.terminal_calls) == 2


def test_mode_failure_evidence_survives_the_actual_shared_mode_provider_wiring() -> None:
    # P4-CODEX-011 §1.2: the previous Test used an independent Fake
    # Observer whose `is_active()` always returned `True`, which does not
    # represent the real Composition Root — there, the Hook's
    # `mode_provider` and the real `EvidenceGovernanceObserver`'s own
    # `mode_provider` are the *same* Callable. This Test uses the real
    # `EvidenceGovernanceObserver` (not a Fake) and passes the identical
    # raising Callable to both, proving the Degraded Terminal Event still
    # gets written even though `is_active()` would itself fail closed to
    # `False` if it were consulted first.
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    store = InMemoryEvidenceStore()
    run_id = AuditRunId(value="run-shared-provider")

    def _shared_raising_mode_provider() -> str:
        raise RuntimeError("mode provider is down")

    observer = EvidenceGovernanceObserver(
        store_factory=lambda: store,
        run_id=run_id,
        source_component="test.runtime_governance",
        mode_provider=_shared_raising_mode_provider,
    )
    assert observer.is_active() is False  # confirms the shared Provider really fails closed

    pre_hook, _ = build_main_model_governance_hooks(
        composition=composition,
        mode_provider=_shared_raising_mode_provider,
        governance_observer=observer,
    )

    should_stop, reason = pre_hook(_request())
    assert should_stop is True
    assert reason == "governance_mode_unavailable"

    events = store.read_all(run_id)
    terminal_events = [
        e for e in events if e.envelope.event_kind is AuditEventKind.GOVERNANCE_POINT_TERMINAL
    ]
    assert len(terminal_events) == 1
    payload = terminal_events[0].envelope.safe_payload
    assert payload.execution_state == "degraded"  # type: ignore[union-attr]
    assert payload.degraded_reason_code == "mode_provider_unavailable"  # type: ignore[union-attr]


def test_observer_interaction_degraded_is_set_when_is_active_raises() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    assert composition.observer_interaction_degraded() is False
    pre_hook, _ = build_main_model_governance_hooks(
        composition=composition,
        mode_provider=lambda: "observe",
        governance_observer=_RaisingIsActiveObserver(),
    )
    assert pre_hook(_request()) == (False, "")
    assert composition.observer_interaction_degraded() is True


def _request() -> GenerationRequest:
    return GenerationRequest(
        request_id="req-1",
        model_key="main.qwen3-4b-q4-k-m",
        messages=(ChatMessage(role=MessageRole.USER, content="hello"),),
        parameters=GenerationParameters(),
    )
