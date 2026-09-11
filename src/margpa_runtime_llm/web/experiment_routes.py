"""Local-private `/api/v7/experiment` routes (Phase 9-2, WU-A A4/WU-E E4;
R1-WU-03/04/05).

The Minimal Experiment screen's own Backend surface: Preset Case/Variant
listing, Plan creation, Run start (Fixture or, when `runtime.
production_turn_adapter` is wired, a real Production Turn -- the WU-06
bounded real-Model Gate is a distinct, separate script this router never
touches), Cancel, single-Run read, per-Experiment Run listing, and a
Comparison Report projection. `runtime.experiment_service is None`
degrades every route to `enabled=False`/404, exactly like every other
Optional `WebRuntime` feature in this codebase -- it never silently
no-ops.

R1-WU-05: `POST /runs` returns immediately (`state="running"`) and hands
the real Actor Call to `runtime.experiment_run_worker` -- it never blocks
the request on a potentially slow real Production Turn."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.adapters.experiment.semantic_fixture_adapter import (
    FIXTURE_GUARD_SHORT_CIRCUIT_MODE,
    FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
    FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE,
    FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE,
    FIXTURE_MAIN_NEGATED_CURRENT_MODE,
    execute_fixture_case,
    fixture_comparison_declarations,
)
from margpa_runtime_llm.modules.experiment.application.case_evaluator import evaluate_case_outcome
from margpa_runtime_llm.modules.experiment.application.comparison_service import (
    build_comparison_report,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
    VariantRunResult,
)
from margpa_runtime_llm.modules.experiment.application.production_turn_runner import (
    run_production_turn_variant,
)
from margpa_runtime_llm.modules.experiment.domain.case_pack import build_case_pack
from margpa_runtime_llm.modules.experiment.domain.comparison_declaration import (
    VariantComparisonDeclaration,
)
from margpa_runtime_llm.modules.experiment.domain.composition import ActorInvocationRecord
from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    EffectiveConfigurationSnapshot,
    find_mismatched_slots,
    overlay_variant_onto_snapshot,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import (
    EvaluationCaseManifest,
    compute_case_digest_sha512,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlan,
    ExperimentPlanBudget,
    StopPolicy,
    VariantConfigurationRef,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState, VariantRun
from margpa_runtime_llm.modules.experiment.domain.semantic_evidence import (
    CaseSemanticEvidence,
    semantic_metric_truth,
)
from margpa_runtime_llm.modules.runtime_model_control.application.provider_selection_controller import (  # noqa: E501
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
)

from .contracts import WebRuntime

EXPERIMENT_API_PREFIX = "/api/v7/experiment"


def _fixture_variant(
    variant_id: str, modes: dict[ComponentKey, str]
) -> VariantDescriptor:
    return VariantDescriptor(
        variant_id=variant_id,
        components=tuple(
            ComponentSelection(
                component_key=key,
                mode=modes.get(key, "off"),
            )
            for key in ComponentKey
        ),
    )

_PRESET_VARIANTS: tuple[VariantDescriptor, ...] = (
    VariantDescriptor(
        variant_id="baseline-all-off",
        components=tuple(
            ComponentSelection(component_key=key, mode="off") for key in ComponentKey
        ),
    ),
    VariantDescriptor(
        variant_id="judge-observe",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="observe"),),
    ),
    VariantDescriptor(
        variant_id="judge-enforce-repair",
        components=(
            ComponentSelection(
                component_key=ComponentKey.JUDGE,
                mode=FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
            ),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="enforce"),
        ),
    ),
    _fixture_variant("fixture-main-active", {ComponentKey.MAIN: "active"}),
    _fixture_variant("fixture-main-active-replica", {ComponentKey.MAIN: "active"}),
    _fixture_variant(
        "fixture-main-negated-current",
        {ComponentKey.MAIN: FIXTURE_MAIN_NEGATED_CURRENT_MODE},
    ),
    _fixture_variant("fixture-judge-observe", {ComponentKey.JUDGE: "observe"}),
    _fixture_variant("fixture-guard-enforce", {ComponentKey.GUARD: "enforce"}),
    _fixture_variant(
        "fixture-main-governance-strict",
        {ComponentKey.MAIN_GOVERNANCE: "strict"},
    ),
    _fixture_variant(
        "fixture-definition-manual",
        {ComponentKey.DEFINITION_SET: "manual"},
    ),
    _fixture_variant(
        "fixture-definition-static",
        {ComponentKey.DEFINITION_SET: "static"},
    ),
    _fixture_variant(
        "fixture-definition-dynamic",
        {ComponentKey.DEFINITION_SET: "dynamic"},
    ),
    _fixture_variant(
        "fixture-definition-manual-judge-request",
        {
            ComponentKey.JUDGE: FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
            ComponentKey.DEFINITION_SET: "manual",
        },
    ),
    _fixture_variant(
        "fixture-definition-manual-with-repair",
        {
            ComponentKey.JUDGE: FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
            ComponentKey.DEFINITION_SET: "manual",
            ComponentKey.REPAIR: "enforce",
        },
    ),
    _fixture_variant(
        "fixture-rag-relevant",
        {ComponentKey.MAIN: "active", ComponentKey.RAG: "relevant_hit"},
    ),
    _fixture_variant(
        "fixture-rag-no-hit",
        {ComponentKey.MAIN: "active", ComponentKey.RAG: "no_hit"},
    ),
    _fixture_variant(
        "fixture-rag-strict-no-hit",
        {ComponentKey.MAIN: "active", ComponentKey.RAG: "strict_no_hit"},
    ),
    _fixture_variant("fixture-repair-enforce", {ComponentKey.REPAIR: "enforce"}),
    _fixture_variant(
        "fixture-main-governance-request-no-repair",
        {ComponentKey.MAIN_GOVERNANCE: FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE},
    ),
    _fixture_variant(
        "fixture-main-governance-with-repair",
        {
            ComponentKey.MAIN_GOVERNANCE: FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE,
            ComponentKey.REPAIR: "enforce",
        },
    ),
    _fixture_variant(
        "fixture-judge-main-governance-with-repair",
        {
            ComponentKey.JUDGE: FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
            ComponentKey.MAIN_GOVERNANCE: FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE,
            ComponentKey.REPAIR: "enforce",
        },
    ),
    _fixture_variant(
        "fixture-presentation-strict",
        {ComponentKey.PRESENTATION: "strict_buffer"},
    ),
    _fixture_variant(
        "fixture-presentation-progressive",
        {ComponentKey.PRESENTATION: "progressive"},
    ),
    _fixture_variant("fixture-recording-active", {ComponentKey.RECORDING: "active"}),
    _fixture_variant(
        "fixture-manual-url-fail-closed",
        {ComponentKey.MAIN: FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE},
    ),
    _fixture_variant(
        "fixture-guard-short-circuit",
        {
            ComponentKey.MAIN: "active",
            ComponentKey.GUARD: FIXTURE_GUARD_SHORT_CIRCUIT_MODE,
        },
    ),
    VariantDescriptor(
        variant_id="fixture-judge-enforce-no-repair",
        components=(
            ComponentSelection(
                component_key=ComponentKey.JUDGE,
                mode=FIXTURE_JUDGE_REPAIR_REQUEST_MODE,
            ),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
        ),
    ),
    # R2-WU-01 (Handoff R2 SS4.1: "Fixture用PresetとProductionで実行不可能な
    # Presetを混同しない"): `baseline-all-off` declares `main` `mode="off"`,
    # which no live, functioning Main Turn Runtime can ever actually be --
    # `find_mismatched_slots()` correctly, permanently rejects it for
    # `execution_mode="production"`. These three exist specifically so a
    # Production Run has a genuinely satisfiable declared Configuration,
    # and map 1:1 onto Handoff R2 SS9.2's three named Real-Model-Gate
    # Variants ("Main Qwen only" / "+ Gemma Judge/Repair" / "+ Qwen3Guard").
    # R4-WU-01 (Handoff R4 SS4.1.1): each Production Preset now also pins
    # its own `selector_id` for every Role it actually engages -- ModeだけでなくProvider
    # Identityも明示する -- reusing the SAME Provider constants already
    # registered live in `runtime_model_control.application.
    # provider_selection_controller` (never a fresh, Experiment-Core-local
    # Provider identifier). A Role this Preset turns `off` never declares a
    # `selector_id` (Don't-care, WU-C C3): OFF has no Provider to pin.
    VariantDescriptor(
        variant_id="production-main-only-baseline",
        components=(
            ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id=QWEN_MAIN, mode="active"
            ),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="off"),
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
            ComponentSelection(component_key=ComponentKey.RECORDING, mode="off"),
        ),
    ),
    VariantDescriptor(
        variant_id="production-judge-repair-baseline",
        components=(
            ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id=QWEN_MAIN, mode="active"
            ),
            ComponentSelection(
                component_key=ComponentKey.JUDGE, selector_id=GEMMA_E2B_JUDGE, mode="enforce"
            ),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="off"),
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off"),
            ComponentSelection(component_key=ComponentKey.RECORDING, mode="off"),
        ),
    ),
    VariantDescriptor(
        variant_id="production-guard-baseline",
        components=(
            ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id=QWEN_MAIN, mode="active"
            ),
            ComponentSelection(
                component_key=ComponentKey.GUARD, selector_id=QWEN3_GUARD, mode="enforce"
            ),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
            ComponentSelection(component_key=ComponentKey.RECORDING, mode="off"),
        ),
    ),
)

_PRESET_VARIANT_LABELS: dict[str, str] = {
    "baseline-all-off": "Baseline (all components off)",
    "judge-observe": "Judge OBSERVE only",
    "judge-enforce-repair": "Judge + Repair ENFORCE",
    "fixture-main-active": "Fixture: Main active",
    "fixture-main-active-replica": "Fixture: Main active replication control",
    "fixture-main-negated-current": "Fixture: Main denies the Current Value",
    "fixture-judge-observe": "Fixture: Judge OBSERVE",
    "fixture-guard-enforce": "Fixture: Guard ENFORCE",
    "fixture-main-governance-strict": "Fixture: Main Governance strict",
    "fixture-definition-manual": "Fixture: Definition routing manual",
    "fixture-definition-static": "Fixture: Definition routing static",
    "fixture-definition-dynamic": "Fixture: Definition routing dynamic",
    "fixture-definition-manual-judge-request": "Fixture: Definition manual, Judge requests repair",
    "fixture-definition-manual-with-repair": "Fixture: Definition repair propagation",
    "fixture-rag-relevant": "Fixture: RAG relevant hit",
    "fixture-rag-no-hit": "Fixture: RAG NO_HIT with Main call",
    "fixture-rag-strict-no-hit": "Fixture: Strict NO_HIT Call 0",
    "fixture-repair-enforce": "Fixture: Repair ENFORCE without requester",
    "fixture-main-governance-request-no-repair": (
        "Fixture: Main Governance requests repair, Repair off"
    ),
    "fixture-main-governance-with-repair": "Fixture: Main Governance requests repair",
    "fixture-judge-main-governance-with-repair": "Fixture: Judge + Main Governance request repair",
    "fixture-presentation-strict": "Fixture: Strict Buffer",
    "fixture-presentation-progressive": "Fixture: Progressive",
    "fixture-recording-active": "Fixture: Recording active",
    "fixture-manual-url-fail-closed": "Fixture: Manual URL fail-closed Call 0",
    "fixture-guard-short-circuit": "Fixture: Guard short-circuit Call 0",
    "fixture-judge-enforce-no-repair": "Fixture: Judge ENFORCE, Repair ablated",
    "production-main-only-baseline": "Production: Main only",
    "production-judge-repair-baseline": "Production: Main + Judge/Repair ENFORCE",
    "production-guard-baseline": "Production: Main + Guard ENFORCE",
}


@dataclass(frozen=True, slots=True)
class ExperimentWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def experiment_error_response(error: ExperimentWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _disabled_error() -> ExperimentWebError:
    return ExperimentWebError(
        503,
        "experiment_disabled",
        "The Experiment runtime is not enabled in this deployment.",
    )


_NOT_FOUND_SHAPED_CODES = frozenset({"not_found", "unknown_variant"})


def _core_error_to_web_error(
    exc: ExperimentCoreError, *, not_found_status: int = 409
) -> ExperimentWebError:
    status_code = 404 if exc.code.value in _NOT_FOUND_SHAPED_CODES else not_found_status
    return ExperimentWebError(status_code, exc.code.value, exc.safe_message)


class _ExperimentContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ExperimentComponentSelectionResponse(_ExperimentContract):
    component_key: str
    selector_id: str | None = None
    mode: str | None = None


class ExperimentVariantPresetResponse(_ExperimentContract):
    variant_id: str
    label: str
    components: tuple[ExperimentComponentSelectionResponse, ...]


class ExperimentCasePresetResponse(_ExperimentContract):
    case_id: str
    revision: str
    input: str
    requires_human_review: bool


class ExperimentPresetsResponse(_ExperimentContract):
    enabled: bool
    cases: tuple[ExperimentCasePresetResponse, ...] = ()
    variants: tuple[ExperimentVariantPresetResponse, ...] = ()


class CreatePlanRequest(_ExperimentContract):
    experiment_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    variant_ids: tuple[str, ...] = Field(min_length=1)
    max_variant_runs: int | None = Field(default=None, gt=0)
    deadline_ms: int | None = Field(default=None, gt=0)
    stop_policy: StopPolicy | None = None
    execution_mode: Literal["fixture", "production"] = "fixture"
    """R3-WU-01 (IR-P9-2-R2-07 MAJOR fix): Frozen Identity, decided ONCE
    here at Plan-creation time -- `StartRunRequest` no longer carries its
    own `execution_mode` at all, so the SAME Plan/Variant can never be run
    as both Fixture and Production."""


class ExperimentVariantConfigurationResponse(_ExperimentContract):
    """R3-WU-01/05 (IR-P9-2-R2-01/03 fix): this Variant's own "Desired
    Configuration" -- its declared Components overlaid onto whatever was
    Live at Plan-creation time (`config_snapshot.overlay_variant_onto_
    snapshot()`). Deliberately never called "Frozen" here: it is a
    pre-Run planning reference the User can read to know what to set
    ordinary Settings to before starting THIS Variant's Run -- a Run's own
    genuine Frozen Configuration (what Live actually WAS at that Run's own
    start) is a separate field on `VariantRunResponse`/`ExperimentCompar
    isonRowResponse`, captured fresh, per-Run, not reused from here."""

    variant_id: str
    desired_configuration_digest_sha512: str | None = None
    desired_components: tuple[ExperimentComponentSelectionResponse, ...] = ()


class ExperimentPlanResponse(_ExperimentContract):
    experiment_id: str
    case_id: str
    case_revision: str
    variant_ids: tuple[str, ...]
    plan_digest_sha512: str
    execution_mode: Literal["fixture", "production"] = "fixture"
    variant_configurations: tuple[ExperimentVariantConfigurationResponse, ...] = ()


class StartRunRequest(_ExperimentContract):
    """R3-WU-01 (IR-P9-2-R2-07 MAJOR fix): no `execution_mode` field here
    at all -- it is Frozen on the Plan at creation time
    (`CreatePlanRequest.execution_mode`) and read from `plan.execution_
    mode` in `start_run()` below, never chosen per-Run."""

    experiment_id: str = Field(min_length=1)
    variant_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    request_id: str | None = None


class ActorInvocationResponse(_ExperimentContract):
    """R3-WU-02 (IR-P9-2-R2-04 fix): a genuine three-state DTO, mirroring
    `domain.composition.ActorInvocationRecord` -- `called=None` (JSON
    `null`) means this Round's Evidence source genuinely cannot tell
    whether this Component was called; a Frontend renders that as
    Unavailable/`—`, never as a confirmed `false`/`0`."""

    component_key: str
    called: bool | None
    outcome: str
    mutation_count: int | None
    evidence_count: int | None
    authority_exercised: bool | None


class VariantRunResponse(_ExperimentContract):
    run_id: str
    experiment_id: str
    variant_id: str
    request_id: str
    execution_mode: Literal["fixture", "production"]
    state: str
    generation: int
    started_at: str | None = None
    completed_at: str | None = None
    failure_reason: str | None = None
    fixture_only: bool = True
    """R2-WU-04 (IR-P9-2-R1-07 fix): now a plain derived alias of
    `execution_mode != "production"` -- kept only so an existing Frontend
    reader is not broken by this field's removal. `execution_mode` itself
    is the authoritative, Frozen-at-Run-start field; unlike R1, this is
    never inferred from whether Raw Evidence happens to exist yet."""
    frozen_configuration_digest_sha512: str | None = None
    """R3-WU-01/05 (IR-P9-2-R2-03 fix): the digest of this Run's OWN
    genuine Frozen Configuration Snapshot -- captured fresh, LIVE, at
    THIS Run's own Call-0 check, never the Plan-level "Desired" digest
    (`ExperimentVariantConfigurationResponse`, a pre-Run planning
    reference). Always `None` for a Fixture Run (Fixture never reads Live
    Configuration) and for a Production Run still `planned`/`running`
    whose Call-0 check has not yet completed."""


class VariantRunResultResponse(_ExperimentContract):
    run: VariantRunResponse
    invocations: tuple[ActorInvocationResponse, ...] = ()
    production_request_id: str | None = None
    """The REAL `ConversationGenerationSession.request_id` Phase 9-1
    itself assigned to this Turn -- a distinct identifier from `run.
    request_id` (the Experiment-side Request identity assigned at Run
    start), present only for an `execution_mode="production"` Run."""
    assistant_content: str | None = None
    final_disposition: str | None = None


class ExperimentRunListResponse(_ExperimentContract):
    experiment_id: str
    runs: tuple[VariantRunResponse, ...] = ()


class ExperimentEvaluationObservationResponse(_ExperimentContract):
    evaluator_kind: str
    evaluator_identity: str
    outcome: str
    score: float | None = None
    reason: str | None = None


class ExperimentMetricResponse(_ExperimentContract):
    runtime_state: str
    latency_ms: int | None = None
    call_count: int | None = None
    unknown_component_count: int | None = None
    """R3-WU-02 (IR-P9-2-R2-04 fix): how many Components this Run's own
    Evidence reports `called=None` for -- `call_count` above is a lower
    bound only (CONFIRMED calls), never silently inflated or left
    ambiguous by folding Unknown into either `0` or a total."""
    deviation_count: int | None = None
    repair_adopted: bool | None = None
    false_positive: bool | None = None
    false_grounding: bool | None = None
    correction_acceptance: bool | None = None


class ExperimentComparisonRowResponse(_ExperimentContract):
    variant_id: str
    run_id: str
    execution_mode: Literal["fixture", "production"] | None = None
    runtime_state: str
    metric: ExperimentMetricResponse | None = None
    observations: tuple[ExperimentEvaluationObservationResponse, ...] = ()
    failure_reason: str | None = None
    raw_evidence_pointer: str
    variant_components: tuple[ExperimentComponentSelectionResponse, ...] = ()
    frozen_configuration_digest_sha512: str | None = None
    """R3-WU-01/05 (IR-P9-2-R2-03 fix): this ROW's own Run's genuine
    Frozen Configuration digest (captured fresh at that Run's own Call-0
    check) -- lets a Comparison reader see, side by side, that two
    Production Variant Runs in the same Experiment really executed under
    two DIFFERENT Live Configurations, never the same one copied across
    rows."""
    semantic_evidence: CaseSemanticEvidence | None = None


class ExperimentComparisonResponse(_ExperimentContract):
    experiment_id: str
    case_id: str
    case_revision: str
    variant_relationships: tuple[VariantComparisonDeclaration, ...] = ()
    rows: tuple[ExperimentComparisonRowResponse, ...] = ()


def _frozen_configuration_digest_for(
    service: ExperimentService, run_id: str
) -> str | None:
    """R3-WU-01/05 (IR-P9-2-R2-03 fix): reads back a Run's own genuine
    Frozen Configuration Snapshot digest (persisted, fresh, at that Run's
    own Call-0 check) -- `None` for a Fixture Run, or a Production Run
    whose Call-0 check has not yet persisted one."""

    snapshot = service.store.load_run_configuration_snapshot(run_id)
    if snapshot is None:
        return None
    digest = snapshot.get("configuration_digest_sha512")
    return digest if isinstance(digest, str) else None


def _run_response(
    run: VariantRun, *, frozen_configuration_digest_sha512: str | None = None
) -> VariantRunResponse:
    """R2-WU-04 (IR-P9-2-R1-07 fix): `run.execution_mode` is Frozen
    Identity, set once at `ExperimentService.start_run()` and never
    inferred from whether Raw Evidence happens to exist yet -- a `running`
    Production Run (no Raw Evidence saved yet) correctly keeps reporting
    `execution_mode="production"`, never falls back to looking like a
    Fixture Run the way R1's `_fixture_only_from_evidence()` did."""

    return VariantRunResponse(
        run_id=run.run_id,
        experiment_id=run.experiment_id,
        variant_id=run.variant_id,
        request_id=run.request_id,
        execution_mode=run.execution_mode,
        state=run.state.value,
        generation=run.generation,
        started_at=run.started_at,
        completed_at=run.completed_at,
        failure_reason=run.failure_reason,
        fixture_only=run.execution_mode != "production",
        frozen_configuration_digest_sha512=frozen_configuration_digest_sha512,
    )


