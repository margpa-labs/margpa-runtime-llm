"""Incremental Stream Guard (architecture §6, P5-PNT-005, ADR-5-006,
P5-C-WU-002, P5-CODEX-004 Rework).

Enforce Streaming must never be "release now, Reject later" — an
Adversarial Pattern that straddles a Chunk boundary must be caught
*before* the matching bytes ever leave this process. `IncrementalStreamGuard`
keeps only a bounded trailing Window (never the full accumulated Stream
history) and only ever releases the Window minus a bounded trailing
Holdback, so any Match at most as long as `holdback_chars` can never be
split across a "released" boundary.

`holdback_chars` is derived from each wired Detector's own
`max_match_length` contract (P5-CODEX-004), never a fixed guess — a
fixed guess is exactly what let a Match Prefix leak past Holdback once
the accumulated Stream grew past it before the Match itself completed
(Codex's reproduced `feed("a"*100)` -> `"@example.com"` finding). On a
genuine Match, or a Detector Failure, or the bounded Window's own sanity
ceiling being exceeded, nothing further is ever released — the caller
converges on a Typed Terminal instead, never a Silent Pass.

`ObservingStreamGuard` is the separate OBSERVE-mode Scanner (architecture
§6.1): it releases every Delta immediately and unmodified (true
Byte-identical Streaming, not merely "eventually flushed"), while still
recording Detection/Failure as Bounded State — "non-intervening" and
"unobserved" are not the same guarantee.

`NullStreamGuard` is the OFF-mode substitute — Detector Call 0.

All three are Request-local by construction (one instance per
Invocation) — never shared across Turns/Tabs/Users (architecture §10,
P5-ACC-022).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..domain import DetectionOutcome
from ..ports import DetectorPort

# Explicit safety boundary (P5-CODEX-004 item 4, "Limit超過...はSilent
# Passしない"): even if a single fed Delta is pathologically large, the
# bounded Window this Scanner keeps must never grow past a hard,
# documented ceiling. Generous relative to any real Detector's
# `max_match_length` today (the largest, PII's, is in the low hundreds),
# while still bounding worst-case per-feed Scan cost.
_MAX_WINDOW_CHARS = 8192

_DETECTOR_ERROR_REASON_CODE = "guardrail_stream_detector_error"
_LIMIT_EXCEEDED_REASON_CODE = "guardrail_stream_limit_exceeded"


def _detects_match(detector: DetectorPort, content: str) -> bool:
    try:
        return detector.detect(content=content).outcome is DetectionOutcome.MATCH
    except Exception:
        return False


@dataclass(frozen=True, slots=True)
class StreamGuardDecision:
    safe_release: str
    terminated: bool
    reason_code: str | None = None


@dataclass(frozen=True, slots=True)
class StreamGuardSummary:
    """Terminal, Bounded roll-up of one Stage's Stream Guard activity
    (P5-CODEX-009 Rework, Codex Second Independent Review item 2) —
    Safe Counts only, never Raw Candidate content, so it can cross the
    same Boundary `guardrail_governance_routes.py` already enforces for
    every other Point's Status projection."""

    detection_count: int
    match_count: int
    degraded: bool
    terminated: bool
    reason_code: str | None = None


def _holdback_chars(detectors: tuple[DetectorPort, ...]) -> int:
    return max((detector.max_match_length for detector in detectors), default=0)


@dataclass(slots=True)
class IncrementalStreamGuard:
    """Enforce-mode Terminal Scanner (architecture §6.2). Bounded Window
    only — never the full Stream history — so per-feed Scan cost stays
    bounded by `holdback_chars` regardless of total Stream length, not
    the O(n²) full-buffer-every-chunk cost of re-scanning everything fed
    so far (P5-CODEX-004 item 4)."""

    detectors: tuple[DetectorPort, ...]
    holdback_chars: int = field(init=False)
    detection_count: int = field(default=0, init=False)
    match_count: int = field(default=0, init=False)
    _window: str = field(default="", init=False)
    _terminated: bool = field(default=False, init=False)
    _reason_code: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.holdback_chars = _holdback_chars(self.detectors)

    def feed(self, delta: str) -> StreamGuardDecision:
        if self._terminated:
            return self._terminal_decision()
        self._window += delta
        if len(self._window) > _MAX_WINDOW_CHARS:
            return self._terminate(_LIMIT_EXCEEDED_REASON_CODE)
        for detector in self.detectors:
            try:
                detection = detector.detect(content=self._window)
            except Exception:
                return self._terminate(_DETECTOR_ERROR_REASON_CODE)
            self.detection_count += 1
            if detection.outcome is DetectionOutcome.MATCH:
                self.match_count += 1
                return self._terminate(detection.category_id)
            if detection.outcome is DetectionOutcome.ERROR:
                return self._terminate(_DETECTOR_ERROR_REASON_CODE)
        safe_len = max(0, len(self._window) - self.holdback_chars)
        release = self._window[:safe_len]
        self._window = self._window[safe_len:]
        return StreamGuardDecision(safe_release=release, terminated=False)

    def finalize(self) -> StreamGuardDecision:
        """The upstream Model Stream ended normally — release whatever
        Holdback remains, unless a Match/Failure already Terminated this
        Scanner (never release Held-back content after Termination)."""

        if self._terminated:
            return self._terminal_decision()
        release = self._window
        self._window = ""
        return StreamGuardDecision(safe_release=release, terminated=False)

    def summary(self) -> StreamGuardSummary:
        return StreamGuardSummary(
            detection_count=self.detection_count,
            match_count=self.match_count,
            degraded=False,
            terminated=self._terminated,
            reason_code=self._reason_code,
        )

    def _terminate(self, reason_code: str) -> StreamGuardDecision:
        self._terminated = True
        self._reason_code = reason_code
        self._window = ""
        return self._terminal_decision()

    def _terminal_decision(self) -> StreamGuardDecision:
        return StreamGuardDecision(safe_release="", terminated=True, reason_code=self._reason_code)


