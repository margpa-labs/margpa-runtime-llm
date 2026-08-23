"""Action Resolver routing order (architecture §4 ENFORCE, P4-E-WU-001/003,
P4-ACT-001..005, ADR-4-005/4-008, P4-CODEX-006 Rework).

Routing order under test: conflict resolution -> mode -> authority/policy
-> capability -> budget -> registered adapter validation -> execute or
explicit not_executed. `capability`/`policy`/`budget` are re-verified as
one Binding-staleness check (the live Snapshot no longer matching what
was embedded in the Binding at Bind time)."""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.application import bind, resolve_actions
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    MAIN_MODEL_PRE_POINT_ID,
    STAGE_POST,
    STAGE_PRE,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BoundGovernancePlan,
    BudgetSnapshot,
    EvaluationMethod,
    ExecutedAction,
    ExecutionDescriptor,
    NotExecutedReason,
    PolicySnapshot,
    RecommendedAction,
    RuntimeCapabilitySnapshot,
    Severity,
)
from margpa_runtime_llm.modules.runtime_governance.ports import ActionAdapterPort


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _policy() -> PolicySnapshot:
    return PolicySnapshot(policy_revision=1, profile="core")


def _budget() -> BudgetSnapshot:
    return BudgetSnapshot(
        max_calls_per_invocation=0,
        max_latency_ms=1000,
        max_snapshot_chars=10_000,
        allowed_generation_config_fields=(),
    )


def _descriptor(descriptor_id: str = "argd.rule-1") -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id=descriptor_id,
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def _binding(
    *,
    granted: tuple[str, ...] = (),
    registered: tuple[str, ...] = (),
    point_id: str = MAIN_MODEL_POST_POINT_ID,
    capability: RuntimeCapabilitySnapshot | None = None,
    authority: AuthoritySnapshot | None = None,
    authority_revision: int = 1,
    policy: PolicySnapshot | None = None,
    budget: BudgetSnapshot | None = None,
    action_registry: ActionRegistrySnapshot | None = None,
) -> BoundGovernancePlan:
    return bind(
        point_id=point_id,
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
        descriptors=(_descriptor(),),
        capability=capability or _capability(),
        authority=authority
        or AuthoritySnapshot(authority_revision=authority_revision, granted_action_ids=granted),
        policy=policy or _policy(),
        budget=budget or _budget(),
        action_registry=action_registry
        or ActionRegistrySnapshot(registry_revision=1, registered_action_ids=registered),
    )


class _RecordingAdapter:
    def __init__(self, *, intervening_by_action: dict[str, bool] | None = None) -> None:
        self.calls: list[tuple[str, str, str]] = []
        self._intervening_by_action = intervening_by_action or {}

    def execute(self, *, action_id: str, point_id: str, stage: str) -> ExecutedAction:
        self.calls.append((action_id, point_id, stage))
        return ExecutedAction(
            action_id=action_id,
            executed=True,
            intervening=self._intervening_by_action.get(action_id, False),
        )


def _resolve(
    *,
    recommended_actions: tuple[RecommendedAction, ...],
    point_id: str = MAIN_MODEL_POST_POINT_ID,
    stage: str = STAGE_POST,
    mode: str = "enforce",
    binding: BoundGovernancePlan,
    authority: AuthoritySnapshot,
    registry: dict[str, ActionRegistryEntry],
    adapters: dict[str, ActionAdapterPort],
    capability: RuntimeCapabilitySnapshot | None = None,
    policy: PolicySnapshot | None = None,
    budget: BudgetSnapshot | None = None,
    action_registry: ActionRegistrySnapshot | None = None,
) -> tuple[ExecutedAction, ...]:
    return resolve_actions(
        recommended_actions=recommended_actions,
        point_id=point_id,
        stage=stage,
        mode=mode,
        binding=binding,
        capability=capability or _capability(),
        authority=authority,
        policy=policy or _policy(),
        budget=budget or _budget(),
        action_registry=action_registry
        or ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=tuple(registry.keys())
        ),
        registry=registry,
        adapters=adapters,
    )