def _invocation_response(record: ActorInvocationRecord) -> ActorInvocationResponse:
    return ActorInvocationResponse(
        component_key=record.component_key.value,
        called=record.called,
        outcome=record.outcome,
        mutation_count=record.mutation_count,
        evidence_count=record.evidence_count,
        authority_exercised=record.authority_exercised,
    )


def _result_response(
    service: ExperimentService, result: VariantRunResult
) -> VariantRunResultResponse:
    invocations: tuple[ActorInvocationResponse, ...] = ()
    production_request_id: str | None = None
    assistant_content: str | None = None
    final_disposition: str | None = None
    if result.raw_evidence is not None:
        entries_raw = result.raw_evidence.get("invocations", [])
        entries: list[object] = entries_raw if isinstance(entries_raw, list) else []
        invocations = tuple(ActorInvocationResponse.model_validate(entry) for entry in entries)
        if result.raw_evidence.get("execution_mode") == "production":
            raw_request_id = result.raw_evidence.get("request_id")
            production_request_id = raw_request_id if isinstance(raw_request_id, str) else None
            raw_content = result.raw_evidence.get("assistant_content")
            assistant_content = raw_content if isinstance(raw_content, str) else None
            raw_disposition = result.raw_evidence.get("final_disposition")
            final_disposition = raw_disposition if isinstance(raw_disposition, str) else None
    return VariantRunResultResponse(
        run=_run_response(
            result.run,
            frozen_configuration_digest_sha512=_frozen_configuration_digest_for(
                service, result.run.run_id
            ),
        ),
        invocations=invocations,
        production_request_id=production_request_id,
        assistant_content=assistant_content,
        final_disposition=final_disposition,
    )


