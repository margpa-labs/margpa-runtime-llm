"""Guardrail Point Runtime Mode routing (P5-MOD-002..004, P5-CODEX-007
Rework)."""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.application import GuardrailPointRuntime
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    ApprovalOutcome,
    ApprovalState,
    AuthoritySnapshot,
    DetectionOutcome,
    DetectorRegistrySnapshot,
    ExecutedAction,
    ExecutionState,
    GuardDetection,
    PolicyApplicability,
    PolicyDecision,
    PolicySnapshot,
    Severity,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import GuardActionAdapterPort


class _FixedProvider[T]:
    """Generic `.snapshot() -> T` Provider returning the same fixed
    value every call — the common-case Fake for a Provider whose live
    value never actually changes across a test."""

    def __init__(self, snapshot: T) -> None:
        self._snapshot = snapshot

    def snapshot(self) -> T:
        return self._snapshot


class _AlwaysNotRequiredApproval:
    def state_for(self, *, action_id: str) -> ApprovalState:
        return ApprovalState(action_id=action_id, outcome=ApprovalOutcome.NOT_REQUIRED)


class _RecordingDetector:
    max_match_length = 0

    def __init__(self, *, detection: GuardDetection) -> None:
        self.detector_id = detection.detector_id
        self._detection = detection
        self.calls = 0

    def detect(self, *, content: str) -> GuardDetection:
        self.calls += 1
        return self._detection


class _ExplodingDetector:
    detector_id = "exploding"
    max_match_length = 0

    def detect(self, *, content: str) -> GuardDetection:
        raise AssertionError("Detector must never be called in OFF mode")


class _EchoPolicyProvider:
    """Recommends `reject_output` for any MATCH Detection, else not_applicable.

    Stamps every `PolicyDecision` with its own live `snapshot()`'s
    Revision/Digest (P5-CODEX-007 Rework) — mirrors `LocalPolicyProvider`
    exactly, so the Entry Binding's Policy-Decision-Stamp cross-check
    passes for a genuinely well-behaved Provider."""

    def __init__(self, *, policy_revision: int = 1) -> None:
        self._policy_revision = policy_revision

    def snapshot(self) -> PolicySnapshot:
        return PolicySnapshot(policy_revision=self._policy_revision, profile="core")

    def evaluate(
        self, *, point_id: str, detections: tuple[GuardDetection, ...]
    ) -> tuple[PolicyDecision, ...]:
        snapshot = self.snapshot()
        decisions: list[PolicyDecision] = []
        for detection in detections:
            if detection.outcome is DetectionOutcome.MATCH:
                decisions.append(
                    PolicyDecision(
                        policy_id=f"core.{detection.category_id}",
                        applicability=PolicyApplicability.APPLICABLE,
                        recommended_action_ids=("reject_output",),
                        policy_revision=snapshot.policy_revision,
                        policy_digest_sha512=snapshot.digest_sha512,
                    )
                )
            else:
                decisions.append(
                    PolicyDecision(
                        policy_id="core.none",
                        applicability=PolicyApplicability.NOT_APPLICABLE,
                        policy_revision=snapshot.policy_revision,
                        policy_digest_sha512=snapshot.digest_sha512,
                    )
                )
        return tuple(decisions)


def _clear_detection() -> GuardDetection:
    return GuardDetection(
        detection_id="d1", detector_id="det1", category_id="secret", outcome=DetectionOutcome.CLEAR
    )


def _match_detection() -> GuardDetection:
    return GuardDetection(
        detection_id="d1",
        detector_id="det1",
        category_id="secret",
        outcome=DetectionOutcome.MATCH,
        severity=Severity.HIGH,
    )


def _authority_provider(
    *, granted_action_ids: tuple[str, ...]
) -> _FixedProvider[AuthoritySnapshot]:
    return _FixedProvider(
        AuthoritySnapshot(authority_revision=1, granted_action_ids=granted_action_ids)
    )


def _action_registry_provider(
    *, registered_action_ids: tuple[str, ...]
) -> _FixedProvider[ActionRegistrySnapshot]:
    return _FixedProvider(
        ActionRegistrySnapshot(registry_revision=1, registered_action_ids=registered_action_ids)
    )


def _detector_registry_provider(
    *, registered_detector_ids: tuple[str, ...] = ()
) -> _FixedProvider[DetectorRegistrySnapshot]:
    return _FixedProvider(
        DetectorRegistrySnapshot(
            registry_revision=1, registered_detector_ids=registered_detector_ids
        )
    )


class _AlwaysExecutingAdapter:
    def execute(self, *, action_id: str, point_id: str) -> ExecutedAction:
        return ExecutedAction(action_id=action_id, executed=True, intervening=True)


