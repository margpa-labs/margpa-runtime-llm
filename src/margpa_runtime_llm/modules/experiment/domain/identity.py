"""Experiment/Plan/Variant Identity Contracts (Phase 9-2, WU-A A1/A2).

Model, Provider, and GD-specific identities are never hard-coded here
(Handoff WU-A A1: "Model/Provider/GD固有SchemaをCoreへHard-codeしない").
`ComponentSelection.selector_id`/`mode` are opaque, Adapter-interpreted
strings -- Experiment Core validates only that they are safe, non-secret
identifiers (WU-A A2: "Secret、認証情報、User絶対PathをSnapshotへ入れない"),
never their meaning. `ComponentKey` is Core's own generic taxonomy of
"which layer this slot is" (Design §5/§6 C1's nine named slots), not a
Provider/Model vocabulary, so enumerating it here does not reintroduce
the coupling the Handoff prohibits.
"""

from __future__ import annotations

import hashlib
import re
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .canonical import canonical_json_bytes
from .errors import ExperimentCoreError, ExperimentCoreErrorCode

SHA512_PATTERN = r"^[0-9a-f]{128}$"

# Deliberately excludes "/", "\", whitespace, and "=" -- rules out an
# absolute User Path, a traversal segment, or a `KEY=VALUE`-shaped secret
# ending up in a Snapshot/Plan that gets persisted and compared verbatim.
_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def require_safe_identifier(value: str, *, field_name: str) -> str:
    if not value:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.EMPTY_IDENTIFIER,
            safe_message=f"{field_name} must not be empty",
        )
    if not _SAFE_ID_PATTERN.match(value):
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.UNSAFE_IDENTIFIER,
            safe_message=f"{field_name} is not a safe identifier: {value!r}",
        )
    return value


class ComponentKey(StrEnum):
    """The nine named Variant Component slots (Design §6 C1) -- a
    structural taxonomy owned by Experiment Core itself, not a Provider or
    Model vocabulary."""

    MAIN = "main"
    JUDGE = "judge"
    GUARD = "guard"
    MAIN_GOVERNANCE = "main_governance"
    DEFINITION_SET = "definition_set"
    RAG = "rag"
    REPAIR = "repair"
    RECORDING = "recording"
    PRESENTATION = "presentation"


class ComponentSelection(ImmutableContract):
    """One Variant Component slot: an opaque ID reference to a
    Provider/Mode/Definition-Set understood only by the Actor Adapter for
    this `component_key` (WU-C C2) -- Experiment Core itself never
    interprets `selector_id`/`mode`, only validates they are safe,
    non-secret, non-Path identifiers or absent entirely (`None` means
    "this Component is OFF/absent for this Variant", WU-C C3)."""

    component_key: ComponentKey
    selector_id: str | None = None
    mode: str | None = None

    @field_validator("selector_id", "mode")
    @classmethod
    def _validate_optional_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return require_safe_identifier(value, field_name="ComponentSelection field")


class VariantDescriptor(ImmutableContract):
    """WU-A A1 / WU-C C1: a named, ID-referenced combination of Component
    Selections. `components` need not cover every `ComponentKey` -- an
    absent key means that Component is unspecified/absent for this
    Variant (distinct from an explicit `mode="off"` ComponentSelection,
    WU-C C3's "不在" vs "OFF" distinction)."""

    variant_id: str
    components: tuple[ComponentSelection, ...] = ()

    @field_validator("variant_id")
    @classmethod
    def _validate_variant_id(cls, value: str) -> str:
        return require_safe_identifier(value, field_name="variant_id")

    @model_validator(mode="after")
    def _validate_unique_component_keys(self) -> VariantDescriptor:
        keys = [item.component_key for item in self.components]
        if len(keys) != len(set(keys)):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                safe_message=(
                    f"variant {self.variant_id!r} declares the same component_key more than once"
                ),
            )
        return self

    def component(self, key: ComponentKey) -> ComponentSelection | None:
        for item in self.components:
            if item.component_key is key:
                return item
        return None


class ExperimentIdentity(ImmutableContract):
    """WU-A A1: Experiment, Run, Variant, and Request are always distinct
    IDs -- this Contract only ever carries the top-level Experiment
    Identity, never a Run or Variant one."""

    experiment_id: str
    owner_scope: str
    created_at: str

    @field_validator("experiment_id", "owner_scope")
    @classmethod
    def _validate_ids(cls, value: str) -> str:
        return require_safe_identifier(value, field_name="ExperimentIdentity field")

    @field_validator("created_at")
    @classmethod
    def _validate_created_at(cls, value: str) -> str:
        if not value:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.EMPTY_IDENTIFIER,
                safe_message="created_at must not be empty",
            )
        return value


class StopPolicy(StrEnum):
    """R1-WU-02: `ExperimentPlanBudget.stop_policy` is a closed vocabulary,
    never a free-form string a Runtime would have to interpret loosely."""

    CONTINUE_ON_FAILURE = "continue_on_failure"
    HALT_ON_FIRST_FAILURE = "halt_on_first_failure"