def test_mode_not_enforce_never_executes_and_never_calls_the_adapter() -> None:
    binding = _binding(granted=("reject_output",), registered=("reject_output",))
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        mode="observe",
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert len(results) == 1
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.MODE_NOT_ENFORCE.value
    assert adapter.calls == []


def test_unavailable_binding_never_executes_and_never_calls_the_adapter() -> None:
    binding = _binding()  # empty registry/authority -> not executable
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert len(results) == 1
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.BINDING_UNAVAILABLE.value
    assert adapter.calls == []


def test_missing_authority_is_not_executed() -> None:
    binding = _binding(granted=("reject_output",), registered=("warn",))
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="warn", severity=Severity.LOW),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "warn": ActionRegistryEntry(
                action_id="warn",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"warn": adapter},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.AUTHORITY_MISSING.value
    assert adapter.calls == []


def test_action_not_allowed_at_this_point_or_stage_is_not_executed() -> None:
    binding = _binding(
        granted=("reject_output",),
        registered=("reject_output",),
        point_id=MAIN_MODEL_PRE_POINT_ID,
    )
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id=MAIN_MODEL_PRE_POINT_ID,
        stage=STAGE_PRE,
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert (
        results[0].not_executed_reason_code == NotExecutedReason.ACTION_NOT_ALLOWED_AT_POINT.value
    )
    assert adapter.calls == []


def test_repair_and_regenerate_are_never_executable() -> None:
    binding = _binding(granted=("repair",), registered=("repair",))
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="repair", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("repair",)),
        registry={},
        adapters={},
        action_registry=ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=("repair",)
        ),
    )
    assert results[0].not_executed_reason_code == (
        NotExecutedReason.NOT_EXECUTABLE_ACTION_CLASS.value
    )


def test_a_valid_action_executes_through_its_registered_adapter() -> None:
    binding = _binding(granted=("reject_output",), registered=("reject_output",))
    adapter = _RecordingAdapter(intervening_by_action={"reject_output": True})
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert results[0].executed is True
    assert results[0].intervening is True
    assert adapter.calls == [("reject_output", MAIN_MODEL_POST_POINT_ID, STAGE_POST)]


def test_duplicate_recommendations_for_the_same_action_execute_once() -> None:
    binding = _binding(granted=("warn",), registered=("warn",))
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="warn", severity=Severity.LOW),
            RecommendedAction(action_id="warn", severity=Severity.HIGH),
        ),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("warn",)),
        registry={
            "warn": ActionRegistryEntry(
                action_id="warn",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"warn": adapter},
    )
    assert len(results) == 1
    assert len(adapter.calls) == 1


