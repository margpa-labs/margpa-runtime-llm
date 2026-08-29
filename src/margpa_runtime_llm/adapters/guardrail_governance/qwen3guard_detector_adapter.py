"""Additive `DetectorPort` wrapping a dynamically-Activated Qwen3Guard-Gen
Adapter (P6-RR-O-WU-002, Production Wiring Delta; resolves P6-CODEX-048).

Detector Registry membership must stay static (P5-CODEX-007's Entry/
Resolution Binding requires one fixed, self-consistent Detector set per
Point — see `point_runtime.py`), while dedicated-Model *availability* is
dynamic (`RoleProviderLifecycleManager`, only Active after a successful
Mode Activation). This module resolves that mismatch the same way
`judge_live_integration.py`'s `judge_provider_is_built_in` resolver does:
always registered, resolved fresh on every `detect()` call, never
constructed once and cached.

When the dedicated Guard is not currently Active, this Detector reports
`DetectionOutcome.UNAVAILABLE` (never `CLEAR` — CLEAR asserts "scanned,
found nothing"; UNAVAILABLE means "did not scan") and never blocks the
Rule/Pattern Detectors it runs alongside (P6-RR-DELTA §4.3 "Qwen3Guard
Resultは...加算する...Qwen3Guard Model unavailable時のMode RollbackとFailure
表示を保証する" — the Mode/Activation half of that contract is
`role_provider_lifecycle`'s job; this module is the additive-merge half).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_UNKNOWN_UNRESOLVED,
    CATEGORY_UNSAFE_CONTENT,
    DetectionOutcome,
    GuardDetection,
    ModelDetectionProvenance,
    Qwen3GuardClassification,
    Qwen3GuardTarget,
    Severity,
)

from .qwen3guard_adapter import Qwen3GuardGenAdapter

_SEVERITY_ORDER = (Severity.NONE, Severity.LOW, Severity.MODERATE, Severity.HIGH, Severity.CRITICAL)

# Model-backed: classifies the whole scan target as one unit, not a
# literal-string span. This Detector is never registered with
# `IncrementalStreamGuard`'s Holdback Window (it is added only to the
# static `GuardrailPointRuntime` Detector sets for guardrail.input/
# output_candidate/context_source), so this bound is a documented,
# conservative placeholder rather than a Stream-Release-relevant contract.
_MODEL_BACKED_MAX_MATCH_LENGTH = 4096


@dataclass(frozen=True, slots=True)
class Qwen3GuardRoleTurn:
    """P6-RR-R21 (resolves P6-CODEX-086): pairs the concrete
    `Qwen3GuardGenAdapter` with an opaque Turn Lease token, both produced
    together by one atomic `begin_role_turn` call — mirrors
    `role_lifecycle_manager.RoleTurnHandle` one layer up, kept as its own
    small type here so this module still never imports a concrete
    `runtime_model_control` Lifecycle type (matching `judge_live_
    integration.py`'s identical Provider-neutral boundary discipline)."""

    adapter: Qwen3GuardGenAdapter
    lease: object


class Qwen3GuardDetectorAdapter:
    detector_id = "safety_model.qwen3guard_gen"
    max_match_length = _MODEL_BACKED_MAX_MATCH_LENGTH

    def __init__(
        self,
        *,
        target: Qwen3GuardTarget,
        begin_role_turn: Callable[[], Qwen3GuardRoleTurn | None],
        end_role_turn: Callable[[object], None],
    ) -> None:
        self._target = target
        self._begin_role_turn = begin_role_turn
        self._end_role_turn = end_role_turn

    def _release(self, lease: object) -> None:
        try:
            self._end_role_turn(lease)
        except Exception:
            pass

    def detect(self, *, content: str) -> GuardDetection:
        # P6-RR-R21 (resolves P6-CODEX-086): resolving the Adapter and
        # acquiring its Turn Lease happen together, in one call
        # (`begin_role_turn`, backed by `RoleProviderLifecycleManager.
        # begin_role_turn()`'s single-Lock-acquisition contract) — the
        # previous design resolved the Adapter here and never acquired any
        # Lease at all, so a concurrent Provider switch, Mode OFF, or
        # Shutdown could Unload this exact Adapter while `classify_point`
        # below was still mid-call.
        try:
            turn = self._begin_role_turn()
        except Exception:
            turn = None
        if turn is None:
            return GuardDetection(
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.UNAVAILABLE,
            )
        try:
            classification = turn.adapter.classify_point(target=self._target, content=content)
        except Exception:
            return GuardDetection(
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.ERROR,
            )
        finally:
            # Exactly-once Release on every path out of this `try` — the
            # early UNAVAILABLE `return` above never reaches here (no
            # Lease was ever acquired for it), and both the ERROR `return`
            # and the normal fall-through below run this `finally` first.
            self._release(turn.lease)
        # P6-RR-R27 (resolves P6-CODEX-091): every real `classification`
        # this point onward — Clear, Match, Unknown, Timeout, Malformed —
        # already carries genuine Identity (`Qwen3GuardGenAdapter` always
        # populates it, success or typed failure alike). Projected onto
        # the Generic `GuardDetection` this method returns, so real
        # Provider Identity survives from Result to Evidence instead of
        # being silently discarded at this exact narrowing boundary.
        provenance = _provenance_for(classification)
        if not classification.detections:
            return GuardDetection(
                detection_id=str(uuid4()),
                detector_id=self.detector_id,
                category_id=CATEGORY_UNSAFE_CONTENT,
                outcome=DetectionOutcome.CLEAR,
                model_provenance=provenance,
            )
        # `classify_point()` may report multiple mapped Categories; this
        # Port's contract is one GuardDetection per Detector per call, so
        # the single most severe one is surfaced (never silently averaged
        # or the first one picked arbitrarily).
        highest = max(
            classification.detections,
            key=lambda item: _SEVERITY_ORDER.index(item.severity),
        )
        return GuardDetection(
            detection_id=highest.detection_id,
            detector_id=self.detector_id,
            category_id=highest.category_id,
            outcome=highest.outcome,
            confidence=highest.confidence,
            severity=highest.severity,
            model_provenance=provenance,
        )


def _provenance_for(classification: Qwen3GuardClassification) -> ModelDetectionProvenance:
    return ModelDetectionProvenance(
        model_id=classification.model_id,
        exact_revision=classification.exact_revision,
        artifact_digest_sha512=classification.artifact_digest_sha512,
        contract_manifest_digest_sha512=classification.contract_manifest_digest_sha512,
        label_schema_id=classification.label_schema_id,
    )


__all__ = ["Qwen3GuardDetectorAdapter", "Qwen3GuardRoleTurn"]
