"""P2B-LIF-001..004, P2B-CAS-005, and P2B-REC-001..002."""

import sqlite3
from collections.abc import Generator, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest

from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationError,
    PersistentConversationErrorCode,
    PersistentConversationService,
    PersistentGenerationIdentities,
    PersistentServiceReadiness,
)
from margpa_runtime_llm.modules.conversation.application import (
    persistent_conversation_service as persistent_module,
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
    ConversationSessionState,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationTurnId,
    ConversationTurnState,
    StorageMutationOutcome,
)
from margpa_runtime_llm.modules.conversation.ports import (
    CommitConversation,
    ConversationCommitReceipt,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

NOW = datetime(2026, 8, 14, tzinfo=UTC)
SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")


class Clock:
    def __init__(self) -> None:
        self.value = NOW

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class FakeSession:
    def __init__(self, events: tuple[ConversationEvent, ...]) -> None:
        self.request_id = "request-1"
        self._events = events
        self.documentation_augmentation = None

    def events(self) -> Iterator[ConversationEvent]:
        yield from self._events


class FakeGenerationService:
    def __init__(self, events: tuple[ConversationEvent, ...]) -> None:
        self.events = events
        self.calls = 0

    def start(self, _: object) -> FakeSession:
        self.calls += 1
        return FakeSession(self.events)


def op(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def identities() -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        assistant_message_id=ConversationMessageId(value="message-assistant-1"),
        append_operation_id=op("append-1"),
        start_operation_id=op("start-1"),
        terminal_operation_id=op("terminal-1"),
    )


def settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def completed_event() -> ConversationEvent:
    return ConversationEvent(
        event=ConversationEventType.COMPLETED,
        data={
            "request_id": "request-1",
            "assistant_message": {"role": "assistant", "content": "canonical final"},
        },
    )


def make_service(
    tmp_path: Path,
    events: tuple[ConversationEvent, ...] = (),
) -> tuple[PersistentConversationService, SQLiteConversationStore, FakeGenerationService]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = FakeGenerationService(events)
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
        clock=Clock(),
        recovery_operation_factory=lambda value: op(f"recovery:{value}"),
    )
    return service, store, generation


def test_lifecycle_create_pending_generating_complete_close_resume(tmp_path: Path) -> None:
    service, _, _ = make_service(tmp_path)
    created = service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    pending = service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        content="hello",
        operation_id=op("append"),
        expected_revision=created.storage_revision,
    )
    generating = service.start_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        request_id="request-1",
        operation_id=op("start"),
        expected_revision=pending.storage_revision,
    )
    completed = service.complete_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        assistant_message_id=ConversationMessageId(value="message-assistant-1"),
        content="answer",
        operation_id=op("complete"),
        expected_revision=generating.storage_revision,
    )
    assert completed.storage_revision == 4
    assert completed.conversation.turns[0].state is ConversationTurnState.COMPLETED
    assert completed.conversation.messages[-1].content == "answer"
    assert completed.conversation.head_turn_id == ConversationTurnId(value="turn-1")

    listed_while_active = service.list_conversations()
    assert listed_while_active.items[0].has_active_session is True

    with pytest.raises(PersistentConversationError):
        service.fail_generation(
            conversation_id=CID,
            turn_id=ConversationTurnId(value="turn-1"),
            operation_id=op("reopen"),
            expected_revision=completed.storage_revision,
        )
    closed = service.close_session(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("close"),
        expected_revision=completed.storage_revision,
    )
    listed_while_closed = service.list_conversations()
    assert listed_while_closed.items[0].has_active_session is False

    resumed = service.resume_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-2"),
        operation_id=op("resume"),
        expected_revision=closed.storage_revision,
    )
    assert resumed.conversation.sessions[0].state is ConversationSessionState.CLOSED
    assert resumed.conversation.sessions[1].state is ConversationSessionState.ACTIVE
    listed_after_resume = service.list_conversations()
    assert listed_after_resume.items[0].has_active_session is True


