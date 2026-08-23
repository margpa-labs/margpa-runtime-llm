"""In-process ASGI tests for the Phase 1-G delivery adapter."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import re
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
from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_governance_definitions_runtime,
)
from margpa_runtime_llm.modules.audit_evidence.generation_observation import (
    GenerationObserverStatus,
)
from margpa_runtime_llm.modules.conversation.public import (
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationAugmentation,
    DocumentationCitation,
    DocumentationEvidence,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRagAvailability,
    DocumentationRagRequestContext,
    DocumentationRetrievalState,
)
from margpa_runtime_llm.modules.documentation_rag.ports import RagOrchestratorPort
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
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage
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
from margpa_runtime_llm.web.access_profiles import (
    DocumentationRagEffectiveState,
    OptionalControlMode,
    load_web_access_profile,
)
from margpa_runtime_llm.web.app import (
    SHUTDOWN_FAILURE_MESSAGE,
    create_web_app,
    stream_session_with_control_policy,
)
from margpa_runtime_llm.web.auth import (
    WebAccessPolicy,
    WebAuthMode,
    load_web_access_policy,
)
from margpa_runtime_llm.web.contracts import (
    DocumentationRagRuntimeSnapshot,
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)
from margpa_runtime_llm.web.streaming import SSE_QUEUE_CAPACITY, stream_session_as_sse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_PROFILE = load_web_access_profile(PROJECT_ROOT / "config/web_profiles/public_demo.toml")


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


class RecordingControlPolicy:
    mode = OptionalControlMode.OFF

    def __init__(self) -> None:
        self.calls: list[str] = []

    def check_request(self) -> None:
        self.calls.append("check_request")

    def before_generation(self) -> None:
        self.calls.append("before_generation")

    def observe_generation(self) -> None:
        self.calls.append("observe_generation")

    def after_generation(self) -> None:
        self.calls.append("after_generation")


class RecordingGenerationObserver:
    def __init__(self) -> None:
        self.started_calls: list[dict[str, object]] = []
        self.terminal_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return True

    def status(self) -> GenerationObserverStatus:
        return GenerationObserverStatus()

    def observe_generation_started(self, *, request_id: str, profile_key: str) -> None:
        self.started_calls.append({"request_id": request_id, "profile_key": profile_key})

    def observe_generation_terminal(self, **kwargs: object) -> None:
        self.terminal_calls.append(dict(kwargs))


class RaisingGenerationObserver:
    def __init__(self) -> None:
        self._degraded_calls = 0

    def is_active(self) -> bool:
        return True

    def status(self) -> GenerationObserverStatus:
        return GenerationObserverStatus(
            degraded=self._degraded_calls > 0,
            degraded_reason_code="evidence_write_failed" if self._degraded_calls > 0 else None,
            degraded_event_count=self._degraded_calls,
        )

    def observe_generation_started(self, **kwargs: object) -> None:
        self._degraded_calls += 1
        raise RuntimeError("generation observer failure")

    def observe_generation_terminal(self, **kwargs: object) -> None:
        self._degraded_calls += 1
        raise RuntimeError("generation observer failure")


class InactiveSpyGenerationObserver:
    """`is_active() -> False`: a P3-CODEX-002 Spy proving the Hook itself
    is never called (not merely that it writes nothing) while Mode is
    off — the caller must never even construct a Tracker."""

    def __init__(self) -> None:
        self.started_calls: list[dict[str, object]] = []
        self.terminal_calls: list[dict[str, object]] = []

    def is_active(self) -> bool:
        return False

    def status(self) -> GenerationObserverStatus:
        return GenerationObserverStatus()

    def observe_generation_started(self, **kwargs: object) -> None:
        self.started_calls.append(dict(kwargs))

    def observe_generation_terminal(self, **kwargs: object) -> None:
        self.terminal_calls.append(dict(kwargs))


class FakeDocumentationRag:
    def __init__(
        self,
        citation_path: str = "docs/project/current/requirements_ja.md",
    ) -> None:
        self.queries: list[str] = []
        self.request_contexts: list[DocumentationRagRequestContext] = []
        self.citation_path = citation_path

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> DocumentationAugmentation:
        self.request_contexts.append(request_context)
        return self.augment(query_text, cancelled=cancelled)

    def augment(
        self,
        query_text: str,
        *,
        cancelled: Callable[[], bool] | None = None,
    ) -> DocumentationAugmentation:
        del cancelled
        self.queries.append(query_text)
        citation = DocumentationCitation(
            citation_id="citation-1",
            project_relative_path=self.citation_path,
            heading_breadcrumb="Requirements",
            chunk_id=hashlib.sha512(b"chunk").hexdigest(),
            document_sha512=hashlib.sha512(b"document").hexdigest(),
            retrieval_score=3.0,
            selected_order=1,
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            reference_message="untrusted documentation reference",
            citations=(citation,),
            evidence=DocumentationEvidence(
                query_digest=hashlib.sha512(query_text.encode()).hexdigest(),
                corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
                retriever_key="field_weighted_bm25",
                retriever_version="1",
                selected_chunk_ids=(citation.chunk_id,),
                selected_document_digests=(citation.document_sha512,),
                selected_scores=(citation.retrieval_score,),
                base_prompt_used=64,
                base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
                base_prompt_exact=True,
                context_budget=768,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=100,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=768,
                context_token_budget_used=True,
                retrieved_chunk_count=1,
                assembled_block_count=1,
                identifier_subject_count=1,
                retrieval_covered_subject_count=1,
                retrieval_uncovered_subject_count=0,
                covered_subject_count=1,
                uncovered_subject_count=0,
                grounding_state=DocumentationGroundingState.GROUNDED_READY,
                generation_allowed=True,
                retrieval_duration_ms=1.0,
            ),
            document_count=1,
            selected_chunk_count=1,
            duration_ms=1.0,
        )


def presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def exact_chat_prompt_count(
    messages: tuple[ChatMessage, ...],
    thinking_mode: ThinkingMode,
) -> int:
    return sum(len(message.content) for message in messages) + (
        1 if thinking_mode is ThinkingMode.ENABLED else 0
    )


def build_runtime(
    inference: FakeInference,
    closed: list[bool],
    *,
    thinking_control_available: bool = True,
    documentation_rag: RagOrchestratorPort | None = None,
    documentation_rag_availability: DocumentationRagAvailability = (
        DocumentationRagAvailability.UNAVAILABLE
    ),
    documentation_rag_state: DocumentationRagEffectiveState = (
        DocumentationRagEffectiveState.UNAVAILABLE
    ),
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
        documentation_rag=documentation_rag,
        documentation_rag_availability=documentation_rag_availability,
        chat_prompt_token_counter=exact_chat_prompt_count,
        effective_context_size=4096,
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
            documentation_rag=DocumentationRagRuntimeSnapshot(
                effective_state=documentation_rag_state,
                control_available=(
                    documentation_rag_availability is DocumentationRagAvailability.AVAILABLE
                ),
                provider_display_name=(
                    "Local lexical documentation" if documentation_rag is not None else None
                ),
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
    documentation_rag_mode: str = "disabled",
) -> dict[str, object]:
    return {
        "messages": [{"role": "user", "content": "hello"}],
        "settings": {
            "response_language": "ja",
            "max_new_tokens": 2048,
            "thinking_mode": thinking_mode,
            "thinking_visibility": visibility,
            "summary_mode": summary_mode,
            "documentation_rag_mode": documentation_rag_mode,
        },
    }


def normalize_request_ids(text: str) -> str:
    """Blank out the per-call random `request_id` so two independently
    generated SSE streams can be compared shape-for-shape."""

    return re.sub(r'"request_id":\s*"[^"]*"', '"request_id":"<id>"', text)


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
async def test_public_demo_is_credentialless_with_chat_controls_and_public_rag() -> None:
    inference = FakeInference()
    rag = FakeDocumentationRag("docs/public/overview_en.md")
    app = create_web_app(
        runtime_factory=lambda: build_runtime(
            inference,
            [],
            documentation_rag=rag,
            documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
            documentation_rag_state=DocumentationRagEffectiveState.ENABLED,
        ),
        access_policy=load_web_access_policy({}, profile=PUBLIC_PROFILE),
    )

    async with client_for(app) as client:
        root = await client.get("/")
        runtime = await client.get("/api/v1/runtime")
        stream = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(
                thinking_mode="enabled",
                visibility="visible",
                summary_mode="post_generation",
            ),
        )
        inactive_stop = await client.post(
            "/api/v1/chat/stop",
            json={"request_id": "not-active"},
        )
        rag_override = await client.post(
            "/api/v1/chat/stream",
            json={
                **request_payload(),
                "documentation_rag": "enabled",
            },
        )
        valid_shape_rag_override = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(documentation_rag_mode="enabled"),
        )

    assert root.status_code == 200
    assert runtime.status_code == 200
    assert stream.status_code == 200
    assert "event: completed" in stream.text
    assert inactive_stop.status_code == 404
    assert rag_override.status_code == 422
    assert rag_override.json() == {
        "code": "invalid_request",
        "message": "The request is invalid.",
    }
    assert valid_shape_rag_override.status_code == 200
    assert "docs/public/overview_en.md" in valid_shape_rag_override.text
    assert rag.queries == ["hello"]
    assert inference.requests
    for response in (
        root,
        runtime,
        stream,
        inactive_stop,
        rag_override,
        valid_shape_rag_override,
    ):
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert str(PROJECT_ROOT) not in response.text


@pytest.mark.asyncio
async def test_local_documentation_rag_runtime_stream_and_system_citation() -> None:
    inference = FakeInference()
    rag = FakeDocumentationRag()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(
            inference,
            [],
            documentation_rag=rag,
            documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
            documentation_rag_state=DocumentationRagEffectiveState.ENABLED,
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        snapshot = await client.get("/api/v1/runtime")
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(documentation_rag_mode="enabled"),
        )

    assert snapshot.json()["documentation_rag"] == {
        "effective_state": "enabled",
        "control_available": True,
        "provider_display_name": "Local lexical documentation",
        "default_mode": "disabled",
        "schema_version": "1",
    }
    assert rag.queries == ["hello"]
    assert len(rag.request_contexts) == 1
    request_context = rag.request_contexts[0]
    assert request_context.effective_context_size == 4096
    assert request_context.requested_max_new_tokens == 2048
    assert request_context.prompt_token_count_exact is True
    assert request_context.system_history_current_prompt_tokens is not None
    assert "event: retrieval" in response.text
    assert "docs/project/current/requirements_ja.md" in response.text
    assert str(PROJECT_ROOT) not in response.text
    assert inference.requests[0].messages[1].name == "documentation_reference"
    assert (
        request_context.system_history_current_prompt_tokens
        + request_context.requested_max_new_tokens
        <= request_context.effective_context_size
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("summary_mode", ["off", "post_generation"])
async def test_control_policy_wraps_completed_and_summary_generation(
    summary_mode: str,
) -> None:
    policy = RecordingControlPolicy()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
        control_policy=policy,
    )

    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=request_payload(summary_mode=summary_mode),
        )

    assert response.status_code == 200
    assert "event: completed" in response.text
    assert app.state.public_control_policy is policy
    assert policy.calls[:2] == ["check_request", "before_generation"]
    assert policy.calls[-1] == "after_generation"
    assert policy.calls.count("after_generation") == 1
    assert set(policy.calls[2:-1]) == {"observe_generation"}


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal_kind", ["cancelled", "error"])
async def test_control_policy_finalizes_cancelled_and_error_generation_once(
    terminal_kind: str,
) -> None:
    if terminal_kind == "cancelled":
        inference = FakeInference(
            lambda: FakeStream(
                text_deltas=(),
                finish_reason=FinishReason.CANCELLED,
            )
        )
    else:

        class FailingStream(FakeStream):
            def __iter__(self) -> Iterator[GenerationChunk]:
                raise RuntimeError("private generation failure")
                yield  # pragma: no cover

        inference = FakeInference(FailingStream)

    policy = RecordingControlPolicy()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
        control_policy=policy,
    )

    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=request_payload())

    assert response.status_code == 200
    assert f"event: {terminal_kind}" in response.text
    assert policy.calls[:2] == ["check_request", "before_generation"]
    assert policy.calls[-1] == "after_generation"
    assert policy.calls.count("after_generation") == 1
    assert set(policy.calls[2:-1]) == {"observe_generation"}


@pytest.mark.asyncio
async def test_generation_observer_records_start_and_terminal_without_altering_the_stream() -> None:
    observer = RecordingGenerationObserver()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.generation_observer = observer

    bare_app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        observed = await client.post("/api/v1/chat/stream", json=request_payload())
    async with client_for(bare_app) as client:
        bare = await client.post("/api/v1/chat/stream", json=request_payload())

    assert observed.status_code == 200
    assert normalize_request_ids(observed.text) == normalize_request_ids(bare.text)
    assert len(observer.started_calls) == 1
    assert observer.started_calls[0]["profile_key"] == "local.macos-arm64.metal"
    assert len(observer.terminal_calls) == 1
    assert observer.terminal_calls[0]["stop_reason"] == "stop"
    assert observer.terminal_calls[0]["error_count"] == 0


@pytest.mark.asyncio
async def test_an_inactive_generation_observer_receives_zero_calls_not_just_zero_writes() -> None:
    observer = InactiveSpyGenerationObserver()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.generation_observer = observer

    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=request_payload())

    assert response.status_code == 200
    assert "event: completed" in response.text
    assert observer.started_calls == []
    assert observer.terminal_calls == []


@pytest.mark.asyncio
async def test_a_raising_generation_observer_never_alters_the_sse_stream() -> None:
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.generation_observer = RaisingGenerationObserver()

    bare_app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )

    async with client_for(app) as client:
        observed = await client.post("/api/v1/chat/stream", json=request_payload())
    async with client_for(bare_app) as client:
        bare = await client.post("/api/v1/chat/stream", json=request_payload())

    assert observed.status_code == 200
    assert normalize_request_ids(observed.text) == normalize_request_ids(bare.text)


@pytest.mark.asyncio
async def test_evidence_write_failure_leaves_generation_ok_but_degrades_status() -> None:
    observer = RaisingGenerationObserver()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.generation_observer = observer
    app.state.governance_definitions_runtime = build_governance_definitions_runtime(
        definitions_root=None
    )

    async with client_for(app) as client:
        pre_failure_status = await client.get("/api/v3/governance/runtime")
        generation = await client.post("/api/v1/chat/stream", json=request_payload())
        post_failure_status = await client.get("/api/v3/governance/runtime")

    assert pre_failure_status.status_code == 200
    assert pre_failure_status.json()["evidence"] == {
        "degraded": False,
        "degraded_reason_code": None,
        "degraded_event_count": 0,
    }

    assert generation.status_code == 200
    assert "event: completed" in generation.text
    assert "event: error" not in generation.text

    assert post_failure_status.status_code == 200
    evidence = post_failure_status.json()["evidence"]
    assert evidence["degraded"] is True
    assert evidence["degraded_reason_code"] == "evidence_write_failed"
    assert evidence["degraded_event_count"] == 2


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
    # Three STATUS events per Turn now (P6-CODEX-012, Second Rework):
    # "preparing" and "guarding" precede the Turn's own START event, and
    # "summarizing_answer" (this test's original concern) still follows it.
    assert response.text.count("event: status") == 3
    assert response.text.count("event: delta") == 1
    assert response.text.count("event: completed") == 1
    assert response.text.index("event: start") < response.text.index("summarizing_answer")
    assert response.text.index("summarizing_answer") < response.text.index("event: delta")
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
    policy = RecordingControlPolicy()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(FakeInference(), []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
        control_policy=policy,
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
    assert policy.calls == []


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
    policy = RecordingControlPolicy()
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
        control_policy=policy,
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
    assert policy.calls == ["check_request", "before_generation", "after_generation"]


def test_package_identity_naming_is_current() -> None:
    # The frontend (React/Vite, see frontend/) now owns the UI-copy and
    # markup contracts this used to grep out of the static app.js/index.html
    # source; that coverage lives in the frontend's own Vitest suite
    # (frontend/src/**/*.test.tsx) since bundled/minified output no longer
    # contains those literal identifiers. This keeps only the one assertion
    # here that was never about the frontend: the backend package's own
    # product-naming string.
    package_init = (PROJECT_ROOT / "src/margpa_runtime_llm/__init__.py").read_text(encoding="utf-8")

    assert "Nazuna Research Governance LLM" in package_init
    deprecated_name = "legacy-public-identity"
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
    # The UI's handling of this warning (preserving it as the terminal status
    # instead of overwriting it with "completed") is a frontend behavior now
    # covered by frontend/src/App.test.tsx, not this backend SSE contract.


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
    policy = RecordingControlPolicy()
    events = [
        chunk
        async for chunk in stream_session_with_control_policy(
            request=request,
            session=session,
            control_policy=policy,
        )
    ]

    # P6-CODEX-012 (Second Rework): the turn may be cooperatively cancelled
    # before its own START event is reached (it now follows two leading
    # STATUS markers) — any real event proves the turn genuinely began.
    assert any("event: start" in chunk or "event: status" in chunk for chunk in events)
    assert inference.streams == []
    assert session.finished is True
    assert runtime.conversation.active_request_id is None
    assert policy.calls == ["observe_generation", "after_generation"]


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
    # P6-CODEX-012 (Second Rework): drain the two new leading STATUS
    # markers ("preparing", "guarding") before the Turn's own START event.
    preparing_event = await anext(stream)
    assert "preparing" in preparing_event
    guarding_event = await anext(stream)
    assert "guarding" in guarding_event
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
    # P6-CODEX-012 (Second Rework): every Turn now opens with two
    # additional STATUS markers ("preparing", "guarding") before its own
    # START event — drain those here so the keepalive check below still
    # observes the first genuinely *blocked* gap, not one of these.
    chunks = [await anext(stream)]
    assert "preparing" in chunks[-1]
    chunks.append(await anext(stream))
    assert "guarding" in chunks[-1]
    chunks.append(await anext(stream))
    assert "event: start" in chunks[-1]
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
    # P6-CODEX-012 (Second Rework): drain the two new leading STATUS
    # markers ("preparing", "guarding") before the Turn's own START event.
    assert "preparing" in await anext(stream)
    assert "guarding" in await anext(stream)
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
    # P6-CODEX-012 (Second Rework): drain the two new leading STATUS
    # markers ("preparing", "guarding") before the Turn's own START event.
    assert "preparing" in await anext(stream)
    assert "guarding" in await anext(stream)
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