@dataclass(slots=True)
class ObservingStreamGuard:
    """OBSERVE-mode Scanner (architecture §6.1, P5-CODEX-004 Rework):
    Bounded Scanner State that observes Detections without ever changing
    the live Stream. Every fed Delta is released back immediately and
    unmodified — true Byte-identical Streaming, satisfying P5-ACC-005's
    Output-Mutation-0 requirement exactly, never merely "flushed whole
    at the end". A Match or a Detector Failure is recorded into Bounded
    State (`detection_count`, `match_count`, `degraded`) instead of ever
    Suppressing or Terminating — "non-intervening" and "unobserved" are
    not the same guarantee (mirrors Phase 4's own ADR-4-007 Observation
    Count precedent)."""

    detectors: tuple[DetectorPort, ...]
    window_chars: int = field(init=False)
    detection_count: int = field(default=0, init=False)
    match_count: int = field(default=0, init=False)
    degraded: bool = field(default=False, init=False)
    _window: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.window_chars = _holdback_chars(self.detectors)

    def feed(self, delta: str) -> StreamGuardDecision:
        # P5-CODEX-009 Rework (Codex Second Independent Review Probe C):
        # the previous `(self._window + delta)[-self.window_chars:]`
        # truncated *before* scanning — an oversized single `delta`
        # (larger than `window_chars`) silently discarded its own
        # leading/interior characters from ever reaching a Detector.
        # This Scanner must remain non-intervening (`safe_release=delta`
        # always, unmodified, released immediately below) but must never
        # skip scanning any character that ever arrived — so the *full*
        # combined text is scanned first, and only the bounded trailing
        # slice of it is *retained* afterward as this call's carry-over
        # for the next `feed()` (bounding future calls' cost, exactly
        # like before; never bounding what this call itself scans).
        old_window = self._window
        combined = old_window + delta
        for detector in self.detectors:
            try:
                detection = detector.detect(content=combined)
            except Exception:
                self.degraded = True
                continue
            self.detection_count += 1
            if detection.outcome is DetectionOutcome.MATCH:
                # A Match already fully contained in the *previously*
                # retained tail was already counted on the prior
                # `feed()` call that first scanned it — re-scanning the
                # combined text every call (required so a Match spanning
                # the old/new boundary is never missed) would otherwise
                # double-count it on every subsequent call for as long
                # as it stays inside the bounded window. Re-checking the
                # old window alone (never counted toward `detection_
                # count`, purely a suppression signal) distinguishes
                # "still the same old Match" from "a genuinely new one".
                already_counted = bool(old_window) and _detects_match(detector, old_window)
                if not already_counted:
                    self.match_count += 1
            elif detection.outcome is DetectionOutcome.ERROR:
                self.degraded = True
        self._window = combined[-self.window_chars :] if self.window_chars > 0 else ""
        return StreamGuardDecision(safe_release=delta, terminated=False)

    def finalize(self) -> StreamGuardDecision:
        return StreamGuardDecision(safe_release="", terminated=False)

    def summary(self) -> StreamGuardSummary:
        return StreamGuardSummary(
            detection_count=self.detection_count,
            match_count=self.match_count,
            degraded=self.degraded,
            terminated=False,
            reason_code=None,
        )


@dataclass(frozen=True, slots=True)
class NullStreamGuard:
    """OFF-mode substitute: releases every byte immediately and never
    terminates, and never calls a Detector at all — Detector Call 0
    (P5-MOD-002, P5-ACC-004)."""

    def feed(self, delta: str) -> StreamGuardDecision:
        return StreamGuardDecision(safe_release=delta, terminated=False)

    def finalize(self) -> StreamGuardDecision:
        return StreamGuardDecision(safe_release="", terminated=False)

    def summary(self) -> StreamGuardSummary:
        return StreamGuardSummary(
            detection_count=0, match_count=0, degraded=False, terminated=False, reason_code=None
        )
