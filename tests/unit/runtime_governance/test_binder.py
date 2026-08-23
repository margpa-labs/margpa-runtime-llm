"""Governance Binder: content-addressed identity and Cache invalidation
(P4-B-WU-001/002/003)."""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.application import (
    BoundGovernancePlanCache,
    bind,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_PRE_POINT_ID,
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BudgetSnapshot,
    EvaluationMethod,
    ExecutionDescriptor,
    PolicySnapshot,
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


def _authority(*, granted: tuple[str, ...] = ()) -> AuthoritySnapshot:
    return AuthoritySnapshot(authority_revision=1, granted_action_ids=granted)


def _policy() -> PolicySnapshot:
    return PolicySnapshot(policy_revision=1, profile="core")


def _budget() -> BudgetSnapshot:
    return BudgetSnapshot(
        max_calls_per_invocation=0,
        max_latency_ms=1000,
        max_snapshot_chars=10_000,
        allowed_generation_config_fields=(),
    )


def _registry(*, registered: tuple[str, ...] = ()) -> ActionRegistrySnapshot:
    return ActionRegistrySnapshot(registry_revision=1, registered_action_ids=registered)


def _descriptor(
    descriptor_id: str, *, recommended_action_id: str | None = None
) -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id=descriptor_id,
        source_definition_id="argd",
        source_pointer="$.argd.axiomatic_reasoning_governance_definition",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
        recommended_action_id=recommended_action_id,
    )


def test_bind_never_marks_empty_registry_as_executable() -> None:
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(),
    )
    assert plan.executable is False


def test_bind_is_not_executable_with_zero_descriptors_despite_registry_and_authority() -> None:
    # P4-CODEX-004 Rework: Registry/Authority alone were never enough —
    # a Binding with zero validated Descriptors has nothing to enforce
    # and must never be Executable (Frozen Acceptance Matrix
    # `Definitions 0 + enforce: unsupported / mutation 0`).
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    assert plan.executable is False
    assert plan.unavailable_reason_code == "no_definitions"


def test_bind_is_executable_with_descriptors_registry_authority_and_source_plan_present() -> None:
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id="plan-1",
        source_plan_digest_sha512="a" * 128,
        descriptors=(_descriptor("argd.rule-1"),),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    assert plan.executable is True
    assert plan.unavailable_reason_code is None
    assert plan.binding_id == plan.binding_digest_sha512


def test_bind_is_not_executable_with_descriptors_but_no_source_plan() -> None:
    # P4-CODEX-008: non-empty Descriptors without a real Phase 3 Source
    # Plan Identity behind them must stay non-Executable — there is
    # nothing to trace the Binding back to.
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(_descriptor("argd.rule-1"),),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    assert plan.executable is False
    assert plan.unavailable_reason_code == "no_source_plan"


def test_bind_digest_distinguishes_unavailable_reasons_with_identical_empty_descriptors() -> None:
    # P4-CODEX-008: `no_provider`/`provider_failure`/`invalid_bundle` all
    # produce identical empty Descriptors/Digests otherwise — they must
    # not collide on the same Binding Digest.
    no_provider = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
        descriptor_unavailable_reason_code="no_provider",
    )
    provider_failure = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
        descriptor_unavailable_reason_code="provider_failure",
    )
    invalid_bundle = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
        descriptor_unavailable_reason_code="invalid_bundle",
    )
    digests = {
        no_provider.binding_digest_sha512,
        provider_failure.binding_digest_sha512,
        invalid_bundle.binding_digest_sha512,
    }
    assert len(digests) == 3


def test_bind_surfaces_a_composition_supplied_reason_for_empty_descriptors() -> None:
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
        descriptor_unavailable_reason_code="invalid_bundle",
    )
    assert plan.executable is False
    assert plan.unavailable_reason_code == "invalid_bundle"


def test_bind_flags_descriptors_recommending_an_unregistered_action_as_unresolved() -> None:
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(_descriptor("argd.rule-1", recommended_action_id="reject_output"),),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    assert plan.unresolved_descriptor_ids == ("argd.rule-1",)
    assert plan.executable is False


def test_bind_is_deterministic_for_identical_inputs() -> None:
    kwargs = dict(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id="plan-1",
        source_plan_digest_sha512="a" * 128,
        descriptors=(_descriptor("argd.rule-1"),),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    first = bind(**kwargs)  # type: ignore[arg-type]
    second = bind(**kwargs)  # type: ignore[arg-type]
    assert first.binding_digest_sha512 == second.binding_digest_sha512


def test_bind_changes_digest_when_any_snapshot_changes() -> None:
    base = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn",)),
    )
    changed = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(granted=("warn",)),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(registered=("warn", "reject_output")),
    )
    assert base.binding_digest_sha512 != changed.binding_digest_sha512


def test_cache_hit_only_on_exact_digest() -> None:
    cache = BoundGovernancePlanCache()
    plan = bind(
        point_id=MAIN_MODEL_PRE_POINT_ID,
        source_plan_id=None,
        source_plan_digest_sha512=None,
        descriptors=(),
        capability=_capability(),
        authority=_authority(),
        policy=_policy(),
        budget=_budget(),
        action_registry=_registry(),
    )
    assert cache.get(plan.binding_digest_sha512) is None
    cache.put(plan)
    assert cache.get(plan.binding_digest_sha512) == plan
    cache.clear()
    assert cache.size() == 0