def test_adapter_exception_is_reported_not_executed_not_raised() -> None:
    binding = _binding(granted=("warn",), registered=("warn",))

    class _RaisingAdapter:
        def execute(self, *, action_id: str, point_id: str, stage: str) -> ExecutedAction:
            raise RuntimeError("boom")

    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="warn", severity=Severity.LOW),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("warn",)),
        registry={
            "warn": ActionRegistryEntry(
                action_id="warn",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"warn": _RaisingAdapter()},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.ADAPTER_FAILURE.value


def test_adapter_misreporting_intervening_is_reported_as_adapter_failure() -> None:
    # A Faulty Adapter claiming `intervening=False` for `reject_output`
    # (which is Frozen to always intervene) must never be trusted as
    # success — the Resolver treats the mismatch as a Fault (P4-PNT-006).
    binding = _binding(granted=("reject_output",), registered=("reject_output",))
    adapter = _RecordingAdapter(intervening_by_action={"reject_output": False})
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.ADAPTER_FAILURE.value


def test_terminal_action_supersedes_a_co_recommended_non_terminal_action() -> None:
    binding = _binding(
        granted=("stop_before_generation", "constrain_generation_config"),
        registered=("stop_before_generation", "constrain_generation_config"),
        point_id=MAIN_MODEL_PRE_POINT_ID,
    )
    adapter = _RecordingAdapter(intervening_by_action={"stop_before_generation": True})
    results = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="stop_before_generation", severity=Severity.MODERATE),
            RecommendedAction(action_id="constrain_generation_config", severity=Severity.MODERATE),
        ),
        point_id=MAIN_MODEL_PRE_POINT_ID,
        stage=STAGE_PRE,
        binding=binding,
        authority=AuthoritySnapshot(
            authority_revision=1,
            granted_action_ids=("stop_before_generation", "constrain_generation_config"),
        ),
        registry={
            "stop_before_generation": ActionRegistryEntry(
                action_id="stop_before_generation",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_PRE_POINT_ID,),
                allowed_stages=(STAGE_PRE,),
                side_effect_class="local",
            ),
            "constrain_generation_config": ActionRegistryEntry(
                action_id="constrain_generation_config",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_PRE_POINT_ID,),
                allowed_stages=(STAGE_PRE,),
                side_effect_class="local",
            ),
        },
        adapters={"stop_before_generation": adapter, "constrain_generation_config": adapter},
    )
    by_action = {result.action_id: result for result in results}
    assert by_action["stop_before_generation"].executed is True
    assert by_action["constrain_generation_config"].executed is False
    assert (
        by_action["constrain_generation_config"].not_executed_reason_code
        == NotExecutedReason.SUPERSEDED_BY_HIGHER_PRIORITY_ACTION.value
    )
    assert adapter.calls == [("stop_before_generation", MAIN_MODEL_PRE_POINT_ID, STAGE_PRE)]


def test_non_terminal_actions_do_not_supersede_each_other() -> None:
    binding = _binding(
        granted=("warn", "constrain_generation_config"),
        registered=("warn", "constrain_generation_config"),
        point_id=MAIN_MODEL_PRE_POINT_ID,
    )
    adapter = _RecordingAdapter(intervening_by_action={"constrain_generation_config": True})
    results = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="warn", severity=Severity.LOW),
            RecommendedAction(action_id="constrain_generation_config", severity=Severity.MODERATE),
        ),
        point_id=MAIN_MODEL_PRE_POINT_ID,
        stage=STAGE_PRE,
        binding=binding,
        authority=AuthoritySnapshot(
            authority_revision=1, granted_action_ids=("warn", "constrain_generation_config")
        ),
        registry={
            "warn": ActionRegistryEntry(
                action_id="warn",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_PRE_POINT_ID,),
                allowed_stages=(STAGE_PRE,),
                side_effect_class="local",
            ),
            "constrain_generation_config": ActionRegistryEntry(
                action_id="constrain_generation_config",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_PRE_POINT_ID,),
                allowed_stages=(STAGE_PRE,),
                side_effect_class="local",
            ),
        },
        adapters={"warn": adapter, "constrain_generation_config": adapter},
    )
    assert all(result.executed for result in results)
    assert len(adapter.calls) == 2


def test_stale_binding_from_a_changed_capability_snapshot_executes_nothing() -> None:
    bind_time_capability = _capability()
    binding = _binding(
        granted=("reject_output",), registered=("reject_output",), capability=bind_time_capability
    )
    live_capability = bind_time_capability.model_copy(update={"max_context_tokens": 8192})
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
        capability=live_capability,
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_stale_binding_from_a_changed_budget_snapshot_executes_nothing() -> None:
    bind_time_budget = _budget()
    binding = _binding(
        granted=("reject_output",), registered=("reject_output",), budget=bind_time_budget
    )
    live_budget = bind_time_budget.model_copy(update={"max_snapshot_chars": 1})
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
        budget=live_budget,
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


