"""P6-CODEX-001: OFF must be zero Model Calls; OBSERVE/ENFORCE must run a
real (Fake, here) Model Call on a background thread and correlate the
result by request_id, without ever touching the caller's own Canonical
content — `build_judge_completion_hook`'s Hook never returns a value the
caller could use even if it wanted to.

Recording is decoupled entirely from Judge (P6-CODEX-011, Second Rework) —
this module no longer calls any Recording Writer, so Recording OFF/FULL
coverage against this Hook was removed. See
`tests/unit/bootstrap/test_recording_live_integration.py` for the
independent Recording hook's own coverage.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    LiveJudgeResult,
    build_judge_completion_hook,
)
from margpa_runtime_llm.bootstrap.recording_live_integration import build_judge_evidence_recorder
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import StageBudgetProfile
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeReference
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode

_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key="main.test-model",
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)


class _FakeInferenceService:
    def __init__(self, *, content: str) -> None:
        self.content = content
        self.calls: list[GenerationRequest] = []

    def generate(
        self, request: GenerationRequest, *, cancellation: object = None
    ) -> GenerationResult:
        self.calls.append(request)
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=self.content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_RUNTIME_REF,
        )


def _wait_for_result(
    composition: JudgeGovernanceComposition, *, timeout_seconds: float = 2.0
) -> LiveJudgeResult:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = composition.last_result()
        if result is not None:
            return result
        time.sleep(0.005)
    raise AssertionError("Judge background thread did not record a result in time")


def test_judge_off_never_calls_the_model() -> None:
    controller = JudgeModeController()
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-1",
            user_input="What is 2+2?",
            assistant_content="4",
        )
    )
    time.sleep(0.05)

    assert service.calls == []
    assert composition.last_result() is None


def test_judge_observe_runs_a_real_call_and_correlates_by_request_id() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(
        content='{"recommendation": "accept", "confidence": 0.9, "reasoning": "correct"}'
    )
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-42",
            user_input="What is 2+2?",
            assistant_content="4",
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert result.request_id == "req-42"
    assert result.judge_role.value == "main_self"
    assert result.recommendation == "accept"
    assert result.execution_state == "completed"


def test_judge_call_uses_a_tight_max_new_tokens_cap() -> None:
    """Real-hardware finding (P6-CODEX-006/007): this environment has no
    separate Judge Artifact, so the Judge call shares the Main Model's
    single generation lock with real user Turns — a concurrent user message
    can receive a retryable model_busy error while a Judge call is in
    flight. A short cap on the Judge's own output shrinks that window; it
    does not eliminate it (see the Rework Candidate Handoff)."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model", request_id="req-cap", user_input="Q", assistant_content="A"
        )
    )
    _wait_for_result(composition)

    assert len(service.calls) == 1
    assert service.calls[0].parameters.max_new_tokens == 200


def test_built_in_judge_provider_makes_zero_model_calls_and_completes_unknown() -> None:
    """P6-RR-N-WU-001: Built-in must never call the Model — not even the
    combined general-quality-plus-Semantic prompt the Main-Model path
    builds — and must report `completed`/`unknown`, never
    `failed`/`malformed_output` (P6-CODEX-047/056 as reproduced by P6-GOV-017
    Manual Check M-5)."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        judge_provider_is_built_in=lambda: True,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-built-in",
            user_input="What is 2+2?",
            assistant_content="4",
        )
    )
    result = _wait_for_result(composition)

    assert service.calls == []
    assert result.judge_role.value == "built_in"
    assert result.recommendation == "unknown"
    assert result.execution_state == "completed"
    assert result.failure_reason is None


def test_built_in_judge_enforce_converges_to_safe_fallback_without_a_model_call() -> None:
    """Built-in can never ACCEPT (it has no semantic judgment capability),
    so ENFORCE must fall through to the existing safe_fallback contract —
    reusing `_run_judge()`'s own early-return normalization, not a
    Built-in-specific presentation path."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        judge_provider_is_built_in=lambda: True,
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-built-in-enforce",
            user_input="Question",
            assistant_content="Candidate answer",
            judge_mode="enforce",
            enforce_presented_final=True,
        )
    )

    assert service.calls == []
    assert decision is not None
    assert decision.presentation_outcome == "safe_fallback"
    assert decision.candidate_withheld is True
    result = composition.last_result()
    assert result is not None
    assert result.judge_role.value == "built_in"
    assert result.execution_state == "completed"
    assert result.failure_reason is None


def test_built_in_judge_reports_every_semantic_criterion_as_not_applicable() -> None:
    """N-WU-002 Criterion Capability Mapping: every ARGD/DAGD Semantic
    Criterion (CLASSIFICATION*/ABSOLUTE_SCORING — inherently qualitative)
    is honestly `not_applicable`/`unsupported_mapping`, never silently
    dropped and never fabricated as `pass`."""
    from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
    from margpa_runtime_llm.modules.runtime_governance.domain import (
        SemanticCriterion,
        SemanticCriterionDisposition,
        SemanticEvaluationMethod,
        SemanticEvaluationResponse,
        SemanticEvaluationStage,
        SemanticProviderState,
    )

    criterion = SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512="a" * 128,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512="a" * 128,
        instruction="Do not contradict cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )
    frozen = freeze_semantic_turn(
        request_id="req-built-in-semantic",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="built_in.deterministic",
        active_provider="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    recorded: list[SemanticEvaluationResponse] = []

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        judge_provider_is_built_in=lambda: True,
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-built-in-semantic" else None
        ),
        semantic_result_recorder=recorded.append,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-built-in-semantic",
            user_input="Question",
            assistant_content="Candidate answer",
        )
    )
    _wait_for_result(composition)

    assert len(recorded) == 1
    response = recorded[0]
    assert response.provider_id == "built_in.deterministic"
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert len(response.results) == 1
    assert response.results[0].criterion_id == "semantic.argd.evidence.1"
    assert response.results[0].disposition is SemanticCriterionDisposition.NOT_APPLICABLE
    assert response.results[0].reason_code == "unsupported_mapping"