def test_cancel_complete_competition_allows_only_one_terminal_commit(tmp_path: Path) -> None:
    service, _, _ = make_service(tmp_path)
    created = service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    pending = service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        content="hello",
        operation_id=op("append"),
        expected_revision=created.storage_revision,
    )
    generating = service.start_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        request_id="request-1",
        operation_id=op("start"),
        expected_revision=pending.storage_revision,
    )
    cancelled = service.cancel_generation(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        operation_id=op("cancel"),
        expected_revision=generating.storage_revision,
    )
    with pytest.raises(ConversationStorageError) as captured:
        service.complete_generation(
            conversation_id=CID,
            turn_id=ConversationTurnId(value="turn-1"),
            assistant_message_id=ConversationMessageId(value="message-assistant-1"),
            content="must not persist",
            operation_id=op("complete"),
            expected_revision=generating.storage_revision,
        )
    assert captured.value.code is ConversationStorageErrorCode.CONFLICT
    assert len(cancelled.conversation.messages) == 1


def test_terminal_event_is_exposed_only_after_canonical_commit(tmp_path: Path) -> None:
    status = ConversationEvent(
        event=ConversationEventType.STATUS,
        data={"request_id": "request-1", "state": "generating"},
    )
    service, store, generation = make_service(tmp_path, (status, completed_event()))
    assert service.recover_incomplete_conversations().inspected_conversations == 0
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="hello",
        settings=settings(),
        identities=identities(),
    )
    assert next(stream).event is ConversationEventType.STATUS
    before_terminal = store.get(SCOPE, CID)
    assert before_terminal.conversation.turns[0].state is ConversationTurnState.GENERATING  # type: ignore[union-attr]
    assert next(stream).event is ConversationEventType.COMPLETED
    after_terminal = store.get(SCOPE, CID)
    assert after_terminal.conversation.turns[0].state is ConversationTurnState.COMPLETED  # type: ignore[union-attr]
    assert after_terminal.conversation.messages[-1].content == "canonical final"  # type: ignore[union-attr]
    assert generation.calls == 1


def test_consumer_disconnect_commits_interrupted_without_partial_text(tmp_path: Path) -> None:
    status = ConversationEvent(
        event=ConversationEventType.STATUS,
        data={"request_id": "request-1", "state": "generating"},
    )
    partial = ConversationEvent(
        event=ConversationEventType.DELTA,
        data={"request_id": "request-1", "channel": "final", "text": "partial-secret"},
    )
    service, store, _ = make_service(tmp_path, (status, partial, completed_event()))
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="hello",
        settings=settings(),
        identities=identities(),
    )
    assert next(stream).event is ConversationEventType.STATUS
    assert next(stream).event is ConversationEventType.DELTA
    cast(Generator[ConversationEvent, None, None], stream).close()
    stored = store.get(SCOPE, CID)
    assert stored.conversation.turns[0].state is ConversationTurnState.INTERRUPTED  # type: ignore[union-attr]
    assert len(stored.conversation.messages) == 1  # type: ignore[union-attr]
    assert "partial-secret" not in store.database_path.read_bytes().decode("utf-8", errors="ignore")


def test_startup_recovery_interrupts_nonterminal_state_before_ready(tmp_path: Path) -> None:
    service, store, _ = make_service(tmp_path)
    created = service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        content="hello",
        operation_id=op("append"),
        expected_revision=created.storage_revision,
    )
    result = service.recover_incomplete_conversations()
    assert result.recovered_conversations == 1
    assert service.readiness is PersistentServiceReadiness.READY
    stored = store.get(SCOPE, CID)
    assert stored.conversation.turns[0].state is ConversationTurnState.INTERRUPTED  # type: ignore[union-attr]
    assert stored.conversation.sessions[0].state is ConversationSessionState.INTERRUPTED  # type: ignore[union-attr]
    assert len(stored.conversation.messages) == 1  # type: ignore[union-attr]


def test_generate_requires_completed_recovery_gate(tmp_path: Path) -> None:
    service, _, _ = make_service(tmp_path, (completed_event(),))
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    with pytest.raises(PersistentConversationError) as captured:
        next(
            service.generate_turn(
                conversation_id=CID,
                content="hello",
                settings=settings(),
                identities=identities(),
            )
        )
    assert captured.value.code is PersistentConversationErrorCode.STORAGE_NOT_READY


