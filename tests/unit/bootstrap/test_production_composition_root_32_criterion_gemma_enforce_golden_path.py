"""R3-WU-05 (Controller Review IR-R2-04): the real 32-Criterion Production
Web Golden Path, driven through `build_phase1_web_runtime()` itself -- the
genuine Production Composition Root, never a hand-built lookalike.

IR-R2-04 confirmed two distinct gaps in R2's own Fixture/real-hardware
Tests: (1) both used a bounded 4/1-Criterion set, never the real ARGD/DAGD
`max_criteria=32` selection; (2) both hand-assembled `ConversationGeneration
Service`/`RuntimeGovernanceComposition` directly, bypassing `build_phase1_
web_runtime()` entirely -- so R2-WU-01's own `semantic_turn_begin_hook`
wiring was never actually exercised end to end.

This module closes both gaps:

- `runtime_governance_definitions_root` points at the real project `
  definitions/` ARGD/DAGD bundle (the same real 109-Criterion corpus every
  real-hardware Test already compiles) -- `max_criteria` stays at its own
  Production default (32), so the 32 Criteria a real Turn selects here are
  the genuine rotation-based selection, never a hand-picked list.
- `build_phase1_web_runtime()` itself is called, with `build_phase1_
  application()` monkeypatched to hand back a Fixture Main `service`/
  `config` (no real Main Model Load) and `dedicated_role_adapters.
  LlamaCppModelAdapter` monkeypatched to a Fixture Model Port (no real
  Gemma Model Load) -- every other piece of the real Composition Root
  (Provider Selection/Lifecycle, Judge/Repair/Recording Mode Controllers,
  Main Governance Composition, the real `SemanticRuntimeCoordinator`/
  `semantic_turn_begin_hook` wiring, real `PersistentConversationService`,
  real Recording Writers) runs unmodified, exactly as Production wires it.
  `build_governance_observer` is monkeypatched only to redirect its own
  Evidence-write location to `tmp_path` (never its logic) -- Governance
  Evidence would otherwise write into the real repository's shared
  `runtime_data/audit_evidence/`, a side effect this Test must not leave
  behind on every ordinary suite run.

The Fixture Gemma Model Port's own `generate()` is criterion-aware: it
inspects the real rendered prompt text for which of the 32 real (pre-
computed, never invented) Criterion ids it names, and answers exactly
those -- so this Test's own Fixture responses are always in step with
whatever the real Composition Root's own Batch planner actually did,
without this Test needing to reimplement that planner's own token-budget
logic itself."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace, TracebackType
from typing import Any

import pytest

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.adapters.runtime_governance.semantic_criterion_adapter import (
    compile_argd_dagd_semantic_criteria,
)
from margpa_runtime_llm.adapters.runtime_model_control import dedicated_role_adapters
from margpa_runtime_llm.bootstrap import web_application as web_application_module
from margpa_runtime_llm.bootstrap.audit_evidence import build_governance_observer
from margpa_runtime_llm.bootstrap.runtime_governance import (
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.modules.conversation.adapters import LocalConversationPersistenceSettings
from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    scope_directory_key,
)
from margpa_runtime_llm.modules.conversation.application import PersistentGenerationIdentities
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEventType,
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
    ConversationTurnState,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.runtime_model_control.application import GEMMA_E2B_JUDGE
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_MAIN_MODEL_KEY = "main.qwen3-4b"
_WRONG_ANSWER = "The capital of France is Tenon."
_CORRECTED_ANSWER = "The capital of France is Paris."
_SCOPE = ConversationScopeId(value="scope-r3-wu05-golden-path")


def _select_real_32_criteria() -> tuple[str, ...]:
    """The exact 32 real Criterion ids a fresh `SemanticRuntimeCoordinator`
    (rotation_offset=0, the state of a just-built Composition Root's first
    Turn) selects from the real ARGD/DAGD bundle, at `max_criteria=32` (the
    real Production default) -- computed once, independently, purely as a
    pre-check this Test's own Fixture responses can key off of. `capability`
    /`authority` do not affect which Descriptors/Criteria are extracted at
    all (only the separate Source-Plan-compilation digest), so this
    genuinely is the same 32 ids the real Composition Root's own (separate)
    Coordinator instance will select."""
    loaded = load_reference_descriptors(
        definitions_root=_PROJECT_ROOT / "definitions",
        capability=RuntimeCapabilitySnapshot(
            model_key=_MAIN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=False,
            max_context_tokens=8192,
        ),
        authority=default_authority(),
    )
    assert loaded.state == "loaded"
    compiled = compile_argd_dagd_semantic_criteria(loaded.descriptors)
    assert len(compiled.criteria) == 109
    probe = freeze_semantic_turn(
        request_id="probe-select-32",
        generation=1,
        criteria=compiled.criteria,
        language="en",
        main_mode="enforce",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=GEMMA_E2B_JUDGE,
        active_provider=GEMMA_E2B_JUDGE,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=32,
    )
    assert len(probe.snapshot.criteria) == 32
    return tuple(item.criterion_id for item in probe.snapshot.criteria)


def _matched_criterion_ids(*, prompt: str, known_ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cid for cid in known_ids if cid in prompt)


def _approx_token_count(messages: tuple[object, ...]) -> int:
    """A genuine (if approximate) chars-per-token estimate -- never a raw
    character count, which would make this Fixture's own crude counting
    the actual cause of a real Repair/Rejudge Budget rejection for a
    32-Criterion combined Prompt, rather than a real Token/Context
    shortfall this Test is not about."""
    total_chars = sum(len(str(getattr(message, "content", ""))) for message in messages)
    return max(1, total_chars // 4)


def _fake_judge_response(*, matched_ids: tuple[str, ...], deviation_id: str | None) -> str:
    return json.dumps(
        {
            "recommendation": "needs_repair" if deviation_id in matched_ids else "accept",
            "confidence": 0.9,
            "reasoning": "fixture",
            "criterion_results": [
                {
                    "criterion_id": cid,
                    "disposition": "deviation" if cid == deviation_id else "pass",
                    "confidence": 0.9,
                    "reason_code": ("unsupported_claim" if cid == deviation_id else None),
                    "evidence_refs": (["/rules/evidence/1"] if cid == deviation_id else []),
                }
                for cid in matched_ids
            ],
        }
    )


class _FakeStream:
    def __init__(self, *, text_deltas: tuple[str, ...]) -> None:
        self.text_deltas = text_deltas
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "fake-main-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        for sequence, text in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="fake-main-request", sequence=sequence, text_delta=text, is_final=False
            )
        yield GenerationChunk(
            request_id="fake-main-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> _FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


_MAIN_RUNTIME_INFO = ModelRuntimeInfo(
    load_instance_id="fixture-main-load-1",
    model_key=_MAIN_MODEL_KEY,
    backend_key="fixture_main_backend",
    backend_version="0.0.0-fixture",
    model_architecture="qwen3",
    format="gguf",
    quantization="q4_k_m",
    artifact_size_bytes=1024,
    artifact_digest=ModelDigest(value="e" * 128),
    definition_file_sha512="a" * 128,
    loaded_context_size=16384,
    effective_capabilities=ModelCapabilities(
        features=MODEL_REQUIRED_CAPABILITIES,
        native_context_limit=16384,
        loaded_context_size=16384,
        supported_message_roles=frozenset(
            {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
        ),
    ),
    chat_template_source="fixture",
    chat_template_digest=ModelDigest(value="f" * 128),
    device="cpu",
    device_kind="cpu",
    acceleration_api="none",
    gpu_offload=False,
    gpu_offload_evidence=GpuOffloadEvidence(
        supported=False, requested=False, observed=False, observation_source="not_requested"
    ),
)


class _FakeMainService:
    """Stands in for `Phase1Application.service` -- `.stream()` produces
    the initial (deliberately wrong) Candidate; `.generate()` produces the
    Repair Candidate `attempt_live_repair()` itself requests via Main's own
    `service` parameter (never `rejudge_service`, which is Gemma's own --
    see `judge_live_integration.py`'s dispatch router)."""

    def __init__(self) -> None:
        self.runtime_info = _MAIN_RUNTIME_INFO
        self.stream_requests: list[GenerationRequest] = []
        self.generate_requests: list[GenerationRequest] = []

    def count_text_tokens(self, text: str) -> int:
        return len(text.split())

    def count_chat_prompt_tokens(self, messages: tuple[object, ...], thinking_mode: object) -> int:
        del thinking_mode
        return _approx_token_count(messages)

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.stream_requests.append(request)
        return _FakeStream(text_deltas=(_WRONG_ANSWER,))

    def generate(
        self, request: GenerationRequest, *, cancellation: object | None = None
    ) -> GenerationResult:
        del cancellation
        self.generate_requests.append(request)
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=_CORRECTED_ANSWER,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=8, total_tokens=18),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_MAIN_RUNTIME_INFO.reference(),
        )


