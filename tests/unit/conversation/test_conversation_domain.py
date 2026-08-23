from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.conversation.domain import (
    ConversationDomainError,
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
    ConversationTurnOrigin,
    ConversationTurnState,
    PersistedConversationMessage,
    PersistedConversationRole,
    project_generation_history,
    transition_conversation_state,
    transition_session,
    transition_turn,
)

NOW = datetime(2026, 8, 12, 0, 0, tzinfo=UTC)


def scope(value: str = "scope-1") -> ConversationScopeId:
    return ConversationScopeId(value=value)


def conversation_id(value: str = "conversation-1") -> ConversationId:
    return ConversationId(value=value)


def session_id(value: str = "session-1") -> ConversationSessionId:
    return ConversationSessionId(value=value)


def turn_id(value: str = "turn-1") -> ConversationTurnId:
    return ConversationTurnId(value=value)


def message_id(value: str) -> ConversationMessageId:
    return ConversationMessageId(value=value)


def session(
    *,
    state: ConversationSessionState = ConversationSessionState.ACTIVE,
    identity: str = "session-1",
) -> ConversationSessionRecord:
    finished_at = None if state is ConversationSessionState.ACTIVE else NOW + timedelta(seconds=5)
    return ConversationSessionRecord(
        session_id=session_id(identity),
        conversation_id=conversation_id(),
        state=state,
        opened_at=NOW,
        finished_at=finished_at,
    )


def message(
    identity: str,
    *,
    turn_identity: str,
    sequence: int,
    role: PersistedConversationRole,
    content: str,
) -> PersistedConversationMessage:
    return PersistedConversationMessage(
        message_id=message_id(identity),
        conversation_id=conversation_id(),
        turn_id=turn_id(turn_identity),
        sequence=sequence,
        role=role,
        content=content,
        created_at=NOW + timedelta(seconds=sequence),
    )


def completed_turn(
    identity: str = "turn-1",
    *,
    sequence: int = 0,
    parent: str | None = None,
    derived: str | None = None,
    origin: ConversationTurnOrigin = ConversationTurnOrigin.NORMAL,
    session_identity: str = "session-1",
) -> ConversationTurn:
    return ConversationTurn(
        turn_id=turn_id(identity),
        conversation_id=conversation_id(),
        session_id=session_id(session_identity),
        sequence=sequence,
        state=ConversationTurnState.COMPLETED,
        origin=origin,
        parent_turn_id=turn_id(parent) if parent else None,
        derived_from_turn_id=turn_id(derived) if derived else None,
        user_message_id=message_id(f"{identity}-user"),
        assistant_message_id=message_id(f"{identity}-assistant"),
        request_id=f"request-{identity}",
        started_at=NOW + timedelta(seconds=sequence * 10),
        finished_at=NOW + timedelta(seconds=sequence * 10 + 5),
    )


def pending_turn(
    identity: str,
    *,
    sequence: int,
    parent: str | None,
    derived: str | None = None,
    origin: ConversationTurnOrigin = ConversationTurnOrigin.NORMAL,
) -> ConversationTurn:
    return ConversationTurn(
        turn_id=turn_id(identity),
        conversation_id=conversation_id(),
        session_id=session_id(),
        sequence=sequence,
        state=ConversationTurnState.PENDING,
        origin=origin,
        parent_turn_id=turn_id(parent) if parent else None,
        derived_from_turn_id=turn_id(derived) if derived else None,
        user_message_id=message_id(f"{identity}-user"),
        started_at=NOW + timedelta(seconds=sequence * 10),
    )


def turn_messages(
    identity: str,
    *,
    turn_sequence: int,
    assistant: bool,
) -> tuple[PersistedConversationMessage, ...]:
    messages = [
        message(
            f"{identity}-user",
            turn_identity=identity,
            sequence=turn_sequence * 2,
            role=PersistedConversationRole.USER,
            content=f"user {identity}",
        )
    ]
    if assistant:
        messages.append(
            message(
                f"{identity}-assistant",
                turn_identity=identity,
                sequence=turn_sequence * 2 + 1,
                role=PersistedConversationRole.ASSISTANT,
                content=f"assistant {identity}",
            )
        )
    return tuple(messages)


