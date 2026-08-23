"""Safety Model Seam Adapters (architecture §8, P5-E-WU-001/002,
P5-SFM-001..004, P5-CODEX-003 Rework).

`UnavailableSafetyModelAdapter` is the Production default — no Artifact
is selected/loaded in Phase 5's Initial Freeze, so every call honestly
raises `SafetyModelUnavailable` rather than fabricating a Call Success
(P5-SFM-003).

P5-CODEX-008 Rework (Codex Third Independent Review): `SafetyModelPort.
classify()` itself now returns `RawSafetyModelObservation` — the
unvalidated shape — never the already-decided `SafetyModelResponse`
(see `ports.py`). `DeterministicFakeSafetyModelAdapter` therefore no
longer calls `decode_safety_model_observation()` itself; it only ever
supplies a raw observation, structurally identical in shape to what any
real Provider Integration would return. `SafetyModelDetectorAdapter`
(the "Trusted Bridge") is now the *only* place `decode_safety_model_
observation()` is ever called — since the Port Contract's return type
no longer has an `is_trustworthy` to fabricate, no Provider
implementation (real or test) can hand this Bridge a pre-decided
trustworthy Response for an unregistered Category; the Decoder boundary
is structurally unavoidable, not merely a convention the Fake happens
to follow (closing the exact gap Codex's Third Review Probe reproduced:
a Port-conformant class handing `SafetyModelDetectorAdapter` a
completed `SafetyModelResponse` claiming `outcome=clear` for
`category_id=novel_unknown_label` used to be trusted as-is).

`SafetyModelDetectorAdapter` bridges a `SafetyModelPort` into the
`DetectorPort` shape so its classification can flow through the exact
same additive multi-Detector pipeline every Deterministic Detector
already uses — the Safety Model can only ever *add* a Detection
alongside the Deterministic ones, never suppress or downgrade another
Detector's own Match (P5-SFM-001, "not the Deterministic Baseline's
substitute or final Authority"), and any non-`NONE` Failure or
below-threshold Confidence converges on `DetectionOutcome.UNKNOWN`,
never `CLEAR` (P5-RES-005).
"""

from __future__ import annotations

from uuid import uuid4

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_UNKNOWN_UNRESOLVED,
    DetectionOutcome,
    GuardDetection,
    RawSafetyModelObservation,
    SafetyModelFailureKind,
    decode_safety_model_observation,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import (
    SafetyModelPort,
    SafetyModelUnavailable,
)

_FAKE_MODEL_ID = "test.fake-safety-model"
_FAKE_EXACT_REVISION = "test-fixture-1"
_FAKE_LABEL_SCHEMA_ID = "test.fake-label-schema-v1"


class UnavailableSafetyModelAdapter:
    """`P5-SFM-003`: honestly `unavailable` — never a Fake Production
    Call Success."""

    def classify(self, *, content: str) -> RawSafetyModelObservation:
        del content
        raise SafetyModelUnavailable("no Safety Model Artifact is selected/loaded")


