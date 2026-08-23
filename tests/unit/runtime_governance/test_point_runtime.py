"""Governance Point Runtime Mode routing (P4-D-WU-001, P4-PNT-001..006,
P4-MOD-001..005, ADR-4-007)."""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.application import (
    GovernancePointRuntime,
    bind,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    STAGE_POST,
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BoundGovernancePlan,
    BudgetSnapshot,
    EvaluationMethod,
    ExecutedAction,
    ExecutionDescriptor,
    ExecutionState,
    Observation,
    ObservationOutcome,
    PolicySnapshot,
    RecommendedAction,
    RuntimeCapabilitySnapshot,
    Severity,
)


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _budget() -> BudgetSnapshot:
    return BudgetSnapshot(
        max_calls_per_invocation=0,
        max_latency_ms=1000,
        max_snapshot_chars=10_000,
        allowed_generation_config_fields=(),
    )


class _RecordingEvaluator:
    def __init__(self, observations: tuple[Observation, ...]) -> None:
        self.observations = observations
        self.calls = 0

    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        snapshot: str,
        budget: BudgetSnapshot,
    ) -> tuple[Observation, ...]:
        self.calls += 1
        return self.observations


class _ExplodingEvaluator:
    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        snapshot: str,
        budget: BudgetSnapshot,
    ) -> tuple[Observation, ...]:
        raise AssertionError("evaluator must never be called in OFF mode")


def test_off_mode_never_calls_the_evaluator() -> None:
    runtime = GovernancePointRuntime(evaluator=_ExplodingEvaluator())
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="off",
        snapshot="hello",
        binding=None,
        descriptors=(),
        budget=_budget(),
    )
    assert result.execution_state is ExecutionState.NOT_EVALUATED
    assert result.observations == ()
    assert result.executed_actions == ()


def test_enforce_without_a_binding_is_unavailable_not_downgraded() -> None:
    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="enforce",
        snapshot="hello",
        binding=None,
        descriptors=(),
        budget=_budget(),
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert evaluator.calls == 0


def test_zero_descriptors_and_observe_is_inactive_no_definitions_not_evaluated() -> None:
    # P4-CODEX-004 Rework: zero bound Descriptors must short-circuit
    # *before* the Evaluator runs, converging to `inactive_no_definitions`
    # (Frozen Acceptance Matrix `Definitions 0 + observe:
    # inactive_no_definitions / output unchanged`) — not a genuine
    # `evaluated` Result with Core-only structural Deviations.
    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="",
        binding=None,
        descriptors=(),
        budget=_budget(),
    )
    assert result.execution_state is ExecutionState.INACTIVE_NO_DEFINITIONS
    assert result.unavailable_reason_code == "no_definitions"
    assert evaluator.calls == 0
    assert result.observations == ()
    assert result.executed_actions == ()


def _real_descriptor() -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="qualitative rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def test_observe_never_calls_the_action_resolver() -> None:
    deviation = Observation(
        descriptor_id="structural.empty_output",
        evaluation_method="deterministic",
        outcome=ObservationOutcome.DEVIATION,
        detail_code="empty_output",
        severity=Severity.HIGH,
        recommended_action_id="reject_output",
    )
    evaluator = _RecordingEvaluator((deviation,))
    runtime = GovernancePointRuntime(evaluator=evaluator)

    def _explode(recommended: tuple[RecommendedAction, ...]) -> tuple[ExecutedAction, ...]:
        raise AssertionError("Observe must never call the Action Resolver (ADR-4-007)")

    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="",
        binding=None,
        descriptors=(_real_descriptor(),),
        budget=_budget(),
        resolve_actions=_explode,
    )
    assert result.execution_state is ExecutionState.EVALUATED
    assert result.executed_actions == ()
    assert len(result.deviations) == 1
    assert result.severity is Severity.HIGH
    assert result.recommended_actions[0].action_id == "reject_output"


def test_enforce_with_a_valid_binding_calls_the_action_resolver() -> None:
    descriptors = (_real_descriptor(),)
    plan = bind(
        point_id=MAIN_MODEL_POST_POINT_ID,
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
        descriptors=descriptors,
        capability=_capability(),
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        policy=PolicySnapshot(policy_revision=1, profile="core"),
        budget=_budget(),
        action_registry=ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=("reject_output",)
        ),
    )
    assert plan.executable is True
    deviation = Observation(
        descriptor_id="structural.empty_output",
        evaluation_method="deterministic",
        outcome=ObservationOutcome.DEVIATION,
        detail_code="empty_output",
        severity=Severity.HIGH,
        recommended_action_id="reject_output",
    )
    evaluator = _RecordingEvaluator((deviation,))
    runtime = GovernancePointRuntime(evaluator=evaluator)

    executed = (ExecutedAction(action_id="reject_output", executed=True, intervening=True),)

    def _resolve(recommended: tuple[RecommendedAction, ...]) -> tuple[ExecutedAction, ...]:
        assert recommended[0].action_id == "reject_output"
        return executed

    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="enforce",
        snapshot="",
        binding=plan,
        descriptors=descriptors,
        budget=_budget(),
        resolve_actions=_resolve,
    )
    assert result.execution_state is ExecutionState.EVALUATED
    assert result.executed_actions == executed


