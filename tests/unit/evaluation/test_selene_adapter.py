from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import (
    _MODEL_BUSY_RETRY_DELAYS_SECONDS,
    GemmaPromptAdapter,
    SelenePromptAdapter,
    SelenePromptUnavailable,
    SeleneSemanticEvaluator,
    _sanitize_evidence_refs,
    build_gemma_judge_structured_output_constraint,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.errors import InferenceErrorCode
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
        "Query:\n{{query}}\nCandidate:\n{{candidate}}\nDialogue:\n{{dialogue}}\n"
        "Reference:\n{{reference}}\nCriteria:\n{{criteria}}\nSchema:\n{{response_schema}}\n"
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


def test_prompt_adapter_projects_prior_dialogue_exactly_once_separate_from_reference(
    tmp_path: Path,
) -> None:
    """Gemma Judge-only Constrained Decoding Rework (WU-04): `SemanticEvaluation
    Request.dialogue_context` was already received here but never projected
    into the rendered Prompt at all (`phase_9_1_gemma_judge_only_constrained_
    decoding_strategy_decision_ja_20260906111043.md` §3: a Prompt Contract
    gap, not a Model quality defect -- User Test A's Gemma could not see a
    fact ("765") the User had established two Turns earlier). This pins
    that the real prior-Turn history now appears in the rendered Prompt
    exactly once, in its own Section, never merged into or confused with
    the separate Citation Evidence Section."""
    request = _request().model_copy(
        update={"dialogue_context": ("user: PRIOR TURN SENTINEL 765",)}
    )
    prompt = _verified_adapter(tmp_path).build(request=request)
    assert prompt.count("PRIOR TURN SENTINEL 765") == 1
    dialogue_index = prompt.index("PRIOR TURN SENTINEL 765")
    reference_index = prompt.index("REFERENCE SENTINEL")
    assert dialogue_index != reference_index


def test_prompt_adapter_renders_none_for_absent_prior_dialogue(tmp_path: Path) -> None:
    """WU-04: an empty `dialogue_context` (the ordinary case -- a Turn's own
    first message) renders an explicit `(none)`, matching this Adapter's
    own established convention for an empty `evidence_context`, never a
    blank/missing Section."""
    prompt = _verified_adapter(tmp_path).build(request=_request())
    assert "Dialogue:\n(none)" in prompt


def test_gemma_prompt_schema_is_a_single_unambiguous_parseable_json_example() -> None:
    """R3-WU-04 (Controller Review IR-R2-05/IR-R3 §5), superseded for the
    Criterion Schema itself by R4-WU-04 (Controller Review IR-R3-04): the
    Gemma-only Prompt Schema must be one genuinely parseable JSON Object
    with no natural-language placeholder phrase left for the model to
    mistake as copyable prose -- verified here by actually `json.loads()`-
    ing the exact substituted `{{response_schema}}` blob out of a real
    rendered Prompt (the real production Gemma manifest/template), never
    merely asserting substring presence. R4-WU-04: the one `criterion_
    results[]` example is now a Compact three-Field Schema -- `criterion_
    id`/`disposition`/`confidence` only, `reason_code`/`evidence_refs`
    entirely absent (never emitted as an empty/null placeholder either) --
    since R3-WU-05's own real-hardware Golden Path Trial confirmed the same
    class of Malformed JSON defect resurfaces specifically when a genuine
    Deviation forces non-empty content into those two fields; the shared
    Decoder already treats both as optional (see `test_judge_prompt_and_
    decoder.py`'s own dedicated pin test), so omitting them needs no
    Decoder change."""
    manifest_path = Path(__file__).parents[3] / "config/judge_templates/gemma_4_e2b/manifest.json"
    adapter = GemmaPromptAdapter(manifest_path=manifest_path)
    prompt = adapter.build(request=_request())

    schema_line = next(
        line for line in prompt.splitlines() if line.strip().startswith('{"recommendation"')
    )
    schema = json.loads(schema_line)

    assert set(schema.keys()) == {
        "recommendation",
        "confidence",
        "reasoning",
        "criterion_results",
    }
    assert isinstance(schema["criterion_results"], list)
    assert len(schema["criterion_results"]) == 1
    example = schema["criterion_results"][0]
    assert list(example.keys()) == ["criterion_id", "disposition", "confidence"]
    assert isinstance(example["criterion_id"], str)
    assert isinstance(example["disposition"], str)
    assert isinstance(example["confidence"], str)
    # No ambiguous natural-language placeholder phrase left anywhere in the
    # rendered Prompt -- the exact defect Controller Review confirmed
    # Gemma copies literally into its own output. Selene's own shared
    # schema (unaffected by this Rework) still uses these phrases, so this
    # asserts on the Gemma-only rendered Prompt text specifically.
    assert "short reference" not in prompt
    assert "short code" not in prompt
    # R4-WU-04: `reason_code`/`evidence_refs` must not appear anywhere in
    # the rendered Gemma Prompt at all -- neither in the Schema example nor
    # as a dangling mention -- except the new explicit Rule stating their
    # omission outright.
    assert "evidence_refs" not in schema_line
    assert "reason_code" not in schema_line
    assert "Do not include reason_code or evidence_refs" in prompt


def test_gemma_prompt_adapter_never_changes_selenes_own_shared_schema() -> None:
    """R3-WU-04 explicitly forbids propagating the Gemma-only fix to
    Selene/Main-shared Prompts -- `SelenePromptAdapter.build()` itself
    (used unchanged by Selene) must still render the pre-Rework placeholder
    phrases verbatim."""
    manifest_path = Path(__file__).parents[3] / "config/judge_templates/selene/manifest.json"
    adapter = SelenePromptAdapter(manifest_path=manifest_path)
    prompt = adapter.build(request=_request())

    assert "short reference" in prompt
    assert "short code" in prompt


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


def test_gemma_structured_output_schema_compiles_to_a_real_grammar_and_sizes_the_batch() -> None:
    """Gemma Judge-only Constrained Decoding Rework (WU-03): the Dynamic
    Judge Schema Factory must produce a genuinely compilable JSON Schema
    (verified here against the real `llama_cpp` library, never a mocked
    compiler) whose `criterion_results` Array is sized to the exact Batch
    it was built for -- a different Batch size must never reuse a
    differently-sized Schema."""
    from llama_cpp.llama_grammar import LlamaGrammar

    constraint = build_gemma_judge_structured_output_constraint(("a.1", "a.2", "a.3"))
    schema = constraint.json_schema
    assert schema["type"] == "object"
    criterion_results_schema = cast(dict[str, object], schema["properties"])["criterion_results"]
    assert isinstance(criterion_results_schema, dict)
    assert criterion_results_schema["minItems"] == 3
    assert criterion_results_schema["maxItems"] == 3
    grammar = LlamaGrammar.from_json_schema(json.dumps(schema), verbose=False)
    assert isinstance(grammar, LlamaGrammar)

    smaller = build_gemma_judge_structured_output_constraint(("a.1",))
    smaller_results = cast(dict[str, object], smaller.json_schema["properties"])[
        "criterion_results"
    ]
    assert isinstance(smaller_results, dict)
    assert smaller_results["minItems"] == 1
    assert smaller_results["maxItems"] == 1
    assert smaller.schema_digest_sha512 != constraint.schema_digest_sha512


def test_gemma_structured_output_schema_matches_the_strict_decoders_own_field_contract() -> None:
    """WU-03: the Factory's Schema must never claim a Field shape the
    shared Strict Decoder (`judge_output_decoder.py`) does not already
    accept -- `criterion_id` is deliberately only `{"type": "string",
    "minLength": 1}` (never constrained to the exact expected id set),
    since Exact ID/duplicate/missing checks remain the Decoder's own job,
    unchanged by this Factory (Handoff WU-03's own explicit instruction)."""
    constraint = build_gemma_judge_structured_output_constraint(("a.1", "a.2"))
    properties = cast(dict[str, object], constraint.json_schema["properties"])
    assert set(properties) == {"recommendation", "confidence", "reasoning", "criterion_results"}
    criterion_results = cast(dict[str, object], properties["criterion_results"])
    item_schema = cast(dict[str, object], criterion_results["items"])
    item_properties = cast(dict[str, object], item_schema["properties"])
    assert set(item_properties) == {"criterion_id", "disposition", "confidence"}
    assert item_schema["required"] == ["criterion_id", "disposition", "confidence"]
    assert item_schema["additionalProperties"] is False
    criterion_id_schema = cast(dict[str, object], item_properties["criterion_id"])
    assert criterion_id_schema == {"type": "string", "minLength": 1}


def test_sanitize_evidence_refs_replaces_unencodable_surrogates() -> None:
    """P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
    Finding 2 from an independent adversarial-input audit): a lone,
    unpaired Unicode surrogate (e.g. `'\\ud800'`) is syntactically legal
    inside a JSON string -- `json.loads()` accepts it without complaint --
    but crashes `semantic_contract_digest()`'s `json.dumps(...,
    ensure_ascii=False).encode('utf-8')` with an uncaught
    `UnicodeEncodeError` if it reaches `SemanticCriterionResult.
    evidence_refs` unsanitized. `_sanitize_evidence_refs()` must neutralize
    it while leaving ordinary text untouched."""
    sanitized = _sanitize_evidence_refs(("plain reference", "bad\ud800ref"))
    assert sanitized[0] == "plain reference"
    assert "\ud800" not in sanitized[1]
    for item in sanitized:
        item.encode("utf-8")  # must never raise UnicodeEncodeError


def test_evaluate_never_crashes_on_a_surrogate_in_evidence_refs(tmp_path: Path) -> None:
    """Integration-level counterpart to the direct `_sanitize_evidence_refs`
    Test above: a Judge response containing an unpaired surrogate inside
    `evidence_refs` must not raise out of `evaluate()` at all -- confirming
    the sanitizer is actually applied at the real construction site, not
    only correct in isolation."""
    raw = json.dumps(
        {
            "recommendation": "accept",
            "confidence": 0.93,
            "reasoning": "fixture",
            "criterion_results": [
                {
                    "criterion_id": "semantic.argd.evidence.1",
                    "disposition": "pass",
                    "confidence": 0.91,
                    "reason_code": "fixture_result",
                    "evidence_refs": ["bad\ud800ref"],
                }
            ],
        }
    )
    response = SeleneSemanticEvaluator(
        service=_FakeService(raw),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.ACTIVE
    for ref in response.results[0].evidence_refs:
        ref.encode("utf-8")  # must never raise UnicodeEncodeError


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


class _RequestCapturingService(_FakeService):
    def __init__(self, content: str) -> None:
        super().__init__(content)
        self.requests: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        self.requests.append(request)
        return super().generate(request, cancellation=cancellation)


def test_selene_without_an_override_keeps_the_library_default_sampling(tmp_path: Path) -> None:
    """R2-WU-04 (Controller Review IR-CI-05): `sampling_overrides` must
    never spread unconditionally to Selene -- omitting it (Selene's own
    call site never supplies one) must leave every `GenerationParameters`
    Sampling field at its untouched library default."""
    service = _RequestCapturingService(_valid_output())
    SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())

    parameters = service.requests[0].parameters
    defaults = type(parameters)()
    assert parameters.temperature == defaults.temperature
    assert parameters.top_p == defaults.top_p
    assert parameters.top_k == defaults.top_k
    assert parameters.seed == defaults.seed


def test_selene_sampling_overrides_reach_the_real_generation_request(tmp_path: Path) -> None:
    """The injectable Role-specific Contract itself: whatever the
    Composition Root supplies via `sampling_overrides` must reach the
    real `GenerationRequest.parameters` sent to the Backend, unchanged."""
    service = _RequestCapturingService(_valid_output())
    SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
        sampling_overrides={"temperature": 0.0, "top_p": 1.0, "top_k": 1, "seed": 0},
    ).evaluate(request=_request())

    parameters = service.requests[0].parameters
    assert parameters.temperature == 0.0
    assert parameters.top_p == 1.0
    assert parameters.top_k == 1
    assert parameters.seed == 0
    # `max_new_tokens` is deliberately untouched by the override contract
    # -- still the Evaluator's own configured Budget (default 1000), not
    # overridden by the Sampling Contract.
    assert parameters.max_new_tokens == 1000


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
    ],
    ids=("malformed", "partial"),
)
def test_invalid_selene_outputs_are_typed_malformed_output(tmp_path: Path, raw_text: str) -> None:
    """P9-1 Package 2 Common Substrate fix: a Strict-Decode rejection means
    the model *did* respond, but its output failed the expected schema --
    this is now distinguished from a genuine `UNAVAILABLE` (adapter/
    infrastructure) failure, both because it is a materially different
    failure category (mirrors `JudgeFailureReason.MALFORMED_OUTPUT`, the
    same vocabulary the Main-shared decode pipeline already uses) and
    because the two were previously indistinguishable for every provider
    sharing this evaluator, obscuring whether Selene and Main-shared were
    hitting the same underlying truncation/decode defect."""
    response = SeleneSemanticEvaluator(
        service=_FakeService(raw_text),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.FAILED
    assert response.results == ()
    assert response.failure_reason is not None
    assert response.failure_reason.startswith("malformed_output:")


def test_self_contradictory_recommendation_no_longer_fails_decode(tmp_path: Path) -> None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 5): a Model self-reporting
    `"accept"` while its own `criterion_results` shows a `deviation` used to
    raise `JudgeDecodeError(reason="recommendation contradicts criterion
    results")`, converging to the same `malformed_output` failure category
    as genuinely broken JSON. `decode_judge_output()` now derives the final
    Recommendation mechanically from `criterion_results` instead of trusting
    the self-report, so this case succeeds and correctly reports
    `needs_repair` (matching the real `deviation` Disposition) regardless of
    what the Model's own `recommendation` field said."""
    response = SeleneSemanticEvaluator(
        service=_FakeService(_valid_output(recommendation="accept", disposition="deviation")),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert response.results[0].disposition is SemanticCriterionDisposition.DEVIATION


class _FakeCodedError(Exception):
    """Duck-types a real `InferenceError`'s `.code` attribute without
    depending on `modules.inference.domain.errors`, matching this module's
    own test fakes' existing decoupling style. `details` mirrors the real
    `InferenceError.details` field the same way -- `None` by default, so
    every existing test that constructs this without a `details` argument
    keeps its pre-WU-01 expected string unchanged."""

    def __init__(self, code: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.details = details


class _CountTokensFailingService(_FakeService):
    def __init__(self, *, code: str) -> None:
        super().__init__(_valid_output())
        self._code = code

    def count_chat_prompt_tokens(
        self,
        messages: tuple[object, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        del messages, thinking_mode
        raise _FakeCodedError(self._code)


class _GenerateFailingService(_FakeService):
    def __init__(self, *, code: str, details: dict[str, str] | None = None) -> None:
        super().__init__(_valid_output())
        self._code = code
        self._details = details

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        del request, cancellation
        raise _FakeCodedError(self._code, details=self._details)


def test_evaluate_with_zero_max_calls_makes_zero_model_calls_and_emits_zero_batch_evidence(
    tmp_path: Path,
) -> None:
    """Codex Controller Review (2026-09-06 12:44, IR-FC-03) Required Test:
    "max_calls=0...で、Model Call 0...を確認する" -- `max_calls=0` is this
    Engine's own genuine "every Criterion is Budget-Deferred, zero real
    Batch Calls dispatched" shape (`_plan_batches()`'s own `len(batches) >=
    self._max_calls` guard defers immediately when `max_calls=0`, before
    the Batch loop -- and thus before `self._service.generate()` -- ever
    runs). Confirms the underlying Service is never invoked and no
    `BatchDispatchEvidence` is ever emitted for this genuinely Model-Call-0
    Run -- the exact real-world condition `_run_selene_dispatch()`'s own
    `call_count=len(frozen_batch_evidence)` fix (no more `or 1` fallback)
    must now record honestly as `call_count=0`."""
    service = _FakeService(_valid_output())
    batch_evidence: list[object] = []
    response = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
        max_calls=0,
    ).evaluate(request=_request(), batch_evidence_observer=batch_evidence.append)
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert service.requested_model is None
    assert batch_evidence == []
    assert len(response.results) == 1
    assert response.results[0].disposition is SemanticCriterionDisposition.DEFERRED
    assert response.budget is not None
    assert response.budget.calls_started == 0
    assert response.budget.calls_completed == 0


def test_plan_batches_failure_preserves_exception_code_in_failure_reason(
    tmp_path: Path,
) -> None:
    """P9-1 Judge Dispatch "unavailable" Root Cause Fix, Round 1 Self-review
    finding: `_plan_batches()`'s pre-flight `count_chat_prompt_tokens()` call
    used to collapse into a generic `"{label}_unavailable:{ExceptionType}"`
    failure_reason with no way to tell, from persisted Evidence alone,
    *which* underlying condition caused it (this is exactly what made the
    now-fixed spurious `MODEL_BUSY` lock contention on
    `LlamaCppModelAdapter.count_chat_prompt_tokens()` indistinguishable from
    every other cause without a live reproduction). Confirms the exception's
    `.code`, when present, now survives into the raw string."""
    response = SeleneSemanticEvaluator(
        service=_CountTokensFailingService(code="model_busy"),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.UNAVAILABLE
    assert response.failure_reason == "selene_unavailable:_FakeCodedError:model_busy"


def test_generate_failure_preserves_exception_code_in_failure_reason(tmp_path: Path) -> None:
    """Same rationale as `test_plan_batches_failure_preserves_exception_code_
    in_failure_reason`, for the `run_tracked_stage()`/`generate()` collapse
    site. Real end-to-end re-verification (Round 1 Self-review) confirmed
    this path still reaches the same generic bucket via a genuine
    `InferenceError(code=MODEL_BUSY)` when a prior Turn's orphaned
    background Thread on the same dedicated Adapter is still actually
    generating — a legitimate busy state the fix's own lock-removal never
    touched (only `count_chat_prompt_tokens`/`count_text_tokens` were
    changed, `generate()`'s own exclusivity is unchanged by design)."""
    response = SeleneSemanticEvaluator(
        service=_GenerateFailingService(code="model_busy"),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.UNAVAILABLE
    assert response.failure_reason == "selene_unavailable:_FakeCodedError:model_busy"


def test_generate_failure_appends_details_when_present_and_stays_unaffected_when_absent(
    tmp_path: Path,
) -> None:
    """P9-1 Judge/Governance Rework (WU-01): a real Main+Selene concurrent-
    Load reproduction confirmed `InferenceErrorCode.GENERATION_FAILED` is
    raised by two structurally different paths that collapse to the exact
    same `.code` -- the Pathological Repetition Detector
    (`details={"reason": "pathological_repetition_detected"}`) and
    `raise_mapped_backend_error()`'s generic fallback for any other native
    exception (`details={"operation": ..., "exception_type": ...}`, the
    real shape a genuine `RuntimeError: llama_decode returned -3` reaches).
    `_diagnostic_exception_detail()` now appends `.details` (sorted, when
    present) so the persisted `failure_reason` string alone tells the two
    apart -- and stays exactly as before (no trailing `:` or empty suffix)
    when `.details` is absent, matching every pre-existing test above that
    asserts the bare `type:code` shape."""
    response_with_details = SeleneSemanticEvaluator(
        service=_GenerateFailingService(
            code="generation_failed",
            details={"reason": "pathological_repetition_detected"},
        ),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response_with_details.failure_reason == (
        "selene_unavailable:_FakeCodedError:generation_failed:"
        "reason=pathological_repetition_detected"
    )

    response_without_details = SeleneSemanticEvaluator(
        service=_GenerateFailingService(code="generation_failed"),  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response_without_details.failure_reason == (
        "selene_unavailable:_FakeCodedError:generation_failed"
    )


class _BusyThenSucceedService(_FakeService):
    """`generate()` raises a genuine `InferenceErrorCode.MODEL_BUSY` (the
    actual Enum member, matching real `InferenceError.code`'s identity —
    not a plain string, which the retry logic's `is` check deliberately
    does not treat as a real busy code) for the first `busy_calls`
    invocations, then succeeds — simulates a prior Turn's orphaned
    background generate() Thread clearing partway through the retry
    window."""

    def __init__(self, *, busy_calls: int, content: str) -> None:
        super().__init__(content)
        self._busy_calls_remaining = busy_calls
        self.generate_call_count = 0

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        self.generate_call_count += 1
        if self._busy_calls_remaining > 0:
            self._busy_calls_remaining -= 1
            raise _FakeCodedError(InferenceErrorCode.MODEL_BUSY)
        return super().generate(request, cancellation=cancellation)


class _AlwaysBusyService(_FakeService):
    def __init__(self) -> None:
        super().__init__(_valid_output())
        self.generate_call_count = 0

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        self.generate_call_count += 1
        raise _FakeCodedError(InferenceErrorCode.MODEL_BUSY)


class _NonBusyFailingService(_FakeService):
    def __init__(self, *, exception: Exception) -> None:
        super().__init__(_valid_output())
        self.generate_call_count = 0
        self._exception = exception

    def generate(self, request: GenerationRequest, *, cancellation: object = None) -> _Generated:
        self.generate_call_count += 1
        raise self._exception


def test_generate_busy_collision_retries_and_succeeds_once_orphan_clears(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P9-1 Judge Dispatch "unavailable" Round 3 fix (Open Finding 6
    resolution, User-authorized "念のため3回まで" bounded retry): a genuine
    `MODEL_BUSY` from a still-generating orphaned prior Turn now retries
    instead of instantly and permanently failing this Turn. Simulates the
    orphan clearing on the 2nd retry (well within the 3-retry budget) and
    confirms the Turn succeeds normally, with no user-visible failure at
    all — the actual real-world improvement this fix delivers."""
    monkeypatch.setattr(CancellationToken, "wait", lambda self, timeout=None: self.is_cancelled())
    service = _BusyThenSucceedService(busy_calls=2, content=_valid_output())
    response = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert response.results[0].disposition is SemanticCriterionDisposition.PASS
    assert service.generate_call_count == 3


def test_generate_busy_collision_exhausts_retries_and_reports_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The retry is bounded (User: "念のためretryの回数は決めよう...3回まで")
    specifically so a busy collision that never clears cannot become an
    unbounded/"謎のLoop" — confirms it gives up after exactly the fixed
    number of attempts (`_MODEL_BUSY_RETRY_DELAYS_SECONDS` has 3 entries,
    so 1 initial attempt + 3 retries = 4 total calls) and still reports the
    same "unavailable" category as before this fix, with the diagnostic
    detail intact."""
    monkeypatch.setattr(CancellationToken, "wait", lambda self, timeout=None: self.is_cancelled())
    service = _AlwaysBusyService()
    response = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.UNAVAILABLE
    assert response.failure_reason == "selene_unavailable:_FakeCodedError:model_busy"
    assert service.generate_call_count == 4


@pytest.mark.parametrize(
    "exception",
    [RuntimeError("boom"), _FakeCodedError(InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED)],
    ids=("no_code_attribute", "different_inference_error_code"),
)
def test_generate_non_busy_failure_is_never_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    exception: Exception,
) -> None:
    """The retry exists only for the specific, confirmed-legitimate
    `MODEL_BUSY` collision (Open Finding 6) — any other failure (no `.code`
    at all, or a real `InferenceError` with a *different* code) must fail
    immediately on the first attempt, exactly as before this fix, since
    retrying those would only add latency to a failure that retrying can
    never resolve."""
    monkeypatch.setattr(CancellationToken, "wait", lambda self, timeout=None: self.is_cancelled())
    service = _NonBusyFailingService(exception=exception)
    response = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert response.provider_state is SemanticProviderState.UNAVAILABLE
    assert service.generate_call_count == 1


class _RecordingCancellationToken:
    """Reports cancelled only from its `n`-th `wait()`/`is_cancelled()` check
    onward — lets a test deterministically fire cancellation exactly between
    two retry attempts without any real time passing. Implements `wait()`
    (what `_generate_with_busy_retry` actually calls between retries, Round 3
    Self-review fix — see `_MODEL_BUSY_RETRY_DELAYS_SECONDS`'s docstring)
    rather than a real `CancellationToken`'s interruptible-Event wait, since
    this fake never needs to actually block."""

    def __init__(self, *, cancelled_from_check: int) -> None:
        self._cancelled_from_check = cancelled_from_check
        self.check_count = 0

    def _advance(self) -> bool:
        self.check_count += 1
        return self.check_count >= self._cancelled_from_check

    def is_cancelled(self) -> bool:
        return self._advance()

    def wait(self, timeout: float | None = None) -> bool:
        del timeout
        return self._advance()


def test_generate_busy_collision_stops_retrying_once_cancelled(tmp_path: Path) -> None:
    """A busy collision that would otherwise keep retrying must still yield
    immediately to Cancellation (e.g. Main-priority preemption) rather than
    consuming its full retry budget regardless. Uses `_RecordingCancellation
    Token`, not the real `CancellationToken` (no monkeypatch needed here —
    the fake's own `wait()` never really blocks)."""
    service = _AlwaysBusyService()
    token = _RecordingCancellationToken(cancelled_from_check=1)
    with pytest.raises(_FakeCodedError):
        SeleneSemanticEvaluator(
            service=service,  # type: ignore[arg-type]
            model_key=_PROVIDER,
            prompt_adapter=_verified_adapter(tmp_path),
        )._generate_with_busy_retry(
            request_id="cancel-test",
            prompt="prompt",
            criterion_ids=(),
            cancellation=token,  # type: ignore[arg-type]
        )
    assert service.generate_call_count == 1


def test_model_busy_retry_window_covers_the_largest_documented_real_hardware_orphan() -> None:
    """Round 3 Self-review finding (Test Coverage audit), corrected in
    Round 4 (Docs-consistency audit caught a wrong citation here — see
    `_MODEL_BUSY_RETRY_DELAYS_SECONDS`'s module docstring for the full
    correction): the *only* genuine real-hardware measurement of how long
    an orphaned background generate() Thread takes to naturally clear is
    ~0.85s (Root Cause investigation's real Main+Gemma reproduction,
    `waited_s=0.854`) — a single clean data point, not a worst-case
    distribution. This tripwire asserts the retry window keeps a
    deliberate, honestly-labeled safety margin (10x that one measurement)
    rather than shrinking back down toward it, since a sample size of one
    is not itself a guarantee of the real worst case. Fails loudly if a
    future edit shrinks the total below that margin, so the two can never
    silently drift apart again."""
    only_clean_real_hardware_orphan_clear_seconds = 0.854  # Root Cause doc, waited_s
    safety_margin_multiplier = 10  # honest heuristic given the n=1 sample, not a proof
    assert sum(_MODEL_BUSY_RETRY_DELAYS_SECONDS) >= (
        only_clean_real_hardware_orphan_clear_seconds * safety_margin_multiplier
    )


def test_model_busy_retry_uses_the_documented_delay_sequence_in_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pins the exact retry wait sequence (Round 3 Self-review finding): the
    other retry tests only monkeypatch `CancellationToken.wait` to return
    instantly, which proves attempt *counts* but never the actual delay
    *values* passed to it — a bug that reordered or mis-indexed
    `_MODEL_BUSY_RETRY_DELAYS_SECONDS` (e.g. `pop()` instead of `pop(0)`,
    silently reversing the backoff) would not be caught by those alone."""
    recorded_timeouts: list[float | None] = []

    def _recording_wait(self: CancellationToken, timeout: float | None = None) -> bool:
        recorded_timeouts.append(timeout)
        return self.is_cancelled()

    monkeypatch.setattr(CancellationToken, "wait", _recording_wait)
    service = _AlwaysBusyService()
    SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_adapter(tmp_path),
    ).evaluate(request=_request())
    assert recorded_timeouts == list(_MODEL_BUSY_RETRY_DELAYS_SECONDS)