# -- P4-CODEX-010 Rework: Current Authority Staleness and Terminal
# Conflict Resolution independent of input order. --


def test_stale_binding_from_a_changed_authority_revision_executes_nothing() -> None:
    bind_time_authority = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=("reject_output",)
    )
    binding = _binding(
        registered=("reject_output",),
        authority=bind_time_authority,
    )
    # Same grant set, but a live Authority Revision bump — Architecture §9
    # "Authority Revision変更でStale Bindingを再利用しない".
    live_authority = AuthoritySnapshot(authority_revision=2, granted_action_ids=("reject_output",))
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=live_authority,
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_stale_binding_from_a_changed_authority_grant_set_executes_nothing() -> None:
    bind_time_authority = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=("reject_output", "warn")
    )
    binding = _binding(
        registered=("reject_output",),
        authority=bind_time_authority,
    )
    # Same Revision, but the live Grant set has shrunk (still contains
    # reject_output, so the per-action Authority check alone would pass —
    # the point is that Staleness must be caught independently of that).
    live_authority = AuthoritySnapshot(authority_revision=1, granted_action_ids=("reject_output",))
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=live_authority,
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_current_authority_check_still_applies_when_the_binding_is_fresh() -> None:
    # A sanity check that the new Authority-in-Staleness-Check addition
    # did not silently swallow the pre-existing per-action Authority
    # Missing check: same live+bind-time Authority (fresh Binding), but
    # the Action itself simply is not Granted.
    authority = AuthoritySnapshot(authority_revision=1, granted_action_ids=("warn",))
    binding = _binding(registered=("reject_output",), authority=authority)
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        binding=binding,
        authority=authority,
        registry={
            "reject_output": ActionRegistryEntry(
                action_id="reject_output",  # type: ignore[arg-type]
                allowed_points=(MAIN_MODEL_POST_POINT_ID,),
                allowed_stages=(STAGE_POST,),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": adapter},
    )
    assert results[0].executed is False
    assert results[0].not_executed_reason_code == NotExecutedReason.AUTHORITY_MISSING.value


def _terminal_conflict_setup() -> tuple[
    dict[str, ActionRegistryEntry], AuthoritySnapshot, BoundGovernancePlan
]:
    # A Test-only Registry where BOTH Terminal Actions are (unusually,
    # for this scenario only) scoped to the exact same Point/Stage — the
    # real `bootstrap/runtime_governance.py` Registry never does this
    # (`stop_before_generation` is pre-only, `reject_output` is
    # post-only, so they can never be simultaneously eligible there) —
    # this is the only way to genuinely exercise a two-eligible-Terminal
    # scenario, which the real Registry's own Point/Stage scoping
    # structurally forbids.
    registry = {
        "stop_before_generation": ActionRegistryEntry(
            action_id="stop_before_generation",  # type: ignore[arg-type]
            allowed_points=(MAIN_MODEL_POST_POINT_ID,),
            allowed_stages=(STAGE_POST,),
            side_effect_class="local",
        ),
        "reject_output": ActionRegistryEntry(
            action_id="reject_output",  # type: ignore[arg-type]
            allowed_points=(MAIN_MODEL_POST_POINT_ID,),
            allowed_stages=(STAGE_POST,),
            side_effect_class="local",
        ),
    }
    authority = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=("stop_before_generation", "reject_output")
    )
    binding = _binding(registered=("stop_before_generation", "reject_output"), authority=authority)
    return registry, authority, binding