def _bound_plan(
    *,
    descriptors: tuple[ExecutionDescriptor, ...],
    source_plan_id: str | None = "plan-test",
    source_plan_digest_sha512: str | None = "a" * 128,
) -> BoundGovernancePlan:
    return bind(
        point_id=MAIN_MODEL_POST_POINT_ID,
        source_plan_id=source_plan_id,
        source_plan_digest_sha512=source_plan_digest_sha512,
        descriptors=descriptors,
        capability=_capability(),
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        policy=PolicySnapshot(policy_revision=1, profile="core"),
        budget=_budget(),
        action_registry=ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=("reject_output",)
        ),
    )


def test_observe_with_a_valid_binding_carries_its_digest_but_never_calls_the_resolver() -> None:
    # P4-CODEX-011 §1.1: Observe now Binds too — a Valid Bundle Observe
    # Result must carry the real Binding/Source Plan Identity, never
    # `None`, while still never reaching the Action Resolver.
    descriptors = (_real_descriptor(),)
    plan = _bound_plan(descriptors=descriptors)
    assert plan.executable is True

    def _explode(recommended: tuple[RecommendedAction, ...]) -> tuple[ExecutedAction, ...]:
        raise AssertionError("Observe must never call the Action Resolver (ADR-4-007)")

    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="a real answer",
        binding=plan,
        descriptors=descriptors,
        budget=_budget(),
        resolve_actions=_explode,
    )
    assert result.execution_state is ExecutionState.EVALUATED
    assert result.executed_actions == ()
    assert result.binding_digest_sha512 == plan.binding_digest_sha512
    assert plan.source_plan_id == "plan-test"
    assert plan.source_plan_digest_sha512 == "a" * 128


def test_observe_with_a_non_executable_binding_short_circuits_before_the_evaluator() -> None:
    # P4-CODEX-011 §1.1 "valid definitions + stale binding + observe ->
    # rebind or explicit unavailable" — a non-executable Binding (here:
    # no real Source Plan behind non-empty Descriptors) must converge to
    # a Typed Unavailable Result, never silently fall through to the
    # Evaluator.
    descriptors = (_real_descriptor(),)
    stale_plan = _bound_plan(
        descriptors=descriptors, source_plan_id=None, source_plan_digest_sha512=None
    )
    assert stale_plan.executable is False
    assert stale_plan.unavailable_reason_code == "no_source_plan"

    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)

    def _explode(recommended: tuple[RecommendedAction, ...]) -> tuple[ExecutedAction, ...]:
        raise AssertionError("must never reach the Action Resolver")

    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="hello",
        binding=stale_plan,
        descriptors=descriptors,
        budget=_budget(),
        resolve_actions=_explode,
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "no_source_plan"
    assert result.binding_digest_sha512 == stale_plan.binding_digest_sha512
    assert evaluator.calls == 0
    assert result.executed_actions == ()


def test_observe_with_zero_descriptors_keeps_the_bindings_real_reason() -> None:
    # P4-CODEX-011 §1.1: Definitions-0 Observe keeps `inactive_no_definitions`
    # as its `execution_state`, but the Safe Reason must come from the
    # Binding itself (e.g. `provider_failure`) — never collapsed to a
    # single hardcoded `no_definitions` string regardless of the real cause.
    plan = bind(
        point_id=MAIN_MODEL_POST_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        policy=PolicySnapshot(policy_revision=1, profile="core"),
        budget=_budget(),
        action_registry=ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=("reject_output",)
        ),
        descriptor_unavailable_reason_code="provider_failure",
    )
    assert plan.executable is False
    assert plan.unavailable_reason_code == "provider_failure"

    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="hello",
        binding=plan,
        descriptors=(),
        budget=_budget(),
    )
    assert result.execution_state is ExecutionState.INACTIVE_NO_DEFINITIONS
    assert result.unavailable_reason_code == "provider_failure"
    assert evaluator.calls == 0


def test_enforce_with_a_non_executable_binding_and_descriptors_is_unavailable() -> None:
    # Regression guard: the new unconditional non-executable check must
    # still route `enforce` to UNAVAILABLE exactly as before, for the
    # non-empty-Descriptors case too (not just the zero-Descriptor case
    # already covered by `test_enforce_without_a_binding_is_unavailable_not_downgraded`).
    descriptors = (_real_descriptor(),)
    stale_plan = _bound_plan(
        descriptors=descriptors, source_plan_id=None, source_plan_digest_sha512=None
    )
    assert stale_plan.executable is False

    evaluator = _RecordingEvaluator(())
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="enforce",
        snapshot="hello",
        binding=stale_plan,
        descriptors=descriptors,
        budget=_budget(),
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "no_source_plan"
    assert evaluator.calls == 0


def test_deferred_observations_produce_no_deviation() -> None:
    descriptor = ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="qualitative rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )
    deferred = Observation(
        descriptor_id="argd.rule-1",
        evaluation_method="requires_semantic_evaluator",
        outcome=ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR,
    )
    evaluator = _RecordingEvaluator((deferred,))
    runtime = GovernancePointRuntime(evaluator=evaluator)
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="hello",
        binding=None,
        descriptors=(descriptor,),
        budget=_budget(),
    )
    assert result.deviations == ()
    assert result.severity is Severity.NONE
    assert result.observations == (deferred,)
    assert result.selected_descriptor_ids == ("argd.rule-1",)
