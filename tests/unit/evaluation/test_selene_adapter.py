from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import (
    SelenePromptAdapter,
    SelenePromptUnavailable,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    ThinkingMode,
)
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationStage,
    SemanticProviderState,
)

_DIGEST = "a" * 128
_PROVIDER = "judge.selene-1-mini-llama-3.1-8b-q5-k-m"


def _criterion() -> SemanticCriterion:
    return SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512=_DIGEST,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512=_DIGEST,
        instruction="Do not contradict cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


def _request() -> SemanticEvaluationRequest:
    frozen = freeze_semantic_turn(
        request_id="selene-test",
        generation=1,
        criteria=(_criterion(),),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_PROVIDER,
        active_provider=_PROVIDER,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    return SemanticEvaluationRequest(
        snapshot=frozen.snapshot,
        stage="post",
        user_input="QUERY SENTINEL",
        candidate_answer="CANDIDATE SENTINEL",
        evidence_context=("REFERENCE SENTINEL",),
    )


def _verified_adapter(tmp_path: Path) -> SelenePromptAdapter:
    template = (
        "Query:\n{{query}}\nCandidate:\n{{candidate}}\nReference:\n{{reference}}\n"
        "Criteria:\n{{criteria}}\nSchema:\n{{response_schema}}\n"
    )
    template_path = tmp_path / "official-fixture.txt"
    template_path.write_text(template, encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "provider_id": _PROVIDER,
                "template_type": "verified_test_fixture",
                "upstream_repository_url": "https://example.invalid/fixture",
                "upstream_revision": "f" * 40,
                "template_file": template_path.name,
                "template_sha512": hashlib.sha512(template.encode()).hexdigest(),
                "retrieval_status": "verified_test_fixture_only",
                "verified_official_copy": True,
            }
        ),
        encoding="utf-8",
    )
    return SelenePromptAdapter(manifest_path=manifest_path)


def _unresolved_adapter(tmp_path: Path) -> SelenePromptAdapter:
    manifest_path = tmp_path / "manifest-unresolved.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "provider_id": _PROVIDER,
                "template_type": "official_selene_prompt_template_unresolved",
                "upstream_repository_url": "https://example.invalid/upstream",
                "upstream_revision": None,
                "template_file": None,
                "template_sha512": None,
                "retrieval_status": "unavailable_network_prohibited_by_exact_resume_authority",
                "verified_official_copy": False,
            }
        ),
        encoding="utf-8",
    )
    return SelenePromptAdapter(manifest_path=manifest_path)


def test_production_manifest_builds_with_project_derived_contract() -> None:
    manifest_path = Path(__file__).parents[3] / "config/judge_templates/selene/manifest.json"
    adapter = SelenePromptAdapter(manifest_path=manifest_path)
    assert adapter.manifest.verified_official_copy is False
    assert adapter.manifest.template_type == "project_derived_multi_criterion_v1"
    prompt = adapter.build(request=_request())
    assert "QUERY SENTINEL" in prompt
    assert "semantic.argd.evidence.1" in prompt


def test_unresolved_manifest_stays_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(SelenePromptUnavailable, match="network_prohibited"):
        _unresolved_adapter(tmp_path).build(request=_request())


def test_prompt_adapter_preserves_query_candidate_reference_and_criterion(
    tmp_path: Path,
) -> None:
    prompt = _verified_adapter(tmp_path).build(request=_request())
    assert "QUERY SENTINEL" in prompt
    assert "CANDIDATE SENTINEL" in prompt
    assert "REFERENCE SENTINEL" in prompt
    assert "semantic.argd.evidence.1" in prompt
    assert "classification_with_reference" in prompt
    assert "criterion_results" in prompt


@dataclass(frozen=True)
class _Usage:
    completion_tokens: int = 17


@dataclass(frozen=True)
class _Generated:
    content: str
    usage: _Usage | None = _Usage()
    finish_reason: FinishReason = FinishReason.STOP


class _FakeService:
    def __init__(self, content: str) -> None:
        self.content = content
        self.requested_model: str | None = None
        self.runtime_info = None

    def count_chat_prompt_tokens(
        self,
        messages: tuple[object, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        del thinking_mode
        return sum(len(str(getattr(message, "content", ""))) for message in messages)

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        del cancellation
        self.requested_model = request.model_key
        return _Generated(content=self.content)


def _valid_output(*, recommendation: str = "accept", disposition: str = "pass") -> str:
    return json.dumps(
        {
            "recommendation": recommendation,
            "confidence": 0.93,
            "reasoning": "fixture",
            "criterion_results": [
                {
                    "criterion_id": "semantic.argd.evidence.1",
                    "disposition": disposition,
                    "confidence": 0.91,
                    "reason_code": "fixture_result",
                    "evidence_refs": ["REFERENCE SENTINEL"],
                }
            ],
        }
    )


def test_dedicated_runtime_result_keeps_selene_identity_and_independence(
    tmp_path: Path,
) -> None:
    service = _FakeService(_valid_output())
    response = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert service.requested_model == _PROVIDER
    assert response.provider_id == _PROVIDER
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert response.results[0].disposition is SemanticCriterionDisposition.PASS


@pytest.mark.parametrize(
    "raw_text",
    [
        "not-json",
        json.dumps(
            {
                "recommendation": "accept",
                "confidence": 1.0,
                "criterion_results": [],
            }
        ),
        _valid_output(recommendation="accept", disposition="deviation"),
    ],
    ids=("malformed", "partial", "contradictory"),
)
def test_invalid_selene_outputs_are_typed_unavailable(tmp_path: Path, raw_text: str) -> None:
    response = SeleneSemanticEvaluator(
        service=_FakeService(raw_text),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.UNAVAILABLE
    assert response.results == ()
    assert response.failure_reason == "selene_unavailable:JudgeDecodeError"
