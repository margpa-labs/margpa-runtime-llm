"""Dedicated Qwen3Guard-Gen adapter with exact fail-closed decoding."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_UNKNOWN_UNRESOLVED,
    DetectionOutcome,
    Qwen3GuardClassification,
    Qwen3GuardDecodeError,
    Qwen3GuardTarget,
    RawSafetyModelObservation,
    SafetyModelFailureKind,
    decode_qwen3guard_output,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import SafetyModelUnavailable
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole

from .qwen3guard_manifest import Qwen3GuardManifestUnavailable, load_qwen3guard_manifest


class Qwen3GuardGenAdapter:
    """P6-RR-R23 (Post-Codex Independent Review Rework, resolves
    P6-CODEX-087): loads and validates its Official Contract Manifest at
    Construction time (Pydantic schema validation on `load_qwen3guard_
    manifest()` — a malformed Manifest file fails Adapter Construction
    itself, mirroring `SelenePromptAdapter.__init__`'s identical
    fail-fast-on-malformed-Manifest contract) and gates every real
    `classify_point()` call on the loaded Manifest's own `is_complete_and_
    verified` property — never on a caller-supplied `verified_official_
    contract` boolean in isolation (the previous shape here, and exactly
    the gap P6-CODEX-087 flagged).

    P6-RR-R27 (Post-Codex Independent Review Rework, resolves the
    Adapter-side half of P6-CODEX-090): Construction also requires the
    loaded Manifest's own `provider_id` to equal this exact `model_id` —
    a checked-in Manifest pointed at the wrong Model config (e.g. a
    future second dedicated Model reusing this Adapter class by mistake)
    fails Construction itself, never silently reports Identity for a
    Model it was not actually verified against."""

    def __init__(
        self,
        *,
        service: InferenceService,
        model_id: str,
        artifact_digest_sha512: str,
        manifest_path: Path,
        max_new_tokens: int = 256,
    ) -> None:
        self._service = service
        self._model_id = model_id
        self._artifact_digest = artifact_digest_sha512
        self._manifest_path = manifest_path
        self._manifest = load_qwen3guard_manifest(manifest_path)
        if self._manifest.provider_id != model_id:
            raise Qwen3GuardManifestUnavailable(
                f"manifest_provider_id_mismatch:{self._manifest.provider_id}!={model_id}"
            )
        self._manifest_digest_sha512 = hashlib.sha512(manifest_path.read_bytes()).hexdigest()
        self._max_new_tokens = max_new_tokens

    @property
    def manifest_digest_sha512(self) -> str:
        return self._manifest_digest_sha512

    def classify(self, *, content: str) -> RawSafetyModelObservation:
        classification = self.classify_point(target=Qwen3GuardTarget.INPUT, content=content)
        primary = classification.detections[0]
        if classification.failure is SafetyModelFailureKind.UNKNOWN_LABEL:
            raw_category = classification.categories[0]
            claimed_failure = SafetyModelFailureKind.NONE
        else:
            raw_category = primary.category_id
            claimed_failure = classification.failure
        return RawSafetyModelObservation(
            model_id=classification.model_id,
            exact_revision=classification.exact_revision,
            artifact_digest_sha512=classification.artifact_digest_sha512,
            label_schema_id=classification.label_schema_id,
            raw_category_label=raw_category,
            raw_signal=(
                DetectionOutcome.MATCH
                if primary.outcome is DetectionOutcome.MATCH
                else DetectionOutcome.CLEAR
            ),
            raw_confidence=1.0 if classification.failure is SafetyModelFailureKind.NONE else 0.0,
            confidence_threshold=1.0,
            timed_out=classification.failure is SafetyModelFailureKind.TIMEOUT,
            latency_ms=classification.latency_ms,
            call_count=classification.call_count,
            token_count=classification.token_count,
            claimed_failure=claimed_failure,
        )

    def classify_point(
        self,
        *,
        target: Qwen3GuardTarget,
        content: str,
        query: str | None = None,
    ) -> Qwen3GuardClassification:
        manifest = self._manifest
        # P6-RR-R23 (resolves P6-CODEX-087): `is_complete_and_verified`
        # checks the bare `verified_official_contract` flag together with
        # every Source Identity and Category-list field the Manifest
        # claims to carry — a genuinely incomplete Manifest can never
        # dispatch a real Model Call, even if `verified_official_contract`
        # alone were somehow `True`.
        if not manifest.is_complete_and_verified:
            raise SafetyModelUnavailable(manifest.retrieval_status)
        revision = manifest.huggingface_source.exact_revision
        assert revision is not None  # guaranteed by `is_complete_and_verified` above
        started = time.monotonic()
        try:
            generated = self._service.generate(
                GenerationRequest(
                    request_id=f"qwen3guard:{target.value}",
                    model_key=self._model_id,
                    messages=_messages_for(target=target, content=content, query=query),
                    parameters=GenerationParameters(max_new_tokens=self._max_new_tokens),
                )
            )
            latency_ms = max(0, int((time.monotonic() - started) * 1000))
            return decode_qwen3guard_output(
                raw_text=generated.content,
                target=target,
                # P6-RR-R23 (resolves P6-CODEX-087 contract item 4): the
                # Target-scoped subset of the Manifest's Category mapping
                # — e.g. `Jailbreak` is dropped for `OUTPUT_CANDIDATE`, so
                # the Strict Decoder treats it as an unknown label there,
                # never a silently-accepted one.
                category_mapping=manifest.category_mapping_for(target),
                model_id=self._model_id,
                exact_revision=revision,
                artifact_digest_sha512=self._artifact_digest,
                contract_manifest_digest_sha512=self._manifest_digest_sha512,
                # P6-RR-R27 (resolves the `label_schema_id` half of
                # P6-CODEX-090): projected from the verified Manifest,
                # never a second independent hardcoded literal.
                label_schema_id=manifest.label_schema_id,
                latency_ms=latency_ms,
                token_count=(
                    generated.usage.completion_tokens if generated.usage is not None else 0
                ),
            )
        except TimeoutError:
            return _failure_classification(
                model_id=self._model_id,
                revision=revision,
                artifact_digest=self._artifact_digest,
                manifest_digest=self._manifest_digest_sha512,
                label_schema_id=manifest.label_schema_id,
                target=target,
                failure=SafetyModelFailureKind.TIMEOUT,
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
            )
        except Qwen3GuardDecodeError:
            return _failure_classification(
                model_id=self._model_id,
                revision=revision,
                artifact_digest=self._artifact_digest,
                manifest_digest=self._manifest_digest_sha512,
                label_schema_id=manifest.label_schema_id,
                target=target,
                failure=SafetyModelFailureKind.MALFORMED_RESPONSE,
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
            )
        except Exception:
            return _failure_classification(
                model_id=self._model_id,
                revision=revision,
                artifact_digest=self._artifact_digest,
                manifest_digest=self._manifest_digest_sha512,
                label_schema_id=manifest.label_schema_id,
                target=target,
                failure=SafetyModelFailureKind.INTERNAL_ERROR,
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
            )


def _messages_for(
    *, target: Qwen3GuardTarget, content: str, query: str | None
) -> tuple[ChatMessage, ...]:
    if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
        return (
            ChatMessage(role=MessageRole.USER, content=query or "(no preceding user query)"),
            ChatMessage(role=MessageRole.ASSISTANT, content=content),
        )
    return (ChatMessage(role=MessageRole.USER, content=content),)


def _failure_classification(
    *,
    model_id: str,
    revision: str,
    artifact_digest: str,
    manifest_digest: str,
    label_schema_id: str,
    target: Qwen3GuardTarget,
    failure: SafetyModelFailureKind,
    latency_ms: int,
) -> Qwen3GuardClassification:
    from margpa_runtime_llm.modules.guardrail_governance.domain import GuardDetection

    return Qwen3GuardClassification(
        model_id=model_id,
        exact_revision=revision,
        artifact_digest_sha512=artifact_digest,
        contract_manifest_digest_sha512=manifest_digest,
        label_schema_id=label_schema_id,
        target=target,
        detections=(
            GuardDetection(
                detection_id="qwen3guard-failure",
                detector_id="safety_model.qwen3guard_gen",
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=DetectionOutcome.UNKNOWN,
            ),
        ),
        failure=failure,
        latency_ms=latency_ms,
    )
