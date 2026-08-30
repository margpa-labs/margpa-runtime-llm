"""Framework-independent Phase 1-G conversation contract tests."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import ClassVar

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.adapters.documentation_rag.bounded_context_assembler import (
    REFERENCE_INSTRUCTION,
)
from margpa_runtime_llm.adapters.output_protocols.plain_text import PlainTextOutputParser
from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    NO_HIT_FRESHNESS_INSTRUCTION,
)
from margpa_runtime_llm.modules.conversation.public import (
    TOKEN_LIMIT_WARNING,
    ContextUsagePromptInjectionMode,
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
    ExpressiveMode,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationAugmentation,
    DocumentationCitation,
    DocumentationEvidence,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagRequestContext,
    DocumentationReferenceBlock,
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
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError, InferenceErrorCode
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
from margpa_runtime_llm.orchestration.response_language import JAPANESE_RESPONSE_INSTRUCTION


def _as_dict(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return value


class FakeStream:
    def __init__(
        self,
        *,
        text_deltas: tuple[str, ...] = ("answer",),
        finish_reason: FinishReason = FinishReason.STOP,
        failure: InferenceError | None = None,
        usage: TokenUsage | None = None,
    ) -> None:
        self.text_deltas = text_deltas
        self.finish_reason = finish_reason
        self.failure = failure
        self.usage = usage
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "fake-generation"

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
        if self.failure is not None:
            raise self.failure
        for sequence, text in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="fake-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="fake-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=self.finish_reason,
            usage=self.usage,
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


class NoTerminalStream(FakeStream):
    def __iter__(self) -> Iterator[GenerationChunk]:
        yield GenerationChunk(
            request_id="fake-request",
            sequence=0,
            text_delta="incomplete summary",
            is_final=False,
        )


class FakeInference:
    def __init__(self, factory: Callable[[], GenerationStream] | None = None) -> None:
        self.factory = factory or FakeStream
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return self.factory()


class RecordingContextualRag:
    def __init__(self) -> None:
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
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            evidence=DocumentationEvidence(
                query_digest=hashlib.sha512(query_text.encode()).hexdigest(),
                corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
                retriever_key="test",
                retriever_version="1",
                base_prompt_used=request_context.system_history_current_prompt_tokens,
                base_prompt_unit=request_context.prompt_measurement_unit,
                base_prompt_exact=request_context.prompt_token_count_exact,
                context_budget=0,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=0,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=0,
                context_token_budget_used=True,
                retrieved_chunk_count=0,
                assembled_block_count=0,
                identifier_subject_count=0,
                retrieval_covered_subject_count=0,
                retrieval_uncovered_subject_count=0,
                covered_subject_count=0,
                uncovered_subject_count=0,
                grounding_state=DocumentationGroundingState.NO_HIT,
                generation_allowed=True,
                retrieval_duration_ms=0,
            ),
            document_count=1,
            selected_chunk_count=0,
            duration_ms=0,
        )


class IdentifierNoHitRag:
    """P7-RW3-B (P7-CODEX-013 §7.3): NO_HIT with a named high-signal
    Subject (`identifier_subject_count=1`) and zero retrieved evidence -
    the exact condition `_identifier_no_hit_denied()` gates on."""

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        del cancelled
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            evidence=DocumentationEvidence(
                query_digest=hashlib.sha512(query_text.encode()).hexdigest(),
                corpus_manifest_digest=hashlib.sha512(b"manifest").hexdigest(),
                retriever_key="test",
                retriever_version="1",
                base_prompt_used=request_context.system_history_current_prompt_tokens,
                base_prompt_unit=request_context.prompt_measurement_unit,
                base_prompt_exact=request_context.prompt_token_count_exact,
                context_budget=0,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=0,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=0,
                context_token_budget_used=True,
                retrieved_chunk_count=0,
                assembled_block_count=0,
                identifier_subject_count=1,
                retrieval_covered_subject_count=0,
                retrieval_uncovered_subject_count=1,
                covered_subject_count=0,
                uncovered_subject_count=1,
                grounding_state=DocumentationGroundingState.NO_HIT,
                generation_allowed=True,
                retrieval_duration_ms=0,
            ),
            document_count=1,
            selected_chunk_count=0,
            duration_ms=0,
        )


class BudgetAwareGroundedRag:
    _definitions: ClassVar[dict[str, str]] = {
        "EASA": (
            "内部安全傾向、周辺安全制御、入力文脈、生成過程から現れる複合的安全挙動を扱います。"
        ),
        "ARGD": "Premise、Context、矛盾、情報不足およびRepairを扱う宣言的Governanceです。",
        "DLAGSA": (
            "複数の判断・実行・検証主体間の責任、委譲、例外、証跡および安全側制御を扱います。"
        ),
    }

    def __init__(self, *, safety_margin_tokens: int = 512) -> None:
        self.safety_margin_tokens = safety_margin_tokens
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
        assert request_context.system_history_current_prompt_tokens is not None
        budget = min(
            768,
            max(
                0,
                request_context.effective_context_size
                - request_context.system_history_current_prompt_tokens
                - request_context.requested_max_new_tokens
                - self.safety_margin_tokens,
            ),
        )
        subject = next(
            candidate for candidate in self._definitions if candidate in query_text.upper()
        )
        chunk_id = hashlib.sha512(f"chunk:{subject}".encode()).hexdigest()
        document_digest = hashlib.sha512(f"document:{subject}".encode()).hexdigest()
        common_evidence = {
            "query_digest": hashlib.sha512(query_text.encode()).hexdigest(),
            "corpus_manifest_digest": hashlib.sha512(b"manifest").hexdigest(),
            "retriever_key": "test_budget_aware",
            "retriever_version": "1",
            "selected_chunk_ids": (chunk_id,),
            "selected_document_digests": (document_digest,),
            "selected_scores": (3.0,),
            "base_prompt_used": request_context.system_history_current_prompt_tokens,
            "base_prompt_unit": DocumentationMeasurementUnit.TOKENS,
            "base_prompt_exact": request_context.prompt_token_count_exact,
            "context_budget": budget,
            "context_budget_unit": DocumentationMeasurementUnit.TOKENS,
            "context_measurement_unit": DocumentationMeasurementUnit.TOKENS,
            "context_measurement_limit": budget,
            "context_token_budget_used": True,
            "retrieved_chunk_count": 1,
            "identifier_subject_count": 1,
            "retrieval_covered_subject_count": 1,
            "retrieval_uncovered_subject_count": 0,
            "retrieval_duration_ms": 0.0,
        }
        if budget < 128:
            return DocumentationAugmentation(
                state=DocumentationRetrievalState.ENABLED,
                should_generate=False,
                evidence=DocumentationEvidence.model_validate(
                    {
                        **common_evidence,
                        "context_used": 0,
                        "assembled_block_count": 0,
                        "covered_subject_count": 0,
                        "uncovered_subject_count": 1,
                        "grounding_state": DocumentationGroundingState.CONTEXT_INSUFFICIENT,
                        "generation_allowed": False,
                    }
                ),
                warnings=(
                    DocumentationWarning(
                        code="documentation_context_budget_insufficient",
                        message="根拠を取得しましたが、Context余力不足のため回答に使用できません。",
                    ),
                ),
                document_count=1,
                selected_chunk_count=0,
                duration_ms=0.0,
            )

        reference_message = (
            f"{REFERENCE_INSTRUCTION}\n\n[REFERENCE ref-1]\n"
            f"Path: docs/public/{subject.casefold()}_ja.md\n"
            f"Heading: {subject}\nContent:\n{self._definitions[subject]}\n"
            "[/REFERENCE ref-1]"
        )
        citation = DocumentationCitation(
            citation_id="citation-1",
            project_relative_path=f"docs/public/{subject.casefold()}_ja.md",
            heading_breadcrumb=subject,
            chunk_id=chunk_id,
            document_sha512=document_digest,
            retrieval_score=3.0,
            selected_order=1,
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            reference_message=reference_message,
            citations=(citation,),
            evidence=DocumentationEvidence.model_validate(
                {
                    **common_evidence,
                    "context_used": min(100, budget),
                    "assembled_block_count": 1,
                    "covered_subject_count": 1,
                    "uncovered_subject_count": 0,
                    "grounding_state": DocumentationGroundingState.GROUNDED_READY,
                    "generation_allowed": True,
                }
            ),
            document_count=1,
            selected_chunk_count=1,
            duration_ms=0.0,
        )


class GroundedCodeRag:
    """P7-RW3-C (P7-CODEX-012): a minimal always-`GROUNDED_READY` fixture
    whose Current Evidence names one concrete Code-shaped Identifier
    (`CEDAR-25123`) - used by the Grounding Consistency Check tests
    below to exercise a real Candidate against real Evidence content."""

    EVIDENCE_CONTENT = "Nazuna Probe Orionの検証コードは CEDAR-25123 である。"

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        del cancelled
        chunk_id = hashlib.sha512(b"grounded-code-probe-chunk").hexdigest()
        document_digest = hashlib.sha512(b"grounded-code-probe-document").hexdigest()
        reference_message = (
            f"{REFERENCE_INSTRUCTION}\n\n[REFERENCE ref-1]\n"
            "Path: local-corpus/margpa-manual-probe-8.md\n"
            f"Heading: MARGPA Manual Probe 8\nContent:\n{self.EVIDENCE_CONTENT}\n"
            "[/REFERENCE ref-1]"
        )
        block = DocumentationReferenceBlock(
            reference_id="ref-1",
            project_relative_path="local-corpus/margpa-manual-probe-8.md",
            heading_breadcrumb="MARGPA Manual Probe 8",
            chunk_id=chunk_id,
            content=self.EVIDENCE_CONTENT,
            measured_size=len(self.EVIDENCE_CONTENT),
            measurement_unit=DocumentationMeasurementUnit.TOKENS,
        )
        citation = DocumentationCitation(
            citation_id="citation-1",
            project_relative_path="local-corpus/margpa-manual-probe-8.md",
            heading_breadcrumb="MARGPA Manual Probe 8",
            chunk_id=chunk_id,
            document_sha512=document_digest,
            retrieval_score=3.0,
            selected_order=1,
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            reference_message=reference_message,
            citations=(citation,),
            reference_blocks=(block,),
            evidence=DocumentationEvidence.model_validate(
                {
                    "query_digest": hashlib.sha512(query_text.encode()).hexdigest(),
                    "corpus_manifest_digest": hashlib.sha512(b"manifest").hexdigest(),
                    "retriever_key": "test_grounded_code",
                    "retriever_version": "1",
                    "selected_chunk_ids": (chunk_id,),
                    "selected_document_digests": (document_digest,),
                    "selected_scores": (3.0,),
                    "base_prompt_used": request_context.system_history_current_prompt_tokens,
                    "base_prompt_unit": DocumentationMeasurementUnit.TOKENS,
                    "base_prompt_exact": request_context.prompt_token_count_exact,
                    "context_budget": 768,
                    "context_budget_unit": DocumentationMeasurementUnit.TOKENS,
                    "context_used": len(self.EVIDENCE_CONTENT),
                    "context_measurement_unit": DocumentationMeasurementUnit.TOKENS,
                    "context_measurement_limit": 768,
                    "context_token_budget_used": True,
                    "retrieved_chunk_count": 1,
                    "assembled_block_count": 1,
                    "identifier_subject_count": 1,
                    "retrieval_covered_subject_count": 1,
                    "retrieval_uncovered_subject_count": 0,
                    "covered_subject_count": 1,
                    "uncovered_subject_count": 0,
                    "grounding_state": DocumentationGroundingState.GROUNDED_READY,
                    "generation_allowed": True,
                    "retrieval_duration_ms": 0.0,
                }
            ),
            document_count=1,
            selected_chunk_count=1,
            duration_ms=0.0,
        )


def presentation_policy(
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN,
) -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=visibility,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def conversation_input(
    *,
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN,
    thinking_mode: ThinkingMode = ThinkingMode.ENABLED,
    max_new_tokens: int = 128,
    summary_mode: SummaryMode = SummaryMode.OFF,
    documentation_rag_mode: DocumentationRagMode = DocumentationRagMode.DISABLED,
    context_usage_prompt_injection_mode: ContextUsagePromptInjectionMode = (
        ContextUsagePromptInjectionMode.DISABLED
    ),
    expressive_mode: ExpressiveMode = ExpressiveMode.DISABLED,
) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(
            ConversationMessage(role=ConversationRole.USER, content="first"),
            ConversationMessage(role=ConversationRole.ASSISTANT, content="prior answer"),
            ConversationMessage(role=ConversationRole.USER, content="next"),
        ),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=max_new_tokens,
            thinking_mode=thinking_mode,
            thinking_visibility=visibility,
            summary_mode=summary_mode,
            documentation_rag_mode=documentation_rag_mode,
            context_usage_prompt_injection_mode=context_usage_prompt_injection_mode,
            expressive_mode=expressive_mode,
        ),
    )


def service(inference: FakeInference) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048,
            thinking_mode=ThinkingMode.ENABLED,
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
    )


def event_types(events: list[ConversationEvent]) -> list[ConversationEventType]:
    return [event.event for event in events]


def test_history_contract_rejects_invalid_roles_order_and_values() -> None:
    with pytest.raises(ValidationError):
        ConversationMessage.model_validate({"role": "system", "content": "unsafe"})
    with pytest.raises(ValidationError):
        ConversationMessage(role=ConversationRole.USER, content=" ")
    with pytest.raises(ValidationError):
        ConversationGenerationInput(
            messages=(ConversationMessage(role=ConversationRole.ASSISTANT, content="bad"),),
            settings=conversation_input().settings,
        )
    with pytest.raises(ValidationError):
        ConversationGenerationInput(
            messages=(
                ConversationMessage(role=ConversationRole.USER, content="one"),
                ConversationMessage(role=ConversationRole.USER, content="two"),
            ),
            settings=conversation_input().settings,
        )


@pytest.mark.parametrize("value", [True, 1.5, "128", 0])
def test_max_new_tokens_is_a_positive_strict_integer(value: object) -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": value,
                "thinking_visibility": "hidden",
            }
        )


def test_max_new_tokens_schema_defers_the_upper_bound_to_the_runtime_snapshot() -> None:
    settings = ConversationSettings.model_validate(
        {
            "response_language": "ja",
            "max_new_tokens": 2049,
            "thinking_visibility": "hidden",
        }
    )

    assert settings.max_new_tokens == 2049


def test_summary_mode_rejects_unknown_client_value() -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": 128,
                "thinking_visibility": "hidden",
                "summary_mode": "on",
            }
        )


@pytest.mark.parametrize("value", ["model_default", "unknown"])
def test_web_thinking_mode_rejects_unsupported_values(value: str) -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": 128,
                "thinking_mode": value,
                "thinking_visibility": "hidden",
            }
        )


def test_request_composition_preserves_history_and_only_overrides_allowed_values() -> None:
    inference = FakeInference()
    generation = service(inference)

    events = list(generation.start(conversation_input(max_new_tokens=128)).events())

    request = inference.requests[0]
    assert [message.role for message in request.messages] == [
        MessageRole.SYSTEM,
        MessageRole.USER,
        MessageRole.ASSISTANT,
        MessageRole.USER,
    ]
    assert request.messages[0].content == JAPANESE_RESPONSE_INSTRUCTION
    assert [message.content for message in request.messages[1:]] == [
        "first",
        "prior answer",
        "next",
    ]
    assert request.parameters.max_new_tokens == 128
    assert request.parameters.thinking_mode is ThinkingMode.ENABLED
    assert event_types(events) == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.DELTA,
        ConversationEventType.COMPLETED,
    ]


def test_documentation_request_context_uses_effective_context_history_and_request_limit() -> None:
    inference = FakeInference()
    rag = RecordingContextualRag()
    counter_calls: list[tuple[tuple[ChatMessage, ...], ThinkingMode]] = []

    def exact_prompt_counter(
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        counter_calls.append((messages, thinking_mode))
        return sum(len(message.content) for message in messages)

    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=exact_prompt_counter,
        effective_context_size=8192,
    )
    short = conversation_input(
        max_new_tokens=128,
        documentation_rag_mode=DocumentationRagMode.ENABLED,
    )
    long = short.model_copy(
        update={
            "messages": (
                ConversationMessage(role=ConversationRole.USER, content="first" * 200),
                ConversationMessage(role=ConversationRole.ASSISTANT, content="answer" * 200),
                ConversationMessage(role=ConversationRole.USER, content="next"),
            ),
            "settings": short.settings.model_copy(update={"max_new_tokens": 512}),
        }
    )

    list(generation.start(short).events())
    list(generation.start(long).events())

    short_context, long_context = rag.contexts
    assert short_context.effective_context_size == 8192
    assert short_context.requested_max_new_tokens == 128
    assert long_context.requested_max_new_tokens == 512
    assert short_context.system_history_current_prompt_tokens is not None
    assert long_context.system_history_current_prompt_tokens is not None
    assert (
        long_context.system_history_current_prompt_tokens
        > short_context.system_history_current_prompt_tokens
    )
    assert short_context.prompt_token_count_exact is True
    assert long_context.prompt_token_count_exact is True
    assert short_context.prompt_measurement_unit is DocumentationMeasurementUnit.TOKENS
    # Each Turn is counted once before Documentation RAG budgeting and once
    # after augmentation for the exact remaining-context enforcement boundary.
    assert len(counter_calls) == 4
    assert counter_calls[0][1] is ThinkingMode.ENABLED
    assert short_context.system_history_current_prompt_tokens == sum(
        len(message.content) for message in counter_calls[0][0]
    )
    assert short_context.system_history_current_prompt_tokens != sum(
        len(message.content.encode("utf-8")) for message in counter_calls[0][0]
    )
    assert long_context.system_history_current_prompt_tokens == sum(
        len(message.content) for message in counter_calls[2][0]
    )


def test_no_hit_splices_a_freshness_notice_and_still_generates() -> None:
    """P7-RW2-B (P7-CODEX-008): NO_HIT never carries a `reference_message`,
    but the model must still receive an explicit "no current evidence"
    notice rather than only the raw conversation History (which may hold a
    now-stale earlier answer) - and it must still be allowed to answer
    ordinary out-of-corpus questions (`should_generate=True` is preserved).
    """

    inference = FakeInference()
    rag = RecordingContextualRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    assert event_types(events)[-1] == ConversationEventType.COMPLETED
    request = inference.requests[0]
    # P7-RW3-C (P7-CODEX-012): the Notice now sits immediately before the
    # Current User Message, *after* every Historical Turn - not right
    # after System/before all History (the previous, Handoff-flagged order
    # a Model was observed to weigh less than a nearer stale Historical
    # Assistant Turn).
    notice = request.messages[-2]
    assert notice.role is MessageRole.TOOL
    assert notice.name == "documentation_no_hit_notice"
    assert notice.content == NO_HIT_FRESHNESS_INSTRUCTION
    assert "現在の根拠" in notice.content
    assert request.messages[-1].role is MessageRole.USER
    assert request.messages[-1].content == "next"
    # The real conversation History still precedes it, untouched, right
    # after System.
    assert [message.content for message in request.messages[1:-2]] == [
        "first",
        "prior answer",
    ]


def test_identifier_no_hit_denies_generation_with_a_fixed_presentation() -> None:
    """P7-RW3-B (P7-CODEX-013 §7.3): unlike ordinary NO_HIT (the previous
    test above), a query naming a high-signal Identifier/Subject with
    zero Current Corpus Evidence must converge to a fixed Presentation
    *before* any Inference Call - the Main Model is never given the
    chance to fabricate a plausible-looking value from its own General
    Knowledge or Conversation History."""

    inference = FakeInference()
    rag = IdentifierNoHitRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    # No Model Call happened at all.
    assert inference.requests == []
    assert event_types(events)[-1] == ConversationEventType.COMPLETED
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assistant = _as_dict(completed.data["assistant_message"])
    assert "根拠が見つかりませんでした" in str(assistant["content"])
    retrieval_data = _as_dict(completed.data["documentation_retrieval"])
    assert retrieval_data["citations"] == []


def test_long_japanese_multi_turn_keeps_citations_with_exact_room_and_fails_when_exhausted() -> (
    None
):
    inference = FakeInference()
    rag = BudgetAwareGroundedRag()
    counter_calls: list[tuple[ChatMessage, ...]] = []

    def exact_counter(
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        del thinking_mode
        counter_calls.append(messages)
        return 32 + sum(max(1, len(message.content) // 8) for message in messages)

    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=2048),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=exact_counter,
        effective_context_size=4096,
    )
    settings = ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=2048,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        documentation_rag_mode=DocumentationRagMode.ENABLED,
    )
    long_answer_1 = "長い日本語の回答です。" * 180
    long_answer_2 = "別の長い日本語の回答です。" * 160
    turns = (
        ConversationGenerationInput(
            messages=(ConversationMessage(role=ConversationRole.USER, content="EASAとは?"),),
            settings=settings,
        ),
        ConversationGenerationInput(
            messages=(
                ConversationMessage(role=ConversationRole.USER, content="EASAとは?"),
                ConversationMessage(
                    role=ConversationRole.ASSISTANT,
                    content=long_answer_1,
                ),
                ConversationMessage(role=ConversationRole.USER, content="ARGDとは?"),
            ),
            settings=settings,
        ),
        ConversationGenerationInput(
            messages=(
                ConversationMessage(role=ConversationRole.USER, content="EASAとは?"),
                ConversationMessage(
                    role=ConversationRole.ASSISTANT,
                    content=long_answer_1,
                ),
                ConversationMessage(role=ConversationRole.USER, content="ARGDとは?"),
                ConversationMessage(
                    role=ConversationRole.ASSISTANT,
                    content=long_answer_2,
                ),
                ConversationMessage(role=ConversationRole.USER, content="DLAGSAとは?"),
            ),
            settings=settings,
        ),
    )

    event_batches = [list(generation.start(turn).events()) for turn in turns]

    assert len(inference.requests) == 3
    assert len(rag.contexts) == 3
    assert all(context.prompt_token_count_exact for context in rag.contexts)
    for events in event_batches:
        retrieval = next(
            event for event in events if event.event is ConversationEventType.RETRIEVAL
        )
        assert retrieval.data["citations"]
        assert events[-1].event is ConversationEventType.COMPLETED
    assert rag.contexts[1].system_history_current_prompt_tokens is not None
    assert rag.contexts[1].system_history_current_prompt_tokens < sum(
        len(message.content.encode("utf-8")) for message in counter_calls[1]
    )

    def exhausted_counter(
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        del messages, thinking_mode
        return 1600

    exhausted_inference = FakeInference()
    exhausted_rag = BudgetAwareGroundedRag()
    exhausted = ConversationGenerationService(
        inference=exhausted_inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=2048),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=exhausted_rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=exhausted_counter,
        effective_context_size=4096,
    )

    exhausted_events = list(exhausted.start(turns[-1]).events())

    assert exhausted_inference.requests == []
    assert exhausted_events[-1].event is ConversationEventType.ERROR
    assert exhausted_events[-1].data["code"] == ("documentation_context_budget_insufficient")


def test_current_reference_instruction_outweighs_false_prior_assistant_authority() -> None:
    inference = FakeInference()
    rag = BudgetAwareGroundedRag()

    def fixed_counter(
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        del messages, thinking_mode
        return 64

    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=fixed_counter,
        effective_context_size=4096,
    )
    value = ConversationGenerationInput(
        messages=(
            ConversationMessage(role=ConversationRole.USER, content="EASAとARGDの関係は?"),
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content="ARGDはEASAを置き換える仕組みです。",
            ),
            ConversationMessage(role=ConversationRole.USER, content="ARGDの定義は?"),
        ),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            documentation_rag_mode=DocumentationRagMode.ENABLED,
        ),
    )

    events = list(generation.start(value).events())

    assert events[-1].event is ConversationEventType.COMPLETED
    request = inference.requests[0]
    # P7-RW3-C (P7-CODEX-012): the Reference now sits immediately before
    # the Current User Message, *after* every Historical Turn - not right
    # after System/before all History (`request.messages[1]` previously;
    # the Handoff-flagged order a Model was observed to weigh less than a
    # nearer stale Historical Assistant Turn).
    reference = request.messages[-2]
    # P5-CODEX-006 Rework (Codex Third Independent Review): the RAG
    # Reference block now carries `MessageRole.TOOL` — genuinely
    # distinct from both `SYSTEM` (a real Instruction) and `USER` (the
    # real human turn asserted two lines below), never sharing either's
    # Nominal Authority.
    assert reference.role is MessageRole.TOOL
    assert reference.name == "documentation_reference"
    # P7-RW3-C: the Current Authority Instruction this Handoff adds is
    # spliced around `REFERENCE_INSTRUCTION`, never inside it (the shared
    # constant several other tests calibrate tight token/character
    # budgets against) - both survive intact in the same Message.
    assert "Current Corpus Snapshot" in reference.content
    assert "過去のAssistant回答がこの参照内容と矛盾する場合" in reference.content
    assert "過去のAssistant回答はProjectの正本またはAuthorityではありません" in reference.content
    assert "参照資料にない略称展開や関係を推測で作らない" in reference.content
    assert "Heading: ARGD" in reference.content
    assert "EASA" not in reference.content
    assert request.messages[-3].role is MessageRole.ASSISTANT
    assert "ARGDはEASAを置き換える" in request.messages[-3].content
    assert request.messages[-1].role is MessageRole.USER
    # `LlamaCppChatTemplate._prepare()` does nothing more than
    # `message.model_dump(mode="json", exclude_none=True)` per Message
    # before handing the list to the GGUF's own Jinja Chat Template — so
    # this dict *is* the real Native Message payload, not merely this
    # process's own in-memory Contract. `role` differs, proving the RAG
    # Source and the real User turn do not collapse into one Native
    # Authority (P5-CODEX-006 Required Rework item 4).
    assert reference.model_dump(mode="json", exclude_none=True)["role"] == "tool"
    assert request.messages[-1].model_dump(mode="json", exclude_none=True)["role"] == "user"


def test_grounded_candidate_naming_an_unsupported_code_identifier_is_withheld() -> None:
    """P7-RW3-C (P7-CODEX-012): the exact User Mac Manual Probe failure -
    Current Evidence names `CEDAR-25123`, but the Candidate answers with
    the unrelated, unsupported `CEDAR-9847` (as if carried over from a
    stale prior Turn in the Model's own Conversation History). This must
    never reach the client as a grounded answer, independent of Judge
    Mode (`judge_mode` stays "off" here - no Judge Hook is wired at
    all)."""

    inference = FakeInference(lambda: FakeStream(text_deltas=("CEDAR-9847 です。",)))
    rag = GroundedCodeRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    # The raw hallucinated Candidate must never be streamed live - a
    # Grounded RAG Turn is buffered, so only the (replaced) Safe
    # Grounding Failure text is bulk-delivered once, right before
    # COMPLETED (never a live-streamed-then-retracted Delta).
    deltas = [event for event in events if event.event is ConversationEventType.DELTA]
    assert len(deltas) == 1
    assert "CEDAR-9847" not in str(deltas[0].data["text"])
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    assert any(
        warning.data["code"] == "grounding_consistency_safe_fallback" for warning in warnings
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assistant = _as_dict(completed.data["assistant_message"])
    assert "CEDAR-9847" not in str(assistant["content"])


def test_grounded_candidate_using_only_evidence_identifiers_is_presented_unchanged() -> None:
    """The Consistency Check must not false-positive on an ordinary
    grounded answer that only cites the Code the Current Evidence
    actually contains."""

    inference = FakeInference(lambda: FakeStream(text_deltas=("検証コードは CEDAR-25123 です。",)))
    rag = GroundedCodeRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    assert not any(
        warning.data["code"] == "grounding_consistency_safe_fallback" for warning in warnings
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assistant = _as_dict(completed.data["assistant_message"])
    assert "CEDAR-25123" in str(assistant["content"])


def test_no_hit_candidate_naming_a_code_shaped_identifier_is_withheld() -> None:
    """P7-RW4 (Codex Controller Independent Review, P7-CODEX-013's
    remaining path): a plain NO_HIT Turn (`identifier_subject_count=0` -
    the Query itself named no high-signal Subject, so
    `_identifier_no_hit_denied()` never fires and a real Inference Call
    happens) whose Candidate nonetheless names a Code-shaped Identifier
    must be withheld exactly like a Grounded Turn's Consistency Check -
    the same `CEDAR-9847` failure, but for the residual path a
    compound Subject like `Nazuna Probe Orion` takes after its
    Document is deleted (its individual words are not
    `identifier_subject_count` high-signal, so the pre-Inference gate
    does not cover it)."""

    inference = FakeInference(lambda: FakeStream(text_deltas=("CEDAR-9847 です。",)))
    rag = RecordingContextualRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    # A real Inference Call did happen (unlike the pre-Inference Identifier
    # NO_HIT Denial path) - but its Candidate was never streamed live and
    # never presented.
    assert inference.requests != []
    deltas = [event for event in events if event.event is ConversationEventType.DELTA]
    assert len(deltas) == 1
    assert "CEDAR-9847" not in str(deltas[0].data["text"])
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    assert any(
        warning.data["code"] == "grounding_consistency_safe_fallback" for warning in warnings
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assistant = _as_dict(completed.data["assistant_message"])
    assert "CEDAR-9847" not in str(assistant["content"])
    retrieval_data = _as_dict(completed.data["documentation_retrieval"])
    assert retrieval_data["citations"] == []


def test_no_hit_candidate_without_a_code_shaped_identifier_is_presented_unchanged() -> None:
    """The NO_HIT Consistency Check must not false-positive on an
    ordinary out-of-corpus answer that never names any Code-shaped
    Identifier at all - the common chit-chat NO_HIT case."""

    inference = FakeInference(lambda: FakeStream(text_deltas=("特に決まった値はありません。",)))
    rag = RecordingContextualRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
    )

    events = list(
        generation.start(
            conversation_input(documentation_rag_mode=DocumentationRagMode.ENABLED)
        ).events()
    )

    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    assert not any(
        warning.data["code"] == "grounding_consistency_safe_fallback" for warning in warnings
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assistant = _as_dict(completed.data["assistant_message"])
    assert "特に決まった値はありません。" in str(assistant["content"])


def test_hidden_thinking_never_enters_display_payload_or_canonical_history() -> None:
    inference = FakeInference(
        lambda: FakeStream(text_deltas=("<think>secret", "</think>safe answer"))
    )

    events = list(service(inference).start(conversation_input()).events())
    deltas = "".join(
        str(event.data["text"]) for event in events if event.event is ConversationEventType.DELTA
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)

    assert deltas == "safe answer"
    assert all(
        event.data["channel"] == "final"
        for event in events
        if event.event is ConversationEventType.DELTA
    )
    assert "secret" not in deltas
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "safe answer",
    }


def test_visible_thinking_is_display_only_and_canonical_final_stays_separate() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("<think>reason", "</think>answer")))

    events = list(
        service(inference).start(conversation_input(visibility=ThinkingVisibility.VISIBLE)).events()
    )
    deltas = [event for event in events if event.event is ConversationEventType.DELTA]
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)

    assert [(event.data["channel"], event.data["text"]) for event in deltas] == [
        ("reasoning", "reason"),
        ("final", "answer"),
    ]
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


@pytest.mark.parametrize(
    ("thinking_mode", "visibility", "expected_channels"),
    [
        (ThinkingMode.DISABLED, ThinkingVisibility.HIDDEN, ["final"]),
        (ThinkingMode.DISABLED, ThinkingVisibility.VISIBLE, ["final"]),
        (ThinkingMode.ENABLED, ThinkingVisibility.HIDDEN, ["final"]),
        (ThinkingMode.ENABLED, ThinkingVisibility.VISIBLE, ["reasoning", "final"]),
    ],
)
def test_thinking_generation_and_visibility_combinations_are_separate(
    thinking_mode: ThinkingMode,
    visibility: ThinkingVisibility,
    expected_channels: list[str],
) -> None:
    inference = FakeInference(
        lambda: FakeStream(text_deltas=("<think>private-trace-2371</think>answer",))
    )

    events = list(
        service(inference)
        .start(conversation_input(thinking_mode=thinking_mode, visibility=visibility))
        .events()
    )

    assert inference.requests[0].parameters.thinking_mode is thinking_mode
    assert [
        str(event.data["channel"]) for event in events if event.event is ConversationEventType.DELTA
    ] == expected_channels
    if visibility is ThinkingVisibility.HIDDEN or thinking_mode is ThinkingMode.DISABLED:
        assert "private-trace-2371" not in repr(events)


def test_unavailable_thinking_control_rejects_enablement_without_taking_gate() -> None:
    inference = FakeInference()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        thinking_control_available=False,
    )

    with pytest.raises(InferenceError) as captured:
        generation.start(conversation_input(thinking_mode=ThinkingMode.ENABLED))
    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY

    completed = list(
        generation.start(conversation_input(thinking_mode=ThinkingMode.DISABLED)).events()
    )
    assert completed[-1].event is ConversationEventType.COMPLETED


def test_final_answer_token_exhaustion_is_explicit() -> None:
    inference = FakeInference(
        lambda: FakeStream(
            text_deltas=("<think>unfinished",),
            finish_reason=FinishReason.LENGTH,
        )
    )

    events = list(service(inference).start(conversation_input()).events())
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]

    assert any(event.data.get("code") == "final_answer_token_limit" for event in warnings)
    assert any(event.data.get("message") == TOKEN_LIMIT_WARNING for event in warnings)


def test_busy_cancel_and_post_cancel_generation_release_the_gate() -> None:
    streams: list[FakeStream] = []

    def factory() -> FakeStream:
        result = FakeStream(text_deltas=("chunk",))
        streams.append(result)
        return result

    generation = service(FakeInference(factory))
    first = generation.start(conversation_input())
    with pytest.raises(InferenceError) as captured:
        generation.start(conversation_input())
    assert captured.value.code is InferenceErrorCode.MODEL_BUSY
    assert generation.cancel("wrong-request") is False
    assert generation.cancel(first.request_id) is True

    first_events = list(first.events())
    assert ConversationEventType.CANCELLED in event_types(first_events)
    assert streams == []

    second_events = list(generation.start(conversation_input()).events())
    assert second_events[-1].event is ConversationEventType.COMPLETED


def test_stream_failure_is_sanitized_and_releases_the_gate() -> None:
    call_count = 0

    def factory() -> FakeStream:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return FakeStream(
                failure=InferenceError(
                    code=InferenceErrorCode.GENERATION_FAILED,
                    safe_message="Safe generation failure.",
                )
            )
        return FakeStream()

    generation = service(FakeInference(factory))
    failed = list(generation.start(conversation_input()).events())
    recovered = list(generation.start(conversation_input()).events())

    assert failed[-1].event is ConversationEventType.ERROR
    assert failed[-1].data["message"] == "Safe generation failure."
    assert recovered[-1].event is ConversationEventType.COMPLETED


def test_post_generation_summary_is_sequential_buffered_and_canonical() -> None:
    pending_streams = iter(
        (
            FakeStream(text_deltas=("<think>normal secret</think>Long original answer",)),
            FakeStream(text_deltas=("<think>summary secret</think>Short summary",)),
        )
    )
    inference = FakeInference(lambda: next(pending_streams))

    events = list(
        service(inference)
        .start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
        .events()
    )

    assert event_types(events) == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.STATUS,
        ConversationEventType.DELTA,
        ConversationEventType.COMPLETED,
    ]
    assert events[0].data["state"] == "preparing"
    assert events[1].data["state"] == "guarding"
    assert events[2].data["state"] == "generating_answer"
    assert events[3].data["state"] == "summarizing_answer"
    assert events[4].data["text"] == "Short summary"
    serialized_events = repr([event.model_dump(mode="json") for event in events])
    assert "normal secret" not in serialized_events
    assert "summary secret" not in serialized_events
    assert "Long original answer" not in serialized_events

    assert len(inference.requests) == 2
    original_request, summary_request = inference.requests
    assert original_request.parameters.max_new_tokens == 128
    assert summary_request.model_key == original_request.model_key
    assert summary_request.parameters.max_new_tokens == 1024
    assert summary_request.parameters.thinking_mode is ThinkingMode.DISABLED
    assert len(summary_request.messages) == 2
    assert "Long original answer" in summary_request.messages[-1].content
    assert "first" not in summary_request.messages[-1].content
    assert "next" not in summary_request.messages[-1].content

    completed = events[-1]
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "Short summary",
    }
    assert completed.data["transformation"] == {
        "summary_mode": "post_generation",
        "summary_applied": True,
        "fallback_used": False,
        "original_finish_reason": "stop",
        "summary_finish_reason": "stop",
    }
    assert "original_assistant_message" not in completed.data
    assert "summary_assistant_message" not in completed.data


@pytest.mark.parametrize(
    "summary_stream",
    [
        FakeStream(text_deltas=("partial summary",), finish_reason=FinishReason.LENGTH),
        FakeStream(text_deltas=("   ",)),
        FakeStream(text_deltas=("<think>unclosed reasoning",)),
        NoTerminalStream(),
        FakeStream(
            failure=InferenceError(
                code=InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED,
                safe_message="Safe context error.",
            )
        ),
    ],
)
def test_invalid_summary_falls_back_to_original_without_leaking_partial_output(
    summary_stream: FakeStream,
) -> None:
    pending_streams = iter((FakeStream(text_deltas=("Original answer",)), summary_stream))
    inference = FakeInference(lambda: next(pending_streams))

    events = list(
        service(inference)
        .start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
        .events()
    )

    display = "".join(
        str(event.data["text"]) for event in events if event.event is ConversationEventType.DELTA
    )
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    completed = events[-1]
    assert display == "Original answer"
    assert all("partial summary" not in repr(event.data) for event in events)
    assert any(event.data["code"] == "summary_fallback_original" for event in warnings)
    assert completed.event is ConversationEventType.COMPLETED
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "Original answer",
    }
    assert completed.data["transformation"] == {
        "summary_mode": "post_generation",
        "summary_applied": False,
        "fallback_used": True,
        "original_finish_reason": "stop",
        "summary_finish_reason": None,
    }
    assert "original_assistant_message" not in completed.data
    assert "summary_assistant_message" not in completed.data


def test_cancel_between_normal_and_summary_is_not_a_fallback_or_history_result() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("Original answer",)))
    session = service(inference).start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
    events = session.events()

    preparing = next(events)
    assert preparing.event is ConversationEventType.STATUS
    assert preparing.data["state"] == "preparing"
    guarding = next(events)
    assert guarding.event is ConversationEventType.STATUS
    assert guarding.data["state"] == "guarding"
    assert next(events).event is ConversationEventType.START
    status = next(events)
    assert status.event is ConversationEventType.STATUS
    assert len(inference.requests) == 1
    session.request_cancel()
    remaining = list(events)

    assert event_types(remaining) == [ConversationEventType.CANCELLED]
    assert len(inference.requests) == 1
    assert all(event.event is not ConversationEventType.WARNING for event in remaining)
    assert session.finished


def test_context_usage_is_absent_when_backend_reports_no_usage() -> None:
    events = list(service(FakeInference()).start(conversation_input()).events())

    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assert completed.data["context_usage"] is None


def test_context_usage_breakdown_uses_text_token_counter_and_effective_context_size() -> None:
    usage = TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120)
    inference = FakeInference(lambda: FakeStream(usage=usage))
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        text_token_counter=len,
        effective_context_size=1000,
    )

    events = list(
        generation.start(conversation_input(thinking_mode=ThinkingMode.DISABLED)).events()
    )

    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    context_usage = completed.data["context_usage"]
    assert context_usage is not None
    system_prompt_tokens = len(JAPANESE_RESPONSE_INSTRUCTION)
    assert context_usage == {
        "prompt_tokens": 100,
        "completion_tokens": 20,
        "total_tokens": 120,
        "loaded_context_size": 1000,
        "usage_ratio": pytest.approx(0.12),
        "breakdown": {
            "conversation_history_tokens": 100 - system_prompt_tokens,
            "system_prompt_tokens": system_prompt_tokens,
            "rag_context_tokens": 0,
            "free_tokens": 880,
        },
    }


def test_context_usage_breakdown_separates_rag_reference_from_system_prompt() -> None:
    # P7-RW3-C (P7-CODEX-012): `prompt_tokens` must comfortably exceed the
    # Reference Message's own length now that `CURRENT_EVIDENCE_AUTHORITY_
    # INSTRUCTION` is prepended to it at splice time - this fake `usage`
    # is an arbitrary backend-reported total decoupled from real message
    # content length, not one of the tight token/character budgets other
    # tests calibrate against, so it is simply raised here.
    usage = TokenUsage(prompt_tokens=2000, completion_tokens=50, total_tokens=2050)
    inference = FakeInference(lambda: FakeStream(usage=usage))
    rag = BudgetAwareGroundedRag()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=lambda messages, thinking_mode: sum(
            len(message.content) for message in messages
        ),
        text_token_counter=len,
        effective_context_size=4096,
    )
    value = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="EASAとは?"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            documentation_rag_mode=DocumentationRagMode.ENABLED,
        ),
    )

    events = list(generation.start(value).events())

    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    breakdown = _as_dict(_as_dict(completed.data["context_usage"])["breakdown"])
    reference_message = inference.requests[0].messages[1]
    assert reference_message.name == "documentation_reference"
    assert breakdown["rag_context_tokens"] == len(reference_message.content)
    assert breakdown["system_prompt_tokens"] == len(JAPANESE_RESPONSE_INSTRUCTION)
    assert breakdown["conversation_history_tokens"] == 2000 - (
        breakdown["rag_context_tokens"] + breakdown["system_prompt_tokens"]
    )


def test_context_usage_reflects_original_turn_not_summary_subrequest() -> None:
    pending_streams = iter(
        (
            FakeStream(
                text_deltas=("Long original answer",),
                usage=TokenUsage(prompt_tokens=800, completion_tokens=100, total_tokens=900),
            ),
            FakeStream(
                text_deltas=("Short summary",),
                usage=TokenUsage(prompt_tokens=30, completion_tokens=10, total_tokens=40),
            ),
        )
    )
    inference = FakeInference(lambda: next(pending_streams))
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        text_token_counter=len,
        effective_context_size=4096,
    )

    events = list(
        generation.start(
            conversation_input(
                thinking_mode=ThinkingMode.DISABLED,
                summary_mode=SummaryMode.POST_GENERATION,
            )
        ).events()
    )

    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    context_usage = _as_dict(completed.data["context_usage"])
    assert context_usage["prompt_tokens"] == 800
    assert context_usage["completion_tokens"] == 100
    assert context_usage["total_tokens"] == 900


def test_context_usage_prompt_injection_defaults_off_and_adds_no_system_message() -> None:
    inference = FakeInference()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        chat_prompt_token_counter=lambda messages, thinking_mode: sum(
            len(message.content) for message in messages
        ),
        effective_context_size=4096,
    )

    list(generation.start(conversation_input(thinking_mode=ThinkingMode.DISABLED)).events())

    request = inference.requests[0]
    assert all(message.name != "context_usage_notice" for message in request.messages)


def test_context_usage_prompt_injection_when_enabled_adds_reactive_only_system_message() -> None:
    inference = FakeInference()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        chat_prompt_token_counter=lambda messages, thinking_mode: sum(
            len(message.content) for message in messages
        ),
        effective_context_size=4096,
    )

    list(
        generation.start(
            conversation_input(
                thinking_mode=ThinkingMode.DISABLED,
                context_usage_prompt_injection_mode=ContextUsagePromptInjectionMode.ENABLED,
            )
        ).events()
    )

    request = inference.requests[0]
    notice = next(message for message in request.messages if message.name == "context_usage_notice")
    assert notice.role is MessageRole.SYSTEM
    assert "%" in notice.content
    assert "尋ねられた場合にのみ" in notice.content
    assert "自発的に言及しないで" in notice.content


def test_context_usage_prompt_injection_is_skipped_without_a_chat_prompt_token_counter() -> None:
    inference = FakeInference()
    generation = service(inference)

    list(
        generation.start(
            conversation_input(
                context_usage_prompt_injection_mode=ContextUsagePromptInjectionMode.ENABLED,
            )
        ).events()
    )

    request = inference.requests[0]
    assert all(message.name != "context_usage_notice" for message in request.messages)


def test_expressive_mode_defaults_off_and_adds_no_system_message() -> None:
    inference = FakeInference()
    generation = service(inference)

    list(generation.start(conversation_input()).events())

    request = inference.requests[0]
    assert all(message.name != "expressive_style_notice" for message in request.messages)


def test_expressive_mode_when_enabled_adds_a_style_only_system_message() -> None:
    inference = FakeInference()
    generation = service(inference)

    list(
        generation.start(
            conversation_input(expressive_mode=ExpressiveMode.ENABLED),
        ).events()
    )

    request = inference.requests[0]
    notice = next(
        message for message in request.messages if message.name == "expressive_style_notice"
    )
    assert notice.role is MessageRole.SYSTEM
    assert "推論の正確性" in notice.content
    assert "www" in notice.content
    assert "絵文字" in notice.content
    assert "顔文字" in notice.content


def test_expressive_and_context_notices_follow_base_instruction() -> None:
    inference = FakeInference()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        chat_prompt_token_counter=lambda messages, thinking_mode: sum(
            len(message.content) for message in messages
        ),
        effective_context_size=4096,
    )

    list(
        generation.start(
            conversation_input(
                thinking_mode=ThinkingMode.DISABLED,
                expressive_mode=ExpressiveMode.ENABLED,
                context_usage_prompt_injection_mode=ContextUsagePromptInjectionMode.ENABLED,
            )
        ).events()
    )

    request = inference.requests[0]
    names = [message.name for message in request.messages]
    # Both injections always insert right after the leading (unnamed) base
    # instruction, so the base instruction stays first regardless of order;
    # the two notices' relative order between themselves is incidental.
    assert names[0] is None
    assert request.messages[0].role is MessageRole.SYSTEM
    assert "expressive_style_notice" in names
    assert "context_usage_notice" in names


def test_context_usage_breakdown_defaults_to_zero_without_a_text_token_counter() -> None:
    usage = TokenUsage(prompt_tokens=64, completion_tokens=8, total_tokens=72)
    inference = FakeInference(lambda: FakeStream(usage=usage))

    events = list(service(inference).start(conversation_input()).events())

    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    breakdown = _as_dict(_as_dict(completed.data["context_usage"])["breakdown"])
    assert breakdown == {
        "conversation_history_tokens": 64,
        "system_prompt_tokens": 0,
        "rag_context_tokens": 0,
        "free_tokens": 4096 - 72,
    }
