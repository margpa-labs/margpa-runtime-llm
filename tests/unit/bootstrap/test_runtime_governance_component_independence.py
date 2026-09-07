"""P9-1 Component Independence Rework (WU-01): reproduces, and verifies the
fix for, the confirmed coupling Failure the Codex Controller Exact Handoff
(`phase_9_controller_component_independence_gemma_guard_main_rework_exact_
handoff_ja_20260905121655.md`) describes in its own section 2 (確定
Failure): Current Production's Main Governance PRE hook only ever calls
`RuntimeGovernanceComposition.begin_semantic_turn()` when Main's own mode is
not `off` (`runtime_governance.py`'s `_pre_hook`, unchanged by this Rework),
so `SemanticRuntimeCoordinator._current` stays `None` forever whenever Main
is OFF/absent for a Turn -- and the pre-Rework `web_application.py` wiring
handed the Judge Completion Hook a purely *read-only* `semantic_snapshot_
provider` (`runtime_governance_composition.semantic_runtime.snapshot_for()`,
returning `None` when `runtime_governance_composition is None` too), so a
Dedicated Judge (Selene/Gemma-shaped) dispatch with real Semantic Criteria
selected always failed `semantic_snapshot_unavailable` whenever Main was
OFF/absent, regardless of Judge's own Mode.

This module tests the fix's two new collaborators directly (`runtime_
governance.build_neutral_semantic_runtime()` and `runtime_governance.
JudgeSemanticTurnProvider`) at the Fixture level -- no real Model, matching
this Rework's own "全81組合せへ重い実Modelを回さない" instruction: Mode/
Call/Authority invariants are proven via Parameterized Fixtures here; real-
Model verification is reserved for WU-02's own representative real-hardware
trial.

Group C (`test_build_phase1_web_runtime_wires_a_neutral_judge_snapshot_
provider_when_main_is_absent`) exercises the actual `web_application.py`
composition-root wiring end-to-end (via `build_phase1_web_runtime()` itself,
`build_judge_completion_hook` captured rather than really invoked) --
Groups A/B construct `JudgeSemanticTurnProvider` directly, which proves the
new collaborator and the Dispatch Router are each correct, but neither
touches `web_application.py`'s own wiring code, so neither could catch a
regression reintroducing the pre-Rework read-only lambda there. Group C is
the one that can and does: Sabotage-regression note (recorded in the Exact
Return, not re-derived here) -- reverting `web_application.py`'s
`semantic_snapshot_provider=` wiring to the pre-Rework read-only lambda
(`runtime_governance_composition.semantic_runtime.snapshot_for(...) if
runtime_governance_composition is not None else None`) makes that Group C
test fail (the captured provider becomes `None` when `runtime_governance_
enabled=False`), confirming it genuinely detects the reproduced coupling
defect."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from margpa_runtime_llm.bootstrap import web_application as web_application_module
from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    LiveJudgeResult,
    build_judge_completion_hook,
)
from margpa_runtime_llm.bootstrap.phase1_application import Phase1Application
from margpa_runtime_llm.bootstrap.runtime_governance import (
    JudgeSemanticTurnProvider,
    RuntimeGovernanceComposition,
    SemanticRuntimeBindingContext,
    build_neutral_semantic_runtime,
)
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
    JudgeExecutionModeSnapshot,
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
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    ModelLoadConfig,
    ModelRuntimeReference,
)
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    SemanticRuntimeCoordinator,
    resolve_semantic_action,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticFinalDisposition,
    SemanticProviderState,
    SemanticTurnSnapshot,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig

_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Local, minimal duplicates of `test_judge_live_integration_dispatch_
# router.py`'s own Fixture Fakes -- `tests/unit/bootstrap/` has no
# `__init__.py` (unlike e.g. `tests/unit/repair/`), so a relative
# cross-module import is not available here without a repo-wide test-
# package structure change out of this Rework's own narrow scope.
_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key="main.test-model",
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)
_SELENE_PROVIDER_ID = "judge.selene-1-mini-llama-3.1-8b-q5-k-m"


class _FakeInferenceService:
    def __init__(self, *, content: str) -> None:
        self.content = content
        self.calls: list[GenerationRequest] = []
        self.runtime_info: object | None = None

    def count_chat_prompt_tokens(self, messages: tuple[object, ...], thinking_mode: object) -> int:
        del thinking_mode
        return sum(len(str(getattr(message, "content", ""))) for message in messages)

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


class _FakeSeleneEvaluator:
    def __init__(self, *, response: SemanticEvaluationResponse) -> None:
        self._response = response
        self.calls: list[SemanticEvaluationRequest] = []
        self.inference_service: object | None = None

    def evaluate(
        self,
        *,
        request: SemanticEvaluationRequest,
        cancellation: CancellationToken | None = None,
        inference_budget_ms: int = 0,
        late_worker_observer: Callable[[Future[object]], None] | None = None,
        batch_evidence_observer: Callable[[object], None] | None = None,
    ) -> SemanticEvaluationResponse:
        del cancellation, inference_budget_ms, late_worker_observer, batch_evidence_observer
        self.calls.append(request)
        return self._response


class _FakeSeleneRoleAdapter:
    def __init__(self, *, provider_id: str, evaluator: _FakeSeleneEvaluator) -> None:
        self.provider_id = provider_id
        self.semantic_evaluator = evaluator


class _Handle:
    def __init__(self, adapter: object, *, lease: object = "test-lease") -> None:
        self.adapter = adapter
        self.lease = lease


def _handle(adapter: object, *, lease: object = "test-lease") -> _Handle:
    return _Handle(adapter, lease=lease)


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


def _criterion(*, criterion_id: str = "semantic.argd.evidence.1") -> SemanticCriterion:
    return SemanticCriterion(
        criterion_id=criterion_id,
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


def _static_context(
    *,
    judge_mode: str = "enforce",
    repair_mode: str = "off",
    configured_provider: str = _SELENE_PROVIDER_ID,
    active_provider: str | None = _SELENE_PROVIDER_ID,
    provider_state: SemanticProviderState = SemanticProviderState.ACTIVE,
) -> SemanticRuntimeBindingContext:
    return SemanticRuntimeBindingContext(
        language="en",
        judge_mode=judge_mode,
        repair_mode=repair_mode,
        configured_provider=configured_provider,
        active_provider=active_provider,
        provider_state=provider_state,
        budget_profile="test",
        max_criteria=8,
    )


class _FixedMainMode:
    """A `main_mode_provider` Callable stand-in a real Composition Root
    would derive from `RuntimeGovernanceComposition.mode_controller.
    current_mode_value` (when Main exists) or the literal `"absent"`
    sentinel (when it does not) -- see `web_application.py`'s own
    `_current_main_mode()`."""

    def __init__(self, mode: str) -> None:
        self._mode = mode

    def __call__(self) -> str:
        return self._mode


# ---------------------------------------------------------------------------
# Group A: `JudgeSemanticTurnProvider` / `build_neutral_semantic_runtime` --
# pure Fixture-level proof of the neutral Turn-freezing boundary itself.
# ---------------------------------------------------------------------------


def test_judge_gets_a_snapshot_when_main_is_off_and_never_froze_one() -> None:
    """The exact confirmed Failure shape: nothing ever called `begin()` for
    this `request_id` (Main OFF means its own PRE hook never does) -- the
    neutral provider must still freeze one itself and hand back a valid,
    non-`None` Snapshot correlated to the same `request_id`, never raising
    and never requiring Main to be turned on."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode("off"),
    )

    snapshot = provider("req-main-off-1")

    assert snapshot is not None
    assert snapshot.request_id == "req-main-off-1"
    assert snapshot.frozen_main_mode == "off"
    assert snapshot.frozen_judge_mode == "enforce"


