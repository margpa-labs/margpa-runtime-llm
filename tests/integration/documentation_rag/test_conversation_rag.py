"""Conversation-level retrieval, citation, summary, and denial integration tests."""

from __future__ import annotations

import hashlib
import threading
import time
from collections.abc import Iterator
from types import TracebackType
from typing import Any, cast

import pytest

from margpa_runtime_llm.adapters.output_protocols.plain_text import PlainTextOutputParser
from margpa_runtime_llm.modules.conversation.public import (
    ConversationEvent,
    ConversationEventType,
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
    DocumentationRagMode,
    DocumentationRetrievalState,
    DocumentationWarning,
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
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode


class FakeStream:
    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def generation_id(self) -> str:
        return "fake"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        yield GenerationChunk(
            request_id="fake",
            sequence=0,
            text_delta=self._text,
            is_final=False,
        )
        yield GenerationChunk(
            request_id="fake",
            sequence=1,
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
        )

    def cancel(self) -> None:
        return None

    def close(self) -> None:
        return None

    def __enter__(self) -> FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class FakeInference:
    def __init__(self) -> None:
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return FakeStream("summary" if request.request_id.endswith(":summary") else "answer")


class FakeRag:
    def __init__(self, augmentation: DocumentationAugmentation) -> None:
        self.augmentation = augmentation
        self.queries: list[str] = []

    def augment(
        self,
        query_text: str,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        del cancelled
        self.queries.append(query_text)
        return self.augmentation


class WaitingRag(FakeRag):
    def __init__(self) -> None:
        super().__init__(unavailable_augmentation())
        self.started = threading.Event()

    def augment(
        self,
        query_text: str,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        self.queries.append(query_text)
        self.started.set()
        deadline = time.monotonic() + 2.0
        while cancelled is not None and not cancelled() and time.monotonic() < deadline:
            time.sleep(0.001)
        return self.augmentation


def evidence(
    *,
    grounding_state: DocumentationGroundingState,
    generation_allowed: bool,
    retrieved_chunk_count: int,
    assembled_block_count: int,
) -> DocumentationEvidence:
    selected_chunk_ids = (hashlib.sha512(b"chunk").hexdigest(),) if retrieved_chunk_count else ()
    selected_document_digests = (
        (hashlib.sha512(b"document").hexdigest(),) if retrieved_chunk_count else ()
    )
    selected_scores = (3.0,) if retrieved_chunk_count else ()
    return DocumentationEvidence(
        query_digest=hashlib.sha512(b"query").hexdigest(),
        corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
        retriever_key="field_weighted_bm25",
        retriever_version="1",
        selected_chunk_ids=selected_chunk_ids,
        selected_document_digests=selected_document_digests,
        selected_scores=selected_scores,
        base_prompt_used=64,
        base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
        base_prompt_exact=True,
        context_budget=768,
        context_budget_unit=DocumentationMeasurementUnit.TOKENS,
        context_used=100 if assembled_block_count else 0,
        context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
        context_measurement_limit=768,
        context_token_budget_used=True,
        retrieved_chunk_count=retrieved_chunk_count,
        assembled_block_count=assembled_block_count,
        identifier_subject_count=1 if retrieved_chunk_count else 0,
        retrieval_covered_subject_count=1 if retrieved_chunk_count else 0,
        retrieval_uncovered_subject_count=0,
        covered_subject_count=1 if assembled_block_count else 0,
        uncovered_subject_count=(1 if retrieved_chunk_count and not assembled_block_count else 0),
        grounding_state=grounding_state,
        generation_allowed=generation_allowed,
        retrieval_duration_ms=1.0,
    )


def successful_augmentation() -> DocumentationAugmentation:
    citation = DocumentationCitation(
        citation_id="citation-1",
        project_relative_path="docs/project/current/requirements_ja.md",
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
        evidence=evidence(
            grounding_state=DocumentationGroundingState.GROUNDED_READY,
            generation_allowed=True,
            retrieved_chunk_count=1,
            assembled_block_count=1,
        ),
        document_count=1,
        selected_chunk_count=1,
        duration_ms=1.0,
    )


def unavailable_augmentation() -> DocumentationAugmentation:
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.UNAVAILABLE,
        should_generate=False,
        evidence=evidence(
            grounding_state=DocumentationGroundingState.UNAVAILABLE,
            generation_allowed=False,
            retrieved_chunk_count=0,
            assembled_block_count=0,
        ),
        warnings=(
            DocumentationWarning(
                code="documentation_docs_missing",
                message="docsが設置されていないため参照出来ません。",
            ),
        ),
        document_count=0,
        selected_chunk_count=0,
        duration_ms=1.0,
    )


def context_insufficient_augmentation() -> DocumentationAugmentation:
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=False,
        evidence=evidence(
            grounding_state=DocumentationGroundingState.CONTEXT_INSUFFICIENT,
            generation_allowed=False,
            retrieved_chunk_count=1,
            assembled_block_count=0,
        ),
        warnings=(
            DocumentationWarning(
                code="documentation_context_budget_insufficient",
                message="根拠を取得しましたが、Context余力不足のため回答に使用できません。",
            ),
        ),
        document_count=1,
        selected_chunk_count=0,
        duration_ms=1.0,
    )


def subject_coverage_insufficient_augmentation() -> DocumentationAugmentation:
    chunk_ids = tuple(hashlib.sha512(f"chunk-{index}".encode()).hexdigest() for index in range(3))
    document_digests = tuple(
        hashlib.sha512(f"document-{index}".encode()).hexdigest() for index in range(3)
    )
    citation = DocumentationCitation(
        citation_id="citation-1",
        project_relative_path="docs/project/current/easa_ja.md",
        heading_breadcrumb="EASA",
        chunk_id=chunk_ids[0],
        document_sha512=document_digests[0],
        retrieval_score=3.0,
        selected_order=1,
    )
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=False,
        citations=(citation,),
        evidence=DocumentationEvidence(
            query_digest=hashlib.sha512(b"combined-query").hexdigest(),
            corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
            retriever_key="field_weighted_bm25",
            retriever_version="5",
            selected_chunk_ids=chunk_ids,
            selected_document_digests=document_digests,
            selected_scores=(3.0, 2.0, 1.0),
            base_prompt_used=64,
            base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
            base_prompt_exact=True,
            context_budget=768,
            context_budget_unit=DocumentationMeasurementUnit.TOKENS,
            context_used=100,
            context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
            context_measurement_limit=768,
            context_token_budget_used=True,
            retrieved_chunk_count=3,
            assembled_block_count=1,
            identifier_subject_count=3,
            retrieval_covered_subject_count=3,
            retrieval_uncovered_subject_count=0,
            covered_subject_count=1,
            uncovered_subject_count=2,
            grounding_state=DocumentationGroundingState.SUBJECT_COVERAGE_INSUFFICIENT,
            generation_allowed=False,
            truncation_state=True,
            retrieval_duration_ms=1.0,
        ),
        warnings=(
            DocumentationWarning(
                code="documentation_subject_coverage_insufficient",
                message=(
                    "質問対象の一部に必要なProject Docsの根拠が揃わないため、回答を停止しました。"
                ),
            ),
        ),
        document_count=3,
        selected_chunk_count=1,
        duration_ms=1.0,
    )


def policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def value(
    *,
    summary: SummaryMode = SummaryMode.OFF,
    documentation_rag: DocumentationRagMode = DocumentationRagMode.ENABLED,
) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(
            ConversationMessage(role=ConversationRole.USER, content="old"),
            ConversationMessage(role=ConversationRole.ASSISTANT, content="prior"),
            ConversationMessage(role=ConversationRole.USER, content="latest query"),
        ),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            summary_mode=summary,
            documentation_rag_mode=documentation_rag,
        ),
    )


def service(
    inference: FakeInference,
    rag: FakeRag | None,
    availability: DocumentationRagAvailability,
) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=policy(),
        documentation_rag=rag,
        documentation_rag_availability=availability,
    )


def test_reference_is_system_owned_latest_query_only_and_citation_is_separate() -> None:
    inference = FakeInference()
    rag = FakeRag(successful_augmentation())
    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE).start(value()).events()
    )

    assert rag.queries == ["latest query"]
    assert [event.event for event in events].count(ConversationEventType.RETRIEVAL) == 1
    retrieval = next(event for event in events if event.event is ConversationEventType.RETRIEVAL)
    retrieval_data = cast(dict[str, Any], retrieval.data)
    assert retrieval_data["citations"][0]["project_relative_path"].startswith("docs/")
    assert inference.requests[0].messages[0].role.value == "system"
    assert inference.requests[0].messages[1].name == "documentation_reference"
    assert inference.requests[0].messages[-1].content == "latest query"