class ExperimentPlanBudget(ImmutableContract):
    """WU-A A1: budget/deadline/stop_policy are part of the frozen Plan,
    never mutated once the Plan is created. R1-WU-02: every bound, once
    set, must be a genuine positive limit -- `max_variant_runs=0` or a
    negative `deadline_ms` could never be satisfied by any real Run, so
    Pydantic rejects them at construction rather than letting a
    Runtime-enforcement bug silently treat them as "no limit"."""

    max_variant_runs: int | None = Field(default=None, gt=0)
    deadline_ms: int | None = Field(default=None, gt=0)
    stop_policy: StopPolicy | None = None


class VariantConfigurationRef(ImmutableContract):
    """R1-WU-01: one Variant's Frozen Effective Configuration reference --
    `identity.py` itself never imports `config_snapshot.py` (that would
    invert this module's own dependency direction, since `config_snapshot.
    py` already imports `ComponentKey`/`ComponentSelection` from here), so
    this Plan-level Contract carries only the already-computed
    `EffectiveConfigurationSnapshot.configuration_digest_sha512` by
    reference, never the Snapshot object itself."""

    variant_id: str
    configuration_digest_sha512: str = Field(pattern=SHA512_PATTERN)

    @field_validator("variant_id")
    @classmethod
    def _validate_variant_id(cls, value: str) -> str:
        return require_safe_identifier(value, field_name="variant_id")


class ExperimentPlan(ImmutableContract):
    """WU-A A1/A2: freezes Case Revision and the Variant set together --
    once built, `variants`/`execution_order`/`case_revision` never change;
    a differently-scoped Plan is a new `ExperimentPlan` with a new digest,
    never a mutation of this one.

    R1-WU-01 (IR-P9-2-02 fix): `case_revision` alone cannot answer "which
    Case did this Plan choose" when a Case Pack revision covers several
    Cases (`case_pack.CASE_PACK_REVISION`) -- `case_id`/`case_digest_
    sha512` close that gap. `variant_configuration_digests` is this
    Plan's own record of each Variant's Frozen Effective Configuration
    (by digest reference, `VariantConfigurationRef` above); it defaults
    to empty so a purely Fixture-Matrix-scoped Plan (no live Provider/
    Config identity to freeze) stays valid, but every entry it does carry
    must reference one of this Plan's own `variants`."""

    experiment_id: str
    case_id: str
    case_revision: str
    case_digest_sha512: str = Field(pattern=SHA512_PATTERN)
    variants: tuple[VariantDescriptor, ...] = Field(min_length=1)
    execution_order: tuple[str, ...]
    budget: ExperimentPlanBudget = ExperimentPlanBudget()
    variant_configuration_digests: tuple[VariantConfigurationRef, ...] = ()
    execution_mode: Literal["fixture", "production"] = "fixture"
    """R3-WU-01 (IR-P9-2-R2-07 MAJOR fix): Frozen Identity, decided once at
    Plan-creation time and never re-specified per-Run -- R2's own
    `StartRunRequest.execution_mode` let the SAME Plan/Variant be run as
    both Fixture and Production, leaving ambiguous which Config contract
    was actually frozen for it. Every Run started against this Plan uses
    THIS value; there is no longer any way to choose differently at
    Run-start time."""
    plan_digest_sha512: str = Field(pattern=SHA512_PATTERN)

    @field_validator("experiment_id", "case_id", "case_revision")
    @classmethod
    def _validate_ids(cls, value: str) -> str:
        return require_safe_identifier(value, field_name="ExperimentPlan field")

    @model_validator(mode="after")
    def _validate_variant_and_order_consistency(self) -> ExperimentPlan:
        variant_ids = [item.variant_id for item in self.variants]
        if len(variant_ids) != len(set(variant_ids)):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                safe_message=f"plan {self.experiment_id!r} declares a duplicate variant_id",
            )
        if set(self.execution_order) != set(variant_ids) or len(self.execution_order) != len(
            variant_ids
        ):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.UNKNOWN_VARIANT,
                safe_message=(
                    f"plan {self.experiment_id!r} execution_order does not match "
                    "its own variant set exactly"
                ),
            )
        config_ref_ids = [item.variant_id for item in self.variant_configuration_digests]
        if len(config_ref_ids) != len(set(config_ref_ids)):
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER,
                safe_message=(
                    f"plan {self.experiment_id!r} declares a duplicate "
                    "variant_configuration_digests entry"
                ),
            )
        variant_id_set = set(variant_ids)
        for ref in self.variant_configuration_digests:
            if ref.variant_id not in variant_id_set:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.CONFIG_DIGEST_UNKNOWN_VARIANT,
                    safe_message=(
                        f"plan {self.experiment_id!r} variant_configuration_digests "
                        f"references unknown variant_id {ref.variant_id!r}"
                    ),
                )
        expected_digest = compute_plan_digest_sha512(
            experiment_id=self.experiment_id,
            case_id=self.case_id,
            case_revision=self.case_revision,
            case_digest_sha512=self.case_digest_sha512,
            variants=self.variants,
            execution_order=self.execution_order,
            budget=self.budget,
            variant_configuration_digests=self.variant_configuration_digests,
            execution_mode=self.execution_mode,
        )
        if self.plan_digest_sha512 != expected_digest:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.PLAN_DIGEST_MISMATCH,
                safe_message=(
                    f"plan {self.experiment_id!r} plan_digest_sha512 does not match "
                    "its own recomputed content digest"
                ),
            )
        return self

    def variant(self, variant_id: str) -> VariantDescriptor:
        for item in self.variants:
            if item.variant_id == variant_id:
                return item
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.UNKNOWN_VARIANT,
            safe_message=f"variant {variant_id!r} is not part of plan {self.experiment_id!r}",
        )

    def configuration_digest_for(self, variant_id: str) -> str | None:
        for ref in self.variant_configuration_digests:
            if ref.variant_id == variant_id:
                return ref.configuration_digest_sha512
        return None