def snapshot(
    *,
    turns: tuple[ConversationTurn, ...] = (),
    messages: tuple[PersistedConversationMessage, ...] = (),
    head: str | None = None,
    sessions: tuple[ConversationSessionRecord, ...] | None = None,
    state: ConversationState = ConversationState.ACTIVE,
) -> ConversationSnapshot:
    return ConversationSnapshot(
        scope_id=scope(),
        conversation_id=conversation_id(),
        state=state,
        head_turn_id=turn_id(head) if head else None,
        created_at=NOW,
        updated_at=NOW + timedelta(minutes=1),
        sessions=(session(),) if sessions is None else sessions,
        turns=turns,
        messages=messages,
    )


@pytest.mark.parametrize(
    "identifier_type",
    [
        ConversationScopeId,
        ConversationId,
        ConversationSessionId,
        ConversationTurnId,
        ConversationMessageId,
    ],
)
@pytest.mark.parametrize("value", ["", " ", "unsafe/value", "a" * 129])
def test_identifiers_reject_invalid_values(identifier_type: type, value: str) -> None:
    with pytest.raises(ValidationError):
        identifier_type(value=value)


def test_identifier_types_remain_distinct() -> None:
    conversation = ConversationId(value="same")
    session_value = ConversationSessionId(value="same")
    assert conversation.__class__.__name__ != session_value.__class__.__name__


def test_persisted_message_rejects_unknown_fields_and_non_utc_time() -> None:
    payload = message(
        "turn-1-user",
        turn_identity="turn-1",
        sequence=0,
        role=PersistedConversationRole.USER,
        content="hello",
    ).model_dump()
    payload["unknown"] = True
    with pytest.raises(ValidationError):
        PersistedConversationMessage.model_validate(payload)

    payload.pop("unknown")
    payload["created_at"] = datetime(2026, 8, 12, 0, 0)
    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        PersistedConversationMessage.model_validate(payload)

    payload["created_at"] = datetime(
        2026,
        8,
        12,
        9,
        0,
        tzinfo=timezone(timedelta(hours=9)),
    )
    with pytest.raises(ValidationError, match="timezone-aware UTC"):
        PersistedConversationMessage.model_validate(payload)


def test_persisted_message_roles_make_hidden_content_categories_unrepresentable() -> None:
    assert set(PersistedConversationRole) == {
        PersistedConversationRole.USER,
        PersistedConversationRole.ASSISTANT,
    }
    with pytest.raises(ValidationError):
        PersistedConversationMessage.model_validate(
            {
                "message_id": message_id("message-1"),
                "conversation_id": conversation_id(),
                "turn_id": turn_id(),
                "sequence": 0,
                "role": "system",
                "content": "hidden prompt",
                "created_at": NOW,
            }
        )


def test_turn_state_shape_is_strict() -> None:
    payload = completed_turn().model_dump()
    payload["assistant_message_id"] = None
    with pytest.raises(ValidationError, match="completed turn requires"):
        ConversationTurn.model_validate(payload)

    payload = pending_turn("turn-2", sequence=1, parent=None).model_dump()
    payload["finished_at"] = NOW
    with pytest.raises(ValidationError, match="non-terminal"):
        ConversationTurn.model_validate(payload)


def test_retry_and_regenerate_require_a_source_turn() -> None:
    payload = pending_turn("turn-2", sequence=1, parent=None).model_dump()
    payload["origin"] = ConversationTurnOrigin.REGENERATE
    with pytest.raises(ValidationError, match="requires derived_from_turn_id"):
        ConversationTurn.model_validate(payload)


def test_aggregate_accepts_completed_branch_and_pending_regenerate() -> None:
    first = completed_turn()
    regenerate = pending_turn(
        "turn-2",
        sequence=1,
        parent=None,
        derived="turn-1",
        origin=ConversationTurnOrigin.REGENERATE,
    )
    aggregate = snapshot(
        turns=(first, regenerate),
        messages=turn_messages("turn-1", turn_sequence=0, assistant=True)
        + turn_messages("turn-2", turn_sequence=1, assistant=False),
        head="turn-1",
    )
    projected = project_generation_history(aggregate, pending_turn_id=turn_id("turn-2"))
    assert [item.role for item in projected] == [
        PersistedConversationRole.USER,
        PersistedConversationRole.ASSISTANT,
        PersistedConversationRole.USER,
    ]
    assert projected[-1].turn_id == turn_id("turn-2")


def test_completed_turn_requires_an_explicit_conversation_head() -> None:
    first = completed_turn()
    with pytest.raises(ValidationError, match="requires a head"):
        snapshot(
            turns=(first,),
            messages=turn_messages("turn-1", turn_sequence=0, assistant=True),
        )


