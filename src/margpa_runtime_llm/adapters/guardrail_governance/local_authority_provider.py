"""Local Authority Provider (P5-D-WU-002).

A fixed, in-process Grant Set for this MVP — Authority is never inferred
from a Detector, Model or Definition output (ADR-5-005). A future Phase
can make this Configuration-driven without changing the Port shape.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.domain import ActionId, AuthoritySnapshot

_DEFAULT_GRANTED_ACTION_IDS = (
    ActionId.WARN.value,
    ActionId.REJECT_INPUT.value,
    ActionId.STOP_BEFORE_GENERATION.value,
    ActionId.SUPPRESS_STREAM_CANDIDATE.value,
    ActionId.REJECT_OUTPUT.value,
    ActionId.REDACT_TYPED_SECRET.value,
    ActionId.REDACT_TYPED_PII.value,
)


class LocalAuthorityProvider:
    def __init__(
        self, *, revision: int = 1, granted_action_ids: tuple[str, ...] | None = None
    ) -> None:
        self._revision = revision
        self._granted_action_ids = (
            granted_action_ids if granted_action_ids is not None else _DEFAULT_GRANTED_ACTION_IDS
        )

    def snapshot(self) -> AuthoritySnapshot:
        return AuthoritySnapshot(
            authority_revision=self._revision, granted_action_ids=self._granted_action_ids
        )


def default_authority_snapshot() -> AuthoritySnapshot:
    return LocalAuthorityProvider().snapshot()