class FailingTerminalStore(SQLiteConversationStore):
    def commit(self, command: CommitConversation):  # type: ignore[no-untyped-def]
        if command.operation_id.value == "terminal-1":
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.STORAGE_UNAVAILABLE,
                safe_message="The conversation store is unavailable.",
            )
        return super().commit(command)


def test_terminal_persistence_failure_never_exposes_terminal_event(tmp_path: Path) -> None:
    store = FailingTerminalStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = FakeGenerationService(
        (
            ConversationEvent(
                event=ConversationEventType.STATUS,
                data={"request_id": "request-1", "state": "generating"},
            ),
            completed_event(),
        )
    )
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
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="hello",
        settings=settings(),
        identities=identities(),
    )
    assert next(stream).event is ConversationEventType.STATUS
    with pytest.raises(PersistentConversationError) as captured:
        next(stream)
    assert captured.value.code is PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.GENERATING
    assert len(stored.conversation.messages) == 1


class RecoveryFaultStore(SQLiteConversationStore):
    def __init__(self, *args: object, fault: str, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.fault = fault
        self.recovery_attempts = 0

    def commit(self, command: CommitConversation):  # type: ignore[no-untyped-def]
        if command.operation_id.value.startswith("recovery:") and self.recovery_attempts == 0:
            self.recovery_attempts += 1
            if self.fault == "conflict":
                raise ConversationStorageError(
                    code=ConversationStorageErrorCode.CONFLICT,
                    safe_message="The conversation changed before recovery.",
                    retryable=True,
                )
            super().commit(command)
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.ATOMIC_COMMIT_FAILED,
                safe_message="The conversation commit outcome is unknown.",
                mutation_outcome=StorageMutationOutcome.UNKNOWN,
            )
        return super().commit(command)


@pytest.mark.parametrize("fault", ["conflict", "unknown"])
def test_recovery_handles_bounded_conflict_and_receipted_unknown(
    tmp_path: Path,
    fault: str,
) -> None:
    store = RecoveryFaultStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
        fault=fault,
    )
    store.initialize_new_store()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=FakeGenerationService(()),  # type: ignore[arg-type]
        clock=Clock(),
        recovery_operation_factory=lambda value: op(f"recovery:{value}"),
    )
    created = service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        content="hello",
        operation_id=op("append"),
        expected_revision=created.storage_revision,
    )
    result = service.recover_incomplete_conversations(max_conflict_retries=1)
    assert result.recovered_conversations == 1
    assert service.readiness is PersistentServiceReadiness.READY
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.INTERRUPTED


class LockProbeSession(FakeSession):
    def __init__(self, database_path: Path) -> None:
        super().__init__((completed_event(),))
        self.database_path = database_path
        self.lock_acquired = False

    def events(self) -> Iterator[ConversationEvent]:
        connection = sqlite3.connect(self.database_path, isolation_level=None, timeout=0.05)
        try:
            connection.execute("BEGIN IMMEDIATE")
            self.lock_acquired = True
            connection.rollback()
        finally:
            connection.close()
        yield from super().events()


class LockProbeGeneration:
    def __init__(self, session: LockProbeSession) -> None:
        self.session = session

    def start(self, _: object) -> LockProbeSession:
        return self.session


def test_generation_holds_no_storage_connection_transaction_or_lock(tmp_path: Path) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    probe = LockProbeSession(store.database_path)
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=LockProbeGeneration(probe),  # type: ignore[arg-type]
        clock=Clock(),
    )
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    assert (
        tuple(
            service.generate_turn(
                conversation_id=CID,
                content="hello",
                settings=settings(),
                identities=identities(),
            )
        )[-1].event
        is ConversationEventType.COMPLETED
    )
    assert probe.lock_acquired


