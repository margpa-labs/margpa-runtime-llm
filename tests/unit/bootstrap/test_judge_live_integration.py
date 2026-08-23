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
        governance_post_hook: object,
        guardrail_post_hook: object,
        cancellation: object = None,
        model_runtime_info: object = None,
        stage_hook: object = None,
    ) -> object:
        from margpa_runtime_llm.bootstrap.repair_live_integration import RepairExecutionResult

        captured_calls.append(
            {
                "request_id": request_id,
                "user_input": user_input,
                "original_answer": original_answer,
                "before_recommendation": before_recommendation,
                "judge_reasoning": judge_reasoning,
            }
        )
        return RepairExecutionResult(
            request_id=request_id,
            outcome="improved",
            accepted=True,
            new_turn_id="new-turn-1",
            rejected_reason=None,
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
    assert captured_calls[0]["request_id"] == "req-repair-1"
    assert captured_calls[0]["judge_reasoning"] == "vague"
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    assert result.repair_new_turn_id == "new-turn-1"


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
    assert files[0].name == "req-evidence-1-judge-evidence.json"
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
    assert files[0].name == "req-recording-frozen-1-judge-evidence.json"


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
