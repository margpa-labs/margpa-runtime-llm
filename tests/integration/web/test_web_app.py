"""In-process ASGI tests for the Phase 1-G delivery adapter."""

from __future__ import annotations

import asyncio
import base64
import threading
import time
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import cast

import httpx
import pytest
from fastapi import FastAPI
from starlette.requests import Request
from starlette.types import Message, Scope

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.public import (
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import (
    SummarizationConfig,
    SummaryMode,
)
from margpa_runtime_llm.web import streaming as web_streaming
from margpa_runtime_llm.web.app import SHUTDOWN_FAILURE_MESSAGE, create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import (
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)
from margpa_runtime_llm.web.streaming import SSE_QUEUE_CAPACITY, stream_session_as_sse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = PROJECT_ROOT / "src/margpa_runtime_llm/web/static"


class FakeStream:
    def __init__(
        self,
        text_deltas: tuple[str, ...] = ("<think>secret</think>safe",),
        delay_seconds: float = 0.0,
        finish_reason: FinishReason = FinishReason.STOP,
    ) -> None:
        self.text_deltas = text_deltas
        self.delay_seconds = delay_seconds
        self.finish_reason = finish_reason
        self.cancelled = False
        self.closed = False
        self.yielded_chunks = 0

    @property
    def generation_id(self) -> str:
        return "web-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        if self.cancelled:
            return GenerationTerminalState.CANCELLED
        if self.closed:
            return GenerationTerminalState.CLOSED_BY_CONSUMER
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        for sequence, text in enumerate(self.text_deltas):
            if self.delay_seconds:
                time.sleep(self.delay_seconds)
            self.yielded_chunks += 1
            yield GenerationChunk(
                request_id="web-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="web-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=self.finish_reason,
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


class ThreadAffineBlockingStream(FakeStream):
    def __init__(self) -> None:
        super().__init__(text_deltas=("released",))
        self.next_entered = threading.Event()
        self.release_next = threading.Event()
        self.iteration_thread_id: int | None = None
        self.cancel_thread_ids: list[int] = []
        self.close_thread_ids: list[int] = []

    def __iter__(self) -> Iterator[GenerationChunk]:
        self.iteration_thread_id = threading.get_ident()
        self.next_entered.set()
        if not self.release_next.wait(timeout=5.0):
            raise RuntimeError("the controlled native next() was not released")
        yield from super().__iter__()

    def cancel(self) -> None:
        current_thread_id = threading.get_ident()
        self.cancel_thread_ids.append(current_thread_id)
        self._assert_iteration_thread(current_thread_id)
        super().cancel()
        self.close()

    def close(self) -> None:
        current_thread_id = threading.get_ident()
        self.close_thread_ids.append(current_thread_id)
        self._assert_iteration_thread(current_thread_id)
        super().close()

    def _assert_iteration_thread(self, current_thread_id: int) -> None:
        if self.iteration_thread_id != current_thread_id:
            raise ValueError("generator already executing")


class FakeInference:
    def __init__(self, stream_factory: Callable[[], FakeStream] | None = None) -> None:
        self.requests: list[GenerationRequest] = []
        self.streams: list[FakeStream] = []
        self.stream_factory = stream_factory or FakeStream

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        stream = self.stream_factory()
        self.streams.append(stream)
        return stream


def presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def build_runtime(
    inference: FakeInference,
    closed: list[bool],
    *,
    thinking_control_available: bool = True,
) -> WebRuntime:
    conversation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.qwen3-4b-q4-k-m",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048,
            thinking_mode=ThinkingMode.ENABLED,
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        summarization=SummarizationConfig(),
        thinking_control_available=thinking_control_available,
    )
    return WebRuntime(
        conversation=conversation,
        snapshot=SafeRuntimeSnapshot(
            model_key="main.qwen3-4b-q4-k-m",
            profile_key="local.macos-arm64.metal",
            device_kind="gpu",
            acceleration_api="metal",
            defaults=RuntimeDefaults(
                response_language=ResponseLanguage.JA,
                max_new_tokens=2048,
                thinking_mode=ThinkingMode.DISABLED,
                thinking_visibility=ThinkingVisibility.HIDDEN,
                thinking_display_label="推論過程",
                thinking_control_available=thinking_control_available,
                summary_mode=SummaryMode.OFF,
            ),
        ),
        close_callback=lambda: closed.append(True),
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client


def basic_header() -> dict[str, str]:
    encoded = base64.b64encode(b"preview-user:preview-password").decode()
    return {"Authorization": f"Basic {encoded}"}


def request_payload(
    *,
    visibility: str = "hidden",
    thinking_mode: str = "disabled",
    summary_mode: str = "off",
) -> dict[str, object]:
    return {
        "messages": [{"role": "user", "content": "hello"}],
        "settings": {
            "response_language": "ja",
            "max_new_tokens": 2048,
            "thinking_mode": thinking_mode,
            "thinking_visibility": visibility,
            "summary_mode": summary_mode,
        },
    }


@pytest.mark.asyncio
async def test_health_is_minimal_and_runtime_factory_loads_once() -> None:
    inference = FakeInference()
    closed: list[bool] = []
    factory_calls = 0

    def factory() -> WebRuntime:
        nonlocal factory_calls
        factory_calls += 1
        return build_runtime(inference, closed)

    app = create_web_app(
        runtime_factory=factory,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        first = await client.get("/healthz")
        second = await client.get("/healthz")
        runtime = await client.get("/api/v1/runtime")

        assert first.json() == {"status": "ok"}
        assert second.json() == {"status": "ok"}
        assert runtime.status_code == 200
        assert factory_calls == 1
    assert closed == [True]


@pytest.mark.asyncio
async def test_basic_auth_protects_ui_assets_and_api_but_not_health() -> None:
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(
            mode=WebAuthMode.BASIC,
            username="preview-user",
            password="preview-password",
        ),
    )
    async with client_for(app) as client:
        assert (await client.get("/healthz")).status_code == 200
        for path in ("/", "/assets/app.js", "/api/v1/runtime"):
            response = await client.get(path)
            assert response.status_code == 401
            assert "WWW-Authenticate" in response.headers
        authorized = await client.get("/api/v1/runtime", headers=basic_header())

    payload = authorized.json()
    assert authorized.status_code == 200
    assert payload["model_key"] == "main.qwen3-4b-q4-k-m"
    serialized = authorized.text
    assert "preview-password" not in serialized
    assert str(PROJECT_ROOT) not in serialized


@pytest.mark.asyncio
async def test_chat_sse_hides_thinking_and_returns_canonical_final_once() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(thinking_mode="enabled"),
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.text.count("event: start") == 1
    assert response.text.count("event: completed") == 1
    assert "event: error" not in response.text
    assert "secret" not in response.text
    assert "safe" in response.text
    assert inference.requests[0].messages[-1].content == "hello"
    assert inference.requests[0].parameters.thinking_mode is ThinkingMode.ENABLED
    assert '"channel":"final"' in response.text
    assert '"channel":"reasoning"' not in response.text


@pytest.mark.asyncio
async def test_visible_thinking_and_final_use_separate_semantic_sse_channels() -> None:
    inference = FakeInference(
        lambda: FakeStream(text_deltas=("<think>visible reason</think>safe final",))
    )
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(thinking_mode="enabled", visibility="visible"),
        )

    assert response.status_code == 200
    assert '"channel":"reasoning","text":"visible reason"' in response.text
    assert '"channel":"final","text":"safe final"' in response.text
    assert '"content":"safe final"' in response.text
    assert '"content":"visible reason' not in response.text


@pytest.mark.asyncio
async def test_unavailable_thinking_control_is_reported_and_enablement_fails_closed() -> None:
    runtime = build_runtime(
        FakeInference(),
        [],
        thinking_control_available=False,
    )
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        snapshot = await client.get("/api/v1/runtime")
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(thinking_mode="enabled"),
        )

    assert snapshot.json()["defaults"]["thinking_control_available"] is False
    assert response.status_code == 400
    assert response.json()["code"] == "unsupported_capability"