def _fake_gemma_port_class(
    *, known_ids: tuple[str, ...], deviation_id: str
) -> tuple[type, list[Any]]:
    """Monkeypatched in place of `dedicated_role_adapters.LlamaCppModelAdapter`
    -- never touches a real file or the `llama_cpp` library. Mirrors
    `test_dedicated_role_adapters_production_wiring.py`'s own proven
    `_fake_model_port_class` shape (`LlamaCppRuntimeModelBackend` itself is
    never patched -- its `probe_capability()`/`load()`/`unload()` only ever
    delegate to whichever Adapter it was constructed with)."""

    created: list[Any] = []

    class _FakeGemmaPort:
        def __init__(self, *, model_root: Path) -> None:
            self.model_root = model_root
            self._state = ModelLifecycleState.UNLOADED
            self._runtime_info: ModelRuntimeInfo | None = None
            self.generate_calls: list[GenerationRequest] = []
            self.unload_calls = 0
            created.append(self)

        @property
        def state(self) -> ModelLifecycleState:
            return self._state

        @property
        def runtime_info(self) -> ModelRuntimeInfo | None:
            return self._runtime_info

        def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
            capabilities = ModelCapabilities(
                # Gemma Judge-only Constrained Decoding Rework (WU-02): the
                # real Backend now reports this Capability for every loaded
                # Role uniformly (see `LlamaCppModelAdapter._build_runtime_
                # info()`'s own real `hasattr` probe) -- this Fixture Gemma
                # Port mirrors that so its own `structured_output`-carrying
                # Request is not spuriously rejected.
                features=MODEL_REQUIRED_CAPABILITIES
                | {CapabilityFeature.JSON_SCHEMA, CapabilityFeature.GRAMMAR},
                native_context_limit=definition.model.native_context_limit,
                loaded_context_size=config.context_size,
                supported_message_roles=frozenset(
                    {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
                ),
            )
            self._runtime_info = ModelRuntimeInfo(
                load_instance_id="fixture-gemma-load-1",
                model_key=definition.model_key,
                backend_key="fixture_gemma_backend",
                backend_version="0.0.0-fixture",
                model_architecture=definition.model.architecture,
                format=definition.artifact.format,
                quantization=definition.artifact.quantization,
                artifact_size_bytes=definition.artifact.size_bytes,
                artifact_digest=ModelDigest(value=definition.artifact.sha512),
                definition_file_sha512=definition.definition_file_sha512,
                loaded_context_size=config.context_size,
                effective_capabilities=capabilities,
                chat_template_source="fixture",
                chat_template_digest=ModelDigest(value="b" * 128),
                device="cpu",
                device_kind="cpu",
                acceleration_api="none",
                gpu_offload=False,
                gpu_offload_evidence=GpuOffloadEvidence(
                    supported=False,
                    requested=False,
                    observed=False,
                    observation_source="not_requested",
                ),
            )
            self._state = ModelLifecycleState.LOADED
            return self._runtime_info

        def unload(self) -> None:
            self.unload_calls += 1
            self._state = ModelLifecycleState.UNLOADED
            self._runtime_info = None

        def capabilities(self) -> ModelCapabilities:
            assert self._runtime_info is not None
            return self._runtime_info.effective_capabilities

        def count_chat_prompt_tokens(
            self, messages: tuple[object, ...], thinking_mode: object
        ) -> int:
            del thinking_mode
            return _approx_token_count(messages)

        def generate(
            self, request: GenerationRequest, *, cancellation: object | None = None
        ) -> GenerationResult:
            del cancellation
            self.generate_calls.append(request)
            assert self._runtime_info is not None
            prompt = str(request.messages[0].content)
            matched = _matched_criterion_ids(prompt=prompt, known_ids=known_ids)
            assert matched, (
                "the Fixture Gemma Port received a real Judge/Rejudge prompt "
                "that named none of the 32 pre-computed real Criterion ids"
            )
            # The Rejudge Call re-scores the Repaired Candidate -- the whole
            # point of Repair succeeding -- so it must genuinely report the
            # Deviation as fixed, never repeat the identical Deviation the
            # initial dispatch found (which would make Repair correctly,
            # honestly, `no_change`/not-accepted rather than a Fixture bug).
            is_rejudge = request.request_id.endswith(":rejudge")
            content = _fake_judge_response(
                matched_ids=matched,
                deviation_id=None if is_rejudge else deviation_id,
            )
            completion_tokens = 60 * len(matched)
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content=content,
                finish_reason=FinishReason.STOP,
                usage=TokenUsage(
                    prompt_tokens=200,
                    completion_tokens=completion_tokens,
                    total_tokens=200 + completion_tokens,
                ),
                timing=GenerationTiming(total_generation_seconds=0.01),
                runtime_info=self._runtime_info.reference(),
            )

    return _FakeGemmaPort, created


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="thinking",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.EN,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def _fake_config() -> SimpleNamespace:
    return SimpleNamespace(
        selected_model=_MAIN_MODEL_KEY,
        profile_key="test.fixture",
        generation=GenerationParameters(max_new_tokens=128, thinking_mode=ThinkingMode.DISABLED),
        response=SimpleNamespace(language=ResponseLanguage.EN),
        presentation=_presentation_policy(),
        summarization=SummarizationConfig(),
        model_root=_PROJECT_ROOT / "models",
        # R4-WU-05 (Controller Review IR-R3-05): the real deployed Gemma
        # context_size (`config/profiles/local_macos_arm64.toml`'s own
        # `[dedicated_role_load_overrides]`), never an inflated Fixture-only
        # value -- a 32768 Context here would let this Test pass without
        # actually proving the real, unbatched Rejudge Call (naming all 32
        # real Criteria at once) genuinely fits the real deployment's own
        # Context bound. `count_chat_prompt_tokens()` below uses a genuine
        # (if approximate) chars-per-token estimate, never an inflated one
        # that would make this Fixture's own crude counting the actual
        # cause of a Repair Budget rejection independent of the real
        # Context size.
        dedicated_role_load=ModelLoadConfig(context_size=8192),
    )


