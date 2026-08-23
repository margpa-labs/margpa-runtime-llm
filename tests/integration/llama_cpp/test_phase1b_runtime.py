"""Opt-in Phase 1-B macOS production adapter test using the local Qwen3 artifact."""

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.phase1_application import build_phase1_application
from margpa_runtime_llm.modules.conversation.public import (
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationTerminalState,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResponseLanguage,
    ResponseLanguageSource,
    ResponsePolicyConfig,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ThinkingPresentationConfig,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode
from margpa_runtime_llm.orchestration.response_language import (
    compose_generation_messages,
    resolve_response_policy,
)
from margpa_runtime_llm.orchestration.thinking_presentation import (
    resolve_thinking_presentation_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
PROFILE_PATH = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"
REGISTRY_PATH = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
APPLICATION_PRESENTATION = ThinkingPresentationConfig()


def parameters(
    max_new_tokens: int = 48,
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED,
) -> GenerationParameters:
    return GenerationParameters(
        max_new_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.8,
        top_k=20,
        min_p=0.0,
        presence_penalty=1.5,
        seed=2371,
        thinking_mode=thinking_mode,
    )


def request(
    request_id: str,
    prompt: str,
    max_new_tokens: int = 48,
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED,
) -> GenerationRequest:
    return GenerationRequest(
        request_id=request_id,
        model_key="main.qwen3-4b-q4-k-m",
        messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
        parameters=parameters(max_new_tokens, thinking_mode),
    )


def assert_state(actual: ModelLifecycleState, expected: ModelLifecycleState) -> None:
    assert actual is expected


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 1-B native runtime test requires the macOS Metal deployment",
)
def test_phase1b_production_runtime_load_generate_stream_cancel_and_unload() -> None:
    if not MODEL_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {MODEL_PATH}")

    with build_phase1_application(
        project_root=PROJECT_ROOT,
        profile_path=PROFILE_PATH,
        registry_path=REGISTRY_PATH,
        generation_overrides={"max_new_tokens": 48, "seed": 2371},
    ) as application:
        runtime = application.service.runtime_info
        assert runtime is not None
        assert runtime.backend_version == "0.3.34"
        assert runtime.backend_build_variant == "metal"
        assert runtime.loaded_context_size == 8192
        assert runtime.model_architecture == "qwen3"
        assert runtime.device == "metal"
        assert runtime.device_kind == "gpu"
        assert runtime.acceleration_api == "metal"
        assert runtime.gpu_offload
        assert runtime.gpu_offload_evidence.supported
        assert runtime.gpu_offload_evidence.requested
        assert runtime.gpu_offload_evidence.observed
        assert runtime.gpu_offload_evidence.observation_source == "metal_model_load"
        assert runtime.artifact_digest.value.startswith("f182f1d40606")
        assert runtime.artifact_digest_verified
        assert CapabilityFeature.THINKING_CONTROL in runtime.effective_capabilities.features
        assert CapabilityFeature.GPU_OFFLOAD in runtime.effective_capabilities.features
        assert not runtime.warnings
        assert application.config.application_key == "default"
        assert application.config.application_schema_version == "3"
        assert application.definition.schema_version == "2"
        assert application.config.generation.thinking_mode is ThinkingMode.DISABLED
        assert application.config.response.language is ResponseLanguage.JA
        assert application.config.response.source is ResponseLanguageSource.APPLICATION
        assert application.config.presentation.visibility is ThinkingVisibility.HIDDEN
        assert application.config.presentation.display_label == "推論過程"
        assert application.config.presentation.persistence == "disabled"
        assert (
            application.config.presentation.visibility_source
            is ThinkingPresentationSource.APPLICATION
        )
        assert application.definition.output_protocol.thinking.parser_key == "tagged_thinking_v1"
        assert application.config.profile_resolution_source == "explicit"
        assert application.runtime_observation.host.operating_system_key == "macos"
        assert application.runtime_observation.detected.build_variant_source == "observed"
        assert application.runtime_observation.detected.build_variant_key == "metal"
        assert application.runtime_observation.detected.acceleration_api_key == "metal"
        assert application.runtime_observation.detected.gpu_offload
        assert application.runtime_observation.executed is None

        idempotent = application.service.load(application.definition, application.config.load)
        assert idempotent.load_instance_id == runtime.load_instance_id

        result = application.service.generate(
            GenerationRequest(
                request_id="request-language-ja",
                model_key=application.config.selected_model,
                messages=compose_generation_messages(
                    user_prompt="『成功』とだけ答えてください。",
                    user_system_message=None,
                    policy=application.config.response,
                ),
                parameters=parameters(),
            )
        )
        assert result.content.strip()
        assert "<think>" not in result.content
        assert "</think>" not in result.content
        assert result.finish_reason in {FinishReason.STOP, FinishReason.LENGTH}
        assert result.usage is not None
        assert result.usage.total_tokens > 0
        assert result.timing.total_generation_seconds > 0
        assert result.timing.tokens_per_second is not None

        for language, prompt in (
            (ResponseLanguage.EN, "Reply with the single word success."),
            (ResponseLanguage.AUTO, "OKとだけ答えてください。"),
        ):
            policy = resolve_response_policy(
                application_policy=ResponsePolicyConfig(language=ResponseLanguage.JA),
                environment={},
                explicit_language=language,
            )
            language_result = application.service.generate(
                GenerationRequest(
                    request_id=f"request-language-{language.value}",
                    model_key=application.config.selected_model,
                    messages=compose_generation_messages(
                        user_prompt=prompt,
                        user_system_message=None,
                        policy=policy,
                    ),
                    parameters=parameters(24),
                )
            )
            assert language_result.content.strip()

        thinking_result = application.service.generate(
            request(
                "request-thinking",
                "1+1を考えてください。",
                128,
                ThinkingMode.ENABLED,
            )
        )
        assert thinking_result.content.strip()
        hidden_thinking = application.presentation_service.present_text(
            thinking_result.content,
            application.config.presentation,
        )
        visible_policy = resolve_thinking_presentation_policy(
            application_policy=APPLICATION_PRESENTATION,
            environment={},
            explicit_visibility=ThinkingVisibility.VISIBLE,
            explicit_display_label=None,
        )
        visible_thinking = application.presentation_service.present_text(
            thinking_result.content,
            visible_policy,
        )
        custom_policy = resolve_thinking_presentation_policy(
            application_policy=APPLICATION_PRESENTATION,
            environment={},
            explicit_visibility=ThinkingVisibility.VISIBLE,
            explicit_display_label="思考過程",
        )
        custom_thinking = application.presentation_service.present_text(
            thinking_result.content,
            custom_policy,
        )
        assert "<think>" not in hidden_thinking.display_content
        assert "</think>" not in hidden_thinking.display_content
        assert "<think>" not in visible_thinking.display_content
        assert "</think>" not in visible_thinking.display_content
        if visible_thinking.normalized.reasoning_content is not None:
            assert visible_thinking.display_content.startswith("<推論過程>")
            assert "</推論過程>" in visible_thinking.display_content
            assert custom_thinking.display_content.startswith("<思考過程>")
            assert "</思考過程>" in custom_thinking.display_content

        active_stream = application.service.stream(
            request("request-stream", "1から順に整数を列挙してください。", 64)
        )
        assert_state(application.service.state, ModelLifecycleState.GENERATING)
        with pytest.raises(InferenceError) as busy:
            application.service.generate(request("request-busy", "OKと答えてください。", 16))
        assert busy.value.code is InferenceErrorCode.MODEL_BUSY

        iterator = iter(active_stream)
        first_chunk = next(iterator)
        assert first_chunk.text_delta
        active_stream.cancel()
        active_stream.cancel()
        assert active_stream.terminal_state is GenerationTerminalState.CANCELLED
        assert_state(application.service.state, ModelLifecycleState.LOADED)

        post_cancel = application.service.generate(
            request("request-post-cancel", "日本語でOKとだけ答えてください。", 16)
        )
        assert post_cancel.content.strip()
        assert post_cancel.finish_reason in {FinishReason.STOP, FinishReason.LENGTH}

        conversation = ConversationGenerationService(
            inference=application.service,
            presentation=application.presentation_service,
            model_key=application.config.selected_model,
            generation_defaults=application.config.generation.model_copy(update={"seed": 2371}),
            response_language_default=application.config.response.language,
            presentation_default=application.config.presentation,
            summarization=application.config.summarization,
        )
        summary_events = list(
            conversation.start(
                ConversationGenerationInput(
                    messages=(
                        ConversationMessage(
                            role=ConversationRole.USER,
                            content=(
                                "Nazuna ResearchはLLM Governanceを研究します。"
                                "短く説明してください。"
                            ),
                        ),
                    ),
                    settings=ConversationSettings(
                        response_language=ResponseLanguage.JA,
                        max_new_tokens=64,
                        thinking_visibility=ThinkingVisibility.HIDDEN,
                        summary_mode=SummaryMode.POST_GENERATION,
                    ),
                )
            ).events()
        )
        assert [event.event for event in summary_events].count(ConversationEventType.START) == 1
        # P6-CODEX-039 (Fifth Rework): this Turn goes through
        # `_events_with_summary()` (SummaryMode.POST_GENERATION), which
        # emits three STATUS phase markers — "preparing" (events() entry),
        # "guarding" (pre-check phase), and "summarizing_answer" (after the
        # original answer completes, before the summary generation call) —
        # not the single "preparing"-only marker an earlier STATUS
        # vocabulary had. Asserting the exact sequence (not just a count)
        # keeps this test meaningful rather than a magic number.
        status_states = [
            event.data.get("state")
            for event in summary_events
            if event.event is ConversationEventType.STATUS
        ]
        assert status_states == ["preparing", "guarding", "summarizing_answer"]
        assert summary_events[-1].event is ConversationEventType.COMPLETED
        transformation = summary_events[-1].data["transformation"]
        assistant_message = summary_events[-1].data["assistant_message"]
        assert isinstance(transformation, dict)
        assert isinstance(assistant_message, dict)
        assert transformation["summary_applied"] is True
        assert transformation["fallback_used"] is False
        assert assistant_message["content"]
        assert "original_assistant_message" not in summary_events[-1].data
        assert "summary_assistant_message" not in summary_events[-1].data

        completed_stream = application.service.stream(
            request("request-complete-stream", "日本語で完了とだけ答えてください。", 24)
        )
        chunks = list(completed_stream)
        assert chunks[-1].is_final
        assert chunks[-1].finish_reason in {FinishReason.STOP, FinishReason.LENGTH}
        assert [chunk.sequence for chunk in chunks] == list(range(len(chunks)))
        assert completed_stream.terminal_state is GenerationTerminalState.COMPLETED
        assert completed_stream.timing is not None

    assert_state(application.service.state, ModelLifecycleState.UNLOADED)
    application.close()
    assert_state(application.service.state, ModelLifecycleState.UNLOADED)