def test_context_mapping_failure_converges_pending_turn_without_generation_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, store, generation = make_service(tmp_path)
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )

    def reject_context(*_: object, **__: object) -> object:
        raise PersistentConversationError(
            code=PersistentConversationErrorCode.GENERATION_CONTEXT_LIMIT_EXCEEDED,
            safe_message="The conversation context exceeds the generation limit.",
        )

    monkeypatch.setattr(persistent_module, "map_generation_context", reject_context)
    with pytest.raises(PersistentConversationError) as captured:
        next(
            service.generate_turn(
                conversation_id=CID,
                content="hello",
                settings=settings(),
                identities=identities(),
            )
        )
    assert captured.value.code is PersistentConversationErrorCode.GENERATION_CONTEXT_LIMIT_EXCEEDED
    assert generation.calls == 0
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.FAILED
    assert len(stored.conversation.messages) == 1
    assert service.readiness is PersistentServiceReadiness.READY


class StartFailureGeneration:
    calls = 0

    def start(self, _: object) -> object:
        self.calls += 1
        raise RuntimeError("generation start fixture failure")


def test_generation_start_failure_converges_pending_turn(tmp_path: Path) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = StartFailureGeneration()
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
        operation_id=op("create"),
    )
    with pytest.raises(RuntimeError, match="generation start fixture failure"):
        next(
            service.generate_turn(
                conversation_id=CID,
                content="hello",
                settings=settings(),
                identities=identities(),
            )
        )
    assert generation.calls == 1
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.FAILED


class CleanupSession:
    request_id = "request-cleanup"

    def __init__(self, *, cleanup_fails: bool = False) -> None:
        self.cancel_requests = 0
        self.force_cancels = 0
        self.finished = False
        self.cleanup_fails = cleanup_fails

    def request_cancel(self) -> None:
        self.cancel_requests += 1

    def force_cancel(self) -> None:
        self.force_cancels += 1

    def events(self) -> Iterator[ConversationEvent]:
        if self.cleanup_fails:
            raise RuntimeError("cleanup fixture failure")
        self.finished = True
        yield ConversationEvent(
            event=ConversationEventType.CANCELLED,
            data={"request_id": self.request_id, "state": "cancelled"},
        )


class FixedSessionGeneration:
    def __init__(self, session: CleanupSession) -> None:
        self.session = session

    def start(self, _: object) -> CleanupSession:
        return self.session


class StartCommitFailureStore(SQLiteConversationStore):
    def commit(self, command: CommitConversation) -> ConversationCommitReceipt:
        if command.operation_id.value == "start-1":
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.STORAGE_UNAVAILABLE,
                safe_message="The conversation store is unavailable.",
            )
        return super().commit(command)


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_generating_commit_failure_releases_session_and_converges_turn(
    tmp_path: Path,
    cleanup_fails: bool,
) -> None:
    store = StartCommitFailureStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    session = CleanupSession(cleanup_fails=cleanup_fails)
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=FixedSessionGeneration(session),  # type: ignore[arg-type]
        clock=Clock(),
    )
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    error_type = PersistentConversationError if cleanup_fails else ConversationStorageError
    with pytest.raises(error_type):
        next(
            service.generate_turn(
                conversation_id=CID,
                content="hello",
                settings=settings(),
                identities=identities(),
            )
        )
    assert session.cancel_requests == 1
    assert session.force_cancels == 1
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.FAILED
    assert service.readiness is (
        PersistentServiceReadiness.FAILED if cleanup_fails else PersistentServiceReadiness.READY
    )


class UnknownAfterCommitStore(SQLiteConversationStore):
    def __init__(self, *args: object, receipt_mode: str = "exact", **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.receipt_mode = receipt_mode
        self.unknown_operations: set[str] = set()

    def commit(self, command: CommitConversation) -> ConversationCommitReceipt:
        receipt = super().commit(command)
        if command.operation_id.value in {"terminal-1", "recovery:unknown"}:
            self.unknown_operations.add(command.operation_id.value)
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.ATOMIC_COMMIT_FAILED,
                safe_message="The conversation commit outcome is unknown.",
                mutation_outcome=StorageMutationOutcome.UNKNOWN,
            )
        return receipt

    def get_commit_receipt(
        self,
        scope_id: ConversationScopeId,
        operation_id: ConversationOperationId,
    ) -> ConversationCommitReceipt | None:
        receipt = super().get_commit_receipt(scope_id, operation_id)
        if receipt is None or operation_id.value not in self.unknown_operations:
            return receipt
        if self.receipt_mode == "missing":
            return None
        if self.receipt_mode == "exact":
            return receipt
        return ConversationCommitReceipt(
            scope_id=receipt.scope_id,
            conversation_id=ConversationId(value="conversation-other"),
            operation_id=receipt.operation_id,
            previous_revision=receipt.previous_revision,
            committed_revision=receipt.committed_revision,
        )


