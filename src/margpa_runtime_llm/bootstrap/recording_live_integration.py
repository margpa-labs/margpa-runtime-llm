"""Live Recording Integration (P6-CODEX-011, Second Rework).

Decoupled entirely from Judge: `build_recording_completion_hook()`'s Hook is
wired directly into `ConversationGenerationSession._completed_event()` via
`RecordingCompletionHook`, independent of Judge Mode (ADR-6-013 Mode
orthogonality) — Recording FULL/METADATA now produces a record for every
completed Turn whether or not Judge ever ran, and Judge OFF/ENFORCE has zero
effect on whether a Turn gets recorded.

`build_judge_evidence_recorder()` is a second, separate Recording call site
used only by `judge_live_integration.py`'s own Background Task, writing a
Judge Run's own Provenance (Model/Artifact identity, Rubric, Prompt Digest,
Recommendation/Confidence, Token/Latency/Call traces, and, when Repair ran,
its Outcome/Acceptance/new Turn correlation) into a distinct file so it
never collides with (or is gated by) the Turn's own recording above.

Both call sites are best-effort and fail-closed with an explicit Degraded
projection (`RecordingCompositionState`) rather than a silent drop — a
Recording bug or a Quota/Path rejection is visible to a Status reader, but
never allowed to affect the Canonical Turn or the Judge Run itself.
"""

from __future__ import annotations

