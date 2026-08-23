"""Persistent conversation aggregate contracts and pure domain policies."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ConversationDomainError, ConversationDomainErrorCode
from .identity import (
    ConversationId,
    ConversationMessageId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationTurnId,
)

MAX_PERSISTED_MESSAGE_CHARACTERS = 32_768
MAX_CONVERSATION_TITLE_CHARACTERS = 200


class ConversationState(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ConversationSessionState(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    INTERRUPTED = "interrupted"


class ConversationTurnState(StrEnum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ConversationTurnOrigin(StrEnum):
    NORMAL = "normal"
    RETRY = "retry"
    REGENERATE = "regenerate"
    REPAIR = "repair"
    """A Bounded Repair's New Attempt (P6-CODEX-009, Second Rework):
    persists exactly like REGENERATE (same source User Message content,
    a genuinely new Turn/Message Identity, never a rewrite of the
    Original) — the only difference is which internal caller produced it
    and that it is created only after the Original's own Turn already
    completed and a Rejudge confirmed the new candidate is an
    improvement."""


class PersistedConversationRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


def _is_utc(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() == timedelta(0)


def _require_utc(value: datetime, *, field_name: str) -> datetime:
    if not _is_utc(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


def _validate_title(value: str | None) -> str | None:
    """A conversation title is either absent (fall back to an auto-generated
    label) or a non-blank, already-trimmed single line within the length
    limit. `None` and `""` are deliberately not interchangeable: only `None`
    means "no custom title" — an empty string is rejected rather than
    silently treated the same way, so a caller cannot accidentally persist
    an ambiguous blank title.
    """

    if value is None:
        return None
    if value != value.strip() or not value:
        raise ValueError("conversation title must be a non-blank, trimmed value")
    if len(value) > MAX_CONVERSATION_TITLE_CHARACTERS:
        raise ValueError("conversation title exceeds the maximum length")
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in value):
        raise ValueError("conversation title must not contain control characters")
    return value


class PersistedConversationMessage(ImmutableContract):
    message_id: ConversationMessageId
    conversation_id: ConversationId
    turn_id: ConversationTurnId
    sequence: int = Field(strict=True, ge=0)
    role: PersistedConversationRole
    content: str = Field(max_length=MAX_PERSISTED_MESSAGE_CHARACTERS)
    created_at: datetime

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("persisted conversation message content must not be blank")
        return value

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        return _require_utc(value, field_name="created_at")


class ConversationSessionRecord(ImmutableContract):
    session_id: ConversationSessionId
    conversation_id: ConversationId
    state: ConversationSessionState
    opened_at: datetime
    finished_at: datetime | None = None

    @field_validator("opened_at")
    @classmethod
    def validate_opened_at(cls, value: datetime) -> datetime:
        return _require_utc(value, field_name="opened_at")

    @field_validator("finished_at")
    @classmethod
    def validate_finished_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _require_utc(value, field_name="finished_at")

    @model_validator(mode="after")
    def validate_terminal_time(self) -> ConversationSessionRecord:
        if self.state is ConversationSessionState.ACTIVE and self.finished_at is not None:
            raise ValueError("an active conversation session must not have finished_at")
        if self.state is not ConversationSessionState.ACTIVE and self.finished_at is None:
            raise ValueError("a terminal conversation session requires finished_at")
        if self.finished_at is not None and self.finished_at < self.opened_at:
            raise ValueError("conversation session finished_at precedes opened_at")
        return self


class ConversationTurnProvenance(ImmutableContract):
    """A completed Generation Attempt's Model/Backend/Context identity
    (P6-CODEX-013): Role is `origin` on the owning `ConversationTurn`
    itself, so it is not repeated here. `generation_config_digest_sha512`
    is Optional because not every caller (e.g. Repair's out-of-band
    candidate generation) computes one today; absent is represented
    explicitly as `None`, never a fabricated placeholder."""

    model_identity: str = Field(min_length=1)
    backend_key: str = Field(min_length=1)
    backend_version: str = Field(min_length=1)
    artifact_digest_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")
    context_size: int = Field(gt=0)
    generation_config_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")


class ConversationTurn(ImmutableContract):
    turn_id: ConversationTurnId
    conversation_id: ConversationId
    session_id: ConversationSessionId
    sequence: int = Field(strict=True, ge=0)
    state: ConversationTurnState
    origin: ConversationTurnOrigin = ConversationTurnOrigin.NORMAL
    parent_turn_id: ConversationTurnId | None = None
    derived_from_turn_id: ConversationTurnId | None = None
    user_message_id: ConversationMessageId
    assistant_message_id: ConversationMessageId | None = None
    request_id: str | None = Field(default=None, min_length=1, max_length=128)
    started_at: datetime
    finished_at: datetime | None = None
    failure_reason_code: str | None = Field(default=None, min_length=1, max_length=128)
    """Set only when `state is FAILED` (P6-CODEX-003): the Guardrail/
    Governance/generic reason_code the terminal `error` event carried, so a
    Reload/Resume can reconstruct the same Safe Refusal Presentation the
    live SSE stream showed, without persisting an actual Assistant Message
    (P6-ACC-042 — a Safe Refusal must never become Assistant Authority).
    A new Optional field with a default of None round-trips through the
    existing JSON-blob storage format without a schema migration: old rows
    simply decode as None."""
    provenance: ConversationTurnProvenance | None = Field(default=None)
    """Set only when `state is COMPLETED` (P6-CODEX-013): the real Model/
    Backend/Context identity this specific Generation Attempt actually
    ran with. Same additive-Optional-field, no-migration shape as
    `failure_reason_code` above; old persisted rows simply decode as
    None rather than fabricating a value for an Attempt that predates
    this field's existence."""

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("request_id must not be blank")
        return value

    @field_validator("started_at")
    @classmethod
    def validate_started_at(cls, value: datetime) -> datetime:
        return _require_utc(value, field_name="started_at")

    @field_validator("finished_at")
    @classmethod
    def validate_finished_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _require_utc(value, field_name="finished_at")

    @model_validator(mode="after")
    def validate_state_shape(self) -> ConversationTurn:
        terminal = self.state in {
            ConversationTurnState.COMPLETED,
            ConversationTurnState.CANCELLED,
            ConversationTurnState.FAILED,
            ConversationTurnState.INTERRUPTED,
        }
        if terminal and self.finished_at is None:
            raise ValueError("a terminal conversation turn requires finished_at")
        if not terminal and self.finished_at is not None:
            raise ValueError("a non-terminal conversation turn must not have finished_at")
        if self.finished_at is not None and self.finished_at < self.started_at:
            raise ValueError("conversation turn finished_at precedes started_at")
        if self.state is ConversationTurnState.COMPLETED:
            if self.assistant_message_id is None:
                raise ValueError("a completed turn requires an assistant message")
        elif self.assistant_message_id is not None:
            raise ValueError("only a completed turn may reference an assistant message")
        if self.state is not ConversationTurnState.FAILED and self.failure_reason_code is not None:
            raise ValueError("only a failed turn may carry a failure_reason_code")
        if self.parent_turn_id == self.turn_id:
            raise ValueError("a turn cannot be its own parent")
        if self.derived_from_turn_id == self.turn_id:
            raise ValueError("a turn cannot be derived from itself")
        if self.origin is ConversationTurnOrigin.NORMAL:
            if self.derived_from_turn_id is not None:
                raise ValueError("a normal turn must not have derived_from_turn_id")
        elif self.derived_from_turn_id is None:
            raise ValueError("a retry or regenerate turn requires derived_from_turn_id")
        return self


