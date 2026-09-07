"""Phase 9-2 WU-B B4: Baseline/Regression/Ablation single-factor check."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.comparison_declaration import (
    VariantComparisonDeclaration,
    VariantRelationship,
    diff_component_keys,
    verify_single_factor_difference,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
)


def _variant(variant_id: str, *, judge_mode: str, guard_mode: str = "off") -> VariantDescriptor:
    return VariantDescriptor(
        variant_id=variant_id,
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode=judge_mode),
            ComponentSelection(component_key=ComponentKey.GUARD, mode=guard_mode),
        ),
    )


def test_diff_component_keys_finds_exactly_the_changed_slot() -> None:
    baseline = _variant("baseline", judge_mode="off")
    variant = _variant("judge-enforce", judge_mode="enforce")
    assert diff_component_keys(baseline, variant) == (ComponentKey.JUDGE,)


def test_verify_single_factor_difference_accepts_a_genuinely_single_factor_regression() -> None:
    baseline = _variant("baseline", judge_mode="off")
    variant = _variant("judge-enforce", judge_mode="enforce")
    declared = VariantComparisonDeclaration(
        baseline_variant_id="baseline",
        variant_id="judge-enforce",
        relationship=VariantRelationship.REGRESSION,
        varied_component_keys=(ComponentKey.JUDGE,),
    )
    verify_single_factor_difference(baseline=baseline, variant=variant, declared=declared)


def test_verify_single_factor_difference_rejects_a_multi_factor_change_declared_as_single() -> None:
    baseline = _variant("baseline", judge_mode="off", guard_mode="off")
    variant = _variant("judge-and-guard-enforce", judge_mode="enforce", guard_mode="enforce")
    declared = VariantComparisonDeclaration(
        baseline_variant_id="baseline",
        variant_id="judge-and-guard-enforce",
        relationship=VariantRelationship.ABLATION,
        varied_component_keys=(ComponentKey.JUDGE, ComponentKey.GUARD),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        verify_single_factor_difference(baseline=baseline, variant=variant, declared=declared)
    assert excinfo.value.code is ExperimentCoreErrorCode.MULTI_FACTOR_DIFFERENCE


def test_verify_single_factor_difference_rejects_a_falsely_declared_diff_set() -> None:
    """The real diff only touches JUDGE, but the declaration claims GUARD
    -- this must be rejected even though the declared count (1) looks
    single-factor on its face."""
    baseline = _variant("baseline", judge_mode="off")
    variant = _variant("judge-enforce", judge_mode="enforce")
    declared = VariantComparisonDeclaration(
        baseline_variant_id="baseline",
        variant_id="judge-enforce",
        relationship=VariantRelationship.REGRESSION,
        varied_component_keys=(ComponentKey.GUARD,),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        verify_single_factor_difference(baseline=baseline, variant=variant, declared=declared)
    assert excinfo.value.code is ExperimentCoreErrorCode.DECLARED_DIFF_MISMATCH


def test_verify_single_factor_difference_rejects_mismatched_variant_identity() -> None:
    baseline = _variant("baseline", judge_mode="off")
    variant = _variant("judge-enforce", judge_mode="enforce")
    declared = VariantComparisonDeclaration(
        baseline_variant_id="not-the-real-baseline",
        variant_id="judge-enforce",
        relationship=VariantRelationship.REGRESSION,
        varied_component_keys=(ComponentKey.JUDGE,),
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        verify_single_factor_difference(baseline=baseline, variant=variant, declared=declared)
    assert excinfo.value.code is ExperimentCoreErrorCode.DECLARED_DIFF_MISMATCH


def test_verify_single_factor_difference_allows_a_baseline_declaration_with_no_diff_claim() -> None:
    baseline = _variant("baseline", judge_mode="off")
    declared = VariantComparisonDeclaration(
        baseline_variant_id="baseline",
        variant_id="baseline",
        relationship=VariantRelationship.BASELINE,
    )
    verify_single_factor_difference(baseline=baseline, variant=baseline, declared=declared)
