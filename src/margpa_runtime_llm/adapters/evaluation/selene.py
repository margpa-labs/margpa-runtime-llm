"""Dedicated Selene prompt/decoder/runtime adapter.

The checked-in manifest is fail-closed: without a verified official template
copy and immutable upstream revision, production prompt construction is
unavailable.  Tests may provide an explicit verified fixture manifest/template
to exercise the adapter contract without mislabelling a remembered prompt as
official.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    decode_judge_output,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeCriterionDisposition,
    JudgeIndependenceClass,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterionDisposition,
    SemanticCriterionResult,
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

    def __init__(self, *, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._manifest = load_selene_prompt_manifest(manifest_path)

    @property
    def manifest(self) -> SelenePromptManifest:
        return self._manifest

    def build(self, *, request: SemanticEvaluationRequest) -> str:
        manifest = self._manifest
        if (
            not manifest.verified_official_copy
            or manifest.upstream_revision is None
            or manifest.template_file is None
            or manifest.template_sha512 is None
        ):
            raise SelenePromptUnavailable(manifest.retrieval_status)
        template_path = self._manifest_path.parent / manifest.template_file
        template = template_path.read_text(encoding="utf-8")
        digest = hashlib.sha512(template.encode("utf-8")).hexdigest()
        if digest != manifest.template_sha512:
            raise SelenePromptUnavailable("template_digest_mismatch")
        if any(placeholder not in template for placeholder in self._REQUIRED_PLACEHOLDERS):
            raise SelenePromptUnavailable("template_placeholder_contract_mismatch")
        criteria = "\n".join(
            (
                f"{item.criterion_id} | {item.evaluation_method.value} | "
                f"{item.instruction} | source={item.source_pointer}"
            )
            for item in request.snapshot.criteria
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


class SeleneSemanticEvaluator:
    def __init__(
        self,
        *,
        service: InferenceService,
        model_key: str,
        prompt_adapter: SelenePromptAdapter,
        max_new_tokens: int = 1000,
    ) -> None:
        self._service = service
        self._model_key = model_key
        self._prompt_adapter = prompt_adapter
        self._max_new_tokens = max_new_tokens

    @property
    def inference_service(self) -> InferenceService:
        """The loaded dedicated service, retained for frozen repair rejudge."""
        return self._service

    def evaluate(self, *, request: SemanticEvaluationRequest) -> SemanticEvaluationResponse:
        started = time.monotonic()
        try:
            prompt = self._prompt_adapter.build(request=request)
            generated = self._service.generate(
                GenerationRequest(
                    request_id=f"{request.snapshot.request_id}:selene",
                    model_key=self._model_key,
                    messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
                    parameters=GenerationParameters(max_new_tokens=self._max_new_tokens),
                )
            )
            decoded = decode_judge_output(
                raw_text=generated.content,
                judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
                token_usage=(
                    generated.usage.completion_tokens if generated.usage is not None else 0
                ),
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                expected_criterion_ids=tuple(
                    item.criterion_id for item in request.snapshot.criteria
                ),
            )
        except Exception as exc:
            return SemanticEvaluationResponse(
                request_id=request.snapshot.request_id,
                generation=request.snapshot.generation,
                provider_id=self._model_key,
                provider_state=SemanticProviderState.UNAVAILABLE,
                results=(),
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                failure_reason=f"selene_unavailable:{type(exc).__name__}",
            )
        results = tuple(
            SemanticCriterionResult(
                criterion_id=item.criterion_id,
                descriptor_id=next(
                    criterion.descriptor_id
                    for criterion in request.snapshot.criteria
                    if criterion.criterion_id == item.criterion_id
                ),
                disposition={
                    JudgeCriterionDisposition.PASS: SemanticCriterionDisposition.PASS,
                    JudgeCriterionDisposition.DEVIATION: (SemanticCriterionDisposition.DEVIATION),
                    JudgeCriterionDisposition.UNKNOWN: SemanticCriterionDisposition.UNKNOWN,
                }[item.disposition],
                confidence=item.confidence,
                reason_code=item.reason_code,
                evidence_refs=item.evidence_refs,
            )
            for item in decoded.criterion_results
        )
        return SemanticEvaluationResponse(
            request_id=request.snapshot.request_id,
            generation=request.snapshot.generation,
            provider_id=self._model_key,
            provider_state=SemanticProviderState.ACTIVE,
            results=results,
            latency_ms=decoded.latency_ms,
        )