def test_off_mode_never_calls_a_detector() -> None:
    runtime = GuardrailPointRuntime(detectors=(_ExplodingDetector(),))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="off",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=()),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(registered_action_ids=()),
        detector_registry_provider=_detector_registry_provider(),
        registry={},
        adapters={},
    )
    assert result.execution_state is ExecutionState.NOT_EVALUATED
    assert result.detections == ()


def test_observe_runs_detectors_and_policy_but_never_executes() -> None:
    detector = _RecordingDetector(detection=_match_detection())

    runtime = GuardrailPointRuntime(detectors=(detector,))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="observe",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(registered_action_ids=()),
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={},
        adapters={},
    )
    assert result.execution_state is ExecutionState.EVALUATED
    assert detector.calls == 1
    assert len(result.recommended_actions) == 1
    assert result.recommended_actions[0].action_id == "reject_output"
    assert result.executed_actions == ()


def test_clear_detection_recommends_nothing() -> None:
    detector = _RecordingDetector(detection=_clear_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="observe",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=()),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(registered_action_ids=()),
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={},
        adapters={},
    )
    assert result.recommended_actions == ()
    assert result.severity is Severity.NONE


def test_observe_reports_degraded_when_authority_is_never_established() -> None:
    # P5-CODEX-007 Rework: OBSERVE must never stay a plain `evaluated`
    # Result when the Binding it read is genuinely Stale/Unknown — a
    # Revision of `0` ("never established") is exactly that case.
    detector = _RecordingDetector(detection=_clear_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    stale_authority = _FixedProvider(AuthoritySnapshot(authority_revision=0, granted_action_ids=()))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="observe",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=stale_authority,
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(registered_action_ids=()),
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={},
        adapters={},
    )
    assert result.execution_state is ExecutionState.DEGRADED
    assert result.degraded_reason_code == "binding_stale"


def test_enforce_reports_unavailable_when_action_registry_is_never_established() -> None:
    # Codex Second Independent Review Probe B: an Action Registry
    # Revision of `0` must Fail-closed through this Runtime itself, not
    # only through a Direct Resolver call.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    stale_action_registry = _FixedProvider(
        ActionRegistrySnapshot(registry_revision=0, registered_action_ids=("reject_output",))
    )
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=stale_action_registry,
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={},
        adapters={},
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)


class _SequencedProvider[T]:
    """Returns a different value on each successive `.snapshot()` call
    (repeating the last one once exhausted) — proves the Entry-vs-
    Resolution Binding comparison in `GuardrailPointRuntime.invoke()`
    is a genuine, live comparison between two independent Provider
    reads, not a tautology derived from the same object twice (Codex
    Second Independent Review: `expected_authority_digest_sha512` was
    previously always computed from the very `authority` object handed
    straight to the Resolver in the same call)."""

    def __init__(self, snapshots: tuple[T, ...]) -> None:
        self._snapshots = snapshots
        self._call_count = 0

    def snapshot(self) -> T:
        index = min(self._call_count, len(self._snapshots) - 1)
        self._call_count += 1
        return self._snapshots[index]


def test_enforce_fails_closed_when_action_registry_digest_changes_before_resolution() -> None:
    # The other half of Probes A/B: not just Revision `0`, but a genuine
    # live Digest change between the Entry-time Binding capture and the
    # Resolution-time independent re-fetch (both `registry_revision=1`,
    # so `has_established_revision` alone would not catch this — only a
    # real Digest comparison across two separate `.snapshot()` calls
    # does). `registry`/`adapters` are populated to genuinely agree with
    # the Entry Snapshot's own `registered_action_ids`, so only the
    # Resolution-time Digest mismatch (never the new Entry-Binding
    # cross-checks) is what this specific Test isolates.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    changing_action_registry = _SequencedProvider(
        (
            ActionRegistrySnapshot(registry_revision=1, registered_action_ids=("reject_output",)),
            ActionRegistrySnapshot(
                registry_revision=1, registered_action_ids=("reject_output", "warn")
            ),
        )
    )
    registry = {
        "reject_output": ActionRegistryEntry(
            action_id=ActionId.REJECT_OUTPUT,
            allowed_points=("guardrail.output_candidate",),
            side_effect_class="local",
        )
    }
    adapters: dict[str, GuardActionAdapterPort] = {"reject_output": _AlwaysExecutingAdapter()}
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=changing_action_registry,
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry=registry,
        adapters=adapters,
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)
    assert changing_action_registry._call_count == 2


def test_enforce_succeeds_when_every_binding_component_genuinely_agrees() -> None:
    # Positive control for the new Entry-Binding cross-checks (P5-CODEX-
    # 007 Rework): confirms the new checks do not themselves become a
    # false-positive Fail-closed trap when every component of the
    # Binding — Scope, real Detector ids, real Action Registry/Adapter
    # keys, and the Policy Provider's own stamped Decisions — is
    # genuinely self-consistent.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    registry = {
        "reject_output": ActionRegistryEntry(
            action_id=ActionId.REJECT_OUTPUT,
            allowed_points=("guardrail.output_candidate",),
            side_effect_class="local",
        )
    }
    adapters: dict[str, GuardActionAdapterPort] = {"reject_output": _AlwaysExecutingAdapter()}
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(
            registered_action_ids=("reject_output",)
        ),
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry=registry,
        adapters=adapters,
    )
    assert result.execution_state is ExecutionState.EVALUATED
    executed_ids = {action.action_id for action in result.executed_actions if action.executed}
    assert "reject_output" in executed_ids