def test_judge_gets_a_snapshot_when_main_composition_is_entirely_absent() -> None:
    """Main Composition absent entirely (`runtime_governance_enabled=
    False`) is a distinct state from "Main present but OFF" -- the
    `main_mode_provider` reports the `"absent"` sentinel (see `web_
    application.py`'s own `_current_main_mode()`), and the neutral provider
    must behave identically to the OFF case: a valid Snapshot, never a
    dependency on Main existing at all."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode("absent"),
    )

    snapshot = provider("req-main-absent-1")

    assert snapshot is not None
    assert snapshot.request_id == "req-main-absent-1"
    assert snapshot.frozen_main_mode == "absent"


def test_main_and_judge_share_the_identical_turn_result_whichever_freezes_first() -> None:
    """Main OBSERVE/ENFORCE may consume the exact same Turn Result Judge
    already froze (Judge ran first because Main's own PRE hook happened to
    run after -- not the normal production ordering, but the invariant
    must hold regardless of which side gets there first): a second read
    must never re-freeze a new generation."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(judge_mode="observe"),
        main_mode_provider=_FixedMainMode("observe"),
    )

    first = provider("req-shared-1")
    assert first is not None
    # Simulates Main's own `RuntimeGovernanceComposition.begin_semantic_
    # turn()` reading the Turn back after Judge already froze it -- Main
    # must see the identical Snapshot, not a fresh one.
    main_side_read = coordinator.snapshot_for(request_id="req-shared-1")
    second_judge_read = provider("req-shared-1")

    assert main_side_read is not None
    assert main_side_read.generation == first.generation
    assert main_side_read.frozen_digest_sha512 == first.frozen_digest_sha512
    assert second_judge_read is not None
    assert second_judge_read.generation == first.generation
    assert second_judge_read.frozen_digest_sha512 == first.frozen_digest_sha512


def test_main_freezing_first_is_read_back_unchanged_by_judge() -> None:
    """The normal production ordering: Main's own PRE hook (`begin()`)
    always runs before Judge's POST-generation dispatch when Main is
    active. Judge's neutral provider must read that exact same Snapshot
    back, never overwrite it with a second `begin()`."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    main_frozen = coordinator.begin(
        request_id="req-main-first-1",
        language="ja",
        main_mode="enforce",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_SELENE_PROVIDER_ID,
        active_provider=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        # A deliberately different Context than what Main actually froze
        # with -- if the provider ever re-froze instead of reading back,
        # this divergent Context would be visible in the result.
        context_provider=lambda: _static_context(judge_mode="off"),
        main_mode_provider=_FixedMainMode("off"),
    )

    judge_read = provider("req-main-first-1")

    assert judge_read is not None
    assert judge_read.generation == main_frozen.generation
    assert judge_read.frozen_digest_sha512 == main_frozen.frozen_digest_sha512
    assert judge_read.frozen_judge_mode == "enforce"  # Main's own freeze, not the Provider's


def test_zero_criteria_provider_converges_to_general_quality_never_forces_main_on() -> None:
    """A Criteria Provider Port reporting zero Descriptors (no Reference
    Bundle, or Main Governance never configured) must still let Judge
    freeze a valid Turn -- with an empty Criteria tuple, converging to
    Judge's own general-quality path (see `judge_live_integration.py`'s
    `_run_judge_and_repair`'s own `semantic_snapshot.criteria` branch) --
    never silently requiring Main to be turned on to get any Snapshot."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode("absent"),
    )

    snapshot = provider("req-zero-criteria-1")

    assert snapshot is not None
    assert snapshot.criteria == ()
    assert snapshot.frozen_main_mode == "absent"


