"""Guardrail Governance Ports (architecture §2, P5-A-WU-003).

Every Port is a `Protocol` — the Domain never imports Web, Model or File
I/O directly. Detector/Policy/Authority/Approval/Action/SafetyModel stay
separate Contracts so no single Provider can generate another's Effect
(P5-AUT-002).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken

from .domain import (
    ActionRegistrySnapshot,
    ApprovalState,
    AuthoritySnapshot,
    DetectorRegistrySnapshot,
    ExecutedAction,
    GuardDetection,
    PolicyDecision,
    PolicySnapshot,
    RawSafetyModelObservation,
)


@runtime_checkable
class DetectorPort(Protocol):
    """One Deterministic (or Safety-Model-backed) Detector. Never raises
    for a routine non-match — a genuine internal fault returns a
    `DetectionOutcome.ERROR` Detection instead (P5-DET-005).

    `max_match_length` is the Detector's own contracted upper bound on
    how many characters a single Match can ever span (P5-CODEX-004
    Rework, architecture §6.2) — the Incremental Stream Guard's Holdback
    Window is derived from this exact number, never a fixed constant, so
    a Match can never have any of its characters released before the
    Match itself is confirmed. A Detector whose underlying Pattern has
    no true upper bound must pick and document a deliberate, realistic
    ceiling (e.g. RFC 5321's 64-character email local-part limit) rather
    than leaving this unbounded."""

    detector_id: str
    max_match_length: int

    def detect(
        self,
        *,
        content: str,
        cancellation: CancellationToken | None = None,
    ) -> GuardDetection: ...


@runtime_checkable
class PolicyProviderPort(Protocol):
    def snapshot(self) -> PolicySnapshot: ...

    def evaluate(
        self, *, point_id: str, detections: tuple[GuardDetection, ...]
    ) -> tuple[PolicyDecision, ...]: ...


@runtime_checkable
class AuthorityProviderPort(Protocol):
    def snapshot(self) -> AuthoritySnapshot: ...


@runtime_checkable
class ApprovalPort(Protocol):
    """Returns Approval State a human (or an external, non-AI System)
    already established — this Port never lets the caller construct an
    `approved` outcome itself (ADR-5-005)."""

    def state_for(self, *, action_id: str) -> ApprovalState: ...


@runtime_checkable
class GuardActionAdapterPort(Protocol):
    def execute(self, *, action_id: str, point_id: str) -> ExecutedAction: ...


class SafetyModelUnavailable(Exception):
    """Raised by a `SafetyModelPort` implementation to signal the Model
    itself is not selected/loaded — distinct from a genuine Detection
    Error (P5-SFM-003)."""


@runtime_checkable
class SafetyModelPort(Protocol):
    """Optional, replaceable Seam (P5-SFM-001) — never the Deterministic
    Baseline's substitute or final Authority. A Production default MUST
    raise `SafetyModelUnavailable` rather than fabricate a Call Success
    (P5-SFM-003).

    P5-CODEX-008 Rework (Codex Third Independent Review): `classify()`
    returns `RawSafetyModelObservation` — the *unvalidated* shape a real
    Provider Integration actually produces — never the already-decided
    `SafetyModelResponse`. This is a structural, Decoder-unavoidable
    boundary: no Port implementation, real or test, can hand
    `SafetyModelDetectorAdapter` a pre-decided `is_trustworthy=True` for
    an unregistered Category, because this Protocol's return type
    itself no longer has an `is_trustworthy` to fabricate. Only
    `SafetyModelDetectorAdapter` (the one caller of `decode_safety_model
    _observation()`) ever produces a `SafetyModelResponse` at all — a
    genuine per-call fault (Timeout, Malformed Response, Unknown Label,
    Low Confidence) is reported *from the raw fields*
    (`timed_out`/`claimed_failure`/`raw_category_label`/`raw_confidence`)
    and independently re-derived by the Decoder, distinct from
    `SafetyModelUnavailable`'s "no Model at all" — never read as
    `safe`/`allow` on a Provider's own say-so (P5-RES-005)."""

    def classify(self, *, content: str) -> RawSafetyModelObservation: ...


@runtime_checkable
class DetectorRegistryPort(Protocol):
    def snapshot(self) -> DetectorRegistrySnapshot: ...


@runtime_checkable
class ActionRegistryPort(Protocol):
    def snapshot(self) -> ActionRegistrySnapshot: ...