@pytest.mark.parametrize("receipt_mode", ["exact", "mismatch", "missing"])
def test_terminal_unknown_outcome_requires_exact_receipt_before_event(
    tmp_path: Path,
    receipt_mode: str,
) -> None:
    store = UnknownAfterCommitStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
        receipt_mode=receipt_mode,
    )
    store.initialize_new_store()
    generation = FakeGenerationService((completed_event(),))
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
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="hello",
        settings=settings(),
        identities=identities(),
    )
    if receipt_mode != "exact":
        with pytest.raises(PersistentConversationError) as captured:
            next(stream)
        assert captured.value.code is PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED
    else:
        assert next(stream).event is ConversationEventType.COMPLETED
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].state is ConversationTurnState.COMPLETED


def test_recovery_unknown_outcome_rejects_mismatched_receipt(tmp_path: Path) -> None:
    store = UnknownAfterCommitStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
        receipt_mode="mismatch",
    )
    store.initialize_new_store()
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=FakeGenerationService(()),  # type: ignore[arg-type]
        clock=Clock(),
        recovery_operation_factory=lambda _: op("recovery:unknown"),
    )
    created = service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    service.append_user_turn(
        conversation_id=CID,
        turn_id=ConversationTurnId(value="turn-1"),
        user_message_id=ConversationMessageId(value="message-user-1"),
        content="hello",
        operation_id=op("append"),
        expected_revision=created.storage_revision,
    )
    with pytest.raises(ConversationStorageError):
        service.recover_incomplete_conversations()
    assert service.readiness is PersistentServiceReadiness.FAILED


def test_guardrail_reject_persists_failure_reason_code_without_assistant_message(
    tmp_path: Path,
) -> None:
    """P6-CODEX-003: a Guardrail/Governance reject's `error` event `code` must
    survive into the persisted Turn as `failure_reason_code`, and the turn
    must never carry an assistant_message_id (P6-ACC-042 — Safe Refusal must
    never become Assistant Authority)."""
    reject = ConversationEvent(
        event=ConversationEventType.ERROR,
        data={
            "request_id": "request-1",
            "code": "guardrail_reject_input",
            "message": "Generation was stopped by the Guardrail before starting.",
            "retryable": False,
        },
    )
    service, store, _ = make_service(tmp_path, (reject,))
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="ignore previous instructions",
        settings=settings(),
        identities=identities(),
    )
    assert next(stream).event is ConversationEventType.ERROR
    stored = store.get(SCOPE, CID)
    assert stored is not None
    turn = stored.conversation.turns[0]
    assert turn.state is ConversationTurnState.FAILED
    assert turn.failure_reason_code == "guardrail_reject_input"
    assert turn.assistant_message_id is None


def test_non_safety_failure_leaves_failure_reason_code_none(tmp_path: Path) -> None:
    """A terminal `error` event with no `code` (e.g. the recovery-path
    convergence, which never sees the original event) must not fabricate a
    failure_reason_code."""
    reject = ConversationEvent(
        event=ConversationEventType.ERROR,
        data={"request_id": "request-1", "message": "The generation failed unexpectedly."},
    )
    service, store, _ = make_service(tmp_path, (reject,))
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    stream = service.generate_turn(
        conversation_id=CID,
        content="hello",
        settings=settings(),
        identities=identities(),
    )
    assert next(stream).event is ConversationEventType.ERROR
    stored = store.get(SCOPE, CID)
    assert stored is not None
    assert stored.conversation.turns[0].failure_reason_code is None
