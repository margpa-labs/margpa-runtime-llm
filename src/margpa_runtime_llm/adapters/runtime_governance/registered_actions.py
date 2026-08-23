"""Phase 4 Registered Action Adapters (P4-E-WU-002, architecture §5,
P4-CODEX-006 Rework).

Every adapter here is Local and side-effect-free at *this* layer — the
actual behavioral effect (skip the Model Call, replace the Canonical
Terminal event) is applied by the caller inspecting the returned
`ExecutedAction`, exactly like the existing Evidence Observer pattern:
this module never reaches into Conversation/Generation state itself.

Only `stop_before_generation`/`reject_output` are registered for Phase 4
MVP (`bootstrap/runtime_governance.py`) — a Caller genuinely inspects and
acts on those two. `constrain_generation_config` is intentionally *not*
registered this cycle (no Caller applies a Config Patch), and `warn`'s
real effect is that its `ExecutedAction` reaches the Evidence/Status
Subscriber pipeline (P4-CODEX-003) — never claimed `executed=True`
without that real projection.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.domain import ActionId, ExecutedAction

_INTERVENING_ACTION_IDS = frozenset(
    {ActionId.STOP_BEFORE_GENERATION.value, ActionId.REJECT_OUTPUT.value}
)


class LocalActionAdapter:
    """One stateless Adapter shared by every Phase 4 registered Action.

    `execute()` only records that the Action was Authorized/Registered
    for this Invocation; it never raises for a routine call (only a
    genuine internal fault should ever propagate, and the Action
    Resolver already treats any raised exception as `adapter_failure`,
    never as success).
    """

    def execute(self, *, action_id: str, point_id: str, stage: str) -> ExecutedAction:
        del point_id, stage
        return ExecutedAction(
            action_id=action_id,
            executed=True,
            intervening=action_id in _INTERVENING_ACTION_IDS,
        )