def compute_plan_digest_sha512(
    *,
    experiment_id: str,
    case_id: str,
    case_revision: str,
    case_digest_sha512: str,
    variants: tuple[VariantDescriptor, ...],
    execution_order: tuple[str, ...],
    budget: ExperimentPlanBudget,
    variant_configuration_digests: tuple[VariantConfigurationRef, ...] = (),
    execution_mode: Literal["fixture", "production"] = "fixture",
) -> str:
    """WU-A A2: Dict order, wall-clock time, or Process-local values never
    affect this digest -- only the frozen Plan content itself, hashed
    through the shared Canonical JSON encoder."""

    def _component_payload(variant: VariantDescriptor) -> list[dict[str, str | None]]:
        entries: list[dict[str, str | None]] = [
            {
                "component_key": component.component_key.value,
                "selector_id": component.selector_id,
                "mode": component.mode,
            }
            for component in variant.components
        ]
        entries.sort(key=lambda entry: entry["component_key"] or "")
        return entries

    payload: dict[str, object] = {
        "experiment_id": experiment_id,
        "case_id": case_id,
        "case_revision": case_revision,
        "case_digest_sha512": case_digest_sha512,
        "variants": [
            {
                "variant_id": variant.variant_id,
                "components": _component_payload(variant),
            }
            for variant in sorted(variants, key=lambda item: item.variant_id)
        ],
        "execution_order": list(execution_order),
        "budget": budget.model_dump(mode="json"),
        "variant_configuration_digests": [
            {
                "variant_id": ref.variant_id,
                "configuration_digest_sha512": ref.configuration_digest_sha512,
            }
            for ref in sorted(variant_configuration_digests, key=lambda item: item.variant_id)
        ],
        "execution_mode": execution_mode,
    }
    return hashlib.sha512(canonical_json_bytes(payload)).hexdigest()


def build_experiment_plan(
    *,
    experiment_id: str,
    case_id: str,
    case_revision: str,
    case_digest_sha512: str,
    variants: tuple[VariantDescriptor, ...],
    execution_order: tuple[str, ...],
    budget: ExperimentPlanBudget | None = None,
    variant_configuration_digests: tuple[VariantConfigurationRef, ...] = (),
    execution_mode: Literal["fixture", "production"] = "fixture",
) -> ExperimentPlan:
    """The one supported construction path for `ExperimentPlan` outside of
    re-hydrating a persisted one: computes `plan_digest_sha512` from the
    supplied content so a caller can never hand-pick a mismatched digest
    (mirrors `StructuredOutputConstraint.from_schema()`'s own
    compute-then-construct pattern). `case_digest_sha512` itself is taken
    as given rather than recomputed here: `identity.py` does not import
    `dataset.py`'s `EvaluationCaseManifest`/`compute_case_digest_sha512`
    (that would invert the two modules' existing dependency direction,
    `dataset.py` -> `identity.py`) -- the caller (Application layer,
    which already imports both) computes `case_digest_sha512` via
    `dataset.compute_case_digest_sha512()` before calling this function."""

    resolved_budget = budget if budget is not None else ExperimentPlanBudget()
    digest = compute_plan_digest_sha512(
        experiment_id=experiment_id,
        case_id=case_id,
        case_revision=case_revision,
        case_digest_sha512=case_digest_sha512,
        variants=variants,
        execution_order=execution_order,
        budget=resolved_budget,
        variant_configuration_digests=variant_configuration_digests,
        execution_mode=execution_mode,
    )
    return ExperimentPlan(
        experiment_id=experiment_id,
        case_id=case_id,
        case_revision=case_revision,
        case_digest_sha512=case_digest_sha512,
        variants=variants,
        execution_order=execution_order,
        budget=resolved_budget,
        variant_configuration_digests=variant_configuration_digests,
        execution_mode=execution_mode,
        plan_digest_sha512=digest,
    )
