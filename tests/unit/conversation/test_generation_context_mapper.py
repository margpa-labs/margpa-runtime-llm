"""P2B-MAP-001..002 generation mapping and explicit limit behavior."""

from datetime import UTC, datetime, timedelta

import pytest

from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationError,
    PersistentConversationErrorCode,
    map_generation_context,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationSessionRecord,
    ConversationSessionState,
    ConversationSnapshot,
    ConversationState,
    ConversationTurn,
    ConversationTurnId,
    ConversationTurnState,
    PersistedConversationMessage,
    PersistedConversationRole,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

NOW = datetime(2026, 8, 14, tzinfo=UTC)
CID = ConversationId(value="conversation-1")
SID = ConversationSessionId(value="session-1")


def settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def build_snapshot(completed_count: int) -> tuple[ConversationSnapshot, ConversationTurnId]:
    turns: list[ConversationTurn] = []
    messages: list[PersistedConversationMessage] = []
    parent: ConversationTurnId | None = None
    for sequence in range(completed_count):
        turn_id = ConversationTurnId(value=f"turn-{sequence}")
        user_id = ConversationMessageId(value=f"message-{sequence}-user")
        assistant_id = ConversationMessageId(value=f"message-{sequence}-assistant")
        turns.append(
            ConversationTurn(
                turn_id=turn_id,
                conversation_id=CID,
                session_id=SID,
                sequence=sequence,
                state=ConversationTurnState.COMPLETED,
                parent_turn_id=parent,
                user_message_id=user_id,
                assistant_message_id=assistant_id,
                request_id=f"request-{sequence}",
                started_at=NOW + timedelta(seconds=sequence * 3),
                finished_at=NOW + timedelta(seconds=sequence * 3 + 2),
            )
        )
        messages.extend(
            (
                PersistedConversationMessage(
                    message_id=user_id,
                    conversation_id=CID,
                    turn_id=turn_id,
                    sequence=sequence * 2,
                    role=PersistedConversationRole.USER,
                    content=f"user {sequence}",
                    created_at=NOW + timedelta(seconds=sequence * 3),
                ),
                PersistedConversationMessage(
                    message_id=assistant_id,
                    conversation_id=CID,
                    turn_id=turn_id,
                    sequence=sequence * 2 + 1,
                    role=PersistedConversationRole.ASSISTANT,
                    content=f"assistant {sequence}",
                    created_at=NOW + timedelta(seconds=sequence * 3 + 1),
                ),
            )
        )
        parent = turn_id
    pending_id = ConversationTurnId(value="turn-pending")
    pending_message = ConversationMessageId(value="message-pending-user")
    turns.append(
        ConversationTurn(
            turn_id=pending_id,
            conversation_id=CID,
            session_id=SID,
            sequence=completed_count,
            state=ConversationTurnState.PENDING,
            parent_turn_id=parent,
            user_message_id=pending_message,
            started_at=NOW + timedelta(seconds=completed_count * 3),
        )
    )
    messages.append(
        PersistedConversationMessage(
            message_id=pending_message,
            conversation_id=CID,
            turn_id=pending_id,
            sequence=completed_count * 2,
            role=PersistedConversationRole.USER,
            content="pending user",
            created_at=NOW + timedelta(seconds=completed_count * 3),
        )
    )
    return (
        ConversationSnapshot(
            scope_id=ConversationScopeId(value="scope-private"),
            conversation_id=CID,
            state=ConversationState.ACTIVE,
            head_turn_id=parent,
            created_at=NOW,
            updated_at=NOW + timedelta(hours=1),
            sessions=(
                ConversationSessionRecord(
                    session_id=SID,
                    conversation_id=CID,
                    state=ConversationSessionState.ACTIVE,
                    opened_at=NOW,
                ),
            ),
            turns=tuple(turns),
            messages=tuple(messages),
        ),
        pending_id,
    )


def test_mapper_projects_only_completed_branch_and_pending_user_in_order() -> None:
    snapshot, pending = build_snapshot(2)
    value = map_generation_context(snapshot, pending_turn_id=pending, settings=settings())
    assert [message.role for message in value.messages] == [
        ConversationRole.USER,
        ConversationRole.ASSISTANT,
        ConversationRole.USER,
        ConversationRole.ASSISTANT,
        ConversationRole.USER,
    ]
    assert [message.content for message in value.messages] == [
        "user 0",
        "assistant 0",
        "user 1",
        "assistant 1",
        "pending user",
    ]


def test_mapper_rejects_message_count_overflow_without_truncation() -> None:
    snapshot, pending = build_snapshot(32)
    before = snapshot.model_dump_json()
    with pytest.raises(PersistentConversationError) as captured:
        map_generation_context(snapshot, pending_turn_id=pending, settings=settings())
    assert captured.value.code is PersistentConversationErrorCode.GENERATION_CONTEXT_LIMIT_EXCEEDED
    assert snapshot.model_dump_json() == before
