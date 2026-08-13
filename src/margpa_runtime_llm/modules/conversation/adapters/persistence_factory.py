"""Explicit local-private construction boundary for conversation persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..application.conversation_generation import ConversationGenerationService
from ..application.persistent_conversation_service import PersistentConversationService
from ..application.recording import ConversationRecordingMode
from ..domain import ConversationScopeId
from ..ports import StorageReadiness
from .sqlite_conversation_store import SQLiteConversationStore
from .sqlite_migration import SQLiteConversationMaintenance


@dataclass(frozen=True, slots=True)
class LocalConversationPersistenceSettings:
    enabled: bool = False
    runtime_data_root: Path | None = None
    scope_id: ConversationScopeId | None = None
    busy_timeout_ms: int = 5_000
    recording_mode: ConversationRecordingMode = ConversationRecordingMode.OFF

    def __post_init__(self) -> None:
        if self.enabled and (self.runtime_data_root is None or self.scope_id is None):
            raise ValueError("enabled local persistence requires an explicit root and scope")
        if self.runtime_data_root is not None and not self.runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if self.recording_mode is not ConversationRecordingMode.OFF:
            raise ValueError("Phase 2-B supports recording mode off only")


@dataclass(frozen=True, slots=True)
class LocalConversationPersistence:
    enabled: bool
    store: SQLiteConversationStore | None = None
    maintenance: SQLiteConversationMaintenance | None = None
    service: PersistentConversationService | None = None


def build_local_conversation_persistence(
    settings: LocalConversationPersistenceSettings,
    *,
    generation_service: ConversationGenerationService,
) -> LocalConversationPersistence:
    """Build objects only; never initialize or open the filesystem store."""

    if not settings.enabled:
        return LocalConversationPersistence(enabled=False)
    assert settings.runtime_data_root is not None
    assert settings.scope_id is not None
    store = SQLiteConversationStore(
        runtime_data_root=settings.runtime_data_root,
        bound_scope_id=settings.scope_id,
        busy_timeout_ms=settings.busy_timeout_ms,
    )
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=settings.scope_id,
        generation_service=generation_service,
    )
    maintenance = SQLiteConversationMaintenance(store=store)
    return LocalConversationPersistence(
        enabled=True,
        store=store,
        maintenance=maintenance,
        service=service,
    )


def start_local_conversation_persistence(
    settings: LocalConversationPersistenceSettings,
    *,
    generation_service: ConversationGenerationService,
) -> LocalConversationPersistence:
    """Explicitly initialize/open and recover one opted-in local composition."""

    composition = build_local_conversation_persistence(
        settings,
        generation_service=generation_service,
    )
    if not composition.enabled:
        return composition
    assert composition.store is not None
    assert composition.service is not None
    readiness = composition.store.inspect_schema().readiness
    if readiness is StorageReadiness.EMPTY:
        composition.store.initialize_new_store()
    elif readiness is StorageReadiness.READY:
        composition.store.open_ready_store()
    else:
        composition.store.open_ready_store()
    composition.service.recover_incomplete_conversations()
    return composition
