"""Incremental Stream Guard — Bounded Holdback/Cross-chunk Match
Adversarial Test (P5-PNT-005, ADR-5-006, P5-ACC-009, P5-CODEX-004 Rework).

`holdback_chars`/`window_chars` are no longer a caller-supplied constant
— they are derived from the wired Detectors' own `max_match_length`
contract (`IncrementalStreamGuard.__post_init__`/`ObservingStreamGuard.
__post_init__`), so every fixture Detector below declares an exact,
honest `max_match_length` rather than leaving it implicit."""

from __future__ import annotations

from margpa_runtime_llm.modules.guardrail_governance.application import (
    IncrementalStreamGuard,
    NullStreamGuard,
    ObservingStreamGuard,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    DetectionOutcome,
    GuardDetection,
    Severity,
)


class _MarkerDetector:
    """Fixture Detector matching one fixed literal Marker — its
    `max_match_length` is honestly the Marker's own length, mirroring
    the real `MarkerDetector`'s exact-bound contract."""

    detector_id = "test-marker"

    def __init__(self, marker: str, *, category_id: str = "secret") -> None:
        self._marker = marker
        self._category_id = category_id
        self.max_match_length = len(marker)

    def detect(self, *, content: str) -> GuardDetection:
        if self._marker in content:
            return GuardDetection(
                detection_id="d1",
                detector_id=self.detector_id,
                category_id=self._category_id,
                outcome=DetectionOutcome.MATCH,
                severity=Severity.CRITICAL,
            )
        return GuardDetection(
            detection_id="d1",
            detector_id=self.detector_id,
            category_id=self._category_id,
            outcome=DetectionOutcome.CLEAR,
        )


class _RaisingDetector:
    """Fixture Detector that always raises — proves Detector Failure
    Fail-closes rather than Silent-Passing (P5-CODEX-004 item 4)."""

    detector_id = "test-raising"
    max_match_length = 8

    def detect(self, *, content: str) -> GuardDetection:
        raise RuntimeError("simulated detector crash")


class _ErrorOutcomeDetector:
    """Fixture Detector that reports a genuine `ERROR` Detection
    Outcome (a caught internal fault, distinct from an uncaught raise) —
    must Fail-closed identically to a raising Detector."""

    detector_id = "test-error-outcome"
    max_match_length = 8

    def detect(self, *, content: str) -> GuardDetection:
        return GuardDetection(
            detection_id="d1",
            detector_id=self.detector_id,
            category_id="secret",
            outcome=DetectionOutcome.ERROR,
        )


_SECRET_MARKER = "SECRET-MARKER"


def _secret_detector() -> _MarkerDetector:
    return _MarkerDetector(_SECRET_MARKER)


def test_holdback_is_derived_from_the_detectors_own_max_match_length() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    assert guard.holdback_chars == len(_SECRET_MARKER)


def test_normal_text_releases_up_to_the_holdback_boundary() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    holdback = len(_SECRET_MARKER)
    decision = guard.feed("a" * (holdback + 20))
    assert decision.terminated is False
    assert len(decision.safe_release) == 20
    final = guard.finalize()
    assert final.safe_release == "a" * holdback  # remaining holdback flushed at Terminal


def test_pattern_split_exactly_across_two_chunks_is_still_caught() -> None:
    # "SECRET-MARKER" split mid-token across two Deltas — the classic
    # Cross-chunk evasion attempt (P5-ACC-009).
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    first = guard.feed("hello SECRET-MAR")
    assert first.terminated is False
    second = guard.feed("KER world")
    assert second.terminated is True
    assert second.safe_release == ""
    assert second.reason_code == "secret"


def test_pattern_split_one_character_per_chunk_is_still_caught() -> None:
    # The most adversarial possible Chunking: one character fed at a
    # time. Proves the Holdback contract holds regardless of how finely
    # the upstream Model Stream happens to Chunk (P5-CODEX-004 item 5).
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    released = ""
    terminated = False
    reason_code: str | None = None
    for character in f"hello {_SECRET_MARKER} world":
        decision = guard.feed(character)
        released += decision.safe_release
        if decision.terminated:
            terminated = True
            reason_code = decision.reason_code
            break
    assert terminated is True
    assert reason_code == "secret"
    assert _SECRET_MARKER not in released


def test_holdback_boundary_minus_one_char_still_catches_the_match() -> None:
    # The Match completes with exactly `holdback_chars - 1` trailing
    # Benign characters already fed after it in the same buffer — still
    # inside the Held-back Window, so still zero-leak.
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    holdback = len(_SECRET_MARKER)
    decision = guard.feed(_SECRET_MARKER + "x" * (holdback - 1))
    assert decision.terminated is True
    assert decision.safe_release == ""