class DeterministicFakeSafetyModelAdapter:
    """Test-only Fake — deterministic, no real Model Call, exact Label
    Schema known to the Test that constructs it. Never registered as a
    Production default (P5-E-WU-002).

    Returns a *raw*, unvalidated `RawSafetyModelObservation`
    (`raw_category_label`/`raw_signal`/`raw_confidence`/`timed_out`) —
    exactly the shape `SafetyModelPort.classify()` now requires of every
    implementation (P5-CODEX-008 Rework). It never calls the Decoder
    itself; `SafetyModelDetectorAdapter` does that unconditionally for
    every Provider, this Fake included, so `TIMEOUT`/`UNKNOWN_LABEL`/
    `LOW_CONFIDENCE` can never be short-circuited by this Fake claiming
    them directly — they are only ever *derived* by the Bridge, from
    `timed_out=True`, an unregistered `raw_category_label`, or
    `confidence < threshold` respectively."""

    def __init__(
        self,
        *,
        match_marker: str,
        raw_category_label: str = CATEGORY_UNKNOWN_UNRESOLVED,
        confidence: float = 1.0,
        confidence_threshold: float = 0.5,
        timed_out: bool = False,
        claimed_failure: SafetyModelFailureKind = SafetyModelFailureKind.NONE,
        label_schema_id: str = _FAKE_LABEL_SCHEMA_ID,
    ) -> None:
        self._match_marker = match_marker
        self._raw_category_label = raw_category_label
        self._confidence = confidence
        self._confidence_threshold = confidence_threshold
        self._timed_out = timed_out
        self._claimed_failure = claimed_failure
        self._label_schema_id = label_schema_id

    def classify(self, *, content: str) -> RawSafetyModelObservation:
        raw_signal = (
            DetectionOutcome.MATCH if self._match_marker in content else DetectionOutcome.CLEAR
        )
        return RawSafetyModelObservation(
            model_id=_FAKE_MODEL_ID,
            exact_revision=_FAKE_EXACT_REVISION,
            artifact_digest_sha512=None,
            label_schema_id=self._label_schema_id,
            raw_category_label=self._raw_category_label,
            raw_signal=raw_signal,
            raw_confidence=self._confidence,
            confidence_threshold=self._confidence_threshold,
            timed_out=self._timed_out,
            claimed_failure=self._claimed_failure,
        )


class SafetyModelDetectorAdapter:
    """Bridges a `SafetyModelPort` into the `DetectorPort` shape
    (P5-CODEX-003 Rework). `max_match_length` is `0` — a Safety Model
    Classification is a whole-Candidate Judgment, not a Span-bounded
    literal Match, so this Adapter's Stream Guard usage is out of Scope
    while Production stays `SafetyModelUnavailable`-by-default; wiring
    it into a live Stream Point is Non-scope for Phase 5 (P5-SFM-004).

    The sole caller of `decode_safety_model_observation()` (P5-CODEX-008
    Rework) — every `RawSafetyModelObservation` any wired `SafetyModelPort`
    ever returns is unconditionally routed through the Label-Schema
    Decoder here before this Adapter ever inspects `is_trustworthy`.
    `classify()` and the Decoder call both sit inside `detect()`'s one
    Fail-closed `try` (P5-CODEX-008 Rework, Codex Fourth Independent
    Review): a `Protocol` return type is never Runtime-enforced, so a
    Malformed Provider Return (`object()`, a stale decoded
    `SafetyModelResponse`, a missing Field) must converge on Typed
    `ERROR` here rather than let the Decoder's own `AttributeError`/
    `ValidationError` escape this Adapter uncaught."""

    detector_id = "safety_model.bridge"
    max_match_length = 0

    def __init__(self, *, safety_model: SafetyModelPort) -> None:
        self._safety_model = safety_model

    def detect(self, *, content: str) -> GuardDetection:
        # P5-CODEX-008 Rework (Codex Fourth Independent Review): the
        # Decoder call itself must sit inside this same Fail-closed
        # boundary, not only the `classify()` call — `Protocol`/return
        # type annotations are never enforced at runtime, so a
        # Malformed Provider (returning `object()`, a stale decoded
        # `SafetyModelResponse`, or anything else `decode_safety_model_
        # observation()` cannot actually parse) must converge on a
        # Typed `ERROR` Detection here, never let the underlying
        # `AttributeError`/`ValidationError` escape this Adapter.
        try:
            observation = self._safety_model.classify(content=content)
            response = decode_safety_model_observation(
                observation,
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
            )
        except SafetyModelUnavailable:
            return GuardDetection(
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.UNAVAILABLE,
            )
        except Exception:
            return GuardDetection(
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.ERROR,
            )
        if not response.is_trustworthy:
            # P5-RES-005: Unknown/Timeout/Malformed/Low Confidence never
            # convert to `safe`/`allow` — regardless of what Label the
            # underlying call actually produced.
            return GuardDetection(
                detection_id=response.detection.detection_id,
                detector_id=self.detector_id,
                category_id=response.detection.category_id,
                outcome=DetectionOutcome.UNKNOWN,
            )
        return response.detection
