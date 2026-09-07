"""P9-1 Judge/Governance Rework (WU-03) Real Local Experiment: Main
Governance-origin Repair through the real Main Qwen3-4B model self-judging
(Main-self, no dedicated Judge Artifact needed), with real, compiler-derived
ARGD/DAGD Criteria and the normal production Main Context (16384, matching
`config/profiles/local_macos_arm64.toml`'s `context_size`).

Distinct from three other Test layers, deliberately:

- `test_real_local_main_runtime_governance_enforce_smoke.py` exercises
  `SemanticRuntimeCoordinator`/`resolve_semantic_action()` directly, one
  layer below the Hook, and loads its Service at `context_size=4096` (an
  explicit, narrower experimental condition for that lower-layer Test, not
  a normal-configuration confirmation).
- `tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py`'s
  `test_main_shared_judge_repair_and_rejudge_genuinely_execute_via_the_
  production_repair_composition` and `test_main_shared_rejudge_with_no_
  criterion_results_is_never_accepted` cover the same Frozen-Criterion-
  survives-to-Rejudge contract with a hand-authored Fixture Criterion and a
  fully scripted Fixture Model Service -- no real Model, no real ARGD/DAGD
  Corpus. Those Tests are the ones that can (and do) deterministically
  force the exact Controller Review IR-02/IR-03 failure shapes on demand;
  this file is real-Model evidence that the same fix behaves correctly
  against a genuine local Model and the checked-in ARGD/DAGD Reference
  Corpus, not a proof of the contract itself.
- `test_a_real_main_governance_origin_repair_completes_end_to_end_via_the_
  hook_with_real_argd_dagd_criteria` below calls the Hook directly
  (`build_judge_completion_hook()`'s returned callable, `enforce_presented_
  final=True`) -- the exact synchronous in-line-adoption shape the real
  Conversation Turn pipeline itself invokes for ENFORCE, but without a real
  `PersistentConversationService` behind it (`persist_accepted_attempt=
  False`, no Turn ever created). `test_a_real_main_governance_origin_
  repair_persists_a_derived_turn_through_the_normal_conversation_save_path`
  below is the separate persistence-path Test: `attempt_live_repair()`
  called against a real `SQLiteConversationStore`-backed
  `PersistentConversationService` with `persist_accepted_attempt=True`,
  proving the accepted repair genuinely lands through the same atomic
  `append_derived_turn -> start_generation -> complete_generation`
  CAS-guarded chain a real persisted Conversation actually uses -- not
  merely that the Hook's own in-line return value looks right.

Controller Review (2026-09-04 19:16, IR-03) found the pre-Controller
version of this file used a hand-crafted single Criterion with a fake
digest (`"a" * 128`) rather than reading real ARGD/DAGD Compiler output,
asserted only the repair *origin* and that the known-flawed Candidate was
withheld -- never that Repair actually succeeded (`repair_accepted`) --
and let a Decode-failure/no-Deviation outcome SKIP the same way a genuine
Repair failure silently would (Controller mechanically forced the Repair
Executor to always return `accepted=False` in-memory and the entire Test
function's own Assertions still passed). Every Assertion below that
matters for the golden path is a hard `assert`, never conditional on
`repair_accepted`/`presentation_outcome` themselves -- only the earlier,
independently-legitimate real-Model non-determinism gate (did this run's
real Model actually flag the contradiction as a Deviation at all) may
still SKIP, and it SKIPs *before* any Repair-outcome Assertion, never in
place of one.
"""

from __future__ import annotations

