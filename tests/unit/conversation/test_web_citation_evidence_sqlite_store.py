"""P8-MR7-3 (P8-CODEX-015): Web Citation Evidence Schema 1/2 Reader
Backward Compatibility, against real Encoded SQLite Records — mirrors
`test_citation_evidence_sqlite_store.py`'s established pattern for
Documentation RAG Citations (see its
`test_pre_source_class_citation_record_still_decodes_with_default`), applied
to the Web Citation store instead."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

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
    ConversationTurn,
    ConversationTurnId,
    ConversationTurnOrigin,
    ConversationTurnState,
    PersistedConversationMessage,
    PersistedConversationRole,
)
from margpa_runtime_llm.modules.conversation.ports import CommitConversation
from margpa_runtime_llm.modules.web_knowledge import (
    PersistedTurnWebCitationEvidence,
    SourceAuthorityClass,
    WebCitation,
    WebContentTransformation,
    WebSearchActivation,
)

NOW = datetime(2026, 8, 15, tzinfo=UTC)
_SHA = "d" * 128


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
                content="このURLを要約して",
                created_at=NOW,
            ),
            PersistedConversationMessage(
                message_id=ConversationMessageId(value=f"{turn_id}-assistant"),
                conversation_id=ConversationId(value=conversation_id),
                turn_id=ConversationTurnId(value=turn_id),
                sequence=1,
                role=PersistedConversationRole.ASSISTANT,
                content="summarized",
                created_at=NOW,
            ),
        ),
    )


def _web_citation_evidence(
    conversation_id: str = "conversation-1",
    turn_id: str = "turn-1",
) -> PersistedTurnWebCitationEvidence:
    return PersistedTurnWebCitationEvidence(
        conversation_id=conversation_id,
        turn_id=turn_id,
        citation_schema_version=3,
        activation=WebSearchActivation.MANUAL,
        citations=(
            WebCitation(
                citation_id="web-citation-1",
                requested_url="https://example.org/redirected-from",
                canonical_url="https://example.org/article",
                title="Example Article",
                provider_key="direct_url",
                source_authority=SourceAuthorityClass.GENERAL,
                fetched_at="2026-08-30T00:00:00Z",
                content_type="text/html",
                transformation=WebContentTransformation.HTML_TEXT_EXTRACTED,
                content_sha512=_SHA,
                source_class="public_web",
                selected_order=1,
            ),
        ),
    )


def _downgrade_web_citation_record(
    store: SQLiteConversationStore,
    *,
    schema_version: int,
    drop_fields: tuple[str, ...],
) -> None:
    """Rewrites the real Encoded SQLite Record to look exactly like one a
    prior Schema Version would have produced — both the DB column and the
    embedded envelope version are downgraded, and Fields that did not exist
    at that Schema Version are removed, keeping the stored Digest
    self-consistent (never simulating Digest tampering here — that is a
    separate, already-covered Fail-closed case)."""

    with sqlite3.connect(store.database_path) as connection:
        row = connection.execute("SELECT citations_json FROM turn_web_citations").fetchone()
        envelope = json.loads(bytes(row[0]).decode("utf-8"))
        citation_evidence = envelope["citation_evidence"]
        citation_evidence["citation_schema_version"] = schema_version
        for citation in citation_evidence["citations"]:
            for field in drop_fields:
                citation.pop(field, None)
        payload = json.dumps(
            envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest = hashlib.sha512(payload).hexdigest()
        connection.execute(
            "UPDATE turn_web_citations SET citation_schema_version = ?, "
            "citations_json = ?, citations_sha512 = ?",
            (schema_version, payload, digest),
        )


def _commit(store: SQLiteConversationStore) -> None:
    store.commit(
        CommitConversation(
            scope_id=_scope(),
            operation_id=ConversationOperationId(value="op-1"),
            conversation=_completed_snapshot(),
            web_citation_evidence=_web_citation_evidence(),
        )
    )


def test_schema_3_current_record_decodes_unchanged(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _commit(store)
    result = store.get_turn_web_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnWebCitationEvidence)
    assert result.citation_schema_version == 3
    assert result.citations[0].requested_url == "https://example.org/redirected-from"
    assert result.citations[0].transformation is WebContentTransformation.HTML_TEXT_EXTRACTED


def test_schema_2_record_missing_transformation_is_upgraded_on_read(tmp_path: Path) -> None:
    """P8-MR2 bumped Schema 2 -> 3 when `transformation` became required.
    A genuine Schema 2 Record predates that Field entirely — the Reader
    must derive it from the already-recorded `content_type`, never degrade
    to `corrupt_record`."""

    store = _store(tmp_path)
    _commit(store)
    _downgrade_web_citation_record(store, schema_version=2, drop_fields=("transformation",))

    result = store.get_turn_web_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnWebCitationEvidence)
    assert result.citation_schema_version == 2
    assert result.citations[0].transformation is WebContentTransformation.HTML_TEXT_EXTRACTED
    # requested_url already existed at Schema 2 - untouched, still the genuine value.
    assert result.citations[0].requested_url == "https://example.org/redirected-from"


def test_schema_1_record_missing_requested_url_and_transformation_is_upgraded_on_read(
    tmp_path: Path,
) -> None:
    """P8-RW6-A bumped Schema 1 -> 2 when `requested_url` became required.
    A genuine Schema 1 Record predates both `requested_url` and
    `transformation` - the Reader must recover a usable Citation from
    what Schema 1 actually recorded, honestly projecting `requested_url`
    as the same value `canonical_url` already carries (never inventing a
    separately-recorded pre-Redirect URL Schema 1 never had)."""

    store = _store(tmp_path)
    _commit(store)
    _downgrade_web_citation_record(
        store, schema_version=1, drop_fields=("requested_url", "transformation")
    )

    result = store.get_turn_web_citations("conversation-1", "turn-1")
    assert isinstance(result, PersistedTurnWebCitationEvidence)
    assert result.citation_schema_version == 1
    assert result.citations[0].canonical_url == "https://example.org/article"
    assert result.citations[0].requested_url == "https://example.org/article"
    assert result.citations[0].transformation is WebContentTransformation.HTML_TEXT_EXTRACTED
