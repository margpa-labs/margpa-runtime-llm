"""Dedicated Selene prompt/decoder/runtime adapter.

Manifest provenance is explicit and fail-closed:
1) a verified official copy with immutable upstream revision, or
2) a checked-in project-derived contract with its own immutable digest.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.bootstrap.stage_deadline import stage_deadline
from margpa_runtime_llm.bootstrap.tracked_stage_worker import (
    TrackedStageWorkerRegistry,
    run_tracked_stage,
)
from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    decode_judge_output,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeCriterionDisposition,
    JudgeIndependenceClass,
)
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    LOCAL_MACOS_SELENE_JUDGE_BUDGET,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationBudget,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticProviderState,
)


class SelenePromptManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1"
    provider_id: str = Field(min_length=1)
    template_type: str = Field(min_length=1)
    upstream_repository_url: str = Field(min_length=1)
    upstream_revision: str | None
    template_file: str | None
    template_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    derived_template_file: str | None = None
    derived_template_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    derived_from_upstream_revision: str | None = None
    derived_from_upstream_basis: str | None = Field(default=None, min_length=1)
    project_contract_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    retrieval_status: str = Field(min_length=1)
    verified_official_copy: bool


@dataclass(frozen=True, slots=True)
class SelenePromptUnavailable(Exception):
    reason: str

    def __str__(self) -> str:
        return f"Selene prompt unavailable: {self.reason}"


def load_selene_prompt_manifest(path: Path) -> SelenePromptManifest:
    return SelenePromptManifest.model_validate_json(path.read_text(encoding="utf-8"))


class SelenePromptAdapter:
    _REQUIRED_PLACEHOLDERS = (
        "{{query}}",
        "{{candidate}}",
        "{{reference}}",
        "{{criteria}}",
        "{{response_schema}}",
    )
    _PROJECT_DERIVED_TEMPLATE_TYPE = "project_derived_multi_criterion_v1"

    def __init__(self, *, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._manifest = load_selene_prompt_manifest(manifest_path)

    @property
    def manifest(self) -> SelenePromptManifest:
        return self._manifest

    def preflight_contract(self) -> None:
        """Fail-closed contract check used by dedicated-role preflight."""
        self._validated_template()

    def _derived_contract_digest(self, *, template_sha512: str) -> str:
        payload = {
            "contract_kind": self._PROJECT_DERIVED_TEMPLATE_TYPE,
            "decoder": "judge_output_decoder_v1",
            "required_placeholders": list(self._REQUIRED_PLACEHOLDERS),
            "template_sha512": template_sha512,
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha512(serialized.encode("utf-8")).hexdigest()

    def _validated_template(self) -> str:
        manifest = self._manifest
        template_file: str | None = None
        expected_digest: str | None = None
        if manifest.verified_official_copy:
            if manifest.upstream_revision is None:
                raise SelenePromptUnavailable("official_upstream_revision_missing")
            template_file = manifest.template_file
            expected_digest = manifest.template_sha512
        elif manifest.template_type == self._PROJECT_DERIVED_TEMPLATE_TYPE:
            template_file = manifest.derived_template_file
            expected_digest = manifest.derived_template_sha512
            if manifest.derived_from_upstream_revision is not None:
                raise SelenePromptUnavailable("unverified_basis_misrepresented_as_revision")
            if manifest.derived_from_upstream_basis is None:
                raise SelenePromptUnavailable("derived_from_basis_missing")
            if manifest.project_contract_digest_sha512 is None:
                raise SelenePromptUnavailable("project_contract_digest_missing")
        else:
            raise SelenePromptUnavailable(manifest.retrieval_status)
        if template_file is None or expected_digest is None:
            raise SelenePromptUnavailable(manifest.retrieval_status)
        template_path = self._manifest_path.parent / template_file
        template = template_path.read_text(encoding="utf-8")
        digest = hashlib.sha512(template.encode("utf-8")).hexdigest()
        if digest != expected_digest:
            raise SelenePromptUnavailable("template_digest_mismatch")
        if any(placeholder not in template for placeholder in self._REQUIRED_PLACEHOLDERS):
            raise SelenePromptUnavailable("template_placeholder_contract_mismatch")
        if not manifest.verified_official_copy:
            assert manifest.project_contract_digest_sha512 is not None
            contract_digest = self._derived_contract_digest(template_sha512=digest)
            if contract_digest != manifest.project_contract_digest_sha512:
                raise SelenePromptUnavailable("project_contract_digest_mismatch")
        return template

    def build(
        self,
        *,
        request: SemanticEvaluationRequest,
        criteria: tuple[SemanticCriterion, ...] | None = None,
    ) -> str:
        template = self._validated_template()
        criteria = "\n".join(
            (
                f"{item.criterion_id} | {item.evaluation_method.value} | "
                f"{item.instruction} | source={item.source_pointer}"
            )
            for item in (criteria if criteria is not None else request.snapshot.criteria)
        )
        schema = json.dumps(
            {
                "recommendation": "accept|needs_repair|unknown",
                "confidence": "0..1",
                "reasoning": "short string",
                "criterion_results": [
                    {
                        "criterion_id": "exact id",
                        "disposition": "pass|deviation|unknown",
                        "confidence": "0..1",
                        "reason_code": "short code",
                        "evidence_refs": ["short reference"],
                    }
                ],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        replacements = {
            "{{query}}": request.user_input,
            "{{candidate}}": request.candidate_answer,
            "{{reference}}": "\n".join(request.evidence_context) or "(none)",
            "{{criteria}}": criteria,
            "{{response_schema}}": schema,
        }
        prompt = template
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)
        return prompt


@dataclass(frozen=True, slots=True)
class _SeleneBatch:
    criteria: tuple[SemanticCriterion, ...]
    prompt: str
    prompt_tokens: int


@dataclass(frozen=True, slots=True)
class _SeleneBatchGeneration:
    generated: GenerationResult
    deadline_exceeded: bool


class SeleneSemanticEvaluator:
    def __init__(
        self,
        *,
        service: InferenceService,
        model_key: str,
        prompt_adapter: SelenePromptAdapter,
        max_new_tokens: int = 1000,
        max_criteria_per_call: int = 8,
        max_calls: int = 4,
        max_prompt_tokens_per_call: int = 4096,
        cancel_grace_ms: int = LOCAL_MACOS_SELENE_JUDGE_BUDGET.cancel_grace_ms,
        tracked_stage_registry: TrackedStageWorkerRegistry | None = None,
    ) -> None:
        self._service = service
        self._model_key = model_key
        self._prompt_adapter = prompt_adapter
        self._max_new_tokens = max(1, max_new_tokens)
        self._max_criteria_per_call = max(1, max_criteria_per_call)
        self._max_calls = max(0, max_calls)
        self._max_prompt_tokens_per_call = max(0, max_prompt_tokens_per_call)
        self._cancel_grace_ms = max(0, cancel_grace_ms)
        self._tracked_stage_registry = tracked_stage_registry

    @property
    def inference_service(self) -> InferenceService:
        """The loaded dedicated service, retained for frozen repair rejudge."""
        return self._service

    def evaluate(
        self,
        *,
        request: SemanticEvaluationRequest,
        cancellation: CancellationToken | None = None,
        inference_budget_ms: int = LOCAL_MACOS_SELENE_JUDGE_BUDGET.inference_budget_ms,
        late_worker_observer: Callable[[Future[object]], None] | None = None,
    ) -> SemanticEvaluationResponse:
        started = time.monotonic()
        calls_started = 0
        calls_completed = 0
        completion_tokens = 0
        prompt_tokens_by_call: list[int] = []
        deferred: list[SemanticCriterionResult] = []

        def budget(
            *,
            deadline_exceeded: bool = False,
            cancelled: bool = False,
        ) -> SemanticEvaluationBudget:
            return SemanticEvaluationBudget(
                max_criteria_per_call=self._max_criteria_per_call,
                max_calls=self._max_calls,
                max_prompt_tokens_per_call=self._effective_max_prompt_tokens(),
                max_output_tokens_per_call=self._max_new_tokens,
                context_limit_tokens=self._context_limit_tokens(),
                inference_deadline_ms=max(0, inference_budget_ms),
                calls_started=calls_started,
                calls_completed=calls_completed,
                prompt_tokens_by_call=tuple(prompt_tokens_by_call),
                completion_tokens=completion_tokens,
                budget_deferred_criteria=len(deferred),
                deadline_exceeded=deadline_exceeded,
                cancelled=cancelled,
            )

        def response(
            *,
            provider_state: SemanticProviderState,
            results: tuple[SemanticCriterionResult, ...] = (),
            failure_reason: str | None = None,
            deadline_exceeded: bool = False,
            cancelled: bool = False,
        ) -> SemanticEvaluationResponse:
            return SemanticEvaluationResponse(
                request_id=request.snapshot.request_id,
                generation=request.snapshot.generation,
                provider_id=self._model_key,
                provider_state=provider_state,
                results=results,
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                failure_reason=failure_reason,
                budget=budget(
                    deadline_exceeded=deadline_exceeded,
                    cancelled=cancelled,
                ),
            )

        if cancellation is not None and cancellation.is_cancelled():
            return response(
                provider_state=SemanticProviderState.FAILED,
                failure_reason="selene_cancelled",
                cancelled=True,
            )
        try:
            batches, deferred = self._plan_batches(request=request)
        except Exception as exc:
            return response(
                provider_state=SemanticProviderState.UNAVAILABLE,
                failure_reason=f"selene_unavailable:{type(exc).__name__}",
            )
        results: list[SemanticCriterionResult] = []
        for batch_index, batch in enumerate(batches, start=1):
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_cancelled",
                    cancelled=True,
                )
            call_cancellation = CancellationToken.linked_to(cancellation)
            calls_started += 1
            prompt_tokens_by_call.append(batch.prompt_tokens)

            def generate_batch(
                batch_index: int = batch_index,
                batch: _SeleneBatch = batch,
                call_cancellation: CancellationToken = call_cancellation,
            ) -> _SeleneBatchGeneration:
                return self._generate_batch(
                    request_id=f"{request.snapshot.request_id}:selene:{batch_index}",
                    prompt=batch.prompt,
                    cancellation=call_cancellation,
                    inference_budget_ms=max(0, inference_budget_ms),
                )

            try:
                stage_outcome = run_tracked_stage(
                    work=generate_batch,
                    budget_ms=max(0, inference_budget_ms) + self._cancel_grace_ms,
                    registry=self._tracked_stage_registry,
                    cancellation=call_cancellation,
                )
            except Exception as exc:
                if cancellation is not None and cancellation.is_cancelled():
                    return response(
                        provider_state=SemanticProviderState.FAILED,
                        failure_reason="selene_cancelled",
                        cancelled=True,
                    )
                return response(
                    provider_state=SemanticProviderState.UNAVAILABLE,
                    failure_reason=f"selene_unavailable:{type(exc).__name__}",
                )
            if stage_outcome.timed_out or stage_outcome.result is None:
                call_cancellation.cancel()
                if late_worker_observer is not None:
                    late_worker_observer(cast(Future[object], stage_outcome.future))
                if cancellation is not None and cancellation.is_cancelled():
                    return response(
                        provider_state=SemanticProviderState.FAILED,
                        failure_reason="selene_cancelled",
                        cancelled=True,
                    )
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_inference_deadline_exceeded",
                    deadline_exceeded=True,
                )
            calls_completed += 1
            generated = stage_outcome.result.generated
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_cancelled",
                    cancelled=True,
                )
            if stage_outcome.result.deadline_exceeded:
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_inference_deadline_exceeded",
                    deadline_exceeded=True,
                )
            if generated.finish_reason is FinishReason.CANCELLED:
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_generation_cancelled",
                    cancelled=True,
                )
            completion_tokens += (
                generated.usage.completion_tokens if generated.usage is not None else 0
            )
            try:
                decoded = decode_judge_output(
                    raw_text=generated.content,
                    judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
                    token_usage=(
                        generated.usage.completion_tokens if generated.usage is not None else 0
                    ),
                    latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                    expected_criterion_ids=tuple(item.criterion_id for item in batch.criteria),
                )
            except Exception as exc:
                return response(
                    provider_state=SemanticProviderState.UNAVAILABLE,
                    failure_reason=f"selene_unavailable:{type(exc).__name__}",
                )
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason="selene_cancelled",
                    cancelled=True,
                )
            criteria_by_id = {item.criterion_id: item for item in batch.criteria}
            results.extend(
                SemanticCriterionResult(
                    criterion_id=item.criterion_id,
                    descriptor_id=criteria_by_id[item.criterion_id].descriptor_id,
                    disposition={
                        JudgeCriterionDisposition.PASS: SemanticCriterionDisposition.PASS,
                        JudgeCriterionDisposition.DEVIATION: SemanticCriterionDisposition.DEVIATION,
                        JudgeCriterionDisposition.UNKNOWN: SemanticCriterionDisposition.UNKNOWN,
                    }[item.disposition],
                    confidence=item.confidence,
                    reason_code=item.reason_code,
                    evidence_refs=item.evidence_refs,
                )
                for item in decoded.criterion_results
            )
        return response(
            provider_state=SemanticProviderState.ACTIVE,
            results=tuple((*results, *deferred)),
        )

    def _context_limit_tokens(self) -> int | None:
        runtime_info = self._service.runtime_info
        return runtime_info.loaded_context_size if runtime_info is not None else None

    def _effective_max_prompt_tokens(self) -> int:
        context_limit = self._context_limit_tokens()
        if context_limit is None:
            return self._max_prompt_tokens_per_call
        return min(
            self._max_prompt_tokens_per_call,
            max(0, context_limit - self._max_new_tokens),
        )

    def _plan_batches(
        self,
        *,
        request: SemanticEvaluationRequest,
    ) -> tuple[tuple[_SeleneBatch, ...], list[SemanticCriterionResult]]:
        criteria = request.snapshot.criteria
        max_prompt_tokens = self._effective_max_prompt_tokens()
        batches: list[_SeleneBatch] = []
        deferred: list[SemanticCriterionResult] = []
        index = 0
        while index < len(criteria):
            if len(batches) >= self._max_calls:
                deferred.extend(self._deferred_results(criteria[index:]))
                break
            batch_criteria: list[SemanticCriterion] = []
            batch_prompt = ""
            batch_prompt_tokens = 0
            while index < len(criteria) and len(batch_criteria) < self._max_criteria_per_call:
                candidate = (*batch_criteria, criteria[index])
                prompt = self._prompt_adapter.build(request=request, criteria=candidate)
                prompt_tokens = self._service.count_chat_prompt_tokens(
                    (ChatMessage(role=MessageRole.USER, content=prompt),),
                    ThinkingMode.DISABLED,
                )
                if prompt_tokens > max_prompt_tokens:
                    if batch_criteria:
                        break
                    deferred.extend(self._deferred_results((criteria[index],)))
                    index += 1
                    continue
                batch_criteria = list(candidate)
                batch_prompt = prompt
                batch_prompt_tokens = prompt_tokens
                index += 1
            if batch_criteria:
                batches.append(
                    _SeleneBatch(
                        criteria=tuple(batch_criteria),
                        prompt=batch_prompt,
                        prompt_tokens=batch_prompt_tokens,
                    )
                )
        return tuple(batches), deferred

    @staticmethod
    def _deferred_results(
        criteria: tuple[SemanticCriterion, ...],
    ) -> tuple[SemanticCriterionResult, ...]:
        return tuple(
            SemanticCriterionResult(
                criterion_id=item.criterion_id,
                descriptor_id=item.descriptor_id,
                disposition=SemanticCriterionDisposition.DEFERRED,
                reason_code=SemanticDeferredReason.BUDGET_EXHAUSTED.value,
            )
            for item in criteria
        )

    def _generate_batch(
        self,
        *,
        request_id: str,
        prompt: str,
        cancellation: CancellationToken,
        inference_budget_ms: int,
    ) -> _SeleneBatchGeneration:
        with stage_deadline(
            cancellation=cancellation,
            budget_ms=inference_budget_ms,
        ) as deadline_exceeded:
            generated = self._service.generate(
                GenerationRequest(
                    request_id=request_id,
                    model_key=self._model_key,
                    messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
                    parameters=GenerationParameters(max_new_tokens=self._max_new_tokens),
                ),
                cancellation=cancellation,
            )
        return _SeleneBatchGeneration(
            generated=generated,
            deadline_exceeded=deadline_exceeded(),
        )
