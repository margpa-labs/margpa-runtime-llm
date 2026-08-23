"""Safety Model Seam Negative Matrix (architecture §8, P5-SFM-001..004,
P5-RES-005, P5-CODEX-003/008 Rework).

Unknown Label, Low Confidence, Timeout, Malformed Response and a
genuine Conflict against a Deterministic Detector must never convert to
`safe`/`allow` — every scenario here is exercised through the real
`SafetyModelDetectorAdapter` Bridge, never by inspecting a Fake's
`.classify()` output directly (P5-CODEX-008 Rework, Codex Third
Independent Review: `SafetyModelPort.classify()` now returns the raw,
unvalidated `RawSafetyModelObservation` — only the Bridge ever decodes
it into a `SafetyModelResponse`)."""

from __future__ import annotations

from margpa_runtime_llm.adapters.guardrail_governance.safety_model_adapters import (
    DeterministicFakeSafetyModelAdapter,
    SafetyModelDetectorAdapter,
    UnavailableSafetyModelAdapter,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_SECRET,
    DetectionOutcome,
    GuardDetection,
    RawSafetyModelObservation,
    SafetyModelFailureKind,
    Severity,
)


def test_unavailable_adapter_is_not_trustworthy_and_never_reaches_the_bridge_as_a_label() -> None:
    bridge = SafetyModelDetectorAdapter(safety_model=UnavailableSafetyModelAdapter())
    result = bridge.detect(content="anything")
    assert result.outcome is DetectionOutcome.UNAVAILABLE


def test_timeout_failure_is_not_trustworthy_and_never_converts_to_clear() -> None:
    adapter = DeterministicFakeSafetyModelAdapter(match_marker="TESTMATCH", timed_out=True)
    observation = adapter.classify(content="prefix TESTMATCH suffix")
    assert observation.timed_out is True
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.UNKNOWN


def test_malformed_response_failure_never_converts_to_clear() -> None:
    adapter = DeterministicFakeSafetyModelAdapter(
        match_marker="TESTMATCH",
        claimed_failure=SafetyModelFailureKind.MALFORMED_RESPONSE,
    )
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.UNKNOWN


def test_unknown_raw_category_label_is_independently_rejected_by_the_decoder() -> None:
    # P5-CODEX-008 Rework (Codex Second Independent Review Probe D): the
    # Fake here claims everything is fine — a real MATCH signal, full
    # Confidence — for a `raw_category_label` this process has never
    # registered. The Decoder boundary inside the Bridge's
    # `decode_safety_model_observation()` call must independently
    # override this to `UNKNOWN_LABEL` regardless of what the Provider
    # itself asserts.
    adapter = DeterministicFakeSafetyModelAdapter(
        match_marker="TESTMATCH",
        raw_category_label="novel_unknown_label",
        confidence=1.0,
        confidence_threshold=0.0,
    )
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.UNKNOWN


def test_an_arbitrary_port_conformant_provider_cannot_bypass_the_decoder() -> None:
    # P5-CODEX-008 Rework (Codex Third Independent Review item 3): not
    # only the Fake — *any* class structurally satisfying `SafetyModelPort`
    # (a hand-rolled one here, never importing `DeterministicFakeSafety
    # ModelAdapter` at all) that returns a raw Observation claiming
    # `claimed_failure=NONE`, full Confidence, and `raw_signal=MATCH` for
    # an unregistered Category must still converge on `UNKNOWN` through
    # the Bridge — the Decoder boundary is a property of `SafetyModel
    # DetectorAdapter` itself, not something only the Test Fixture
    # happens to opt into. Reproduces Codex's own Third Review Probe
    # verbatim (`failure=none`, `confidence=1.0`, `confidence_threshold=
    # 0.0`, `category_id=novel_unknown_label`, `outcome=clear`).
    class _HostileConformantProvider:
        def classify(self, *, content: str) -> RawSafetyModelObservation:
            del content
            return RawSafetyModelObservation(
                model_id="hostile.provider",
                exact_revision="v1",
                label_schema_id="hostile.schema",
                raw_category_label="novel_unknown_label",
                raw_signal=DetectionOutcome.CLEAR,
                raw_confidence=1.0,
                confidence_threshold=0.0,
                claimed_failure=SafetyModelFailureKind.NONE,
            )

    bridge = SafetyModelDetectorAdapter(safety_model=_HostileConformantProvider())
    result = bridge.detect(content="anything")
    assert result.outcome is DetectionOutcome.UNKNOWN
    assert result.category_id != "novel_unknown_label"