def test_summary_retrieves_once_and_keeps_original_citation() -> None:
    inference = FakeInference()
    rag = FakeRag(successful_augmentation())
    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE)
        .start(value(summary=SummaryMode.POST_GENERATION))
        .events()
    )

    assert rag.queries == ["latest query"]
    assert len(inference.requests) == 2
    completed = events[-1]
    assert completed.event is ConversationEventType.COMPLETED
    completed_data = cast(dict[str, Any], completed.data)
    assert completed_data["documentation_retrieval"]["citations"]


def test_docs_missing_emits_safe_error_without_model_call() -> None:
    inference = FakeInference()
    rag = FakeRag(unavailable_augmentation())
    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE).start(value()).events()
    )

    assert inference.requests == []
    assert [event.event for event in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.RETRIEVAL,
        ConversationEventType.ERROR,
    ]
    assert events[-1].data["message"] == "docsが設置されていないため参照出来ません。"


def test_context_insufficient_emits_distinct_error_without_model_call() -> None:
    inference = FakeInference()
    rag = FakeRag(context_insufficient_augmentation())

    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE).start(value()).events()
    )

    assert inference.requests == []
    assert [event.event for event in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.RETRIEVAL,
        ConversationEventType.ERROR,
    ]
    assert events[-1].data["code"] == "documentation_context_budget_insufficient"
    assert "Context余力不足" in str(events[-1].data["message"])


def test_partial_subject_coverage_emits_safe_error_without_model_call() -> None:
    inference = FakeInference()
    rag = FakeRag(subject_coverage_insufficient_augmentation())

    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE).start(value()).events()
    )

    assert inference.requests == []
    assert [event.event for event in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.RETRIEVAL,
        ConversationEventType.ERROR,
    ]
    assert events[-1].data["code"] == "documentation_subject_coverage_insufficient"
    retrieval_data = cast(dict[str, Any], events[2].data)
    assert len(retrieval_data["citations"]) == 1


def test_off_mode_never_calls_documentation_rag() -> None:
    inference = FakeInference()
    rag = FakeRag(successful_augmentation())

    events = list(
        service(inference, rag, DocumentationRagAvailability.AVAILABLE)
        .start(value(documentation_rag=DocumentationRagMode.DISABLED))
        .events()
    )

    assert rag.queries == []
    assert len(inference.requests) == 1
    assert all(event.event is not ConversationEventType.RETRIEVAL for event in events)


def test_cancel_during_retrieval_releases_busy_gate_without_model_call() -> None:
    inference = FakeInference()
    rag = WaitingRag()
    conversation = service(inference, rag, DocumentationRagAvailability.AVAILABLE)
    session = conversation.start(value())
    iterator = session.events()
    assert next(iterator).data["state"] == "preparing"
    assert next(iterator).data["state"] == "retrieving_documentation"
    remaining_events: list[ConversationEvent] = []
    worker = threading.Thread(target=lambda: remaining_events.extend(iterator))
    worker.start()
    assert rag.started.wait(1.0)

    with pytest.raises(InferenceError) as busy:
        conversation.start(value())
    assert busy.value.code.value == "model_busy"
    assert conversation.cancel(session.request_id) is True
    worker.join(2.0)

    assert worker.is_alive() is False
    assert remaining_events[-1].event is ConversationEventType.CANCELLED
    assert inference.requests == []
    follow_up = list(
        service(
            inference,
            FakeRag(successful_augmentation()),
            DocumentationRagAvailability.AVAILABLE,
        )
        .start(value())
        .events()
    )
    assert follow_up[-1].event is ConversationEventType.COMPLETED


def test_denied_or_unavailable_request_fails_before_rag_and_model() -> None:
    for availability in (
        DocumentationRagAvailability.DENIED,
        DocumentationRagAvailability.UNAVAILABLE,
    ):
        inference = FakeInference()
        rag = FakeRag(successful_augmentation())
        with pytest.raises(InferenceError):
            service(inference, rag, availability).start(value())
        assert rag.queries == []
        assert inference.requests == []