class ConversationSnapshot(ImmutableContract):
    scope_id: ConversationScopeId
    conversation_id: ConversationId
    state: ConversationState
    title: str | None = None
    head_turn_id: ConversationTurnId | None = None
    created_at: datetime
    updated_at: datetime
    sessions: tuple[ConversationSessionRecord, ...] = ()
    turns: tuple[ConversationTurn, ...] = ()
    messages: tuple[PersistedConversationMessage, ...] = ()

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return _validate_title(value)

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_timestamp(cls, value: datetime, info: object) -> datetime:
        field_name = getattr(info, "field_name", "timestamp")
        return _require_utc(value, field_name=field_name)

    @model_validator(mode="after")
    def validate_aggregate(self) -> ConversationSnapshot:
        if self.updated_at < self.created_at:
            raise ValueError("conversation updated_at precedes created_at")

        self._require_unique_identity(self.sessions, "session_id", "session")
        self._require_unique_identity(self.turns, "turn_id", "turn")
        self._require_unique_identity(self.messages, "message_id", "message")
        session_by_id = {session.session_id.value: session for session in self.sessions}
        turn_by_id = {turn.turn_id.value: turn for turn in self.turns}
        message_by_id = {message.message_id.value: message for message in self.messages}
        self._require_unique_sequence(self.turns, "turn")
        self._require_unique_sequence(self.messages, "message")

        messages_by_turn: dict[str, list[PersistedConversationMessage]] = defaultdict(list)
        for session in self.sessions:
            self._require_conversation(session.conversation_id, "session")
        for message in self.messages:
            self._require_conversation(message.conversation_id, "message")
            messages_by_turn[message.turn_id.value].append(message)

        non_terminal_count = 0
        for turn in self.turns:
            self._require_conversation(turn.conversation_id, "turn")
            turn_session = session_by_id.get(turn.session_id.value)
            if turn_session is None:
                raise ValueError("conversation turn references an unknown session")
            user_message = message_by_id.get(turn.user_message_id.value)
            if user_message is None or user_message.role is not PersistedConversationRole.USER:
                raise ValueError("conversation turn user message is missing or has wrong role")
            if user_message.turn_id != turn.turn_id:
                raise ValueError("conversation turn user message belongs to another turn")
            assistant_message = (
                message_by_id.get(turn.assistant_message_id.value)
                if turn.assistant_message_id is not None
                else None
            )
            if turn.assistant_message_id is not None:
                if (
                    assistant_message is None
                    or assistant_message.role is not PersistedConversationRole.ASSISTANT
                ):
                    raise ValueError(
                        "conversation turn assistant message is missing or has wrong role"
                    )
                if assistant_message.turn_id != turn.turn_id:
                    raise ValueError("conversation turn assistant message belongs to another turn")
            turn_messages = messages_by_turn.get(turn.turn_id.value, [])
            users = [
                message
                for message in turn_messages
                if message.role is PersistedConversationRole.USER
            ]
            assistants = [
                message
                for message in turn_messages
                if message.role is PersistedConversationRole.ASSISTANT
            ]
            if len(users) != 1 or len(assistants) > 1:
                raise ValueError("a turn requires one user and at most one assistant message")
            self._require_prior_parent(turn, turn.parent_turn_id, turn_by_id)
            derived_turn = self._require_prior_derived(
                turn,
                turn.derived_from_turn_id,
                turn_by_id,
            )
            if derived_turn is not None and turn.parent_turn_id != derived_turn.parent_turn_id:
                raise ValueError(
                    "a retry or regenerate turn must preserve its source branch parent"
                )
            if turn.state in {
                ConversationTurnState.PENDING,
                ConversationTurnState.GENERATING,
            }:
                if turn_session.state is not ConversationSessionState.ACTIVE:
                    raise ValueError("a non-terminal turn requires an active conversation session")
                non_terminal_count += 1

        if set(messages_by_turn) != set(turn_by_id):
            raise ValueError("conversation contains orphan messages or message-less turns")
        if non_terminal_count > 1:
            raise ValueError("a conversation may contain at most one non-terminal turn")

        completed_turns = [
            turn for turn in self.turns if turn.state is ConversationTurnState.COMPLETED
        ]
        if completed_turns and self.head_turn_id is None:
            raise ValueError("a conversation with completed turns requires a head")
        if self.head_turn_id is not None:
            head = turn_by_id.get(self.head_turn_id.value)
            if head is None or head.state is not ConversationTurnState.COMPLETED:
                raise ValueError("conversation head must reference a completed turn")

        if self.state in {ConversationState.ARCHIVED, ConversationState.DELETED}:
            if any(session.state is ConversationSessionState.ACTIVE for session in self.sessions):
                raise ValueError(
                    "an archived or deleted conversation cannot have an active session"
                )
            if non_terminal_count:
                raise ValueError(
                    "an archived or deleted conversation cannot have a non-terminal turn"
                )
        return self

    @staticmethod
    def _require_unique_identity(
        values: tuple[object, ...],
        attribute: str,
        label: str,
    ) -> None:
        identities: set[str] = set()
        for item in values:
            identity = getattr(item, attribute).value
            if identity in identities:
                raise ValueError(f"duplicate {label} identity")
            identities.add(identity)

    @staticmethod
    def _require_unique_sequence(
        values: tuple[ConversationTurn, ...] | tuple[PersistedConversationMessage, ...],
        label: str,
    ) -> None:
        sequences = [item.sequence for item in values]
        if len(sequences) != len(set(sequences)):
            raise ValueError(f"duplicate {label} sequence")

    def _require_conversation(self, conversation_id: ConversationId, label: str) -> None:
        if conversation_id != self.conversation_id:
            raise ValueError(f"{label} belongs to another conversation")

    @staticmethod
    def _require_prior_parent(
        turn: ConversationTurn,
        reference_id: ConversationTurnId | None,
        turn_by_id: dict[str, ConversationTurn],
    ) -> None:
        if reference_id is None:
            return
        reference = turn_by_id.get(reference_id.value)
        if reference is None:
            raise ValueError("conversation turn references an unknown parent turn")
        if reference.sequence >= turn.sequence:
            raise ValueError("conversation turn parent must precede the turn")
        if reference.state is not ConversationTurnState.COMPLETED:
            raise ValueError("conversation turn parent must be completed")

    @staticmethod
    def _require_prior_derived(
        turn: ConversationTurn,
        reference_id: ConversationTurnId | None,
        turn_by_id: dict[str, ConversationTurn],
    ) -> ConversationTurn | None:
        if reference_id is None:
            return None
        reference = turn_by_id.get(reference_id.value)
        if reference is None:
            raise ValueError("conversation turn references an unknown derived turn")
        if reference.sequence >= turn.sequence:
            raise ValueError("conversation turn derived source must precede the turn")
        if reference.state in {
            ConversationTurnState.PENDING,
            ConversationTurnState.GENERATING,
        }:
            raise ValueError("conversation turn derived source must be terminal")
        return reference