def test_built_in_judge_reports_not_applicable_never_as_evaluated_or_unknown() -> None:
    """P6-RR-R3-WU-005 (Post-Claude Independent Review Rework, resolves
    the rest of P6-CODEX-064): every Built-in Criterion is NOT_APPLICABLE
    — the previous `criteria_evaluated=len(criteria)` +
    `criteria_unknown=len(criteria)` double-counted the same Criteria into
    two mutually-exclusive buckets and conflated NOT_APPLICABLE with the
    distinct UNKNOWN Disposition."""
    from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
    from margpa_runtime_llm.modules.runtime_governance.domain import (
        SemanticCriterion,
        SemanticEvaluationMethod,
        SemanticEvaluationStage,
        SemanticProviderState,
    )

    criterion = SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512="a" * 128,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512="a" * 128,
        instruction="Do not contradict cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )
    frozen = freeze_semantic_turn(
        request_id="req-built-in-counts",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="built_in.deterministic",
        active_provider="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        judge_provider_is_built_in=lambda: True,
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-built-in-counts" else None
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-built-in-counts",
            user_input="Question",
            assistant_content="Candidate answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.criteria_selected == 1
    assert result.criteria_evaluated == 0
    assert result.criteria_unknown == 0
    assert result.criteria_not_applicable == 1
    assert result.criteria_deferred == 0
    assert result.executed_provider == "built_in.deterministic"
    assert result.budget_profile == "local_macos_built_in_judge_v1"


def test_frozen_language_survives_main_governance_off_no_semantic_snapshot() -> None:
    """P6-RR-R14-WU-006/007 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-076): Main Runtime Governance OFF means no Semantic
    Snapshot is ever created for this Turn (`begin_semantic_turn()` is
    only called from `_pre_hook()` when Governance Mode is non-OFF), yet
    Judge can run independently in ENFORCE. The Turn's own frozen
    `context.response_language` — never a Semantic-Snapshot-derived value
    that defaults to English whenever no Snapshot exists — must still
    drive the Japanese Safe-Fallback message."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="not valid json at all")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        # No semantic_snapshot_provider supplied at all -> `_semantic_
        # snapshot()` always returns None, exactly like Main Governance
        # OFF in production.
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-frozen-lang-ja",
            user_input="質問",
            assistant_content="回答",
            enforce_presented_final=True,
            response_language="ja",
        )
    )

    assert decision is not None
    assert decision.candidate_withheld is True
    assert "判定結果を使用していません" in decision.presented_content
    assert "could not be interpreted" not in decision.presented_content
    result = composition.last_result()
    assert result is not None
    assert result.failure_language == "ja"


def test_frozen_language_defaults_to_english_when_response_language_unset() -> None:
    """Baseline: a caller that never supplies `response_language` (the
    dataclass default) keeps the pre-Rework English fallback — no
    behavior change for callers that do not opt into per-Turn Frozen
    Language."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="not valid json at all")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-frozen-lang-default",
            user_input="Question",
            assistant_content="Answer",
            enforce_presented_final=True,
        )
    )

    assert decision is not None
    assert "could not be interpreted" in decision.presented_content
    result = composition.last_result()
    assert result is not None
    assert result.failure_language == "en"


class _SlowCancellableService:
    def __init__(self) -> None:
        self.content = '{"recommendation": "accept", "confidence": 1.0}'
        self.calls: list[GenerationRequest] = []

    def generate(
        self, request: GenerationRequest, *, cancellation: CancellationToken | None = None
    ) -> GenerationResult:
        self.calls.append(request)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if cancellation is not None and cancellation.is_cancelled():
                break
            time.sleep(0.005)
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=self.content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            timing=GenerationTiming(total_generation_seconds=2.0),
            runtime_info=_RUNTIME_REF,
        )


def _slow_inference_service_for_timeout() -> _SlowCancellableService:
    return _SlowCancellableService()


def _tight_inference_budget() -> StageBudgetProfile:
    return StageBudgetProfile(
        profile_id="test_tight_inference_budget_s12_s13",
        role="judge",
        provider_id="main.self",
        hardware_profile="test",
        verification_state="test",
        load_budget_ms=60_000,
        prompt_build_budget_ms=5_000,
        inference_budget_ms=50,
        decode_budget_ms=5_000,
        repair_generation_budget_ms=60_000,
        rejudge_budget_ms=60_000,
        cancel_grace_ms=2_000,
    )


def test_live_turn_timeout_failure_presentation_is_japanese_when_frozen_ja() -> None:
    """Regression Scenario S12 (P6-RR-R20-WU-003, resolves the Timeout/JA
    half of P6-CODEX-085): a genuine Inference Stage Deadline, through the
    real live Hook (not `present_evaluation_failure()` called directly),
    must present the Japanese Timeout message when `response_language`
    is frozen `ja`. OBSERVE (not ENFORCE) so the background dispatch path
    is exercised directly, matching `test_inference_stage_deadline_
    actually_interrupts_a_slow_model_call`'s own established pattern —
    ENFORCE's synchronous wait-loop has its own, separate Timeout/Cancel
    semantics this Test is not about."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _slow_inference_service_for_timeout()
    tight_budget = _tight_inference_budget()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-timeout-ja",
            user_input="質問",
            assistant_content="回答",
            response_language="ja",
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)

    assert result.execution_state == "cancelled"
    assert result.failure_reason == "inference_stage_deadline_exceeded"
    assert result.failure_language == "ja"
    assert result.failure_message is not None
    assert "入力内容の問題ではありません" in result.failure_message


def test_live_turn_timeout_failure_presentation_is_english_when_frozen_en() -> None:
    """S13 (Timeout/EN half of P6-CODEX-085): the converse in English."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _slow_inference_service_for_timeout()
    tight_budget = _tight_inference_budget()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-timeout-en",
            user_input="Question",
            assistant_content="Answer",
            response_language="en",
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)

    assert result.execution_state == "cancelled"
    assert result.failure_reason == "inference_stage_deadline_exceeded"
    assert result.failure_language == "en"
    assert result.failure_message is not None
    assert "not caused by your input" in result.failure_message


def test_live_turn_unavailable_failure_presentation_is_japanese_when_frozen_ja() -> None:
    """S12 (Unavailable/JA half of P6-CODEX-085): Provider Selection wired
    but Active Adapter is None (fail-closed, zero Model Calls) — the
    presented content must use the Japanese Unavailable message."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        begin_judge_role_turn=lambda: None,
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-unavailable-ja",
            user_input="質問",
            assistant_content="回答",
            enforce_presented_final=True,
            response_language="ja",
        )
    )

    assert service.calls == []
    assert decision is not None
    result = composition.last_result()
    assert result is not None
    assert result.failure_reason == "judge_provider_unavailable"


def test_live_turn_unavailable_failure_presentation_is_english_when_frozen_en() -> None:
    """S13 (Unavailable/EN half of P6-CODEX-085): the converse in
    English."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        begin_judge_role_turn=lambda: None,
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-unavailable-en",
            user_input="Question",
            assistant_content="Answer",
            enforce_presented_final=True,
            response_language="en",
        )
    )

    assert service.calls == []
    assert decision is not None
    result = composition.last_result()
    assert result is not None
    assert result.failure_reason == "judge_provider_unavailable"


def test_live_turn_timeout_with_auto_and_japanese_input_presents_japanese() -> None:
    """P6-CODEX-085 (AUTO日本語): `ResponseLanguage.AUTO` resolved from a
    Japanese User Input (the same `resolve_effective_response_language()`
    `ConversationGenerationSession` itself uses, R18) must feed the exact
    same live Timeout presentation path as an explicit `ja`."""
    from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
    from margpa_runtime_llm.orchestration.response_language import (
        resolve_effective_response_language,
    )

    resolved = resolve_effective_response_language(
        language=ResponseLanguage.AUTO, user_input="今日の天気を教えてください"
    )
    assert resolved.value == "ja"

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _slow_inference_service_for_timeout()
    tight_budget = _tight_inference_budget()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-timeout-auto-ja",
            user_input="今日の天気を教えてください",
            assistant_content="回答",
            response_language=resolved.value,
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)

    assert result.failure_language == "ja"
    assert result.failure_message is not None
    assert "入力内容の問題ではありません" in result.failure_message