def test_runtime_governance_composition_uses_the_injected_shared_coordinator() -> None:
    """`RuntimeGovernanceComposition(semantic_runtime=...)` must genuinely
    share the injected Coordinator instance, not merely accept the
    parameter cosmetically -- a Turn Main's own `begin_semantic_turn()`
    freezes must be visible on the exact same external `coordinator`
    object a Judge-side `JudgeSemanticTurnProvider` was also built from."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    capability = RuntimeCapabilitySnapshot(
        model_key="main.test-model",
        backend_kind="fake",
        supports_streaming=True,
        supports_thinking=False,
        max_context_tokens=8192,
    )
    composition = RuntimeGovernanceComposition(
        capability=capability,
        semantic_runtime=coordinator,
    )
    composition.set_semantic_context_provider(
        lambda: SemanticRuntimeBindingContext(
            language="en",
            judge_mode="off",
            repair_mode="off",
        )
    )

    composition.begin_semantic_turn(request_id="req-injected-1", main_mode="enforce")

    # Read back from the *external* coordinator reference directly -- not
    # through `composition` at all -- proving this is genuine sharing, not
    # a private instance `RuntimeGovernanceComposition` happens to also
    # expose under the same attribute name.
    shared_read = coordinator.snapshot_for(request_id="req-injected-1")
    assert shared_read is not None
    assert shared_read.frozen_main_mode == "enforce"


@pytest.mark.parametrize("main_mode", ["off", "absent"])
def test_main_off_or_absent_never_produces_main_repair_requested_even_with_a_deviation(
    main_mode: str,
) -> None:
    """The top-level invariant's other half: "Main OFFならMain Evidence/
    Action 0". Even when a Dedicated Judge genuinely evaluates a real
    Criterion and finds a DEVIATION, `resolve_semantic_action()` (Main's
    own, unchanged, Action-resolution function) must never authorize
    `REPAIR_REQUESTED` for a Turn whose `frozen_main_mode` truthfully
    reports `off`/`absent` -- this is what keeps `_finalize_judge_
    dispatch()`'s `main_requests_repair` False in that case, without any
    change to `resolve_semantic_action()` itself."""
    coordinator = build_neutral_semantic_runtime(descriptors=(),)
    criterion = _criterion()
    # Rebuild the Coordinator with a real Criterion this time (the empty-
    # descriptors helper above only proves the zero-criteria path).
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode(main_mode),
    )

    snapshot = provider("req-no-main-action-1")
    assert snapshot is not None
    deviation_result = SemanticCriterionResult(
        criterion_id=criterion.criterion_id,
        descriptor_id=criterion.descriptor_id,
        disposition=SemanticCriterionDisposition.DEVIATION,
        confidence=0.9,
    )

    action = resolve_semantic_action(snapshot=snapshot, results=(deviation_result,))

    # `OBSERVED` is itself proof of "never REPAIR_REQUESTED" -- `resolve_
    # semantic_action()` returns exactly one `SemanticFinalDisposition`, so
    # asserting the actual value already excludes every other one (mypy
    # correctly flags a further `is not REPAIR_REQUESTED` here as a
    # non-overlapping/redundant identity check on the now-narrowed Literal).
    assert action.executed_disposition is SemanticFinalDisposition.OBSERVED


@pytest.mark.parametrize("main_mode", ["off", "observe", "enforce", "absent"])
@pytest.mark.parametrize("judge_mode", ["off", "observe", "enforce"])
def test_provider_never_raises_and_honestly_freezes_both_modes_across_the_matrix(
    main_mode: str, judge_mode: str
) -> None:
    """Handoff WU-01's own "最低Matrix" collapsed into one Parameterized
    Fixture sweep (16 combinations, zero real Model Calls): regardless of
    Main's mode/absence or Judge's own mode, the neutral provider always
    freezes a valid, correlated Snapshot that honestly reports both modes
    -- Judge's own Mode is never coupled to, or silently overridden by,
    Main's."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(judge_mode=judge_mode),
        main_mode_provider=_FixedMainMode(main_mode),
    )

    snapshot = provider(f"req-matrix-{main_mode}-{judge_mode}")

    assert snapshot is not None
    assert snapshot.frozen_main_mode == main_mode
    assert snapshot.frozen_judge_mode == judge_mode


# ---------------------------------------------------------------------------
# Group B: end-to-end proof through the real Judge Completion Hook Dispatch
# Router (`judge_live_integration.build_judge_completion_hook`) -- confirms
# the fix closes the actual `semantic_snapshot_unavailable` Failure a real
# Selene/Gemma-shaped Dedicated Judge hit with Main OFF/absent, not merely
# that the new collaborator classes work in isolation.
# ---------------------------------------------------------------------------