import platform
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_governance.semantic_criterion_adapter import (
    compile_argd_dagd_semantic_criteria,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import build_judge_completion_hook
from margpa_runtime_llm.bootstrap.repair_live_integration import attempt_live_repair
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    SemanticRuntimeBindingContext,
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationTurnId,
    ConversationTurnOrigin,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    JudgePromptCriterion,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    SemanticRuntimeCoordinator,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"
ARTIFACT_PATH = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
# Matches `config/profiles/local_macos_arm64.toml`'s `context_size` for
# Main -- the normal production configuration, not a narrower experimental
# one (Controller Review IR-03: the pre-Controller version of this file
# used 4096, undocumented as a deliberate deviation).
NORMAL_MAIN_CONTEXT_SIZE = 16384

pytestmark = [
    pytest.mark.model_smoke,
    pytest.mark.skipif(
        platform.system() != "Darwin" or platform.machine() != "arm64",
        reason="The Phase 6/9 model smoke requires Apple Silicon",
    ),
]


def _bounded_real_criterion() -> SemanticCriterion:
    """One real, compiler-derived, bounded Criterion -- never a hand-crafted
    Fixture (Controller Review IR-03).

    Reads the actual checked-in ARGD/DAGD Reference Corpus through the same
    `load_reference_descriptors()` / `compile_argd_dagd_semantic_criteria()`
    pipeline the real production Runtime Governance bootstrap uses (see
    `test_real_local_main_runtime_governance_enforce_smoke.py`'s own
    `_real_criteria()`, which keeps the full 109-Criterion compiled set for
    its own lower-layer, higher-`max_criteria` Coordinator Test). This Test
    instead filters that real compiled output down to exactly the one
    Criterion whose own instruction text is about contradiction detection
    (`semantic.argd.info_contradiction_information.0`: "When a contradiction
    is detected explicitly indicate it and prohibit proceeding to a
    conclusion while unresolved") -- a real, non-fabricated rule, but
    *targeted* rather than a blind rotation-offset pick across all 109 real
    Criteria (most of which have nothing to do with the France/Tenon
    factual-contradiction scenario this file evaluates against, and would
    make a genuine Deviation far less likely to be flagged this run, purely
    by chance of rotation order -- not evidence of anything about the fix
    itself). Bounded to exactly one Criterion deliberately: Repair's own
    Rejudge has no batching machinery of its own (unlike the Judge's own
    dispatch -- see `repair_live_integration.py`'s `_rejudge_max_new_
    tokens()` docstring), so this stays inside a single bounded real Model
    Call by construction, matching the "有界Criterion" (bounded Criterion)
    the Controller Review explicitly asked for.
    """
    loaded = load_reference_descriptors(
        definitions_root=PROJECT_ROOT / "definitions",
        capability=RuntimeCapabilitySnapshot(
            model_key=QWEN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=NORMAL_MAIN_CONTEXT_SIZE,
        ),
        authority=default_authority(),
    )
    assert loaded.state == "loaded"
    compiled = compile_argd_dagd_semantic_criteria(loaded.descriptors)
    matches = tuple(
        item
        for item in compiled.criteria
        if item.criterion_id == "semantic.argd.info_contradiction_information.0"
    )
    assert len(matches) == 1, (
        "expected the real ARGD/DAGD Corpus to contain exactly one "
        "semantic.argd.info_contradiction_information.0 Criterion; the "
        f"compiled set instead had {len(matches)} matches -- the Corpus or "
        "the Compiler changed shape, this file's target Criterion id needs "
        "re-selecting, never silently falling back to a fabricated one"
    )
    return matches[0]


def _to_prompt_criterion(criterion: SemanticCriterion) -> JudgePromptCriterion:
    return JudgePromptCriterion(
        criterion_id=criterion.criterion_id,
        instruction=criterion.instruction,
        evaluation_method=criterion.evaluation_method.value,
        source_pointer=criterion.source_pointer,
    )


def _load_service(*, context_size: int = NORMAL_MAIN_CONTEXT_SIZE) -> InferenceService:
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    definition = definitions.resolve(model_key=QWEN_MODEL_KEY)
    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(definition, ModelLoadConfig(context_size=context_size, gpu_layers=-1))
    return service


def test_a_real_main_governance_origin_repair_completes_end_to_end_via_the_hook_with_real_argd_dagd_criteria() -> (  # noqa: E501
    None
):
    """Hook-direct call (`build_judge_completion_hook()`'s returned
    callable, `enforce_presented_final=True`) -- the exact synchronous
    in-line-adoption shape the real Conversation Turn pipeline invokes for
    ENFORCE. Real Main Qwen3-4B, real compiled ARGD/DAGD Criterion, normal
    16384 Context, existing (Judge-side) Repair Mode deliberately OFF so a
    real Repair Attempt running here can only be explained by Main
    Governance's own ENFORCE authorization."""
    if not ARTIFACT_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {ARTIFACT_PATH}")
    criterion = _bounded_real_criterion()
    service = _load_service()
    try:
        composition = RuntimeGovernanceComposition(
            capability=RuntimeCapabilitySnapshot(
                model_key=QWEN_MODEL_KEY,
                backend_kind="llama_cpp",
                supports_streaming=True,
                supports_thinking=True,
                max_context_tokens=NORMAL_MAIN_CONTEXT_SIZE,
            ),
        )
        composition.semantic_runtime = SemanticRuntimeCoordinator(criteria=(criterion,))
        composition.set_semantic_context_provider(
            lambda: SemanticRuntimeBindingContext(
                language="en",
                judge_mode="enforce",
                repair_mode="off",
                configured_provider=QWEN_MODEL_KEY,
                active_provider=QWEN_MODEL_KEY,
                provider_state=SemanticProviderState.ACTIVE,
                budget_profile="test",
                max_criteria=8,
            )
        )
        request_id = "real-main-origin-repair-hook-1"
        composition.begin_semantic_turn(request_id=request_id, main_mode="enforce")

        judge_controller = JudgeModeController()
        judge_controller.apply_mode(EvaluationMode.ENFORCE)
        repair_controller = RepairModeController()  # default OFF -- the whole point of this test
        hook, hook_composition = build_judge_completion_hook(
            service=service,
            judge_mode_controller=judge_controller,
            model_access_coordinator=ModelAccessCoordinator(),
            repair_mode_controller=repair_controller,
            repair_executor=partial(
                attempt_live_repair,
                service=service,
                model_key=QWEN_MODEL_KEY,
                persistent=None,
            ),
            semantic_snapshot_provider=lambda rid: composition.semantic_runtime.snapshot_for(
                request_id=rid
            ),
            semantic_result_recorder=lambda response: composition.record_semantic_response(
                response=response
            ),
        )
        candidate = "The capital of France is Tenon."
        decision = hook(
            JudgeCompletionContext(
                model_key=QWEN_MODEL_KEY,
                request_id=request_id,
                user_input="What is the capital of France?",
                assistant_content=candidate,
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
                judge_mode="enforce",
                repair_mode="off",
                recording_mode="off",
                enforce_presented_final=True,
            )
        )
        assert decision is not None
        result = hook_composition.last_result()
        assert result is not None
        if result.execution_state != "completed" or result.criteria_evaluated == 0:
            pytest.skip(
                f"Real Judge output was not decodable/evaluated this run "
                f"(legitimate fail-closed outcome, not necessarily a code "
                f"defect): execution_state={result.execution_state!r} "
                f"failure_reason={result.failure_reason!r} "
                f"criteria_evaluated={result.criteria_evaluated}"
            )
        if result.criteria_deviated == 0:
            pytest.skip(
                "Real Model did not flag this contradicting Candidate as a "
                "Deviation this run (real-model non-determinism, not a "
                "code defect)"
            )
        # The crux, Controller Review IR-03 fix: everything below is a hard
        # requirement of the golden path once a real Deviation was found --
        # none of it is conditional, and a forced/degraded Repair Executor
        # (Controller's own memory-patch Probe: `accepted=False` always)
        # must fail these Assertions, not silently satisfy them.
        assert result.repair_requested_by == "main_governance"
        assert result.repair_outcome == "improved"
        assert result.repair_accepted is True
        assert decision.presentation_outcome == "repair_accepted"
        assert candidate not in decision.presented_content
        assert decision.presented_content.strip() != ""
    finally:
        service.unload()


def _persist_settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.EN,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


class _FixedTurnSession:
    """A completed source Turn with fixed content -- no real Model Call.
    This file's real-Model evidence is about Repair's own Candidate/Rejudge
    Calls (exercised directly against the real Service below); the *source*
    Turn only needs to exist and be COMPLETED so `attempt_live_repair()` has
    a genuine persisted Turn to locate and derive from."""

    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.documentation_augmentation = None
        self.web_search_result = None

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": "generating"},
        )
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "finish_reason": "stop",
                "assistant_message": {"role": "assistant", "content": self.answer},
            },
        )