def test_live_turn_timeout_with_auto_and_english_input_presents_english() -> None:
    """P6-CODEX-085 (AUTO英語): the converse — AUTO resolved from an
    English User Input must present the English Timeout message."""
    from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
    from margpa_runtime_llm.orchestration.response_language import (
        resolve_effective_response_language,
    )

    resolved = resolve_effective_response_language(
        language=ResponseLanguage.AUTO, user_input="What is today's weather?"
    )
    assert resolved.value == "en"

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _slow_inference_service_for_timeout()
    tight_budget = _tight_inference_budget()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-timeout-auto-en",
            user_input="What is today's weather?",
            assistant_content="Answer",
            response_language=resolved.value,
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)

    assert result.failure_language == "en"
    assert result.failure_message is not None
    assert "not caused by your input" in result.failure_message


def test_inference_stage_deadline_actually_interrupts_a_slow_model_call() -> None:
    """P6-RR-R14-WU-001..005 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-075): a real, preemptive per-Stage Deadline —
    proven here by a Fake Service that would otherwise run for ~2 real
    seconds (checking Cancellation cooperatively, exactly like the real
    llama.cpp backend does), bounded by an Inference Budget of only
    50ms. The previous "measure elapsed time after the Call already
    returned" pattern could never have interrupted this Call early; it
    would have observed the full ~2 second latency and only then
    reported a Timeout. A Stage Deadline Owner that is merely
    decorative would let this Test's wall-clock elapsed time stay near
    2 seconds — this pins that it does not."""
    from margpa_runtime_llm.modules.evaluation.domain.stage_budget import StageBudgetProfile

    class _SlowCancellableService:
        def __init__(self) -> None:
            self.calls: list[GenerationRequest] = []

        def generate(
            self, request: GenerationRequest, *, cancellation: CancellationToken | None = None
        ) -> GenerationResult:
            self.calls.append(request)
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                if cancellation is not None and cancellation.is_cancelled():
                    break
                time.sleep(0.005)
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content='{"recommendation": "accept", "confidence": 1.0}',
                finish_reason=FinishReason.STOP,
                usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                timing=GenerationTiming(total_generation_seconds=2.0),
                runtime_info=_RUNTIME_REF,
            )

    tight_budget = StageBudgetProfile(
        profile_id="test_tight_inference_budget",
        role="judge",
        provider_id="main.self",
        hardware_profile="test",
        verification_state="test",
        load_budget_ms=60_000,
        prompt_build_budget_ms=5_000,
        inference_budget_ms=50,
        decode_budget_ms=5_000,
        repair_generation_budget_ms=60_000,
        rejudge_budget_ms=60_000,
        cancel_grace_ms=2_000,
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _SlowCancellableService()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        # `_frozen_stage_budget()` prefers `stage_budget_resolver(provider_id)`
        # over the bare `stage_budget` fallback whenever it resolves
        # without raising — the real default resolver always succeeds
        # (falling through to `LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET`), so
        # this Test must force the tight Budget through the same
        # resolver path a real per-Provider Budget would use.
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    call_started = time.monotonic()
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-stage-deadline-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)
    elapsed_seconds = time.monotonic() - call_started

    assert elapsed_seconds < 1.0, (
        f"expected the Stage Deadline to interrupt the ~2s Call, took {elapsed_seconds:.2f}s"
    )
    assert result.execution_state == "cancelled"
    assert result.failure_reason == "inference_stage_deadline_exceeded"


def test_prompt_build_stage_deadline_interrupts_a_slow_builder_with_no_late_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6-RR-R18-WU-001..003 (Post-Claude Independent Review Rework,
    resolves the Prompt Build half of P6-CODEX-081): `build_judge_prompt`
    is a synchronous, non-Cancellable CPU call — `stage_deadline()`'s own
    Timer cannot preempt it in-thread. This Test monkeypatches it to
    sleep ~2 real seconds and pins that `run_tracked_stage()` still
    bounds the caller to the real `prompt_build_budget_ms` (R18-A), and
    that once the real slow call eventually finishes in the background,
    its result never overwrites the already-published Timeout Result
    (Late Publish 0)."""
    import margpa_runtime_llm.bootstrap.judge_live_integration as judge_live_integration_module
    from margpa_runtime_llm.modules.evaluation.domain.stage_budget import StageBudgetProfile

    builder_finished = threading.Event()

    def _slow_build_judge_prompt(*args: object, **kwargs: object) -> str:
        del args, kwargs
        time.sleep(2.0)
        builder_finished.set()
        return "late-prompt-text"

    monkeypatch.setattr(
        judge_live_integration_module, "build_judge_prompt", _slow_build_judge_prompt
    )

    tight_budget = StageBudgetProfile(
        profile_id="test_tight_prompt_build_budget",
        role="judge",
        provider_id="main.self",
        hardware_profile="test",
        verification_state="test",
        load_budget_ms=60_000,
        prompt_build_budget_ms=50,
        inference_budget_ms=5_000,
        decode_budget_ms=5_000,
        repair_generation_budget_ms=60_000,
        rejudge_budget_ms=60_000,
        cancel_grace_ms=2_000,
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    call_started = time.monotonic()
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-prompt-build-deadline-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)
    elapsed_seconds = time.monotonic() - call_started

    assert elapsed_seconds < 1.0, (
        f"expected the Prompt Build Deadline to interrupt the ~2s call, took {elapsed_seconds:.2f}s"
    )
    assert result.execution_state == "failed"
    assert result.failure_reason == "prompt_build_timeout"
    assert service.calls == [], "a timed-out Prompt Build must never reach the Model Call"

    # Let the real slow Builder actually finish in the background, then
    # confirm its late "success" never overwrote the already-published
    # Timeout Result (Late Publish 0).
    assert builder_finished.wait(timeout=5.0)
    time.sleep(0.05)
    late_check = composition.last_result()
    assert late_check is not None
    assert late_check.request_id == "req-prompt-build-deadline-1"
    assert late_check.execution_state == "failed"
    assert late_check.failure_reason == "prompt_build_timeout"


def test_decode_stage_deadline_interrupts_a_slow_decoder_with_no_late_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6-RR-R18-WU-001..003 (resolves the Decode half of P6-CODEX-081):
    same real Bound and Late-Publish-0 guarantee as the Prompt Build Test
    above, for `decode_judge_output_fail_closed` (R18-B)."""
    import margpa_runtime_llm.bootstrap.judge_live_integration as judge_live_integration_module
    from margpa_runtime_llm.modules.evaluation.domain.stage_budget import StageBudgetProfile

    decoder_finished = threading.Event()

    def _slow_decode_judge_output_fail_closed(*args: object, **kwargs: object) -> object:
        del args, kwargs
        time.sleep(2.0)
        decoder_finished.set()
        raise AssertionError("must never be awaited/consulted after the Decode Timeout")

    monkeypatch.setattr(
        judge_live_integration_module,
        "decode_judge_output_fail_closed",
        _slow_decode_judge_output_fail_closed,
    )

    tight_budget = StageBudgetProfile(
        profile_id="test_tight_decode_budget",
        role="judge",
        provider_id="main.self",
        hardware_profile="test",
        verification_state="test",
        load_budget_ms=60_000,
        prompt_build_budget_ms=5_000,
        inference_budget_ms=5_000,
        decode_budget_ms=50,
        repair_generation_budget_ms=60_000,
        rejudge_budget_ms=60_000,
        cancel_grace_ms=2_000,
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 1.0}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        stage_budget=tight_budget,
        stage_budget_resolver=lambda provider_id: tight_budget,
    )

    call_started = time.monotonic()
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-decode-deadline-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition, timeout_seconds=3.0)
    elapsed_seconds = time.monotonic() - call_started

    assert elapsed_seconds < 1.0, (
        f"expected the Decode Deadline to interrupt the ~2s call, took {elapsed_seconds:.2f}s"
    )
    assert result.execution_state == "failed"
    assert result.failure_reason == "timeout"
    assert len(service.calls) == 1, "the Model Call itself must still have run exactly once"

    assert decoder_finished.wait(timeout=5.0)
    time.sleep(0.05)
    late_check = composition.last_result()
    assert late_check is not None
    assert late_check.request_id == "req-decode-deadline-1"
    assert late_check.execution_state == "failed"
    assert late_check.failure_reason == "timeout"