def test_dispatch_completes_when_main_is_off_and_never_froze_a_turn() -> None:
    """WU-01 Matrix items 1-3: Main OFF, Dedicated Judge (Selene-shaped,
    standing in for Gemma -- the Dispatch Router treats both identically,
    see `judge_live_integration.py`'s own `selene_evaluator is not None`
    branch) ENFORCE -- must dispatch and complete, never
    `semantic_snapshot_unavailable`."""
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(judge_mode="enforce"),
        main_mode_provider=_FixedMainMode("off"),
    )
    selene_response = SemanticEvaluationResponse(
        request_id="req-dispatch-main-off-1",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.95,
            ),
        ),
        latency_ms=10,
    )
    evaluator = _FakeSeleneEvaluator(response=selene_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="should never be used")

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        # No `semantic_result_recorder`/`semantic_deferred_recorder` wired
        # -- matches the true "Main Composition entirely absent" wiring
        # shape in `web_application.py` (those two stay `None` whenever
        # `runtime_governance_composition is None`).
        semantic_snapshot_provider=provider,
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-dispatch-main-off-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "completed"
    assert result.failure_reason != "semantic_snapshot_unavailable"
    assert result.recommendation == "accept"
    assert service.calls == []
    assert len(evaluator.calls) == 1


def test_dispatch_completes_when_main_composition_is_entirely_absent() -> None:
    """WU-01 Matrix item 5: no Main Composition at all (`runtime_
    governance_enabled=False`) -- Dedicated Judge dispatch must still
    complete, exercising the `"absent"` sentinel path end-to-end through
    the real Dispatch Router."""
    criterion = _criterion(criterion_id="semantic.argd.evidence.2")
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(judge_mode="enforce"),
        main_mode_provider=_FixedMainMode("absent"),
    )
    selene_response = SemanticEvaluationResponse(
        request_id="req-dispatch-main-absent-1",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.95,
            ),
        ),
        latency_ms=10,
    )
    evaluator = _FakeSeleneEvaluator(response=selene_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="should never be used")

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=provider,
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-dispatch-main-absent-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "completed"
    assert result.failure_reason != "semantic_snapshot_unavailable"
    assert result.recommendation == "accept"


@pytest.mark.parametrize("repair_mode_value", ["off", "enforce"])
def test_dispatch_completes_with_main_off_across_repair_off_and_enforce(
    repair_mode_value: str,
) -> None:
    """WU-01 Matrix items 2-3 explicitly: Main OFF, Judge ENFORCE, with
    Repair OFF and separately Repair ENFORCE -- the Snapshot's availability
    (and thus whether dispatch even starts) must not depend on Repair's
    Mode at all."""
    criterion = _criterion(criterion_id="semantic.argd.evidence.3")
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(
            judge_mode="enforce", repair_mode=repair_mode_value
        ),
        main_mode_provider=_FixedMainMode("off"),
    )
    selene_response = SemanticEvaluationResponse(
        request_id=f"req-dispatch-repair-{repair_mode_value}",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.95,
            ),
        ),
        latency_ms=10,
    )
    evaluator = _FakeSeleneEvaluator(response=selene_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="should never be used")

    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=provider,
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id=f"req-dispatch-repair-{repair_mode_value}",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert result.execution_state == "completed"
    assert result.failure_reason != "semantic_snapshot_unavailable"


def test_dispatch_unaffected_by_which_guardrail_hook_is_wired_matrix_item_6() -> None:
    """WU-01 Matrix item 6: Guard OFF/OBSERVE/ENFORCE combined with the
    above must not change whether Judge can dispatch at all -- proven
    structurally here by wiring two different fake `guardrail_post_hook`
    values (standing in for Guard OFF vs. an active Guard Hook) and
    confirming the Snapshot-availability outcome (`execution_state`/
    `failure_reason`) is identical either way; `build_judge_completion_
    hook()`'s own dispatch routing never reads `guardrail_post_hook` to
    decide whether to call `semantic_snapshot_provider` at all."""
    criterion = _criterion(criterion_id="semantic.argd.evidence.4")

    def _run_with_guard_hook(guard_hook: object | None) -> str:
        coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
        provider = JudgeSemanticTurnProvider(
            coordinator=coordinator,
            context_provider=lambda: _static_context(judge_mode="enforce"),
            main_mode_provider=_FixedMainMode("off"),
        )
        selene_response = SemanticEvaluationResponse(
            request_id="req-dispatch-guard-matrix",
            generation=1,
            provider_id=_SELENE_PROVIDER_ID,
            provider_state=SemanticProviderState.ACTIVE,
            results=(
                SemanticCriterionResult(
                    criterion_id=criterion.criterion_id,
                    descriptor_id=criterion.descriptor_id,
                    disposition=SemanticCriterionDisposition.PASS,
                    confidence=0.95,
                ),
            ),
            latency_ms=10,
        )
        evaluator = _FakeSeleneEvaluator(response=selene_response)
        controller = JudgeModeController()
        controller.apply_mode(EvaluationMode.ENFORCE)
        service = _FakeInferenceService(content="should never be used")
        hook, composition = build_judge_completion_hook(
            service=service,  # type: ignore[arg-type]
            judge_mode_controller=controller,
            model_access_coordinator=ModelAccessCoordinator(),
            semantic_snapshot_provider=provider,
            guardrail_post_hook=guard_hook,  # type: ignore[arg-type]
            begin_judge_role_turn=lambda: _handle(
                _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
            ),
        )
        hook(
            JudgeCompletionContext(
                model_key="main.test-model",
                request_id="req-dispatch-guard-matrix",
                user_input="Question",
                assistant_content="Answer",
            )
        )
        return _wait_for_result(composition).execution_state

    outcome_guard_absent = _run_with_guard_hook(None)
    outcome_guard_present = _run_with_guard_hook(lambda *_args, **_kwargs: (False, ""))

    assert outcome_guard_absent == "completed"
    assert outcome_guard_present == "completed"
    assert outcome_guard_absent == outcome_guard_present