def test_enforce_fails_closed_when_snapshot_scope_disagrees_with_the_rest() -> None:
    # Codex Third Independent Review Probe A/B: a Snapshot whose own
    # `scope` disagrees with the other three is not a single coherent
    # Current Binding, even when its Revision/Digest are internally
    # self-consistent across the Entry/Resolution re-fetch.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    foreign_scope_detector_registry = _FixedProvider(
        DetectorRegistrySnapshot(
            registry_revision=1, registered_detector_ids=("det1",), scope="foreign_scope"
        )
    )
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(
            registered_action_ids=("reject_output",)
        ),
        detector_registry_provider=foreign_scope_detector_registry,
        registry={
            "reject_output": ActionRegistryEntry(
                action_id=ActionId.REJECT_OUTPUT,
                allowed_points=("guardrail.output_candidate",),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": _AlwaysExecutingAdapter()},
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)


def test_enforce_fails_closed_when_detector_registry_ids_disagree_with_real_detectors() -> None:
    # Codex Third Independent Review Probe A, reproduced exactly: the
    # Detector Registry Snapshot claims a Detector id set that does not
    # match the real, wired `self._detectors` — must Fail-closed even
    # though Revision/Digest/Scope all look internally fine.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    mismatched_detector_registry = _detector_registry_provider(
        registered_detector_ids=("not.the.real.detector",)
    )
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(
            registered_action_ids=("reject_output",)
        ),
        detector_registry_provider=mismatched_detector_registry,
        registry={
            "reject_output": ActionRegistryEntry(
                action_id=ActionId.REJECT_OUTPUT,
                allowed_points=("guardrail.output_candidate",),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": _AlwaysExecutingAdapter()},
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)


def test_enforce_fails_closed_when_action_registry_ids_disagree_with_real_registry() -> None:
    # Codex Third Independent Review Probe B, reproduced exactly: the
    # Action Registry Snapshot claims a narrower Action id set than the
    # real `registry`/`adapters` dicts actually contain.
    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    narrow_action_registry = _action_registry_provider(registered_action_ids=("warn",))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_EchoPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=narrow_action_registry,
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id=ActionId.REJECT_OUTPUT,
                allowed_points=("guardrail.output_candidate",),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": _AlwaysExecutingAdapter()},
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)


def test_enforce_fails_closed_when_a_policy_decision_stamp_disagrees_with_the_snapshot() -> None:
    # Codex Third Independent Review Probe C, reproduced exactly: a
    # Policy Provider whose `evaluate()` stamps a `PolicyDecision` with a
    # Revision/Digest different from its own `snapshot()`'s Entry
    # Binding must Fail-closed, even though the Snapshot itself
    # (Revision, Digest-vs-itself across two reads) looks fine.
    class _MisstampedPolicyProvider:
        def snapshot(self) -> PolicySnapshot:
            return PolicySnapshot(policy_revision=1, profile="core")

        def evaluate(
            self, *, point_id: str, detections: tuple[GuardDetection, ...]
        ) -> tuple[PolicyDecision, ...]:
            return tuple(
                PolicyDecision(
                    policy_id=f"core.{detection.category_id}",
                    applicability=PolicyApplicability.APPLICABLE,
                    recommended_action_ids=("reject_output",),
                    policy_revision=999,
                    policy_digest_sha512="a" * 128,
                )
                for detection in detections
            )

    detector = _RecordingDetector(detection=_match_detection())
    runtime = GuardrailPointRuntime(detectors=(detector,))
    result = runtime.invoke(
        invocation_id="inv-1",
        point_id="guardrail.output_candidate",
        mode="enforce",
        content="hello",
        policy_provider=_MisstampedPolicyProvider(),
        authority_provider=_authority_provider(granted_action_ids=("reject_output",)),
        approval_port=_AlwaysNotRequiredApproval(),
        action_registry_provider=_action_registry_provider(
            registered_action_ids=("reject_output",)
        ),
        detector_registry_provider=_detector_registry_provider(registered_detector_ids=("det1",)),
        registry={
            "reject_output": ActionRegistryEntry(
                action_id=ActionId.REJECT_OUTPUT,
                allowed_points=("guardrail.output_candidate",),
                side_effect_class="local",
            )
        },
        adapters={"reject_output": _AlwaysExecutingAdapter()},
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "binding_stale"
    assert all(not action.executed for action in result.executed_actions)
