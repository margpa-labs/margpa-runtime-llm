"""Baseline / Regression / Ablation Declarations (Phase 9-2, WU-B B4).

WU-B B4: "同一CaseへBaselineと1要素差Variantを適用し、複数要素を同時変更
した結果を単一要因の効果と主張しない" -- `verify_single_factor_difference`
independently recomputes the real diff between two `VariantDescriptor`s
and rejects a `REGRESSION`/`ABLATION` declaration whose claimed
`varied_component_keys` does not exactly match that real diff, or whose
real diff touches more than one Component. A caller cannot simply assert
"this is a single-factor change" -- it is mechanically checked against
the actual two Variants being compared."""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import ComponentKey, VariantDescriptor, require_safe_identifier


class VariantRelationship(StrEnum):
    BASELINE = "baseline"
    REGRESSION = "regression"
    ABLATION = "ablation"


class VariantComparisonDeclaration(ImmutableContract):
    baseline_variant_id: str
    variant_id: str
    relationship: VariantRelationship
    varied_component_keys: tuple[ComponentKey, ...] = ()

    @model_validator(mode="after")
    def _validate_ids(self) -> VariantComparisonDeclaration:
        require_safe_identifier(self.baseline_variant_id, field_name="baseline_variant_id")
        require_safe_identifier(self.variant_id, field_name="variant_id")
        return self


def diff_component_keys(
    baseline: VariantDescriptor, variant: VariantDescriptor
) -> tuple[ComponentKey, ...]:
    """The real, independently-recomputed set of `ComponentKey`s whose
    `ComponentSelection` differs (including one being present and the
    other absent) between the two Variants -- never author-asserted."""

    keys = set(ComponentKey)
    differing = [
        key for key in keys if baseline.component(key) != variant.component(key)
    ]
    return tuple(sorted(differing, key=lambda key: key.value))


def verify_single_factor_difference(
    *,
    baseline: VariantDescriptor,
    variant: VariantDescriptor,
    declared: VariantComparisonDeclaration,
) -> None:
    """Fail-closed: raises `ExperimentCoreError` if `declared` claims a
    diff that does not exactly match the real, recomputed diff between
    `baseline` and `variant`, or if a `REGRESSION`/`ABLATION` declaration
    is not genuinely single-factor."""

    if declared.baseline_variant_id != baseline.variant_id:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.DECLARED_DIFF_MISMATCH,
            safe_message=(
                f"declared baseline_variant_id {declared.baseline_variant_id!r} does not "
                f"match the supplied baseline Variant {baseline.variant_id!r}"
            ),
        )
    if declared.variant_id != variant.variant_id:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.DECLARED_DIFF_MISMATCH,
            safe_message=(
                f"declared variant_id {declared.variant_id!r} does not match the "
                f"supplied Variant {variant.variant_id!r}"
            ),
        )
    actual_diff = diff_component_keys(baseline, variant)
    if declared.relationship is VariantRelationship.BASELINE:
        return
    if set(declared.varied_component_keys) != set(actual_diff):
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.DECLARED_DIFF_MISMATCH,
            safe_message=(
                f"declared varied_component_keys {sorted(declared.varied_component_keys)} "
                f"does not match the real recomputed diff {list(actual_diff)}"
            ),
        )
    if len(actual_diff) != 1:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.MULTI_FACTOR_DIFFERENCE,
            safe_message=(
                f"declared a single-factor {declared.relationship.value} between "
                f"{baseline.variant_id!r} and {variant.variant_id!r}, but the real diff "
                f"touches {len(actual_diff)} components: {list(actual_diff)}"
            ),
        )