def test_built_in_enforce_resolves_synchronously_with_zero_pipeline_budget_no_race() -> None:
    """P6-RR-R14-WU-003/004 (Post-Claude Independent Review Rework,
    resolves the rest of P6-CODEX-075): the real
    `LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET` has `enforce_pipeline_budget_ms
    == 0` — the previous Background-Task + Timeout-Wait path could
    spuriously report `deadline_exceeded` purely from thread-scheduling
    latency with a 0-second wait_timeout. Resolving Built-in inline,
    synchronously, removes the race entirely: `composition.last_result()`
    must already be populated the instant `hook()` returns, with no
    polling/wait needed at all (unlike every Model-backed path, which
    genuinely runs on a Background Thread)."""
    from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
        LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET,
        resolve_local_macos_judge_budget,
    )

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="should never be called")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        judge_provider_is_built_in=lambda: True,
        stage_budget_resolver=resolve_local_macos_judge_budget,
    )
    assert LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET.enforce_pipeline_budget_ms == 0

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-built-in-zero-budget",
            user_input="Question",
            assistant_content="Answer",
            enforce_presented_final=True,
        )
    )

    assert service.calls == []
    assert decision is not None
    result = composition.last_result()
    assert result is not None, "Built-in must resolve synchronously — no wait/poll needed"
    assert result.execution_state == "completed"
    assert result.failure_reason is None
    assert result.judge_role.value == "built_in"


def test_frozen_guard_mode_reflects_the_real_resolver_not_a_hardcoded_none() -> None:
    """P6-RR-O-WU-004: resolves P6-CODEX-053/061's `frozen_guard_mode=None`
    literal — the Turn's real Guardrail Mode must reach `LiveJudgeResult`.
    """
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(
        content='{"recommendation": "accept", "confidence": 0.9, "reasoning": "ok"}'
    )
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        guardrail_mode_resolver=lambda: "enforce",
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-guard-mode",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.frozen_guard_mode == "enforce"


def test_frozen_guard_mode_defaults_to_none_when_resolver_absent() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-no-guard-resolver",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.frozen_guard_mode is None


def test_judge_enforce_also_runs_and_malformed_output_fails_closed() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="not json at all")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-7",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert result.execution_state == "failed"
    assert result.failure_reason == "malformed_output"


def test_presented_final_enforce_turns_malformed_judge_output_into_safe_fallback() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="not json at all")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-enforce-final-failure",
            user_input="Question",
            assistant_content="Known failed candidate",
            judge_mode="enforce",
            enforce_presented_final=True,
        )
    )

    assert decision is not None
    assert decision.presentation_outcome == "safe_fallback"
    assert decision.candidate_withheld is True
    assert "Known failed candidate" not in decision.presented_content
    assert decision.presented_content == (
        "The Judge response could not be interpreted, so its result was not used."
    )
    result = composition.last_result()
    assert result is not None
    assert result.execution_state == "failed"
    assert result.repair_accepted is None


def test_presented_final_enforce_deadline_is_bounded_and_late_worker_cannot_overwrite() -> None:
    """RW8-B: deadline owns the terminal even if Backend returns later."""

    worker_entered = threading.Event()
    release_worker = threading.Event()
    evidence_calls: list[dict[str, object]] = []

    def _evidence_recorder(**fields: object) -> None:
        evidence_calls.append(fields)

    class _IgnoringCancellationService:
        def generate(
            self,
            request: GenerationRequest,
            *,
            cancellation: CancellationToken | None = None,
        ) -> GenerationResult:
            worker_entered.set()
            release_worker.wait(timeout=2.0)
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content='{"recommendation":"accept","confidence":1.0}',
                finish_reason=FinishReason.STOP,
                usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                timing=GenerationTiming(total_generation_seconds=0.01),
                runtime_info=_RUNTIME_REF,
            )

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    coordinator = ModelAccessCoordinator()
    hook, composition = build_judge_completion_hook(
        service=_IgnoringCancellationService(),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
        judge_evidence_recorder=_evidence_recorder,
        enforce_wait_timeout_seconds=0.03,
        enforce_cancel_grace_seconds=0.01,
    )

    started = time.monotonic()
    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-enforce-deadline",
            user_input="Question",
            assistant_content="Raw candidate must stay withheld",
            judge_mode="enforce",
            recording_mode="full",
            enforce_presented_final=True,
        )
    )
    elapsed = time.monotonic() - started

    assert worker_entered.is_set()
    assert elapsed < 0.5
    assert decision is not None
    assert decision.presentation_outcome == "safe_fallback"
    assert "Raw candidate" not in decision.presented_content
    assert decision.presented_content == (
        "Evaluation did not finish within its configured time; this was not caused by your input."
    )
    deadline_result = composition.last_result()
    assert deadline_result is not None
    assert deadline_result.execution_state == "failed"
    assert deadline_result.failure_reason == "deadline_exceeded"
    assert evidence_calls == []

    release_worker.set()
    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)

    assert coordinator.current_background_task_id() is None
    assert composition.last_result() == deadline_result
    assert evidence_calls == []


