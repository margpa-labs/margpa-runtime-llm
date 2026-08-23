"""Local-private `/api/v4/runtime-model` routes (Phase 6-G-WU-001/002/003,
Guard/Governance Layer identity added P6-CODEX-005).

Read-only `/status` projects all four Component Identities (Architecture
11.1): Main Model and Judge Model from RuntimeModelController's Snapshot;
Guard Model as the honest `model_id=None` default (Production has no bound
Safety Model Artifact as of Phase 5 — never fabricated, P6-ACC-024A); and
Governance Layer from the real, currently-bound Phase 4 Runtime Governance
(`WebRuntime.runtime_governance_composition.source_plan_id`/
`.source_plan_digest_sha512` — the actual verified Plan behind whatever
Descriptors are gating Main Model generation right now), never the
independent Phase 3 `governance_definitions` package-browse control surface
(P6-CODEX-014, Second Rework): that flag can be enabled or disabled with
zero effect on whether Phase 4 itself is bound, so deriving Current
Governance Layer from it could show `None` even while a real Phase 4
binding is active — or, symmetrically, imply a binding when only the
browse-only Package view is enabled. `None` here now means precisely "Phase
4 Runtime Governance is not enabled, or is enabled but has not bound a
source Plan" — never a guess derived from an unrelated control surface.

`/context` and `/max-new-tokens` are CAS-guarded Mutations (Architecture
5.1/5.2), following the same expected_revision/expected_digest pattern as
`configuration_routes.py`'s Preview/Apply — except there is no separate
Preview step here (Architecture 5.1's own Preview is the client reading
`/status` first to see the effective max before submitting).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelBusyError,
    RuntimeModelContextLimitExceeded,
    RuntimeModelLoadFailure,
    RuntimeModelMaxNewTokensExceeded,
    RuntimeModelRevisionConflict,
    RuntimeModelRollbackFailure,
    RuntimeModelTargetNotRegistered,
)
from margpa_runtime_llm.modules.runtime_observability.projection.component_identity_projection import (  # noqa: E501
    project_governance_layer_identity,
    project_guard_model_identity,
    project_judge_model_identity,
    project_main_model_identity,
)

from .contracts import WebRuntime

RUNTIME_MODEL_CONTROL_API_PREFIX = "/api/v4/runtime-model"


@dataclass(frozen=True, slots=True)
class RuntimeModelControlWebError(Exception):
    status_code: int
    code: str
    safe_message: str


class _RuntimeModelContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MainModelIdentityResponse(_RuntimeModelContract):
    model_key: str
    artifact_digest: str
    backend_identity: str
    state: str


class JudgeModelIdentityResponse(_RuntimeModelContract):
    model_key: str | None
    independence_class: str
    state: str


class GuardModelIdentityResponse(_RuntimeModelContract):
    model_id: str | None
    exact_revision: str | None
    artifact_digest_sha512: str | None
    state: str


class GovernanceLayerIdentityResponse(_RuntimeModelContract):
    package_id: str | None
    manifest_digest_sha512: str | None
    state: str


class AvailableModelResponse(_RuntimeModelContract):
    """One `logical_role="main"` Registry entry a Runtime Switch may target
    (Fourth Rework, P6-CODEX-026) — sourced from
    `RuntimeModelController.available_models()`, never a hardcoded list, so
    a newly registered Definition (e.g. DeepSeek) appears without a code
    change on this side."""

    model_key: str
    provider: str
    native_context_limit: int


class RuntimeModelStatusResponse(_RuntimeModelContract):
    enabled: bool
    revision: int | None = None
    digest_sha512: str | None = None
    """CAS token for /context, /max-new-tokens and /switch — distinct from
    main_model.artifact_digest, which identifies only the artifact."""
    runtime_state: str | None = None
    loaded_context_size: int | None = None
    model_native_context_limit: int | None = None
    backend_context_limit: int | None = None
    deployment_verified_context_limit: int | None = None
    max_output_token_limit: int | None = None
    current_max_new_tokens: int | None = None
    main_model: MainModelIdentityResponse | None = None
    judge_model: JudgeModelIdentityResponse | None = None
    guard_model: GuardModelIdentityResponse | None = None
    governance_layer: GovernanceLayerIdentityResponse | None = None
    available_models: tuple[AvailableModelResponse, ...] = ()


class ContextChangeRequest(_RuntimeModelContract):
    expected_revision: int = Field(ge=0)
    expected_digest: str = Field(min_length=1)
    requested_context_size: int = Field(gt=0)


class MaxNewTokensRequest(_RuntimeModelContract):
    expected_revision: int = Field(ge=0)
    expected_digest: str = Field(min_length=1)
    requested_max_new_tokens: int = Field(gt=0)


class SwitchRequest(_RuntimeModelContract):
    expected_revision: int = Field(ge=0)
    expected_digest: str = Field(min_length=1)
    target_model_key: str = Field(min_length=1)
    requested_context_size: int = Field(gt=0)


def _project_status(request: Request) -> RuntimeModelStatusResponse:
    runtime = _runtime(request)
    controller = runtime.runtime_model_control
    if controller is None:
        return RuntimeModelStatusResponse(enabled=False)
    snapshot = controller.snapshot()
    main_identity = project_main_model_identity(snapshot=snapshot)
    judge_identity = project_judge_model_identity(snapshot=snapshot)
    # Guard Model has no bound Safety Model Artifact in Production as of
    # Phase 5 (UnavailableSafetyModelAdapter) — model_id=None is the honest
    # current value, never fabricated (P6-ACC-024A/P6-CODEX-005).
    guard_identity = project_guard_model_identity(
        model_id=None, exact_revision=None, artifact_digest_sha512=None
    )
    runtime_governance_composition = runtime.runtime_governance_composition
    governance_layer_identity = project_governance_layer_identity(
        package_id=(
            None
            if runtime_governance_composition is None
            else runtime_governance_composition.source_plan_id
        ),
        manifest_digest_sha512=(
            None
            if runtime_governance_composition is None
            else runtime_governance_composition.source_plan_digest_sha512
        ),
    )
    return RuntimeModelStatusResponse(
        enabled=True,
        revision=snapshot.revision,
        digest_sha512=snapshot.digest_sha512,
        runtime_state=snapshot.runtime_state.value,
        loaded_context_size=snapshot.loaded_context_size,
        model_native_context_limit=snapshot.model_native_context_limit,
        backend_context_limit=snapshot.backend_context_limit,
        deployment_verified_context_limit=snapshot.deployment_verified_context_limit,
        max_output_token_limit=snapshot.max_output_token_limit,
        current_max_new_tokens=snapshot.current_max_new_tokens,
        main_model=MainModelIdentityResponse(
            model_key=main_identity.model_key,
            artifact_digest=main_identity.artifact_digest,
            backend_identity=main_identity.backend_identity,
            state=main_identity.state.value,
        ),
        judge_model=JudgeModelIdentityResponse(
            model_key=judge_identity.model_key,
            independence_class=judge_identity.independence_class.value,
            state=judge_identity.state.value,
        ),
        guard_model=GuardModelIdentityResponse(
            model_id=guard_identity.model_id,
            exact_revision=guard_identity.exact_revision,
            artifact_digest_sha512=guard_identity.artifact_digest_sha512,
            state=guard_identity.state.value,
        ),
        governance_layer=GovernanceLayerIdentityResponse(
            package_id=governance_layer_identity.package_id,
            manifest_digest_sha512=governance_layer_identity.manifest_digest_sha512,
            state=governance_layer_identity.state.value,
        ),
        available_models=tuple(
            AvailableModelResponse(
                model_key=definition.model_key,
                provider=definition.source.provider,
                native_context_limit=definition.model.native_context_limit,
            )
            for definition in controller.available_models()
        ),
    )


def _require_controller(runtime: WebRuntime) -> RuntimeModelController:
    controller = runtime.runtime_model_control
    if controller is None:
        raise RuntimeModelControlWebError(
            status_code=404,
            code="runtime_model_control_not_enabled",
            safe_message="Runtime model control is not enabled.",
        )
    return controller


def create_runtime_model_control_router() -> APIRouter:
    router = APIRouter(prefix=RUNTIME_MODEL_CONTROL_API_PREFIX)

    @router.get("/status", response_model=RuntimeModelStatusResponse)
    async def get_status(request: Request) -> RuntimeModelStatusResponse:
        return _project_status(request)

    @router.post("/context", response_model=RuntimeModelStatusResponse)
    async def apply_context(
        request: Request, body: ContextChangeRequest
    ) -> RuntimeModelStatusResponse:
        controller = _require_controller(_runtime(request))
        await asyncio.to_thread(
            controller.request_context_change,
            expected_revision=body.expected_revision,
            expected_digest=body.expected_digest,
            transition_id=str(uuid4()),
            requested_context_size=body.requested_context_size,
        )
        return _project_status(request)

    @router.post("/max-new-tokens", response_model=RuntimeModelStatusResponse)
    async def apply_max_new_tokens(
        request: Request, body: MaxNewTokensRequest
    ) -> RuntimeModelStatusResponse:
        controller = _require_controller(_runtime(request))
        await asyncio.to_thread(
            controller.set_max_new_tokens,
            expected_revision=body.expected_revision,
            expected_digest=body.expected_digest,
            requested_max_new_tokens=body.requested_max_new_tokens,
        )
        return _project_status(request)

    @router.post("/switch", response_model=RuntimeModelStatusResponse)
    async def switch_model(request: Request, body: SwitchRequest) -> RuntimeModelStatusResponse:
        controller = _require_controller(_runtime(request))
        await asyncio.to_thread(
            controller.switch_to_model_key,
            expected_revision=body.expected_revision,
            expected_digest=body.expected_digest,
            transition_id=str(uuid4()),
            target_model_key=body.target_model_key,
            requested_context_size=body.requested_context_size,
        )
        return _project_status(request)

    return router


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime


def runtime_model_control_error_response(
    error: (
        RuntimeModelRevisionConflict
        | RuntimeModelContextLimitExceeded
        | RuntimeModelMaxNewTokensExceeded
        | RuntimeModelBusyError
        | RuntimeModelLoadFailure
        | RuntimeModelRollbackFailure
        | RuntimeModelTargetNotRegistered
    ),
) -> JSONResponse:
    if isinstance(error, RuntimeModelRevisionConflict):
        return JSONResponse(
            status_code=409,
            content={
                "code": "runtime_model_revision_conflict",
                "message": "The runtime model snapshot has changed; reload and retry.",
                "current_revision": error.current_revision,
                "current_digest": error.current_digest,
            },
        )
    if isinstance(error, RuntimeModelTargetNotRegistered):
        return JSONResponse(
            status_code=404,
            content={
                "code": "runtime_model_target_not_registered",
                "message": "The requested switch target is not a registered model.",
            },
        )
    if isinstance(error, RuntimeModelBusyError):
        return JSONResponse(
            status_code=409,
            content={"code": "runtime_model_busy", "message": "A generation is in progress."},
        )
    if isinstance(error, RuntimeModelContextLimitExceeded | RuntimeModelMaxNewTokensExceeded):
        return JSONResponse(
            status_code=422,
            content={"code": "runtime_model_limit_exceeded", "message": str(error)},
        )
    return JSONResponse(
        status_code=502,
        content={
            "code": "runtime_model_change_failed",
            "message": "The runtime model change could not be completed safely.",
        },
    )


def runtime_model_control_web_error_response(error: RuntimeModelControlWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )
