"""Phase 5 Registered Guardrail Action Adapters (architecture §5,
mirrors Phase 4's `runtime_governance/registered_actions.py` pattern).

`execute()` only records that an Action was Authorized/Registered for
this Invocation — the actual behavioral effect (skip the Model Call,
replace the Canonical Terminal event, apply a Verified Redaction) is
applied by the Caller inspecting the returned `ExecutedAction`. This
module never reaches into Conversation/Generation state itself.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.domain import ActionId, ExecutedAction

_INTERVENING_ACTION_IDS = frozenset(
    {
        ActionId.REJECT_INPUT.value,
        ActionId.STOP_BEFORE_GENERATION.value,
        ActionId.SUPPRESS_STREAM_CANDIDATE.value,
        ActionId.REJECT_OUTPUT.value,
        ActionId.REDACT_TYPED_SECRET.value,
        ActionId.REDACT_TYPED_PII.value,
    }
)


class LocalGuardActionAdapter:
    """One stateless Adapter shared by every Phase 5 registered Action.

    Never raises for a routine call — the Action Resolver already
    treats any raised exception as `adapter_failure`, never success.
    """

    def execute(self, *, action_id: str, point_id: str) -> ExecutedAction:
        del point_id
        return ExecutedAction(
            action_id=action_id,
            executed=True,
            intervening=action_id in _INTERVENING_ACTION_IDS,
        )