def test_enforce_worker_cannot_enter_recorder_before_terminal_owner_authorizes() -> None:
    """Ninth Rework: old check-then-act Recorder race is structural zero."""

    recorder_entered = threading.Event()
    allow_commit = threading.Event()
    evidence_calls: list[dict[str, object]] = []

    def _blocking_recorder(**fields: object) -> None:
        recorder_entered.set()
        allow_commit.wait(timeout=2.0)
        evidence_calls.append(fields)

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    coordinator = ModelAccessCoordinator()
    hook, composition = build_judge_completion_hook(
        service=_FakeInferenceService(content='{"recommendation":"accept","confidence":1.0}'),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
        judge_evidence_recorder=_blocking_recorder,
        enforce_wait_timeout_seconds=0.05,
    )

    started = time.monotonic()
    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-pending-evidence-arbitration",
            user_input="Q",
            assistant_content="A",
            judge_mode="enforce",
            recording_mode="full",
            enforce_presented_final=True,
        )
    )

    assert time.monotonic() - started < 0.5
    assert decision is not None
    assert decision.finalize_evidence is not None
    assert recorder_entered.is_set() is False
    assert evidence_calls == []
    result = composition.last_result()
    assert result is not None
    assert result.recommendation == "accept"

    # Terminal ownership is the sole publication authority. Signalling it
    # is non-blocking even though the Recorder itself then blocks.
    finalize_started = time.monotonic()
    decision.finalize_evidence(True)
    assert time.monotonic() - finalize_started < 0.5
    assert recorder_entered.wait(timeout=1.0)
    assert evidence_calls == []

    # The Recorder owns a tracked auxiliary Task, never the Model lease.
    # A new Main Turn acquires immediately even while publication blocks.
    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)
    assert coordinator.current_background_task_id() is None
    assert coordinator.current_auxiliary_task_ids() == (
        "req-pending-evidence-arbitration:judge-evidence",
    )
    coordinator.acquire_main(task_id="main-after-blocked-evidence")
    coordinator.release_main(task_id="main-after-blocked-evidence")

    # Shutdown must track the blocked Publisher and refuse a false-clean
    # result. Once the Recorder drains, retry converges cleanly.
    assert coordinator.shutdown(join_timeout_seconds=0.01) is False

    allow_commit.set()
    assert coordinator.shutdown(join_timeout_seconds=2.0) is True
    assert coordinator.current_auxiliary_task_ids() == ()
    assert len(evidence_calls) == 1


def test_enforce_cancel_before_terminal_authorization_discards_pending_evidence() -> None:
    cancellation = CancellationToken()
    evidence_calls: list[dict[str, object]] = []
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    coordinator = ModelAccessCoordinator()
    hook, _composition = build_judge_completion_hook(
        service=_FakeInferenceService(content='{"recommendation":"accept","confidence":1.0}'),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-cancel-before-evidence",
            user_input="Q",
            assistant_content="A",
            judge_mode="enforce",
            recording_mode="full",
            enforce_presented_final=True,
            cancellation=cancellation,
        )
    )
    assert decision is not None
    assert decision.finalize_evidence is not None

    cancellation.cancel()
    decision.finalize_evidence(True)
    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)

    assert coordinator.current_background_task_id() is None
    assert evidence_calls == []


def test_delayed_normal_enforce_publishes_evidence_exactly_once_after_authorization() -> None:
    evidence_calls: list[dict[str, object]] = []
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    coordinator = ModelAccessCoordinator()
    hook, _composition = build_judge_completion_hook(
        service=_FakeInferenceService(content='{"recommendation":"accept","confidence":1.0}'),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-enforce-evidence-once",
            user_input="Q",
            assistant_content="A",
            judge_mode="enforce",
            recording_mode="full",
            enforce_presented_final=True,
        )
    )
    assert decision is not None
    assert decision.finalize_evidence is not None
    # Replacement-final Governance/Guardrail and caller-side composition
    # may legitimately take longer than the old 0.25-second Worker wait.
    # Pending Evidence remains owned until the terminal decision; it is
    # neither silently timed out nor published early.
    time.sleep(0.3)
    assert evidence_calls == []
    decision.finalize_evidence(True)
    decision.finalize_evidence(True)

    deadline = time.monotonic() + 2.0
    while coordinator.current_auxiliary_task_ids() and time.monotonic() < deadline:
        time.sleep(0.005)
    assert coordinator.current_auxiliary_task_ids() == ()
    assert len(evidence_calls) == 1


def test_observe_publishes_evidence_once_and_recording_off_calls_recorder_zero() -> None:
    evidence_calls: list[dict[str, object]] = []
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    coordinator = ModelAccessCoordinator()
    hook, composition = build_judge_completion_hook(
        service=_FakeInferenceService(content='{"recommendation":"accept","confidence":1.0}'),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-observe-evidence-once",
            user_input="Q",
            assistant_content="A",
            judge_mode="observe",
            recording_mode="full",
        )
    )
    _wait_for_result(composition)
    deadline = time.monotonic() + 2.0
    while coordinator.current_auxiliary_task_ids() and time.monotonic() < deadline:
        time.sleep(0.005)
    assert coordinator.current_auxiliary_task_ids() == ()
    assert len(evidence_calls) == 1

    off_coordinator = ModelAccessCoordinator()
    off_hook, off_composition = build_judge_completion_hook(
        service=_FakeInferenceService(content='{"recommendation":"accept","confidence":1.0}'),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=off_coordinator,
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
    )
    off_hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-observe-recording-off",
            user_input="Q",
            assistant_content="A",
            judge_mode="observe",
            recording_mode="off",
        )
    )
    _wait_for_result(off_composition)
    assert off_coordinator.current_auxiliary_task_ids() == ()
    assert len(evidence_calls) == 1


def test_dialogue_correction_and_citation_evidence_reach_the_real_judge_prompt() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation":"needs_repair","confidence":0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-context-evidence",
            user_input="No, the correct reading is Amane Kanata.",
            assistant_content="The official reading is Tenon.",
            dialogue_context=("assistant: The official reading is Tenon.",),
            evidence_context=("ref-1 | official.md: Amane Kanata",),
            judge_mode="observe",
        )
    )
    _wait_for_result(composition)

    prompt = service.calls[0].messages[0].content
    assert "No, the correct reading is Amane Kanata." in prompt
    assert "assistant: The official reading is Tenon." in prompt
    assert "ref-1 | official.md: Amane Kanata" in prompt


def test_terminal_result_contains_correlation_timestamps_modes_provider_and_outcome() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    hook, composition = build_judge_completion_hook(
        service=_FakeInferenceService(  # type: ignore[arg-type]
            content='{"recommendation":"accept","confidence":0.9}'
        ),
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-correlation-summary",
            user_input="Q",
            assistant_content="A",
            judge_mode="observe",
            repair_mode="off",
            recording_mode="metadata",
        )
    )
    result = _wait_for_result(composition)
    assert result.started_at is not None
    assert result.completed_at is not None
    assert result.frozen_judge_mode == "observe"
    assert result.frozen_repair_mode == "off"
    assert result.recording_mode == "metadata"
    assert result.configured_provider == "main.test-model"
    assert result.active_provider == "main.test-model"
    assert result.judge_outcome == "accept"
    assert result.final_disposition == "observed_candidate"


