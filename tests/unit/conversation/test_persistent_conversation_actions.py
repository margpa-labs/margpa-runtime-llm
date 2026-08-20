"""Phase 2-C derived actions, branch selection, and cancel-boundary tests."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationError,
    PersistentConversationErrorCode,
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationSessionState,
    ConversationState,
    ConversationStorageError,
    ConversationTurnId,
    ConversationTurnOrigin,
    ConversationTurnState,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 14, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class Session:
    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.documentation_augmentation = None

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": "generating"},
        )
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "finish_reason": "stop",
                "assistant_message": {"role": "assistant", "content": self.answer},
            },
        )


class Generation:
    def __init__(self) -> None:
        self.inputs: list[ConversationGenerationInput] = []
        self.active_request_id: str | None = None
        self.cancelled: list[str] = []

    def start(self, value: ConversationGenerationInput) -> Session:
        self.inputs.append(value)
        self.active_request_id = f"request-{len(self.inputs)}"
        return Session(self.active_request_id, f"answer-{len(self.inputs)}")

    def cancel(self, request_id: str) -> bool:
        if self.active_request_id != request_id:
            return False
        self.cancelled.append(request_id)
        return True


def settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def ids(label: str) -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value=f"turn-{label}"),
        user_message_id=ConversationMessageId(value=f"message-user-{label}"),
        assistant_message_id=ConversationMessageId(value=f"message-assistant-{label}"),
        append_operation_id=ConversationOperationId(value=f"append-{label}"),
        start_operation_id=ConversationOperationId(value=f"start-{label}"),
        terminal_operation_id=ConversationOperationId(value=f"terminal-{label}"),
    )


def built(
    tmp_path: Path,
) -> tuple[PersistentConversationService, SQLiteConversationStore, Generation]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = Generation()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
        clock=Clock(),
    )
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=ConversationOperationId(value="create"),
    )
    return service, store, generation


def test_regenerate_preserves_source_and_maps_only_source_parent_plus_user(
    tmp_path: Path,
) -> None:
    service, _, generation = built(tmp_path)
    first = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="canonical user",
            settings=settings(),
            identities=ids("normal"),
            expected_revision=1,
        )
    )
    assert first[-1].event is ConversationEventType.COMPLETED
    before = service.get_conversation(CID)
    regenerated = tuple(
        service.generate_derived_turn(
            conversation_id=CID,
            source_turn_id=ConversationTurnId(value="turn-normal"),
            origin=ConversationTurnOrigin.REGENERATE,
            expected_revision=before.storage_revision,
            settings=settings(),
            identities=ids("regenerate"),
        )
    )
    assert regenerated[-1].event is ConversationEventType.COMPLETED
    stored = service.get_conversation(CID)
    assert [turn.state for turn in stored.conversation.turns] == [
        ConversationTurnState.COMPLETED,
        ConversationTurnState.COMPLETED,
    ]
    assert stored.conversation.turns[1].derived_from_turn_id == ConversationTurnId(
        value="turn-normal"
    )
    assert stored.conversation.head_turn_id == ConversationTurnId(value="turn-regenerate")
    assert [message.content for message in generation.inputs[1].messages] == ["canonical user"]


def test_retry_rejects_completed_and_accepts_failed_without_replacement_content(
    tmp_path: Path,
) -> None:
    service, _, generation = built(tmp_path)
    pending = service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-failed"),
        user_message_id=ConversationMessageId(value="message-user-failed"),
        content="server canonical retry",
        operation_id=ConversationOperationId(value="append-failed"),
        expected_revision=1,
    )
    failed = service.fail_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-failed"),
        operation_id=ConversationOperationId(value="fail-source"),
        expected_revision=pending.storage_revision,
    )
    events = tuple(
        service.generate_derived_turn(
            conversation_id=CID,
            source_turn_id=ConversationTurnId(value="turn-failed"),
            origin=ConversationTurnOrigin.RETRY,
            expected_revision=failed.storage_revision,
            settings=settings(),
            identities=ids("retry"),
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED
    assert [message.content for message in generation.inputs[-1].messages] == [
        "server canonical retry"
    ]
    current = service.get_conversation(CID)
    with pytest.raises(PersistentConversationError):
        service.append_derived_turn(
            conversation_id=CID,
            source_turn_id=ConversationTurnId(value="turn-retry"),
            origin=ConversationTurnOrigin.RETRY,
            turn_id=ConversationTurnId(value="turn-invalid"),
            user_message_id=ConversationMessageId(value="message-user-invalid"),
            operation_id=ConversationOperationId(value="append-invalid"),
            expected_revision=current.storage_revision,
        )


def test_branch_selection_is_cas_only_and_stale_revision_writes_nothing(tmp_path: Path) -> None:
    service, _, generation = built(tmp_path)
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="first",
            settings=settings(),
            identities=ids("first"),
            expected_revision=1,
        )
    )
    after_first = service.get_conversation(CID)
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="second",
            settings=settings(),
            identities=ids("second"),
            expected_revision=after_first.storage_revision,
        )
    )
    before_select = service.get_conversation(CID)
    counts = (len(before_select.conversation.turns), len(before_select.conversation.messages))
    selected = service.select_branch_head(
        conversation_id=CID,
        completed_turn_id=ConversationTurnId(value="turn-first"),
        operation_id=ConversationOperationId(value="select-first"),
        expected_revision=before_select.storage_revision,
    )
    assert selected.conversation.head_turn_id == ConversationTurnId(value="turn-first")
    assert (len(selected.conversation.turns), len(selected.conversation.messages)) == counts
    with pytest.raises(ConversationStorageError):
        service.select_branch_head(
            conversation_id=CID,
            completed_turn_id=ConversationTurnId(value="turn-second"),
            operation_id=ConversationOperationId(value="select-stale"),
            expected_revision=before_select.storage_revision,
        )
    assert service.get_conversation(CID).storage_revision == selected.storage_revision
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="after selected branch",
            settings=settings(),
            identities=ids("after-select"),
            expected_revision=selected.storage_revision,
        )
    )
    assert [message.content for message in generation.inputs[-1].messages] == [
        "first",
        "answer-1",
        "after selected branch",
    ]


def test_rename_conversation_updates_title_and_clears_to_auto(tmp_path: Path) -> None:
    service, _, _ = built(tmp_path)
    renamed = service.rename_conversation(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="rename-1"),
        expected_revision=1,
        title="My renamed chat",
    )
    assert renamed.conversation.title == "My renamed chat"
    cleared = service.rename_conversation(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="rename-2"),
        expected_revision=renamed.storage_revision,
        title=None,
    )
    assert cleared.conversation.title is None


def test_rename_conversation_rejects_deleted_conversation(tmp_path: Path) -> None:
    service, _, _ = built(tmp_path)
    deleted = service.set_deleted(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="delete-1"),
        expected_revision=1,
    )
    assert deleted.conversation.state is ConversationState.DELETED
    with pytest.raises(PersistentConversationError) as captured:
        service.rename_conversation(
            conversation_id=CID,
            operation_id=ConversationOperationId(value="rename-after-delete"),
            expected_revision=deleted.storage_revision,
            title="too late",
        )
    assert captured.value.code is PersistentConversationErrorCode.INVALID_LIFECYCLE


def test_set_deleted_closes_active_session_from_active_state(tmp_path: Path) -> None:
    service, _, _ = built(tmp_path)
    deleted = service.set_deleted(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="delete-1"),
        expected_revision=1,
    )
    assert deleted.conversation.state is ConversationState.DELETED
    assert all(
        item.state is not ConversationSessionState.ACTIVE for item in deleted.conversation.sessions
    )


def test_set_deleted_from_archived_state(tmp_path: Path) -> None:
    service, _, _ = built(tmp_path)
    archived = service.set_archived(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="archive-1"),
        expected_revision=1,
        archived=True,
    )
    deleted = service.set_deleted(
        conversation_id=CID,
        operation_id=ConversationOperationId(value="delete-1"),
        expected_revision=archived.storage_revision,
    )
    assert deleted.conversation.state is ConversationState.DELETED


def test_set_deleted_rejects_non_terminal_turn(tmp_path: Path) -> None:
    service, _, _ = built(tmp_path)
    pending = service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-pending"),
        user_message_id=ConversationMessageId(value="message-user-pending"),
        content="still going",
        operation_id=ConversationOperationId(value="append-pending"),
        expected_revision=1,
    )
    with pytest.raises(PersistentConversationError) as captured:
        service.set_deleted(
            conversation_id=CID,
            operation_id=ConversationOperationId(value="delete-blocked"),
            expected_revision=pending.storage_revision,
        )
    assert captured.value.code is PersistentConversationErrorCode.INVALID_LIFECYCLE


def test_cancel_requires_exact_generating_revision_and_request(tmp_path: Path) -> None:
    service, _, generation = built(tmp_path)
    pending = service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-active"),
        user_message_id=ConversationMessageId(value="message-user-active"),
        content="active",
        operation_id=ConversationOperationId(value="append-active"),
        expected_revision=1,
    )
    generating = service.start_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-active"),
        request_id="request-active",
        operation_id=ConversationOperationId(value="start-active"),
        expected_revision=pending.storage_revision,
    )
    generation.active_request_id = "request-active"
    with pytest.raises(PersistentConversationError):
        service.cancel_active_generation(
            conversation_id=CID,
            request_id="request-other",
            expected_revision=generating.storage_revision,
        )
    with pytest.raises(ConversationStorageError):
        service.cancel_active_generation(
            conversation_id=CID,
            request_id="request-active",
            expected_revision=generating.storage_revision - 1,
        )
    assert service.cancel_active_generation(
        conversation_id=CID,
        request_id="request-active",
        expected_revision=generating.storage_revision,
    )
    assert generation.cancelled == ["request-active"]
