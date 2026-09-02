"""P6-RR-O-WU-002: `Qwen3GuardDetectorAdapter`'s dynamic-availability
resolution — the Detector must never assert `CLEAR` (scanned, found
nothing) when the dedicated Guard is not currently Active, and must
collapse a multi-Category Classification into the single most-severe
`GuardDetection` this Port's Contract requires.

P6-RR-R21 (Post-Codex Independent Review Rework, resolves P6-CODEX-086):
the Detector now acquires a Turn Lease (`begin_role_turn`) together with
the Adapter it dispatches through, and Releases it (`end_role_turn`)
exactly once per `detect()` call — on the CLEAR/MATCH success path, the
`classify_point` ERROR path, and (implicitly, by never acquiring one in
the first place) the UNAVAILABLE path.

P6-RR-R27 (Post-Codex Independent Review Rework, resolves P6-CODEX-091):
`detect()` must project the real Model Provider Identity (`model_id`/
Exact Revision/Artifact SHA-512/Contract Manifest Digest/Schema ID) that
`Qwen3GuardClassification` already carries onto the returned
`GuardDetection.model_provenance` — Codex's Review found this exact
narrowing step (Classification -> Generic GuardDetection) silently
discarded it. `test_model_provenance_round_trips_from_result_to_evidence`
proves this holds across all 3 Targets and all 5 real Outcome shapes
(Safe/Match/Unknown/Timeout/Malformed)."""

from __future__ import annotations

import threading
import time

import pytest

from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_detector_adapter import (
    Qwen3GuardDetectorAdapter,
    Qwen3GuardRoleTurn,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_UNKNOWN_UNRESOLVED,
    DetectionOutcome,
    GuardDetection,
    Qwen3GuardClassification,
    Qwen3GuardSafety,
    Qwen3GuardTarget,
    SafetyModelFailureKind,
    Severity,
)

_MODEL_ID = "guard.qwen3guard-gen-0.6b-q8-0"
_LEASE = "lease-token-1"


class _FakeQwen3GuardAdapter:
    def __init__(
        self,
        *,
        classification: Qwen3GuardClassification | None,
        raises: bool = False,
        block_until: threading.Event | None = None,
    ) -> None:
        self._classification = classification
        self._raises = raises
        self._block_until = block_until
        self.calls: list[tuple[Qwen3GuardTarget, str]] = []

    def classify_point(
        self,
        *,
        target: Qwen3GuardTarget,
        content: str,
        query: str | None = None,
        cancellation: object | None = None,
    ) -> Qwen3GuardClassification:
        del query, cancellation
        self.calls.append((target, content))
        if self._raises:
            raise RuntimeError("simulated failure")
        if self._block_until is not None:
            self._block_until.wait(timeout=5.0)
        assert self._classification is not None
        return self._classification

    def timeout_classification(
        self, *, target: Qwen3GuardTarget, latency_ms: int
    ) -> Qwen3GuardClassification:
        return Qwen3GuardClassification(
            model_id=_MODEL_ID,
            exact_revision="rev-timeout",
            artifact_digest_sha512="a" * 128,
            contract_manifest_digest_sha512="b" * 128,
            label_schema_id="qwen3guard_gen_frozen_line_protocol_v1",
            target=target,
            detections=(
                _detection(
                    category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                    outcome=DetectionOutcome.UNKNOWN,
                    severity=Severity.NONE,
                ),
            ),
            failure=SafetyModelFailureKind.TIMEOUT,
            latency_ms=latency_ms,
        )


class _ReleaseTracker:
    """Records every `end_role_turn` call so tests can assert
    exactly-once Release."""

    def __init__(self) -> None:
        self.released: list[object] = []

    def __call__(self, lease: object) -> None:
        self.released.append(lease)


def _detection(
    *, category_id: str, outcome: DetectionOutcome, severity: Severity
) -> GuardDetection:
    return GuardDetection(
        detection_id="det-1",
        detector_id="safety_model.qwen3guard_gen",
        category_id=category_id,
        outcome=outcome,
        severity=severity,
    )


def test_reports_unavailable_when_resolver_returns_none() -> None:
    release = _ReleaseTracker()
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: None,
        end_role_turn=release,
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.UNAVAILABLE
    assert result.detector_id == "safety_model.qwen3guard_gen"
    # No Adapter was ever resolved, so there is nothing to Release.
    assert release.released == []


def test_reports_unavailable_when_resolver_itself_raises() -> None:
    def _raising_resolver() -> None:
        raise RuntimeError("resolver failure")

    release = _ReleaseTracker()
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=_raising_resolver,
        end_role_turn=release,
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.UNAVAILABLE
    assert release.released == []


def test_reports_error_when_classify_point_raises_and_still_releases_lease() -> None:
    fake = _FakeQwen3GuardAdapter(classification=None, raises=True)
    release = _ReleaseTracker()
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=release,
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.ERROR
    # P6-RR-R21: exactly-once Release even on the classify_point Exception
    # path (`finally` inside `detect()`), never a leaked Lease.
    assert release.released == [_LEASE]


