"""Safety Model Seam Typed Contract (architecture §8, P5-SFM-001..004,
P5-CODEX-003 Rework).

`P5-SFM-002` requires Model ID, Exact Revision, Artifact Digest, Label
Schema, Calibration, Timeout, Latency, Token/Call count and Failure to
stay separate — never folded into a bare `content -> GuardDetection`
mapping, which is what let Unknown Label/Low Confidence/Timeout/
Malformed have no Typed representation to fail closed from (P5-RES-005).

`SafetyModelFailureKind.NONE` is the only value a caller may ever treat
as "the classification itself is trustworthy" — every other value must
converge on `DetectionOutcome.UNKNOWN`, never `CLEAR`/`safe`/`allow`
(P5-RES-005), regardless of what Label the underlying call happened to
produce.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN
from .results import DetectionOutcome, GuardDetection, Severity
from .taxonomy import CATEGORY_UNKNOWN_UNRESOLVED, CategoryRegistry, default_category_registry

_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"


class SafetyModelFailureKind(StrEnum):
    NONE = "none"
    """The classification is trustworthy — the only value a caller may
    ever treat as such."""

    TIMEOUT = "timeout"
    MALFORMED_RESPONSE = "malformed_response"
    UNKNOWN_LABEL = "unknown_label"
    LOW_CONFIDENCE = "low_confidence"
    INTERNAL_ERROR = "internal_error"


class SafetyModelResponse(ImmutableContract):
    """`P5-SFM-002`'s required separation, as one Typed Contract."""

    model_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    exact_revision: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    artifact_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    label_schema_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    detection: GuardDetection
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    calibrated: bool = False
    timed_out: bool = False
    latency_ms: int = Field(default=0, ge=0)
    call_count: int = Field(default=0, ge=0)
    token_count: int = Field(default=0, ge=0)
    failure: SafetyModelFailureKind = SafetyModelFailureKind.NONE

    @property
    def is_trustworthy(self) -> bool:
        """`False` for any non-`NONE` Failure *or* a Confidence below
        this Response's own declared threshold — Low Confidence Fails
        closed even when a caller forgets to set `failure` explicitly."""

        if self.failure is not SafetyModelFailureKind.NONE:
            return False
        return self.confidence >= self.confidence_threshold


class RawSafetyModelObservation(ImmutableContract):
    """What a Safety Model Provider literally returned, *before* the
    Label-Schema Decoder boundary below ever runs (P5-CODEX-008 Rework,
    Codex Second Independent Review).

    `raw_category_label` is completely unvalidated — a genuine Model
    Call can return any string here, including one this process has
    never seen before. Unlike `SafetyModelResponse` (whose `.detection`
    is already a finished, decided `GuardDetection`), nothing about this
    Contract's shape lets a caller skip validation: `decode_safety_model_
    observation()` below is the only supported way to turn one of these
    into a `SafetyModelResponse`, and it is the one place `raw_category_
    label` is ever checked against a Label/Category allow-list."""

    model_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    exact_revision: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    artifact_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    label_schema_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    # The raw, unvalidated Label the Provider itself returned — may be
    # any string, including one absent from every known Category
    # Registry (P5-CODEX-008's exact reopened gap).
    raw_category_label: str = Field(min_length=1, max_length=128)
    # The Provider's own binary Match/Clear signal, *before* this
    # process decides whether `raw_category_label` is even trustworthy
    # enough to honor that signal.
    raw_signal: DetectionOutcome = DetectionOutcome.CLEAR
    raw_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    calibrated: bool = False
    timed_out: bool = False
    latency_ms: int = Field(default=0, ge=0)
    call_count: int = Field(default=0, ge=0)
    token_count: int = Field(default=0, ge=0)
    # A Provider *may* self-report certain Failure classes directly
    # (e.g. it caught its own malformed/internal fault) — but never
    # `UNKNOWN_LABEL` or `LOW_CONFIDENCE` this way; those two are always
    # independently *derived* by the Decoder below from `raw_category_
    # label`/`raw_confidence`, never merely taken on the Provider's own
    # say-so (the exact shortcut P5-CODEX-008 closes).
    claimed_failure: SafetyModelFailureKind = SafetyModelFailureKind.NONE

    @field_validator("raw_signal")
    @classmethod
    def _validate_raw_signal(cls, value: DetectionOutcome) -> DetectionOutcome:
        if value not in (DetectionOutcome.CLEAR, DetectionOutcome.MATCH):
            raise ValueError("raw_signal must be CLEAR or MATCH")
        return value

    @field_validator("claimed_failure")
    @classmethod
    def _validate_claimed_failure(cls, value: SafetyModelFailureKind) -> SafetyModelFailureKind:
        if value in (SafetyModelFailureKind.UNKNOWN_LABEL, SafetyModelFailureKind.LOW_CONFIDENCE):
            raise ValueError(
                "UNKNOWN_LABEL/LOW_CONFIDENCE must be derived by "
                "decode_safety_model_observation(), never self-claimed"
            )
        return value


def decode_safety_model_observation(
    observation: RawSafetyModelObservation,
    *,
    detection_id: str,
    detector_id: str,
    category_registry: CategoryRegistry | None = None,
    match_severity: Severity = Severity.NONE,
) -> SafetyModelResponse:
    """The Label-Schema Decoder boundary P5-CODEX-008 requires: the
    *only* place `raw_category_label` is ever compared against a known
    Category allow-list. A Provider claiming `failure=none`, high
    Confidence and a `match` signal can no longer make an unrecognized
    Category trustworthy by simply asserting it is — this function
    independently overrides the outcome to `UNKNOWN_LABEL` regardless
    (Codex Second Independent Review Probe D, reproduced and closed by
    this function's own `default_category_registry()` fallback)."""

    registry = category_registry if category_registry is not None else default_category_registry()
    if observation.timed_out:
        failure = SafetyModelFailureKind.TIMEOUT
    elif observation.claimed_failure is not SafetyModelFailureKind.NONE:
        failure = observation.claimed_failure
    elif not registry.is_known(observation.raw_category_label):
        failure = SafetyModelFailureKind.UNKNOWN_LABEL
    elif observation.raw_confidence < observation.confidence_threshold:
        failure = SafetyModelFailureKind.LOW_CONFIDENCE
    else:
        failure = SafetyModelFailureKind.NONE

    trustworthy = failure is SafetyModelFailureKind.NONE
    outcome = observation.raw_signal if trustworthy else DetectionOutcome.UNKNOWN
    detection = GuardDetection(
        detection_id=detection_id,
        detector_id=detector_id,
        category_id=(
            observation.raw_category_label if trustworthy else CATEGORY_UNKNOWN_UNRESOLVED
        ),
        outcome=outcome,
        confidence=observation.raw_confidence,
        severity=match_severity if outcome is DetectionOutcome.MATCH else Severity.NONE,
    )
    return SafetyModelResponse(
        model_id=observation.model_id,
        exact_revision=observation.exact_revision,
        artifact_digest_sha512=observation.artifact_digest_sha512,
        label_schema_id=observation.label_schema_id,
        detection=detection,
        confidence=observation.raw_confidence,
        confidence_threshold=observation.confidence_threshold,
        calibrated=observation.calibrated,
        timed_out=observation.timed_out,
        latency_ms=observation.latency_ms,
        call_count=observation.call_count,
        token_count=observation.token_count,
        failure=failure,
    )
