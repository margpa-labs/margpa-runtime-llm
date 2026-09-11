"""Local Filesystem `CompactionStorePort` implementation (Phase 9-3, CL-P9-3-B).

One JSON envelope per persisted object under `base_dir`:

    <base_dir>/snapshots/<snapshot_id>.json
    <base_dir>/plans/<plan_id>.json
    <base_dir>/attempts/<attempt_id>.json
    <base_dir>/structured_context/<structured_context_id>.json
    <base_dir>/active_projection/<branch_id>.json
    <base_dir>/activation_records/<attempt_id>__<result>__<counter>.json
    <base_dir>/recovery_index/<recovery_index_id>.json
    <base_dir>/handoff/<handoff_artifact_id>.json

Every write is temp-file-then-`Path.replace` (POSIX-atomic on the same
filesystem). Every envelope carries an explicit `schema_version` (the
Artifact's own Pydantic `schema_version` field) and a `digest_sha512` of the
canonical (sorted-key, no-whitespace) serialized body, computed and stored
at write time and re-verified at every read (Canonical Design SS8.4/
Mandatory Hard Evidence #11). A digest mismatch, an unreadable/corrupt
envelope or an unrecognized `schema_version` raises a typed
`ContextCompactionDomainError` -- never a silent best-effort decode and
never a value fabricated in its place.

`compare_and_swap_active_context_projection` holds `self._lock` across its
own read-compare-write sequence (not just the final write), so no other
in-process caller's CAS or plain read can interleave between the compare
and the write -- exactly the invariant SS9's "二重Publish...を拒否する"
depends on for same-process concurrent Attempts.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from threading import Lock
from typing import Any

from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    TERMINAL_ATTEMPT_STATES,
    ActivationRecord,
    ActiveContextProjection,
    CompactionAttempt,
    CompactionPlan,
    ContextHandoffArtifact,
    PreActionSnapshot,
    RecoveryIndex,
    StructuredContextArtifact,
)
from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
    ContextCompactionDomainErrorCode,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import (
    CompactionAttemptId,
    CompactionPlanId,
    ContextBranchId,
    HandoffArtifactId,
    RecoveryIndexId,
    SnapshotId,
    StructuredContextId,
)
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _safe_file_name(identifier: str, *, kind: str) -> str:
    if not _SAFE_ID_PATTERN.match(identifier):
        raise ContextCompactionDomainError(
            code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
            safe_message=f"unsafe {kind} for a store file name",
        )
    return f"{identifier}.json"


def _canonical_bytes(body: dict[str, Any]) -> bytes:
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


class LocalFilesystemCompactionStore:
    def __init__(self, *, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._lock = Lock()

    def _write_envelope(self, sub_dir: str, file_name: str, body: dict[str, Any]) -> None:
        directory = self._base_dir / sub_dir
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / file_name
        tmp = directory / f".{file_name}.tmp"
        envelope = {
            "schema_version": body.get("schema_version", "1"),
            "digest_sha512": hashlib.sha512(_canonical_bytes(body)).hexdigest(),
            "body": body,
        }
        data = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._lock:
            tmp.write_text(data, encoding="utf-8")
            tmp.replace(target)

    def _read_envelope(self, sub_dir: str, file_name: str) -> dict[str, Any] | None:
        target = self._base_dir / sub_dir / file_name
        if not target.is_file():
            return None
        try:
            envelope: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The stored Compaction Artifact could not be read.",
            ) from exc
        body = envelope.get("body")
        digest = envelope.get("digest_sha512")
        if not isinstance(body, dict) or not isinstance(digest, str):
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The stored Compaction Artifact envelope is malformed.",
            )
        if hashlib.sha512(_canonical_bytes(body)).hexdigest() != digest:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_DIGEST_MISMATCH,
                safe_message="The stored Compaction Artifact failed Digest verification.",
            )
        if envelope.get("schema_version") != body.get("schema_version", "1"):
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.UNKNOWN_SCHEMA_VERSION,
                safe_message="The stored Compaction Artifact schema version is inconsistent.",
            )
        return body

    # -- Pre-action Snapshot ------------------------------------------------

    def save_pre_action_snapshot(self, snapshot: PreActionSnapshot) -> None:
        file_name = _safe_file_name(snapshot.snapshot_id.value, kind="snapshot_id")
        self._write_envelope("snapshots", file_name, snapshot.model_dump(mode="json"))

    def load_pre_action_snapshot(self, snapshot_id: SnapshotId) -> PreActionSnapshot | None:
        file_name = _safe_file_name(snapshot_id.value, kind="snapshot_id")
        body = self._read_envelope("snapshots", file_name)
        return None if body is None else PreActionSnapshot.model_validate(body)

    # -- Compaction Plan ------------------------------------------------------

    def save_compaction_plan(self, plan: CompactionPlan) -> None:
        file_name = _safe_file_name(plan.plan_id.value, kind="plan_id")
        self._write_envelope("plans", file_name, plan.model_dump(mode="json"))

    def load_compaction_plan(self, plan_id: CompactionPlanId) -> CompactionPlan | None:
        file_name = _safe_file_name(plan_id.value, kind="plan_id")
        body = self._read_envelope("plans", file_name)
        return None if body is None else CompactionPlan.model_validate(body)

    # -- Compaction Attempt -----------------------------------------------------

    def save_compaction_attempt(self, attempt: CompactionAttempt) -> None:
        file_name = _safe_file_name(attempt.attempt_id.value, kind="attempt_id")
        self._write_envelope("attempts", file_name, attempt.model_dump(mode="json"))

    def load_compaction_attempt(
        self, attempt_id: CompactionAttemptId
    ) -> CompactionAttempt | None:
        file_name = _safe_file_name(attempt_id.value, kind="attempt_id")
        body = self._read_envelope("attempts", file_name)
        return None if body is None else CompactionAttempt.model_validate(body)

    def list_non_terminal_attempts(
        self, conversation_id: ConversationId, branch_id: ContextBranchId
    ) -> tuple[CompactionAttempt, ...]:
        directory = self._base_dir / "attempts"
        if not directory.is_dir():
            return ()
        found: list[CompactionAttempt] = []
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("."):
                continue
            body = self._read_envelope("attempts", path.name)
            if body is None:
                continue
            attempt = CompactionAttempt.model_validate(body)
            if (
                attempt.conversation_id == conversation_id
                and attempt.branch_id == branch_id
                and attempt.state not in TERMINAL_ATTEMPT_STATES
            ):
                found.append(attempt)
        return tuple(found)

    # -- Structured Context Artifact --------------------------------------------

    def save_structured_context_artifact(self, artifact: StructuredContextArtifact) -> None:
        file_name = _safe_file_name(
            artifact.structured_context_id.value, kind="structured_context_id"
        )
        self._write_envelope("structured_context", file_name, artifact.model_dump(mode="json"))

    def load_structured_context_artifact(
        self, structured_context_id: StructuredContextId
    ) -> StructuredContextArtifact | None:
        file_name = _safe_file_name(structured_context_id.value, kind="structured_context_id")
        body = self._read_envelope("structured_context", file_name)
        return None if body is None else StructuredContextArtifact.model_validate(body)

    # -- Active Context Projection (CAS pointer) --------------------------------

    def load_active_context_projection(
        self, conversation_id: ConversationId, branch_id: ContextBranchId
    ) -> ActiveContextProjection | None:
        file_name = _safe_file_name(branch_id.value, kind="branch_id")
        body = self._read_envelope("active_projection", file_name)
        if body is None:
            return None
        projection = ActiveContextProjection.model_validate(body)
        if projection.conversation_id != conversation_id:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message=(
                    "The stored Active Context Projection belongs to another conversation."
                ),
            )
        return projection

    def compare_and_swap_active_context_projection(
        self,
        *,
        conversation_id: ConversationId,
        branch_id: ContextBranchId,
        expected_active_projection_revision: int,
        new_projection: ActiveContextProjection,
    ) -> bool:
        if (
            new_projection.conversation_id != conversation_id
            or new_projection.branch_id != branch_id
        ):
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.INVALID_LIFECYCLE,
                safe_message=(
                    "The new Active Context Projection targets a different Conversation/Branch."
                ),
            )
        file_name = _safe_file_name(branch_id.value, kind="branch_id")
        directory = self._base_dir / "active_projection"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / file_name
        with self._lock:
            current_revision = 0
            if target.is_file():
                current_body = self._read_locked_envelope(target)
                current = ActiveContextProjection.model_validate(current_body)
                if current.conversation_id != conversation_id:
                    raise ContextCompactionDomainError(
                        code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                        safe_message=(
                            "The stored Active Context Projection belongs to another conversation."
                        ),
                    )
                current_revision = current.active_projection_revision
            if current_revision != expected_active_projection_revision:
                return False
            body = new_projection.model_dump(mode="json")
            envelope = {
                "schema_version": body.get("schema_version", "1"),
                "digest_sha512": hashlib.sha512(_canonical_bytes(body)).hexdigest(),
                "body": body,
            }
            data = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            tmp = directory / f".{file_name}.tmp"
            tmp.write_text(data, encoding="utf-8")
            tmp.replace(target)
            return True

    def _read_locked_envelope(self, target: Path) -> dict[str, Any]:
        """Same verification as `_read_envelope`, callable while `self._lock`
        is already held (the public method would deadlock re-acquiring it)."""

        try:
            envelope: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The stored Active Context Projection could not be read.",
            ) from exc
        body = envelope.get("body")
        digest = envelope.get("digest_sha512")
        if not isinstance(body, dict) or not isinstance(digest, str):
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT,
                safe_message="The stored Active Context Projection envelope is malformed.",
            )
        if hashlib.sha512(_canonical_bytes(body)).hexdigest() != digest:
            raise ContextCompactionDomainError(
                code=ContextCompactionDomainErrorCode.ARTIFACT_DIGEST_MISMATCH,
                safe_message="The stored Active Context Projection failed Digest verification.",
            )
        return body

    # -- Activation Record (append-only Evidence) -------------------------------

    def save_activation_record(self, record: ActivationRecord) -> None:
        with self._lock:
            directory = self._base_dir / "activation_records"
            directory.mkdir(parents=True, exist_ok=True)
            existing = len(list(directory.glob(f"{record.attempt_id.value}__*.json")))
        file_name = _safe_file_name(
            f"{record.attempt_id.value}__{record.result.value}__{existing}",
            kind="activation_record",
        )
        self._write_envelope("activation_records", file_name, record.model_dump(mode="json"))

    # -- Recovery Index -----------------------------------------------------------

    def save_recovery_index(self, index: RecoveryIndex) -> None:
        file_name = _safe_file_name(index.recovery_index_id.value, kind="recovery_index_id")
        self._write_envelope("recovery_index", file_name, index.model_dump(mode="json"))

    def load_recovery_index(self, recovery_index_id: RecoveryIndexId) -> RecoveryIndex | None:
        file_name = _safe_file_name(recovery_index_id.value, kind="recovery_index_id")
        body = self._read_envelope("recovery_index", file_name)
        return None if body is None else RecoveryIndex.model_validate(body)

    # -- Context Handoff Artifact ---------------------------------------------------

    def save_handoff_artifact(self, artifact: ContextHandoffArtifact) -> None:
        file_name = _safe_file_name(
            artifact.handoff_artifact_id.value, kind="handoff_artifact_id"
        )
        self._write_envelope("handoff", file_name, artifact.model_dump(mode="json"))

    def load_handoff_artifact(
        self, handoff_artifact_id: HandoffArtifactId
    ) -> ContextHandoffArtifact | None:
        file_name = _safe_file_name(handoff_artifact_id.value, kind="handoff_artifact_id")
        body = self._read_envelope("handoff", file_name)
        return None if body is None else ContextHandoffArtifact.model_validate(body)
