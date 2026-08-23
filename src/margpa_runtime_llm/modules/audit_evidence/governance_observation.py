"""Non-intervening Observation Port for Phase 4 Main Runtime Governance
Points (P4-EVD-001, P4-CODEX-003 Rework, mirrors `generation_observation.
py`'s established P3-CODEX-002/009 pattern exactly).

Like `GenerationObserverPort`, every method here takes plain scalar
kwargs rather than a typed Result object — `audit_evidence` is a Phase 3
module and must not depend on `runtime_governance` (Phase 4), even at
type-checking time; the caller (`bootstrap/runtime_governance.py`)
projects its own `StandardGovernanceResult` into these scalars.

An implementation MUST NOT raise, MUST NOT block the caller beyond a
small bounded local write, and a Write/Store failure inside it MUST
NEVER alter, delay, or interrupt the Governance Point's own Stop/Reject
decision — that decision is computed independently, from the same
already-evaluated Result these scalars are projected from (the Result is
evaluated exactly once and shared, never re-evaluated for Evidence's
sake, P4-CODEX-003 §"同じResultを2回評価しない").

`is_active()` is the binding-time gate a caller checks once per
Invocation, before calling `observe_point_started`/`observe_point_
terminal` at all — this is what keeps "Governance Evidence Call 0 while
off" literal (zero calls, not merely zero writes).

`status()` is the Safe Status Surface: a Write/Store failure never
alters Model/Governance behavior, but per P3-CODEX-009's established
principle it must not be silently invisible either — it becomes visible
only through this aggregate, Process-local, reason-code-only snapshot.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .domain import SafeExecutedActionRecord, SafeObservationRecord, SafeRecommendedActionRecord

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class GovernanceObserverStatus(ImmutableContract):
    degraded: bool = False
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )
    degraded_event_count: int = Field(default=0, ge=0)


@runtime_checkable
class GovernanceObserverPort(Protocol):
    def is_active(self) -> bool: ...

    def status(self) -> GovernanceObserverStatus: ...

    def observe_point_started(
        self, *, invocation_id: str, point_id: str, stage: str, mode: str
    ) -> None: ...

    def observe_point_terminal(
        self,
        *,
        invocation_id: str,
        point_id: str,
        stage: str,
        mode: str,
        execution_state: str,
        severity: str,
        selected_descriptor_ids: tuple[str, ...],
        observations: tuple[SafeObservationRecord, ...],
        recommended_actions: tuple[SafeRecommendedActionRecord, ...],
        executed_actions: tuple[SafeExecutedActionRecord, ...],
        unavailable_reason_code: str | None,
        degraded_reason_code: str | None,
        binding_digest_sha512: str | None,
        source_plan_id: str | None,
        source_plan_digest_sha512: str | None,
        capability_snapshot_digest_sha512: str | None,
        authority_snapshot_digest_sha512: str | None,
        policy_snapshot_digest_sha512: str | None,
        budget_snapshot_digest_sha512: str | None,
        action_registry_digest_sha512: str | None,
        latency_ms: int,
        call_count: int,
    ) -> None: ...