def test_needs_repair_recommendation_with_repair_enforce_resolves_eligible() -> None:
    """P6-CODEX-002 (partial, real): a real needs_repair Recommendation is
    actually passed to resolve_repair_eligibility(), not merely capable of
    being passed."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "needs_repair", "confidence": 0.4}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-99",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.recommendation == "needs_repair"
    assert result.repair_eligibility == "eligible"


def test_judge_observe_never_resolves_repair_eligibility_even_with_needs_repair() -> None:
    """OBSERVE must have zero downstream effect, including feeding
    Eligibility Resolution — only ENFORCE actually passes the Recommendation
    onward (per the Rework Handoff's literal "Judge ENFORCE: ... can pass to
    Repair Eligibility")."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.OBSERVE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "needs_repair", "confidence": 0.4}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-observe-99",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.recommendation == "needs_repair"
    assert result.repair_eligibility is None


def test_needs_repair_recommendation_with_repair_off_resolves_not_eligible() -> None:
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()  # default OFF
    service = _FakeInferenceService(content='{"recommendation": "needs_repair", "confidence": 0.4}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-100",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.repair_eligibility == "not_eligible_mode_off"


def test_accept_recommendation_never_resolves_eligibility() -> None:
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.95}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-101",
            user_input="Question",
            assistant_content="A solid answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.recommendation == "accept"
    assert result.repair_eligibility == "not_eligible_no_repair_recommendation"


def test_repair_executor_is_invoked_when_eligible_and_result_is_recorded() -> None:
    """P6-CODEX-009 (Second Rework): a real Repair Executor Port, when bound
    and Eligibility resolves ELIGIBLE, is actually called with the Judge's
    own before_recommendation/reasoning — and its outcome is projected onto
    the Composition's recorded LiveJudgeResult, not silently dropped."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(
        content='{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague"}'
    )
    captured_calls: list[dict[str, object]] = []

    def _fake_repair_executor(
        *,
        request_id: str,
        model_key: str,
        user_input: str,
        original_answer: str,
        before_recommendation: object,
        judge_reasoning: str,
        dialogue_context: tuple[str, ...],
        evidence_context: tuple[str, ...],
        governance_post_hook: object,
        guardrail_post_hook: object,
        cancellation: object = None,
        model_runtime_info: object = None,
        stage_hook: object = None,
        persist_accepted_attempt: bool = True,
        stage_budget: object = None,
        rejudge_service: object = None,
        rejudge_model_key: str | None = None,
        rejudge_role: object = None,
        language: str = "en",
    ) -> object:
        from margpa_runtime_llm.bootstrap.repair_live_integration import RepairExecutionResult

        captured_calls.append(
            {
                "request_id": request_id,
                "user_input": user_input,
                "original_answer": original_answer,
                "before_recommendation": before_recommendation,
                "judge_reasoning": judge_reasoning,
                "rejudge_model_key": rejudge_model_key,
            }
        )
        return RepairExecutionResult(
            request_id=request_id,
            outcome="improved",
            accepted=True,
            new_turn_id="new-turn-1",
            rejected_reason=None,
            presented_content="A corrected answer",
        )

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-repair-1",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert len(captured_calls) == 1
    assert captured_calls[0]["rejudge_model_key"] == "main.test-model"
    assert captured_calls[0]["request_id"] == "req-repair-1"
    assert captured_calls[0]["judge_reasoning"] == "vague"
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    assert result.repair_new_turn_id == "new-turn-1"


def test_presented_final_enforce_returns_only_an_accepted_repair_candidate() -> None:
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(
        content='{"recommendation":"needs_repair","confidence":0.9,"reasoning":"contradiction"}'
    )

    def _repair(**kwargs: object) -> object:
        from margpa_runtime_llm.bootstrap.repair_live_integration import RepairExecutionResult

        return RepairExecutionResult(
            request_id=str(kwargs["request_id"]),
            outcome="improved",
            accepted=True,
            new_turn_id=None,
            rejected_reason=None,
            presented_content="Source-grounded corrected answer",
        )

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_repair,  # type: ignore[arg-type]
    )
    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-repaired-final",
            user_input="Correct this answer",
            assistant_content="Known failed candidate",
            judge_mode="enforce",
            enforce_presented_final=True,
        )
    )

    assert decision is not None
    assert decision.presented_content == "Source-grounded corrected answer"
    assert decision.presentation_outcome == "repair_accepted"
    assert decision.candidate_withheld is True
    result = composition.last_result()
    assert result is not None
    assert result.repair_accepted is True


def test_judging_state_is_observable_while_the_judge_model_call_is_in_flight() -> None:
    """P6-OBS-004/P6-CODEX-031 (Fourth Rework): before this fix, the entire
    Judge Call -> Repair Call -> Rejudge Call pipeline collapsed into one
    generic "running" state — an external Status reader could never tell
    which of the three real Model Calls was actually in flight. This
    proves "judging" specifically is genuinely observable while the
    initial Judge Model Call is running, not merely a value set-then-
    immediately-overwritten before any reader could ever observe it."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.OBSERVE)
    judge_call_entered = threading.Event()
    allow_judge_call_to_finish = threading.Event()

    class _SlowJudgeService:
        def generate(self, request: object, *, cancellation: object = None) -> GenerationResult:
            judge_call_entered.set()
            allow_judge_call_to_finish.wait(timeout=5.0)
            return GenerationResult(
                request_id="req-judging-state-1:judge",
                model_key="main.test-model",
                content='{"recommendation": "accept", "confidence": 0.9}',
                finish_reason=FinishReason.STOP,
                usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                timing=GenerationTiming(total_generation_seconds=0.01),
                runtime_info=_RUNTIME_REF,
            )

    hook, composition = build_judge_completion_hook(
        service=_SlowJudgeService(),  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-judging-state-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )

    assert judge_call_entered.wait(timeout=2.0)
    assert composition.current_state() == "judging"
    assert composition.current_request_id() == "req-judging-state-1"

    allow_judge_call_to_finish.set()
    _wait_for_result(composition)


