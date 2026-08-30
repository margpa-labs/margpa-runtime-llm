"""Phase 2-E: atomicity, idempotency, and fail-closed reads for citation evidence."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    SQLiteConversationStore,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationSessionRecord,
    ConversationSessionState,
    ConversationSnapshot,
    ConversationState,
    ConversationStorageError,
    ConversationTurn,
    ConversationTurnId,
    ConversationTurnOrigin,
    ConversationTurnState,
    PersistedConversationMessage,
    PersistedConversationRole,
)
from margpa_runtime_llm.modules.conversation.ports import CommitConversation
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CitationUnavailable,
    DocumentationCitation,
    DocumentationGroundingState,
    DocumentationRetrievalState,
    PersistedTurnCitationEvidence,
)

NOW = datetime(2026, 8, 15, tzinfo=UTC)
_SHA = "b" * 128


def _scope(value: str = "scope-private") -> ConversationScopeId:
    return ConversationScopeId(value=value)


def _store(tmp_path: Path) -> SQLiteConversationStore:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=_scope(),
    )
    store.initialize_new_store()
    return store


def _completed_snapshot(
    conversation_id: str = "conversation-1",
    turn_id: str = "turn-1",
) -> ConversationSnapshot:
    return ConversationSnapshot(
        scope_id=_scope(),
        conversation_id=ConversationId(value=conversation_id),
        state=ConversationState.ACTIVE,
        head_turn_id=ConversationTurnId(value=turn_id),
        created_at=NOW,
        updated_at=NOW,
        sessions=(
            ConversationSessionRecord(
                session_id=ConversationSessionId(value="session-1"),
                conversation_id=ConversationId(value=conversation_id),
                state=ConversationSessionState.CLOSED,
                opened_at=NOW,
                finished_at=NOW,
            ),
        ),
        turns=(
            ConversationTurn(
                turn_id=ConversationTurnId(value=turn_id),
                conversation_id=ConversationId(value=conversation_id),
                session_id=ConversationSessionId(value="session-1"),
                sequence=0,
                state=ConversationTurnState.COMPLETED,
                origin=ConversationTurnOrigin.NORMAL,
                user_message_id=ConversationMessageId(value=f"{turn_id}-user"),
                assistant_message_id=ConversationMessageId(value=f"{turn_id}-assistant"),
                started_at=NOW,
                finished_at=NOW,
            ),
        ),
        messages=(
            PersistedConversationMessage(
                message_id=ConversationMessageId(value=f"{turn_id}-user"),
                conversation_id=ConversationId(value=conversation_id),
                turn_id=ConversationTurnId(value=turn_id),
                sequence=0,
                role=PersistedConversationRole.USER,
                content="hello",
                created_at=NOW,
            ),
            PersistedConversationMessage(
                message_id=ConversationMessageId(value=f"{turn_id}-assistant"),
                conversation_id=ConversationId(value=conversation_id),
                turn_id=ConversationTurnId(value=turn_id),
                sequence=1,
                role=PersistedConversationRole.ASSISTANT,
                content="hi there",
                created_at=NOW,
            ),
        ),
    )


def _citation_evidence(
    conversation_id: str = "conversation-1",
    turn_id: str = "turn-1",
) -> PersistedTurnCitationEvidence:
    return PersistedTurnCitationEvidence(
        conversation_id=conversation_id,
        turn_id=turn_id,
        citation_schema_version=1,
        corpus_revision=_SHA,
        retrieval_state=DocumentationRetrievalState.ENABLED,
        grounding_state=DocumentationGroundingState.GROUNDED_READY,
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
    )


def test_commit_with_citation_evidence_is_readable_afterwards(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnCitationEvidence)
    assert result.citations[0].project_relative_path == "docs/public/overview_ja.md"


def test_no_citation_evidence_reports_not_present(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
        )
    )
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "not_present"


def test_missing_conversation_reports_not_present(tmp_path: Path) -> None:
    store = _store(tmp_path)
    result = store.get_turn_citations("does-not-exist", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "not_present"


def test_commit_and_citation_are_atomic_within_one_transaction(tmp_path: Path) -> None:
    """A failed citation write must roll back the whole turn commit too."""

    store = _store(tmp_path)
    bad_evidence = _citation_evidence(turn_id="turn-does-not-exist")
    with pytest.raises(Exception):  # noqa: B017 - pydantic validation on construction
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=bad_evidence,
        )
    # The conversation must not have been committed by the failed construction attempt.
    assert store.get(_scope(), ConversationId(value="conversation-1")) is None


def test_retrying_the_same_operation_is_idempotent_and_writes_once(tmp_path: Path) -> None:
    store = _store(tmp_path)
    command = CommitConversation(
        scope_id=_scope(),
        operation_id=ConversationOperationId(value="op-1"),
        conversation=_completed_snapshot(),
        citation_evidence=_citation_evidence(),
    )
    first = store.commit(command)
    second = store.commit(command)
    assert first == second
    with sqlite3.connect(store.database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM turn_citations").fetchone()[0]
    assert count == 1


def test_second_citation_write_for_same_turn_under_new_operation_is_rejected(
    tmp_path: Path,
) -> None:
    """Enforces at the storage layer that a completed turn's citations never change."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with pytest.raises(ConversationStorageError):
        store.commit(
            CommitConversation(
                scope_id=_scope(),
                operation_id=ConversationOperationId(value="op-2"),
                expected_revision=1,
                conversation=_completed_snapshot(),
                citation_evidence=_citation_evidence(),
            )
        )