def test_forwards_clear_when_active_and_safe_and_releases_lease_exactly_once() -> None:
    classification = Qwen3GuardClassification(
        model_id=_MODEL_ID,
        exact_revision="rev-1",
        label_schema_id="qwen3guard_gen_frozen_line_protocol_v1",
        target=Qwen3GuardTarget.INPUT,
        safety=Qwen3GuardSafety.SAFE,
        detections=(
            _detection(
                category_id="unsafe_content",
                outcome=DetectionOutcome.CLEAR,
                severity=Severity.NONE,
            ),
        ),
    )
    fake = _FakeQwen3GuardAdapter(classification=classification)
    release = _ReleaseTracker()
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=release,
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.CLEAR
    assert fake.calls == [(Qwen3GuardTarget.INPUT, "hello")]
    assert release.released == [_LEASE]


def test_collapses_multiple_categories_into_the_most_severe_single_detection() -> None:
    classification = Qwen3GuardClassification(
        model_id=_MODEL_ID,
        exact_revision="rev-1",
        label_schema_id="qwen3guard_gen_frozen_line_protocol_v1",
        target=Qwen3GuardTarget.OUTPUT_CANDIDATE,
        safety=Qwen3GuardSafety.UNSAFE,
        categories=("Violent", "Toxic"),
        mapped_category_ids=("violence", "toxicity"),
        detections=(
            _detection(
                category_id="violence",
                outcome=DetectionOutcome.MATCH,
                severity=Severity.MODERATE,
            ),
            _detection(
                category_id="toxicity", outcome=DetectionOutcome.MATCH, severity=Severity.HIGH
            ),
        ),
    )
    fake = _FakeQwen3GuardAdapter(classification=classification)
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.OUTPUT_CANDIDATE,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=_ReleaseTracker(),
    )
    result = detector.detect(content="answer")
    assert result.outcome is DetectionOutcome.MATCH
    assert result.severity is Severity.HIGH
    assert result.category_id == "toxicity"


def test_empty_detections_from_classification_reports_clear() -> None:
    classification = Qwen3GuardClassification(
        model_id=_MODEL_ID,
        exact_revision="rev-1",
        label_schema_id="qwen3guard_gen_frozen_line_protocol_v1",
        target=Qwen3GuardTarget.CONTEXT_SOURCE,
        detections=(),
    )
    fake = _FakeQwen3GuardAdapter(classification=classification)
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.CONTEXT_SOURCE,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=_ReleaseTracker(),
    )
    result = detector.detect(content="doc")
    assert result.outcome is DetectionOutcome.CLEAR
    assert result.category_id != CATEGORY_UNKNOWN_UNRESOLVED


def test_end_role_turn_raising_never_masks_the_detection_result() -> None:
    """P6-RR-R21: `_release()`'s own defensive try/except means a broken
    `end_role_turn` Callable degrades to a silent no-op, never a crash
    that would replace an already-computed real `GuardDetection`."""
    classification = Qwen3GuardClassification(
        model_id=_MODEL_ID,
        exact_revision="rev-1",
        label_schema_id="qwen3guard_gen_frozen_line_protocol_v1",
        target=Qwen3GuardTarget.INPUT,
        safety=Qwen3GuardSafety.SAFE,
        detections=(
            _detection(
                category_id="unsafe_content",
                outcome=DetectionOutcome.CLEAR,
                severity=Severity.NONE,
            ),
        ),
    )
    fake = _FakeQwen3GuardAdapter(classification=classification)

    def _raising_release(lease: object) -> None:
        del lease
        raise RuntimeError("release failure")

    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=_raising_release,
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.CLEAR


