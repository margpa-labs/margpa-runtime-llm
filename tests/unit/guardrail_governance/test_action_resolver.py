"""Guardrail Action Resolver routing order (architecture §4, ADR-5-004,
P5-D-WU-003)."""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.application import resolve_actions
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    ApprovalOutcome,
    ApprovalState,
    AuthoritySnapshot,
    DetectionOutcome,
    ExecutedAction,
    GuardDetection,
    NotExecutedReason,
    PolicyApplicability,
    PolicyDecision,
    RecommendedAction,
    Severity,
)


def _authority(*, granted: tuple[str, ...] = ()) -> AuthoritySnapshot:
    return AuthoritySnapshot(authority_revision=1, granted_action_ids=granted)


def _registry(*, registered: tuple[str, ...] = ()) -> ActionRegistrySnapshot:
    return ActionRegistrySnapshot(registry_revision=1, registered_action_ids=registered)


def _entry(action_id: ActionId, *, points: tuple[str, ...]) -> ActionRegistryEntry:
    return ActionRegistryEntry(
        action_id=action_id, allowed_points=points, side_effect_class="local"
    )


class _AlwaysNotRequiredApproval:
    def state_for(self, *, action_id: str) -> ApprovalState:
        return ApprovalState(action_id=action_id, outcome=ApprovalOutcome.NOT_REQUIRED)


class _AlwaysPendingApproval:
    def state_for(self, *, action_id: str) -> ApprovalState:
        return ApprovalState(action_id=action_id, outcome=ApprovalOutcome.PENDING)


class _RecordingAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def execute(self, *, action_id: str, point_id: str) -> ExecutedAction:
        self.calls.append((action_id, point_id))
        intervening = action_id in {
            ActionId.REJECT_INPUT.value,
            ActionId.STOP_BEFORE_GENERATION.value,
            ActionId.SUPPRESS_STREAM_CANDIDATE.value,
            ActionId.REJECT_OUTPUT.value,
            ActionId.REDACT_TYPED_SECRET.value,
            ActionId.REDACT_TYPED_PII.value,
        }
        return ExecutedAction(action_id=action_id, executed=True, intervening=intervening)


def _detection(detection_id: str, *, category_id: str = "secret") -> GuardDetection:
    return GuardDetection(
        detection_id=detection_id,
        detector_id="det1",
        category_id=category_id,
        outcome=DetectionOutcome.MATCH,
        severity=Severity.HIGH,
    )


def _policy(action_id: str) -> PolicyDecision:
    return PolicyDecision(
        policy_id="core.test",
        applicability=PolicyApplicability.APPLICABLE,
        recommended_action_ids=(action_id,),
    )


def test_mode_not_enforce_executes_nothing() -> None:
    result = resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="observe",
        detections=(),
        content_length=0,
        policy_decisions=(),
        authority=_authority(granted=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": _RecordingAdapter()},
    )
    assert len(result) == 1
    assert result[0].executed is False
    assert result[0].not_executed_reason_code == NotExecutedReason.MODE_NOT_ENFORCE.value


def test_empty_registry_or_authority_is_binding_unavailable() -> None:
    result = resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(),
        authority=_authority(),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(),
        registry={},
        adapters={},
    )
    assert result[0].not_executed_reason_code == NotExecutedReason.BINDING_UNAVAILABLE.value


def test_valid_enforce_executes_the_registered_action() -> None:
    adapter = _RecordingAdapter()
    detection = _detection("d1")
    result = resolve_actions(
        recommended_actions=(
            RecommendedAction(
                action_id="reject_output", reason_detection_id="d1", severity=Severity.HIGH
            ),
        ),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(detection,),
        content_length=10,
        policy_decisions=(_policy("reject_output"),),
        authority=_authority(granted=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": adapter},
    )
    assert result[0].executed is True
    assert adapter.calls == [("reject_output", "guardrail.output_candidate")]


def test_policy_not_applicable_blocks_execution() -> None:
    result = resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(),  # no Policy recommends reject_output
        authority=_authority(granted=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": _RecordingAdapter()},
    )
    assert result[0].not_executed_reason_code == NotExecutedReason.POLICY_NOT_APPLICABLE.value


def test_missing_authority_blocks_execution() -> None:
    result = resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(_policy("reject_output"),),
        authority=_authority(granted=("warn",)),  # reject_output not granted
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": _RecordingAdapter()},
    )
    assert result[0].not_executed_reason_code == NotExecutedReason.AUTHORITY_MISSING.value


