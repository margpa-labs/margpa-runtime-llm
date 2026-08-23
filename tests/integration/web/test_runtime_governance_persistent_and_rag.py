"""Phase 4 Golden Matrix cross-checks: Persistent conversation turns and
Documentation RAG-augmented requests both flow through the same Runtime
Governance hooks as the plain ephemeral path (P4-G-WU-001).

`PersistentConversationService` and `ConversationGenerationSession`'s RAG
retrieval both wrap the *same* `ConversationGenerationService` instance
that ephemeral chat uses (`bootstrap/web_application.py` wires one
Service into both `ConversationGenerationService(...)` itself and
`PersistentConversationService(generation_service=conversation, ...)`),
so these tests build that same real Service — with real Governance hooks
attached — rather than the lightweight Session/Generation test doubles
`test_persistent_web_app.py` uses elsewhere, since those doubles bypass
`ConversationGenerationSession` entirely and would prove nothing about
Governance wiring.
"""

from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
)
from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.domain import ConversationScopeId
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
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
from margpa_runtime_llm.modules.documentation_rag.ports import CancellationCheck
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
from margpa_runtime_llm.modules.runtime_governance.domain import (
    EvaluationMethod,
    ExecutionDescriptor,
    RuntimeCapabilitySnapshot,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

SCOPE = ConversationScopeId(value="p4-governance-scope")


class FakeStream:
    def __init__(self, text_deltas: tuple[str, ...] = ("a real answer",)) -> None:
        self.text_deltas = text_deltas
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "gov-persistent-rag-generation"

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
            yield GenerationChunk(
                request_id="gov-persistent-rag-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="gov-persistent-rag-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
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


class FakeInference:
    def __init__(self, *, empty_output: bool = False) -> None:
        self.requests: list[GenerationRequest] = []
        self.empty_output = empty_output

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return FakeStream(text_deltas=() if self.empty_output else ("a real answer",))


class RecordingContextualRag:
    """A minimal Contextual RAG Orchestrator that always injects a large
    fixed `reference_message` block — enough to push a tiny snapshot
    budget over the edge, so a Pre-point Enforce reaction proves the
    Governance snapshot was built from the *augmented* request, not the
    raw pre-RAG one."""

    def __init__(self, *, injected_context: str) -> None:
        self.injected_context = injected_context
        self.contexts: list[DocumentationRagRequestContext] = []

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        del cancelled
        self.contexts.append(request_context)
        citation = DocumentationCitation(
            citation_id="citation-1",
            project_relative_path="docs/example.md",
            heading_breadcrumb="Example",
            chunk_id=hashlib.sha512(b"chunk").hexdigest(),
            document_sha512=hashlib.sha512(b"document").hexdigest(),
            retrieval_score=1.0,
            selected_order=1,
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            reference_message=self.injected_context,
            citations=(citation,),
            evidence=DocumentationEvidence(
                query_digest=hashlib.sha512(query_text.encode()).hexdigest(),
                corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
                retriever_key="test",
                retriever_version="1",
                selected_chunk_ids=(citation.chunk_id,),
                selected_document_digests=(citation.document_sha512,),
                selected_scores=(citation.retrieval_score,),
                base_prompt_used=request_context.system_history_current_prompt_tokens,
                base_prompt_unit=request_context.prompt_measurement_unit,
                base_prompt_exact=request_context.prompt_token_count_exact,
                context_budget=0,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=0,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=0,
                context_token_budget_used=True,
                retrieved_chunk_count=1,
                assembled_block_count=1,
                identifier_subject_count=0,
                retrieval_covered_subject_count=0,
                retrieval_uncovered_subject_count=0,
                covered_subject_count=0,
                uncovered_subject_count=0,
                grounding_state=DocumentationGroundingState.GROUNDED_READY,
                generation_allowed=True,
                retrieval_duration_ms=0,
            ),
            document_count=1,
            selected_chunk_count=1,
            duration_ms=0,
        )


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor() -> ExecutionDescriptor:
    # Enforce Availability now genuinely requires a bound, non-empty
    # Descriptor set (P4-CODEX-004 Rework) — a real Test double stands
    # in for the Reference Bundle so ENFORCE has something to enforce.
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
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
            thinking_control_available=True,
            summary_mode=SummaryMode.OFF,
        ),
    )


def _governed_conversation_service(
    inference: FakeInference,
    *,
    mode: str,
    composition: RuntimeGovernanceComposition,
) -> ConversationGenerationService:
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: mode
    )
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.qwen3-4b-q4-k-m",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        summarization=SummarizationConfig(),
        governance_pre_hook=pre_hook,
        governance_post_hook=post_hook,
    )


