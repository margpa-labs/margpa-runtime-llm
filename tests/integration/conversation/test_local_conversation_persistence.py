"""P2B integration: opt-in binding, durable lifecycle, and zero-write defaults."""

from collections.abc import Iterator
from pathlib import Path

from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
    SQLiteConversationStore,
    build_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.application import (
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
    ConversationTurnState,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")


class FakeSession:
    request_id = "request-integration"

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "assistant_message": {"role": "assistant", "content": "durable final"},
            },
        )


class FakeGeneration:
    def start(self, _: object) -> FakeSession:
        return FakeSession()


def op(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def test_factory_is_write_free_and_disabled_by_default(tmp_path: Path) -> None:
    project_runtime = Path.cwd() / "runtime_data"
    project_state_before = project_runtime.exists()
    disabled = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert (
        not disabled.enabled
        and disabled.store is None
        and disabled.maintenance is None
        and disabled.service is None
    )

    root = tmp_path / "explicit-runtime"
    enabled = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert (
        enabled.enabled
        and enabled.store is not None
        and enabled.maintenance is not None
        and enabled.service is not None
    )
    assert not root.exists()
    assert project_runtime.exists() is project_state_before


def test_durable_generation_survives_new_adapter_instance(tmp_path: Path) -> None:
    root = tmp_path / "explicit-runtime"
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None and built.service is not None
    built.store.initialize_new_store()
    service = built.service
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user canonical",
            settings=ConversationSettings(
                response_language=ResponseLanguage.JA,
                max_new_tokens=128,
                thinking_mode=ThinkingMode.DISABLED,
                thinking_visibility=ThinkingVisibility.HIDDEN,
                summary_mode=SummaryMode.OFF,
                documentation_rag_mode=DocumentationRagMode.DISABLED,
            ),
            identities=PersistentGenerationIdentities(
                turn_id=ConversationTurnId(value="turn-1"),
                user_message_id=ConversationMessageId(value="message-user-1"),
                assistant_message_id=ConversationMessageId(value="message-assistant-1"),
                append_operation_id=op("append"),
                start_operation_id=op("start"),
                terminal_operation_id=op("complete"),
            ),
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED
    reopened = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=SCOPE)
    stored = reopened.open_ready_store().get(SCOPE, CID)
    assert stored is not None
    assert stored.storage_revision == 4
    assert stored.conversation.turns[0].state is ConversationTurnState.COMPLETED
    assert [message.content for message in stored.conversation.messages] == [
        "user canonical",
        "durable final",
    ]


def test_restart_recovers_max_length_conversation_identity(tmp_path: Path) -> None:
    root = tmp_path / "explicit-runtime"
    long_conversation_id = ConversationId(value="c" * 128)
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None and built.service is not None
    built.store.initialize_new_store()
    built.service.recover_incomplete_conversations()
    built.service.create_conversation(
        conversation_id=long_conversation_id,
        session_id=ConversationSessionId(value="session-before-restart"),
        operation_id=op("create-before-restart"),
    )

    reopened = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert reopened.store is not None and reopened.service is not None
    reopened.store.open_ready_store()
    result = reopened.service.recover_incomplete_conversations()

    assert result.recovered_conversations == 1
    stored = reopened.store.get(SCOPE, long_conversation_id)
    assert stored is not None
    assert stored.conversation.sessions[0].state.value == "interrupted"
