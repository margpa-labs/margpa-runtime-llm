"""Lifecycle, generation orchestration, and crash recovery for persistent chats."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterator, Mapping
from datetime import UTC, datetime
from functools import partial

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CitationUnavailable,
    DocumentationAugmentation,
    PersistedTurnCitationEvidence,
    build_turn_citation_evidence,
)
from margpa_runtime_llm.modules.documentation_rag.ports import CitationEvidenceStorePort

from ..contracts import ConversationEvent, ConversationEventType, ConversationSettings
from ..domain import (
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
    ConversationStorageErrorCode,
    ConversationTurn,
    ConversationTurnId,
    ConversationTurnOrigin,
    ConversationTurnState,
    PersistedConversationMessage,
    PersistedConversationRole,
    StorageMutationOutcome,
    transition_conversation_state,
    transition_session,
    transition_turn,
)
from ..ports import (
    CommitConversation,
    ConversationCommitReceipt,
    ConversationListQuery,
    ConversationPage,
    ConversationRepositoryPort,
    StoredConversation,
)
from .conversation_generation import (
    ConversationGenerationService,
    ConversationGenerationSession,
)
from .generation_context_mapper import map_generation_context
from .persistence_models import (
    PersistentConversationError,
    PersistentConversationErrorCode,
    PersistentGenerationIdentities,
    PersistentServiceReadiness,
    RecoveryResult,
)

Clock = Callable[[], datetime]
RecoveryOperationFactory = Callable[[str], ConversationOperationId]


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _recovery_operation_id(label: str) -> ConversationOperationId:
    digest = hashlib.sha512(f"margpa:conversation-recovery:v1:{label}".encode()).hexdigest()
    return ConversationOperationId(value=digest)


class PersistentConversationService:
    def __init__(
        self,
        *,
        repository: ConversationRepositoryPort,
        bound_scope_id: ConversationScopeId,
        generation_service: ConversationGenerationService,
        clock: Clock = _utc_now,
        recovery_operation_factory: RecoveryOperationFactory = _recovery_operation_id,
    ) -> None:
        self._repository = repository
        self._scope_id = bound_scope_id
        self._generation = generation_service
        self._clock = clock
        self._recovery_operation_factory = recovery_operation_factory
        self._readiness = PersistentServiceReadiness.NOT_READY

    @property
    def readiness(self) -> PersistentServiceReadiness:
        return self._readiness

    def get_conversation(self, conversation_id: ConversationId) -> StoredConversation:
        """Return the bound-scope canonical aggregate without mutating it."""

        return self._require(conversation_id)

    def get_conversation_citations(
        self,
        conversation_id: ConversationId,
    ) -> Mapping[str, PersistedTurnCitationEvidence | CitationUnavailable]:
        """Persisted per-turn citation evidence, if the repository stores it.

        Returns an empty mapping (not an error) when the bound repository does
        not implement `CitationEvidenceStorePort` — e.g. a Public/Basic Preview
        or test double that never constructs citation storage at all.
        """

        if not isinstance(self._repository, CitationEvidenceStorePort):
            return {}
        return self._repository.get_conversation_citations(conversation_id.value)

    def list_conversations(
        self,
        *,
        states: frozenset[ConversationState] = frozenset(),
        limit: int = 50,
        cursor: str | None = None,
    ) -> ConversationPage:
        """Return a safe bound-scope page directly from the repository."""

        return self._repository.list(
            ConversationListQuery(
                scope_id=self._scope_id,
                states=states,
                limit=limit,
                cursor=cursor,
            )
        )

    def operation_was_applied(self, operation_id: ConversationOperationId) -> bool:
        """Check a transport-derived repository identity without exposing its receipt."""

        return self._repository.get_commit_receipt(self._scope_id, operation_id) is not None

    def create_conversation(
        self,
        *,
        conversation_id: ConversationId,
        session_id: ConversationSessionId,
        operation_id: ConversationOperationId,
    ) -> StoredConversation:
        now = self._clock()
        snapshot = ConversationSnapshot(
            scope_id=self._scope_id,
            conversation_id=conversation_id,
            state=ConversationState.ACTIVE,
            created_at=now,
            updated_at=now,
            sessions=(
                ConversationSessionRecord(
                    session_id=session_id,
                    conversation_id=conversation_id,
                    state=ConversationSessionState.ACTIVE,
                    opened_at=now,
                ),
            ),
        )
        self._commit(snapshot, operation_id=operation_id, expected_revision=None)
        return self._require(conversation_id)

    def resume_conversation(
        self,
        *,
        conversation_id: ConversationId,
        session_id: ConversationSessionId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        if snapshot.state is not ConversationState.ACTIVE or any(
            item.state is ConversationSessionState.ACTIVE for item in snapshot.sessions
        ):
            raise self._invalid_lifecycle()
        now = self._clock()
        session = ConversationSessionRecord(
            session_id=session_id,
            conversation_id=conversation_id,
            state=ConversationSessionState.ACTIVE,
            opened_at=now,
        )
        candidate = snapshot.model_copy(
            update={"sessions": (*snapshot.sessions, session), "updated_at": now}
        )
        candidate = ConversationSnapshot.model_validate(candidate.model_dump())
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def append_user_turn(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        user_message_id: ConversationMessageId,
        content: str,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        active_sessions = [
            item for item in snapshot.sessions if item.state is ConversationSessionState.ACTIVE
        ]
        if (
            snapshot.state is not ConversationState.ACTIVE
            or len(active_sessions) != 1
            or any(
                turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                for turn in snapshot.turns
            )
        ):
            raise self._invalid_lifecycle()
        now = self._clock()
        turn_sequence = max((item.sequence for item in snapshot.turns), default=-1) + 1
        message_sequence = max((item.sequence for item in snapshot.messages), default=-1) + 1
        turn = ConversationTurn(
            turn_id=turn_id,
            conversation_id=conversation_id,
            session_id=active_sessions[0].session_id,
            sequence=turn_sequence,
            state=ConversationTurnState.PENDING,
            origin=ConversationTurnOrigin.NORMAL,
            parent_turn_id=snapshot.head_turn_id,
            user_message_id=user_message_id,
            started_at=now,
        )
        message = PersistedConversationMessage(
            message_id=user_message_id,
            conversation_id=conversation_id,
            turn_id=turn_id,
            sequence=message_sequence,
            role=PersistedConversationRole.USER,
            content=content,
            created_at=now,
        )
        candidate = snapshot.model_copy(
            update={
                "turns": (*snapshot.turns, turn),
                "messages": (*snapshot.messages, message),
                "updated_at": now,
            }
        )
        candidate = ConversationSnapshot.model_validate(candidate.model_dump())
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def append_derived_turn(
        self,
        *,
        conversation_id: ConversationId,
        source_turn_id: ConversationTurnId,
        origin: ConversationTurnOrigin,
        turn_id: ConversationTurnId,
        user_message_id: ConversationMessageId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        """Append a retry/regenerate candidate from canonical server state."""

        if origin not in {ConversationTurnOrigin.RETRY, ConversationTurnOrigin.REGENERATE}:
            raise self._invalid_lifecycle()
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        source = self._find_turn(snapshot, source_turn_id)
        retry_states = {
            ConversationTurnState.FAILED,
            ConversationTurnState.CANCELLED,
            ConversationTurnState.INTERRUPTED,
        }
        if (origin is ConversationTurnOrigin.RETRY and source.state not in retry_states) or (
            origin is ConversationTurnOrigin.REGENERATE
            and source.state is not ConversationTurnState.COMPLETED
        ):
            raise self._invalid_lifecycle()
        active_sessions = [
            item for item in snapshot.sessions if item.state is ConversationSessionState.ACTIVE
        ]
        if (
            snapshot.state is not ConversationState.ACTIVE
            or len(active_sessions) != 1
            or any(
                turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                for turn in snapshot.turns
            )
        ):
            raise self._invalid_lifecycle()
        source_message = next(
            (item for item in snapshot.messages if item.message_id == source.user_message_id),
            None,
        )
        if source_message is None or source_message.role is not PersistedConversationRole.USER:
            raise self._invalid_lifecycle()
        now = self._clock()
        turn = ConversationTurn(
            turn_id=turn_id,
            conversation_id=conversation_id,
            session_id=active_sessions[0].session_id,
            sequence=max((item.sequence for item in snapshot.turns), default=-1) + 1,
            state=ConversationTurnState.PENDING,
            origin=origin,
            parent_turn_id=source.parent_turn_id,
            derived_from_turn_id=source_turn_id,
            user_message_id=user_message_id,
            started_at=now,
        )
        message = PersistedConversationMessage(
            message_id=user_message_id,
            conversation_id=conversation_id,
            turn_id=turn_id,
            sequence=max((item.sequence for item in snapshot.messages), default=-1) + 1,
            role=PersistedConversationRole.USER,
            content=source_message.content,
            created_at=now,
        )
        candidate = snapshot.model_copy(
            update={
                "turns": (*snapshot.turns, turn),
                "messages": (*snapshot.messages, message),
                "updated_at": now,
            }
        )
        candidate = ConversationSnapshot.model_validate(candidate.model_dump())
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def start_generation(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        request_id: str,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        return self._transition_terminal_or_generating(
            conversation_id=conversation_id,
            turn_id=turn_id,
            target=ConversationTurnState.GENERATING,
            operation_id=operation_id,
            expected_revision=expected_revision,
            request_id=request_id,
        )

    def complete_generation(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        assistant_message_id: ConversationMessageId,
        content: str,
        operation_id: ConversationOperationId,
        expected_revision: int,
        documentation_augmentation: DocumentationAugmentation | None = None,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        turn = self._find_turn(snapshot, turn_id)
        now = self._clock()
        assistant = PersistedConversationMessage(
            message_id=assistant_message_id,
            conversation_id=conversation_id,
            turn_id=turn_id,
            sequence=max((item.sequence for item in snapshot.messages), default=-1) + 1,
            role=PersistedConversationRole.ASSISTANT,
            content=content,
            created_at=now,
        )
        completed = transition_turn(
            turn,
            target=ConversationTurnState.COMPLETED,
            finished_at=now,
            assistant_message_id=assistant_message_id,
        )
        candidate = self._replace_turn(
            snapshot,
            completed,
            messages=(*snapshot.messages, assistant),
            head_turn_id=turn_id,
            updated_at=now,
        )
        citation_evidence = (
            None
            if documentation_augmentation is None
            else build_turn_citation_evidence(
                documentation_augmentation,
                conversation_id=conversation_id.value,
                turn_id=turn_id.value,
            )
        )
        self._commit(
            candidate,
            operation_id=operation_id,
            expected_revision=expected_revision,
            citation_evidence=citation_evidence,
        )
        return self._require(conversation_id)

    def cancel_generation(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        return self._transition_terminal_or_generating(
            conversation_id=conversation_id,
            turn_id=turn_id,
            target=ConversationTurnState.CANCELLED,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )

    def fail_generation(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        return self._transition_terminal_or_generating(
            conversation_id=conversation_id,
            turn_id=turn_id,
            target=ConversationTurnState.FAILED,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )

    def interrupt_generation(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        return self._transition_terminal_or_generating(
            conversation_id=conversation_id,
            turn_id=turn_id,
            target=ConversationTurnState.INTERRUPTED,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )

    def close_session(
        self,
        *,
        conversation_id: ConversationId,
        session_id: ConversationSessionId,
        operation_id: ConversationOperationId,
        expected_revision: int,
        interrupted: bool = False,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        if any(
            turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
            and turn.session_id == session_id
            for turn in snapshot.turns
        ):
            raise self._invalid_lifecycle()
        session = next((item for item in snapshot.sessions if item.session_id == session_id), None)
        if session is None:
            raise self._not_found()
        now = self._clock()
        terminal = transition_session(
            session,
            target=(
                ConversationSessionState.INTERRUPTED
                if interrupted
                else ConversationSessionState.CLOSED
            ),
            finished_at=now,
        )
        sessions = tuple(
            terminal if item.session_id == session_id else item for item in snapshot.sessions
        )
        candidate = snapshot.model_copy(update={"sessions": sessions, "updated_at": now})
        candidate = ConversationSnapshot.model_validate(candidate.model_dump())
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def set_archived(
        self,
        *,
        conversation_id: ConversationId,
        operation_id: ConversationOperationId,
        expected_revision: int,
        archived: bool,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        target = ConversationState.ARCHIVED if archived else ConversationState.ACTIVE
        try:
            snapshot = stored.conversation
            now = self._clock()
            if archived:
                if any(
                    turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                    for turn in snapshot.turns
                ):
                    raise ValueError("non-terminal turn")
                sessions = tuple(
                    transition_session(
                        session,
                        target=ConversationSessionState.CLOSED,
                        finished_at=now,
                    )
                    if session.state is ConversationSessionState.ACTIVE
                    else session
                    for session in snapshot.sessions
                )
                snapshot = ConversationSnapshot.model_validate(
                    snapshot.model_copy(update={"sessions": sessions}).model_dump()
                )
            candidate = transition_conversation_state(
                snapshot,
                target=target,
                updated_at=now,
            )
        except Exception:
            raise self._invalid_lifecycle() from None
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def rename_conversation(
        self,
        *,
        conversation_id: ConversationId,
        operation_id: ConversationOperationId,
        expected_revision: int,
        title: str | None,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        if snapshot.state is ConversationState.DELETED:
            raise self._invalid_lifecycle()
        now = self._clock()
        try:
            candidate = ConversationSnapshot.model_validate(
                snapshot.model_copy(update={"title": title, "updated_at": now}).model_dump()
            )
        except Exception:
            raise self._invalid_lifecycle() from None
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def set_deleted(
        self,
        *,
        conversation_id: ConversationId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        """One-directional soft delete: no API-level restore (2-E-H design, Q2/[A])."""

        stored = self._require_revision(conversation_id, expected_revision)
        try:
            snapshot = stored.conversation
            now = self._clock()
            if any(
                turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                for turn in snapshot.turns
            ):
                raise ValueError("non-terminal turn")
            sessions = tuple(
                transition_session(
                    session,
                    target=ConversationSessionState.CLOSED,
                    finished_at=now,
                )
                if session.state is ConversationSessionState.ACTIVE
                else session
                for session in snapshot.sessions
            )
            snapshot = ConversationSnapshot.model_validate(
                snapshot.model_copy(update={"sessions": sessions}).model_dump()
            )
            candidate = transition_conversation_state(
                snapshot,
                target=ConversationState.DELETED,
                updated_at=now,
            )
        except Exception:
            raise self._invalid_lifecycle() from None
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def generate_turn(
        self,
        *,
        conversation_id: ConversationId,
        content: str,
        settings: ConversationSettings,
        identities: PersistentGenerationIdentities,
        expected_revision: int | None = None,
    ) -> Iterator[ConversationEvent]:
        if self._readiness is not PersistentServiceReadiness.READY:
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.STORAGE_NOT_READY,
                safe_message="Persistent conversation service is not ready.",
            )
        initial = (
            self._require(conversation_id)
            if expected_revision is None
            else self._require_revision(conversation_id, expected_revision)
        )
        pending = self.append_user_turn(
            conversation_id=conversation_id,
            turn_id=identities.turn_id,
            user_message_id=identities.user_message_id,
            content=content,
            operation_id=identities.append_operation_id,
            expected_revision=initial.storage_revision,
        )
        yield from self._generate_pending_turn(
            conversation_id=conversation_id,
            pending=pending,
            settings=settings,
            identities=identities,
        )

    def generate_derived_turn(
        self,
        *,
        conversation_id: ConversationId,
        source_turn_id: ConversationTurnId,
        origin: ConversationTurnOrigin,
        expected_revision: int,
        settings: ConversationSettings,
        identities: PersistentGenerationIdentities,
    ) -> Iterator[ConversationEvent]:
        if self._readiness is not PersistentServiceReadiness.READY:
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.STORAGE_NOT_READY,
                safe_message="Persistent conversation service is not ready.",
            )
        pending = self.append_derived_turn(
            conversation_id=conversation_id,
            source_turn_id=source_turn_id,
            origin=origin,
            turn_id=identities.turn_id,
            user_message_id=identities.user_message_id,
            operation_id=identities.append_operation_id,
            expected_revision=expected_revision,
        )
        yield from self._generate_pending_turn(
            conversation_id=conversation_id,
            pending=pending,
            settings=settings,
            identities=identities,
        )

    def select_branch_head(
        self,
        *,
        conversation_id: ConversationId,
        completed_turn_id: ConversationTurnId,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        selected = self._find_turn(snapshot, completed_turn_id)
        if (
            snapshot.state is not ConversationState.ACTIVE
            or selected.state is not ConversationTurnState.COMPLETED
            or any(
                turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                for turn in snapshot.turns
            )
        ):
            raise self._invalid_lifecycle()
        candidate = ConversationSnapshot.model_validate(
            snapshot.model_copy(
                update={"head_turn_id": completed_turn_id, "updated_at": self._clock()}
            ).model_dump()
        )
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    def cancel_active_generation(
        self,
        *,
        conversation_id: ConversationId,
        request_id: str,
        expected_revision: int,
    ) -> bool:
        stored = self._require_revision(conversation_id, expected_revision)
        active = [
            turn
            for turn in stored.conversation.turns
            if turn.state is ConversationTurnState.GENERATING
        ]
        if len(active) != 1 or active[0].request_id != request_id:
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.GENERATION_NOT_ACTIVE,
                safe_message="The requested generation is not active.",
            )
        if not self._generation.cancel(request_id):
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.GENERATION_NOT_ACTIVE,
                safe_message="The requested generation is not active.",
            )
        return True

    def _generate_pending_turn(
        self,
        *,
        conversation_id: ConversationId,
        pending: StoredConversation,
        settings: ConversationSettings,
        identities: PersistentGenerationIdentities,
    ) -> Iterator[ConversationEvent]:
        try:
            pending_turn = self._find_turn(pending.conversation, identities.turn_id)
            mapping_snapshot = (
                pending.conversation
                if pending_turn.origin is ConversationTurnOrigin.NORMAL
                else pending.conversation.model_copy(
                    update={"head_turn_id": pending_turn.parent_turn_id}
                )
            )
            generation_input = map_generation_context(
                mapping_snapshot,
                pending_turn_id=identities.turn_id,
                settings=settings,
            )
        except BaseException:
            self._converge_failed_turn(
                conversation_id=conversation_id,
                turn_id=identities.turn_id,
                operation_id=identities.terminal_operation_id,
            )
            raise
        try:
            session = self._generation.start(generation_input)
        except BaseException:
            self._converge_failed_turn(
                conversation_id=conversation_id,
                turn_id=identities.turn_id,
                operation_id=identities.terminal_operation_id,
            )
            raise
        try:
            generating = self.start_generation(
                conversation_id=conversation_id,
                turn_id=identities.turn_id,
                request_id=session.request_id,
                operation_id=identities.start_operation_id,
                expected_revision=pending.storage_revision,
            )
        except BaseException:
            cleanup_failed = False
            try:
                self._release_failed_ephemeral_session(session)
            except BaseException:
                cleanup_failed = True
            try:
                self._converge_failed_turn(
                    conversation_id=conversation_id,
                    turn_id=identities.turn_id,
                    operation_id=identities.terminal_operation_id,
                )
            except BaseException:
                cleanup_failed = True
            if cleanup_failed:
                self._readiness = PersistentServiceReadiness.FAILED
                raise PersistentConversationError(
                    code=PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED,
                    safe_message="Generation startup cleanup could not be verified.",
                ) from None
            raise
        terminal_persisted = False
        try:
            for event in session.events():
                if event.event is ConversationEventType.COMPLETED:
                    assistant = event.data.get("assistant_message")
                    content_value = (
                        assistant.get("content") if isinstance(assistant, dict) else None
                    )
                    if not isinstance(content_value, str) or not content_value.strip():
                        raise PersistentConversationError(
                            code=PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED,
                            safe_message="The canonical assistant message could not be persisted.",
                        )
                    self._persist_terminal(
                        partial(
                            self.complete_generation,
                            conversation_id=conversation_id,
                            turn_id=identities.turn_id,
                            assistant_message_id=identities.assistant_message_id,
                            content=content_value,
                            operation_id=identities.terminal_operation_id,
                            expected_revision=generating.storage_revision,
                            documentation_augmentation=session.documentation_augmentation,
                        )
                    )
                    terminal_persisted = True
                elif event.event is ConversationEventType.CANCELLED:
                    self._persist_terminal(
                        lambda: self.cancel_generation(
                            conversation_id=conversation_id,
                            turn_id=identities.turn_id,
                            operation_id=identities.terminal_operation_id,
                            expected_revision=generating.storage_revision,
                        )
                    )
                    terminal_persisted = True
                elif event.event is ConversationEventType.ERROR:
                    self._persist_terminal(
                        lambda: self.fail_generation(
                            conversation_id=conversation_id,
                            turn_id=identities.turn_id,
                            operation_id=identities.terminal_operation_id,
                            expected_revision=generating.storage_revision,
                        )
                    )
                    terminal_persisted = True
                yield event
        finally:
            if not terminal_persisted:
                try:
                    current = self._require(conversation_id)
                    turn = self._find_turn(current.conversation, identities.turn_id)
                    if turn.state in {
                        ConversationTurnState.PENDING,
                        ConversationTurnState.GENERATING,
                    }:
                        self.interrupt_generation(
                            conversation_id=conversation_id,
                            turn_id=identities.turn_id,
                            operation_id=identities.terminal_operation_id,
                            expected_revision=current.storage_revision,
                        )
                except Exception:
                    self._readiness = PersistentServiceReadiness.FAILED

    def recover_incomplete_conversations(self, *, max_conflict_retries: int = 2) -> RecoveryResult:
        self._readiness = PersistentServiceReadiness.NOT_READY
        inspected = 0
        recovered = 0
        cursor: str | None = None
        try:
            while True:
                page = self._repository.list(
                    ConversationListQuery(
                        scope_id=self._scope_id,
                        states=frozenset({ConversationState.ACTIVE}),
                        limit=100,
                        cursor=cursor,
                    )
                )
                for summary in page.items:
                    inspected += 1
                    if self._recover_one(summary.conversation_id, max_conflict_retries):
                        recovered += 1
                if page.next_cursor is None:
                    break
                cursor = page.next_cursor
        except BaseException:
            self._readiness = PersistentServiceReadiness.FAILED
            raise
        self._readiness = PersistentServiceReadiness.READY
        return RecoveryResult(
            inspected_conversations=inspected,
            recovered_conversations=recovered,
        )

    def _recover_one(self, conversation_id: ConversationId, retries: int) -> bool:
        for attempt in range(retries + 1):
            stored = self._require(conversation_id)
            snapshot = stored.conversation
            if not self._needs_recovery(snapshot):
                return False
            now = self._clock()
            turns = tuple(
                transition_turn(turn, target=ConversationTurnState.INTERRUPTED, finished_at=now)
                if turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
                else turn
                for turn in snapshot.turns
            )
            sessions = tuple(
                transition_session(
                    session,
                    target=ConversationSessionState.INTERRUPTED,
                    finished_at=now,
                )
                if session.state is ConversationSessionState.ACTIVE
                else session
                for session in snapshot.sessions
            )
            candidate = snapshot.model_copy(
                update={"turns": turns, "sessions": sessions, "updated_at": now}
            )
            candidate = ConversationSnapshot.model_validate(candidate.model_dump())
            operation_id = self._recovery_operation_factory(
                f"{conversation_id.value}:{stored.storage_revision}:{attempt}"
            )
            try:
                self._commit(
                    candidate,
                    operation_id=operation_id,
                    expected_revision=stored.storage_revision,
                )
                return True
            except ConversationStorageError as exc:
                if exc.code is ConversationStorageErrorCode.CONFLICT and attempt < retries:
                    continue
                raise
        return False

    @staticmethod
    def _needs_recovery(snapshot: ConversationSnapshot) -> bool:
        return any(
            turn.state in {ConversationTurnState.PENDING, ConversationTurnState.GENERATING}
            for turn in snapshot.turns
        ) or any(session.state is ConversationSessionState.ACTIVE for session in snapshot.sessions)

    def _transition_terminal_or_generating(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        target: ConversationTurnState,
        operation_id: ConversationOperationId,
        expected_revision: int,
        request_id: str | None = None,
    ) -> StoredConversation:
        stored = self._require_revision(conversation_id, expected_revision)
        snapshot = stored.conversation
        turn = self._find_turn(snapshot, turn_id)
        now = self._clock()
        try:
            transitioned = transition_turn(
                turn,
                target=target,
                finished_at=None if target is ConversationTurnState.GENERATING else now,
                request_id=request_id,
            )
        except Exception:
            raise self._invalid_lifecycle() from None
        candidate = self._replace_turn(snapshot, transitioned, updated_at=now)
        self._commit(candidate, operation_id=operation_id, expected_revision=expected_revision)
        return self._require(conversation_id)

    @staticmethod
    def _replace_turn(
        snapshot: ConversationSnapshot,
        replacement: ConversationTurn,
        *,
        messages: tuple[PersistedConversationMessage, ...] | None = None,
        head_turn_id: ConversationTurnId | None = None,
        updated_at: datetime,
    ) -> ConversationSnapshot:
        turns = tuple(
            replacement if item.turn_id == replacement.turn_id else item for item in snapshot.turns
        )
        candidate = snapshot.model_copy(
            update={
                "turns": turns,
                "messages": snapshot.messages if messages is None else messages,
                "head_turn_id": snapshot.head_turn_id if head_turn_id is None else head_turn_id,
                "updated_at": updated_at,
            }
        )
        return ConversationSnapshot.model_validate(candidate.model_dump())

    @staticmethod
    def _find_turn(snapshot: ConversationSnapshot, turn_id: ConversationTurnId) -> ConversationTurn:
        turn = next((item for item in snapshot.turns if item.turn_id == turn_id), None)
        if turn is None:
            raise PersistentConversationService._not_found()
        return turn

    def _require(self, conversation_id: ConversationId) -> StoredConversation:
        value = self._repository.get(self._scope_id, conversation_id)
        if value is None:
            raise self._not_found()
        return value

    def _require_revision(
        self,
        conversation_id: ConversationId,
        revision: int,
    ) -> StoredConversation:
        value = self._require(conversation_id)
        if value.storage_revision != revision:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The conversation changed before it could be updated.",
                retryable=True,
                expected_revision=revision,
                actual_revision=value.storage_revision,
            )
        return value

    def _commit(
        self,
        snapshot: ConversationSnapshot,
        *,
        operation_id: ConversationOperationId,
        expected_revision: int | None,
        citation_evidence: PersistedTurnCitationEvidence | None = None,
    ) -> ConversationCommitReceipt:
        command = CommitConversation(
            scope_id=self._scope_id,
            operation_id=operation_id,
            expected_revision=expected_revision,
            conversation=snapshot,
            citation_evidence=citation_evidence,
        )
        try:
            return self._repository.commit(command)
        except ConversationStorageError as exc:
            if exc.mutation_outcome is not StorageMutationOutcome.UNKNOWN:
                raise
            try:
                receipt = self._repository.get_commit_receipt(self._scope_id, operation_id)
            except BaseException:
                raise exc from None
            if receipt is not None and self._receipt_matches_command(receipt, command):
                return receipt
            raise

    @staticmethod
    def _receipt_matches_command(
        receipt: ConversationCommitReceipt,
        command: CommitConversation,
    ) -> bool:
        expected_committed = (
            1 if command.expected_revision is None else command.expected_revision + 1
        )
        return (
            receipt.scope_id == command.scope_id
            and receipt.conversation_id == command.conversation.conversation_id
            and receipt.operation_id == command.operation_id
            and receipt.previous_revision == command.expected_revision
            and receipt.committed_revision == expected_committed
        )

    def _converge_failed_turn(
        self,
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        operation_id: ConversationOperationId,
    ) -> None:
        try:
            current = self._require(conversation_id)
            turn = self._find_turn(current.conversation, turn_id)
            if turn.state not in {
                ConversationTurnState.PENDING,
                ConversationTurnState.GENERATING,
            }:
                return
            self.fail_generation(
                conversation_id=conversation_id,
                turn_id=turn_id,
                operation_id=operation_id,
                expected_revision=current.storage_revision,
            )
        except BaseException:
            self._readiness = PersistentServiceReadiness.FAILED
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED,
                safe_message="Generation startup persistence cleanup could not be verified.",
            ) from None

    @staticmethod
    def _release_failed_ephemeral_session(session: ConversationGenerationSession) -> None:
        session.request_cancel()
        session.force_cancel()
        for _ in session.events():
            pass
        if not session.finished:
            raise RuntimeError("generation session cleanup was not verified")

    def _persist_terminal(self, operation: Callable[[], StoredConversation]) -> None:
        try:
            operation()
        except BaseException:
            self._readiness = PersistentServiceReadiness.FAILED
            raise PersistentConversationError(
                code=PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED,
                safe_message="The generation result could not be persisted.",
            ) from None

    @staticmethod
    def _not_found() -> PersistentConversationError:
        return PersistentConversationError(
            code=PersistentConversationErrorCode.NOT_FOUND,
            safe_message="The conversation was not found.",
        )

    @staticmethod
    def _invalid_lifecycle() -> PersistentConversationError:
        return PersistentConversationError(
            code=PersistentConversationErrorCode.INVALID_LIFECYCLE,
            safe_message="The conversation lifecycle operation is not allowed.",
        )
