"""CL-P9-3-E.5/E.6: proves a genuinely Activated Compaction reaches
`map_generation_context()` -- the actual Generation-Mapper connection point
-- and that Original Conversation content is never mutated in the process
(Byte-equivalent Preservation).
"""

import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from margpa_runtime_llm.adapters.context_compaction.local_filesystem_compaction_store import (
    LocalFilesystemCompactionStore,
)
from margpa_runtime_llm.modules.context_compaction.application.auto_policy import (
    AutoCompactionPolicyController,
)
from margpa_runtime_llm.modules.context_compaction.application.budget_service import (
    ContextBudgetService,
    ReserveConfig,
)
from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.application.deterministic_builder import (
    DeterministicExtractiveBuilder,
)
from margpa_runtime_llm.modules.context_compaction.application.generation_projection_adapter import (  # noqa: E501
    CompactionActiveContextProjectionAdapter,
)
from margpa_runtime_llm.modules.context_compaction.application.worker import CompactionWorker
from margpa_runtime_llm.modules.context_compaction.domain import (
    DEFAULT_BRANCH_ID,
    CompactionAttemptState,
    ThresholdConfig,
)
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    SourceConversationTurn,
)
from margpa_runtime_llm.modules.conversation.application.generation_context_mapper import (
    map_generation_context,
)
from margpa_runtime_llm.modules.conversation.contracts import ConversationSettings
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
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility

_NOW = datetime.now(UTC)


class FakeSource:
    def __init__(self, turn_count: int, revision: int = 5) -> None:
        self.turn_count = turn_count
        self.revision = revision

    def read(self, conversation_id: ConversationId) -> ConversationSourceProjection | None:
        turns = tuple(
            SourceConversationTurn(
                turn_id=ConversationTurnId(value=f"turn-{i}"),
                sequence=i,
                user_message_id=ConversationMessageId(value=f"user-{i}"),
                user_content=f"Historical user message {i}: please remember detail X{i}.",
                assistant_message_id=ConversationMessageId(value=f"assistant-{i}"),
                assistant_content=f"Historical assistant reply {i}: acknowledged X{i}.",
            )
            for i in range(self.turn_count)
        )
        return ConversationSourceProjection(
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            source_conversation_revision=self.revision,
            turns=turns,
        )