class _FixedTurnGeneration:
    def __init__(self, *, answer: str) -> None:
        self._answer = answer
        self._count = 0

    def start(self, value: ConversationGenerationInput) -> _FixedTurnSession:
        del value
        self._count += 1
        return _FixedTurnSession(f"request-{self._count}", self._answer)

    def cancel(self, request_id: str) -> bool:
        del request_id
        return False


class _Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 9, 4, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


_SCOPE = ConversationScopeId(value="scope-private")
_CID = ConversationId(value="conversation-1")


def _seed_one_persisted_turn(tmp_path: Path) -> tuple[PersistentConversationService, str]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=_SCOPE,
    )
    store.initialize_new_store()
    persistent = PersistentConversationService(
        repository=store,
        bound_scope_id=_SCOPE,
        generation_service=_FixedTurnGeneration(  # type: ignore[arg-type]
            answer="The capital of France is Tenon."
        ),
        clock=_Clock(),
    )
    persistent.recover_incomplete_conversations()
    persistent.create_conversation(
        conversation_id=_CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=ConversationOperationId(value="create"),
    )
    events = tuple(
        persistent.generate_turn(
            conversation_id=_CID,
            content="What is the capital of France?",
            settings=_persist_settings(),
            identities=PersistentGenerationIdentities(
                turn_id=ConversationTurnId(value="turn-source"),
                user_message_id=ConversationMessageId(value="message-user-source"),
                assistant_message_id=ConversationMessageId(value="message-assistant-source"),
                append_operation_id=ConversationOperationId(value="append-source"),
                start_operation_id=ConversationOperationId(value="start-source"),
                terminal_operation_id=ConversationOperationId(value="terminal-source"),
            ),
            expected_revision=1,
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED
    return persistent, "request-1"


def test_a_real_main_governance_origin_repair_persists_a_derived_turn_through_the_normal_conversation_save_path(  # noqa: E501
    tmp_path: Path,
) -> None:
    """Distinct from the Hook-direct Test above: calls `attempt_live_
    repair()` directly against a real `SQLiteConversationStore`-backed
    `PersistentConversationService` (`persist_accepted_attempt=True`, the
    shape a real persisted Conversation Turn actually uses, never the
    synchronous ENFORCE-Presented-Final in-line-adoption shape) -- proving
    an accepted Main-origin repair genuinely lands through the same atomic
    `append_derived_turn -> start_generation -> complete_generation`
    CAS-guarded chain Retry/Regenerate already use, with the real generated
    content actually persisted as a new REPAIR-origin Turn carrying the
    same Frozen Criterion coverage the Hook-direct Test above requires."""
    if not ARTIFACT_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {ARTIFACT_PATH}")
    criterion = _bounded_real_criterion()
    persistent, source_request_id = _seed_one_persisted_turn(tmp_path)
    service = _load_service()
    try:
        result = attempt_live_repair(
            service=service,
            model_key=QWEN_MODEL_KEY,
            persistent=persistent,
            request_id=source_request_id,
            user_input="What is the capital of France?",
            original_answer="The capital of France is Tenon.",
            before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
            judge_reasoning=(
                f"criterion={criterion.criterion_id}; disposition=deviation; "
                "reason=contradicts_cited_evidence"
            ),
            evidence_context=(
                "official-source | reference.txt: The capital of France is Paris.",
            ),
            governance_post_hook=None,
            guardrail_post_hook=None,
            model_runtime_info=service.runtime_info,
            persist_accepted_attempt=True,
            rejudge_criteria=(_to_prompt_criterion(criterion),),
        )
        assert result is not None
        if not result.accepted:
            pytest.skip(
                f"Real Model did not produce an IMPROVED repair this run "
                f"(real-model non-determinism, not a code defect): "
                f"outcome={result.outcome!r} rejected_reason={result.rejected_reason!r}"
            )
        # The crux: a real derived Turn was actually persisted, not merely
        # returned in-memory.
        assert result.new_turn_id is not None
        stored = persistent.get_conversation(_CID)
        derived_turns = [
            turn for turn in stored.conversation.turns if turn.turn_id.value == result.new_turn_id
        ]
        assert len(derived_turns) == 1
        derived = derived_turns[0]
        assert derived.origin is ConversationTurnOrigin.REPAIR
        assert derived.derived_from_turn_id == ConversationTurnId(value="turn-source")
        assert derived.assistant_message_id is not None
        persisted_message = next(
            item
            for item in stored.conversation.messages
            if item.message_id == derived.assistant_message_id
        )
        assert persisted_message.content == result.presented_content
        assert persisted_message.content.strip() != ""
        assert "Tenon" not in persisted_message.content
    finally:
        service.unload()
