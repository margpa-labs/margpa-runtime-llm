"""CLI behavior without loading a real model."""

from __future__ import annotations

import io
import sys
from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from typing import Any

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.stream import (
    LlamaCppGenerationStream,
)
from margpa_runtime_llm.bootstrap.config_loader import (
    EffectivePhase1Config,
    load_application_config,
    load_deployment_profile,
    resolve_effective_config,
)
from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.bootstrap.output_parser_registry import build_output_parser
from margpa_runtime_llm.bootstrap.profile_resolver import build_runtime_observation
from margpa_runtime_llm.entrypoints.cli import main as cli
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.orchestration.response_language import (
    ENGLISH_RESPONSE_INSTRUCTION,
    JAPANESE_RESPONSE_INSTRUCTION,
    resolve_response_policy,
)
from margpa_runtime_llm.orchestration.thinking_presentation import (
    resolve_thinking_presentation_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITION = load_model_definition(PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml")
APPLICATION = load_application_config(PROJECT_ROOT / "config/application.toml")
PROFILE = load_deployment_profile(PROJECT_ROOT / "config/profiles/local_macos_arm64.toml")
EFFECTIVE = resolve_effective_config(
    APPLICATION,
    PROFILE,
    project_root=PROJECT_ROOT,
    environment={},
)
MAC_RUNTIME_CAPABILITIES = MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}


def runtime_info() -> ModelRuntimeInfo:
    capabilities = ModelCapabilities(
        features=MAC_RUNTIME_CAPABILITIES,
        native_context_limit=32768,
        loaded_context_size=4096,
        supported_message_roles=frozenset(
            {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
        ),
    )
    return ModelRuntimeInfo(
        load_instance_id="load-1",
        model_key=DEFINITION.model_key,
        backend_key="fake",
        backend_version="1",
        model_architecture="qwen3",
        format="gguf",
        quantization="Q4_K_M",
        artifact_size_bytes=DEFINITION.artifact.size_bytes,
        artifact_digest=ModelDigest(value=DEFINITION.artifact.sha512),
        definition_file_sha512=DEFINITION.definition_file_sha512,
        loaded_context_size=4096,
        effective_capabilities=capabilities,
        chat_template_source="fake",
        chat_template_digest=ModelDigest(value="a" * 128),
        device="fake",
        device_kind="gpu",
        acceleration_api="metal",
        gpu_offload=True,
        gpu_offload_evidence=GpuOffloadEvidence(
            supported=True,
            requested=True,
            observed=True,
            observation_source="metal_model_load",
        ),
    )


class FakeStream:
    def __init__(
        self,
        *,
        interrupt: bool = False,
        text_deltas: tuple[str, ...] = ("streamed",),
        finish_reason: FinishReason = FinishReason.STOP,
    ) -> None:
        self.interrupt = interrupt
        self.text_deltas = text_deltas
        self.finish_reason = finish_reason
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "generation-1"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        if self.cancelled:
            return GenerationTerminalState.CANCELLED
        if self.closed:
            return GenerationTerminalState.CLOSED_BY_CONSUMER
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        if self.interrupt:
            raise KeyboardInterrupt
        for sequence, text_delta in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="request",
                sequence=sequence,
                text_delta=text_delta,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=self.finish_reason,
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


class FakeService:
    def __init__(
        self,
        stream: GenerationStream | None = None,
        result_content: str = "generated",
        result_finish_reason: FinishReason = FinishReason.STOP,
    ) -> None:
        self.runtime_info = runtime_info()
        self.stream_value = FakeStream() if stream is None else stream
        self.result_content = result_content
        self.result_finish_reason = result_finish_reason
        self.requests: list[GenerationRequest] = []

    def generate(
        self, request: GenerationRequest, *, cancellation: object = None
    ) -> GenerationResult:
        self.requests.append(request)
        return GenerationResult(
            request_id="request",
            model_key=DEFINITION.model_key,
            content=self.result_content,
            finish_reason=self.result_finish_reason,
            backend_finish_reason=self.result_finish_reason.value,
            timing=GenerationTiming(total_generation_seconds=0.1),
            runtime_info=self.runtime_info.reference(),
        )

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return self.stream_value

    def unload(self) -> None:
        return None


class FakeApplication:
    def __init__(
        self,
        stream: GenerationStream | None = None,
        result_content: str = "generated",
        result_finish_reason: FinishReason = FinishReason.STOP,
    ) -> None:
        self.service = FakeService(stream, result_content, result_finish_reason)
        self.definition = DEFINITION
        self.config: EffectivePhase1Config = EFFECTIVE
        self.presentation_service = ThinkingPresentationService(
            build_output_parser(DEFINITION.output_protocol.thinking)
        )
        self.runtime_observation = build_runtime_observation(
            host=EFFECTIVE.host,
            backend=EFFECTIVE.backend_runtime,
            runtime_info=self.service.runtime_info,
        )

    def apply_response_language(self, language: ResponseLanguage | None) -> None:
        if language is None:
            return
        policy = resolve_response_policy(
            application_policy=APPLICATION.response,
            environment={},
            explicit_language=language,
        )
        self.config = self.config.model_copy(update={"response": policy})

    def apply_generation_overrides(self, overrides: dict[str, object]) -> None:
        if not overrides:
            return
        generation = self.config.generation.model_copy(update=overrides)
        self.config = self.config.model_copy(update={"generation": generation})

    def apply_thinking_presentation(
        self,
        visibility: ThinkingVisibility | None,
        display_label: str | None,
    ) -> None:
        policy = resolve_thinking_presentation_policy(
            application_policy=APPLICATION.presentation.thinking,
            environment=None,
            explicit_visibility=visibility,
            explicit_display_label=display_label,
        )
        self.config = self.config.model_copy(update={"presentation": policy})

    def __enter__(self) -> FakeApplication:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


def install_fake_application(monkeypatch: pytest.MonkeyPatch, application: FakeApplication) -> None:
    def builder(**kwargs: Any) -> FakeApplication:
        application.apply_generation_overrides(kwargs.get("generation_overrides", {}))
        application.apply_response_language(kwargs.get("response_language"))
        application.apply_thinking_presentation(
            kwargs.get("thinking_visibility"),
            kwargs.get("thinking_label"),
        )
        return application

    monkeypatch.setattr(cli, "build_phase1_application", builder)


def test_cli_non_stream_generation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    application = FakeApplication()
    install_fake_application(monkeypatch, application)

    exit_code = cli.main(["generate", "--prompt", "hello", "--no-stream"])

    assert exit_code == 0
    assert capsys.readouterr().out == "generated\n"
    assert application.service.requests[0].messages[0].content == JAPANESE_RESPONSE_INSTRUCTION


def test_cli_stream_generation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    install_fake_application(monkeypatch, FakeApplication())

    exit_code = cli.main(["generate", "--prompt", "hello"])

    assert exit_code == 0
    assert capsys.readouterr().out == "streamed\n"


@pytest.mark.parametrize(
    "argv",
    [
        ["--help"],
        ["generate", "--help"],
        ["model-info", "--help"],
    ],
)
def test_cli_help_explains_metavariables_without_loading_model(
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as captured:
        cli.main(argv)

    assert captured.value.code == 0
    output = capsys.readouterr().out
    assert "仮引数名" in output
    assert "generateまたはmodel-infoの後ろ" in output


def test_cli_help_shows_correct_profile_placement(
    capsys: pytest.CaptureFixture[str],
) -> None:
    correct = cli.build_parser().parse_args(
        ["model-info", "--profile", "config/profiles/example.toml"]
    )
    assert correct.profile == Path("config/profiles/example.toml")

    with pytest.raises(SystemExit) as captured:
        cli.build_parser().parse_args(["--profile", "config/profiles/example.toml", "model-info"])
    assert captured.value.code == 2
    capsys.readouterr()

    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["model-info", "--help"])
    assert "--profile PROFILE_PATH" in capsys.readouterr().out


def test_cli_default_hidden_removes_leading_canonical_reasoning(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    application = FakeApplication(result_content="<think>private</think>final")
    install_fake_application(monkeypatch, application)

    exit_code = cli.main(["generate", "--prompt", "hello", "--no-stream"])

    assert exit_code == 0
    assert capsys.readouterr().out == "final\n"
    assert application.service.requests[0].parameters.thinking_mode == "disabled"


@pytest.mark.parametrize("no_stream", [False, True])
def test_cli_hidden_thinking_token_limit_warning_is_safe_and_successful(
    no_stream: bool,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    if no_stream:
        application = FakeApplication(
            result_content="<think>private reasoning",
            result_finish_reason=FinishReason.LENGTH,
        )
    else:
        application = FakeApplication(
            stream=FakeStream(
                text_deltas=("<think>private ", "reasoning"),
                finish_reason=FinishReason.LENGTH,
            )
        )
    install_fake_application(monkeypatch, application)
    argv = ["generate", "--prompt", "hello", "--thinking"]
    if no_stream:
        argv.append("--no-stream")

    exit_code = cli.main(argv)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "\n"
    assert "最終回答を生成する前にToken上限へ到達しました。" in captured.err
    assert "--max-new-tokens" in captured.err
    assert "private reasoning" not in captured.err


@pytest.mark.parametrize(
    ("content", "finish_reason", "extra_args"),
    [
        ("<think>reasoning", FinishReason.STOP, ["--thinking"]),
        ("<think>reasoning</think>answer", FinishReason.LENGTH, ["--thinking"]),
        ("<think>reasoning", FinishReason.LENGTH, ["--thinking", "--show-thinking"]),
        ("<think>reasoning", FinishReason.LENGTH, ["--no-thinking"]),
        ("", FinishReason.LENGTH, ["--thinking"]),
    ],
)
def test_cli_hidden_thinking_warning_avoids_false_positives(
    content: str,
    finish_reason: FinishReason,
    extra_args: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    application = FakeApplication(
        result_content=content,
        result_finish_reason=finish_reason,
    )
    install_fake_application(monkeypatch, application)

    exit_code = cli.main(["generate", "--prompt", "hello", "--no-stream", *extra_args])

    assert exit_code == 0
    assert "Token上限" not in capsys.readouterr().err


def test_cli_execution_and_visibility_are_independent(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    visible = FakeApplication(result_content="<think>reason</think>answer")
    install_fake_application(monkeypatch, visible)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--show-thinking",
                "--no-stream",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == "<推論過程>reason</推論過程>answer\n"
    assert visible.service.requests[0].parameters.thinking_mode == "disabled"
    assert visible.config.presentation.visibility == "visible"

    hidden = FakeApplication(result_content="<think>reason</think>answer")
    install_fake_application(monkeypatch, hidden)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--thinking",
                "--no-stream",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == "answer\n"
    assert hidden.service.requests[0].parameters.thinking_mode == "enabled"
    assert hidden.service.requests[0].parameters.temperature == 0.7
    assert hidden.service.requests[0].parameters.top_p == 0.8
    assert hidden.service.requests[0].parameters.presence_penalty == 1.5
    assert hidden.config.presentation.visibility == "hidden"


def test_cli_custom_label_and_streaming_non_streaming_parity(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    raw = "<think>reason</think>answer"
    non_streaming = FakeApplication(result_content=raw)
    install_fake_application(monkeypatch, non_streaming)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--show-thinking",
                "--thinking-label",
                "思考過程",
                "--no-stream",
            ]
        )
        == 0
    )
    non_stream_output = capsys.readouterr().out

    streaming = FakeApplication(
        stream=FakeStream(text_deltas=("<thi", "nk>reason</th", "ink>answer"))
    )
    install_fake_application(monkeypatch, streaming)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--show-thinking",
                "--thinking-label",
                "思考過程",
            ]
        )
        == 0
    )
    stream_output = capsys.readouterr().out

    assert non_stream_output == "<思考過程>reason</思考過程>answer\n"
    assert stream_output == non_stream_output
    assert all(
        "思考過程" not in message.content for message in non_streaming.service.requests[0].messages
    )


def test_cli_visibility_flags_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit) as captured:
        cli.build_parser().parse_args(["generate", "--show-thinking", "--hide-thinking"])

    assert captured.value.code == 2