class FakeModelContext:
    def loaded_context_capacity(self) -> int | None:
        return 4096

    def loaded_model_identity(self) -> str | None:
        return "fake-model"

    def count_text_tokens(self, text: str) -> int | None:
        return max(1, len(text) // 4)


def _build_snapshot_for_generation(
    conversation_id: ConversationId, *, turn_count: int, pending_content: str
) -> tuple[ConversationSnapshot, ConversationTurnId]:
    """Mirrors exactly the alternating (user, assistant) turns `FakeSource`
    above serves -- the same 20-Turn history, but as a real
    `ConversationSnapshot` `map_generation_context()` actually consumes."""

    session_id = ConversationSessionId(value="session-1")
    session = ConversationSessionRecord(
        session_id=session_id,
        conversation_id=conversation_id,
        state=ConversationSessionState.ACTIVE,
        opened_at=_NOW,
    )
    turns = []
    messages = []
    parent_turn_id: ConversationTurnId | None = None
    for i in range(turn_count):
        turn_id = ConversationTurnId(value=f"turn-{i}")
        user_message_id = ConversationMessageId(value=f"user-{i}")
        assistant_message_id = ConversationMessageId(value=f"assistant-{i}")
        messages.append(
            PersistedConversationMessage(
                message_id=user_message_id,
                conversation_id=conversation_id,
                turn_id=turn_id,
                sequence=i * 2,
                role=PersistedConversationRole.USER,
                content=f"Historical user message {i}: please remember detail X{i}.",
                created_at=_NOW,
            )
        )
        messages.append(
            PersistedConversationMessage(
                message_id=assistant_message_id,
                conversation_id=conversation_id,
                turn_id=turn_id,
                sequence=i * 2 + 1,
                role=PersistedConversationRole.ASSISTANT,
                content=f"Historical assistant reply {i}: acknowledged X{i}.",
                created_at=_NOW,
            )
        )
        turns.append(
            ConversationTurn(
                turn_id=turn_id,
                conversation_id=conversation_id,
                session_id=session_id,
                sequence=i,
                state=ConversationTurnState.COMPLETED,
                parent_turn_id=parent_turn_id,
                user_message_id=user_message_id,
                assistant_message_id=assistant_message_id,
                started_at=_NOW,
                finished_at=_NOW,
            )
        )
        parent_turn_id = turn_id

    pending_turn_id = ConversationTurnId(value="turn-pending")
    pending_user_message_id = ConversationMessageId(value="user-pending")
    messages.append(
        PersistedConversationMessage(
            message_id=pending_user_message_id,
            conversation_id=conversation_id,
            turn_id=pending_turn_id,
            sequence=turn_count * 2,
            role=PersistedConversationRole.USER,
            content=pending_content,
            created_at=_NOW,
        )
    )
    turns.append(
        ConversationTurn(
            turn_id=pending_turn_id,
            conversation_id=conversation_id,
            session_id=session_id,
            sequence=turn_count,
            state=ConversationTurnState.PENDING,
            parent_turn_id=parent_turn_id,
            user_message_id=pending_user_message_id,
            started_at=_NOW,
        )
    )

    snapshot = ConversationSnapshot(
        scope_id=ConversationScopeId(value="scope-1"),
        conversation_id=conversation_id,
        state=ConversationState.ACTIVE,
        head_turn_id=ConversationTurnId(value=f"turn-{turn_count - 1}"),
        created_at=_NOW,
        updated_at=_NOW,
        sessions=(session,),
        turns=tuple(turns),
        messages=tuple(messages),
    )
    return snapshot, pending_turn_id


def _wait_completed(coordinator: CompactionCoordinator, attempt_id: str) -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        attempt = coordinator.get_attempt(attempt_id)
        if attempt is not None and attempt.state is CompactionAttemptState.COMPLETED:
            return
        time.sleep(0.01)
    raise AssertionError("compaction attempt did not complete in time")


def test_a_completed_compaction_genuinely_changes_what_map_generation_context_sends() -> None:
    turn_count = 20
    cid = ConversationId(value="conv-gen-1")
    source = FakeSource(turn_count=turn_count, revision=turn_count)
    model_context = FakeModelContext()

    with tempfile.TemporaryDirectory() as tmp:
        store = LocalFilesystemCompactionStore(base_dir=Path(tmp))
        budget_service = ContextBudgetService(
            source=source, model_context=model_context, reserves=ReserveConfig()
        )
        builder = DeterministicExtractiveBuilder(model_context=model_context)
        coordinator = CompactionCoordinator(
            store=store,
            budget_service=budget_service,
            builder=builder,
            auto_policy=AutoCompactionPolicyController(enabled=True),
            worker=CompactionWorker(),
            thresholds=ThresholdConfig(
                advisory_remaining_budget_floor=100_000,
                auto_trigger_remaining_budget_floor=100_000,
            ),
            token_budget=250,
        )

        attempt = coordinator.request_manual_compaction(cid, generation_reserve_tokens=100)
        _wait_completed(coordinator, attempt.attempt_id.value)

        snapshot, pending_turn_id = _build_snapshot_for_generation(
            cid, turn_count=turn_count, pending_content="What did I ask you to remember?"
        )
        settings = ConversationSettings(
            response_language=ResponseLanguage.EN,
            max_new_tokens=256,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        )

        original_input = map_generation_context(
            snapshot, pending_turn_id=pending_turn_id, settings=settings
        )

        adapter = CompactionActiveContextProjectionAdapter(coordinator=coordinator)
        compacted_input = map_generation_context(
            snapshot,
            pending_turn_id=pending_turn_id,
            settings=settings,
            context_projection_port=adapter,
            source_conversation_revision=turn_count,
        )

        # The compacted path must send strictly fewer messages, and a
        # middle-of-history Turn (neither the very first -- kept as the
        # Builder's own honest "objective" proxy -- nor recent enough for
        # the Verbatim Tail) must no longer appear verbatim -- proof the
        # Compacted Projection genuinely substituted, not merely that
        # `resolve_messages` was called.
        assert len(compacted_input.messages) < len(original_input.messages)
        assert any("detail X5" in message.content for message in original_input.messages)
        assert not any("detail X5" in message.content for message in compacted_input.messages)
        # The pending Turn's own content must survive unmodified either way.
        assert compacted_input.messages[-1].content == "What did I ask you to remember?"
        assert original_input.messages[-1].content == compacted_input.messages[-1].content

        # Original Conversation Byte-equivalent Preservation: re-running the
        # SAME mapping without the Port produces the identical original
        # result -- Compaction never mutated `snapshot` itself.
        rerun_original = map_generation_context(
            snapshot, pending_turn_id=pending_turn_id, settings=settings
        )
        assert rerun_original == original_input


def test_a_failing_projection_port_falls_back_to_the_original_never_breaks_generation() -> None:
    class _RaisingPort:
        def resolve_messages(self, **_kwargs: object) -> tuple:  # type: ignore[type-arg]
            raise RuntimeError("simulated Compaction-side failure")

    cid = ConversationId(value="conv-gen-2")
    snapshot, pending_turn_id = _build_snapshot_for_generation(
        cid, turn_count=3, pending_content="hello"
    )
    settings = ConversationSettings(
        response_language=ResponseLanguage.EN,
        max_new_tokens=256,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
    )
    original = map_generation_context(snapshot, pending_turn_id=pending_turn_id, settings=settings)
    with_broken_port = map_generation_context(
        snapshot,
        pending_turn_id=pending_turn_id,
        settings=settings,
        context_projection_port=_RaisingPort(),
        source_conversation_revision=3,
    )
    assert with_broken_port == original
