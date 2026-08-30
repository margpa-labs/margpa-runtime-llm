"""Local-private `/api/v2/data-controls` routes and safe errors (P7-G)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.data_controls.contracts import (
    DATA_RETENTION_FACTS,
    DataControlConsentUpdate,
    DataControlPolicySnapshot,
)
from margpa_runtime_llm.modules.data_controls.ports import DataControlConsentStorePort

from .contracts import WebRuntime
from .data_controls_contracts import (
    DataControlConsentUpdateRequest,
    DataControlPolicyResponse,
    project_policy,
)

DATA_CONTROLS_API_PREFIX = "/api/v2/data-controls"


@dataclass(frozen=True, slots=True)
class DataControlsWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_data_controls_router() -> APIRouter:
    router = APIRouter(prefix=DATA_CONTROLS_API_PREFIX)

    @router.get("/policy", response_model=DataControlPolicyResponse)
    async def policy(request: Request) -> DataControlPolicyResponse:
        store = _store(request)
        consent = await asyncio.to_thread(store.get)
        return project_policy(
            DataControlPolicySnapshot(consent=consent, retention_facts=DATA_RETENTION_FACTS)
        )

    @router.put("/consent", response_model=DataControlPolicyResponse)
    async def update_consent(
        request: Request,
        body: DataControlConsentUpdateRequest,
    ) -> DataControlPolicyResponse:
        store = _store(request)
        patch = DataControlConsentUpdate(
            external_query_transmission_consent=body.external_query_transmission_consent,
            feedback_research_use=body.feedback_research_use,
            synthetic_data_use=body.synthetic_data_use,
            future_training_export=body.future_training_export,
        )
        consent = await asyncio.to_thread(store.update, patch)
        return project_policy(
            DataControlPolicySnapshot(consent=consent, retention_facts=DATA_RETENTION_FACTS)
        )

    @router.post("/reset", response_model=DataControlPolicyResponse)
    async def reset(request: Request) -> DataControlPolicyResponse:
        store = _store(request)
        consent = await asyncio.to_thread(store.reset_to_defaults)
        return project_policy(
            DataControlPolicySnapshot(consent=consent, retention_facts=DATA_RETENTION_FACTS)
        )

    return router


def data_controls_error_response(error: DataControlsWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _store(request: Request) -> DataControlConsentStorePort:
    runtime: WebRuntime = request.app.state.runtime
    store = runtime.data_controls_store
    if store is None:
        raise DataControlsWebError(
            404,
            "data_controls_unavailable",
            "Data Controls is unavailable.",
        )
    return store