class ConversationSummary(ImmutableContract):
    scope_id: ConversationScopeId
    conversation_id: ConversationId
    state: ConversationState
    title: str | None = None
    head_turn_id: ConversationTurnId | None = None
    created_at: datetime
    updated_at: datetime
    has_active_session: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return _validate_title(value)

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_timestamp(cls, value: datetime, info: object) -> datetime:
        field_name = getattr(info, "field_name", "timestamp")
        return _require_utc(value, field_name=field_name)

    @model_validator(mode="after")
    def validate_time_order(self) -> ConversationSummary:
        if self.updated_at < self.created_at:
            raise ValueError("conversation summary updated_at precedes created_at")
        return self


def transition_session(
    session: ConversationSessionRecord,
    *,
    target: ConversationSessionState,
    finished_at: datetime,
) -> ConversationSessionRecord:
    if session.state is not ConversationSessionState.ACTIVE or target not in {
        ConversationSessionState.CLOSED,
        ConversationSessionState.INTERRUPTED,
    }:
        raise ConversationDomainError(
            code=ConversationDomainErrorCode.INVALID_TRANSITION,
            safe_message="The conversation session transition is not allowed.",
        )
    candidate = session.model_dump()
    candidate.update({"state": target, "finished_at": finished_at})
    return ConversationSessionRecord.model_validate(candidate)