def test_pending_approval_is_action_zero_not_approved() -> None:
    policy = PolicyDecision(
        policy_id="core.test",
        applicability=PolicyApplicability.APPLICABLE,
        approval_required=True,
        recommended_action_ids=("reject_output",),
    )
    result = resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(policy,),
        authority=_authority(granted=("reject_output",)),
        approval_port=_AlwaysPendingApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": _RecordingAdapter()},
    )
    assert result[0].not_executed_reason_code == NotExecutedReason.APPROVAL_PENDING.value


def test_unverified_span_blocks_redaction() -> None:
    detection = GuardDetection(
        detection_id="d1",
        detector_id="det1",
        category_id="secret",
        outcome=DetectionOutcome.MATCH,
        severity=Severity.HIGH,
        typed_spans=(),  # no Span at all -> never Verified
    )
    result = resolve_actions(
        recommended_actions=(
            RecommendedAction(
                action_id="redact_typed_secret", reason_detection_id="d1", severity=Severity.HIGH
            ),
        ),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(detection,),
        content_length=20,
        policy_decisions=(_policy("redact_typed_secret"),),
        authority=_authority(granted=("redact_typed_secret",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("redact_typed_secret",)),
        registry={
            "redact_typed_secret": _entry(
                ActionId.REDACT_TYPED_SECRET, points=("guardrail.output_candidate",)
            )
        },
        adapters={"redact_typed_secret": _RecordingAdapter()},
    )
    assert result[0].not_executed_reason_code == NotExecutedReason.SPAN_UNVERIFIED.value


def test_allow_and_require_approval_are_never_independently_executable() -> None:
    result = resolve_actions(
        recommended_actions=(
            RecommendedAction(action_id="allow", severity=Severity.NONE),
            RecommendedAction(action_id="require_approval", severity=Severity.MODERATE),
        ),
        point_id="guardrail.input",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(_policy("allow"),),
        authority=_authority(granted=("allow", "require_approval")),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("allow", "require_approval")),
        registry={},
        adapters={},
    )
    reasons = {item.action_id: item.not_executed_reason_code for item in result}
    assert reasons["allow"] == NotExecutedReason.NOT_EXECUTABLE_ACTION_CLASS.value
    assert reasons["require_approval"] == NotExecutedReason.NOT_EXECUTABLE_ACTION_CLASS.value


def test_two_eligible_terminal_candidates_at_equal_severity_are_unresolved() -> None:
    registry = {
        "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",)),
        "suppress_stream_candidate": _entry(
            ActionId.SUPPRESS_STREAM_CANDIDATE, points=("guardrail.output_candidate",)
        ),
    }
    result = resolve_actions(
        recommended_actions=(
            RecommendedAction(action_id="reject_output", severity=Severity.HIGH),
            RecommendedAction(action_id="suppress_stream_candidate", severity=Severity.HIGH),
        ),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(_policy("reject_output"), _policy("suppress_stream_candidate")),
        authority=_authority(granted=("reject_output", "suppress_stream_candidate")),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output", "suppress_stream_candidate")),
        registry=registry,
        adapters={
            "reject_output": _RecordingAdapter(),
            "suppress_stream_candidate": _RecordingAdapter(),
        },
    )
    reasons = {item.action_id: item.not_executed_reason_code for item in result}
    assert reasons["reject_output"] == NotExecutedReason.CONFLICT_UNRESOLVED.value
    assert reasons["suppress_stream_candidate"] == NotExecutedReason.CONFLICT_UNRESOLVED.value


def test_higher_severity_terminal_supersedes_lower_regardless_of_order() -> None:
    registry = {
        "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",)),
        "warn": _entry(ActionId.WARN, points=("guardrail.output_candidate",)),
    }
    for order in (
        ("reject_output", "warn"),
        ("warn", "reject_output"),
    ):
        recommended = tuple(
            RecommendedAction(
                action_id=action_id,
                severity=Severity.CRITICAL if action_id == "reject_output" else Severity.LOW,
            )
            for action_id in order
        )
        result = resolve_actions(
            recommended_actions=recommended,
            point_id="guardrail.output_candidate",
            mode="enforce",
            detections=(),
            content_length=0,
            policy_decisions=(_policy("reject_output"), _policy("warn")),
            authority=_authority(granted=("reject_output", "warn")),
            approval_port=_AlwaysNotRequiredApproval(),
            action_registry=_registry(registered=("reject_output", "warn")),
            registry=registry,
            adapters={"reject_output": _RecordingAdapter(), "warn": _RecordingAdapter()},
        )
        reasons = {item.action_id: item for item in result}
        assert reasons["reject_output"].executed is True
        assert reasons["warn"].not_executed_reason_code == (
            NotExecutedReason.SUPERSEDED_BY_HIGHER_PRIORITY_ACTION.value
        )