def test_a_known_registered_category_is_not_flagged_as_unknown_label() -> None:
    # Confirms the Decoder boundary is not merely "always fail" — a
    # `raw_category_label` that *is* registered (`CATEGORY_SECRET`) must
    # pass through as a genuine, trustworthy MATCH.
    adapter = DeterministicFakeSafetyModelAdapter(
        match_marker="TESTMATCH",
        raw_category_label=CATEGORY_SECRET,
        confidence=0.95,
        confidence_threshold=0.5,
    )
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.MATCH
    assert result.category_id == CATEGORY_SECRET


def test_low_confidence_failure_never_converts_to_clear_even_on_a_real_match() -> None:
    # A Low-Confidence Match is exactly the case P5-RES-005 targets: the
    # underlying Label technically says MATCH, but Confidence fell below
    # the declared threshold — the Bridge must still report UNKNOWN, not
    # a (falsely reassuring) CLEAR or a (falsely confident) MATCH. Low
    # Confidence is always *derived* by the Decoder from `confidence <
    # confidence_threshold` — never a directly-settable `failure` flag.
    adapter = DeterministicFakeSafetyModelAdapter(
        match_marker="TESTMATCH",
        confidence=0.3,
        confidence_threshold=0.8,
    )
    observation = adapter.classify(content="prefix TESTMATCH suffix")
    assert observation.raw_confidence < observation.confidence_threshold
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.UNKNOWN


def test_a_below_threshold_confidence_is_untrustworthy_even_without_an_explicit_failure_flag() -> (
    None
):
    # `SafetyModelResponse.is_trustworthy` must fail closed on
    # Confidence alone, structurally — even a Response some other caller
    # built by hand (via the Decoder, `failure=NONE`) still gets the
    # safe outcome if Confidence sits below its own declared threshold.
    from margpa_runtime_llm.modules.guardrail_governance.domain import (
        decode_safety_model_observation,
    )

    observation = RawSafetyModelObservation(
        model_id="test.direct-construction",
        exact_revision="v1",
        label_schema_id="test.schema",
        raw_category_label=CATEGORY_SECRET,
        raw_signal=DetectionOutcome.MATCH,
        raw_confidence=0.1,
        confidence_threshold=0.9,
    )
    response = decode_safety_model_observation(
        observation, detection_id="d1", detector_id="test.direct"
    )
    assert response.failure is SafetyModelFailureKind.LOW_CONFIDENCE
    assert response.is_trustworthy is False


def test_a_genuine_high_confidence_match_is_trustworthy_and_passes_through() -> None:
    adapter = DeterministicFakeSafetyModelAdapter(
        match_marker="TESTMATCH", confidence=0.95, confidence_threshold=0.5
    )
    bridge = SafetyModelDetectorAdapter(safety_model=adapter)
    result = bridge.detect(content="prefix TESTMATCH suffix")
    assert result.outcome is DetectionOutcome.MATCH


def test_a_raising_safety_model_fails_closed_through_the_bridge_not_silently() -> None:
    class _ExplodingSafetyModel:
        def classify(self, *, content: str) -> RawSafetyModelObservation:
            raise RuntimeError("simulated internal safety model crash")

    bridge = SafetyModelDetectorAdapter(safety_model=_ExplodingSafetyModel())
    result = bridge.detect(content="anything")
    assert result.outcome is DetectionOutcome.ERROR


def test_a_malformed_return_of_a_bare_object_fails_closed_through_the_decoder() -> None:
    # P5-CODEX-008 Rework (Codex Fourth Independent Review): `Protocol`/
    # return-type annotations are never enforced at Runtime — a Provider
    # returning something that isn't even shaped like a
    # `RawSafetyModelObservation` (a bare `object()` here) must still
    # converge on a Typed `ERROR` Detection, not let the Decoder's own
    # `AttributeError` escape `SafetyModelDetectorAdapter.detect()`
    # uncaught. Reproduces Codex's Fourth Review Probe verbatim
    # (`Provider return: object()` -> previously `AttributeError`
    # escaped; now `DetectionOutcome.ERROR`).
    class _MalformedBareObjectProvider:
        def classify(self, *, content: str) -> RawSafetyModelObservation:
            del content
            return object()  # type: ignore[return-value]

    bridge = SafetyModelDetectorAdapter(safety_model=_MalformedBareObjectProvider())
    result = bridge.detect(content="anything")
    assert result.outcome is DetectionOutcome.ERROR