def transition_turn(
    turn: ConversationTurn,
    *,
    target: ConversationTurnState,
    finished_at: datetime | None = None,
    assistant_message_id: ConversationMessageId | None = None,
    request_id: str | None = None,
    failure_reason_code: str | None = None,
    provenance: ConversationTurnProvenance | None = None,
) -> ConversationTurn:
    allowed = {
        ConversationTurnState.PENDING: {
            ConversationTurnState.GENERATING,
            ConversationTurnState.CANCELLED,
            ConversationTurnState.FAILED,
            ConversationTurnState.INTERRUPTED,
        },
        ConversationTurnState.GENERATING: {
            ConversationTurnState.COMPLETED,
            ConversationTurnState.CANCELLED,
            ConversationTurnState.FAILED,
            ConversationTurnState.INTERRUPTED,
        },
    }
    if target not in allowed.get(turn.state, set()):
        raise ConversationDomainError(
            code=ConversationDomainErrorCode.INVALID_TRANSITION,
            safe_message="The conversation turn transition is not allowed.",
        )
    terminal = target is not ConversationTurnState.GENERATING
    candidate = turn.model_dump()
    candidate.update(
        {
            "state": target,
            "finished_at": finished_at if terminal else None,
            "assistant_message_id": (
                assistant_message_id if target is ConversationTurnState.COMPLETED else None
            ),
            "request_id": request_id if request_id is not None else turn.request_id,
            "failure_reason_code": (
                failure_reason_code if target is ConversationTurnState.FAILED else None
            ),
            "provenance": (provenance if target is ConversationTurnState.COMPLETED else None),
        }
    )
    return ConversationTurn.model_validate(candidate)