def _resolve_frozen_case(plan: ExperimentPlan) -> EvaluationCaseManifest:
    """R1-WU-04 (IR-P9-2-02/05 fix): re-derives the Case by `case_id` from
    the LIVE Case Pack and verifies its recomputed content Digest still
    matches the Plan's own frozen `case_digest_sha512` -- if the Case Pack
    changed since this Plan was created, this is a Typed Reject BEFORE any
    Actor is ever invoked, never a silent use of a now-different Case
    under the same `case_id`."""

    case = next((item for item in build_case_pack() if item.case_id == plan.case_id), None)
    if case is None or compute_case_digest_sha512(case) != plan.case_digest_sha512:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.CASE_DIGEST_MISMATCH,
            safe_message=(
                f"case_id {plan.case_id!r} no longer matches the Case Pack content "
                "this plan's case_digest_sha512 was frozen against"
            ),
        )
    return case


def _service(request: Request) -> ExperimentService | None:
    runtime: WebRuntime = request.app.state.runtime
    return runtime.experiment_service


def _invocation_payload(item: ActorInvocationRecord) -> dict[str, object]:
    return {
        "component_key": item.component_key.value,
        "called": item.called,
        "outcome": item.outcome,
        "mutation_count": item.mutation_count,
        "evidence_count": item.evidence_count,
        "authority_exercised": item.authority_exercised,
    }