def test_unsupported_citation_schema_version_returns_unavailable(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("UPDATE turn_citations SET citation_schema_version = 999999")
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "unsupported_schema_version"


def _rewrite_citations_json(
    store: SQLiteConversationStore,
    *,
    citation_schema_version: object,
) -> None:
    """Tamper only the embedded envelope version, keeping the digest self-consistent."""

    with sqlite3.connect(store.database_path) as connection:
        row = connection.execute("SELECT citations_json FROM turn_citations").fetchone()
        envelope = json.loads(bytes(row[0]).decode("utf-8"))
        envelope["citation_evidence"]["citation_schema_version"] = citation_schema_version
        payload = json.dumps(
            envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest = hashlib.sha512(payload).hexdigest()
        connection.execute(
            "UPDATE turn_citations SET citations_json = ?, citations_sha512 = ?",
            (payload, digest),
        )


# --- P2E-CODEX-003 Test Matrix: column-only-unknown / envelope-only-unknown /
# both-known-but-mismatched / normal-matching-version. ---


def test_normal_matching_version_is_accepted(tmp_path: Path) -> None:
    """Column == embedded == known current version: the baseline of the matrix."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnCitationEvidence)
    assert result.citation_schema_version == 1


def test_column_only_unknown_version_is_rejected(tmp_path: Path) -> None:
    """DB column claims an unknown future version; embedded envelope still says 1."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("UPDATE turn_citations SET citation_schema_version = 999")
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "unsupported_schema_version"


def test_embedded_only_unknown_version_is_rejected(tmp_path: Path) -> None:
    """P2E-CODEX-003: the exact reported gap — column says 1, embedded envelope says 999."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    _rewrite_citations_json(store, citation_schema_version=999)
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "unsupported_schema_version"


def test_column_and_embedded_known_but_mismatched_is_rejected(tmp_path: Path) -> None:
    """Both values individually look plausible but disagree with each other."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    # citation_schema_version column stays at 1 (the only currently-known version);
    # the embedded envelope is rewritten to a *different*, still-small integer.
    _rewrite_citations_json(store, citation_schema_version=2)
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "unsupported_schema_version"


# --- P2E-CODEX-005: a non-numeric DB column must degrade safely, never raise. ---


def test_non_numeric_schema_version_column_via_get_turn_citations_does_not_raise(
    tmp_path: Path,
) -> None:
    """SQLite's permissive type affinity can store TEXT in an INTEGER-declared column."""

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("UPDATE turn_citations SET citation_schema_version = 'not-a-number'")
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "corrupt_record"


def test_non_numeric_schema_version_column_via_get_conversation_citations_does_not_raise(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute(
            "UPDATE turn_citations SET citation_schema_version = 'also-not-a-number'"
        )
    mapping = store.get_conversation_citations("conversation-1")
    result = mapping["turn-1"]
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "corrupt_record"
    # The conversation body itself must still be fully readable.
    assert store.get(_scope(), ConversationId(value="conversation-1")) is not None


def test_decoder_rejects_null_and_float_schema_version_without_raising() -> None:
    """Defense in depth for the decoder itself, independent of the DB's own NOT NULL /

    INTEGER-affinity constraints (which already prevent NULL and most non-numeric
    values from ever being written in the first place).
    """

    digest = hashlib.sha512(b"{}").hexdigest()
    for bad_value in (None, 1.5, "1"):
        result = SQLiteConversationStore._decode_citation_evidence(
            "turn-1", bad_value, b"{}", digest
        )
        assert isinstance(result, CitationUnavailable)
        assert result.reason == "corrupt_record"


def test_corrupt_citation_record_returns_unavailable_not_raise(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute(
            "UPDATE turn_citations SET citations_json = ?",
            (json.dumps({"tampered": True}).encode("utf-8"),),
        )
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, CitationUnavailable)
    assert result.reason == "corrupt_record"
    # The conversation itself must still load even though its citation is unavailable.
    assert store.get(_scope(), ConversationId(value="conversation-1")) is not None


def test_get_conversation_citations_returns_a_mapping_by_turn(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    mapping = store.get_conversation_citations("conversation-1")
    assert set(mapping) == {"turn-1"}
    assert isinstance(mapping["turn-1"], PersistedTurnCitationEvidence)


def test_rag_off_commit_writes_zero_citation_rows(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=None,
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM turn_citations").fetchone()[0]
    assert count == 0


def test_pre_source_class_citation_record_still_decodes_with_default(tmp_path: Path) -> None:
    """P7-RW2-A (P7-CODEX-007): a record written before `DocumentationCitation.
    source_class` existed must still decode, filling the same default
    `DOCUMENTATION_RAG_CITATION_SOURCE_CLASS` the field itself defaults to.
    """

    store = _store(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            citation_evidence=_citation_evidence(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        row = connection.execute("SELECT citations_json FROM turn_citations").fetchone()
        envelope = json.loads(bytes(row[0]).decode("utf-8"))
        del envelope["citation_evidence"]["citations"][0]["source_class"]
        payload = json.dumps(
            envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest = hashlib.sha512(payload).hexdigest()
        connection.execute(
            "UPDATE turn_citations SET citations_json = ?, citations_sha512 = ?",
            (payload, digest),
        )
    result = store.get_turn_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnCitationEvidence)
    assert result.citations[0].source_class == "documentation_rag_citation"
    assert result.citations[0].chunk_id == _SHA
