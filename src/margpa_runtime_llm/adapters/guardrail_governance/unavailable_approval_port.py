"""Unavailable Approval Port (P5-D-WU-002, P5-AUT-005, ADR-5-005).

Phase 5 has no real Human Approval UI/Channel yet. This adapter never
fabricates `approved` — it is only ever consulted by the Action Resolver
when a Policy Decision actually sets `approval_required=True` (the
Phase 5 MVP Policy mapping never does), and in that case it honestly
reports `unavailable` rather than a fabricated `not_required` or
`approved` — a request for an unimplemented Approval Channel fails
closed instead of silently granting.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.domain import ApprovalOutcome, ApprovalState


class UnavailableApprovalPort:
    def state_for(self, *, action_id: str) -> ApprovalState:
        return ApprovalState(action_id=action_id, outcome=ApprovalOutcome.UNAVAILABLE)