import hashlib
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    RecordingPathRejected,
    RecordingQuotaExceeded,
    RecordingWriteFailure,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
    RecordingCompletionHook,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_service import (
    RecordingService,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import (
    MetadataValue,
    RecordingMode,
)
from margpa_runtime_llm.modules.runtime_observability.ports import RecordingWriterPort

_RecordingFailure = (RecordingWriteFailure, RecordingQuotaExceeded, RecordingPathRejected)


@dataclass(frozen=True, slots=True)
class RecordingOutcome:
    request_id: str
    ok: bool
    degraded_reason: str | None


class RecordingCompositionState:
    """Last-outcome tracker (P6-CODEX-011: no silent drop). A Status reader
    can distinguish "Recording is OFF" (no state change at all — the Hook
    returns before touching this) from "Recording tried and Degraded"
    (`ok=False`, a concrete `degraded_reason`)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last: RecordingOutcome | None = None

    def record_ok(self, *, request_id: str) -> None:
        with self._lock:
            self._last = RecordingOutcome(request_id=request_id, ok=True, degraded_reason=None)

    def record_degraded(self, *, request_id: str, reason: str) -> None:
        with self._lock:
            self._last = RecordingOutcome(request_id=request_id, ok=False, degraded_reason=reason)

    def last_outcome(self) -> RecordingOutcome | None:
        with self._lock:
            return self._last


def build_recording_completion_hook(
    *,
    recording_mode_controller: RecordingModeController,
    writer: RecordingWriterPort,
    metadata_fields_provider: (
        Callable[[JudgeCompletionContext], dict[str, MetadataValue]] | None
    ) = None,
) -> tuple[RecordingCompletionHook, RecordingCompositionState]:
    state = RecordingCompositionState()

    def hook(context: JudgeCompletionContext) -> None:
        mode = recording_mode_controller.mode_snapshot().current_mode
        if mode is RecordingMode.OFF:
            return
        # P6-CODEX-025 (Fourth Rework): the provider receives this Attempt's
        # own Context so Recorded Model Identity always matches what this
        # specific Turn actually ran with, never a bootstrap-frozen value
        # that goes stale across a live Runtime Model Switch.
        metadata_fields = (
            metadata_fields_provider(context) if metadata_fields_provider is not None else {}
        )
        service = RecordingService(mode=mode, writer=writer)
        try:
            service.record(
                request_id=context.request_id,
                timestamp=datetime.now(UTC).isoformat(),
                metadata_fields=metadata_fields,
                canonical_input=context.user_input,
                presented_answer=context.assistant_content,
            )
        except _RecordingFailure as exc:
            state.record_degraded(
                request_id=context.request_id, reason=f"{type(exc).__name__}: {exc}"
            )
            return
        state.record_ok(request_id=context.request_id)

    return hook, state


JudgeEvidenceRecorder = Callable[..., None]


def build_judge_evidence_recorder(
    *,
    writer: RecordingWriterPort,
) -> tuple[JudgeEvidenceRecorder, RecordingCompositionState]:
    """A Judge Run's own Evidence (Model/Artifact/Backend, Prompt/Rubric
    Digest, Token/Latency/Call traces) written to its own file, distinct
    from the Turn-level record `build_recording_completion_hook` produces —
    never gated by, or gating, that other Hook.

    P6-CODEX-029 (Fourth Rework): `recording_mode` is no longer read here
    from a live `RecordingModeController` at write-time — the caller
    (`judge_live_integration.py`'s Hook) now passes the exact value it
    already froze, together with `judge_mode`/`repair_mode`, at Hook entry.
    Reading it fresh here, on the Background Thread, potentially long
    after Hook entry, meant a live Recording Mode change mid-Run could
    still affect whether that already-in-flight Run's own Evidence got
    written — this function no longer takes a `recording_mode_controller`
    at all, so there is no live value left to accidentally re-read."""

    state = RecordingCompositionState()

    def record_judge_evidence(
        *,
        request_id: str,
        recording_mode: RecordingMode,
        model_identity: str,
        judge_role: str,
        rubric_id: str,
        prompt: str,
        recommendation: str,
        confidence: float,
        token_usage: int,
        latency_ms: int,
        execution_state: str,
        failure_reason: str | None = None,
        repair_outcome: str | None = None,
        repair_accepted: bool | None = None,
        repair_new_turn_id: str | None = None,
        seed: int | None = None,
        config_digest_sha512: str | None = None,
        artifact_digest_sha512: str | None = None,
        backend_key: str | None = None,
        backend_version: str | None = None,
    ) -> None:
        mode = recording_mode
        if mode is RecordingMode.OFF:
            return
        evidence_request_id = f"{request_id}-judge-evidence"
        metadata_fields: dict[str, MetadataValue] = {
            "artifact_kind": "judge_run_evidence",
            "model_identity": model_identity,
            # P6-CODEX-022: the previous cut only ever recorded
            # `model_identity` (a bare config key, e.g. "main.qwen3-4b") —
            # P6-LJG-002's "necessary Traces" also names the Artifact and
            # Backend actually loaded, which `model_identity` alone cannot
            # distinguish across a re-download or a backend upgrade of the
            # same config key. Explicit `unavailable` (never a fabricated
            # value) when the caller has no `ModelRuntimeInfo` to draw from
            # (e.g. a unit test's Fake Inference Service).
            "artifact_digest_sha512": artifact_digest_sha512 or "unavailable",
            "backend_key": backend_key or "unavailable",
            "backend_version": backend_version or "unavailable",
            "judge_role": judge_role,
            "rubric_id": rubric_id,
            "prompt_digest_sha512": hashlib.sha512(prompt.encode("utf-8")).hexdigest(),
            "recommendation": recommendation,
            "confidence": confidence,
            "token_usage": token_usage,
            "latency_ms": latency_ms,
            "call_count": 1,
            "execution_state": execution_state,
            # Explicit, honest absence rather than omission: this Judge call
            # never pins a seed today (deterministic decoding is not
            # requested), so `seed_pinned=False` is itself the accurate
            # Evidence, not a gap to hide by leaving the field out.
            "seed_pinned": seed is not None,
            "seed": seed if seed is not None else "unpinned",
            "config_digest_sha512": config_digest_sha512 or "unavailable",
            # No per-call monetary Cost is ever computed in this local,
            # no-external-API environment — represented explicitly as
            # unavailable rather than a fabricated estimate.
            "cost_estimate_available": False,
        }
        if failure_reason is not None:
            metadata_fields["failure_reason"] = failure_reason
        if repair_outcome is not None:
            metadata_fields["repair_outcome"] = repair_outcome
        if repair_accepted is not None:
            metadata_fields["repair_accepted"] = repair_accepted
        if repair_new_turn_id is not None:
            metadata_fields["repair_new_turn_id"] = repair_new_turn_id
        service = RecordingService(mode=mode, writer=writer)
        try:
            service.record(
                request_id=evidence_request_id,
                timestamp=datetime.now(UTC).isoformat(),
                metadata_fields=metadata_fields,
                # The raw Prompt/Reasoning text is never persisted as
                # Evidence (only its digest, above) — Judge Evidence is a
                # Metadata-shaped record regardless of Recording Mode.
                canonical_input=None,
                presented_answer=None,
            )
        except _RecordingFailure as exc:
            state.record_degraded(
                request_id=evidence_request_id, reason=f"{type(exc).__name__}: {exc}"
            )
            return
        state.record_ok(request_id=evidence_request_id)

    return record_judge_evidence, state
