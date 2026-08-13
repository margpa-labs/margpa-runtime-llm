"""P2B-PRV-001..002 and P2B-REC-003 recording-boundary evidence."""

from margpa_runtime_llm.modules.conversation.application import (
    ConversationRecordingMetadata,
    ConversationRecordingMode,
    ConversationRecordingOutcome,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationScopeId,
    ConversationTurnId,
)


def test_recording_mode_is_off_only_and_metadata_cannot_represent_sensitive_content() -> None:
    assert set(ConversationRecordingMode) == {ConversationRecordingMode.OFF}
    fields = set(ConversationRecordingMetadata.model_fields)
    forbidden = {
        "content",
        "message",
        "prompt",
        "context",
        "thinking",
        "partial",
        "hidden_original",
        "credential",
        "path",
    }
    assert fields.isdisjoint(forbidden)
    event = ConversationRecordingMetadata(
        scope_id=ConversationScopeId(value="scope-private"),
        conversation_id=ConversationId(value="conversation-1"),
        turn_id=ConversationTurnId(value="turn-1"),
        outcome=ConversationRecordingOutcome.COMPLETED,
        occurred_at_utc="2026-08-14T00:00:00+00:00",
    )
    assert forbidden.isdisjoint(event.model_dump())
