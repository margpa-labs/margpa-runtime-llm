"""Phase 5-A Contract Adversarial Test (P5-A-WU-004).

Unknown Enum/Category, NaN/Infinity, Unbounded Span/Collection,
Overlap/Out-of-range Span and extra-field injection must all Fail-closed
at construction time — never silently coerced into a valid Result.
"""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    AuthoritySnapshot,
    DetectionOutcome,
    ExecutionState,
    GuardDetection,
    GuardrailResult,
    PolicySnapshot,
    Severity,
    TypedSpan,
    spans_are_verified,
)


def test_confidence_rejects_nan() -> None:
    with pytest.raises(ValidationError):
        GuardDetection(
            detection_id="d1",
            detector_id="det1",
            category_id="secret",
            outcome=DetectionOutcome.MATCH,
            confidence=math.nan,
        )


def test_confidence_rejects_infinity() -> None:
    with pytest.raises(ValidationError):
        GuardDetection(
            detection_id="d1",
            detector_id="det1",
            category_id="secret",
            outcome=DetectionOutcome.MATCH,
            confidence=math.inf,
        )


def test_confidence_out_of_bounds_rejected() -> None:
    with pytest.raises(ValidationError):
        GuardDetection(
            detection_id="d1",
            detector_id="det1",
            category_id="secret",
            outcome=DetectionOutcome.MATCH,
            confidence=1.5,
        )


def test_unknown_outcome_string_rejected() -> None:
    with pytest.raises(ValidationError):
        GuardDetection.model_validate(
            {
                "detection_id": "d1",
                "detector_id": "det1",
                "category_id": "secret",
                "outcome": "definitely_safe",  # not a real DetectionOutcome member
            }
        )


def test_extra_field_rejected_everywhere() -> None:
    # ImmutableContract's extra="forbid" must hold for every new Phase 5
    # contract, not just Phase 4's.
    with pytest.raises(ValidationError):
        GuardDetection.model_validate(
            {
                "detection_id": "d1",
                "detector_id": "det1",
                "category_id": "secret",
                "outcome": "match",
                "raw_matched_text": "sk-should-never-exist-as-a-field",
            }
        )


def test_span_end_must_be_after_start() -> None:
    with pytest.raises(ValidationError):
        TypedSpan(category_id="secret", start=5, end=5)
    with pytest.raises(ValidationError):
        TypedSpan(category_id="secret", start=10, end=3)


def test_overlapping_spans_are_not_verified() -> None:
    spans = (
        TypedSpan(category_id="secret", start=0, end=10),
        TypedSpan(category_id="secret", start=5, end=15),
    )
    assert spans_are_verified(spans, content_length=20) is False


def test_out_of_range_span_is_not_verified() -> None:
    spans = (TypedSpan(category_id="secret", start=0, end=999),)
    assert spans_are_verified(spans, content_length=20) is False


def test_non_overlapping_in_range_spans_are_verified() -> None:
    spans = (
        TypedSpan(category_id="secret", start=0, end=5),
        TypedSpan(category_id="secret", start=5, end=10),
    )
    assert spans_are_verified(spans, content_length=10) is True


def test_unbounded_detection_collection_is_rejected() -> None:
    detection = GuardDetection(
        detection_id="d1", detector_id="det1", category_id="secret", outcome=DetectionOutcome.CLEAR
    )
    with pytest.raises(ValidationError):
        GuardrailResult(
            invocation_id="inv-1",
            point_id="guardrail.input",
            mode="observe",
            execution_state=ExecutionState.EVALUATED,
            detections=(detection,) * 300,  # exceeds max_length=256
        )


def test_unbounded_span_collection_is_rejected() -> None:
    span = TypedSpan(category_id="secret", start=0, end=1)
    with pytest.raises(ValidationError):
        GuardDetection(
            detection_id="d1",
            detector_id="det1",
            category_id="secret",
            outcome=DetectionOutcome.MATCH,
            typed_spans=(span,) * 100,  # exceeds max_length=64
        )


def test_severity_unknown_string_rejected() -> None:
    with pytest.raises(ValidationError):
        GuardDetection.model_validate(
            {
                "detection_id": "d1",
                "detector_id": "det1",
                "category_id": "secret",
                "outcome": "match",
                "severity": "apocalyptic",
            }
        )


def test_severity_enum_members_are_exact() -> None:
    assert {member.value for member in Severity} == {"none", "low", "moderate", "high", "critical"}


# -- P5-AUT-003/P5-CODEX-002 Rework: Revision/Scope/Digest/Source
# Class/Expiry Typed Contract on Policy/Authority Snapshots. --


def test_authority_snapshot_has_established_revision_is_false_at_the_zero_sentinel() -> None:
    assert (
        AuthoritySnapshot(authority_revision=0, granted_action_ids=()).has_established_revision
        is False
    )
    assert (
        AuthoritySnapshot(authority_revision=1, granted_action_ids=()).has_established_revision
        is True
    )


def test_authority_snapshot_is_expired_only_once_expires_at_is_in_the_past() -> None:
    non_expiring = AuthoritySnapshot(authority_revision=1, granted_action_ids=())
    assert non_expiring.is_expired is False

    past = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=(), expires_at="2000-01-01T00:00:00+00:00"
    )
    assert past.is_expired is True

    future = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=(), expires_at="2999-01-01T00:00:00+00:00"
    )
    assert future.is_expired is False


def test_authority_snapshot_malformed_expiry_fails_closed_as_expired() -> None:
    malformed = AuthoritySnapshot(
        authority_revision=1, granted_action_ids=(), expires_at="not-a-timestamp"
    )
    assert malformed.is_expired is True


def test_authority_snapshot_default_scope_and_source_class_are_populated() -> None:
    snapshot = AuthoritySnapshot(authority_revision=1, granted_action_ids=())
    assert snapshot.scope
    assert snapshot.source_class


def test_policy_snapshot_shares_the_same_revision_and_expiry_contract() -> None:
    assert not PolicySnapshot(policy_revision=0, profile="core").has_established_revision
    assert PolicySnapshot(policy_revision=1, profile="core").has_established_revision
    assert PolicySnapshot(
        policy_revision=1, profile="core", expires_at="2000-01-01T00:00:00+00:00"
    ).is_expired
