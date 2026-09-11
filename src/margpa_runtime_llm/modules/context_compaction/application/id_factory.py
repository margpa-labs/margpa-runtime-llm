"""Fresh Identity generation, isolated so tests can substitute a deterministic factory."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from ..domain.identity import (
    CompactionAttemptId,
    CompactionPlanId,
    ContextActionId,
    HandoffArtifactId,
    RecoveryIndexId,
    SnapshotId,
    StructuredContextId,
)


def _new_token() -> str:
    return uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class CompactionIdFactory:
    token_source: Callable[[], str] = _new_token

    def action_id(self) -> ContextActionId:
        return ContextActionId(value=f"action-{self.token_source()}")

    def snapshot_id(self) -> SnapshotId:
        return SnapshotId(value=f"snapshot-{self.token_source()}")

    def plan_id(self) -> CompactionPlanId:
        return CompactionPlanId(value=f"plan-{self.token_source()}")

    def attempt_id(self) -> CompactionAttemptId:
        return CompactionAttemptId(value=f"attempt-{self.token_source()}")

    def structured_context_id(self) -> StructuredContextId:
        return StructuredContextId(value=f"sctx-{self.token_source()}")

    def recovery_index_id(self) -> RecoveryIndexId:
        return RecoveryIndexId(value=f"recovery-{self.token_source()}")

    def handoff_artifact_id(self) -> HandoffArtifactId:
        return HandoffArtifactId(value=f"handoff-{self.token_source()}")