def test_retry_can_derive_from_a_failed_turn_but_preserves_branch_parent() -> None:
    first = completed_turn()
    failed_payload = pending_turn("turn-2", sequence=1, parent="turn-1").model_dump()
    failed_payload.update(
        {
            "state": ConversationTurnState.FAILED,
            "finished_at": NOW + timedelta(seconds=15),
        }
    )
    failed = ConversationTurn.model_validate(failed_payload)
    retry = pending_turn(
        "turn-3",
        sequence=2,
        parent="turn-1",
        derived="turn-2",
        origin=ConversationTurnOrigin.RETRY,
    )
    aggregate = snapshot(
        turns=(first, failed, retry),
        messages=turn_messages("turn-1", turn_sequence=0, assistant=True)
        + turn_messages("turn-2", turn_sequence=1, assistant=False)
        + turn_messages("turn-3", turn_sequence=2, assistant=False),
        head="turn-1",
    )
    assert aggregate.turns[-1].derived_from_turn_id == turn_id("turn-2")

    invalid_payload = retry.model_dump()
    invalid_payload["parent_turn_id"] = None
    invalid_retry = ConversationTurn.model_validate(invalid_payload)
    with pytest.raises(ValidationError, match="preserve its source branch parent"):
        snapshot(
            turns=(first, failed, invalid_retry),
            messages=turn_messages("turn-1", turn_sequence=0, assistant=True)
            + turn_messages("turn-2", turn_sequence=1, assistant=False)
            + turn_messages("turn-3", turn_sequence=2, assistant=False),
            head="turn-1",
        )


def test_failed_cancelled_and_interrupted_turns_are_not_projected() -> None:
    first = completed_turn()
    failed_payload = pending_turn("turn-2", sequence=1, parent="turn-1").model_dump()
    failed_payload.update(
        {
            "state": ConversationTurnState.FAILED,
            "finished_at": NOW + timedelta(seconds=15),
        }
    )
    failed = ConversationTurn.model_validate(failed_payload)
    aggregate = snapshot(
        turns=(first, failed),
        messages=turn_messages("turn-1", turn_sequence=0, assistant=True)
        + turn_messages("turn-2", turn_sequence=1, assistant=False),
        head="turn-1",
    )
    projected = project_generation_history(aggregate)
    assert [item.turn_id.value for item in projected] == ["turn-1", "turn-1"]


@pytest.mark.parametrize(
    "mutation, match",
    [
        ({"head_turn_id": {"value": "missing"}}, "head"),
        ({"messages": ()}, "missing or has wrong role"),
    ],
)
def test_aggregate_rejects_missing_references(mutation: dict[str, object], match: str) -> None:
    first = completed_turn()
    payload = snapshot(
        turns=(first,),
        messages=turn_messages("turn-1", turn_sequence=0, assistant=True),
        head="turn-1",
    ).model_dump()
    payload.update(mutation)
    with pytest.raises(ValidationError, match=match):
        ConversationSnapshot.model_validate(payload)


def test_aggregate_rejects_cross_conversation_and_duplicate_sequence() -> None:
    first = completed_turn()
    messages = list(turn_messages("turn-1", turn_sequence=0, assistant=True))
    wrong = messages[0].model_dump()
    wrong["conversation_id"] = {"value": "conversation-other"}
    messages[0] = PersistedConversationMessage.model_validate(wrong)
    with pytest.raises(ValidationError, match="another conversation"):
        snapshot(turns=(first,), messages=tuple(messages), head="turn-1")

    duplicate = messages[1].model_dump()
    duplicate["conversation_id"] = {"value": "conversation-1"}
    duplicate["sequence"] = messages[0].sequence
    messages[1] = PersistedConversationMessage.model_validate(duplicate)
    with pytest.raises(ValidationError, match="duplicate message sequence"):
        snapshot(turns=(first,), messages=tuple(messages), head="turn-1")


def test_non_terminal_turn_requires_active_session() -> None:
    pending = pending_turn("turn-1", sequence=0, parent=None)
    with pytest.raises(ValidationError, match="active conversation session"):
        snapshot(
            turns=(pending,),
            messages=turn_messages("turn-1", turn_sequence=0, assistant=False),
            sessions=(session(state=ConversationSessionState.CLOSED),),
        )


def test_archived_conversation_rejects_active_children() -> None:
    with pytest.raises(ValidationError, match="active session"):
        snapshot(state=ConversationState.ARCHIVED)


def test_deleted_conversation_rejects_active_children() -> None:
    with pytest.raises(ValidationError, match="active session"):
        snapshot(state=ConversationState.DELETED)


