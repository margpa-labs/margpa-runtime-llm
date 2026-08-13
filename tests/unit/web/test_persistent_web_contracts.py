"""Phase 2-C v2 schema, identity, and safe projection contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSnapshot,
    ConversationState,
)
from margpa_runtime_llm.modules.conversation.ports import StoredConversation
from margpa_runtime_llm.web.persistent_contracts import (
    PersistentCreateRequest,
    PersistentTurnStreamRequest,
    project_persistent_detail,
)
from margpa_runtime_llm.web.persistent_routes import _generation_identities, _operation


def valid_turn_request() -> dict[str, object]:
    return {
        "content": "hello",
        "operation_id": "action-1",
        "expected_revision": 1,
        "settings": {
            "response_language": "ja",
            "max_new_tokens": 128,
            "thinking_mode": "disabled",
            "thinking_visibility": "hidden",
            "summary_mode": "off",
            "documentation_rag_mode": "disabled",
        },
    }


@pytest.mark.parametrize(
    "field",
    ["messages", "history", "scope_id", "runtime_data_root", "path", "prompt"],
)
def test_turn_contract_forbids_full_history_scope_path_and_hidden_inputs(field: str) -> None:
    value = valid_turn_request()
    value[field] = [] if field in {"messages", "history"} else "forbidden"
    with pytest.raises(ValidationError):
        PersistentTurnStreamRequest.model_validate(value)


def test_contracts_reject_extra_malformed_blank_and_oversize_values() -> None:
    with pytest.raises(ValidationError):
        PersistentCreateRequest.model_validate(
            {"operation_id": "action", "expected_revision": None, "extra": True}
        )
    with pytest.raises(ValidationError):
        PersistentCreateRequest(operation_id="../escape")
    oversized = valid_turn_request()
    oversized["content"] = "x" * 32_769
    with pytest.raises(ValidationError):
        PersistentTurnStreamRequest.model_validate(oversized)
    blank = valid_turn_request()
    blank["content"] = "   "
    with pytest.raises(ValidationError):
        PersistentTurnStreamRequest.model_validate(blank)


def test_operation_mapping_is_deterministic_domain_separated_and_fixed_length() -> None:
    first = _operation("append", "action-1")
    assert first == _operation("append", "action-1")
    assert first != _operation("terminal", "action-1")
    identities = _generation_identities("action-1")
    values = {
        identities.turn_id.value,
        identities.user_message_id.value,
        identities.assistant_message_id.value,
        identities.append_operation_id.value,
        identities.start_operation_id.value,
        identities.terminal_operation_id.value,
    }
    assert len(values) == 6
    assert all(len(value) == 128 for value in values)
    assert all("action-1" not in value for value in values)


def test_detail_projection_excludes_scope_receipts_paths_and_hidden_data() -> None:
    now = datetime(2026, 8, 14, tzinfo=UTC)
    stored = StoredConversation(
        conversation=ConversationSnapshot(
            scope_id=ConversationScopeId(value="private-scope-sentinel"),
            conversation_id=ConversationId(value="conversation-1"),
            state=ConversationState.ACTIVE,
            created_at=now,
            updated_at=now,
        ),
        storage_format_version="sqlite-json-1",
        storage_revision=1,
        last_operation_id=ConversationOperationId(value="operation-secret"),
    )
    payload = project_persistent_detail(stored).model_dump(mode="json")
    text = str(payload)
    assert payload["storage_revision"] == 1
    assert "scope" not in text
    assert "operation" not in text
    assert "path" not in text
    assert "private-scope-sentinel" not in text
