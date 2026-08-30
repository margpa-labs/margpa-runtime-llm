"""Phase 2-E: Citation Evidence survives Restart/Resume/Retry/Regenerate/Branch Select.

Exercises the real `PersistentConversationService` + `SQLiteConversationStore`
end-to-end (generation -> commit -> persisted read), not just the storage
layer in isolation (see `tests/unit/conversation/test_citation_evidence_sqlite_store.py`
for the storage-layer unit tests).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
    SQLiteConversationStore,
    build_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationTurnId,
    ConversationTurnOrigin,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CitationUnavailable,
    DocumentationAugmentation,
    DocumentationCitation,
    DocumentationEvidence,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRagMode,
    DocumentationRetrievalState,
    DocumentationWarning,
    PersistedTurnCitationEvidence,
)
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")
_SHA = "c" * 128


def op(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def _augmentation() -> DocumentationAugmentation:
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=True,
        reference_message="see references",
        citations=(
            DocumentationCitation(
                citation_id="citation-1",
                project_relative_path="docs/public/overview_ja.md",
                heading_breadcrumb="Overview",
                chunk_id=_SHA,
                document_sha512=_SHA,
                retrieval_score=1.0,
                selected_order=1,
            ),
        ),
        evidence=DocumentationEvidence(
            query_digest=_SHA,
            corpus_manifest_digest=_SHA,
            retriever_key="bm25",
            retriever_version="1",
            selected_chunk_ids=(_SHA,),
            selected_document_digests=(_SHA,),
            selected_scores=(1.0,),
            base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
            context_budget=100,
            context_budget_unit=DocumentationMeasurementUnit.TOKENS,
            context_used=10,
            context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
            context_measurement_limit=100,
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
            retrieval_duration_ms=1.0,
        ),
        document_count=1,
        selected_chunk_count=1,
        duration_ms=1.0,
    )


class CitingSession:
    """Completes with a fixed answer and a real RAG augmentation attached."""

    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.documentation_augmentation = _augmentation()

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "assistant_message": {"role": "assistant", "content": self.answer},
            },
        )


class CitingGeneration:
    def __init__(self, answer: str = "cited answer") -> None:
        self.answer = answer
        self.calls = 0

    def start(self, _: object) -> CitingSession:
        self.calls += 1
        return CitingSession(f"request-{self.calls}", self.answer)


def _settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.ENABLED,
    )


def _identities(suffix: str) -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value=f"turn-{suffix}"),
        user_message_id=ConversationMessageId(value=f"message-user-{suffix}"),
        assistant_message_id=ConversationMessageId(value=f"message-assistant-{suffix}"),
        append_operation_id=op(f"append-{suffix}"),
        start_operation_id=op(f"start-{suffix}"),
        terminal_operation_id=op(f"complete-{suffix}"),
    )


def _new_service(root: Path, generation: object) -> PersistentConversationService:
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(enabled=True, runtime_data_root=root, scope_id=SCOPE),
        generation_service=generation,  # type: ignore[arg-type]
    )
    assert built.store is not None and built.service is not None
    if built.store.inspect_schema().readiness.value == "empty":
        built.store.initialize_new_store()
    else:
        built.store.open_ready_store()
    built.service.recover_incomplete_conversations()
    return built.service


def test_citations_survive_server_restart(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    generation = CitingGeneration()
    service = _new_service(root, generation)
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user question",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED

    # Simulate a server restart: a brand-new adapter instance, no in-memory state carried over.
    reopened = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=SCOPE)
    reopened.open_ready_store()
    result = reopened.get_turn_citations(CID.value, "turn-1")
    assert isinstance(result, PersistedTurnCitationEvidence)
    assert result.citations[0].project_relative_path == "docs/public/overview_ja.md"


def test_citations_survive_reopen_from_list_and_resume(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    generation = CitingGeneration()
    service = _new_service(root, generation)
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user question",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    # "Reopen from the Chat List": fetch citations for a conversation freshly looked up,
    # without any live SSE Page Memory for this process.
    fresh_service = _new_service(root, generation)
    reopened_citations = fresh_service.get_conversation_citations(CID)
    assert set(reopened_citations) == {"turn-1"}

    # Resume must not disturb persisted citation evidence.
    fresh_service.resume_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-resume"),
        operation_id=op("resume"),
        expected_revision=fresh_service.get_conversation(CID).storage_revision,
    )
    after_resume = fresh_service.get_conversation_citations(CID)
    assert set(after_resume) == {"turn-1"}
    assert isinstance(after_resume["turn-1"], PersistedTurnCitationEvidence)


def test_regenerate_preserves_source_citations_and_gets_its_own(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    generation = CitingGeneration(answer="first answer")
    service = _new_service(root, generation)
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user question",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    source_before = service.get_conversation_citations(CID)["turn-1"]
    assert isinstance(source_before, PersistedTurnCitationEvidence)

    generation.answer = "regenerated answer"
    stored = service.get_conversation(CID)
    tuple(
        service.generate_derived_turn(
            conversation_id=CID,
            source_turn_id=ConversationTurnId(value="turn-1"),
            origin=ConversationTurnOrigin.REGENERATE,
            expected_revision=stored.storage_revision,
            settings=_settings(),
            identities=_identities("2"),
        )
    )

    citations = service.get_conversation_citations(CID)
    assert set(citations) == {"turn-1", "turn-2"}
    source_after = citations["turn-1"]
    derived = citations["turn-2"]
    assert isinstance(source_after, PersistedTurnCitationEvidence)
    assert isinstance(derived, PersistedTurnCitationEvidence)
    # The source turn's citation row is byte-for-byte unchanged by the regenerate commit.
    assert source_after == source_before


def test_branch_select_does_not_mutate_citation_rows(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    generation = CitingGeneration(answer="first answer")
    service = _new_service(root, generation)
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user question",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    generation.answer = "regenerated answer"
    stored = service.get_conversation(CID)
    tuple(
        service.generate_derived_turn(
            conversation_id=CID,
            source_turn_id=ConversationTurnId(value="turn-1"),
            origin=ConversationTurnOrigin.REGENERATE,
            expected_revision=stored.storage_revision,
            settings=_settings(),
            identities=_identities("2"),
        )
    )
    before = service.get_conversation_citations(CID)

    stored = service.get_conversation(CID)
    service.select_branch_head(
        conversation_id=CID,
        completed_turn_id=ConversationTurnId(value="turn-1"),
        operation_id=op("select-branch"),
        expected_revision=stored.storage_revision,
    )

    after = service.get_conversation_citations(CID)
    assert after == before


def _no_hit_augmentation() -> DocumentationAugmentation:
    sha = "f" * 128
    evidence = DocumentationEvidence(
        query_digest=sha,
        corpus_manifest_digest=sha,
        retriever_key="bm25",
        retriever_version="1",
        base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
        context_budget=100,
        context_budget_unit=DocumentationMeasurementUnit.TOKENS,
        context_used=0,
        context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
        context_measurement_limit=100,
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
        retrieval_duration_ms=1.0,
    )
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=True,
        evidence=evidence,
        warnings=(DocumentationWarning(code="documentation_no_hit", message="no evidence"),),
        document_count=0,
        selected_chunk_count=0,
        duration_ms=1.0,
    )


class NoHitCitingSession:
    """P7-RW5-A (P7-CODEX-014): a real NO_HIT Turn - zero Citations, one
    `documentation_no_hit` Warning - contrasted with `NoCitationSession`
    below (RAG disabled: no `DocumentationAugmentation` at all). Both reach
    `complete_generation()` with empty `citations`, but only NO_HIT is real
    Evidence worth persisting."""

    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.documentation_augmentation = _no_hit_augmentation()

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "assistant_message": {"role": "assistant", "content": self.answer},
            },
        )


class NoHitCitingGeneration:
    def __init__(self, answer: str = "no current grounds") -> None:
        self.answer = answer
        self.calls = 0

    def start(self, _: object) -> NoHitCitingSession:
        self.calls += 1
        return NoHitCitingSession(f"request-{self.calls}", self.answer)


def test_no_hit_turn_persists_zero_citation_evidence_and_survives_restart(
    tmp_path: Path,
) -> None:
    """P7-RW5-A (P7-CODEX-014): unlike RAG disabled (`test_rag_disabled_
    turn_reports_not_present_not_corrupt` below), a NO_HIT Turn's
    Grounding State/Warning Codes must actually be written - previously
    `build_turn_citation_evidence()` treated "zero Citations" as
    equivalent to "nothing to persist" for every State, including NO_HIT,
    so a Persistent Detail reload silently lost the NO_HIT evidence a Live
    SSE `retrieval` event had already shown."""
    root = tmp_path / "runtime-data"
    generation = NoHitCitingGeneration()
    service = _new_service(root, generation)
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="question with no current grounds",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED

    result = service.get_conversation_citations(CID).get("turn-1")
    assert isinstance(result, PersistedTurnCitationEvidence)
    assert result.grounding_state is DocumentationGroundingState.NO_HIT
    assert result.citations == ()
    assert result.warning_codes == ("documentation_no_hit",)

    # Simulate a server restart: a brand-new adapter instance, no in-memory state carried over.
    reopened = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=SCOPE)
    reopened.open_ready_store()
    reopened_result = reopened.get_turn_citations(CID.value, "turn-1")
    assert isinstance(reopened_result, PersistedTurnCitationEvidence)
    assert reopened_result.grounding_state is DocumentationGroundingState.NO_HIT
    assert reopened_result.warning_codes == ("documentation_no_hit",)


def test_rag_disabled_turn_reports_not_present_not_corrupt(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"

    class NoCitationSession:
        request_id = "request-no-rag"
        documentation_augmentation = None

        def events(self) -> Iterator[ConversationEvent]:
            yield ConversationEvent(
                event=ConversationEventType.COMPLETED,
                data={
                    "request_id": self.request_id,
                    "assistant_message": {"role": "assistant", "content": "no citations"},
                },
            )

    class NoCitationGeneration:
        def start(self, _: object) -> NoCitationSession:
            return NoCitationSession()

    service = _new_service(root, NoCitationGeneration())
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user question",
            settings=_settings(),
            identities=_identities("1"),
        )
    )
    result = service.get_conversation_citations(CID).get("turn-1")
    assert result is None or (
        isinstance(result, CitationUnavailable) and result.reason == "not_present"
    )
