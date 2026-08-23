"""`build_main_model_governance_hooks`: Mode routing, zero Model Call
guarantee, Observe non-intervention, and Fail-closed (not Fail-open)
Enforce failure handling (P4-MOD-002..005, ADR-4-007, P4-ACC-006/008/009,
P4-CODEX-005 Rework)."""

from __future__ import annotations

from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
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
    MAIN_MODEL_POST_POINT_ID,
    MAIN_MODEL_PRE_POINT_ID,
    EvaluationMethod,
    ExecutionDescriptor,
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


def _request() -> GenerationRequest:
    return GenerationRequest(
        request_id="req-1",
        model_key="main.qwen3-4b-q4-k-m",
        messages=(ChatMessage(role=MessageRole.USER, content="hello"),),
        parameters=GenerationParameters(),
    )


def test_off_mode_never_binds_or_evaluates() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    baseline_cache_size = composition.plan_cache.size()
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "off"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")
    assert composition.plan_cache.size() == baseline_cache_size


class _ExplodingObserver:
    """Any call at all is a Test failure — Readable OFF must be Evidence
    Call 0 (P4-MOD-002/P4-CODEX-011 Required Test 6), never merely
    "zero writes" after still consulting the Observer."""

    def is_active(self) -> bool:
        raise AssertionError("Observer must never be consulted in OFF mode")

    def status(self) -> GovernanceObserverStatus:  # pragma: no cover - never reached
        raise AssertionError("Observer must never be consulted in OFF mode")

    def observe_point_started(self, **kwargs: object) -> None:  # pragma: no cover
        raise AssertionError("Observer must never be consulted in OFF mode")

    def observe_point_terminal(self, **kwargs: object) -> None:  # pragma: no cover
        raise AssertionError("Observer must never be consulted in OFF mode")


def test_off_mode_never_consults_the_observer_either() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition,
        mode_provider=lambda: "off",
        governance_observer=_ExplodingObserver(),
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")


def test_observe_never_intervenes_even_with_a_real_deviation() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "observe"
    )
    # Empty output is a real, high-severity structural deviation — but
    # Observe must never act on it (ADR-4-007).
    assert post_hook("") == (False, "")
    assert pre_hook(_request()) == (False, "")


def test_observe_with_zero_definitions_is_inactive_not_evaluated() -> None:
    composition = RuntimeGovernanceComposition(capability=_capability())
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "observe"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")


def test_observe_binds_and_carries_binding_and_source_plan_identity() -> None:
    # P4-CODEX-011 §1.1: Observe now Binds too — a Valid Bundle Observe
    # Result/Last-Result must carry the real Binding/Source Plan Identity
    # instead of `None`, while `executed_actions` stays empty (never
    # reaches the Action Resolver).
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "observe"
    )
    expected_binding = composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    assert expected_binding.executable is True

    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")  # a real deviation, but never intervenes

    pre_result = composition.last_result_for(point_id=MAIN_MODEL_PRE_POINT_ID)
    post_result = composition.last_result_for(point_id=MAIN_MODEL_POST_POINT_ID)
    assert pre_result is not None
    assert post_result is not None
    assert pre_result.binding_digest_sha512 is not None
    assert post_result.binding_digest_sha512 == expected_binding.binding_digest_sha512
    assert post_result.executed_actions == ()


def test_observe_with_a_non_executable_binding_is_unavailable_and_never_evaluates() -> None:
    # P4-CODEX-011 §1.1 "valid definitions + stale binding + observe ->
    # rebind or explicit unavailable" — Descriptors exist but no real
    # Source Plan Identity was ever established, so the Binding is
    # non-executable; Observe must converge to a Typed Unavailable
    # Result and never intervene either way.
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "observe"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")

    post_result = composition.last_result_for(point_id=MAIN_MODEL_POST_POINT_ID)
    assert post_result is not None
    assert post_result.unavailable_reason_code == "no_source_plan"
    assert post_result.executed_actions == ()


def test_enforce_stops_before_generation_on_oversized_request() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    composition.budget = composition.budget.model_copy(update={"max_snapshot_chars": 1})
    pre_hook, _ = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    should_stop, reason = pre_hook(_request())
    assert should_stop is True
    assert reason == "governance_stop_before_generation"


def test_enforce_rejects_empty_output() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    _, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    should_reject, reason = post_hook("")
    assert should_reject is True
    assert reason == "governance_reject_output"


def test_enforce_allows_a_normal_request_and_output() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("a perfectly normal answer") == (False, "")


def test_enforce_with_zero_definitions_is_unavailable_and_never_stops_or_rejects() -> None:
    # P4-CODEX-004 Rework: Definitions-0 + enforce must be `unsupported`
    # with zero mutation — the hook must not intervene just because
    # Enforce was requested; there is nothing bound to Enforce.
    composition = RuntimeGovernanceComposition(capability=_capability())
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")


def test_unknown_mode_string_fails_closed_stopping_and_rejecting() -> None:
    # P4-CODEX-005 Rework: an Unreadable Mode must never be silently
    # treated as `off` — it fails Closed (Stop/Reject), not Open.
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "not_a_real_mode"
    )
    assert pre_hook(_request()) == (True, "governance_mode_unavailable")
    assert post_hook("") == (True, "governance_mode_unavailable")


def test_mode_provider_exception_fails_closed_stopping_and_rejecting() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(), descriptors=(_descriptor(),)
    )

    def _explode() -> str:
        raise RuntimeError("boom")

    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=_explode
    )
    assert pre_hook(_request()) == (True, "governance_mode_unavailable")
    assert post_hook("") == (True, "governance_mode_unavailable")


def test_off_mode_still_wins_over_an_otherwise_failing_composition() -> None:
    # `off` is the one Mode that must stay Call-0 even when nothing else
    # about the Composition would succeed — Fail-closed applies to
    # Enforce/Unknown Mode, never retroactively to a genuine, readable
    # `off` (P4-MOD-002 is absolute).
    composition = RuntimeGovernanceComposition(capability=_capability())
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "off"
    )
    assert pre_hook(_request()) == (False, "")
    assert post_hook("") == (False, "")