@pytest.mark.asyncio
async def test_summary_sse_hides_original_then_presents_only_valid_summary() -> None:
    pending_streams = iter(
        (
            FakeStream(text_deltas=("<think>normal secret</think>Original answer",)),
            FakeStream(text_deltas=("<think>summary secret</think>Short summary",)),
        )
    )
    inference = FakeInference(lambda: next(pending_streams))
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(
                thinking_mode="enabled",
                visibility="visible",
                summary_mode="post_generation",
            ),
        )

    assert response.status_code == 200
    assert response.text.count("event: start") == 1
    assert response.text.count("event: status") == 1
    assert response.text.count("event: delta") == 1
    assert response.text.count("event: completed") == 1
    assert response.text.index("event: start") < response.text.index("event: status")
    assert response.text.index("event: status") < response.text.index("event: delta")
    assert "Short summary" in response.text
    assert "Original answer" not in response.text
    assert "normal secret" not in response.text
    assert "summary secret" not in response.text
    assert "original_assistant_message" not in response.text
    assert "summary_assistant_message" not in response.text
    assert '"summary_applied":true' in response.text
    assert '"fallback_used":false' in response.text
    assert len(inference.requests) == 2
    assert inference.requests[0].parameters.thinking_mode is ThinkingMode.ENABLED
    assert inference.requests[1].parameters.thinking_mode is ThinkingMode.DISABLED
    assert inference.requests[1].parameters.max_new_tokens == 1024
    assert inference.streams[0].closed is True
    assert inference.streams[1].closed is True


