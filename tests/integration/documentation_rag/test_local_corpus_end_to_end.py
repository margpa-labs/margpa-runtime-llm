"""Phase 7 (P7-B/C/D): Local Corpus documents flow end-to-end through the
same `DocumentationRagApplicationService` pipeline Phase 2's fixed project
documentation corpus already uses — register -> retrieve -> assemble
context -> citation -> persistable evidence, distinguishable by
`corpus_source_class`/`source_class` from Project Docs citations.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from typing import Any, cast

from margpa_runtime_llm.adapters.documentation_rag import (
    Bm25DocumentationRetriever,
    BoundedDocumentationContextAssembler,
    CompositeDocumentSource,
    DeterministicMarkdownChunker,
    InMemoryLexicalIndexStore,
    JsonFileLocalCorpusRegistry,
    LocalCorpusDocumentSource,
    LocalMarkdownDocumentSource,
    SystemCitationAdapter,
)
from margpa_runtime_llm.adapters.documentation_rag.lexical_tokenizer import (
    JapaneseAwareLexicalTokenizer,
)
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
from margpa_runtime_llm.modules.documentation_rag.application import (
    DocumentationRagApplicationService,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS,
    DocumentationChunkingConfig,
    DocumentationContextConfig,
    DocumentationCorpusConfig,
    DocumentationGroundingState,
    DocumentationLimitsConfig,
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagRequestContext,
    DocumentationRetrievalConfig,
    LocalDocumentationRagFeatureConfig,
    build_turn_citation_evidence,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_SOURCE_CLASS,
    LocalCorpusDocumentInput,
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


def _feature() -> LocalDocumentationRagFeatureConfig:
    return LocalDocumentationRagFeatureConfig(
        profile_key="local.documentation-rag.lexical",
        mode="enabled",
        provider_key="local_lexical",
        provider_display_name="Local Lexical RAG",
        active_phase="phase_7",
        corpus=DocumentationCorpusConfig(),
        limits=DocumentationLimitsConfig(),
        chunking=DocumentationChunkingConfig(),
        retrieval=DocumentationRetrievalConfig(minimum_score=0.0),
        context=DocumentationContextConfig(),
    )


def _service(
    tmp_path: Path,
) -> tuple[DocumentationRagApplicationService, JsonFileLocalCorpusRegistry]:
    feature = _feature()
    project = tmp_path / "project"
    docs_dir = project / "docs/project/current"
    docs_dir.mkdir(parents=True)
    (docs_dir / "project_ja.md").write_text(
        "# Project概要\n\nMARGPAはRuntime Governanceを行うFrameworkです。\n",
        encoding="utf-8",
    )
    registry = JsonFileLocalCorpusRegistry(runtime_data_root=tmp_path / "runtime_data")
    composite = CompositeDocumentSource(
        sources_by_class={
            DOCUMENTATION_RAG_CITATION_SOURCE_CLASS: LocalMarkdownDocumentSource(
                project_root=project, feature=feature
            ),
            LOCAL_CORPUS_SOURCE_CLASS: LocalCorpusDocumentSource(
                registry=registry, project_root=project
            ),
        }
    )
    tokenizer = JapaneseAwareLexicalTokenizer()
    service = DocumentationRagApplicationService(
        source=composite,
        chunker=DeterministicMarkdownChunker(feature.chunking),
        index_store=InMemoryLexicalIndexStore(),
        retriever=Bm25DocumentationRetriever(tokenizer=tokenizer, config=feature.retrieval),
        context_assembler=BoundedDocumentationContextAssembler(token_counter=len),
        citation=SystemCitationAdapter(),
        retrieval_config=feature.retrieval,
        context_budget=feature.context.as_budget(),
        profile_digest="test-profile-digest",
        max_chunks=feature.limits.max_chunks,
    )
    return service, registry


def _request_context() -> DocumentationRagRequestContext:
    return DocumentationRagRequestContext(
        effective_context_size=4096,
        requested_max_new_tokens=512,
        system_history_current_prompt_tokens=100,
        prompt_token_count_exact=True,
    )


def test_local_corpus_document_is_retrieved_and_cited_with_its_own_source_class(
    tmp_path: Path,
) -> None:
    service, registry = _service(tmp_path)
    registry.register(
        LocalCorpusDocumentInput(
            title="研究メモ",
            content="有機化学の量子化Caveatについての研究メモです。",
        )
    )

    augmentation = service.augment_with_context("量子化Caveat", _request_context())

    assert augmentation.evidence.grounding_state is DocumentationGroundingState.GROUNDED_READY
    local_blocks = [
        block
        for block in augmentation.reference_blocks
        if block.source_class == LOCAL_CORPUS_SOURCE_CLASS
    ]
    assert local_blocks, "expected at least one Local Corpus reference block"
    assert "量子化Caveat" in local_blocks[0].content
    assert local_blocks[0].project_relative_path.startswith("local-corpus/")
    local_citations = [
        citation
        for citation in augmentation.citations
        if citation.project_relative_path.startswith("local-corpus/")
    ]
    assert local_citations


def test_project_docs_citation_keeps_its_original_source_class_unchanged(tmp_path: Path) -> None:
    service, _ = _service(tmp_path)

    augmentation = service.augment_with_context("MARGPAのRuntime Governance", _request_context())

    assert augmentation.evidence.grounding_state is DocumentationGroundingState.GROUNDED_READY
    assert augmentation.reference_blocks
    assert all(
        block.source_class == DOCUMENTATION_RAG_CITATION_SOURCE_CLASS
        for block in augmentation.reference_blocks
    )


def test_deleted_local_corpus_document_no_longer_contributes_evidence(tmp_path: Path) -> None:
    service, registry = _service(tmp_path)
    record = registry.register(
        LocalCorpusDocumentInput(title="削除予定", content="削除予定Documentの本文です。")
    )
    registry.delete(record.document_id)

    augmentation = service.augment_with_context("削除予定Document", _request_context())

    local_blocks = [
        block
        for block in augmentation.reference_blocks
        if block.source_class == LOCAL_CORPUS_SOURCE_CLASS
    ]
    assert local_blocks == []


def test_nazuna_probe_orion_freshness_update_delete_regression(tmp_path: Path) -> None:
    """P7-RW2-B (P7-CODEX-008), Handoff §7.3's exact required scenario,
    turned into a deterministic Regression Fixture: register -> ask (rev 1)
    -> update (rev 2) -> ask again (must reflect rev 2, not rev 1) -> soft-
    delete -> ask again (must NOT keep citing the deleted fact's evidence,
    must NOT backfill unrelated Project Docs as if they supported it) ->
    each earlier `augment_with_context()` result stays exactly what it was
    when captured (Historical Immutability - nothing here mutates a prior
    Turn's own Evidence in place, so re-asserting the captured objects
    unchanged is a meaningful proof, not a tautology).
    """

    service, registry = _service(tmp_path)
    probe_query = "Nazuna Probe Orionの検証コードは？"  # noqa: RUF001

    # 1. Register rev 1.
    record = registry.register(
        LocalCorpusDocumentInput(
            title="MARGPA Manual Probe 7",
            content="Nazuna Probe Orionの検証コードは CEDAR-7319 である。",
        )
    )

    # 2. Ask in what stands in for the same Conversation; rev 1 grounds it.
    turn_1 = service.augment_with_context(probe_query, _request_context())
    assert turn_1.evidence.grounding_state is DocumentationGroundingState.GROUNDED_READY
    assert turn_1.reference_message is not None
    assert "CEDAR-7319" in turn_1.reference_message
    turn_1_local_citations = [
        citation
        for citation in turn_1.citations
        if citation.project_relative_path.startswith("local-corpus/")
    ]
    assert turn_1_local_citations
    turn_1_digest = turn_1_local_citations[0].document_sha512

    # 3. Update to rev 2.
    registry.update(
        record.document_id,
        LocalCorpusDocumentInput(
            title="MARGPA Manual Probe 7",
            content="Nazuna Probe Orionの検証コードは CEDAR-8420 である。",
        ),
    )

    # 4. A new Turn in what stands in for the same Conversation must reflect
    # rev 2, with a Citation Identity distinct from rev 1's.
    turn_2 = service.augment_with_context(probe_query, _request_context())
    assert turn_2.evidence.grounding_state is DocumentationGroundingState.GROUNDED_READY
    assert turn_2.reference_message is not None
    assert "CEDAR-8420" in turn_2.reference_message
    assert "CEDAR-7319" not in turn_2.reference_message
    turn_2_local_citations = [
        citation
        for citation in turn_2.citations
        if citation.project_relative_path.startswith("local-corpus/")
    ]
    assert turn_2_local_citations
    assert turn_2_local_citations[0].document_sha512 != turn_1_digest

    # 5. Soft-delete the document.
    registry.delete(record.document_id)

    # 6. A new Turn must NOT keep answering from the now-deleted fact, and
    # must NOT show an unrelated Project Docs Citation as if it supported
    # the (now unanswerable) question - it converges to no current
    # evidence instead (NO_HIT: no Local Corpus content anywhere in the
    # current Corpus mentions "Nazuna"/"Probe"/"Orion" any longer, and the
    # BM25 backfill identifier-overlap guard, P7-RW2-B, keeps the unrelated
    # Project Docs chunk out of `context.blocks`/`citations` rather than
    # padding top-k with it).
    turn_3 = service.augment_with_context(probe_query, _request_context())
    assert turn_3.evidence.grounding_state is DocumentationGroundingState.NO_HIT
    assert turn_3.reference_message is None
    assert turn_3.citations == ()
    assert turn_3.reference_blocks == ()

    # 7. A brand-new Conversation (no prior History at all) converges to the
    # identical no-current-evidence outcome - `augment_with_context` is
    # already Conversation-agnostic (only ever sees the latest query text),
    # so this is the same call/assertion as step 6, proving there is no
    # hidden per-Conversation state anywhere in this layer that could make
    # the two diverge.
    turn_4 = service.augment_with_context(probe_query, _request_context())
    assert turn_4.evidence.grounding_state is DocumentationGroundingState.NO_HIT

    # 8. Steps 2/4's captured results are themselves frozen (`ImmutableContract`)
    # and nothing above ever reassigned them - re-affirming their content
    # here is the Historical Immutability check: no code path in this fix
    # rewrites a past Turn's own Citation/Revision/Digest.
    assert "CEDAR-7319" in turn_1.reference_message
    assert turn_1_local_citations[0].document_sha512 == turn_1_digest
    assert "CEDAR-8420" in turn_2.reference_message
    assert turn_2_local_citations[0].document_sha512 != turn_1_digest


class _FakeStream:
    """Mirrors `tests/integration/documentation_rag/test_conversation_rag.
    py`'s own local `FakeStream` (this repo's established per-file
    convention rather than a shared fixture) - a minimal, deterministic
    `GenerationStream` that always yields exactly one scripted answer."""

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
        yield GenerationChunk(request_id="fake", sequence=0, text_delta=self._text, is_final=False)
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

    def __enter__(self) -> _FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class _ScriptedInference:
    """Pops one scripted Candidate answer per Model Call, in order - lets
    the P7-RW3-C Candidate Presentation regression below simulate exactly
    what the User Mac Manual Probe observed (the Model answering with a
    stale Code from its own Conversation History) without needing a real
    LLM."""

    def __init__(self, answers: list[str]) -> None:
        self._answers = list(answers)
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return _FakeStream(self._answers.pop(0))


def _prompt_token_counter(messages: tuple[ChatMessage, ...], thinking_mode: ThinkingMode) -> int:
    del thinking_mode
    return 32 + sum(max(1, len(message.content) // 8) for message in messages)


def _conversation_service(
    inference: _ScriptedInference, rag: DocumentationRagApplicationService
) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(PlainTextOutputParser()),
        model_key="main.model",
        generation_defaults=GenerationParameters(max_new_tokens=128),
        response_language_default=ResponseLanguage.JA,
        presentation_default=ResolvedThinkingPresentationPolicy(
            visibility=ThinkingVisibility.HIDDEN,
            display_label="推論過程",
            persistence=ThinkingPersistence.DISABLED,
            visibility_source=ThinkingPresentationSource.APPLICATION,
            display_label_source=ThinkingPresentationSource.APPLICATION,
            persistence_source=ThinkingPresentationSource.APPLICATION,
        ),
        documentation_rag=rag,
        documentation_rag_availability=DocumentationRagAvailability.AVAILABLE,
        chat_prompt_token_counter=_prompt_token_counter,
        effective_context_size=4096,
    )


def _conversation_turn(messages: tuple[ConversationMessage, ...]) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=messages,
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            documentation_rag_mode=DocumentationRagMode.ENABLED,
        ),
    )


def _completed_event(events: list[ConversationEvent]) -> ConversationEvent:
    return next(event for event in events if event.event is ConversationEventType.COMPLETED)


def _completed_content(events: list[ConversationEvent]) -> str:
    data = cast("dict[str, Any]", _completed_event(events).data)
    return str(cast("dict[str, Any]", data["assistant_message"])["content"])


def test_nazuna_probe_orion_candidate_presentation_regression(tmp_path: Path) -> None:
    """P7-RW3-C (P7-CODEX-012), Handoff §8.4's exact required scenario -
    unlike `test_nazuna_probe_orion_freshness_update_delete_regression`
    above (which only proves `augment_with_context()`'s raw Evidence),
    this drives the real `ConversationGenerationService` end-to-end and
    asserts the actually-presented Candidate (`assistant_message.
    content`) at each step, including the worst-case failure mode the
    User Mac Manual Probe observed: the Model choosing to answer with a
    stale Code straight out of its own Conversation History despite
    Current Evidence saying otherwise. A Deterministic Test cannot make a
    real LLM choose to hallucinate on cue, so the failure mode is
    reproduced directly (a scripted Candidate that names the stale Code)
    and the Consistency Check (P7-RW3-C) is asserted to withhold it -
    this is the Source-side guarantee; real-Model behavior remains the
    User Manual Gate the Controller Review already established.
    """

    service, registry = _service(tmp_path)
    probe_query = "Nazuna Probe Orionの検証コードは？"  # noqa: RUF001

    # 1. Register rev 1, ask - the Model answers correctly with the
    # Current value on its own (the ordinary case).
    record = registry.register(
        LocalCorpusDocumentInput(
            title="MARGPA Manual Probe 8",
            content="Nazuna Probe Orionの検証コードは CEDAR-25123 である。",
        )
    )
    turn_1_input = _conversation_turn(
        (ConversationMessage(role=ConversationRole.USER, content=probe_query),)
    )
    turn_1_events = list(
        _conversation_service(_ScriptedInference(["検証コードは CEDAR-25123 です。"]), service)
        .start(turn_1_input)
        .events()
    )
    turn_1_content = _completed_content(turn_1_events)
    assert "CEDAR-25123" in turn_1_content

    # 2. The Model instead answers with a stale Code that is not Current
    # Evidence (the exact User Mac Manual Probe failure) - the Presented
    # Candidate must never contain it.
    turn_2_input = _conversation_turn(
        (
            ConversationMessage(role=ConversationRole.USER, content=probe_query),
            ConversationMessage(role=ConversationRole.ASSISTANT, content=turn_1_content),
            ConversationMessage(role=ConversationRole.USER, content=probe_query),
        )
    )
    turn_2_events = list(
        _conversation_service(_ScriptedInference(["CEDAR-9847 です。"]), service)
        .start(turn_2_input)
        .events()
    )
    turn_2_content = _completed_content(turn_2_events)
    assert "CEDAR-9847" not in turn_2_content
    assert any(
        event.event is ConversationEventType.WARNING
        and cast("dict[str, Any]", event.data)["code"] == "grounding_consistency_safe_fallback"
        for event in turn_2_events
    )

    # 3. Update to rev 2 - a fresh Turn answers with the *new* value.
    registry.update(
        record.document_id,
        LocalCorpusDocumentInput(
            title="MARGPA Manual Probe 8",
            content="Nazuna Probe Orionの検証コードは CEDAR-12523 である。",
        ),
    )
    turn_3_events = list(
        _conversation_service(_ScriptedInference(["検証コードは CEDAR-12523 です。"]), service)
        .start(turn_2_input)
        .events()
    )
    turn_3_content = _completed_content(turn_3_events)
    assert "CEDAR-12523" in turn_3_content
    assert "CEDAR-25123" not in turn_3_content

    # 3b. The same updated Turn, but the Model answers with the *old* rev
    # 1 value instead (a still-plausible stale-History failure after an
    # Update, not only after a Delete) - also withheld.
    turn_3b_events = list(
        _conversation_service(_ScriptedInference(["CEDAR-25123 です。"]), service)
        .start(turn_2_input)
        .events()
    )
    assert "CEDAR-25123" not in _completed_content(turn_3b_events)

    # 4. Soft-delete - neither the same nor a brand-new Conversation may
    # present a fabricated Code, and Citations must be exactly 0 (NO_HIT).
    registry.delete(record.document_id)
    turn_4_input = _conversation_turn(
        (
            ConversationMessage(role=ConversationRole.USER, content=probe_query),
            ConversationMessage(role=ConversationRole.ASSISTANT, content=turn_3_content),
            ConversationMessage(role=ConversationRole.USER, content=probe_query),
        )
    )
    turn_4_events = list(
        _conversation_service(
            _ScriptedInference(["現在のCorpusには根拠が見当たりません。"]), service
        )
        .start(turn_4_input)
        .events()
    )
    turn_4_retrieval = cast(
        "dict[str, Any]", _completed_event(turn_4_events).data["documentation_retrieval"]
    )
    assert turn_4_retrieval["citations"] == []

    turn_5_events = list(
        _conversation_service(
            _ScriptedInference(["現在のCorpusには根拠が見当たりません。"]), service
        )
        .start(
            _conversation_turn(
                (ConversationMessage(role=ConversationRole.USER, content=probe_query),)
            )
        )
        .events()
    )
    turn_5_retrieval = cast(
        "dict[str, Any]", _completed_event(turn_5_events).data["documentation_retrieval"]
    )
    assert turn_5_retrieval["citations"] == []


def test_deleted_local_corpus_document_denies_a_stale_code_from_conversation_history_regression(
    tmp_path: Path,
) -> None:
    """P7-RW4 (Codex Controller Independent Review, P7-CODEX-013's
    remaining path): unlike `test_nazuna_probe_orion_candidate_
    presentation_regression` above (whose post-delete Scripted answers
    already started from the already-safe "no current evidence" text -
    the Controller's exact complaint, since that never actually
    exercised the defense), this scripts the real User Mac failure the
    Handoff describes: the same Chat's own History already holds a
    stale Code-shaped Identifier from a past Assistant Turn, the source
    Document is deleted, and the Model reproduces that stale Code
    verbatim instead of admitting it has no current grounds."""

    service, registry = _service(tmp_path)
    probe_query = "Nazuna Probe Orionの検証コードは？"  # noqa: RUF001
    stale_answer = "検証コードは CEDAR-9847 です。"

    # 1. Register a Document naming a *different* Code - the deleted
    # Document was never actually the source of the stale Code either,
    # proving the defense does not depend on what the now-deleted
    # Document used to say.
    record = registry.register(
        LocalCorpusDocumentInput(
            title="MARGPA Manual Probe 9",
            content="Nazuna Probe Orionの検証コードは CEDAR-25123 である。",
        )
    )

    # 2. The same Chat's own History already holds a past Assistant Turn
    # naming the stale Code.
    same_chat_history = (
        ConversationMessage(role=ConversationRole.USER, content=probe_query),
        ConversationMessage(role=ConversationRole.ASSISTANT, content=stale_answer),
        ConversationMessage(role=ConversationRole.USER, content=probe_query),
    )

    # 3. Delete the Document - Current Corpus now has zero evidence.
    registry.delete(record.document_id)

    # 4. The Model reproduces the stale Code verbatim - scripted
    # explicitly, never starting from an already-safe answer.
    same_chat_events = list(
        _conversation_service(_ScriptedInference([stale_answer]), service)
        .start(_conversation_turn(same_chat_history))
        .events()
    )

    # 5. The stale Code never reaches the final Presentation.
    same_chat_content = _completed_content(same_chat_events)
    assert "CEDAR-9847" not in same_chat_content
    # 7. It converges to the fixed Safe Grounding Failure text instead.
    assert any(
        event.event is ConversationEventType.WARNING
        and cast("dict[str, Any]", event.data)["code"] == "grounding_consistency_safe_fallback"
        for event in same_chat_events
    )
    # 6. Citations are exactly 0.
    same_chat_retrieval = cast(
        "dict[str, Any]", _completed_event(same_chat_events).data["documentation_retrieval"]
    )
    assert same_chat_retrieval["citations"] == []
    # Never streamed live either - only the (replaced) Safe text is
    # bulk-delivered once, right before COMPLETED.
    same_chat_deltas = [
        event for event in same_chat_events if event.event is ConversationEventType.DELTA
    ]
    assert len(same_chat_deltas) == 1
    assert "CEDAR-9847" not in str(cast("dict[str, Any]", same_chat_deltas[0].data)["text"])

    # 8. A brand-new Chat (no prior History at all), Scripted with the
    # identical stale Candidate, converges to the identical safe result.
    new_chat_events = list(
        _conversation_service(_ScriptedInference([stale_answer]), service)
        .start(
            _conversation_turn(
                (ConversationMessage(role=ConversationRole.USER, content=probe_query),)
            )
        )
        .events()
    )
    new_chat_content = _completed_content(new_chat_events)
    assert "CEDAR-9847" not in new_chat_content
    new_chat_retrieval = cast(
        "dict[str, Any]", _completed_event(new_chat_events).data["documentation_retrieval"]
    )
    assert new_chat_retrieval["citations"] == []

    # 9. Historical Immutability - `same_chat_history` above is a plain
    # frozen tuple/str nothing in this Turn ever reassigns; re-affirming
    # its content is the check that nothing rewrote it in place.
    assert same_chat_history[1].content == stale_answer

    # 10. RAG OFF keeps its existing behavior and live Streaming
    # unchanged - no Documentation Augmentation exists for this Turn at
    # all, so neither `_grounded_rag_turn()` nor `_no_hit_rag_turn()` can
    # ever be True, and the Consistency Check never applies.
    rag_off_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content=probe_query),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            documentation_rag_mode=DocumentationRagMode.DISABLED,
        ),
    )
    rag_off_events = list(
        _conversation_service(_ScriptedInference([stale_answer]), service)
        .start(rag_off_input)
        .events()
    )
    rag_off_deltas = [
        event for event in rag_off_events if event.event is ConversationEventType.DELTA
    ]
    assert len(rag_off_deltas) >= 1
    assert "CEDAR-9847" in _completed_content(rag_off_events)


def test_local_corpus_citation_persists_through_turn_citation_evidence_projection(
    tmp_path: Path,
) -> None:
    service, registry = _service(tmp_path)
    registry.register(
        LocalCorpusDocumentInput(
            title="研究メモ", content="有機化学の量子化Caveatについての研究メモ。"
        )
    )
    augmentation = service.augment_with_context("量子化Caveat", _request_context())

    evidence = build_turn_citation_evidence(
        augmentation,
        conversation_id="conversation-1",
        turn_id="turn-1",
    )

    assert evidence is not None
    assert any(
        citation.project_relative_path.startswith("local-corpus/")
        for citation in evidence.citations
    )