def _classification_for(
    *, target: Qwen3GuardTarget, outcome_shape: str
) -> Qwen3GuardClassification:
    """One `Qwen3GuardClassification` per real Outcome shape
    `Qwen3GuardGenAdapter.classify_point()` actually produces — Safe/
    Match/Unknown come from `decode_qwen3guard_output()`'s own success
    path, Timeout/Malformed from `_failure_classification()`'s. Every
    shape carries genuine, distinguishable Identity — mirroring exactly
    what the real Adapter always populates, success or typed failure
    alike."""
    model_id = _MODEL_ID
    exact_revision = f"rev-roundtrip-{target.value}-{outcome_shape}"
    artifact_digest_sha512 = "a" * 128
    contract_manifest_digest_sha512 = "b" * 128
    label_schema_id = "qwen3guard_gen_frozen_line_protocol_v1"
    if outcome_shape == "safe":
        return Qwen3GuardClassification(
            model_id=model_id,
            exact_revision=exact_revision,
            artifact_digest_sha512=artifact_digest_sha512,
            contract_manifest_digest_sha512=contract_manifest_digest_sha512,
            label_schema_id=label_schema_id,
            target=target,
            safety=Qwen3GuardSafety.SAFE,
            detections=(
                _detection(
                    category_id="unsafe_content",
                    outcome=DetectionOutcome.CLEAR,
                    severity=Severity.NONE,
                ),
            ),
        )
    if outcome_shape == "match":
        return Qwen3GuardClassification(
            model_id=model_id,
            exact_revision=exact_revision,
            artifact_digest_sha512=artifact_digest_sha512,
            contract_manifest_digest_sha512=contract_manifest_digest_sha512,
            label_schema_id=label_schema_id,
            target=target,
            safety=Qwen3GuardSafety.UNSAFE,
            categories=("Violent",),
            mapped_category_ids=("violent",),
            detections=(
                _detection(
                    category_id="violent", outcome=DetectionOutcome.MATCH, severity=Severity.HIGH
                ),
            ),
        )
    if outcome_shape == "unknown":
        return Qwen3GuardClassification(
            model_id=model_id,
            exact_revision=exact_revision,
            artifact_digest_sha512=artifact_digest_sha512,
            contract_manifest_digest_sha512=contract_manifest_digest_sha512,
            label_schema_id=label_schema_id,
            target=target,
            safety=Qwen3GuardSafety.UNSAFE,
            categories=("Unverified Category",),
            detections=(
                _detection(
                    category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                    outcome=DetectionOutcome.UNKNOWN,
                    severity=Severity.NONE,
                ),
            ),
            failure=SafetyModelFailureKind.UNKNOWN_LABEL,
        )
    failure = (
        SafetyModelFailureKind.TIMEOUT
        if outcome_shape == "timeout"
        else SafetyModelFailureKind.MALFORMED_RESPONSE
    )
    return Qwen3GuardClassification(
        model_id=model_id,
        exact_revision=exact_revision,
        artifact_digest_sha512=artifact_digest_sha512,
        contract_manifest_digest_sha512=contract_manifest_digest_sha512,
        label_schema_id=label_schema_id,
        target=target,
        detections=(
            _detection(
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.UNKNOWN,
                severity=Severity.NONE,
            ),
        ),
        failure=failure,
    )


@pytest.mark.parametrize(
    "target",
    [Qwen3GuardTarget.INPUT, Qwen3GuardTarget.OUTPUT_CANDIDATE, Qwen3GuardTarget.CONTEXT_SOURCE],
)
@pytest.mark.parametrize("outcome_shape", ["safe", "match", "unknown", "timeout", "malformed"])
def test_model_provenance_round_trips_from_result_to_evidence(
    target: Qwen3GuardTarget, outcome_shape: str
) -> None:
    """P6-RR-R27 (resolves P6-CODEX-091): across all 3 Targets and all 5
    real Outcome shapes (15 cases total), `GuardDetection.model_
    provenance` carries the exact same Identity the source `Qwen3Guard
    Classification` held — Result -> Evidence Round-trip, never silently
    dropped at the Generic-Detection narrowing boundary."""
    classification = _classification_for(target=target, outcome_shape=outcome_shape)
    fake = _FakeQwen3GuardAdapter(classification=classification)
    detector = Qwen3GuardDetectorAdapter(
        target=target,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore
        end_role_turn=_ReleaseTracker(),
    )
    result = detector.detect(content="content")
    assert result.model_provenance is not None
    assert result.model_provenance.model_id == classification.model_id
    assert result.model_provenance.exact_revision == classification.exact_revision
    assert result.model_provenance.artifact_digest_sha512 == classification.artifact_digest_sha512
    assert (
        result.model_provenance.contract_manifest_digest_sha512
        == classification.contract_manifest_digest_sha512
    )
    assert result.model_provenance.label_schema_id == classification.label_schema_id


def test_model_provenance_is_none_when_unavailable_no_classification_exists() -> None:
    """The one real Path with genuinely no Classification to source
    Identity from: no Lease/Adapter at all. `model_provenance` correctly
    stays `None` rather than fabricating an Identity for a Model Call
    that never happened."""
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: None,
        end_role_turn=_ReleaseTracker(),
    )
    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.UNAVAILABLE
    assert result.model_provenance is None


def test_timeout_returns_unknown_and_releases_lease_only_after_worker_finishes() -> None:
    release = _ReleaseTracker()
    unblock = threading.Event()
    fake = _FakeQwen3GuardAdapter(classification=None, block_until=unblock)
    detector = Qwen3GuardDetectorAdapter(
        target=Qwen3GuardTarget.INPUT,
        begin_role_turn=lambda: Qwen3GuardRoleTurn(adapter=fake, lease=_LEASE),  # type: ignore[arg-type]
        end_role_turn=release,
        inference_budget_ms=10,
        cancel_grace_ms=0,
    )

    result = detector.detect(content="hello")
    assert result.outcome is DetectionOutcome.UNKNOWN
    assert result.model_provenance is not None
    assert result.model_provenance.model_id == _MODEL_ID
    # Release is deferred until the timed-out worker actually completes.
    assert release.released == []

    unblock.set()
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline and release.released != [_LEASE]:
        time.sleep(0.01)
    assert release.released == [_LEASE]
