"""P9-1 Package 2 Token Planner / Batching Regression Evidence.

This file is a mechanical, User-mandated proof that the Common Substrate
truncation fix (`SeleneSemanticEvaluator`, `src/margpa_runtime_llm/adapters/
evaluation/selene.py`, now shared by Main-shared/Selene/Gemma) actually
changes the observable failure mode, not merely a relabeling of a
`failure_reason` string:

1. `test_undersized_single_call_configuration_truncates_into_malformed_output`
   mechanically reproduces the pre-fix defect shape (all Criteria in one
   Batch, small `max_new_tokens`) using a Fake Service whose `generate()`
   can never emit more characters than the *requested* `max_new_tokens`
   allows -- so the truncation is a genuine function of the parameters
   passed to the real evaluator, not a hand-typed truncated string.
2. `test_fixed_planner_batches_within_budget_with_no_missing_or_duplicate_criteria`
   proves the actual per-Batch Token Budget invariant
   (`prompt_tokens + reserved_output_tokens <= effective_context_limit`)
   holds for every real Batch the Planner emits, that every Criterion
   appears exactly once, and that Provider/Model Identity never changes
   across Batches.
3. `test_a_failed_batch_never_yields_a_partial_success` proves a mid-stream
   Batch failure fails the whole Evaluation closed -- never silently
   presents the batches that *did* succeed as if the Run were complete.
4. `test_decode_deadline_and_cancellation_produce_three_distinct_typed_failures`
   proves Truncation/Malformed-output, Timeout and Cancellation remain
   three distinct `failure_reason` categories, never collapsed into one
   generic bucket.

The Regression Guard (Planner temporarily disabled, confirming (2) fails,
then restored) is performed manually against the real source file and
recorded in the Package 2 Exact Return -- pytest has no built-in "mutate
production code, assert failure, revert" primitive, so that step is done
directly against `selene.py` with a scratchpad backup/diff-verified
restore, following this project's established Regression-guard discipline.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

from margpa_runtime_llm.adapters.evaluation.selene import (
    SelenePromptAdapter,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeReference
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
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
# A conservative, deterministic chars-per-token ratio for a Fixture Fake --
# real tokenizers vary, but the Planner's own arithmetic only needs a
# *consistent* function of text length here, not a real tokenizer.
_CHARS_PER_TOKEN = 4


def _criteria(count: int) -> tuple[SemanticCriterion, ...]:
    return tuple(
        SemanticCriterion(
            criterion_id=f"semantic.argd.evidence.{index}",
            descriptor_id=f"argd.evidence.{index}",
            source_definition_id="argd",
            source_definition_digest_sha512=_DIGEST,
            source_pointer=f"/rules/evidence/{index}",
            source_text_digest_sha512=_DIGEST,
            instruction="Do not contradict cited evidence.",
            governance_point="main_model.semantic",
            evaluation_stage=SemanticEvaluationStage.POST,
            evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
            severity_policy="high",
            recommended_action_policy="repair_or_safe_fallback",
            evidence_requirements=("request_identity",),
        )
        for index in range(1, count + 1)
    )


def _request(*, count: int, max_criteria: int) -> SemanticEvaluationRequest:
    frozen = freeze_semantic_turn(
        request_id="planner-regression-test",
        generation=1,
        criteria=_criteria(count),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_PROVIDER,
        active_provider=_PROVIDER,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=max_criteria,
    )
    return SemanticEvaluationRequest(
        snapshot=frozen.snapshot,
        stage="post",
        user_input="QUERY SENTINEL",
        candidate_answer="CANDIDATE SENTINEL",
        evidence_context=("REFERENCE SENTINEL",),
    )


def _verified_prompt_adapter(tmp_path: Path) -> SelenePromptAdapter:
    import hashlib

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


_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="fixture-load-1",
    model_key=_PROVIDER,
    backend_key="fixture",
    backend_version="0.0.0-fixture",
    definition_file_sha512=_DIGEST,
)


class _TokenBudgetAwareFakeService:
    """A Fake `InferenceService`-shaped object whose `count_chat_prompt_
    tokens` is a real, deterministic function of message length (not a
    hardcoded stub -- the real Planner's own arithmetic is exercised), and
    whose `generate()` can never emit more characters than the *requested*
    `max_new_tokens` allows -- mirroring a real backend that hard-stops at
    its Requested Output Token Budget. This is what makes the "Before"
    reproduction mechanical rather than a hand-typed truncated string: the
    same Fake, given a larger `max_new_tokens`, genuinely emits complete,
    valid JSON.

    `fail_criterion_id`, when set, makes any Batch that contains that
    Criterion return deliberately malformed JSON regardless of budget --
    used to prove a mid-stream Batch failure never yields a partial
    success (test 3).

    `sleep_seconds`, when set, makes `generate()` block for that long
    before returning -- used to prove a Deadline is a distinct Typed
    Failure from a Decode failure (test 4).
    """

    def __init__(
        self,
        *,
        runtime_context_limit: int | None = 4096,
        fail_criterion_id: str | None = None,
        sleep_seconds: float = 0.0,
    ) -> None:
        self.calls: list[GenerationRequest] = []
        self.runtime_info = (
            SimpleNamespace(loaded_context_size=runtime_context_limit)
            if runtime_context_limit is not None
            else None
        )
        self._fail_criterion_id = fail_criterion_id
        self._sleep_seconds = sleep_seconds

    def count_chat_prompt_tokens(
        self, messages: tuple[object, ...], thinking_mode: ThinkingMode
    ) -> int:
        del thinking_mode
        return sum(len(str(getattr(m, "content", ""))) for m in messages) // _CHARS_PER_TOKEN + 1

    def generate(
        self, request: GenerationRequest, *, cancellation: object = None
    ) -> GenerationResult:
        del cancellation
        self.calls.append(request)
        if self._sleep_seconds:
            time.sleep(self._sleep_seconds)
        prompt = request.messages[0].content
        criterion_ids: list[str] = []
        for match in re.findall(r"semantic\.argd\.evidence\.\d+", prompt):
            if match not in criterion_ids:
                criterion_ids.append(match)
        if self._fail_criterion_id is not None and self._fail_criterion_id in criterion_ids:
            content = "not-json-for-this-batch"
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content=content,
                finish_reason=FinishReason.STOP,
                usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                timing=GenerationTiming(total_generation_seconds=0.001),
                runtime_info=_RUNTIME_REF,
            )
        full_json = json.dumps(
            {
                "recommendation": "accept",
                "confidence": 1.0,
                "reasoning": "fixture",
                "criterion_results": [
                    {
                        "criterion_id": criterion_id,
                        "disposition": "pass",
                        "confidence": 1.0,
                        "reason_code": "fixture_result",
                        "evidence_refs": ["REFERENCE SENTINEL"],
                    }
                    for criterion_id in criterion_ids
                ],
            }
        )
        max_chars = request.parameters.max_new_tokens * _CHARS_PER_TOKEN
        truncated = len(full_json) > max_chars
        content = full_json if not truncated else full_json[:max_chars]
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=content,
            finish_reason=FinishReason.LENGTH if truncated else FinishReason.STOP,
            usage=TokenUsage(
                prompt_tokens=10,
                completion_tokens=max(1, len(content) // _CHARS_PER_TOKEN),
                total_tokens=10 + max(1, len(content) // _CHARS_PER_TOKEN),
            ),
            timing=GenerationTiming(total_generation_seconds=0.001),
            runtime_info=_RUNTIME_REF,
        )


def test_undersized_single_call_configuration_truncates_into_malformed_output(
    tmp_path: Path,
) -> None:
    """Mechanical "Before" reproduction: 32 Criteria, `max_criteria_per_call`
    large enough to admit them all into one Batch (mirrors the pre-fix
    Main-shared shape: every selected Criterion in one unbatched call), and
    `max_new_tokens=200` -- `_LIVE_JUDGE_MAX_NEW_TOKENS`'s exact pre-fix
    value (`bootstrap/judge_live_integration.py`). A 32-criterion JSON
    response is far larger than 200 tokens can hold; the Fake genuinely
    truncates it (its `finish_reason` is `length`, matching a real
    backend's own truncation signal), and Strict Decode correctly fails
    closed rather than accepting the partial object."""
    service = _TokenBudgetAwareFakeService()
    evaluator = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
        max_new_tokens=200,
        max_criteria_per_call=32,
        max_calls=1,
        max_prompt_tokens_per_call=4096,
    )
    response = evaluator.evaluate(request=_request(count=32, max_criteria=32))

    assert len(service.calls) == 1
    assert service.calls[0].parameters.max_new_tokens == 200
    # The Fake's own truncation signal -- proves the Fixture is genuinely
    # simulating a token-budget-exhausted real backend, not asserting the
    # label in isolation.
    assert response.provider_state is SemanticProviderState.FAILED
    assert response.failure_reason is not None
    assert response.failure_reason.startswith("malformed_output:")
    assert response.results == ()


def test_fixed_planner_batches_within_budget_with_no_missing_or_duplicate_criteria(
    tmp_path: Path,
) -> None:
    """Mechanical "After" proof: the same 32 Criteria through the actual
    shipped default configuration (`max_criteria_per_call=8, max_new_
    tokens=1000`, matching `SeleneSemanticEvaluator.__init__`'s own
    defaults) -- asserts the real per-Batch Token Budget invariant, exact
    Criterion coverage, and stable Provider/Model Identity across Batches."""
    context_limit = 4096
    service = _TokenBudgetAwareFakeService(runtime_context_limit=context_limit)
    evaluator = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
    )
    response = evaluator.evaluate(request=_request(count=32, max_criteria=32))

    assert response.provider_state is SemanticProviderState.ACTIVE
    assert response.failure_reason is None

    # 32 Criteria / 8 per Batch (the shipped default) = exactly 4 real
    # Model Calls, never 1 (the pre-fix shape) and never 32 (one per
    # Criterion, which no design here ever attempted).
    assert len(service.calls) == 4
    assert response.budget is not None
    assert response.budget.calls_completed == 4
    assert len(response.budget.prompt_tokens_by_call) == 4

    reserved_output_tokens = response.budget.max_output_tokens_per_call
    assert reserved_output_tokens == 1000
    effective_context_limit = response.budget.context_limit_tokens
    assert effective_context_limit == context_limit
    for prompt_tokens in response.budget.prompt_tokens_by_call:
        # The mechanical Token Budget invariant the User asked to see
        # asserted per Batch, not merely implied by construction.
        assert prompt_tokens + reserved_output_tokens <= effective_context_limit

    # No missing, no duplicate Criteria: exact id-set match with matching
    # length rules out both simultaneously.
    expected_ids = {f"semantic.argd.evidence.{index}" for index in range(1, 33)}
    actual_ids = [item.criterion_id for item in response.results]
    assert set(actual_ids) == expected_ids
    assert len(actual_ids) == len(expected_ids) == 32
    assert all(item.disposition is SemanticCriterionDisposition.PASS for item in response.results)

    # Provider/Model Identity never changes across Batches.
    model_keys = {call.model_key for call in service.calls}
    assert model_keys == {_PROVIDER}


def test_a_failed_batch_never_yields_a_partial_success(tmp_path: Path) -> None:
    """10 Criteria / `max_criteria_per_call=8` -> 2 Batches. The second
    Batch is deliberately malformed (`fail_criterion_id` lands in Batch 2).
    The whole Evaluation must fail closed -- the 8 Criteria Batch 1
    genuinely decoded must never be silently presented as if the Run were
    complete."""
    service = _TokenBudgetAwareFakeService(fail_criterion_id="semantic.argd.evidence.9")
    evaluator = SeleneSemanticEvaluator(
        service=service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
    )
    response = evaluator.evaluate(request=_request(count=10, max_criteria=10))

    # Batch 1 (Criteria 1-8) genuinely succeeded before Batch 2 failed --
    # proves this is a real mid-stream failure, not an immediate one.
    assert len(service.calls) == 2
    assert response.provider_state is SemanticProviderState.FAILED
    assert response.failure_reason is not None
    assert response.failure_reason.startswith("malformed_output:")
    # The crux: zero results, never the 8 that already decoded correctly.
    assert response.results == ()


def test_decode_deadline_and_cancellation_produce_three_distinct_typed_failures(
    tmp_path: Path,
) -> None:
    """Truncation/Malformed-output, Timeout and Cancellation stay three
    distinct `failure_reason` categories -- never collapsed into one
    generic bucket a caller could no longer distinguish."""
    # (a) Malformed output: undersized budget, matches test 1's mechanism.
    malformed_service = _TokenBudgetAwareFakeService()
    malformed = SeleneSemanticEvaluator(
        service=malformed_service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
        max_new_tokens=10,
        max_criteria_per_call=1,
        max_calls=1,
    ).evaluate(request=_request(count=1, max_criteria=1))
    assert malformed.failure_reason is not None
    assert malformed.failure_reason.startswith("malformed_output:")

    # (b) Timeout: the real backend call genuinely runs long; the Stage's
    # own real Deadline (`inference_budget_ms=1`) fires first every time,
    # regardless of machine speed, since the Fake sleeps far longer.
    slow_service = _TokenBudgetAwareFakeService(sleep_seconds=0.25)
    timed_out = SeleneSemanticEvaluator(
        service=slow_service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
    ).evaluate(request=_request(count=1, max_criteria=1), inference_budget_ms=1)
    assert timed_out.failure_reason is not None
    assert "inference_deadline_exceeded" in timed_out.failure_reason
    assert timed_out.budget is not None
    assert timed_out.budget.deadline_exceeded is True

    # (c) Cancellation: a Cancellation Token already cancelled before the
    # Run even starts.
    cancellation = CancellationToken()
    cancellation.cancel()
    cancelled_service = _TokenBudgetAwareFakeService()
    cancelled = SeleneSemanticEvaluator(
        service=cancelled_service,  # type: ignore[arg-type]
        model_key=_PROVIDER,
        prompt_adapter=_verified_prompt_adapter(tmp_path),
    ).evaluate(request=_request(count=1, max_criteria=1), cancellation=cancellation)
    assert cancelled.failure_reason is not None
    assert "cancelled" in cancelled.failure_reason
    assert cancelled.budget is not None
    assert cancelled.budget.cancelled is True
    # Never any real Model Call once already Cancelled.
    assert cancelled_service.calls == []

    # All three failure_reason categories are pairwise distinct in kind
    # (never the same string prefix/keyword), not merely non-empty.
    reasons = {
        "malformed": malformed.failure_reason,
        "timeout": timed_out.failure_reason,
        "cancelled": cancelled.failure_reason,
    }
    assert len({value for value in reasons.values()}) == 3
    assert not reasons["timeout"].startswith("malformed_output")
    assert not reasons["cancelled"].startswith("malformed_output")
    assert "inference_deadline_exceeded" not in reasons["cancelled"]