def test_terminal_conflict_resolution_is_independent_of_recommendation_order() -> None:
    registry, authority, binding = _terminal_conflict_setup()
    adapter = _RecordingAdapter(intervening_by_action={"reject_output": True})

    # reject_output recommended *after* stop_before_generation in the
    # input tuple, but reject_output has strictly higher Severity — the
    # higher-Severity, later-recommended candidate must still win.
    forward_order = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="stop_before_generation", severity=Severity.MODERATE),
            RecommendedAction(action_id="reject_output", severity=Severity.CRITICAL),
        ),
        binding=binding,
        authority=authority,
        registry=registry,
        adapters={"stop_before_generation": adapter, "reject_output": adapter},
    )
    by_action_forward = {r.action_id: r for r in forward_order}
    assert by_action_forward["reject_output"].executed is True
    assert by_action_forward["stop_before_generation"].executed is False
    assert (
        by_action_forward["stop_before_generation"].not_executed_reason_code
        == NotExecutedReason.SUPERSEDED_BY_HIGHER_PRIORITY_ACTION.value
    )

    # Same two candidates, reversed input order — result must be
    # identical (order-independence is the whole point of this Rework).
    adapter2 = _RecordingAdapter(intervening_by_action={"reject_output": True})
    reverse_order = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="reject_output", severity=Severity.CRITICAL),
            RecommendedAction(action_id="stop_before_generation", severity=Severity.MODERATE),
        ),
        binding=binding,
        authority=authority,
        registry=registry,
        adapters={"stop_before_generation": adapter2, "reject_output": adapter2},
    )
    by_action_reverse = {r.action_id: r for r in reverse_order}
    assert by_action_reverse["reject_output"].executed is True
    assert by_action_reverse["stop_before_generation"].executed is False
    assert (
        by_action_reverse["stop_before_generation"].not_executed_reason_code
        == NotExecutedReason.SUPERSEDED_BY_HIGHER_PRIORITY_ACTION.value
    )


def test_an_ineligible_terminal_candidate_keeps_its_own_reason_not_superseded() -> None:
    # stop_before_generation is recommended but NOT registered at this
    # Point/Stage in this Test's Registry (only reject_output is) — it
    # must report its own genuine ACTION_NOT_REGISTERED, never be
    # mislabeled `superseded` by reject_output (which never actually
    # competed with an ineligible candidate).
    registry = {
        "reject_output": ActionRegistryEntry(
            action_id="reject_output",  # type: ignore[arg-type]
            allowed_points=(MAIN_MODEL_POST_POINT_ID,),
            allowed_stages=(STAGE_POST,),
            side_effect_class="local",
        ),
    }
    authority = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=("stop_before_generation", "reject_output")
    )
    binding = _binding(registered=("reject_output",), authority=authority)
    adapter = _RecordingAdapter(intervening_by_action={"reject_output": True})
    results = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="stop_before_generation", severity=Severity.CRITICAL),
            RecommendedAction(action_id="reject_output", severity=Severity.MODERATE),
        ),
        binding=binding,
        authority=authority,
        registry=registry,
        adapters={"reject_output": adapter},
    )
    by_action = {r.action_id: r for r in results}
    assert by_action["reject_output"].executed is True
    assert (
        by_action["stop_before_generation"].not_executed_reason_code
        == NotExecutedReason.ACTION_NOT_REGISTERED.value
    )


def test_two_eligible_terminal_candidates_at_the_same_severity_are_unresolved() -> None:
    registry, authority, binding = _terminal_conflict_setup()
    adapter = _RecordingAdapter()
    results = _resolve(
        recommended_actions=(
            RecommendedAction(action_id="stop_before_generation", severity=Severity.HIGH),
            RecommendedAction(action_id="reject_output", severity=Severity.HIGH),
        ),
        binding=binding,
        authority=authority,
        registry=registry,
        adapters={"stop_before_generation": adapter, "reject_output": adapter},
    )
    by_action = {r.action_id: r for r in results}
    assert by_action["stop_before_generation"].executed is False
    assert by_action["reject_output"].executed is False
    assert (
        by_action["stop_before_generation"].not_executed_reason_code
        == NotExecutedReason.CONFLICT_UNRESOLVED.value
    )
    assert (
        by_action["reject_output"].not_executed_reason_code
        == NotExecutedReason.CONFLICT_UNRESOLVED.value
    )
    assert adapter.calls == []
