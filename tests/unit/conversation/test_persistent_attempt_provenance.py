"""P6-CODEX-013 (Second Rework): a COMPLETED event's `attempt_provenance`
dict is decoded and actually persisted onto the completed `ConversationTurn`
itself — retrievable later without any second, ephemeral-log correlation —
and a missing/malformed one degrades to `None` rather than aborting Terminal
Persistence over a non-essential enrichment field.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
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
    ConversationTurnId,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")

_VALID_PROVENANCE = {
    "model_identity": "main.qwen3-4b",
    "backend_key": "llama_cpp",
    "backend_version": "b1234",
    "artifact_digest_sha512": "a" * 128,
    "context_size": 8192,
    "generation_config_digest_sha512": "d" * 128,
}


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 23, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class Session:
    def __init__(self, request_id: str, answer: str, *, attempt_provenance: object) -> None:
        self.request_id = request_id
        self.answer = answer
        self.attempt_provenance = attempt_provenance
        self.documentation_augmentation = None

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": "generating"},
        )
        data: dict[str, object] = {
            "request_id": self.request_id,
            "finish_reason": "stop",
            "assistant_message": {"role": "assistant", "content": self.answer},
        }
        if self.attempt_provenance is not None:
            data["attempt_provenance"] = self.attempt_provenance
        yield ConversationEvent(event=ConversationEventType.COMPLETED, data=data)


class Generation:
    def __init__(self, *, attempt_provenance: object) -> None:
        self.inputs: list[ConversationGenerationInput] = []
        self.attempt_provenance = attempt_provenance

    def start(self, value: ConversationGenerationInput) -> Session:
        self.inputs.append(value)
        request_id = f"request-{len(self.inputs)}"
        return Session(
            request_id, f"answer-{len(self.inputs)}", attempt_provenance=self.attempt_provenance
        )

    def cancel(self, request_id: str) -> bool:
        return False


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


def built(tmp_path: Path, *, attempt_provenance: object) -> PersistentConversationService:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = Generation(attempt_provenance=attempt_provenance)
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
    return service


def test_valid_attempt_provenance_is_persisted_on_the_completed_turn(tmp_path: Path) -> None:
    service = built(tmp_path, attempt_provenance=_VALID_PROVENANCE)
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="canonical user",
            settings=settings(),
            identities=ids("normal"),
            expected_revision=1,
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED

    stored = service.get_conversation(CID)
    turn = stored.conversation.turns[0]
    assert turn.provenance is not None
    assert turn.provenance.model_identity == "main.qwen3-4b"
    assert turn.provenance.backend_key == "llama_cpp"
    assert turn.provenance.backend_version == "b1234"
    assert turn.provenance.artifact_digest_sha512 == "a" * 128
    assert turn.provenance.context_size == 8192
    # P6-CODEX-023 (Third Rework): previously always `None` regardless of
    # what the raw event data carried, because nothing upstream ever set
    # it — now genuinely round-trips through to the stored Turn.
    assert turn.provenance.generation_config_digest_sha512 == "d" * 128


def test_missing_attempt_provenance_persists_as_none(tmp_path: Path) -> None:
    service = built(tmp_path, attempt_provenance=None)
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="canonical user",
            settings=settings(),
            identities=ids("normal"),
            expected_revision=1,
        )
    )

    stored = service.get_conversation(CID)
    assert stored.conversation.turns[0].provenance is None


def test_malformed_attempt_provenance_degrades_to_none_without_aborting_persistence(
    tmp_path: Path,
) -> None:
    malformed = {"model_identity": "main.qwen3-4b"}  # missing required fields
    service = built(tmp_path, attempt_provenance=malformed)
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="canonical user",
            settings=settings(),
            identities=ids("normal"),
            expected_revision=1,
        )
    )

    assert events[-1].event is ConversationEventType.COMPLETED
    stored = service.get_conversation(CID)
    assert stored.conversation.turns[0].provenance is None


def test_provenance_survives_a_real_store_round_trip(tmp_path: Path) -> None:
    service = built(tmp_path, attempt_provenance=_VALID_PROVENANCE)
    tuple(
        service.generate_turn(
            conversation_id=CID,
            content="canonical user",
            settings=settings(),
            identities=ids("normal"),
            expected_revision=1,
        )
    )

    reloaded_store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    reloaded_service = PersistentConversationService(
        repository=reloaded_store,
        bound_scope_id=SCOPE,
        generation_service=Generation(attempt_provenance=None),  # type: ignore[arg-type]
        clock=Clock(),
    )
    reloaded_service.recover_incomplete_conversations()
    stored = reloaded_service.get_conversation(CID)
    assert stored.conversation.turns[0].provenance is not None
    assert stored.conversation.turns[0].provenance.model_identity == "main.qwen3-4b"