@pytest.mark.asyncio
async def test_summary_fallback_presents_original_once_as_assistant_message() -> None:
    pending_streams = iter(
        (
            FakeStream(text_deltas=("Original answer",)),
            FakeStream(text_deltas=("Incomplete summary",), finish_reason=FinishReason.LENGTH),
        )
    )
    inference = FakeInference(lambda: next(pending_streams))
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(summary_mode="post_generation"),
        )

    assistant_payload = '"assistant_message":{"role":"assistant","content":"Original answer"}'
    assert response.status_code == 200
    assert response.text.count(assistant_payload) == 1
    assert "Incomplete summary" not in response.text
    assert "original_assistant_message" not in response.text
    assert "summary_assistant_message" not in response.text
    assert '"summary_applied":false' in response.text
    assert '"fallback_used":true' in response.text


@pytest.mark.asyncio
async def test_request_validation_is_generic_and_rejects_client_system_role() -> None:
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    invalid = request_payload()
    invalid["messages"] = [{"role": "system", "content": "private input"}]
    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=invalid)

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_request",
        "message": "The request is invalid.",
    }
    assert "private input" not in response.text

    invalid_summary = request_payload(summary_mode="on")
    async with client_for(app) as client:
        summary_response = await client.post("/api/v1/chat/stream", json=invalid_summary)
    assert summary_response.status_code == 422
    assert summary_response.json()["code"] == "invalid_request"


@pytest.mark.asyncio
async def test_oversized_content_length_is_rejected_before_body_validation() -> None:
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            content=b"{}",
            headers={"Content-Length": "262145", "Content-Type": "application/json"},
        )

    assert response.status_code == 413
    assert response.json()["code"] == "request_too_large"


@pytest.mark.asyncio
async def test_busy_and_stop_endpoints_use_active_request_only() -> None:
    inference = FakeInference()
    closed: list[bool] = []
    runtime = build_runtime(inference, closed)
    active_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="active"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(active_input)
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        busy = await client.post("/api/v1/chat/stream", json=request_payload())
        wrong = await client.post("/api/v1/chat/stop", json={"request_id": "wrong"})
        stopped = await client.post(
            "/api/v1/chat/stop",
            json={"request_id": session.request_id},
        )
        events = list(session.events())

    assert busy.status_code == 409
    assert busy.json()["code"] == "model_busy"
    assert wrong.status_code == 404
    assert stopped.status_code == 200
    assert stopped.json() == {"status": "cancellation_requested"}
    assert events[-1].event.value == "cancelled"