def transition_conversation_state(
    snapshot: ConversationSnapshot,
    *,
    target: ConversationState,
    updated_at: datetime,
) -> ConversationSnapshot:
    if snapshot.state is target:
        raise ConversationDomainError(
            code=ConversationDomainErrorCode.INVALID_TRANSITION,
            safe_message="The conversation state transition is not allowed.",
        )
    candidate = snapshot.model_dump()
    candidate.update({"state": target, "updated_at": updated_at})
    return ConversationSnapshot.model_validate(candidate)


def project_generation_history(
    snapshot: ConversationSnapshot,
    *,
    pending_turn_id: ConversationTurnId | None = None,
) -> tuple[PersistedConversationMessage, ...]:
    """Return completed branch messages plus an optional pending user message."""

    turns = {turn.turn_id.value: turn for turn in snapshot.turns}
    messages = {message.message_id.value: message for message in snapshot.messages}
    branch: list[ConversationTurn] = []
    cursor = snapshot.head_turn_id
    visited: set[str] = set()
    while cursor is not None:
        if cursor.value in visited:
            raise ConversationDomainError(
                code=ConversationDomainErrorCode.INVARIANT_VIOLATION,
                safe_message="The conversation branch is invalid.",
            )
        visited.add(cursor.value)
        turn = turns.get(cursor.value)
        if turn is None or turn.state is not ConversationTurnState.COMPLETED:
            raise ConversationDomainError(
                code=ConversationDomainErrorCode.INVARIANT_VIOLATION,
                safe_message="The conversation branch is invalid.",
            )
        branch.append(turn)
        cursor = turn.parent_turn_id

    output: list[PersistedConversationMessage] = []
    for turn in reversed(branch):
        output.append(messages[turn.user_message_id.value])
        assert turn.assistant_message_id is not None
        output.append(messages[turn.assistant_message_id.value])

    if pending_turn_id is not None:
        pending = turns.get(pending_turn_id.value)
        if pending is None or pending.state is not ConversationTurnState.PENDING:
            raise ConversationDomainError(
                code=ConversationDomainErrorCode.INVARIANT_VIOLATION,
                safe_message="The pending conversation turn is invalid.",
            )
        output.append(messages[pending.user_message_id.value])
    return tuple(output)