# ---------------------------------------------------------------------------
# Group C: the actual `web_application.py` composition-root wiring, exercised
# end-to-end through `build_phase1_web_runtime()` itself -- the only Group
# that can catch a regression reintroducing the pre-Rework read-only
# `semantic_snapshot_provider` lambda (Groups A/B construct `JudgeSemantic
# TurnProvider` directly and never touch `web_application.py`'s own code).
# ---------------------------------------------------------------------------


def test_build_phase1_web_runtime_wires_a_neutral_judge_snapshot_provider_when_main_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Main Governance entirely absent (`runtime_governance_enabled=False`)
    with the Judge/Repair/Recording feature-mode surface enabled
    (`feature_modes_enabled=True`) -- the real Composition Root must still
    wire a working `semantic_snapshot_provider` into `build_judge_
    completion_hook()`, never `None` and never the pre-Rework read-only
    lambda that always returned `None` in this exact shape. `build_judge_
    completion_hook` itself is monkeypatched to *capture* its kwargs rather
    than build the real Hook -- this test is about what `web_application.py`
    hands it, not about the Dispatch Router's own behavior (already proven
    by Group B)."""
    service = SimpleNamespace(
        runtime_info=SimpleNamespace(
            model_key="main.model",
            backend_key="fake-backend",
            loaded_context_size=4096,
            effective_capabilities=SimpleNamespace(features=frozenset()),
            device_kind="gpu",
            acceleration_api="metal",
        ),
        count_text_tokens=lambda text: len(text.split()),
        count_chat_prompt_tokens=lambda messages, thinking_mode: 1,
    )
    presentation = ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )
    config = SimpleNamespace(
        selected_model="main.model",
        profile_key="mac.local",
        generation=GenerationParameters(max_new_tokens=2048),
        response=SimpleNamespace(language=ResponseLanguage.JA),
        presentation=presentation,
        summarization=SummarizationConfig(),
        # `feature_modes_enabled=True` below also builds a Role Provider
        # Lifecycle (Selene/Gemma/Qwen3Guard dedicated-Role Factory), which
        # reads these two Config fields even though this Test never
        # actually activates any dedicated Role.
        model_root=_PROJECT_ROOT / "models",
        dedicated_role_load=ModelLoadConfig(),
    )
    application = cast(
        Phase1Application,
        SimpleNamespace(
            service=service,
            config=config,
            presentation_service=object(),
            close=lambda: None,
        ),
    )
    monkeypatch.setattr(
        web_application_module,
        "build_phase1_application",
        lambda **_kwargs: application,
    )
    monkeypatch.setattr(
        web_application_module,
        "start_local_conversation_persistence",
        lambda *_args, **_kwargs: pytest.fail(
            "this Test never configures explicit Persistence Settings"
        ),
    )
    captured_kwargs: dict[str, object] = {}

    def _capturing_build_judge_completion_hook(**kwargs: object) -> object:
        captured_kwargs.update(kwargs)
        return build_judge_completion_hook(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(
        web_application_module,
        "build_judge_completion_hook",
        _capturing_build_judge_completion_hook,
    )

    build_phase1_web_runtime(
        project_root=_PROJECT_ROOT,
        profile_path=None,
        registry_path=_PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml",
        runtime_governance_enabled=False,
        feature_modes_enabled=True,
    )

    provider = captured_kwargs.get("semantic_snapshot_provider")
    assert provider is not None, (
        "web_application.py must wire a non-None semantic_snapshot_provider "
        "into build_judge_completion_hook() even when Main Governance is "
        "entirely absent -- a None here is exactly the pre-Rework coupling "
        "defect this Test reproduces (Codex Controller Exact Handoff "
        "2026-09-05 12:16:55 section 2, 確定Failure)."
    )
    snapshot = cast(Callable[[str], SemanticTurnSnapshot | None], provider)(
        "req-web-runtime-main-absent-1"
    )
    assert snapshot is not None
    assert snapshot.request_id == "req-web-runtime-main-absent-1"
    assert snapshot.frozen_main_mode != "enforce"


# ---------------------------------------------------------------------------
# Group D (R2-WU-01, Controller Review IR-CI-01): "Action非介入" (executed
# disposition stays OBSERVED) and "Evidence未生成" (Main's own
# `SemanticRuntimeEvidence`/History Call 0) are two distinct claims -- the
# R1 Round only proved the first. These tests prove the second directly
# against `RuntimeGovernanceComposition.record_semantic_response()`/
# `record_semantic_deferred()` themselves, via a counting subclass of
# `SemanticRuntimeCoordinator` that never touches its own private state,
# only counts calls into `record_response()`/`record_deferred()` before
# delegating unchanged to the real implementation.
# ---------------------------------------------------------------------------


class _CountingSemanticRuntimeCoordinator(SemanticRuntimeCoordinator):
    def __init__(self, *, criteria: tuple[SemanticCriterion, ...] = ()) -> None:
        super().__init__(criteria=criteria)
        self.record_response_calls = 0
        self.record_deferred_calls = 0

    def record_response(self, **kwargs: object) -> object:  # type: ignore[override]
        self.record_response_calls += 1
        return super().record_response(**kwargs)  # type: ignore[arg-type]

    def record_deferred(self, **kwargs: object) -> object:  # type: ignore[override]
        self.record_deferred_calls += 1
        return super().record_deferred(**kwargs)  # type: ignore[arg-type]


def _composition_with_counting_coordinator(
    *, coordinator: _CountingSemanticRuntimeCoordinator
) -> RuntimeGovernanceComposition:
    capability = RuntimeCapabilitySnapshot(
        model_key="main.test-model",
        backend_kind="fake",
        supports_streaming=True,
        supports_thinking=False,
        max_context_tokens=8192,
    )
    composition = RuntimeGovernanceComposition(capability=capability, semantic_runtime=coordinator)
    composition.set_semantic_context_provider(lambda: _static_context())
    return composition


@pytest.mark.parametrize("main_mode", ["off", "absent"])
def test_main_off_or_absent_is_call_zero_into_main_semantic_evidence(main_mode: str) -> None:
    """The confirmed Controller Review Probe (IR-CI-01): `evidence_created
    = true` / `history_created = true` even though `frozen_main_mode =
    off`. This must now never happen -- `record_semantic_response()`
    itself must refuse (Call 0 into `semantic_runtime.record_response()`)
    whenever the Turn it is asked to record for was frozen with a
    `frozen_main_mode` that is not `observe`/`enforce`, distinct from
    (and in addition to) the already-proven "executed disposition stays
    OBSERVED" claim."""
    coordinator = _CountingSemanticRuntimeCoordinator(criteria=(_criterion(),))
    composition = _composition_with_counting_coordinator(coordinator=coordinator)
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode(main_mode),
    )
    snapshot = provider("req-call-zero-1")
    assert snapshot is not None
    response = SemanticEvaluationResponse(
        request_id="req-call-zero-1",
        generation=snapshot.generation,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=snapshot.criteria[0].criterion_id,
                descriptor_id=snapshot.criteria[0].descriptor_id,
                disposition=SemanticCriterionDisposition.DEVIATION,
                confidence=0.9,
            ),
        ),
        latency_ms=5,
    )

    evidence = composition.record_semantic_response(response=response)

    assert evidence is None
    assert coordinator.record_response_calls == 0
    assert coordinator.evidence_for(request_id="req-call-zero-1") is None