def test_static_assets_are_local_thinking_aware_phase_1i_ui() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    markdown_script = (STATIC_ROOT / "safe_markdown.js").read_text(encoding="utf-8")
    package_init = (PROJECT_ROOT / "src/margpa_runtime_llm/__init__.py").read_text(encoding="utf-8")

    assert "https://" not in html
    assert "http://" not in html
    assert "innerHTML" not in script
    assert "innerHTML" not in markdown_script
    assert ".textContent" in script
    assert 'UI_LANGUAGE_KEY = "margpa.ui_language.v1"' in script
    assert script.count("localStorage.") == 2
    assert "要約モード" in html
    assert 'value="post_generation"' in html
    assert 'summary_mode: summaryMode?.value ?? "off"' in script
    assert "document.documentElement.lang = state.uiLanguage" in script
    assert "document.title =" in script
    assert "knownServerMessages" in script
    assert "要約により詳細、前提、注意事項等が省略・変形される可能性があります" in html
    assert "details, assumptions, or cautions may be omitted or altered" in script
    assert 'runtimeStatus: { kind: "loading"' in script
    assert "function renderRuntimeStatus()" in script
    assert 'kind: "known_error"' in script
    assert 'translationKey: "runtimeLoadFailed"' in script
    assert "runtimeText" not in script
    assert html.count("<select") == 1
    assert html.count('type="number"') == 1
    assert html.count('type="checkbox"') == 2
    assert html.count('type="radio"') == 2
    assert 'id="thinking-mode"' in html
    assert 'thinking_mode: elements.thinkingMode.checked ? "enabled" : "disabled"' in script
    assert 'data.channel === "reasoning"' in script
    assert 'data.channel === "final"' in script
    assert "renderSafeMarkdown(canonical)" in script
    assert "navigator.clipboard.writeText(canonicalText)" in script
    assert "clipboard.read" not in script
    assert "event.isComposing" in script
    assert "Cmd+Enter／Ctrl+Enterで送信" in html  # noqa: RUF001
    assert "Send with Cmd+Enter / Ctrl+Enter" in script
    assert 'type="module"' in html
    assert "日本語" in html
    assert "English" in html
    assert "Nazuna Research Governance LLM" in html
    assert "Nazuna Research Governance LLM" in package_init
    deprecated_name = "legacy-public-identity"
    assert deprecated_name not in html.lower()
    assert deprecated_name not in package_init.lower()


def test_sse_keepalive_contract_is_fixed_non_semantic_comment() -> None:
    assert web_streaming.SSE_KEEPALIVE_INTERVAL_SECONDS == 15.0
    assert web_streaming.SSE_KEEPALIVE_COMMENT == ": keepalive\n\n"
    assert "event:" not in web_streaming.SSE_KEEPALIVE_COMMENT
    assert "data:" not in web_streaming.SSE_KEEPALIVE_COMMENT


@pytest.mark.asyncio
async def test_token_limit_warning_precedes_completed_and_ui_preserves_it() -> None:
    inference = FakeInference(
        lambda: FakeStream(
            text_deltas=("<think>unfinished",),
            finish_reason=FinishReason.LENGTH,
        )
    )
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=request_payload())

    warning = '"code":"final_answer_token_limit"'
    assert response.status_code == 200
    assert warning in response.text
    assert response.text.index(warning) < response.text.index("event: completed")
    assert '"content":""' in response.text

    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    warning_branch = script.index('data.code === "final_answer_token_limit"')
    terminal_status = script.index("if (state.terminalWarning !== null)", warning_branch)
    completed_status = script.index('setStatus("completed"', terminal_status)
    assert warning_branch < terminal_status < completed_status
    assert 'state.messages.push({ role: "assistant", content: canonical })' in script
    assert 'state.messages.push({ role: "assistant", content: data.message })' not in script