def _metric_payload(
    *,
    run_id: str,
    case_id: str,
    runtime_state: str,
    invocations: list[dict[str, object]],
    repair_adopted: bool | None,
    semantic_evidence: CaseSemanticEvidence | None = None,
) -> dict[str, object]:
    """R1-WU-04 / R2-WU-02 (IR-P9-2-R1-02 fix): a minimal, real Metric
    derived from the same Invocations already recorded, plus a
    `repair_adopted` the CALLER resolves -- never re-derived here from
    "was Repair called" (a Called-but-rejected Repair is not Adopted;
    see the two call sites below for how each Execution Mode resolves
    it).

    R3-WU-02 (IR-P9-2-R2-04 fix): `call_count` counts a CONFIRMED
    `called=True` only -- a `called=None` (not_observed) Component is
    never silently folded into the same `0` a genuine confirmed-off
    Component reports; `unknown_component_count` carries that fact
    instead, so the two situations are never displayed identically."""

    call_count = sum(1 for item in invocations if item.get("called") is True)
    unknown_component_count = sum(1 for item in invocations if item.get("called") is None)
    false_positive: bool | None = None
    false_grounding: bool | None = None
    correction_acceptance: bool | None = None
    if semantic_evidence is not None:
        false_positive, false_grounding, correction_acceptance = semantic_metric_truth(
            semantic_evidence
        )
    return {
        "run_id": run_id,
        "case_id": case_id,
        "runtime_state": runtime_state,
        "call_count": call_count,
        "unknown_component_count": unknown_component_count,
        "repair_adopted": repair_adopted,
        "false_positive": false_positive,
        "false_grounding": false_grounding,
        "correction_acceptance": correction_acceptance,
    }


