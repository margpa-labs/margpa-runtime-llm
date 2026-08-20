"""Explicit local-private construction boundary for conversation persistence."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..application.conversation_generation import ConversationGenerationService
from ..application.persistent_conversation_service import PersistentConversationService
from ..application.recording import ConversationRecordingMode
from ..domain import ConversationScopeId, ConversationStorageError, ConversationStorageErrorCode
from ..ports import StorageReadiness
from .sqlite_conversation_store import (
    STORAGE_BACKEND_KIND,
    STORAGE_SCHEMA_VERSION,
    SQLiteConversationStore,
)
from .sqlite_migration import (
    CONVERSATION_TITLE_MIGRATION_STEP,
    LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,
    LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,
    TURN_CITATIONS_MIGRATION_STEP,
    SQLiteConversationMaintenance,
)

_MIGRATION_CHECKPOINT_DOMAIN = b"margpa-conversation-explicit-migration-checkpoint-v1\0"


@dataclass(frozen=True, slots=True)
class LocalConversationPersistenceSettings:
    enabled: bool = False
    runtime_data_root: Path | None = None
    scope_id: ConversationScopeId | None = None
    busy_timeout_ms: int = 5_000
    recording_mode: ConversationRecordingMode = ConversationRecordingMode.OFF
    allow_migration: bool = False

    def __post_init__(self) -> None:
        if self.enabled and (self.runtime_data_root is None or self.scope_id is None):
            raise ValueError("enabled local persistence requires an explicit root and scope")
        if self.runtime_data_root is not None and not self.runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if self.recording_mode is not ConversationRecordingMode.OFF:
            raise ValueError("Phase 2-B supports recording mode off only")
        if self.allow_migration and not self.enabled:
            raise ValueError("migration opt-in requires enabled local persistence")


@dataclass(frozen=True, slots=True)
class LocalConversationPersistence:
    enabled: bool
    store: SQLiteConversationStore | None = None
    maintenance: SQLiteConversationMaintenance | None = None
    service: PersistentConversationService | None = None
    storage_backend_kind: str | None = None
    storage_backend_version: str | None = None


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
        known_legacy_versions=(
            LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,
            LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,
        ),
    )
    service = PersistentConversationService(
        repository=store,
        bound_scope_id=settings.scope_id,
        generation_service=generation_service,
    )
    maintenance = SQLiteConversationMaintenance(
        store=store,
        steps=(TURN_CITATIONS_MIGRATION_STEP, CONVERSATION_TITLE_MIGRATION_STEP),
    )
    return LocalConversationPersistence(
        enabled=True,
        store=store,
        maintenance=maintenance,
        service=service,
        storage_backend_kind=STORAGE_BACKEND_KIND,
        storage_backend_version=store.backend_version,
    )


def start_local_conversation_persistence(
    settings: LocalConversationPersistenceSettings,
    *,
    generation_service: ConversationGenerationService,
) -> LocalConversationPersistence:
    """Explicitly initialize/open and recover one opted-in local composition.

    A store found at a known legacy storage version (`MIGRATION_REQUIRED`) is
    never migrated on a normal, unopted-in startup: doing so would silently
    mutate the user's real conversation data as a side effect of starting the
    server. Migration only runs when the caller has separately set
    `settings.allow_migration = True` (see `--conversation-persistence-migrate`
    in the CLI entrypoint), which is itself only meaningful together with
    `enabled=True`.
    """

    composition = build_local_conversation_persistence(
        settings,
        generation_service=generation_service,
    )
    if not composition.enabled:
        return composition
    assert composition.store is not None
    assert composition.service is not None
    assert composition.maintenance is not None
    readiness = composition.store.inspect_schema().readiness
    if readiness is StorageReadiness.EMPTY:
        composition.store.initialize_new_store()
    elif readiness is StorageReadiness.MIGRATION_REQUIRED:
        if not settings.allow_migration:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.MIGRATION_REQUIRED,
                safe_message=(
                    "The conversation store uses an older schema and requires an "
                    "explicit, opted-in migration before it can start. Re-run with "
                    "the migration opt-in enabled to upgrade it in place."
                ),
            )
        _run_explicit_migration(composition.store, composition.maintenance)
        composition.store.open_ready_store()
    else:
        composition.store.open_ready_store()
    composition.service.recover_incomplete_conversations()
    return composition


def _run_explicit_migration(
    store: SQLiteConversationStore,
    maintenance: SQLiteConversationMaintenance,
) -> None:
    plan = maintenance.plan_migration(STORAGE_SCHEMA_VERSION)
    checkpoint_id = hashlib.sha512(
        _MIGRATION_CHECKPOINT_DOMAIN
        + store.database_path.as_posix().encode("utf-8")
        + b"\0"
        + datetime.now(UTC).isoformat().encode("utf-8")
    ).hexdigest()
    maintenance.migrate(plan, checkpoint_id)
