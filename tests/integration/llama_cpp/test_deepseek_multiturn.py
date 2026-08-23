"""Opt-in Phase 6 (P6-CODEX-037, Fifth Rework) real-model multi-turn chat
template compatibility test for the DeepSeek-R1-0528-Qwen3-8B GGUF artifact,
including cross-model continuation with the local Qwen3-4B artifact."""

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.phase1_application import (
    Phase1Application,
    build_phase1_application,
)
from margpa_runtime_llm.modules.conversation.public import (
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROFILE_PATH = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"
QWEN_MODEL_PATH = PROJECT_ROOT / "models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
QWEN_REGISTRY_PATH = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
DEEPSEEK_MODEL_PATH = (
    PROJECT_ROOT
    / "models/main/deepseek-r1-0528-qwen3-8b/gguf/DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf"
)
DEEPSEEK_REGISTRY_PATH = PROJECT_ROOT / "config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml"

_LEAKED_SPECIAL_TOKEN_MARKERS = (
    "<｜end▁of▁sentence｜>",  # noqa: RUF001
    "<｜end of sentence｜>",  # noqa: RUF001
    "<｜User｜>",  # noqa: RUF001
    "<｜Assistant｜>",  # noqa: RUF001
)


def _settings(
    *,
    max_new_tokens: int = 48,
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED,
) -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=max_new_tokens,
        thinking_mode=thinking_mode,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
    )


def _build_service(application: Phase1Application) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=application.service,
        presentation=application.presentation_service,
        model_key=application.config.selected_model,
        generation_defaults=application.config.generation.model_copy(update={"seed": 2371}),
        response_language_default=application.config.response.language,
        presentation_default=application.config.presentation,
        summarization=application.config.summarization,
    )