@pytest.mark.parametrize("main_mode", ["off", "absent"])
def test_main_off_or_absent_is_call_zero_into_main_semantic_deferred_evidence(
    main_mode: str,
) -> None:
    """Same Call-0 guarantee as above, for the deferred-recording path
    (`record_semantic_deferred()`, the ENFORCE-eligibility/pre-empted-
    dispatch counterpart of `record_semantic_response()`)."""
    coordinator = _CountingSemanticRuntimeCoordinator(criteria=(_criterion(),))
    composition = _composition_with_counting_coordinator(coordinator=coordinator)
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode(main_mode),
    )
    provider("req-call-zero-deferred-1")

    evidence = composition.record_semantic_deferred(
        request_id="req-call-zero-deferred-1",
        reason=SemanticDeferredReason.PROVIDER_UNAVAILABLE,
    )

    assert evidence is None
    assert coordinator.record_deferred_calls == 0
    assert coordinator.evidence_for(request_id="req-call-zero-deferred-1") is None


@pytest.mark.parametrize("main_mode", ["observe", "enforce"])
def test_main_observe_or_enforce_does_project_the_frozen_judge_result(main_mode: str) -> None:
    """The symmetric positive case (Handoff R2-WU-01 item 6): Main
    OBSERVE/ENFORCE -- and only OBSERVE/ENFORCE -- may project the same
    Frozen Judge Result into Main's own Semantic Evidence/History. This is
    the "Action非介入" side's opposite number: Evidence *is* created here,
    proving the Call-0 gate above is a genuine `frozen_main_mode` branch,
    not an unconditional refusal."""
    coordinator = _CountingSemanticRuntimeCoordinator(criteria=(_criterion(),))
    composition = _composition_with_counting_coordinator(coordinator=coordinator)
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode(main_mode),
    )
    snapshot = provider("req-projected-1")
    assert snapshot is not None
    response = SemanticEvaluationResponse(
        request_id="req-projected-1",
        generation=snapshot.generation,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=snapshot.criteria[0].criterion_id,
                descriptor_id=snapshot.criteria[0].descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.95,
            ),
        ),
        latency_ms=5,
    )

    evidence = composition.record_semantic_response(response=response)

    assert evidence is not None
    assert coordinator.record_response_calls == 1
    assert coordinator.evidence_for(request_id="req-projected-1") is not None