@pytest.mark.parametrize(
    "value",
    ["", "   ", " leading space", "trailing space ", "x" * 201, "bad\ttab", "bad\nnewline"],
)
def test_conversation_title_rejects_invalid_shapes(value: str) -> None:
    with pytest.raises(ValidationError):
        ConversationSnapshot.model_validate(
            snapshot(sessions=(session(state=ConversationSessionState.CLOSED),))
            .model_copy(update={"title": value})
            .model_dump()
        )


def test_conversation_title_accepts_none_and_trimmed_value() -> None:
    base = snapshot(sessions=(session(state=ConversationSessionState.CLOSED),))
    assert base.title is None
    titled = ConversationSnapshot.model_validate(
        base.model_copy(update={"title": "My renamed chat"}).model_dump()
    )
    assert titled.title == "My renamed chat"


def test_transitions_validate_terminal_state_and_times() -> None:
    active_session = session()
    closed = transition_session(
        active_session,
        target=ConversationSessionState.CLOSED,
        finished_at=NOW + timedelta(seconds=1),
    )
    assert closed.state is ConversationSessionState.CLOSED
    with pytest.raises(ConversationDomainError):
        transition_session(
            closed,
            target=ConversationSessionState.INTERRUPTED,
            finished_at=NOW + timedelta(seconds=2),
        )

    pending = pending_turn("turn-1", sequence=0, parent=None)
    generating = transition_turn(
        pending,
        target=ConversationTurnState.GENERATING,
        request_id="request-1",
    )
    completed = transition_turn(
        generating,
        target=ConversationTurnState.COMPLETED,
        assistant_message_id=message_id("turn-1-assistant"),
        finished_at=NOW + timedelta(seconds=2),
    )
    assert completed.state is ConversationTurnState.COMPLETED
    with pytest.raises(ConversationDomainError):
        transition_turn(completed, target=ConversationTurnState.FAILED)


def test_failed_transition_carries_failure_reason_code_completed_does_not() -> None:
    pending = pending_turn("turn-1", sequence=0, parent=None)
    generating = transition_turn(
        pending,
        target=ConversationTurnState.GENERATING,
        request_id="request-1",
    )
    failed = transition_turn(
        generating,
        target=ConversationTurnState.FAILED,
        finished_at=NOW + timedelta(seconds=1),
        failure_reason_code="guardrail_reject_input",
    )
    assert failed.failure_reason_code == "guardrail_reject_input"

    generating_again = transition_turn(
        pending_turn("turn-2", sequence=0, parent=None),
        target=ConversationTurnState.GENERATING,
        request_id="request-2",
    )
    completed = transition_turn(
        generating_again,
        target=ConversationTurnState.COMPLETED,
        assistant_message_id=message_id("turn-2-assistant"),
        finished_at=NOW + timedelta(seconds=1),
        failure_reason_code="guardrail_reject_input",
    )
    assert completed.failure_reason_code is None


def test_conversation_archive_transition_revalidates_invariants() -> None:
    current = snapshot(sessions=(session(state=ConversationSessionState.CLOSED),))
    archived = transition_conversation_state(
        current,
        target=ConversationState.ARCHIVED,
        updated_at=NOW + timedelta(minutes=2),
    )
    assert archived.state is ConversationState.ARCHIVED

    with pytest.raises(ValidationError, match="active session"):
        transition_conversation_state(
            snapshot(),
            target=ConversationState.ARCHIVED,
            updated_at=NOW + timedelta(minutes=2),
        )


def test_conversation_delete_transition_revalidates_invariants() -> None:
    current = snapshot(sessions=(session(state=ConversationSessionState.CLOSED),))
    deleted = transition_conversation_state(
        current,
        target=ConversationState.DELETED,
        updated_at=NOW + timedelta(minutes=2),
    )
    assert deleted.state is ConversationState.DELETED

    with pytest.raises(ValidationError, match="active session"):
        transition_conversation_state(
            snapshot(),
            target=ConversationState.DELETED,
            updated_at=NOW + timedelta(minutes=2),
        )


def test_projection_rejects_non_pending_extra_turn() -> None:
    first = completed_turn()
    aggregate = snapshot(
        turns=(first,),
        messages=turn_messages("turn-1", turn_sequence=0, assistant=True),
        head="turn-1",
    )
    with pytest.raises(ConversationDomainError):
        project_generation_history(aggregate, pending_turn_id=turn_id("turn-1"))