@pytest.mark.asyncio
async def test_client_disconnect_requests_cooperative_cancel() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("one", "two"), delay_seconds=0.05))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="disconnect"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(generation_input)
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chat/stream",
        "raw_path": b"/api/v1/chat/stream",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": None,
        "server": None,
        "state": {},
    }

    async def receive() -> Message:
        return {"type": "http.disconnect"}

    request = Request(scope, receive)
    events = [chunk async for chunk in stream_session_as_sse(request, session)]

    assert any("event: start" in chunk for chunk in events)
    assert inference.streams == []
    assert session.finished is True
    assert runtime.conversation.active_request_id is None


def test_stop_during_summary_cancels_on_producer_thread_without_fallback() -> None:
    normal_stream = FakeStream(text_deltas=("Original answer",))
    summary_stream = ThreadAffineBlockingStream()
    pending_streams = iter((normal_stream, summary_stream))
    inference = FakeInference(lambda: next(pending_streams))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="summarize"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            summary_mode=SummaryMode.POST_GENERATION,
        ),
    )
    session = runtime.conversation.start(generation_input)
    events: list[object] = []

    producer = threading.Thread(target=lambda: events.extend(session.events()))
    producer.start()
    assert summary_stream.next_entered.wait(timeout=1.0)
    assert runtime.conversation.cancel(session.request_id)
    summary_stream.release_next.set()
    producer.join(timeout=2.0)

    assert producer.is_alive() is False
    assert summary_stream.cancel_thread_ids == [summary_stream.iteration_thread_id]
    assert summary_stream.close_thread_ids == [summary_stream.iteration_thread_id]
    serialized = repr(events)
    assert "cancelled" in serialized
    assert "summary_fallback_original" not in serialized
    assert "completed" not in serialized
    assert runtime.conversation.active_request_id is None


@pytest.mark.asyncio
async def test_backpressured_consumer_close_releases_session_and_generation_gate() -> None:
    first_stream = FakeStream(
        text_deltas=tuple(f"chunk-{index}" for index in range(SSE_QUEUE_CAPACITY * 3))
    )
    second_stream = FakeStream(text_deltas=("next",))
    pending_streams = iter((first_stream, second_stream))
    inference = FakeInference(lambda: next(pending_streams))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="backpressure"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(generation_input)
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chat/stream",
        "raw_path": b"/api/v1/chat/stream",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": None,
        "server": None,
        "state": {},
    }

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    stream = cast(
        AsyncGenerator[str, None],
        stream_session_as_sse(Request(scope, receive), session),
    )
    first_event = await anext(stream)
    for _ in range(100):
        if first_stream.yielded_chunks > SSE_QUEUE_CAPACITY:
            break
        await asyncio.sleep(0.01)

    assert "event: start" in first_event
    assert first_stream.yielded_chunks > SSE_QUEUE_CAPACITY
    await asyncio.wait_for(stream.aclose(), timeout=2.0)

    assert await asyncio.to_thread(session.wait, 2.0)
    assert first_stream.cancelled is True
    assert runtime.conversation.active_request_id is None
    producer_name = f"margpa-sse-producer-{session.request_id}"
    assert not any(
        task.get_name() == producer_name and not task.done() for task in asyncio.all_tasks()
    )

    next_session = runtime.conversation.start(generation_input)
    next_events = list(next_session.events())
    assert next_events[-1].event.value == "completed"
    assert runtime.conversation.active_request_id is None