def test_cli_rejects_invalid_thinking_label_safely(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    application = FakeApplication()
    install_fake_application(monkeypatch, application)

    exit_code = cli.main(
        [
            "generate",
            "--prompt",
            "hello",
            "--thinking-label",
            "<unsafe>",
            "--no-stream",
        ]
    )

    assert exit_code == 2
    error_output = capsys.readouterr().err
    assert "invalid_request" in error_output
    assert "<unsafe>" not in error_output
    assert application.service.requests == []


def test_cli_presentation_environment_and_explicit_precedence(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("MARGPA_THINKING_VISIBILITY", "visible")
    monkeypatch.setenv("MARGPA_THINKING_LABEL", "環境推論")
    environment = FakeApplication(result_content="<think>reason</think>answer")
    install_fake_application(monkeypatch, environment)
    assert cli.main(["generate", "--prompt", "hello", "--no-stream"]) == 0
    assert capsys.readouterr().out == "<環境推論>reason</環境推論>answer\n"
    assert environment.config.presentation.visibility_source == "environment"
    assert environment.config.presentation.display_label_source == "environment"

    explicit = FakeApplication(result_content="<think>reason</think>answer")
    install_fake_application(monkeypatch, explicit)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--hide-thinking",
                "--thinking-label",
                "明示推論",
                "--no-stream",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == "answer\n"
    assert explicit.config.presentation.visibility_source == "explicit"
    assert explicit.config.presentation.display_label_source == "explicit"


def test_cli_response_language_override_and_streaming_parity(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    non_streaming = FakeApplication()
    install_fake_application(monkeypatch, non_streaming)
    assert (
        cli.main(
            [
                "generate",
                "--prompt",
                "hello",
                "--response-language",
                "en",
                "--no-stream",
            ]
        )
        == 0
    )
    capsys.readouterr()

    streaming = FakeApplication()
    install_fake_application(monkeypatch, streaming)
    assert cli.main(["generate", "--prompt", "hello", "--response-language", "en"]) == 0
    capsys.readouterr()

    non_stream_messages = non_streaming.service.requests[0].messages
    stream_messages = streaming.service.requests[0].messages
    assert non_stream_messages == stream_messages
    assert non_stream_messages[0].content == ENGLISH_RESPONSE_INSTRUCTION


def test_cli_reads_prompt_from_stdin(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_fake_application(monkeypatch, FakeApplication())
    monkeypatch.setattr(sys, "stdin", io.StringIO("stdin prompt"))

    exit_code = cli.main(["generate", "--no-stream"])

    assert exit_code == 0
    assert capsys.readouterr().out == "generated\n"


def test_cli_thinking_and_sampling_flags_become_explicit_overrides() -> None:
    args = cli.build_parser().parse_args(
        [
            "generate",
            "--prompt",
            "hello",
            "--thinking",
            "--temperature",
            "0.6",
            "--top-p",
            "0.95",
        ]
    )

    overrides = cli._generation_overrides(args)

    assert overrides["thinking_mode"] == "enabled"
    assert overrides["temperature"] == 0.6
    assert overrides["top_p"] == 0.95


def test_cli_ctrl_c_uses_cooperative_cancel(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stream = FakeStream(interrupt=True)
    install_fake_application(monkeypatch, FakeApplication(stream))

    exit_code = cli.main(["generate", "--prompt", "hello"])

    assert exit_code == 130
    assert stream.cancelled
    assert "cancelled" in capsys.readouterr().err.lower()


def test_cli_ctrl_c_through_llama_cpp_stream_releases_generation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class InterruptingNativeIterator:
        def __init__(self) -> None:
            self.close_calls = 0

        def __iter__(self) -> InterruptingNativeIterator:
            return self

        def __next__(self) -> dict[str, Any]:
            raise KeyboardInterrupt

        def close(self) -> None:
            self.close_calls += 1

    generation_released = False

    def release_generation() -> None:
        nonlocal generation_released
        generation_released = True

    native = InterruptingNativeIterator()
    stream = LlamaCppGenerationStream(
        generation_id="generation-production-boundary",
        request_id="request",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=release_generation,
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
    )
    application = FakeApplication(stream)
    install_fake_application(monkeypatch, application)

    exit_code = cli.main(["generate", "--prompt", "hello"])

    assert exit_code == 130
    assert stream.terminal_state is GenerationTerminalState.CANCELLED
    assert native.close_calls == 1
    assert generation_released
    assert (
        application.service.generate(
            GenerationRequest(
                request_id="after-cancel",
                model_key=DEFINITION.model_key,
                messages=application.service.requests[0].messages,
            )
        ).content
        == "generated"
    )
    captured = capsys.readouterr()
    assert "Generation cancelled." in captured.err
    assert "generation_failed" not in captured.err


def test_cli_model_info_is_structured_and_omits_absolute_model_root(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    install_fake_application(monkeypatch, FakeApplication())

    exit_code = cli.main(["model-info"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"model_key": "main.qwen3-4b-q4-k-m"' in output
    assert '"application_key": "default"' in output
    assert '"artifact_digest_verified": true' in output
    assert '"verification_state": "native_verified"' in output
    assert '"acceleration_api_key": "metal"' in output
    assert '"gpu_offload": true' in output
    assert '"executed": null' in output
    assert '"profile_resolution_source": "explicit"' in output
    assert '"thinking_mode": "disabled"' in output
    assert '"language": "ja"' in output
    assert '"source": "application"' in output
    assert '"application_schema_version": "3"' in output
    assert '"model_definition_schema_version": "2"' in output
    assert '"visibility": "hidden"' in output
    assert '"display_label": "推論過程"' in output
    assert '"persistence": "disabled"' in output
    assert '"visibility_source": "application"' in output
    assert '"display_label_source": "application"' in output
    assert '"persistence_source": "application"' in output
    assert '"parser_key": "tagged_thinking_v1"' in output
    assert str(EFFECTIVE.model_root) not in output


def test_cli_displays_only_safe_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def failing_builder(**kwargs: Any) -> FakeApplication:
        raise InferenceError(
            code=InferenceErrorCode.MODEL_NOT_FOUND,
            safe_message="The configured model artifact was not found.",
            details={"native": "/Users/example/private/model.gguf at 0x1234"},
        )

    monkeypatch.setattr(cli, "build_phase1_application", failing_builder)
    exit_code = cli.main(["model-info"])
    error_output = capsys.readouterr().err

    assert exit_code == 2
    assert "model_not_found" in error_output
    assert "/Users/" not in error_output
    assert "0x1234" not in error_output