# -- P5-AUT-003/P5-CODEX-002 Rework: Synthetic Stale/Unknown/Mismatch
# Revision-Cache Matrix. The current fixed Local Provider can never
# itself *produce* a live Stale/Expired/mismatched Authority — being a
# fixed value is not a reason to leave the Negative Matrix `N/A`, so
# every scenario here is built directly against `resolve_actions()` with
# a deliberately synthetic Snapshot. --


def _resolve_reject_output(
    *,
    authority: AuthoritySnapshot,
    adapter: _RecordingAdapter,
    expected_authority_digest_sha512: str | None = None,
) -> tuple[ExecutedAction, ...]:
    return resolve_actions(
        recommended_actions=(RecommendedAction(action_id="reject_output", severity=Severity.HIGH),),
        point_id="guardrail.output_candidate",
        mode="enforce",
        detections=(),
        content_length=0,
        policy_decisions=(_policy("reject_output"),),
        authority=authority,
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry=_registry(registered=("reject_output",)),
        registry={
            "reject_output": _entry(ActionId.REJECT_OUTPUT, points=("guardrail.output_candidate",))
        },
        adapters={"reject_output": adapter},
        expected_authority_digest_sha512=expected_authority_digest_sha512,
    )


def test_authority_with_unestablished_revision_zero_fails_closed_even_when_granted() -> None:
    # Revision `0` is the "never established" sentinel (P5-AUT-003) — it
    # must never be trusted as a valid grant, even though the Action
    # nominally appears in `granted_action_ids`.
    adapter = _RecordingAdapter()
    unestablished = AuthoritySnapshot(authority_revision=0, granted_action_ids=("reject_output",))
    result = _resolve_reject_output(authority=unestablished, adapter=adapter)
    assert result[0].executed is False
    assert result[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_authority_past_its_expiry_fails_closed_even_when_granted() -> None:
    adapter = _RecordingAdapter()
    expired = AuthoritySnapshot(
        authority_revision=1,
        granted_action_ids=("reject_output",),
        expires_at="2000-01-01T00:00:00+00:00",
    )
    result = _resolve_reject_output(authority=expired, adapter=adapter)
    assert result[0].executed is False
    assert result[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_authority_with_a_future_expiry_still_executes() -> None:
    adapter = _RecordingAdapter()
    not_yet_expired = AuthoritySnapshot(
        authority_revision=1,
        granted_action_ids=("reject_output",),
        expires_at="2999-01-01T00:00:00+00:00",
    )
    result = _resolve_reject_output(authority=not_yet_expired, adapter=adapter)
    assert result[0].executed is True


def test_authority_with_a_malformed_expiry_timestamp_fails_closed() -> None:
    adapter = _RecordingAdapter()
    malformed = AuthoritySnapshot(
        authority_revision=1,
        granted_action_ids=("reject_output",),
        expires_at="not-a-real-timestamp",
    )
    result = _resolve_reject_output(authority=malformed, adapter=adapter)
    assert result[0].executed is False
    assert result[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_authority_digest_mismatch_against_an_expected_pinned_identity_fails_closed() -> None:
    # Simulates a caller that captured an Authority Identity earlier
    # (e.g. at Policy-evaluation time) and the *live* Authority Snapshot
    # passed into this same Resolution has since changed identity —
    # every candidate must fail closed, never silently resolve against
    # whichever Snapshot happened to arrive (P5-ACC-014).
    adapter = _RecordingAdapter()
    live_authority = _authority(granted=("reject_output",))
    result = _resolve_reject_output(
        authority=live_authority,
        adapter=adapter,
        expected_authority_digest_sha512="0" * 128,
    )
    assert result[0].executed is False
    assert result[0].not_executed_reason_code == NotExecutedReason.BINDING_STALE.value
    assert adapter.calls == []


def test_authority_digest_matching_the_expected_pinned_identity_still_executes() -> None:
    adapter = _RecordingAdapter()
    live_authority = _authority(granted=("reject_output",))
    result = _resolve_reject_output(
        authority=live_authority,
        adapter=adapter,
        expected_authority_digest_sha512=live_authority.digest_sha512,
    )
    assert result[0].executed is True
    assert adapter.calls == [("reject_output", "guardrail.output_candidate")]


def test_no_expected_digest_supplied_preserves_pre_existing_behavior() -> None:
    # `expected_authority_digest_sha512=None` (the default) must be a
    # true no-op — every pre-Rework caller that never supplies it keeps
    # its exact prior behavior.
    adapter = _RecordingAdapter()
    authority = _authority(granted=("reject_output",))
    result = _resolve_reject_output(authority=authority, adapter=adapter)
    assert result[0].executed is True
