"""Role provider GET/CAS PUT API for the Advanced Mode control surface."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET,
    LOCAL_MACOS_QWEN3GUARD_BUDGET,
    LOCAL_MACOS_SELENE_JUDGE_BUDGET,
    StageBudgetProfile,
)
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.runtime_model_control.application import (
    QWEN3_GUARD,
    SELENE_JUDGE,
    ProviderSelectionController,
)
from margpa_runtime_llm.modules.runtime_model_control.application.role_lifecycle_manager import (
    ModeReadResult,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelBusyError,
    RuntimeModelContextLimitExceeded,
    RuntimeModelLoadFailure,
    RuntimeModelRevisionConflict,
    RuntimeModelRollbackFailure,
    RuntimeModelTargetNotRegistered,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderIndependence,
    ProviderOption,
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
    ProviderSelectionSnapshot,
    RoleProviderSelection,
)

from .contracts import WebRuntime

PROVIDER_SELECTION_API_PREFIX = "/api/v6/provider-selection"


class _ProviderContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StageBudgetResponse(_ProviderContract):
    profile_id: str
    verification_state: str
    load_budget_ms: int
    prompt_build_budget_ms: int
    inference_budget_ms: int
    decode_budget_ms: int
    repair_generation_budget_ms: int
    rejudge_budget_ms: int
    cancel_grace_ms: int


class ProviderOptionResponse(_ProviderContract):
    provider_id: str
    role: str
    kind: str
    display_name: str
    enabled: bool
    model_key: str | None


class RoleProviderSelectionResponse(_ProviderContract):
    role: str
    configured_provider: str
    active_provider: str | None
    state: str
    independence: str
    failure_reason: str | None
    failure_at: str | None
    budget: StageBudgetResponse | None


class ProviderSelectionStatusResponse(_ProviderContract):
    enabled: bool
    revision: int | None = None
    digest_sha512: str | None = None
    selections: tuple[RoleProviderSelectionResponse, ...] = ()
    options: tuple[ProviderOptionResponse, ...] = ()


class ApplyProviderSelectionRequest(_ProviderContract):
    provider_id: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(ge=1)
    expected_digest: str = Field(pattern=r"^[0-9a-f]{128}$")


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime


def _budget_for(selection: RoleProviderSelection) -> StageBudgetProfile | None:
    if selection.configured_provider == SELENE_JUDGE:
        return LOCAL_MACOS_SELENE_JUDGE_BUDGET
    if selection.configured_provider == QWEN3_GUARD:
        return LOCAL_MACOS_QWEN3GUARD_BUDGET
    if selection.role is ModelRole.JUDGE and selection.independence is ProviderIndependence.SELF:
        return LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET
    return None


def _budget_response(profile: StageBudgetProfile | None) -> StageBudgetResponse | None:
    if profile is None:
        return None
    return StageBudgetResponse(
        profile_id=profile.profile_id,
        verification_state=profile.verification_state,
        load_budget_ms=profile.load_budget_ms,
        prompt_build_budget_ms=profile.prompt_build_budget_ms,
        inference_budget_ms=profile.inference_budget_ms,
        decode_budget_ms=profile.decode_budget_ms,
        repair_generation_budget_ms=profile.repair_generation_budget_ms,
        rejudge_budget_ms=profile.rejudge_budget_ms,
        cancel_grace_ms=profile.cancel_grace_ms,
    )


def _selection_response(
    selection: RoleProviderSelection,
) -> RoleProviderSelectionResponse:
    return RoleProviderSelectionResponse(
        role=selection.role.value,
        configured_provider=selection.configured_provider,
        active_provider=selection.active_provider,
        state=selection.state.value,
        independence=selection.independence.value,
        failure_reason=selection.failure_reason,
        failure_at=selection.failure_at,
        budget=_budget_response(_budget_for(selection)),
    )


def _option_response(option: ProviderOption) -> ProviderOptionResponse:
    return ProviderOptionResponse(
        provider_id=option.provider_id,
        role=option.role.value,
        kind=option.kind.value,
        display_name=option.display_name,
        enabled=option.enabled,
        model_key=option.model_key,
    )


def _read_judge_mode(runtime: WebRuntime) -> ModeReadResult:
    controller = runtime.judge_mode_control
    if controller is None:
        return ModeReadResult(revision=None, value=EvaluationMode.OFF.value)
    snapshot = controller.mode_snapshot()
    return ModeReadResult(revision=snapshot.revision, value=snapshot.current_mode.value)


def _read_guard_mode(runtime: WebRuntime) -> ModeReadResult:
    composition = runtime.guardrail_governance_composition
    if composition is None:
        return ModeReadResult(revision=None, value=GovernanceMode.OFF.value)
    snapshot = composition.mode_controller.mode_snapshot()
    return ModeReadResult(revision=snapshot.revision, value=snapshot.current_mode.value)


async def _status(runtime: WebRuntime) -> ProviderSelectionStatusResponse:
    controller = runtime.provider_selection_control
    if controller is None:
        return ProviderSelectionStatusResponse(enabled=False)
    if runtime.role_provider_lifecycle is not None:
        # P6-RR-R17-WU-001..004 (Post-Claude Independent Review Rework,
        # resolves P6-CODEX-080): Provider Selection state is read through
        # the same Transition Lock a Judge/Guard Mode-Apply or
        # Provider-Selection Transaction holds for its whole critical
        # section — never an independent `controller.snapshot()` call
        # that could observe an in-flight Transition's intermediate
        # Provider state (Mode value is not part of this Response's own
        # shape, but the Lock discipline this composite read enforces is
        # what keeps this Response consistent with whatever Feature Modes
        # GET/Mode Apply Response a concurrent poll observes at the same
        # instant).
        composite = await asyncio.to_thread(
            runtime.role_provider_lifecycle.composite_status,
            read_judge_mode=lambda: _read_judge_mode(runtime),
            read_guard_mode=lambda: _read_guard_mode(runtime),
        )
        return _snapshot_response(composite.provider)
    snapshot = controller.snapshot()
    return _snapshot_response(snapshot)


def _snapshot_response(snapshot: ProviderSelectionSnapshot) -> ProviderSelectionStatusResponse:
    return ProviderSelectionStatusResponse(
        enabled=True,
        revision=snapshot.revision,
        digest_sha512=snapshot.digest_sha512,
        selections=tuple(_selection_response(item) for item in snapshot.selections),
        options=tuple(_option_response(item) for item in snapshot.options),
    )


async def _apply_main_provider_selection(
    *,
    runtime_model_control: RuntimeModelController | None,
    controller: ProviderSelectionController,
    body: ApplyProviderSelectionRequest,
) -> ProviderSelectionSnapshot:
    """P6-CODEX-049 (Production Wiring Delta): the Main Dropdown now drives
    the *same* CAS Switch Transaction `RuntimeModelController` already uses
    (Architecture 3.2, unchanged) — Configured no longer diverges from
    real Main/Sidebar/Model Status without an accompanying Attempt. Success
    converges Configured/Active to the new model in one Revision
    (P6-DELTA-001); failure keeps the previous Active model running and
    reports an Exact Failure Reason instead of a silent stale Configured
    value (P6-DELTA-002)."""
    configured_snapshot = controller.select(
        role=ModelRole.MAIN,
        provider_id=body.provider_id,
        expected_revision=body.expected_revision,
        expected_digest=body.expected_digest,
    )
    if runtime_model_control is None:
        failed = controller.replace_runtime_state(
            role=ModelRole.MAIN,
            configured_provider=body.provider_id,
            active_provider=None,
            state=ProviderRuntimeState.UNAVAILABLE,
            failure_reason="main_runtime_model_control_unavailable",
        )
        raise ProviderSelectionError(
            code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
            safe_message="The Main runtime switch is not available.",
            current_snapshot=failed,
        )
    main_selection = next(
        item for item in configured_snapshot.selections if item.role is ModelRole.MAIN
    )
    if main_selection.active_provider == body.provider_id:
        # Already running the requested model (e.g. re-selecting Current) —
        # Configured/Active already converged; no Switch Transaction needed.
        return configured_snapshot
    model_snapshot = runtime_model_control.snapshot()
    try:
        committed = await asyncio.to_thread(
            runtime_model_control.switch_to_model_key,
            expected_revision=model_snapshot.revision,
            expected_digest=model_snapshot.digest_sha512,
            transition_id=str(uuid4()),
            target_model_key=body.provider_id,
            requested_context_size=model_snapshot.loaded_context_size,
        )
    except (
        RuntimeModelRevisionConflict,
        RuntimeModelBusyError,
        RuntimeModelContextLimitExceeded,
        RuntimeModelTargetNotRegistered,
        RuntimeModelLoadFailure,
        RuntimeModelRollbackFailure,
    ) as exc:
        post_failure_snapshot = runtime_model_control.snapshot()
        rolled_back_active = (
            post_failure_snapshot.selected_model_key
            if post_failure_snapshot.runtime_state is RuntimeState.ACTIVE
            else None
        )
        failed = controller.replace_runtime_state(
            role=ModelRole.MAIN,
            configured_provider=body.provider_id,
            active_provider=rolled_back_active,
            state=ProviderRuntimeState.UNAVAILABLE,
            failure_reason=f"main_switch_failed:{type(exc).__name__}",
        )
        failed_main = next(item for item in failed.selections if item.role is ModelRole.MAIN)
        raise ProviderSelectionError(
            code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
            safe_message=f"The Main model could not be switched: {failed_main.failure_reason}",
            current_snapshot=failed,
        ) from exc
    return controller.replace_runtime_state(
        role=ModelRole.MAIN,
        configured_provider=body.provider_id,
        active_provider=committed.selected_model_key,
        state=ProviderRuntimeState.ACTIVE,
    )


async def _apply_role_provider_selection(
    *,
    runtime: WebRuntime,
    controller: ProviderSelectionController,
    typed_role: ModelRole,
    body: ApplyProviderSelectionRequest,
) -> ProviderSelectionSnapshot:
    """P6-RR-R1-WU-001/003/004/005/006 (Post-Claude Independent Review
    Rework, resolves P6-CODEX-062): a Judge/Guard Configured Provider
    change must never leave `Mode ON / Active none` reachable
    (P6-GOV-018 Addendum Scenario B, P6-DELTA-021/022/023).

    `ProviderSelectionController.select()` deliberately never performs an
    implicit Load or fallback (see its own docstring) — the existing
    Mode-Apply paths (`feature_modes_routes.py`'s `apply_judge()`,
    `configuration_control.py`'s `_GuardrailGovernanceModeApplierAdapter
    .apply()`) already correctly Preflight/Activate the configured
    Provider *before* committing a non-OFF Mode. This Route is therefore
    the other, previously unguarded, entry point that can change which
    Provider is Configured while a Mode is already ON — reusing that same
    Activation machinery here would silently start a Model Load from a
    plain Selection change, which is exactly what `select()`'s contract
    forbids. Instead, any real Configured change for Judge/Guard is
    treated as one atomic Transaction with this Role's Mode and Lifecycle
    Adapter (Addendum M-WU-005's "Mode OFFへRollback" branch): drain/
    unload any stale Active adapter unconditionally (R1-WU-005), and
    force this Role's Mode back to OFF if it was not already OFF
    (R1-WU-001/003/004) — never a half-committed `Mode ON / Active none`
    state, and never a silent auto-Activation of the newly Configured
    Provider. The user must re-apply Judge/Guard Mode explicitly afterward,
    through the routes that already Preflight correctly.
    """

    def _mode_is_on() -> bool:
        # P6-RR-R13-WU-001..004 (Post-Claude Independent Review Rework,
        # resolves P6-CODEX-074/062): this Callable is invoked *inside*
        # `RoleProviderLifecycleManager.apply_provider_selection()`'s own
        # Lock — never read here, outside any Lock, and then acted on
        # later. The Mode-Apply routes (`feature_modes_routes.py`'s
        # `apply_judge()`, `configuration_control.py`'s Guardrail Mode
        # Applier) commit Mode under that identical Lock via
        # `apply_mode_transition()`, so no concurrent request on either
        # path can observe or act on an intermediate state.
        if typed_role is ModelRole.JUDGE:
            return (
                runtime.judge_mode_control is not None
                and runtime.judge_mode_control.mode_snapshot().current_mode
                is not EvaluationMode.OFF
            )
        return (
            runtime.guardrail_governance_composition is not None
            and runtime.guardrail_governance_composition.mode_controller.current_mode_value()
            != GovernanceMode.OFF.value
        )

    if runtime.role_provider_lifecycle is None:
        if not _mode_is_on():
            return controller.select(
                role=typed_role,
                provider_id=body.provider_id,
                expected_revision=body.expected_revision,
                expected_digest=body.expected_digest,
            )
        raise ProviderSelectionError(
            code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
            safe_message="An active role provider cannot be transitioned safely.",
        )
    # P6-RR-R17-WU-001..004 (resolves P6-CODEX-080): this Response is
    # built directly from the returned CompositeRoleStatus's `.provider`
    # — read inside the same Lock the Transition itself just ran under —
    # never from a later, separate `controller.snapshot()` re-read.
    composite = await asyncio.to_thread(
        runtime.role_provider_lifecycle.apply_provider_selection,
        role=typed_role,
        provider_id=body.provider_id,
        expected_revision=body.expected_revision,
        expected_digest=body.expected_digest,
        mode_is_on=_mode_is_on,
        read_judge_mode=lambda: _read_judge_mode(runtime),
        read_guard_mode=lambda: _read_guard_mode(runtime),
    )
    return composite.provider


def create_provider_selection_router() -> APIRouter:
    router = APIRouter(prefix=PROVIDER_SELECTION_API_PREFIX)

    @router.get("", response_model=ProviderSelectionStatusResponse)
    async def get_provider_selection(request: Request) -> ProviderSelectionStatusResponse:
        return await _status(_runtime(request))

    @router.put("/{role}", response_model=ProviderSelectionStatusResponse)
    async def apply_provider_selection(
        request: Request,
        role: str,
        body: ApplyProviderSelectionRequest,
    ) -> ProviderSelectionStatusResponse:
        runtime = _runtime(request)
        controller = runtime.provider_selection_control
        if controller is None:
            return ProviderSelectionStatusResponse(enabled=False)
        try:
            typed_role = ModelRole(role)
        except ValueError:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ROLE_MISMATCH,
                safe_message="The requested provider role is invalid.",
            ) from None
        if typed_role is ModelRole.MAIN:
            snapshot = await _apply_main_provider_selection(
                runtime_model_control=runtime.runtime_model_control,
                controller=controller,
                body=body,
            )
            return _snapshot_response(snapshot)
        snapshot = await _apply_role_provider_selection(
            runtime=runtime,
            controller=controller,
            typed_role=typed_role,
            body=body,
        )
        return _snapshot_response(snapshot)

    return router