@pytest.mark.asyncio
@pytest.mark.parametrize("summary_mode", [SummaryMode.OFF, SummaryMode.POST_GENERATION])
async def test_keepalive_during_silent_normal_or_buffered_summary_generation(
    monkeypatch: pytest.MonkeyPatch,
    summary_mode: SummaryMode,
) -> None:
    monkeypatch.setattr(web_streaming, "SSE_KEEPALIVE_INTERVAL_SECONDS", 0.01)
    blocking_stream = ThreadAffineBlockingStream()
    pending_streams: Iterator[FakeStream]
    if summary_mode is SummaryMode.OFF:
        pending_streams = iter((blocking_stream,))
    else:
        pending_streams = iter((FakeStream(text_deltas=("Original answer",)), blocking_stream))
    inference = FakeInference(lambda: next(pending_streams))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="keepalive"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            summary_mode=summary_mode,
        ),
    )
    session = runtime.conversation.start(generation_input)
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chat/stream",
        "raw_path": b"/api/v1/chat/stream",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": None,
        "server": None,
        "state": {},
    }

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    stream = cast(
        AsyncGenerator[str, None],
        stream_session_as_sse(Request(scope, receive), session),
    )
    chunks = [await anext(stream)]
    if summary_mode is SummaryMode.POST_GENERATION:
        chunks.append(await anext(stream))
        assert "event: status" in chunks[-1]
    assert await asyncio.to_thread(blocking_stream.next_entered.wait, 1.0)
    chunks.append(await asyncio.wait_for(anext(stream), timeout=1.0))
    assert chunks[-1] == web_streaming.SSE_KEEPALIVE_COMMENT
    assert "event:" not in chunks[-1]
    blocking_stream.release_next.set()
    chunks.extend([chunk async for chunk in stream])

    wire = "".join(chunks)
    assert wire.count(web_streaming.SSE_KEEPALIVE_COMMENT) >= 1
    assert wire.count("event: completed") == 1
    assert session.finished
    assert runtime.conversation.active_request_id is None
    producer_name = f"margpa-sse-producer-{session.request_id}"
    assert not any(
        task.get_name() == producer_name and not task.done() for task in asyncio.all_tasks()
    )


@pytest.mark.asyncio
async def test_consumer_close_after_keepalive_cancels_native_iteration_on_producer_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(web_streaming, "SSE_KEEPALIVE_INTERVAL_SECONDS", 0.01)
    first_stream = ThreadAffineBlockingStream()
    second_stream = FakeStream(text_deltas=("next",))
    pending_streams = iter((first_stream, second_stream))
    inference = FakeInference(lambda: next(pending_streams))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="thread-affine"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(generation_input)
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chat/stream",
        "raw_path": b"/api/v1/chat/stream",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": None,
        "server": None,
        "state": {},
    }

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    stream = cast(
        AsyncGenerator[str, None],
        stream_session_as_sse(Request(scope, receive), session),
    )
    first_event = await anext(stream)
    assert "event: start" in first_event
    assert await asyncio.to_thread(first_stream.next_entered.wait, 1.0)
    keepalive = await asyncio.wait_for(anext(stream), timeout=1.0)
    assert keepalive == web_streaming.SSE_KEEPALIVE_COMMENT

    close_task = asyncio.create_task(stream.aclose())
    await asyncio.sleep(0)
    closed_before_native_boundary = close_task.done()
    first_stream.release_next.set()

    assert closed_before_native_boundary is False
    await asyncio.wait_for(close_task, timeout=2.0)
    assert await asyncio.to_thread(session.wait, 2.0)
    assert first_stream.iteration_thread_id is not None
    assert first_stream.cancel_thread_ids == [first_stream.iteration_thread_id]
    assert first_stream.close_thread_ids == [first_stream.iteration_thread_id]
    assert runtime.conversation.active_request_id is None
    producer_name = f"margpa-sse-producer-{session.request_id}"
    assert not any(
        task.get_name() == producer_name and not task.done() for task in asyncio.all_tasks()
    )

    next_session = runtime.conversation.start(generation_input)
    next_events = list(next_session.events())
    assert next_events[-1].event.value == "completed"
    assert runtime.conversation.active_request_id is None