def test_holdback_boundary_plus_one_char_releases_only_the_confirmed_clear_prefix() -> None:
    # One character past the Match's own length: the Match still
    # completes and Terminates on this exact feed — Termination happens
    # the instant the Detector reports MATCH, regardless of how much
    # trailing content already arrived in the same buffer, so the
    # trailing character is never released either.
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    holdback = len(_SECRET_MARKER)
    decision = guard.feed(_SECRET_MARKER + "x" * (holdback + 1))
    assert decision.terminated is True
    assert decision.safe_release == ""


def test_matched_content_is_never_released_even_partially() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    released_so_far = ""
    for chunk in ["he", "llo ", _SECRET_MARKER, " tail"]:
        decision = guard.feed(chunk)
        released_so_far += decision.safe_release
        if decision.terminated:
            break
    assert _SECRET_MARKER not in released_so_far
    assert "tail" not in released_so_far


def test_after_termination_further_feeds_release_nothing() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    guard.feed(_SECRET_MARKER)
    decision = guard.feed(" more content after the hit")
    assert decision.terminated is True
    assert decision.safe_release == ""


def test_finalize_after_termination_releases_nothing() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    guard.feed(_SECRET_MARKER)
    final = guard.finalize()
    assert final.terminated is True
    assert final.safe_release == ""


def test_finalize_on_clean_stream_releases_everything() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    released = guard.feed("a real ").safe_release
    released += guard.feed("answer with no secrets").safe_release
    released += guard.finalize().safe_release
    assert released == "a real answer with no secrets"


def test_total_released_bytes_equal_total_fed_bytes_on_a_clean_stream() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    chunks = ["The ", "quick ", "brown ", "fox ", "jumps."]
    released = ""
    for chunk in chunks:
        decision = guard.feed(chunk)
        released += decision.safe_release
    released += guard.finalize().safe_release
    assert released == "".join(chunks)


def test_a_long_benign_stream_never_grows_the_window_unbounded() -> None:
    # P5-CODEX-004 item 4: the Window must stay bounded by the
    # Detector's own `max_match_length`, never the total Stream length —
    # a long clean Stream must never accumulate without releasing.
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    for _ in range(500):
        decision = guard.feed("benign filler text, no secrets here. ")
        assert len(guard._window) <= guard.holdback_chars
        assert decision.terminated is False
    final = guard.finalize()
    assert final.terminated is False


def test_a_long_realistic_email_local_part_is_still_caught_with_zero_leak() -> None:
    # Codex's own reproduced Finding: a long run of Benign filler
    # followed by a genuine Match must never leak any part of the Match
    # itself, regardless of how much Benign content preceded it — this
    # is exactly what a Detector-contract-derived (not fixed) Holdback
    # guarantees.
    from margpa_runtime_llm.adapters.guardrail_governance.deterministic_detectors import (
        PiiPatternDetector,
    )

    guard = IncrementalStreamGuard(detectors=(PiiPatternDetector(),))
    long_local_part = "a" * 60  # within RFC 5321's 64-char local-part bound
    email = f"{long_local_part}@example.com"
    released = ""
    terminated = False
    for chunk in ["Here is a very long filler prefix. " * 3, email, " trailing text"]:
        decision = guard.feed(chunk)
        released += decision.safe_release
        if decision.terminated:
            terminated = True
            break
    assert terminated is True
    assert email not in released
    assert long_local_part not in released


def test_empty_holdback_when_no_detectors_are_wired_releases_immediately() -> None:
    guard = IncrementalStreamGuard(detectors=())
    assert guard.holdback_chars == 0
    decision = guard.feed("hello")
    assert decision.safe_release == "hello"


def test_a_raising_detector_fails_closed_not_silently_passes() -> None:
    guard = IncrementalStreamGuard(detectors=(_RaisingDetector(),))
    decision = guard.feed("hello world")
    assert decision.terminated is True
    assert decision.safe_release == ""
    assert decision.reason_code == "guardrail_stream_detector_error"


def test_a_detector_error_outcome_fails_closed_not_silently_passes() -> None:
    guard = IncrementalStreamGuard(detectors=(_ErrorOutcomeDetector(),))
    decision = guard.feed("hello world")
    assert decision.terminated is True
    assert decision.safe_release == ""
    assert decision.reason_code == "guardrail_stream_detector_error"


def test_window_sanity_ceiling_fails_closed_on_a_pathologically_large_single_feed() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    decision = guard.feed("x" * 9000)  # past the 8192-char sanity ceiling
    assert decision.terminated is True
    assert decision.safe_release == ""
    assert decision.reason_code == "guardrail_stream_limit_exceeded"