def persistent_runtime_with_governance(
    tmp_path: Path,
    inference: FakeInference,
    *,
    mode: str,
) -> WebRuntime:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    conversation = _governed_conversation_service(inference, mode=mode, composition=composition)
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data", bound_scope_id=SCOPE
    )
    store.initialize_new_store()
    persistent = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=cast(object, conversation),  # type: ignore[arg-type]
    )
    persistent.recover_incomplete_conversations()
    return WebRuntime(
        conversation=cast(object, conversation),  # type: ignore[arg-type]
        snapshot=_snapshot(),
        close_callback=lambda: None,
        persistent_conversation=persistent,
        runtime_governance_composition=composition,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


def _settings_payload() -> dict[str, object]:
    return {
        "response_language": "ja",
        "max_new_tokens": 2048,
        "thinking_mode": "disabled",
        "thinking_visibility": "hidden",
        "summary_mode": "off",
        "documentation_rag_mode": "disabled",
    }


async def _create(client: httpx.AsyncClient) -> dict[str, object]:
    response = await client.post(
        "/api/v2/conversations",
        json={"operation_id": "create-1", "expected_revision": None},
    )
    assert response.status_code == 200
    return cast(dict[str, object], response.json()["detail"])


@pytest.mark.asyncio
async def test_persistent_off_mode_turn_is_unaffected(tmp_path: Path) -> None:
    inference = FakeInference()
    runtime = persistent_runtime_with_governance(tmp_path, inference, mode="off")
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await _create(client)
        streamed = await client.post(
            f"/api/v2/conversations/{detail['conversation_id']}/turns/stream",
            json={
                "content": "hello",
                "settings": _settings_payload(),
                "operation_id": "turn-1",
                "expected_revision": detail["storage_revision"],
            },
        )
    assert streamed.status_code == 200
    assert "event: completed" in streamed.text
    assert "a real answer" in streamed.text


@pytest.mark.asyncio
async def test_persistent_enforce_mode_rejects_empty_output_with_no_ghost_completion(
    tmp_path: Path,
) -> None:
    inference = FakeInference(empty_output=True)
    runtime = persistent_runtime_with_governance(tmp_path, inference, mode="enforce")
    app = create_web_app(
        runtime_factory=lambda: runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        detail = await _create(client)
        conversation_id = detail["conversation_id"]
        streamed = await client.post(
            f"/api/v2/conversations/{conversation_id}/turns/stream",
            json={
                "content": "hello",
                "settings": _settings_payload(),
                "operation_id": "turn-1",
                "expected_revision": detail["storage_revision"],
            },
        )
        persisted = await client.get(f"/api/v2/conversations/{conversation_id}")
    assert streamed.status_code == 200
    assert "event: completed" not in streamed.text
    assert "event: error" in streamed.text
    assert "governance_reject_output" in streamed.text
    # No Ghost Completion in the durable record either: the rejected turn
    # never carries a persisted assistant answer (P4-ACC-020).
    turns = persisted.json()["turns"]
    assert len(turns) == 1
    assert turns[0]["state"] != "completed"
    assert all(message["role"] != "assistant" for message in turns[0]["messages"])


@pytest.mark.asyncio
async def test_ephemeral_enforce_pre_hook_sees_the_rag_augmented_request_not_the_raw_one() -> None:
    inference = FakeInference()
    rag = RecordingContextualRag(injected_context="x" * 5_000)
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    # A budget too small for the raw request but that says nothing yet
    # about the RAG-augmented one — the assertion below is what actually
    # proves inclusion.
    composition.budget = composition.budget.model_copy(update={"max_snapshot_chars": 200})
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition, mode_provider=lambda: "enforce"
    )
    conversation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.qwen3-4b-q4-k-m",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        summarization=SummarizationConfig(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        governance_pre_hook=pre_hook,
        governance_post_hook=post_hook,
    )
    app = create_web_app(
        runtime_factory=lambda: WebRuntime(
            conversation=cast(object, conversation),  # type: ignore[arg-type]
            snapshot=_snapshot(),
            close_callback=lambda: None,
            runtime_governance_composition=composition,
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    payload = {
        "messages": [{"role": "user", "content": "hello"}],
        "settings": {**_settings_payload(), "documentation_rag_mode": "enabled"},
    }
    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "event: completed" not in response.text
    assert "event: error" in response.text
    assert "governance_stop_before_generation" in response.text
    # And the raw pre-RAG request truly was tiny — it is the augmentation
    # that pushed the snapshot over budget, not the bare user turn.
    assert len(rag.contexts) == 1
    assert len(inference.requests) == 0  # Zero Model Call on Stop (P4-MOD-002)