@pytest.mark.asyncio
async def test_cleanup_timeout_fails_without_cross_thread_native_cancel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(web_streaming, "PRODUCER_CLEANUP_TIMEOUT_SECONDS", 0.05)
    first_stream = ThreadAffineBlockingStream()
    second_stream = FakeStream(text_deltas=("next",))
    pending_streams = iter((first_stream, second_stream))
    inference = FakeInference(lambda: next(pending_streams))
    runtime = build_runtime(inference, [])
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="timeout"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(generation_input)
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chat/stream",
        "raw_path": b"/api/v1/chat/stream",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": None,
        "server": None,
        "state": {},
    }

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    stream = cast(
        AsyncGenerator[str, None],
        stream_session_as_sse(Request(scope, receive), session),
    )
    assert "event: start" in await anext(stream)
    assert await asyncio.to_thread(first_stream.next_entered.wait, 1.0)

    with pytest.raises(RuntimeError, match="SSE producer did not stop"):
        await stream.aclose()

    assert first_stream.cancel_thread_ids == []
    assert first_stream.close_thread_ids == []
    assert runtime.conversation.active_request_id == session.request_id

    first_stream.release_next.set()
    assert await asyncio.to_thread(session.wait, 2.0)
    producer_name = f"margpa-sse-producer-{session.request_id}"
    for _ in range(100):
        if not any(
            task.get_name() == producer_name and not task.done() for task in asyncio.all_tasks()
        ):
            break
        await asyncio.sleep(0.01)

    assert first_stream.cancel_thread_ids == [first_stream.iteration_thread_id]
    assert first_stream.close_thread_ids == [first_stream.iteration_thread_id]
    assert runtime.conversation.active_request_id is None
    assert not any(
        task.get_name() == producer_name and not task.done() for task in asyncio.all_tasks()
    )

    next_session = runtime.conversation.start(generation_input)
    next_events = list(next_session.events())
    assert next_events[-1].event.value == "completed"


def test_runtime_shutdown_is_thread_affine_and_closes_model_once() -> None:
    first_stream = ThreadAffineBlockingStream()
    second_stream = FakeStream(text_deltas=("next",))
    pending_streams = iter((first_stream, second_stream))
    inference = FakeInference(lambda: next(pending_streams))
    closed: list[bool] = []
    runtime = build_runtime(inference, closed)
    generation_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="shutdown"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session = runtime.conversation.start(generation_input)
    consumed_events: list[object] = []

    def consume() -> None:
        consumed_events.extend(session.events())

    producer = threading.Thread(target=consume, name="test-native-producer")
    producer.start()
    assert first_stream.next_entered.wait(timeout=1.0)

    shutdown_errors: list[RuntimeError] = []

    def shutdown() -> None:
        try:
            runtime.close(timeout=0.05)
        except RuntimeError as exc:
            shutdown_errors.append(exc)

    shutdown_worker = threading.Thread(target=shutdown, name="test-shutdown-worker")
    shutdown_worker.start()
    shutdown_worker.join(timeout=1.0)

    assert shutdown_worker.is_alive() is False
    assert [str(error) for error in shutdown_errors] == [
        "The active generation did not stop during shutdown."
    ]
    assert first_stream.cancel_thread_ids == []
    assert first_stream.close_thread_ids == []
    assert runtime.conversation.active_request_id == session.request_id
    assert closed == []

    first_stream.release_next.set()
    producer.join(timeout=2.0)

    assert producer.is_alive() is False
    assert consumed_events
    assert first_stream.cancel_thread_ids == [first_stream.iteration_thread_id]
    assert first_stream.close_thread_ids == [first_stream.iteration_thread_id]
    assert runtime.conversation.active_request_id is None

    next_session = runtime.conversation.start(generation_input)
    next_events = list(next_session.events())
    assert next_events[-1].event.value == "completed"

    runtime.close(timeout=0.05)
    runtime.close(timeout=0.05)
    assert closed == [True]


@pytest.mark.asyncio
async def test_lifespan_surfaces_sanitized_shutdown_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    runtime = build_runtime(FakeInference(), [])
    private_failure = f"private shutdown failure at {PROJECT_ROOT}"

    def fail_close() -> None:
        raise RuntimeError(private_failure)

    runtime.close_callback = fail_close
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    with caplog.at_level("ERROR", logger="margpa_runtime_llm.web.app"):
        with pytest.raises(RuntimeError, match=SHUTDOWN_FAILURE_MESSAGE):
            async with app.router.lifespan_context(app):
                pass

    assert caplog.messages == [SHUTDOWN_FAILURE_MESSAGE]
    assert private_failure not in caplog.text
    assert str(PROJECT_ROOT) not in caplog.text