def test_begin_semantic_turn_is_a_peer_read_when_already_frozen() -> None:
    """R2-WU-01 item 2/3: `RuntimeGovernanceComposition.begin_semantic_
    turn()` must never silently re-`begin()` (a second `generation`, a
    fresh re-read of live Mode/Provider Context) once *any* caller
    (Conversation `start()`'s own eager freeze in the wired production
    shape, or -- as here -- a Judge-side read) already froze this exact
    `request_id`. A caller reaching `begin_semantic_turn()` second must
    read the identical Snapshot back, honoring whichever Context/Mode the
    first caller actually froze with."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    capability = RuntimeCapabilitySnapshot(
        model_key="main.test-model",
        backend_kind="fake",
        supports_streaming=True,
        supports_thinking=False,
        max_context_tokens=8192,
    )
    composition = RuntimeGovernanceComposition(capability=capability, semantic_runtime=coordinator)
    # A deliberately different Context than what Main would freeze with --
    # if `begin_semantic_turn()` ever re-froze instead of reading back,
    # this divergent Context would be visible in the result.
    composition.set_semantic_context_provider(lambda: _static_context(judge_mode="off"))
    first = coordinator.begin(
        request_id="req-peer-read-1",
        language="ja",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_SELENE_PROVIDER_ID,
        active_provider=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )

    second = composition.begin_semantic_turn(request_id="req-peer-read-1", main_mode="enforce")

    assert second.generation == first.generation
    assert second.frozen_digest_sha512 == first.frozen_digest_sha512
    # Main's own live `main_mode="enforce"` argument is discarded in favor
    # of the already-frozen value -- proving this really is a read, not a
    # second begin() using the caller's freshly-supplied argument.
    assert second.frozen_main_mode == "observe"


# ---------------------------------------------------------------------------
# Group E (R3-WU-01, Controller Review IR-R2-01 residual): Turn-start Freeze
# is a single Immutable boundary -- the frozen Semantic Turn Snapshot's own
# Judge/Repair Mode must be the identical value Conversation's own already-
# resolved `JudgeExecutionModeSnapshot` carries, never a second, independent
# live read that a Mode change landing between the two could make disagree;
# and a Turn-start Freeze failure must never be silently retried later with
# fresh (possibly post-generation) Live values.
# ---------------------------------------------------------------------------


def test_frozen_snapshot_uses_the_already_resolved_judge_modes_not_a_second_live_read() -> None:
    """The exact Controller Probe schedule IR-R2-01 reported: a Live Mode
    Provider that would answer `observe` if read a second time (simulating
    a Mode change landing between Conversation's own `_resolve_judge_
    modes()` call and the Semantic Turn Freeze) must never leak into the
    frozen Snapshot once `judge_modes` (Conversation's own single, already-
    resolved read) is passed in -- the Snapshot's own `frozen_judge_mode`/
    `frozen_repair_mode` must match `judge_modes` exactly, not the Context
    Provider's own independent (and here, deliberately divergent) answer."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        # A live Context Provider that would freeze `observe`/`enforce` if
        # its own judge_mode/repair_mode were used -- if the Provider ever
        # fell back to this instead of the passed `judge_modes`, the
        # Mismatch would be directly visible in the assertions below.
        context_provider=lambda: _static_context(judge_mode="observe", repair_mode="enforce"),
        main_mode_provider=_FixedMainMode("enforce"),
    )
    already_resolved_judge_modes = JudgeExecutionModeSnapshot(
        judge_mode="enforce", repair_mode="off", recording_mode="full"
    )

    snapshot = provider("req-single-freeze-1", already_resolved_judge_modes)

    assert snapshot is not None
    assert snapshot.frozen_judge_mode == "enforce"
    assert snapshot.frozen_repair_mode == "off"


def test_a_failed_turn_start_freeze_is_never_retried_with_later_live_values() -> None:
    """IR-R2-01's other confirmed gap: a Turn-start Freeze attempt that
    raises must not let a LATER call for the identical `request_id` (the
    shape a Judge Completion Hook's own post-generation `semantic_snapshot_
    provider(request_id)` call takes) retry with fresh Live values -- total
    real Context Provider calls for this `request_id` must stay at exactly
    1 (the one failed attempt), and the later call must return `None`
    (Judge converges to its own existing Typed Unavailable/Deferred
    handling for a `None` Snapshot) rather than a second, delayed `begin()`."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    calls: list[int] = []

    def _raising_once_then_succeeding() -> SemanticRuntimeBindingContext:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("live context read failed")
        return _static_context()

    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=_raising_once_then_succeeding,
        main_mode_provider=_FixedMainMode("enforce"),
    )
    judge_modes = JudgeExecutionModeSnapshot(judge_mode="enforce")

    with pytest.raises(RuntimeError):
        provider("req-failed-freeze-1", judge_modes)

    # A later call for the SAME request_id (e.g. from the Judge Completion
    # Hook, running after this Turn's generation has already completed)
    # must not retry the live read at all.
    second = provider("req-failed-freeze-1", judge_modes)

    assert second is None
    assert len(calls) == 1
    # A different, later request_id on the SAME Provider instance (a
    # genuinely new Turn) must still be able to Freeze normally -- the
    # recorded failure must never leak across Turns.
    third = provider("req-new-turn-1", judge_modes)
    assert third is not None
    assert third.request_id == "req-new-turn-1"
    assert len(calls) == 2


# ---------------------------------------------------------------------------
# Group F (R4-WU-01, Controller Review IR-R3-01): Semantic Snapshot/Freeze
# Failure/Evidence must be request-local -- a different `request_id`
# beginning afterward must never overwrite, re-Freeze, or silently discard
# an earlier `request_id`'s own already-frozen Snapshot or already-recorded
# Freeze failure. These are the exact three Controller Probes IR-R3-01
# reported, made into direct Regression Tests, plus a genuine two-Thread
# concurrent-Begin race for the identical `request_id`.
# ---------------------------------------------------------------------------


def test_a_failed_freeze_for_one_request_survives_a_different_requests_success() -> None:
    """Controller Probe 1 ("Aの開始Freeze失敗 → B成功 → Aを再読"): before
    R4-WU-01, `JudgeSemanticTurnProvider`'s own single `_begin_attempted_
    request_id`/`_begin_failed` slot was silently overwritten by B's own
    attempt (successful or not), making A wrongly eligible for a fresh
    retry the next time it was read back -- total live Context Provider
    calls for A must stay at exactly 1 forever, regardless of how many
    OTHER requests the same Provider instance goes on to serve."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    calls: list[str] = []

    def _context_provider() -> SemanticRuntimeBindingContext:
        calls.append("call")
        if len(calls) == 1:
            raise RuntimeError("A's own live context read failed")
        return _static_context()

    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=_context_provider,
        main_mode_provider=_FixedMainMode("enforce"),
    )
    judge_modes = JudgeExecutionModeSnapshot(judge_mode="enforce")

    with pytest.raises(RuntimeError):
        provider("req-a", judge_modes)
    assert len(calls) == 1

    b_snapshot = provider("req-b", judge_modes)
    assert b_snapshot is not None
    assert len(calls) == 2

    # Re-reading A after B has succeeded must still return `None` (Model
    # Call 0), never a fresh, delayed re-Freeze attempt against A.
    late_a = provider("req-a", judge_modes)
    assert late_a is None
    assert len(calls) == 2


def test_a_successful_freeze_survives_a_different_requests_success_unchanged() -> None:
    """Controller Probe 2 ("A成功(generation 1) → B成功(generation 2) →
    Aを再読"): before R4-WU-01, `SemanticRuntimeCoordinator`'s own single
    `_current` slot meant B beginning made A's own Snapshot unreachable via
    `snapshot_for()`, so a later `JudgeSemanticTurnProvider.__call__("A")`
    performed a brand-new Freeze (a new generation, a changed digest)
    instead of reading A's own original Snapshot back unchanged."""
    coordinator = build_neutral_semantic_runtime(descriptors=())
    provider = JudgeSemanticTurnProvider(
        coordinator=coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode("enforce"),
    )
    judge_modes = JudgeExecutionModeSnapshot(judge_mode="enforce")

    a_first = provider("req-a", judge_modes)
    assert a_first is not None
    assert a_first.generation == 1

    b_snapshot = provider("req-b", judge_modes)
    assert b_snapshot is not None
    assert b_snapshot.generation == 2

    late_a = provider("req-a", judge_modes)
    assert late_a is not None
    assert late_a.generation == 1
    assert late_a.frozen_digest_sha512 == a_first.frozen_digest_sha512


def test_as_late_response_is_recorded_after_b_has_begun_never_dropped() -> None:
    """Controller Probe 3 ("A成功 → B成功 → AのResponseを記録"): before
    R4-WU-01, A's genuine Background Judge Response arriving after B had
    already begun was silently rejected by `record_response()` (`current`
    had already moved to B), recording neither A's Evidence nor its Action
    -- exactly the defect this Ledger fixes. B's own Current/Evidence must
    stay entirely unaffected by A's late, correctly-attributed recording."""
    criterion = SemanticCriterion(
        criterion_id="semantic.argd.rule.1",
        descriptor_id="argd.rule.1",
        source_definition_id="argd",
        source_definition_digest_sha512="a" * 128,
        source_pointer="/rules/1",
        source_text_digest_sha512="a" * 128,
        instruction="Do not contradict the supplied evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )
    real_coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    provider = JudgeSemanticTurnProvider(
        coordinator=real_coordinator,
        context_provider=lambda: _static_context(),
        main_mode_provider=_FixedMainMode("enforce"),
    )
    judge_modes = JudgeExecutionModeSnapshot(judge_mode="enforce")

    a_snapshot = provider("req-a", judge_modes)
    assert a_snapshot is not None
    b_snapshot = provider("req-b", judge_modes)
    assert b_snapshot is not None
    current_after_b = real_coordinator.current_snapshot()
    assert current_after_b is not None
    assert current_after_b.request_id == "req-b"

    a_response = SemanticEvaluationResponse(
        request_id="req-a",
        generation=a_snapshot.generation,
        provider_id=a_snapshot.configured_provider,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.9,
            ),
        ),
        latency_ms=1,
    )
    a_evidence = real_coordinator.record_response(response=a_response, structural=())

    assert a_evidence is not None
    assert a_evidence.request_id == "req-a"
    assert real_coordinator.evidence_for(request_id="req-a") is not None
    # B's own Current/Evidence must remain untouched by A's late recording.
    assert real_coordinator.evidence_for(request_id="req-b") is None
    current_after_a_recorded = real_coordinator.current_snapshot()
    assert current_after_a_recorded is not None
    assert current_after_a_recorded.request_id == "req-b"
    assert real_coordinator.latest_evidence() is None


def test_two_threads_racing_begin_for_the_identical_request_id_yield_one_generation() -> None:
    """Controller Review IR-R3-01's own explicit additional requirement:
    "さらに二Threadが同じrequestを同時Beginしても一つのgenerationだけが
    得られることを確認する". `SemanticRuntimeCoordinator.begin()`'s own
    idempotent-under-Lock check (never the caller's separate, non-atomic
    `snapshot_for()`-then-`begin()` pre-check alone) must make this
    deterministic regardless of Thread scheduling."""
    coordinator = SemanticRuntimeCoordinator(criteria=())
    ready = threading.Barrier(2)
    snapshots: list[SemanticTurnSnapshot] = []
    lock = threading.Lock()

    def _begin() -> None:
        ready.wait(timeout=5.0)
        snapshot = coordinator.begin(
            request_id="req-race",
            language="en",
            main_mode="enforce",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider="judge.test",
            active_provider="judge.test",
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
        with lock:
            snapshots.append(snapshot)

    threads = [threading.Thread(target=_begin) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5.0)

    assert len(snapshots) == 2
    assert snapshots[0].generation == snapshots[1].generation == 1
    assert snapshots[0].frozen_digest_sha512 == snapshots[1].frozen_digest_sha512