def test_null_stream_guard_releases_every_byte_immediately_and_never_terminates() -> None:
    # OFF-mode substitute: even content that would otherwise Match (a
    # live "SECRET-MARKER") is released byte-identically and Detector
    # Call 0, since this Guard runs no Detector at all.
    guard = NullStreamGuard()
    decision = guard.feed(f"{_SECRET_MARKER} leaked in the clear")
    assert decision.safe_release == f"{_SECRET_MARKER} leaked in the clear"
    assert decision.terminated is False
    final = guard.finalize()
    assert final.safe_release == ""
    assert final.terminated is False


def test_observing_stream_guard_never_intervenes_but_records_the_match() -> None:
    # OBSERVE-mode Scanner (architecture §6.1, P5-CODEX-004 Rework):
    # true Byte-identical passthrough on every single feed — never
    # withheld even temporarily — while still recording that a Match
    # occurred as Bounded State.
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    decision = guard.feed(f"leaked: {_SECRET_MARKER}")
    assert decision.safe_release == f"leaked: {_SECRET_MARKER}"
    assert decision.terminated is False
    assert guard.match_count == 1
    assert guard.detection_count == 1
    final = guard.finalize()
    assert final.terminated is False
    assert final.safe_release == ""


def test_observing_stream_guard_is_byte_identical_across_many_feeds() -> None:
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    chunks = ["a" * 40, "b" * 40, _SECRET_MARKER, "c" * 40]
    released = "".join(guard.feed(chunk).safe_release for chunk in chunks)
    released += guard.finalize().safe_release
    assert released == "".join(chunks)
    assert guard.match_count == 1


def test_observing_stream_guard_records_degraded_on_detector_failure_without_intervening() -> None:
    guard = ObservingStreamGuard(detectors=(_RaisingDetector(),))
    decision = guard.feed("hello world")
    assert decision.safe_release == "hello world"
    assert decision.terminated is False
    assert guard.degraded is True


def test_observing_stream_guard_bounds_its_window_on_a_long_benign_stream() -> None:
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    for _ in range(500):
        guard.feed("benign filler text, no secrets here. ")
    assert len(guard._window) <= guard.window_chars


def test_observing_stream_guard_catches_a_match_anywhere_in_an_oversized_single_delta() -> None:
    # P5-CODEX-009 Rework (Codex Second Independent Review Probe C): the
    # previous `(self._window + delta)[-window_chars:]` truncated
    # *before* scanning, so a single `delta` far larger than
    # `window_chars` could carry a Match entirely inside the discarded
    # leading portion and it would never reach a Detector at all. The
    # Match here sits in the *middle* of an oversized single Delta —
    # deliberately not at the tail, where the old, buggy slice would
    # have accidentally still caught it by coincidence.
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    assert guard.window_chars == len(_SECRET_MARKER)
    oversized_delta = ("x" * 500) + _SECRET_MARKER + ("y" * 500)
    decision = guard.feed(oversized_delta)
    assert decision.safe_release == oversized_delta
    assert decision.terminated is False
    assert guard.match_count == 1


def test_observing_stream_guard_never_double_counts_a_match_still_inside_the_retained_window() -> (
    None
):
    # The fix for the bug above (re-scanning the full combined text
    # every `feed()`, not just a truncated tail) introduces its own risk
    # if not handled: a Match fully inside the *previously* retained
    # tail would otherwise be re-detected — and re-counted — on every
    # subsequent `feed()` call for as long as it stays inside the
    # bounded window.
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    guard.feed(_SECRET_MARKER)
    assert guard.match_count == 1
    for _ in range(5):
        guard.feed("z")
    assert guard.match_count == 1


def test_observing_stream_guard_summary_reports_bounded_counts() -> None:
    guard = ObservingStreamGuard(detectors=(_secret_detector(),))
    guard.feed(f"leaked: {_SECRET_MARKER}")
    guard.finalize()
    summary = guard.summary()
    assert summary.detection_count == 1
    assert summary.match_count == 1
    assert summary.degraded is False
    assert summary.terminated is False
    assert summary.reason_code is None


def test_incremental_stream_guard_summary_reports_termination_reason() -> None:
    guard = IncrementalStreamGuard(detectors=(_secret_detector(),))
    guard.feed(_SECRET_MARKER)
    summary = guard.summary()
    assert summary.terminated is True
    assert summary.reason_code == "secret"
    assert summary.match_count == 1


def test_null_stream_guard_summary_is_all_zero() -> None:
    guard = NullStreamGuard()
    guard.feed("hello")
    summary = guard.summary()
    assert summary.detection_count == 0
    assert summary.match_count == 0
    assert summary.degraded is False
    assert summary.terminated is False
    assert summary.reason_code is None