def test_repairing_state_is_observable_while_the_repair_executor_is_in_flight() -> None:
    """P6-OBS-004/P6-CODEX-031 (Fourth Rework): the same proof as above,
    for the "repairing" sub-state, while the Repair Executor Port call
    (the candidate-generation half of Repair) is itself in flight."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(
        content='{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague"}'
    )
    repair_executor_entered = threading.Event()
    allow_repair_executor_to_finish = threading.Event()

    def _slow_repair_executor(**_kwargs: object) -> object:
        repair_executor_entered.set()
        allow_repair_executor_to_finish.wait(timeout=5.0)
        return None

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_slow_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-repairing-state-1",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )

    assert repair_executor_entered.wait(timeout=2.0)
    assert composition.current_state() == "repairing"
    assert composition.current_request_id() == "req-repairing-state-1"

    allow_repair_executor_to_finish.set()
    _wait_for_result(composition)


def test_repair_executor_not_invoked_when_not_eligible() -> None:
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()  # default OFF -> not eligible
    service = _FakeInferenceService(content='{"recommendation": "needs_repair", "confidence": 0.4}')
    calls = 0

    def _fake_repair_executor(**_kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return None

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-102",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert calls == 0
    assert result.repair_outcome is None


def test_repair_observe_never_invokes_the_executor_zero_additional_generation() -> None:
    """P6-ACC-026/P6-GOV-002 (Second Rework): Repair OBSERVE must cause
    zero additional Generation. `resolve_repair_eligibility()` itself
    classifies OBSERVE the same as ENFORCE (it only excludes OFF) — the
    real gate against actually invoking the Repair Executor (2 further
    Model Calls) must live at this call site, keyed on the Mode being
    ENFORCE specifically, not merely on Eligibility."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "needs_repair", "confidence": 0.4}')
    calls = 0

    def _fake_repair_executor(**_kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return None

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-observe-repair",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert calls == 0
    assert result.repair_outcome is None
    # Eligibility is still classified for Status/observability purposes —
    # OBSERVE means "would be Eligible," never a fabricated "not eligible."
    assert result.repair_eligibility == "eligible"


def test_a_failed_model_call_records_a_typed_failure_result_not_a_stale_success() -> None:
    """P6-CODEX-010: a Background Task's Model Call failure must record an
    explicit Failed/typed result, never silently leave whatever the prior
    `last_result()` was looking like it is still "current"."""

    class _RaisingService:
        def generate(
            self, request: GenerationRequest, *, cancellation: object = None
        ) -> GenerationResult:
            raise RuntimeError("boom")

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    hook, composition = build_judge_completion_hook(
        service=_RaisingService(),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-fail-1",
            user_input="Q",
            assistant_content="A",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "failed"
    assert result.failure_reason is not None
    assert result.failure_reason.startswith("model_call_error:")


def test_hook_skips_and_marks_skipped_when_coordinator_is_busy() -> None:
    """P6-CODEX-010, hardened P6-CODEX-020: never queue — if the shared
    Model is already busy with another Background Task, this Turn's Judge
    Run is skipped outright, and the Composition reflects that with an
    explicit `queued_or_skipped` state correlated to *this Turn's own*
    request_id — never a bare `idle` that a Status reader could confuse
    with "Composition never even saw this Turn"."""
    coordinator = ModelAccessCoordinator()
    started_marker = time.monotonic()

    def _hold_background() -> None:
        time.sleep(0.2)

    assert coordinator.start_background(task_id="occupier", target=_hold_background)

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=coordinator,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-skip-1",
            user_input="Q",
            assistant_content="A",
        )
    )

    assert time.monotonic() - started_marker < 0.2
    assert service.calls == []
    assert composition.current_state() == "queued_or_skipped"
    assert composition.current_request_id() == "req-skip-1"
    assert composition.last_result() is None


