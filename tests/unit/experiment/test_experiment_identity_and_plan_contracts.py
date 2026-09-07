"""Phase 9-2 WU-A A1/A2: Experiment/Variant/Plan Identity Contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlan,
    ExperimentPlanBudget,
    VariantConfigurationRef,
    VariantDescriptor,
    build_experiment_plan,
    compute_plan_digest_sha512,
)

_CASE_DIGEST = "2" * 128


def _variant(variant_id: str, *, judge_mode: str = "enforce") -> VariantDescriptor:
    return VariantDescriptor(
        variant_id=variant_id,
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main.qwen3-4b"),
            ComponentSelection(
                component_key=ComponentKey.JUDGE,
                selector_id="judge.gemma-4-e2b-it-q4-0",
                mode=judge_mode,
            ),
        ),
    )


def test_build_experiment_plan_computes_a_verifiable_digest() -> None:
    variant_a = _variant("variant-a")
    variant_b = _variant("variant-b", judge_mode="off")
    plan = build_experiment_plan(
        experiment_id="exp-001",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a, variant_b),
        execution_order=("variant-a", "variant-b"),
    )
    expected = compute_plan_digest_sha512(
        experiment_id="exp-001",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a, variant_b),
        execution_order=("variant-a", "variant-b"),
        budget=ExperimentPlanBudget(),
    )
    assert plan.plan_digest_sha512 == expected
    # Round-trips through JSON (as the filesystem Store will) without
    # losing digest verifiability.
    rehydrated = ExperimentPlan.model_validate(plan.model_dump(mode="json"))
    assert rehydrated == plan


def test_experiment_plan_rejects_duplicate_variant_id() -> None:
    variant = _variant("variant-a")
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_experiment_plan(
            experiment_id="exp-002",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(variant, variant),
            execution_order=("variant-a", "variant-a"),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER


def test_experiment_plan_rejects_empty_experiment_id() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_experiment_plan(
            experiment_id="",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(_variant("variant-a"),),
            execution_order=("variant-a",),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.EMPTY_IDENTIFIER


def test_experiment_plan_rejects_execution_order_referencing_unknown_variant() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_experiment_plan(
            experiment_id="exp-003",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(_variant("variant-a"),),
            execution_order=("variant-a", "variant-does-not-exist"),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.UNKNOWN_VARIANT


def test_experiment_plan_rejects_execution_order_missing_a_declared_variant() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_experiment_plan(
            experiment_id="exp-004",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(_variant("variant-a"), _variant("variant-b")),
            execution_order=("variant-a",),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.UNKNOWN_VARIANT


def test_experiment_plan_rejects_a_hand_picked_mismatched_digest() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        ExperimentPlan(
            experiment_id="exp-005",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(_variant("variant-a"),),
            execution_order=("variant-a",),
            budget=ExperimentPlanBudget(),
            plan_digest_sha512="0" * 128,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.PLAN_DIGEST_MISMATCH


def test_experiment_plan_rejects_config_digest_referencing_unknown_variant() -> None:
    """R1-WU-01: `variant_configuration_digests` must reference only this
    Plan's own `variants` -- never a Variant ID from a different Plan or a
    typo that would silently be dropped."""
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_experiment_plan(
            experiment_id="exp-005b",
            case_id="case-a",
            case_revision="case-rev-1",
            case_digest_sha512=_CASE_DIGEST,
            variants=(_variant("variant-a"),),
            execution_order=("variant-a",),
            variant_configuration_digests=(
                VariantConfigurationRef(
                    variant_id="variant-does-not-exist",
                    configuration_digest_sha512=_CASE_DIGEST,
                ),
            ),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.CONFIG_DIGEST_UNKNOWN_VARIANT


def test_variant_descriptor_rejects_duplicate_component_key() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        VariantDescriptor(
            variant_id="variant-dup",
            components=(
                ComponentSelection(component_key=ComponentKey.JUDGE, selector_id="judge-a"),
                ComponentSelection(component_key=ComponentKey.JUDGE, selector_id="judge-b"),
            ),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER


@pytest.mark.parametrize(
    "unsafe_value",
    ["/etc/passwd", "KEY=SECRET", "has space", "../escape", ""],
)
def test_component_selection_rejects_unsafe_or_path_like_identifiers(unsafe_value: str) -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        ComponentSelection(component_key=ComponentKey.RAG, selector_id=unsafe_value)
    assert excinfo.value.code in (
        ExperimentCoreErrorCode.UNSAFE_IDENTIFIER,
        ExperimentCoreErrorCode.EMPTY_IDENTIFIER,
    )


def test_variant_descriptor_component_lookup_returns_none_for_absent_key() -> None:
    variant = VariantDescriptor(
        variant_id="variant-partial",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    assert variant.component(ComponentKey.MAIN) is not None
    assert variant.component(ComponentKey.RAG) is None


def test_experiment_plan_variant_lookup_raises_typed_error_for_unknown_id() -> None:
    plan = build_experiment_plan(
        experiment_id="exp-006",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(_variant("variant-a"),),
        execution_order=("variant-a",),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        plan.variant("variant-does-not-exist")
    assert excinfo.value.code is ExperimentCoreErrorCode.UNKNOWN_VARIANT


def test_experiment_plan_budget_rejects_a_non_positive_max_variant_runs() -> None:
    """R1-WU-02: a set `max_variant_runs` must be a genuine positive
    limit -- `0` could never be satisfied by any real Run, so this is
    rejected at construction rather than silently behaving like "no
    limit"."""
    with pytest.raises(ValidationError):
        ExperimentPlanBudget(max_variant_runs=0)


def test_experiment_plan_budget_rejects_a_non_positive_deadline_ms() -> None:
    with pytest.raises(ValidationError):
        ExperimentPlanBudget(deadline_ms=-1)
