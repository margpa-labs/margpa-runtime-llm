"""Local Core Policy Provider (architecture §3.3, P5-D-WU-001,
P5-CODEX-001 Rework).

A fixed, Read-only, in-process mapping from Detection Category to
Recommended Action — the Phase 5 MVP Policy. `snapshot()` exposes a
Revision/Digest so a Bound Decision can be invalidated the moment this
mapping ever changes (P5-AUT-003).

`evaluate()` is Point-aware for exactly one reason (architecture
Point/Action Matrix, "context_source: exclude/reject only if explicit
policy/authority"): `guardrail.input`'s Injection/Jailbreak/
Authority-spoofing Matches recommend `reject_input` (only ever
Registered/Point-allowed at `guardrail.input`), while the identical
Categories detected at `guardrail.context_source` recommend
`stop_before_generation` instead (only ever Registered/Point-allowed at
`guardrail.context_source`) — a genuinely different Action Identity per
Point, never the same Action silently reused across Points with
different Authority/Registry scoping.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_AUTHORITY_SPOOFING,
    CATEGORY_JAILBREAK,
    CATEGORY_PII,
    CATEGORY_PROMPT_INJECTION,
    CATEGORY_SECRET,
    GUARDRAIL_CONTEXT_SOURCE_POINT_ID,
    ActionId,
    DetectionOutcome,
    GuardDetection,
    PolicyApplicability,
    PolicyDecision,
    PolicySnapshot,
)

# Category -> (recommended Action ids, Approval required). A single
# fixed Core Policy for Phase 5's Initial Freeze — a future Phase can
# make this Configuration-driven without changing this module's shape.
_CATEGORY_ACTIONS: dict[str, tuple[tuple[str, ...], bool]] = {
    CATEGORY_PROMPT_INJECTION: ((ActionId.REJECT_INPUT.value,), False),
    CATEGORY_JAILBREAK: ((ActionId.REJECT_INPUT.value,), False),
    CATEGORY_AUTHORITY_SPOOFING: ((ActionId.REJECT_INPUT.value,), False),
    CATEGORY_SECRET: ((ActionId.REDACT_TYPED_SECRET.value,), False),
    CATEGORY_PII: ((ActionId.REDACT_TYPED_PII.value,), False),
}

# `guardrail.context_source` never reuses `reject_input` — that Action
# is Registry-scoped to `guardrail.input` only, so recommending it here
# would always converge on `ACTION_NOT_ALLOWED_AT_POINT` rather than a
# genuine, explicit Policy/Authority-backed Stop. Secret/PII are
# deliberately *not* mapped here (unlike `_CATEGORY_ACTIONS` above): this
# Point has no Redaction-in-retrieved-content mechanism wired (Redaction
# needs a mutable target the caller can actually rewrite, which the
# `guardrail_context_source_hook`'s simple stop/continue shape does not
# provide) — an unmapped Category always converges on Policy `UNKNOWN`,
# never a guessed or silently-failing Action recommendation.
_CONTEXT_SOURCE_CATEGORY_ACTIONS: dict[str, tuple[tuple[str, ...], bool]] = {
    CATEGORY_PROMPT_INJECTION: ((ActionId.STOP_BEFORE_GENERATION.value,), False),
    CATEGORY_JAILBREAK: ((ActionId.STOP_BEFORE_GENERATION.value,), False),
    CATEGORY_AUTHORITY_SPOOFING: ((ActionId.STOP_BEFORE_GENERATION.value,), False),
}


class LocalPolicyProvider:
    def __init__(self, *, revision: int = 1) -> None:
        self._revision = revision

    def snapshot(self) -> PolicySnapshot:
        return PolicySnapshot(policy_revision=self._revision, profile="core")

    def evaluate(
        self, *, point_id: str, detections: tuple[GuardDetection, ...]
    ) -> tuple[PolicyDecision, ...]:
        snapshot = self.snapshot()
        category_actions = (
            _CONTEXT_SOURCE_CATEGORY_ACTIONS
            if point_id == GUARDRAIL_CONTEXT_SOURCE_POINT_ID
            else _CATEGORY_ACTIONS
        )
        decisions: list[PolicyDecision] = []
        for detection in detections:
            if detection.outcome is not DetectionOutcome.MATCH:
                decisions.append(
                    PolicyDecision(
                        policy_id=f"core.{detection.category_id}",
                        applicability=PolicyApplicability.NOT_APPLICABLE,
                        policy_revision=snapshot.policy_revision,
                        policy_digest_sha512=snapshot.digest_sha512,
                    )
                )
                continue
            mapping = category_actions.get(detection.category_id)
            if mapping is None:
                # Unknown/unmapped Category — never guessed into an
                # Action; a real Human Decision must extend the mapping
                # (P5-RES-005).
                decisions.append(
                    PolicyDecision(
                        policy_id=f"core.{detection.category_id}",
                        applicability=PolicyApplicability.UNKNOWN,
                        policy_revision=snapshot.policy_revision,
                        policy_digest_sha512=snapshot.digest_sha512,
                    )
                )
                continue
            action_ids, approval_required = mapping
            decisions.append(
                PolicyDecision(
                    policy_id=f"core.{detection.category_id}",
                    applicability=PolicyApplicability.APPLICABLE,
                    approval_required=approval_required,
                    recommended_action_ids=action_ids,
                    policy_revision=snapshot.policy_revision,
                    policy_digest_sha512=snapshot.digest_sha512,
                )
            )
        return tuple(decisions)