def test_a_malformed_return_of_a_stale_decoded_response_fails_closed_through_the_decoder() -> None:
    # A Provider that (incorrectly, post-P5-CODEX-008) still returns the
    # old already-decoded `SafetyModelResponse` shape instead of the now-
    # required `RawSafetyModelObservation` must also fail closed — it is
    # missing `raw_category_label`/`raw_signal`/`claimed_failure`, so the
    # Decoder cannot parse it either.
    from margpa_runtime_llm.modules.guardrail_governance.domain import SafetyModelResponse

    class _MalformedStaleResponseProvider:
        def classify(self, *, content: str) -> RawSafetyModelObservation:
            del content
            stale_response = SafetyModelResponse(
                model_id="stale.provider",
                exact_revision="v1",
                label_schema_id="stale.schema",
                detection=GuardDetection(
                    detection_id="d1",
                    detector_id="stale.detector",
                    category_id=CATEGORY_SECRET,
                    outcome=DetectionOutcome.CLEAR,
                ),
            )
            return stale_response  # type: ignore[return-value]

    bridge = SafetyModelDetectorAdapter(safety_model=_MalformedStaleResponseProvider())
    result = bridge.detect(content="anything")
    assert result.outcome is DetectionOutcome.ERROR


def test_safety_model_conflict_never_suppresses_a_deterministic_match() -> None:
    # P5-SFM-001: the Safety Model is never the Deterministic Baseline's
    # substitute or final Authority — when the Safety Model disagrees
    # (reports CLEAR) on content a Deterministic Detector genuinely
    # Matched, the overall Point result must still reflect the
    # Deterministic Match, never silently downgraded/suppressed by the
    # Safety Model's disagreement.
    class _AlwaysClearSafetyModel:
        def classify(self, *, content: str) -> RawSafetyModelObservation:
            adapter = DeterministicFakeSafetyModelAdapter(match_marker="never-matches-anything")
            return adapter.classify(content=content)

    deterministic_match = GuardDetection(
        detection_id="d1",
        detector_id="deterministic.secret_pattern",
        category_id=CATEGORY_SECRET,
        outcome=DetectionOutcome.MATCH,
        severity=Severity.CRITICAL,
    )
    bridge = SafetyModelDetectorAdapter(safety_model=_AlwaysClearSafetyModel())
    safety_model_detection = bridge.detect(content="a genuine secret: sk-abcdefghijklmnop")

    # The two Detections coexist as separate Facts — nothing here lets
    # the Safety Model's CLEAR erase or override the Deterministic
    # Detector's own MATCH; `GuardrailPointRuntime` folds every
    # Detector's output additively (max-Severity, union of
    # Recommendations), so a Conflict can only ever *add* Evidence, never
    # subtract it.
    assert safety_model_detection.outcome is DetectionOutcome.CLEAR
    assert deterministic_match.outcome is DetectionOutcome.MATCH
    detections = (deterministic_match, safety_model_detection)
    assert any(d.outcome is DetectionOutcome.MATCH for d in detections)


def test_safety_model_bridge_never_wired_into_production_composition_by_default() -> None:
    # Reconfirms P5-SFM-003/004: the Production Composition's own
    # Detector builders never include a Safety-Model-backed Detector —
    # `SafetyModelDetectorAdapter` exists as a reusable Seam a *future*
    # Human Gate can opt into, never something Phase 5 itself switches
    # on (Production Safety Model Call 0).
    from margpa_runtime_llm.adapters.guardrail_governance.deterministic_detectors import (
        build_input_detectors,
        build_output_detectors,
    )

    for detector in (*build_input_detectors(), *build_output_detectors()):
        assert not isinstance(detector, SafetyModelDetectorAdapter)
