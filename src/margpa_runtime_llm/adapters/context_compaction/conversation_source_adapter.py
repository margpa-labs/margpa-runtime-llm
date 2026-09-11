"""`ConversationSourceProjectionPort` over the existing Conversation Store.

Walks the SAME `head_turn_id` -> `parent_turn_id` completed-branch chain
`project_generation_history()` walks, but keeps per-Turn Source Identity
(`turn_id`/`message_id`) intact rather than flattening to a plain message
list -- Compaction needs that Identity for every `ContextSourceTurnReference`
it produces (Invariant: Sourceに存在しないFactを追加しない)."""

from __future__ import annotations

from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
    ContextCompactionDomainErrorCode,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import DEFAULT_BRANCH_ID
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    SourceConversationTurn,
)
from margpa_runtime_llm.modules.conversation.domain.identity import (
    ConversationId,
    ConversationScopeId,
)
from margpa_runtime_llm.modules.conversation.domain.models import (
    ConversationSnapshot,
    ConversationTurnState,
    PersistedConversationRole,
)
from margpa_runtime_llm.modules.conversation.ports.conversation_store import (
    ConversationRepositoryPort,
)


def _walk_completed_branch(snapshot: ConversationSnapshot) -> tuple[SourceConversationTurn, ...]:
    turns_by_id = {turn.turn_id.value: turn for turn in snapshot.turns}
    messages_by_id = {message.message_id.value: message for message in snapshot.messages}
    chain = []
    cursor = snapshot.head_turn_id
    visited: set[str] = set()
    while cursor is not None:
        if cursor.value in visited:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The conversation branch is invalid.",
            )
        visited.add(cursor.value)
        turn = turns_by_id.get(cursor.value)
        if turn is None or turn.state is not ConversationTurnState.COMPLETED:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The conversation branch is invalid.",
            )
        chain.append(turn)
        cursor = turn.parent_turn_id
    output: list[SourceConversationTurn] = []
    for turn in reversed(chain):
        user_message = messages_by_id[turn.user_message_id.value]
        assert user_message.role is PersistedConversationRole.USER
        assistant_message = None
        assistant_content = None
        if turn.assistant_message_id is not None:
            assistant_message = messages_by_id[turn.assistant_message_id.value]
            assistant_content = assistant_message.content
        output.append(
            SourceConversationTurn(
                turn_id=turn.turn_id,
                sequence=turn.sequence,
                user_message_id=turn.user_message_id,
                user_content=user_message.content,
                assistant_message_id=turn.assistant_message_id,
                assistant_content=assistant_content,
            )
        )
    return tuple(output)


class ConversationRepositoryContextSourceAdapter:
    def __init__(
        self, *, repository: ConversationRepositoryPort, scope_id: ConversationScopeId
    ) -> None:
        self._repository = repository
        self._scope_id = scope_id

    def read(self, conversation_id: ConversationId) -> ConversationSourceProjection | None:
        stored = self._repository.get(self._scope_id, conversation_id)
        if stored is None or stored.conversation.head_turn_id is None:
            return None
        turns = _walk_completed_branch(stored.conversation)
        return ConversationSourceProjection(
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            source_conversation_revision=stored.storage_revision,
            turns=turns,
        )