def test_production_composition_root_32_criterion_gemma_enforce_golden_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R3-WU-05: the real 32-Criterion Golden Path through the real
    `build_phase1_web_runtime()` Composition Root --

        Main Governance: ENFORCE
        Judge: Gemma (dedicated) ENFORCE
        Repair (Judge-side toggle): OFF -- Main Governance authorizes it
        Guard: OFF (not wired)
        Recording: FULL
        Criteria: real ARGD/DAGD rotation-selected 32

    Hard Asserts (never `pytest.skip` for anything but a genuinely Missing
    Artifact -- there is none here, this Test never touches real hardware):
    `repair_requested_by == "main_governance"`, Repair accepted, the
    identical 32-Criterion set Rejudged by the same Gemma identity,
    Presented Final content is the corrected answer, same-Turn Persistence,
    and a real on-disk Judge Evidence file naming Gemma's own identity."""
    known_ids = _select_real_32_criteria()
    deviation_id = known_ids[0]

    main_service = _FakeMainService()
    application = SimpleNamespace(
        service=main_service,
        config=_fake_config(),
        presentation_service=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        close=lambda: None,
    )
    monkeypatch.setattr(
        web_application_module, "build_phase1_application", lambda **_kwargs: application
    )

    fake_gemma_port, created_gemma_ports = _fake_gemma_port_class(
        known_ids=known_ids, deviation_id=deviation_id
    )
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_gemma_port)

    # Governance Evidence writes are redirected to `tmp_path` -- the real
    # `EvidenceGovernanceObserver`/`LocalJsonlEvidenceStore` logic runs
    # unmodified, only its on-disk anchor changes, so this Test never
    # leaves real Evidence files behind in the shared repository `
    # runtime_data/audit_evidence/` on every ordinary suite run.
    def _tmp_governance_observer(*, project_root: Path, mode_provider: object) -> object:
        del project_root
        return build_governance_observer(project_root=tmp_path, mode_provider=mode_provider)  # type: ignore[arg-type]

    monkeypatch.setattr(
        web_application_module, "build_governance_observer", _tmp_governance_observer
    )

    runtime_data_root = tmp_path / "runtime-data"
    persistence_settings = LocalConversationPersistenceSettings(
        enabled=True,
        runtime_data_root=runtime_data_root,
        scope_id=_SCOPE,
    )

    runtime = build_phase1_web_runtime(
        project_root=_PROJECT_ROOT,
        profile_path=None,
        registry_path=_PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml",
        runtime_governance_enabled=True,
        runtime_governance_definitions_root=_PROJECT_ROOT / "definitions",
        feature_modes_enabled=True,
        dedicated_model_authority_granted=True,
        conversation_persistence_settings=persistence_settings,
    )
    try:
        assert runtime.judge_mode_control is not None
        assert runtime.repair_mode_control is not None
        assert runtime.recording_mode_control is not None
        assert runtime.role_provider_lifecycle is not None
        assert runtime.runtime_governance_composition is not None
        assert runtime.persistent_conversation is not None

        runtime.recording_mode_control.apply_mode(RecordingMode.FULL)
        # Judge-side Repair Mode toggle stays OFF throughout -- the
        # Handoff's own "Repair: OFF" arm. Only Main Governance's own
        # ENFORCE decision may authorize the Repair below.
        runtime.judge_mode_control.apply_mode(EvaluationMode.ENFORCE)
        activated = runtime.role_provider_lifecycle.activate(role=ModelRole.JUDGE)
        judge_selection = next(
            item for item in activated.selections if item.role is ModelRole.JUDGE
        )
        assert judge_selection.active_provider == GEMMA_E2B_JUDGE
        mode_snapshot = runtime.runtime_governance_composition.mode_controller.apply_mode(
            GovernanceMode.ENFORCE
        )
        assert mode_snapshot.current_mode is GovernanceMode.ENFORCE

        persistent = runtime.persistent_conversation
        conversation_id = ConversationId(value="conversation-r3-wu05-1")
        persistent.create_conversation(
            conversation_id=conversation_id,
            session_id=ConversationSessionId(value="session-r3-wu05-1"),
            operation_id=ConversationOperationId(value="create-r3-wu05-1"),
        )
        identities = PersistentGenerationIdentities(
            turn_id=ConversationTurnId(value="turn-r3-wu05-1"),
            user_message_id=ConversationMessageId(value="message-user-r3-wu05-1"),
            assistant_message_id=ConversationMessageId(value="message-assistant-r3-wu05-1"),
            append_operation_id=ConversationOperationId(value="append-r3-wu05-1"),
            start_operation_id=ConversationOperationId(value="start-r3-wu05-1"),
            terminal_operation_id=ConversationOperationId(value="terminal-r3-wu05-1"),
        )

        events = list(
            persistent.generate_turn(
                conversation_id=conversation_id,
                content="What is the capital of France?",
                settings=_settings(),
                identities=identities,
                expected_revision=1,
            )
        )
        assert events[-1].event is ConversationEventType.COMPLETED

        assert runtime.judge_governance_composition is not None
        result = runtime.judge_governance_composition.last_result()
        assert result is not None
        assert result.execution_state == "completed"
        assert result.failure_reason is None
        assert result.repair_requested_by == "main_governance"
        assert result.repair_accepted is True
        assert result.executed_provider == GEMMA_E2B_JUDGE
        assert result.criteria_selected == 32
        assert result.criteria_deviated >= 1
        # R5-WU-02 (Controller Review): the Golden Path Oracle's own Repair
        # / Presentation / same-32-Criterion / Count-preservation Hard
        # Asserts -- never merely inferred from `execution_state ==
        # "completed"` alone.
        assert result.repair_outcome == "improved"
        assert result.presentation_outcome == "repair_accepted"
        assert result.candidate_withheld is True
        assert result.repair_rejudge_provider == GEMMA_E2B_JUDGE
        assert (
            result.criteria_evaluated + result.criteria_unknown + result.criteria_not_applicable
            == 32
        )
        assert (
            result.criteria_evaluated
            + result.criteria_unknown
            + result.criteria_not_applicable
            + result.criteria_deferred
            == 109
        )

        assert len(created_gemma_ports) == 1
        gemma_port = created_gemma_ports[0]
        # The initial dispatch (`SeleneSemanticEvaluator.evaluate()`) batches
        # the 32 real Criteria across several calls, each request_id shaped
        # `f"{turn_request_id}:{provider_label}:{batch_index}"` -- never a
        # single `:judge`-suffixed call. Only the separate Repair/Rejudge
        # mechanism (`repair_live_integration.py`) uses the `:repair`/
        # `:rejudge` suffixes, and only Rejudge combines all 32 Criteria
        # into one unbatched call.
        initial_calls = [
            call
            for call in gemma_port.generate_calls
            if not call.request_id.endswith(":repair") and not call.request_id.endswith(":rejudge")
        ]
        repair_calls = [
            call for call in gemma_port.generate_calls if call.request_id.endswith(":repair")
        ]
        rejudge_calls = [
            call for call in gemma_port.generate_calls if call.request_id.endswith(":rejudge")
        ]
        assert initial_calls, "expected at least one initial (batched) Judge dispatch call"
        initial_matched: set[str] = set()
        for call in initial_calls:
            initial_matched.update(
                _matched_criterion_ids(prompt=str(call.messages[0].content), known_ids=known_ids)
            )
        assert len(rejudge_calls) == 1
        rejudge_prompt = str(rejudge_calls[0].messages[0].content)
        rejudge_matched = _matched_criterion_ids(prompt=rejudge_prompt, known_ids=known_ids)
        # R5-WU-02: the initial dispatch (across all its batches) and the
        # Repair Rejudge must together name the IDENTICAL 32-Criterion id
        # set -- never a narrower or drifted one, and never merely each
        # independently equal to `known_ids` without being cross-checked
        # against each other.
        assert initial_matched == set(known_ids)
        assert set(rejudge_matched) == set(known_ids)
        assert initial_matched == set(rejudge_matched), (
            "the Repair Rejudge must re-score the identical 32-Criterion set "
            "the initial dispatch evaluated, never a narrower or drifted one"
        )
        # Gemma Judge-only Constrained Decoding Rework (WU-03/WU-06): both
        # the initial Batch Calls and the Repair Rejudge Call carry a real
        # `structured_output` constraint -- the identical Schema Factory
        # (`build_gemma_judge_structured_output_constraint`) building each,
        # so the Rejudge's own Array size matches the FULL 32-Criterion set
        # (a single unbatched Call) while each initial Batch's own Array
        # size matches that Batch's own smaller Criterion count.
        for call in initial_calls:
            assert call.parameters.structured_output is not None
        rejudge_constraint = rejudge_calls[0].parameters.structured_output
        assert rejudge_constraint is not None
        rejudge_results_schema = rejudge_constraint.json_schema["properties"]["criterion_results"]
        assert rejudge_results_schema["minItems"] == 32
        assert rejudge_results_schema["maxItems"] == 32
        # Codex Controller Review (2026-09-06 12:44, IR-FC-01) fix, proven
        # here through the REAL Composition Root (the real `Production
        # RoleAdapterFactory` Gemma branch, real `GEMMA_JUDGE_DETERMINISTIC_
        # SAMPLING`, real `SeleneSemanticEvaluator.sampling_overrides`):
        # the Rejudge Call must carry the identical frozen Sampling
        # contract the initial Batch Calls already used, never the library
        # Defaults it silently fell back to before this fix.
        rejudge_parameters = rejudge_calls[0].parameters
        assert rejudge_parameters.temperature == 0.0
        assert rejudge_parameters.top_p == 1.0
        assert rejudge_parameters.top_k == 1
        assert rejudge_parameters.seed == 0
        for call in initial_calls:
            assert call.parameters.temperature == 0.0
            assert call.parameters.seed == 0
        assert repair_calls == [], (
            "the Repair Candidate itself is Main's own generation "
            "(`_FakeMainService.generate()`), never Gemma's own Port"
        )
        assert len(main_service.generate_requests) == 1
        # WU-06 isolation item 4: the Repair Candidate generation itself
        # (Main's own `generate()`, never Gemma's) carries NO `structured_
        # output` constraint at all -- Constrained Decoding never leaks
        # into Repair Candidate generation.
        assert main_service.generate_requests[0].parameters.structured_output is None
        # WU-06 isolation item 3: Main's initial (deliberately wrong)
        # streamed Candidate answer also carries no constraint.
        assert main_service.stream_requests[0].parameters.structured_output is None

        stored = persistent.get_conversation(conversation_id)
        assert len(stored.conversation.turns) == 1
        turn = stored.conversation.turns[0]
        assert turn.origin is ConversationTurnOrigin.NORMAL
        assert turn.state is ConversationTurnState.COMPLETED
        assert turn.assistant_message_id is not None
        persisted_message = next(
            item
            for item in stored.conversation.messages
            if item.message_id == turn.assistant_message_id
        )
        assert persisted_message.content == _CORRECTED_ANSWER
        assert "Tenon" not in persisted_message.content
    finally:
        runtime.close_callback()

    evidence_root = runtime_data_root / "persistent" / scope_directory_key(_SCOPE) / "evidence"
    evidence_files = [path for path in evidence_root.rglob("*.json") if path.is_file()]
    assert len(evidence_files) == 1, (
        f"expected exactly one real Judge Evidence file under {evidence_root}, "
        f"found {[str(p) for p in evidence_files]}"
    )
    judge_evidence = json.loads(evidence_files[0].read_text(encoding="utf-8"))["metadata_fields"]
    assert judge_evidence["model_identity"] == GEMMA_E2B_JUDGE
    assert judge_evidence["evaluated_model_identity"] == _MAIN_MODEL_KEY
    assert judge_evidence["repair_accepted"] is True
    assert (
        judge_evidence["artifact_digest_sha512"]
        == created_gemma_ports[0].runtime_info.artifact_digest.value
    )
    assert judge_evidence["backend_key"] == "fixture_gemma_backend"
    # Gemma Judge-only Constrained Decoding Rework (WU-05): the initial
    # dedicated Judge dispatch genuinely batches 32 Criteria across 4 real
    # Calls (`max_criteria_per_call=8`) -- `call_count` must reflect that
    # real count, never the pre-Rework hardcoded `1`. `seed`/`seed_pinned`
    # must reflect Gemma's own real deterministic Sampling (`seed=0`),
    # never `unpinned`. `token_usage` must be the real accumulated
    # completion tokens across those Batches, never `0`. `config_digest_
    # sha512` must be a real, Batch/Sampling-contract-derived value, never
    # the generic single-call constant. `batch_evidence_json` must be
    # present and describe all 4 real Batches.
    assert judge_evidence["call_count"] == 4
    assert judge_evidence["seed_pinned"] is True
    assert judge_evidence["seed"] == 0
    assert judge_evidence["token_usage"] > 0
    assert judge_evidence["config_digest_sha512"] != "unavailable"
    # Gemma Final Contract Micro Rework (IR-FC-04): the IR-FC-04 fix only
    # changes the Model-Call-0 shape (zero real Batches) -- a genuine
    # >=1-real-Batch Run like this one must keep producing its real,
    # Batch-content-derived aggregate `prompt_digest_sha512` (a 128-hex-
    # digit SHA-512), never the Model-Call-0 `"unavailable"` sentinel.
    assert judge_evidence["prompt_digest_sha512"] != "unavailable"
    assert len(str(judge_evidence["prompt_digest_sha512"])) == 128
    batch_entries = json.loads(str(judge_evidence["batch_evidence_json"]))
    assert len(batch_entries) == 4
    assert [entry["batch_index"] for entry in batch_entries] == [1, 2, 3, 4]
    assert all(entry["strict_decode_state"] == "decoded" for entry in batch_entries)
    assert all(entry["seed"] == 0 for entry in batch_entries)
    assert all(entry["structured_output_enabled"] is True for entry in batch_entries)
    assert all(
        entry["structured_output_schema_digest_sha512"] is not None for entry in batch_entries
    )