def _run_turn(
    service: ConversationGenerationService,
    messages: tuple[ConversationMessage, ...],
    *,
    max_new_tokens: int = 48,
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED,
) -> str:
    events = list(
        service.start(
            ConversationGenerationInput(
                messages=messages,
                settings=_settings(max_new_tokens=max_new_tokens, thinking_mode=thinking_mode),
            )
        ).events()
    )
    completed = [event for event in events if event.event is ConversationEventType.COMPLETED]
    assert len(completed) == 1, f"expected exactly one COMPLETED event, got: {events}"
    assistant_message = completed[0].data["assistant_message"]
    assert isinstance(assistant_message, dict)
    content = assistant_message["content"]
    assert isinstance(content, str)
    assert content.strip()
    for marker in _LEAKED_SPECIAL_TOKEN_MARKERS:
        assert marker not in content, f"visible special-token leakage detected: {content!r}"
    return content


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 1-B native runtime test requires the macOS Metal deployment",
)
def test_deepseek_multiturn_chat_template_compatibility() -> None:
    """P6-CODEX-037 (Fifth Rework): the DeepSeek GGUF's embedded chat
    template hardcodes its assistant-turn-end marker as a literal '▁'
    (U+2581) separated string that does not match the tokenizer's own
    canonical EOS byte sequence (see chat_template.py's
    `_build_prompt_normalization`). Left unfixed, every past-assistant-turn
    boundary in a multi-turn prompt degrades into ordinary sub-word tokens,
    which previously caused topic confusion across turns and visible
    special-token-like text leaking into the response. This exercises the
    fix against the real artifact across the Fifth Rework Handoff's
    required scenarios: DeepSeek-native multi-turn, cross-model
    continuation in both directions, retry/regenerate-style re-generation,
    and thinking-mode toggling across a turn boundary — asserting zero
    visible special-token leakage and a correct unrelated-topic follow-up
    answer in every case.
    """
    if not QWEN_MODEL_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {QWEN_MODEL_PATH}")
    if not DEEPSEEK_MODEL_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {DEEPSEEK_MODEL_PATH}")

    # `generation_overrides["max_new_tokens"]` here becomes `RuntimeModel
    # Controller.current_max_new_tokens`, and `ConversationGenerationInput.
    # settings.max_new_tokens` is clamped to it per-turn
    # (`effective_max_new_tokens = min(requested, generation_defaults.
    # max_new_tokens)` in conversation_generation.py) — it must be at least
    # as large as the largest per-turn budget requested below.
    with build_phase1_application(
        project_root=PROJECT_ROOT,
        profile_path=PROFILE_PATH,
        registry_path=QWEN_REGISTRY_PATH,
        generation_overrides={"max_new_tokens": 2048, "seed": 2371},
    ) as qwen_application:
        qwen_turn_1 = _run_turn(
            _build_service(qwen_application),
            (ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),),
        )

    deepseek_originated_turn_1: str
    with build_phase1_application(
        project_root=PROJECT_ROOT,
        profile_path=PROFILE_PATH,
        registry_path=DEEPSEEK_REGISTRY_PATH,
        cli_model_key="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        generation_overrides={"max_new_tokens": 2048, "seed": 2371},
    ) as deepseek_application:
        deepseek_service = _build_service(deepseek_application)

        # DeepSeek-R1 distill models reason at length and with highly
        # variable length, even on trivial questions and even under the
        # soft `/no_think` switch (DeepSeek's template has no hard
        # `enable_thinking` switch — see `hard_switch_supported` in
        # chat_template.py; observed reasoning explicitly noticing and
        # commenting on the injected "/no_think" text rather than obeying
        # it). A too-small token budget can be entirely consumed by an
        # unclosed <think> block, leaving nothing after HIDDEN-visibility
        # stripping (a legitimate, already-handled `final_answer_token_
        # limit` warning path — not a chat-template bug). Observed
        # completion length also varies run-to-run at a fixed seed on the
        # Metal/GPU backend (floating-point summation order is not fully
        # deterministic across process runs even with a fixed seed), so use
        # the maximum budget `ConversationSettings` allows
        # (`MAX_WEB_NEW_TOKENS`) for every real DeepSeek turn in this
        # matrix rather than tuning a smaller number that only sometimes
        # suffices.
        deepseek_max_new_tokens = 2048

        native_turn_1 = _run_turn(
            deepseek_service,
            (ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),),
            max_new_tokens=deepseek_max_new_tokens,
        )
        assert "東京" in native_turn_1

        native_turn_2 = _run_turn(
            deepseek_service,
            (
                ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),
                ConversationMessage(role=ConversationRole.ASSISTANT, content=native_turn_1),
                ConversationMessage(
                    role=ConversationRole.USER, content="フランスの首都はどこですか?"
                ),
            ),
            max_new_tokens=deepseek_max_new_tokens,
        )
        assert "パリ" in native_turn_2
        assert "東京" not in native_turn_2

        cross_qwen_to_deepseek = _run_turn(
            deepseek_service,
            (
                ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),
                ConversationMessage(role=ConversationRole.ASSISTANT, content=qwen_turn_1),
                ConversationMessage(
                    role=ConversationRole.USER, content="フランスの首都はどこですか?"
                ),
            ),
            max_new_tokens=deepseek_max_new_tokens,
        )
        assert "パリ" in cross_qwen_to_deepseek

        retry_turn = _run_turn(
            deepseek_service,
            (
                ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),
                ConversationMessage(role=ConversationRole.ASSISTANT, content=native_turn_1),
                ConversationMessage(role=ConversationRole.USER, content="では、フランスの首都は?"),
            ),
            max_new_tokens=deepseek_max_new_tokens,
        )
        assert "パリ" in retry_turn

        thinking_turn = _run_turn(
            deepseek_service,
            (ConversationMessage(role=ConversationRole.USER, content="1+1はいくつですか?"),),
            max_new_tokens=deepseek_max_new_tokens,
            thinking_mode=ThinkingMode.ENABLED,
        )
        thinking_followup = _run_turn(
            deepseek_service,
            (
                ConversationMessage(role=ConversationRole.USER, content="1+1はいくつですか?"),
                ConversationMessage(role=ConversationRole.ASSISTANT, content=thinking_turn),
                ConversationMessage(role=ConversationRole.USER, content="では2+2は?"),
            ),
            max_new_tokens=deepseek_max_new_tokens,
            thinking_mode=ThinkingMode.DISABLED,
        )
        assert "4" in thinking_followup

        deepseek_originated_turn_1 = native_turn_1

    with build_phase1_application(
        project_root=PROJECT_ROOT,
        profile_path=PROFILE_PATH,
        registry_path=QWEN_REGISTRY_PATH,
        generation_overrides={"max_new_tokens": 2048, "seed": 2371},
    ) as qwen_application_2:
        cross_deepseek_to_qwen = _run_turn(
            _build_service(qwen_application_2),
            (
                ConversationMessage(role=ConversationRole.USER, content="日本の首都はどこですか?"),
                ConversationMessage(
                    role=ConversationRole.ASSISTANT, content=deepseek_originated_turn_1
                ),
                ConversationMessage(
                    role=ConversationRole.USER, content="フランスの首都はどこですか?"
                ),
            ),
        )
        assert "パリ" in cross_deepseek_to_qwen