def test_hook_marks_skipped_and_correlated_when_judge_mode_is_off() -> None:
    """P6-CODEX-020: Judge OFF must still correlate the Current Request
    Identity with an explicit outcome — previously the Hook returned
    immediately without touching `composition` at all, so a prior Turn's
    stale `completed` state (and its `last_result`) would keep looking
    "current" for every subsequent OFF Turn indefinitely."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-on-1",
            user_input="Q",
            assistant_content="A",
        )
    )
    _wait_for_result(composition)
    assert composition.current_state() == "completed"

    controller.apply_mode(EvaluationMode.OFF)
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-off-1",
            user_input="Q",
            assistant_content="A",
        )
    )

    assert composition.current_state() == "queued_or_skipped"
    assert composition.current_request_id() == "req-off-1"
    # The stale Turn-1 result is still retrievable as history, but it is no
    # longer presented as "current" — a caller must compare
    # `last_result().request_id` against `current_request_id()`.
    last_result = composition.last_result()
    assert last_result is not None
    assert last_result.request_id == "req-on-1"
    assert last_result.request_id != composition.current_request_id()


def test_judge_evidence_recorder_is_actually_invoked_with_real_provenance(
    tmp_path: Path,
) -> None:
    """P6-GOV-002/P6-ACC-021 (Second Rework): a real, wired
    `judge_evidence_recorder` receives the true Model identity, Rubric,
    Prompt digest, Recommendation/Confidence/Token/Latency, and Seed/Config
    Digest for every completed Judge Run — not just a Callable that could
    exist but is never actually reached from `_run_judge()`."""
    recording_controller = RecordingModeController()
    recording_controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=100_000)
    judge_evidence_recorder, evidence_state = build_judge_evidence_recorder(writer=writer)

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(
        content='{"recommendation": "accept", "confidence": 0.9, "reasoning": "solid"}'
    )
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        recording_mode_controller=recording_controller,
        judge_evidence_recorder=judge_evidence_recorder,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-evidence-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    _wait_for_result(composition)

    deadline = time.monotonic() + 2.0
    files: list[Path] = []
    while time.monotonic() < deadline:
        files = list(tmp_path.glob("*.json"))
        if files:
            break
        time.sleep(0.005)

    assert len(files) == 1
    assert files[0].name == "req-evidence-1.json"
    fields = json.loads(files[0].read_text())["metadata_fields"]
    assert fields["model_identity"] == "main.test-model"
    assert fields["judge_role"] == "main_self"
    assert fields["recommendation"] == "accept"
    assert fields["confidence"] == 0.9
    assert fields["seed_pinned"] is False
    assert fields["config_digest_sha512"] != "unavailable"
    assert len(fields["config_digest_sha512"]) == 128
    # P6-CODEX-022: no ModelRuntimeInfo was supplied at all here — the
    # honest, explicit absence, never a fabricated placeholder.
    assert fields["artifact_digest_sha512"] == "unavailable"
    assert fields["backend_key"] == "unavailable"
    assert fields["backend_version"] == "unavailable"
    outcome = evidence_state.last_outcome()
    assert outcome is not None
    assert outcome.ok is True


def test_judge_evidence_carries_real_artifact_digest_and_backend_when_runtime_info_given(
    tmp_path: Path,
) -> None:
    """P6-CODEX-022: `model_identity` alone (a bare config key) cannot
    distinguish a re-download or backend upgrade of the same key — the
    Artifact Digest and Backend Identity/Version must also be persisted
    when a real `ModelRuntimeInfo` is available."""
    from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
    from margpa_runtime_llm.modules.inference.contracts.runtime import (
        GpuOffloadEvidence,
        ModelCapabilities,
        ModelDigest,
        ModelRuntimeInfo,
    )
    from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature

    runtime_info = ModelRuntimeInfo(
        load_instance_id="load-1",
        model_key="main.qwen3-4b",
        backend_key="llama_cpp",
        backend_version="b1234",
        model_architecture="qwen3",
        format="gguf",
        quantization="q4_k_m",
        artifact_size_bytes=1024,
        artifact_digest=ModelDigest(value="d" * 128),
        definition_file_sha512="e" * 128,
        loaded_context_size=8192,
        effective_capabilities=ModelCapabilities(
            features=frozenset({CapabilityFeature.CHAT}),
            native_context_limit=8192,
            loaded_context_size=8192,
            supported_message_roles=frozenset({MessageRole.USER, MessageRole.ASSISTANT}),
        ),
        chat_template_source="embedded",
        chat_template_digest=ModelDigest(value="f" * 128),
        device="cpu",
        device_kind="cpu",
        acceleration_api="none",
        gpu_offload=False,
        gpu_offload_evidence=GpuOffloadEvidence(
            supported=False, requested=False, observed=False, observation_source="not_requested"
        ),
    )
    recording_controller = RecordingModeController()
    recording_controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=100_000)
    judge_evidence_recorder, _ = build_judge_evidence_recorder(writer=writer)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        recording_mode_controller=recording_controller,
        judge_evidence_recorder=judge_evidence_recorder,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            model_runtime_info=runtime_info,
            request_id="req-evidence-digest-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    _wait_for_result(composition)

    deadline = time.monotonic() + 2.0
    files: list[Path] = []
    while time.monotonic() < deadline:
        files = list(tmp_path.glob("*.json"))
        if files:
            break
        time.sleep(0.005)

    assert len(files) == 1
    fields = json.loads(files[0].read_text())["metadata_fields"]
    assert fields["artifact_digest_sha512"] == "d" * 128
    assert fields["backend_key"] == "llama_cpp"
    assert fields["backend_version"] == "b1234"


def test_repair_mode_is_frozen_at_hook_entry_not_reread_mid_run() -> None:
    """P6-CODEX-020: a Repair Mode change that happens *after* the Hook has
    already been invoked (i.e. during the Background Run) must not affect
    Eligibility/execution for that already-in-flight Run — only the value
    Frozen at Hook entry governs it."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.OFF)
    service = _FakeInferenceService(
        content='{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague"}'
    )
    calls = 0

    def _fake_repair_executor(**_kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return None

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-frozen-1",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    # Flip Repair to ENFORCE immediately after the Hook call returns — the
    # already-frozen snapshot (OFF) inside the just-started Background Task
    # must still govern this Run.
    repair_controller.apply_mode(RepairMode.ENFORCE)
    result = _wait_for_result(composition)

    assert result.repair_eligibility == "not_eligible_mode_off"
    assert calls == 0


def test_recording_mode_is_frozen_at_hook_entry_not_reread_mid_run(tmp_path: Path) -> None:
    """P6-CODEX-029 (Fourth Rework): before this fix, Judge/Repair Mode
    were frozen at Hook entry (see the Repair Mode test above), but
    Recording Mode alone was still re-read fresh by the Judge Evidence
    Recorder at write-time, on the Background Thread — a live Recording
    Mode change made right after this Hook call returns (but before the
    Background Run's own write actually happens) must not affect whether
    that already-in-flight Run's Evidence gets written; only the value
    Frozen at Hook entry governs it, exactly like Judge/Repair Mode."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.OBSERVE)
    recording_controller = RecordingModeController()
    recording_controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=100_000)
    judge_evidence_recorder, _ = build_judge_evidence_recorder(writer=writer)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        recording_mode_controller=recording_controller,
        judge_evidence_recorder=judge_evidence_recorder,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-recording-frozen-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    # Flip Recording OFF immediately after the Hook call returns — the
    # already-frozen snapshot (FULL) inside the just-started Background
    # Task must still govern this Run's own Evidence write.
    recording_controller.apply_mode(RecordingMode.OFF)
    _wait_for_result(composition)

    deadline = time.monotonic() + 2.0
    files: list[Path] = []
    while time.monotonic() < deadline:
        files = list(tmp_path.glob("*.json"))
        if files:
            break
        time.sleep(0.005)

    assert len(files) == 1
    assert files[0].name == "req-recording-frozen-1.json"


def test_unhandled_exception_anywhere_in_the_run_still_reaches_a_terminal_state() -> None:
    """P6-CODEX-020: an exception from a stage other than the Model Call
    itself (here, the Repair Executor) must not leave Composition stuck at
    `running` forever."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(
        content='{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague"}'
    )

    def _raising_repair_executor(**_kwargs: object) -> object:
        raise RuntimeError("repair executor blew up")

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_raising_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-unhandled-1",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "failed"
    assert result.failure_reason == "unhandled_error:RuntimeError"
    assert composition.current_state() == "failed"


def test_repair_degraded_outcome_is_surfaced_on_the_judge_run_too() -> None:
    """P6-CODEX-020/021: a Repair Governance/Guardrail Hook failing
    Fail-closed must be visible on the overall Judge Run state, not only
    buried inside Repair's own Evidence."""
    judge_controller = JudgeModeController()
    judge_controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    service = _FakeInferenceService(
        content='{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague"}'
    )

    def _degraded_repair_executor(**_kwargs: object) -> object:
        from margpa_runtime_llm.bootstrap.repair_live_integration import RepairExecutionResult

        return RepairExecutionResult(
            request_id="req-degraded-1",
            outcome="worse",
            accepted=False,
            new_turn_id=None,
            rejected_reason="governance_post_hook_exception_fail_closed",
            degraded=True,
        )

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_degraded_repair_executor,  # type: ignore[arg-type]
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-degraded-1",
            user_input="Question",
            assistant_content="A shaky answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "degraded"
    assert composition.current_state() == "degraded"


def test_main_preemption_reaching_judge_produces_cancelled_terminal_state() -> None:
    """P6-CODEX-019/020: a Main Turn preempting the shared Model mid-Judge
    Run must reach a distinct `cancelled` terminal state, never be decoded
    as if a possibly-truncated response were a genuine Judge answer."""

    class _SelfCancellingService:
        def __init__(self) -> None:
            self.calls: list[GenerationRequest] = []

        def generate(
            self,
            request: GenerationRequest,
            *,
            cancellation: CancellationToken | None = None,
        ) -> GenerationResult:
            self.calls.append(request)
            if cancellation is not None:
                cancellation.cancel()
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content="",
                finish_reason=FinishReason.CANCELLED,
                usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
                timing=GenerationTiming(total_generation_seconds=0.01),
                runtime_info=_RUNTIME_REF,
            )

    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _SelfCancellingService()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-cancel-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "cancelled"
    assert result.failure_reason == "preempted_by_main_priority"
    assert composition.current_state() == "cancelled"
