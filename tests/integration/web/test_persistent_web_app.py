"""Phase 2-C in-process persistent API integration and compatibility tests."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import threading
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi import FastAPI, Request

from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationTurnState,
)
from margpa_runtime_llm.modules.conversation.ports import (
    CommitConversation,
    ConversationCommitReceipt,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode
from margpa_runtime_llm.web.access_profiles import (
    DocumentationRagEffectiveState,
    WebExposureMode,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import (
    DocumentationRagRuntimeSnapshot,
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)
from margpa_runtime_llm.web.persistent_contracts import PersistentTurnStreamRequest
from margpa_runtime_llm.web.persistent_routes import _generation_identities
from margpa_runtime_llm.web.persistent_streaming import PersistentSseBridge

SCOPE = ConversationScopeId(value="server-private-scope")


class Session:
    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.finished = False
        self.cancelled = False
        self.event_thread_ids: list[int] = []

    def request_cancel(self) -> None:
        self.cancelled = True

    def force_cancel(self) -> None:
        self.cancelled = True

    def events(self) -> Iterator[ConversationEvent]:
        try:
            self.event_thread_ids.append(threading.get_ident())
            yield ConversationEvent(
                event=ConversationEventType.START,
                data={"request_id": self.request_id, "state": "generating"},
            )
            if self.cancelled:
                yield ConversationEvent(
                    event=ConversationEventType.CANCELLED,
                    data={"request_id": self.request_id, "state": "cancelled"},
                )
            else:
                yield ConversationEvent(
                    event=ConversationEventType.DELTA,
                    data={"request_id": self.request_id, "channel": "final", "text": "partial"},
                )
                yield ConversationEvent(
                    event=ConversationEventType.COMPLETED,
                    data={
                        "request_id": self.request_id,
                        "finish_reason": "stop",
                        "assistant_message": {"role": "assistant", "content": self.answer},
                    },
                )
        finally:
            self.event_thread_ids.append(threading.get_ident())
            self.finished = True


class Generation:
    def __init__(self) -> None:
        self.calls: list[ConversationGenerationInput] = []
        self.active: Session | None = None
        self.start_thread_ids: list[int] = []

    def start(self, value: ConversationGenerationInput) -> Session:
        self.start_thread_ids.append(threading.get_ident())
        self.calls.append(value)
        self.active = Session(f"request-{len(self.calls)}", f"canonical-{len(self.calls)}")
        return self.active

    def cancel(self, request_id: str) -> bool:
        if self.active is None or self.active.request_id != request_id:
            return False
        self.active.request_cancel()
        return True

    def shutdown(self, timeout: float = 10.0) -> bool:
        del timeout
        if self.active is not None:
            self.active.request_cancel()
        return True


class FailingTerminalStore(SQLiteConversationStore):
    def commit(self, command: CommitConversation) -> ConversationCommitReceipt:
        if any(
            turn.state is ConversationTurnState.COMPLETED for turn in command.conversation.turns
        ):
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.STORAGE_UNAVAILABLE,
                safe_message="The conversation store is unavailable.",
            )
        return super().commit(command)


class SlowSession(Session):
    def events(self) -> Iterator[ConversationEvent]:
        try:
            self.event_thread_ids.append(threading.get_ident())
            yield ConversationEvent(
                event=ConversationEventType.START,
                data={"request_id": self.request_id, "state": "generating"},
            )
            time.sleep(0.05)
            yield ConversationEvent(
                event=ConversationEventType.DELTA,
                data={"request_id": self.request_id, "channel": "final", "text": "partial"},
            )
            yield ConversationEvent(
                event=ConversationEventType.COMPLETED,
                data={
                    "request_id": self.request_id,
                    "finish_reason": "stop",
                    "assistant_message": {"role": "assistant", "content": self.answer},
                },
            )
        finally:
            self.event_thread_ids.append(threading.get_ident())
            self.finished = True


class SlowGeneration(Generation):
    def start(self, value: ConversationGenerationInput) -> SlowSession:
        self.start_thread_ids.append(threading.get_ident())
        self.calls.append(value)
        self.active = SlowSession("request-slow", "must-not-persist")
        return self.active


class FailingSession(Session):
    def events(self) -> Iterator[ConversationEvent]:
        try:
            self.event_thread_ids.append(threading.get_ident())
            yield ConversationEvent(
                event=ConversationEventType.START,
                data={"request_id": self.request_id, "state": "generating"},
            )
            yield ConversationEvent(
                event=ConversationEventType.ERROR,
                data={
                    "request_id": self.request_id,
                    "code": "generation_failed",
                    "message": "The generation failed.",
                    "retryable": True,
                },
            )
        finally:
            self.event_thread_ids.append(threading.get_ident())
            self.finished = True


class RetryGeneration(Generation):
    def start(self, value: ConversationGenerationInput) -> Session:
        self.start_thread_ids.append(threading.get_ident())
        self.calls.append(value)
        if len(self.calls) == 1:
            self.active = FailingSession("request-failed", "unused")
        else:
            self.active = Session("request-retry", "canonical-retry")
        return self.active


class BlockingSession(Session):
    def events(self) -> Iterator[ConversationEvent]:
        try:
            self.event_thread_ids.append(threading.get_ident())
            yield ConversationEvent(
                event=ConversationEventType.START,
                data={"request_id": self.request_id, "state": "generating"},
            )
            while not self.cancelled:
                time.sleep(0.005)
            yield ConversationEvent(
                event=ConversationEventType.CANCELLED,
                data={"request_id": self.request_id, "state": "cancelled"},
            )
        finally:
            self.event_thread_ids.append(threading.get_ident())
            self.finished = True


class BlockingGeneration(Generation):
    def start(self, value: ConversationGenerationInput) -> BlockingSession:
        self.start_thread_ids.append(threading.get_ident())
        self.calls.append(value)
        self.active = BlockingSession("request-blocking", "unused")
        return self.active


class PersistentCallSpy:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __getattr__(self, name: str) -> object:
        self.calls.append(name)
        raise AssertionError(f"v1 accessed persistent service: {name}")


def runtime_snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key="fixture-model",
        profile_key="local.fixture",
        device_kind="cpu",
        acceleration_api="none",
        defaults=RuntimeDefaults(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            thinking_display_label="reasoning",
            thinking_control_available=False,
            summary_mode=SummaryMode.OFF,
            documentation_rag_mode=DocumentationRagMode.DISABLED,
        ),
        documentation_rag=DocumentationRagRuntimeSnapshot(
            effective_state=DocumentationRagEffectiveState.UNAVAILABLE,
            control_available=False,
        ),
    )


def persistent_runtime(tmp_path: Path) -> tuple[WebRuntime, SQLiteConversationStore, Generation]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = Generation()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
    )
    service.recover_incomplete_conversations()
    runtime = WebRuntime(
        conversation=cast(object, generation),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=service,
    )
    return runtime, store, generation


def disabled_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, Generation()),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


def settings_payload() -> dict[str, object]:
    return {
        "response_language": "ja",
        "max_new_tokens": 128,
        "thinking_mode": "disabled",
        "thinking_visibility": "hidden",
        "summary_mode": "off",
        "documentation_rag_mode": "disabled",
    }


async def create(client: httpx.AsyncClient, operation: str = "create-1") -> dict[str, object]:
    response = await client.post(
        "/api/v2/conversations",
        json={"operation_id": operation, "expected_revision": None},
    )
    assert response.status_code == 200
    return cast(dict[str, object], response.json()["detail"])


@pytest.mark.asyncio
async def test_disabled_runtime_exposes_capability_only_and_data_routes_are_unavailable() -> None:
    app = create_web_app(
        runtime_factory=disabled_runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        runtime = await client.get("/api/v2/conversations/runtime")
        unavailable = await client.get("/api/v2/conversations")
        v1 = await client.get("/api/v1/runtime")
    assert runtime.json() == {
        "enabled": False,
        "api_version": "2",
        "source_of_truth": "server",
        "features": [],
    }
    assert unavailable.status_code == 404
    assert unavailable.json()["code"] == "persistent_conversation_unavailable"
    assert v1.status_code == 200


@pytest.mark.asyncio
async def test_v1_runtime_and_generation_call_persistent_service_zero() -> None:
    generation = Generation()
    persistent_spy = PersistentCallSpy()
    runtime = WebRuntime(
        conversation=cast(object, generation),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=cast(PersistentConversationService, persistent_spy),
    )
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        runtime_response = await client.get("/api/v1/runtime")
        generation_response = await client.post(
            "/api/v1/chat/stream",
            json={
                "messages": [{"role": "user", "content": "v1 remains ephemeral"}],
                "settings": settings_payload(),
            },
        )
    assert runtime_response.status_code == 200
    assert generation_response.status_code == 200
    assert "event: completed" in generation_response.text
    assert persistent_spy.calls == []


@pytest.mark.parametrize(
    ("policy", "authorization"),
    [
        (
            WebAccessPolicy(
                mode=WebAuthMode.DISABLED,
                exposure_mode=WebExposureMode.PUBLIC_DEMO,
                non_loopback_allowed=True,
            ),
            None,
        ),
        (
            WebAccessPolicy(
                mode=WebAuthMode.BASIC,
                exposure_mode=WebExposureMode.BASIC_PREVIEW,
                non_loopback_allowed=True,
                username="preview-user",
                password="preview-password",
            ),
            "Basic " + base64.b64encode(b"preview-user:preview-password").decode("ascii"),
        ),
    ],
)
@pytest.mark.asyncio
async def test_shared_profiles_normal_runtime_have_zero_persistent_service_calls(
    policy: WebAccessPolicy,
    authorization: str | None,
) -> None:
    runtime = disabled_runtime()
    app = create_web_app(runtime_factory=lambda: runtime, access_policy=policy)
    headers = {} if authorization is None else {"Authorization": authorization}
    async with client_for(app) as client:
        capability = await client.get(
            "/api/v2/conversations/runtime",
            headers=headers,
        )
        v1 = await client.get("/api/v1/runtime", headers=headers)
    assert capability.status_code == 200
    assert capability.json()["enabled"] is False
    assert v1.status_code == 200
    assert runtime.persistent_conversation is None


@pytest.mark.asyncio
async def test_nonlocal_app_rejects_accidental_persistent_composition(tmp_path: Path) -> None:
    runtime, _, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(
            mode=WebAuthMode.DISABLED,
            exposure_mode=WebExposureMode.PUBLIC_DEMO,
            non_loopback_allowed=True,
        ),
    )
    with pytest.raises(RuntimeError, match="local loopback"):
        async with client_for(app):
            pass


@pytest.mark.asyncio
async def test_create_list_detail_and_history_open_is_write_free(tmp_path: Path) -> None:
    runtime, store, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        before = hashlib.sha512(store.database_path.read_bytes()).hexdigest()
        listed = await client.get("/api/v2/conversations?limit=20")
        opened = await client.get(f"/api/v2/conversations/{detail['conversation_id']}")
        after = hashlib.sha512(store.database_path.read_bytes()).hexdigest()
    assert listed.status_code == 200 and len(listed.json()["items"]) == 1
    assert opened.status_code == 200 and opened.json()["storage_revision"] == 1
    assert before == after
    text = opened.text
    assert SCOPE.value not in text
    assert str(tmp_path) not in text
    assert "operation" not in text


@pytest.mark.asyncio
async def test_archive_unarchive_resume_and_pagination_are_server_canonical(
    tmp_path: Path,
) -> None:
    runtime, _, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        first = await create(client, "lifecycle-1")
        await create(client, "lifecycle-2")
        page_one = (await client.get("/api/v2/conversations?limit=1")).json()
        page_two = (
            await client.get(
                "/api/v2/conversations?limit=1",
                params={"cursor": page_one["next_cursor"]},
            )
        ).json()
        archived = await client.post(
            f"/api/v2/conversations/{first['conversation_id']}/archive",
            json={"operation_id": "archive-lifecycle", "expected_revision": 1},
        )
        unarchived = await client.post(
            f"/api/v2/conversations/{first['conversation_id']}/unarchive",
            json={"operation_id": "unarchive-lifecycle", "expected_revision": 2},
        )
        resumed = await client.post(
            f"/api/v2/conversations/{first['conversation_id']}/resume",
            json={"operation_id": "resume-lifecycle", "expected_revision": 3},
        )
    assert len(page_one["items"]) == len(page_two["items"]) == 1
    assert page_one["items"][0]["conversation_id"] != page_two["items"][0]["conversation_id"]
    assert page_two["next_cursor"] is None
    archived_detail = archived.json()["detail"]
    assert archived.status_code == 200 and archived_detail["state"] == "archived"
    assert archived_detail["sessions"][0]["state"] == "closed"
    assert unarchived.status_code == 200 and unarchived.json()["detail"]["state"] == "active"
    resumed_detail = resumed.json()["detail"]
    assert resumed.status_code == 200 and resumed_detail["storage_revision"] == 4
    assert [item["state"] for item in resumed_detail["sessions"]] == ["closed", "active"]


@pytest.mark.asyncio
async def test_normal_stream_is_durable_before_terminal_and_replay_mutates_zero(
    tmp_path: Path,
) -> None:
    runtime, _, generation = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        conversation_id = detail["conversation_id"]
        body = {
            "content": "canonical user",
            "settings": settings_payload(),
            "operation_id": "turn-action-1",
            "expected_revision": detail["storage_revision"],
        }
        streamed = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/stream",
            json=body,
        )
        assert streamed.status_code == 200
        assert "event: start" in streamed.text
        assert '"durable_revision":3' in streamed.text
        assert "event: completed" in streamed.text
        assert '"durable_revision":4' in streamed.text
        persisted = await client.get(f"/api/v2/conversations/{conversation_id}")
        replay = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/stream",
            json={**body, "content": "different body", "expected_revision": 4},
        )
        after_replay = await client.get(f"/api/v2/conversations/{conversation_id}")
    assert persisted.json()["storage_revision"] == 4
    assert persisted.json()["turns"][0]["messages"][-1]["content"] == "canonical-1"
    assert replay.status_code == 409
    assert replay.json()["code"] == "operation_already_applied"
    assert after_replay.json()["storage_revision"] == 4
    assert len(generation.calls) == 1
    assert generation.active is not None
    assert generation.start_thread_ids == generation.active.event_thread_ids[:1]
    assert len(set(generation.active.event_thread_ids)) == 1


@pytest.mark.asyncio
async def test_stale_browser_conflict_is_409_with_mutation_zero(tmp_path: Path) -> None:
    runtime, _, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        conversation_id = detail["conversation_id"]
        first = await client.post(
            f"/api/v2/conversations/{conversation_id}/archive",
            json={"operation_id": "archive-1", "expected_revision": 1},
        )
        stale = await client.post(
            f"/api/v2/conversations/{conversation_id}/unarchive",
            json={"operation_id": "unarchive-stale", "expected_revision": 1},
        )
        current = await client.get(f"/api/v2/conversations/{conversation_id}")
    assert first.status_code == 200 and first.json()["detail"]["storage_revision"] == 2
    assert stale.status_code == 409 and stale.json()["code"] == "revision_conflict"
    assert stale.json()["current_revision"] == 2
    assert current.json()["state"] == "archived"
    assert current.json()["storage_revision"] == 2


@pytest.mark.asyncio
async def test_regenerate_and_branch_select_preserve_source_records(tmp_path: Path) -> None:
    runtime, _, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        conversation_id = detail["conversation_id"]
        normal = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/stream",
            json={
                "content": "one user",
                "settings": settings_payload(),
                "operation_id": "normal-1",
                "expected_revision": 1,
            },
        )
        assert normal.status_code == 200
        first_detail = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
        source_id = first_detail["turns"][0]["turn_id"]
        regenerated = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/{source_id}/regenerate/stream",
            json={
                "settings": settings_payload(),
                "operation_id": "regenerate-1",
                "expected_revision": first_detail["storage_revision"],
            },
        )
        assert regenerated.status_code == 200
        second_detail = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
        selected = await client.post(
            f"/api/v2/conversations/{conversation_id}/branches/{source_id}/select",
            json={
                "operation_id": "select-source",
                "expected_revision": second_detail["storage_revision"],
            },
        )
    selected_detail = selected.json()["detail"]
    assert len(selected_detail["turns"]) == 2
    assert selected_detail["head_turn_id"] == source_id
    assert selected_detail["turns"][0]["messages"][1]["content"] == "canonical-1"
    assert selected_detail["turns"][1]["origin"] == "regenerate"


@pytest.mark.asyncio
async def test_retry_api_uses_failed_server_source_without_client_replacement(
    tmp_path: Path,
) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = RetryGeneration()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
    )
    service.recover_incomplete_conversations()
    runtime = WebRuntime(
        conversation=cast(object, generation),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=service,
    )
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client, "retry-create")
        conversation_id = detail["conversation_id"]
        failed = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/stream",
            json={
                "content": "canonical retry source",
                "settings": settings_payload(),
                "operation_id": "retry-source",
                "expected_revision": 1,
            },
        )
        failed_detail = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
        source_turn_id = failed_detail["turns"][0]["turn_id"]
        retried = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/{source_turn_id}/retry/stream",
            json={
                "settings": settings_payload(),
                "operation_id": "retry-derived",
                "expected_revision": failed_detail["storage_revision"],
            },
        )
        final = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
    assert failed.status_code == 200 and "event: error" in failed.text
    assert retried.status_code == 200 and "event: completed" in retried.text
    assert [item["state"] for item in final["turns"]] == ["failed", "completed"]
    assert final["turns"][1]["origin"] == "retry"
    assert final["turns"][1]["derived_from_turn_id"] == source_turn_id
    assert final["turns"][1]["messages"][0]["content"] == "canonical retry source"


@pytest.mark.asyncio
async def test_stop_requests_native_cancel_and_terminal_is_durable(tmp_path: Path) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = BlockingGeneration()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
    )
    service.recover_incomplete_conversations()
    runtime = WebRuntime(
        conversation=cast(object, generation),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=service,
    )
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client, "stop-create")
        conversation_id = detail["conversation_id"]
        stream_task = asyncio.create_task(
            client.post(
                f"/api/v2/conversations/{conversation_id}/turns/stream",
                json={
                    "content": "stop source",
                    "settings": settings_payload(),
                    "operation_id": "stop-turn",
                    "expected_revision": 1,
                },
            )
        )
        for _ in range(100):
            current = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
            if current["turns"] and current["turns"][0]["state"] == "generating":
                break
            await asyncio.sleep(0.005)
        else:
            pytest.fail("persistent generation did not reach durable generating state")
        stopped = await client.post(
            f"/api/v2/conversations/{conversation_id}/generations/request-blocking/stop",
            json={"request_id": "request-blocking", "expected_revision": 3},
        )
        streamed = await asyncio.wait_for(stream_task, timeout=2.0)
        final = (await client.get(f"/api/v2/conversations/{conversation_id}")).json()
    assert stopped.status_code == 200
    assert stopped.json() == {"status": "cancellation_requested"}
    assert "event: cancelled" in streamed.text
    assert final["storage_revision"] == 4
    assert final["turns"][0]["state"] == "cancelled"


@pytest.mark.asyncio
async def test_v2_rejects_full_history_scope_and_sensitive_extra_fields(tmp_path: Path) -> None:
    runtime, store, _ = persistent_runtime(tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        before = store.database_path.read_bytes()
        rejected = await client.post(
            f"/api/v2/conversations/{detail['conversation_id']}/turns/stream",
            json={
                "content": "safe",
                "settings": settings_payload(),
                "operation_id": "extra-fields",
                "expected_revision": 1,
                "messages": [{"role": "user", "content": "hidden-sentinel"}],
                "scope_id": "private-scope-sentinel",
                "prompt": "prompt-sentinel",
            },
        )
    assert rejected.status_code == 422
    assert rejected.json() == {"code": "invalid_request", "message": "The request is invalid."}
    assert store.database_path.read_bytes() == before
    database_text = before.decode("utf-8", errors="ignore")
    assert "hidden-sentinel" not in database_text
    assert "prompt-sentinel" not in database_text


@pytest.mark.asyncio
async def test_terminal_persistence_failure_emits_no_success_terminal(tmp_path: Path) -> None:
    store = FailingTerminalStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = Generation()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
    )
    service.recover_incomplete_conversations()
    runtime = WebRuntime(
        conversation=cast(object, generation),  # type: ignore[arg-type]
        snapshot=runtime_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=service,
    )
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await create(client)
        response = await client.post(
            f"/api/v2/conversations/{detail['conversation_id']}/turns/stream",
            json={
                "content": "canonical user",
                "settings": settings_payload(),
                "operation_id": "terminal-failure",
                "expected_revision": 1,
            },
        )
        persisted = await client.get(f"/api/v2/conversations/{detail['conversation_id']}")
    assert response.status_code == 200
    assert "event: completed" not in response.text
    assert "event: cancelled" not in response.text
    assert "event: error" not in response.text
    assert response.text.count('"durable_revision"') == 1
    assert persisted.json()["turns"][0]["state"] == "interrupted"
    assert len(persisted.json()["turns"][0]["messages"]) == 1


@pytest.mark.asyncio
async def test_disconnect_closes_on_producer_and_persists_interrupted(tmp_path: Path) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = SlowGeneration()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
    )
    service.recover_incomplete_conversations()
    conversation_id = ConversationId(value="conversation-disconnect")
    service.create_conversation(
        conversation_id=conversation_id,
        session_id=ConversationSessionId(value="session-disconnect"),
        operation_id=ConversationOperationId(value="create-disconnect"),
    )
    identities = _generation_identities("disconnect-action")
    request_contract = PersistentTurnStreamRequest.model_validate(
        {
            "content": "canonical user",
            "settings": settings_payload(),
            "operation_id": "disconnect-action",
            "expected_revision": 1,
        }
    )
    events = service.generate_turn(
        conversation_id=conversation_id,
        content=request_contract.content,
        settings=request_contract.settings,
        identities=identities,
        expected_revision=1,
    )

    class DisconnectedRequest:
        async def is_disconnected(self) -> bool:
            return True

    bridge = PersistentSseBridge(
        events=events,
        service=service,
        conversation_id=conversation_id,
        turn_id=identities.turn_id,
    )
    await bridge.prepare()
    chunks = []
    async for chunk in bridge.stream(cast(Request, DisconnectedRequest())):
        chunks.append(chunk)
    stored = service.get_conversation(conversation_id)
    assert chunks and "event: start" in chunks[0]
    assert stored.conversation.turns[0].state is ConversationTurnState.INTERRUPTED
    assert len(stored.conversation.messages) == 1
    assert generation.active is not None
    assert generation.start_thread_ids == generation.active.event_thread_ids[:1]
    assert len(set(generation.active.event_thread_ids)) == 1