def create_experiment_router() -> APIRouter:
    router = APIRouter(prefix=EXPERIMENT_API_PREFIX)

    @router.get("/presets", response_model=ExperimentPresetsResponse)
    async def get_presets(request: Request) -> ExperimentPresetsResponse:
        if _service(request) is None:
            return ExperimentPresetsResponse(enabled=False)
        return ExperimentPresetsResponse(
            enabled=True,
            cases=tuple(
                ExperimentCasePresetResponse(
                    case_id=case.case_id,
                    revision=case.revision,
                    input=case.input,
                    requires_human_review=case.requires_human_review,
                )
                for case in build_case_pack()
            ),
            variants=tuple(
                ExperimentVariantPresetResponse(
                    variant_id=variant.variant_id,
                    label=_PRESET_VARIANT_LABELS.get(variant.variant_id, variant.variant_id),
                    components=tuple(
                        ExperimentComponentSelectionResponse(
                            component_key=component.component_key.value,
                            selector_id=component.selector_id,
                            mode=component.mode,
                        )
                        for component in variant.components
                    ),
                )
                for variant in _PRESET_VARIANTS
            ),
        )

    @router.post("/plans", response_model=ExperimentPlanResponse, status_code=201)
    async def create_plan(request: Request, body: CreatePlanRequest) -> ExperimentPlanResponse:
        service = _service(request)
        if service is None:
            raise _disabled_error()
        runtime: WebRuntime = request.app.state.runtime
        case = next((item for item in build_case_pack() if item.case_id == body.case_id), None)
        if case is None:
            raise ExperimentWebError(404, "unknown_case_id", f"Unknown case_id: {body.case_id!r}")
        variants = tuple(
            variant for variant in _PRESET_VARIANTS if variant.variant_id in body.variant_ids
        )
        if len(variants) != len(set(body.variant_ids)):
            raise ExperimentWebError(
                404, "unknown_variant_id", "One or more variant_ids are unknown"
            )
        # R3-WU-01 (IR-P9-2-R2-01 CRITICAL fix): ONE Live read at Plan-
        # creation time (`base`), but `overlay_variant_onto_snapshot()` is
        # called ONCE PER VARIANT -- each Variant's own declared Components
        # are overlaid onto `base` independently, so two Variants that
        # declare different slots differently get DIFFERENT "Desired"
        # digests. This is what makes the Controller's own confirmed
        # CRITICAL finding ("同一Live Snapshot Digestを...全Variantへ複製
        # して解決扱いにしない") structurally impossible from here on --
        # R2's own version read Live ONCE and copied the SAME digest onto
        # every Variant's `VariantConfigurationRef`, which is exactly what
        # made running two different Production Variants against the same
        # Plan impossible. This Desired value is a pre-Run planning
        # reference ONLY (surfaced on the Response below for the UI) -- it
        # is never compared against Live again at Run-start; the real
        # Call-0 gate is `find_mismatched_slots()` against a FRESH Live
        # read at THAT Run's own start (`start_run()` below), and a Run's
        # own genuine Frozen Configuration is captured there too, fresh,
        # never reused from this Desired value. Stays empty (R1's own
        # observed gap) only when no `live_configuration_reader` is wired
        # at all.
        variant_configuration_digests: tuple[VariantConfigurationRef, ...] = ()
        desired_snapshots: dict[str, EffectiveConfigurationSnapshot] = {}
        if runtime.live_configuration_reader is not None:
            live_at_plan_creation = runtime.live_configuration_reader.snapshot()
            for variant in variants:
                desired = overlay_variant_onto_snapshot(
                    variant=variant, base=live_at_plan_creation
                )
                desired_snapshots[variant.variant_id] = desired
            variant_configuration_digests = tuple(
                VariantConfigurationRef(
                    variant_id=variant.variant_id,
                    configuration_digest_sha512=desired_snapshots[
                        variant.variant_id
                    ].configuration_digest_sha512,
                )
                for variant in variants
            )
        try:
            plan = build_experiment_plan(
                experiment_id=body.experiment_id,
                case_id=case.case_id,
                case_revision=case.revision,
                case_digest_sha512=compute_case_digest_sha512(case),
                variants=variants,
                execution_order=tuple(variant.variant_id for variant in variants),
                budget=ExperimentPlanBudget(
                    max_variant_runs=body.max_variant_runs,
                    deadline_ms=body.deadline_ms,
                    stop_policy=body.stop_policy,
                ),
                variant_configuration_digests=variant_configuration_digests,
                execution_mode=body.execution_mode,
            )
            service.create_plan_with_desired_configurations(
                plan=plan,
                desired_configurations=desired_snapshots,
            )
        except ExperimentCoreError as exc:
            raise _core_error_to_web_error(exc) from exc
        return ExperimentPlanResponse(
            experiment_id=plan.experiment_id,
            case_id=plan.case_id,
            case_revision=plan.case_revision,
            variant_ids=tuple(variant.variant_id for variant in plan.variants),
            plan_digest_sha512=plan.plan_digest_sha512,
            execution_mode=plan.execution_mode,
            variant_configurations=tuple(
                ExperimentVariantConfigurationResponse(
                    variant_id=variant.variant_id,
                    desired_configuration_digest_sha512=plan.configuration_digest_for(
                        variant.variant_id
                    ),
                    desired_components=(
                        tuple(
                            ExperimentComponentSelectionResponse(
                                component_key=component.component_key.value,
                                selector_id=component.selector_id,
                                mode=component.mode,
                            )
                            for component in (
                                desired_snapshots[variant.variant_id].main,
                                desired_snapshots[variant.variant_id].judge,
                                desired_snapshots[variant.variant_id].guard,
                                desired_snapshots[variant.variant_id].main_governance,
                                desired_snapshots[variant.variant_id].definition_set,
                                desired_snapshots[variant.variant_id].rag,
                                desired_snapshots[variant.variant_id].repair,
                                desired_snapshots[variant.variant_id].recording,
                                desired_snapshots[variant.variant_id].presentation,
                            )
                        )
                        if variant.variant_id in desired_snapshots
                        else ()
                    ),
                )
                for variant in plan.variants
            ),
        )

    @router.post("/runs", response_model=VariantRunResponse, status_code=202)
    async def start_run(request: Request, body: StartRunRequest) -> VariantRunResponse:
        service = _service(request)
        runtime: WebRuntime = request.app.state.runtime
        worker = runtime.experiment_run_worker
        if service is None or worker is None:
            raise _disabled_error()
        request_id = body.request_id if body.request_id is not None else uuid.uuid4().hex
        try:
            # R1-WU-02 (IR-P9-2-03 fix): the Variant to execute is read
            # back from the persisted, Frozen `ExperimentPlan` -- never
            # re-searched from the module-level `_PRESET_VARIANTS` (Plan-
            # creation INPUT only, per Handoff R1-WU-02: "PresetはPlan
            # 作成時のInputに限定し、実行時はFrozen Planからのみ読む").
            # Resolved BEFORE `start_run()` so a Run object is never even
            # created for a Variant this Plan's own digest doesn't cover.
            plan = service.store.load_plan(body.experiment_id)
            if plan is None:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.NOT_FOUND,
                    safe_message=f"experiment_id {body.experiment_id!r} has no Plan",
                )
            variant = plan.variant(body.variant_id)
            # R1-WU-04 (IR-P9-2-02/05 fix): the real Case Input a
            # Production Turn needs, re-verified against this Plan's own
            # frozen Case Digest before any Actor is invoked.
            case = _resolve_frozen_case(plan)
            # R3-WU-01 (IR-P9-2-R2-01 CRITICAL fix): the Call-0 gate is
            # now `find_mismatched_slots()` ALONE, against a snapshot read
            # FRESH, right now, at THIS Run's own start -- never a whole-
            # Snapshot digest-equality check against the Plan's own
            # "Desired" value. That whole-digest check is exactly the
            # mechanism the Controller's Independent Review confirmed
            # makes running two different Production Variants against the
            # same Plan structurally impossible: it required Live to stay
            # bit-for-bit IDENTICAL, in every slot (including ones this
            # Variant never declares), across every Variant's own Run --
            # which is precisely what the User must be free to change
            # BETWEEN two Variant Runs of the same Plan (Handoff R3 SS4.2
            # Option A: the User explicitly re-configures ordinary
            # Settings between Runs). `find_mismatched_slots()` only ever
            # checks the slots THIS Variant itself declares -- a drift in
            # an undeclared slot never blocks it, by design.
            if plan.execution_mode == "production":
                if runtime.production_turn_adapter is None:
                    raise ExperimentWebError(
                        503,
                        "production_adapter_unavailable",
                        "The Production Turn Adapter is not available in this deployment.",
                    )
                if runtime.live_configuration_reader is None:
                    raise ExperimentCoreError(
                        code=ExperimentCoreErrorCode.LIVE_CONFIG_UNAVAILABLE,
                        safe_message="No Live Configuration Reader is wired in this deployment.",
                    )
                # R4-WU-02 (Handoff R4 SS5.1): this is an ADVISORY, fast
                # synchronous pre-check only -- it lets an obviously
                # impossible Preset (or an already-drifted Live) 409
                # immediately, before a Run object or a Worker slot is
                # even spent on it. It is deliberately NOT the
                # authoritative gate any more, and never persists a
                # Frozen Snapshot: this read happens with no Lease held
                # at all, arbitrarily long before the real Actor Call
                # might actually run (this Run could still be queued
                # behind another one), so nothing about it can be trusted
                # atomic. The REAL, authoritative Live-match-then-freeze
                # happens again, unconditionally, strictly INSIDE the
                # Configuration Lease's own protected window, immediately
                # before the real Actor Call (`_invoke_production` below).
                advisory_mismatch = find_mismatched_slots(
                    variant=variant, snapshot=runtime.live_configuration_reader.snapshot()
                )
                if advisory_mismatch:
                    raise ExperimentCoreError(
                        code=ExperimentCoreErrorCode.LIVE_CONFIG_MISMATCH,
                        safe_message=(
                            f"variant_id {body.variant_id!r} declares a Configuration Live "
                            "cannot currently satisfy for slot(s): "
                            f"{', '.join(key.value for key in advisory_mismatch)}"
                        ),
                    )
            run = service.start_run(
                experiment_id=body.experiment_id,
                variant_id=body.variant_id,
                run_id=body.run_id,
                request_id=request_id,
            )
        except ExperimentCoreError as exc:
            raise _core_error_to_web_error(exc) from exc

        # R1-WU-05: the Actor Call itself never runs on this request's own
        # Thread -- `start_run()` above already persisted `running`, and
        # this method returns immediately without waiting for `invoke()`.
        # R4-WU-02: `frozen_configuration_digest_sha512` is always `None`
        # in THIS synchronous response for a production Run now -- the
        # genuine Frozen Configuration is only known once the Lease-
        # protected async Task below actually runs (`GET /runs/{run_id}`
        # already anticipated this: "still planned/running... Call-0
        # check has not yet completed").
        if plan.execution_mode == "production":
            adapter = runtime.production_turn_adapter
            live_configuration_reader = runtime.live_configuration_reader
            lease = runtime.experiment_configuration_lease
            if adapter is None or live_configuration_reader is None:
                raise _disabled_error()
            cancel_target: dict[str, str] = {}

            def _register_real_request_id(real_request_id: str) -> None:
                cancel_target["real_request_id"] = real_request_id

            def _cancel() -> None:
                real_id = cancel_target.get("real_request_id")
                if real_id is not None:
                    runtime.conversation.cancel(real_id)

            def _call_zero_invocations() -> list[dict[str, object]]:
                """R4-WU-02: a genuine Typed Call 0 -- Main/Judge/Guard/
                Repair are CONFIRMED never invoked (`called=False`, exact
                zero Mutation/Evidence/Authority), mirroring the same
                shape `run_production_turn_variant()`'s own projection
                produces for a real Turn; the 5 always-unmodeled
                Components stay `called=None`/`"not_observed"`, unchanged."""

                confirmed_absent = (
                    ComponentKey.MAIN,
                    ComponentKey.JUDGE,
                    ComponentKey.GUARD,
                    ComponentKey.REPAIR,
                )
                unmodeled = (
                    ComponentKey.MAIN_GOVERNANCE,
                    ComponentKey.DEFINITION_SET,
                    ComponentKey.RAG,
                    ComponentKey.RECORDING,
                    ComponentKey.PRESENTATION,
                )
                return [
                    _invocation_payload(
                        ActorInvocationRecord(component_key=key, called=False, outcome="call_zero")
                    )
                    for key in confirmed_absent
                ] + [
                    _invocation_payload(
                        ActorInvocationRecord(
                            component_key=key,
                            called=None,
                            mutation_count=None,
                            evidence_count=None,
                            authority_exercised=None,
                            outcome="not_observed",
                        )
                    )
                    for key in unmodeled
                ]

            def _call_zero_result(
                reason: str,
            ) -> tuple[RunState, dict[str, object] | None, str | None]:
                invocations = _call_zero_invocations()
                raw_evidence: dict[str, object] = {
                    "execution_mode": "production",
                    "invocations": invocations,
                    "metric": _metric_payload(
                        run_id=run.run_id,
                        case_id=case.case_id,
                        runtime_state=RunState.FAILED.value,
                        invocations=invocations,
                        repair_adopted=None,
                    ),
                }
                return (RunState.FAILED, raw_evidence, reason)

            def _expected_executed(key: ComponentKey, live_selector_id: str | None) -> str | None:
                declared = variant.component(key)
                if declared is not None and declared.selector_id is not None:
                    return declared.selector_id
                return live_selector_id

            def _invoke_production() -> tuple[RunState, dict[str, object] | None, str | None]:
                # R4-WU-02 (Handoff R4 SS5.1, Hard Assert): "Lease取得不能
                # ...なら無保護実行へFallbackせずTyped Call 0とする" --
                # `run_worker._task()` only ever calls this closure AFTER
                # its own authoritative Terminal Check passes and (when
                # `lease` was given to `submit()`) has already acquired
                # it; if no Lease was wired for this Production
                # Composition at all, running unprotected is never an
                # acceptable fallback.
                if lease is None:
                    return _call_zero_result(
                        ExperimentCoreErrorCode.CONFIGURATION_LEASE_UNAVAILABLE.value
                    )
                # R4-WU-02 (Handoff R4 SS5.1's TOCTOU fix): the FINAL Live
                # read and Variant match happen HERE -- strictly inside
                # the Configuration Lease's own protected window (already
                # held by the time this closure runs) -- immediately
                # before the real Actor Call, with no gap in between for
                # a Settings change to land. This is now the ONE
                # authoritative gate; the earlier pre-submit check above
                # is advisory only.
                final_live_snapshot = live_configuration_reader.snapshot()
                mismatched_slots = find_mismatched_slots(
                    variant=variant, snapshot=final_live_snapshot
                )
                if mismatched_slots:
                    return _call_zero_result(ExperimentCoreErrorCode.LIVE_CONFIG_MISMATCH.value)
                frozen_config_digest = final_live_snapshot.configuration_digest_sha512
                # R4-WU-01 (Handoff R4 SS4.1.5/4.1.6): Provider Identity
                # (Configured/Active/Artifact-Digest, Live-read a second
                # time, still inside this same Lease window) plus this
                # Variant's own "Expected Executed" selector per Role, and
                # a Correlation block so this Snapshot is traceable back
                # to its own Case/Plan/Variant/Run identities without any
                # Digest circularity.
                live_provider_identity = live_configuration_reader.provider_identity()
                provider_identity = live_provider_identity.with_expected_executed(
                    main=_expected_executed(
                        ComponentKey.MAIN, final_live_snapshot.main.selector_id
                    ),
                    judge=_expected_executed(
                        ComponentKey.JUDGE, final_live_snapshot.judge.selector_id
                    ),
                    guard=_expected_executed(
                        ComponentKey.GUARD, final_live_snapshot.guard.selector_id
                    ),
                )
                service.store.save_run_configuration_snapshot(
                    run.run_id,
                    {
                        **final_live_snapshot.model_dump(mode="json"),
                        "provider_identity": provider_identity.model_dump(mode="json"),
                        "correlation": {
                            "run_id": run.run_id,
                            "experiment_id": run.experiment_id,
                            "variant_id": run.variant_id,
                            "case_digest_sha512": plan.case_digest_sha512,
                            "plan_digest_sha512": plan.plan_digest_sha512,
                        },
                    },
                )
                execution = run_production_turn_variant(
                    port=adapter, user_input=case.input, on_request_id=_register_real_request_id
                )
                observation = execution.observation
                invocations = [_invocation_payload(item) for item in execution.invocations]
                if observation.main_outcome == "cancelled":
                    target_state = RunState.CANCELLED
                    failure_reason = None
                elif observation.main_outcome == "failed":
                    target_state = RunState.FAILED
                    failure_reason = observation.failure_reason or "production_turn_failed"
                else:
                    target_state = RunState.COMPLETED
                    failure_reason = None
                # R2-WU-01 (Handoff R2 SS4.2's bounded "Lease" Fallback),
                # now largely a defense-in-depth check rather than the
                # primary protection (R4-WU-02's Lease itself blocks every
                # gated Settings-mutation route for this whole window):
                # re-verified immediately after the real Turn completes --
                # if Live no longer matches what this Run was frozen
                # against, a claimed `COMPLETED` is downgraded to Typed
                # `FAILED`, since nothing observed can be vouched for
                # under a single, stable Configuration throughout.
                if target_state is RunState.COMPLETED:
                    after_snapshot = live_configuration_reader.snapshot()
                    if after_snapshot.configuration_digest_sha512 != frozen_config_digest:
                        target_state = RunState.FAILED
                        failure_reason = "live_config_changed_during_run"
                raw_evidence: dict[str, object] = {
                    "execution_mode": "production",
                    "request_id": observation.request_id,
                    "final_disposition": observation.final_disposition,
                    "assistant_content": observation.assistant_content,
                    "invocations": invocations,
                    "metric": _metric_payload(
                        run_id=run.run_id,
                        case_id=case.case_id,
                        runtime_state=target_state.value,
                        invocations=invocations,
                        repair_adopted=observation.repair_adopted,
                    ),
                }
                return (target_state, raw_evidence, failure_reason)

            worker.submit(
                service=service,
                run=run,
                deadline_ms=plan.budget.deadline_ms,
                invoke=_invoke_production,
                cancel=_cancel,
                # R4-WU-02: held for the duration of the real Actor Call
                # AND the final Live-match-then-freeze immediately
                # preceding it (both now live inside `_invoke_production`
                # itself) -- never for this Run's whole Queued-to-Terminal
                # lifetime. `_invoke_production` itself Typed-Call-0s when
                # `lease` is `None`, so passing it through unconditionally
                # here never means "run unprotected."
                lease=lease,
            )
        else:

            def _invoke_fixture() -> tuple[RunState, dict[str, object] | None, str | None]:
                fixture = execute_fixture_case(case=case, variant=variant)
                execution_result = fixture.execution
                invocations = [_invocation_payload(item) for item in execution_result.invocations]
                # Fixture Actors are a deliberate, deterministic
                # simulation (`FixtureActor.invoke()` always reports
                # `outcome="completed"`) -- unlike a real Production
                # Repair, "Repair was called" and "Repair's output was
                # Adopted" are the same fact in this simulation, so
                # inferring `repair_adopted` from "called" here is not
                # the False-Evidence gap R2-WU-02 fixed for Production.
                repair_called = any(
                    item.get("component_key") == ComponentKey.REPAIR.value and item.get("called")
                    for item in invocations
                )
                raw_evidence: dict[str, object] = {
                    "execution_mode": "fixture",
                    "invocations": invocations,
                    "semantic_evidence": fixture.semantic_evidence.model_dump(mode="json"),
                    "metric": _metric_payload(
                        run_id=run.run_id,
                        case_id=case.case_id,
                        runtime_state=RunState.COMPLETED.value,
                        invocations=invocations,
                        repair_adopted=repair_called,
                        semantic_evidence=fixture.semantic_evidence,
                    ),
                }
                return (RunState.COMPLETED, raw_evidence, None)

            worker.submit(
                service=service,
                run=run,
                deadline_ms=plan.budget.deadline_ms,
                invoke=_invoke_fixture,
            )

        # R4-WU-02: the genuine Frozen Configuration digest is never known
        # synchronously any more -- it is only captured once the Lease-
        # protected async Task actually runs (`_invoke_production` above).
        return _run_response(run, frozen_configuration_digest_sha512=None)

    @router.post("/runs/{run_id}/cancel", response_model=VariantRunResponse)
    async def cancel_run(request: Request, run_id: str) -> VariantRunResponse:
        service = _service(request)
        if service is None:
            raise _disabled_error()
        runtime: WebRuntime = request.app.state.runtime
        if runtime.experiment_run_worker is not None:
            # Best-effort: interrupts a real in-flight Production Turn.
            # The authoritative state transition is always the
            # `service.cancel_run()` call below, regardless of whether an
            # in-flight hook was actually found.
            runtime.experiment_run_worker.request_cancel(run_id)
        try:
            run = service.cancel_run(run_id)
        except ExperimentCoreError as exc:
            if exc.code is ExperimentCoreErrorCode.TERMINAL_ALREADY_PUBLISHED:
                # R2-WU-04 (IR-P9-2-R1-06 fix): the Run's own Cancel Hook
                # (requested above) can race ahead of THIS Cancel and
                # publish `CANCELLED` first through the Worker's own
                # Task -- that is this SAME Cancel succeeding via a
                # different path, never a genuine failure to report as
                # 409. Only a Run that reached a DIFFERENT terminal state
                # (already `COMPLETED`/`FAILED` for an unrelated reason)
                # is a real "too late to cancel" -- that case still 409s.
                already_terminal = service.get_run(run_id)
                if already_terminal.state is RunState.CANCELLED:
                    return _run_response(
                        already_terminal,
                        frozen_configuration_digest_sha512=_frozen_configuration_digest_for(
                            service, run_id
                        ),
                    )
            raise _core_error_to_web_error(exc) from exc
        return _run_response(
            run,
            frozen_configuration_digest_sha512=_frozen_configuration_digest_for(service, run_id),
        )

    @router.get("/runs/{run_id}", response_model=VariantRunResultResponse)
    async def get_run(request: Request, run_id: str) -> VariantRunResultResponse:
        service = _service(request)
        if service is None:
            raise _disabled_error()
        try:
            result = service.get_result(run_id)
        except ExperimentCoreError as exc:
            raise _core_error_to_web_error(exc) from exc
        return _result_response(service, result)

    @router.get("/experiments/{experiment_id}/runs", response_model=ExperimentRunListResponse)
    async def list_runs(request: Request, experiment_id: str) -> ExperimentRunListResponse:
        service = _service(request)
        if service is None:
            raise _disabled_error()
        runs = service.list_runs(experiment_id)
        responses = tuple(
            _run_response(
                run,
                frozen_configuration_digest_sha512=_frozen_configuration_digest_for(
                    service, run.run_id
                ),
            )
            for run in runs
        )
        return ExperimentRunListResponse(experiment_id=experiment_id, runs=responses)

    @router.get(
        "/experiments/{experiment_id}/comparison", response_model=ExperimentComparisonResponse
    )
    async def get_comparison(request: Request, experiment_id: str) -> ExperimentComparisonResponse:
        service = _service(request)
        if service is None:
            raise _disabled_error()
        plan = service.store.load_plan(experiment_id)
        if plan is None:
            raise ExperimentWebError(
                404, "not_found", f"No Plan exists for experiment_id {experiment_id!r}"
            )
        try:
            case = _resolve_frozen_case(plan)
        except ExperimentCoreError as exc:
            raise _core_error_to_web_error(exc) from exc
        # R2-WU-03 (IR-P9-2-R1-04 fix): every real `EvaluationObservation`
        # is computed HERE, in ONE pass over `service.list_runs()`, and
        # passed INTO `build_comparison_report()` -- which both persists
        # (`store.save_comparison()`) and returns this SAME `report.rows`.
        # R1's own version called `build_comparison_report()` with no
        # Observations at all, then separately fabricated one PER ROW
        # only for the HTTP Response -- so Disk and Response never
        # actually carried the same content. This version cannot drift:
        # there is only one computation, and both the persisted and the
        # returned Comparison read the exact same `report.rows`.
        runs_by_id = {run.run_id: run for run in service.list_runs(experiment_id)}
        observations_by_run_id = {
            run.run_id: (
                evaluate_case_outcome(
                    case=case, run=run, raw_evidence=service.store.load_raw_evidence(run.run_id)
                ),
            )
            for run in runs_by_id.values()
        }
        try:
            report = build_comparison_report(
                experiment_id=experiment_id,
                store=service.store,
                observations_by_run_id=observations_by_run_id,
                variant_relationships=(
                    fixture_comparison_declarations(plan)
                    if plan.execution_mode == "fixture"
                    else ()
                ),
            )
        except ExperimentCoreError as exc:
            raise _core_error_to_web_error(exc) from exc
        rows = []
        for row in report.rows:
            variant = next(
                (item for item in plan.variants if item.variant_id == row.variant_id), None
            )
            components = tuple(
                ExperimentComponentSelectionResponse(
                    component_key=component.component_key.value,
                    selector_id=component.selector_id,
                    mode=component.mode,
                )
                for component in (variant.components if variant is not None else ())
            )
            metric_response = None
            if row.metric is not None:
                metric_response = ExperimentMetricResponse(
                    runtime_state=row.metric.runtime_state.value,
                    latency_ms=row.metric.latency_ms,
                    call_count=row.metric.call_count,
                    unknown_component_count=row.metric.unknown_component_count,
                    deviation_count=row.metric.deviation_count,
                    repair_adopted=row.metric.repair_adopted,
                    false_positive=row.metric.false_positive,
                    false_grounding=row.metric.false_grounding,
                    correction_acceptance=row.metric.correction_acceptance,
                )
            observations = tuple(
                ExperimentEvaluationObservationResponse(
                    evaluator_kind=observation.evaluator_kind.value,
                    evaluator_identity=observation.evaluator_identity,
                    outcome=observation.outcome.value,
                    score=observation.score,
                    reason=observation.reason,
                )
                for observation in row.observations
            )
            run_for_row = runs_by_id.get(row.run_id)
            rows.append(
                ExperimentComparisonRowResponse(
                    variant_id=row.variant_id,
                    run_id=row.run_id,
                    execution_mode=run_for_row.execution_mode if run_for_row is not None else None,
                    runtime_state=row.runtime_state.value,
                    metric=metric_response,
                    observations=observations,
                    failure_reason=row.failure_reason,
                    raw_evidence_pointer=row.raw_evidence_pointer,
                    variant_components=components,
                    frozen_configuration_digest_sha512=_frozen_configuration_digest_for(
                        service, row.run_id
                    ),
                    semantic_evidence=row.semantic_evidence,
                )
            )
        return ExperimentComparisonResponse(
            experiment_id=experiment_id,
            case_id=report.case_id,
            case_revision=report.case_revision,
            variant_relationships=report.variant_relationships,
            rows=tuple(rows),
        )

    return router
