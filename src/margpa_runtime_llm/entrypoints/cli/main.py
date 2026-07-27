"""One-shot Phase 1 command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from margpa_runtime_llm.bootstrap.phase1_application import (
    Phase1Application,
    build_phase1_application,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    PresentedThinkingOutput,
    ThinkingVisibility,
)
from margpa_runtime_llm.orchestration.response_language import compose_generation_messages

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
HIDDEN_THINKING_TOKEN_LIMIT_WARNING = (
    "最終回答を生成する前にToken上限へ到達しました。--max-new-tokensを増やして再試行してください。"
)
PLACEHOLDER_HELP = (
    "Usage内の大文字(COMMAND、PROFILE_PATH、MODEL_ROOT、TOKENS等)は、"
    "実際の値へ置き換える仮引数名です。\n"
    "--profile等の共通Optionは、generateまたはmodel-infoの後ろへ指定してください。"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="margpa-llm",
        description=__doc__,
        epilog=PLACEHOLDER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--profile",
        type=Path,
        metavar="PROFILE_PATH",
        help="Deployment Profile path (after COMMAND; env/default resolution when omitted)",
    )
    common.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        metavar="MODEL_DEFINITION_PATH",
        help="Model Definition path (default: tracked Qwen3-4B definition)",
    )
    common.add_argument(
        "--model-root",
        type=Path,
        metavar="MODEL_ROOT",
        help="Model storage root (default source: MARGPA_MODEL_ROOT/application config)",
    )
    common.add_argument(
        "--model-key",
        metavar="MODEL_KEY",
        help="Registered model key (default source: MARGPA_MODEL_KEY/application config)",
    )
    common.add_argument(
        "--context-size",
        type=int,
        metavar="TOKENS",
        help="Loaded context size in tokens (default source: profile/application config)",
    )
    common.add_argument(
        "--response-language",
        type=ResponseLanguage,
        choices=tuple(ResponseLanguage),
        help="Final response language policy (ja, en, or auto; default: application config)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    generate = subparsers.add_parser(
        "generate",
        parents=[common],
        help="Generate one response",
        description="Generate one response from the selected model.",
        epilog=PLACEHOLDER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generate.add_argument(
        "--prompt",
        metavar="TEXT",
        help="User prompt; stdin is used when omitted",
    )
    generate.add_argument("--system", metavar="TEXT", help="Optional system message")
    generate.add_argument(
        "--no-stream",
        action="store_true",
        help="Wait for one non-streaming response",
    )
    thinking = generate.add_mutually_exclusive_group()
    thinking.add_argument("--thinking", action="store_true", help="Enable model thinking")
    thinking.add_argument("--no-thinking", action="store_true", help="Disable model thinking")
    visibility = generate.add_mutually_exclusive_group()
    visibility.add_argument(
        "--show-thinking",
        action="store_true",
        help="Show parsed thinking with the presentation label",
    )
    visibility.add_argument(
        "--hide-thinking",
        action="store_true",
        help="Hide parsed thinking (default: application config)",
    )
    generate.add_argument(
        "--thinking-label",
        metavar="LABEL",
        help="Visible thinking label (default: application config)",
    )
    generate.add_argument(
        "--max-new-tokens",
        type=int,
        metavar="TOKENS",
        help="Maximum generated tokens (default source: env/application config)",
    )
    generate.add_argument(
        "--temperature",
        type=float,
        metavar="VALUE",
        help="Sampling temperature (default source: env/application config)",
    )
    generate.add_argument(
        "--top-p",
        type=float,
        metavar="VALUE",
        help="Nucleus sampling probability (default source: env/application config)",
    )
    generate.add_argument(
        "--top-k",
        type=int,
        metavar="COUNT",
        help="Top-k sampling count (default source: env/application config)",
    )
    generate.add_argument(
        "--min-p",
        type=float,
        metavar="VALUE",
        help="Minimum relative probability (default source: env/application config)",
    )
    generate.add_argument(
        "--presence-penalty",
        type=float,
        metavar="VALUE",
        help="Presence penalty (default source: env/application config)",
    )
    generate.add_argument(
        "--frequency-penalty",
        type=float,
        metavar="VALUE",
        help="Frequency penalty (default source: env/application config)",
    )
    generate.add_argument(
        "--repeat-penalty",
        type=float,
        metavar="VALUE",
        help="Repeat penalty (default source: env/application config)",
    )
    generate.add_argument(
        "--seed",
        type=int,
        metavar="INTEGER",
        help="Deterministic sampling seed (default: backend-selected)",
    )
    generate.add_argument(
        "--stop",
        action="append",
        default=None,
        metavar="TEXT",
        help="Stop sequence; repeat the option to add more than one",
    )

    subparsers.add_parser(
        "model-info",
        parents=[common],
        help="Show effective runtime info",
        description="Load the selected model and show effective runtime information as JSON.",
        epilog=PLACEHOLDER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        generation_overrides = _generation_overrides(args)
        load_overrides = _without_none({"context_size": args.context_size})
        thinking_visibility = _thinking_visibility_override(args)
        with build_phase1_application(
            project_root=PROJECT_ROOT,
            profile_path=args.profile,
            registry_path=args.registry,
            cli_model_root=args.model_root,
            cli_model_key=args.model_key,
            generation_overrides=generation_overrides,
            load_overrides=load_overrides,
            response_language=args.response_language,
            thinking_visibility=thinking_visibility,
            thinking_label=getattr(args, "thinking_label", None),
        ) as application:
            if args.command == "model-info":
                return _print_model_info(application)
            return _generate(application, args)
    except InferenceError as exc:
        print(f"error [{exc.code.value}]: {exc.safe_message}", file=sys.stderr)
        return _exit_code_for_error(exc.code)
    except ValidationError:
        print("error [invalid_request]: The generation request is invalid.", file=sys.stderr)
        return 2


def _generate(application: Phase1Application, args: argparse.Namespace) -> int:
    prompt = args.prompt if args.prompt is not None else sys.stdin.read()
    messages = compose_generation_messages(
        user_prompt=prompt,
        user_system_message=args.system,
        policy=application.config.response,
    )

    request = GenerationRequest(
        request_id=str(uuid4()),
        model_key=application.config.selected_model,
        messages=tuple(messages),
        parameters=application.config.generation,
    )
    if args.no_stream:
        result = application.service.generate(request)
        presented = application.presentation_service.present_text(
            result.content,
            application.config.presentation,
        )
        print(presented.display_content)
        _warn_if_hidden_thinking_exhausted(
            request=request,
            visibility=application.config.presentation.visibility,
            presented=presented,
            finish_reason=result.finish_reason,
        )
        return 0

    stream = application.service.stream(request)
    presentation = application.presentation_service.start_stream(application.config.presentation)
    finish_reason: FinishReason | None = None
    with stream:
        try:
            for chunk in stream:
                if chunk.is_final:
                    finish_reason = chunk.finish_reason
                for display_delta in presentation.feed(chunk.text_delta):
                    print(display_delta, end="", flush=True)
            terminal = presentation.finish()
            for display_delta in terminal.display_deltas:
                print(display_delta, end="", flush=True)
            print()
            _warn_if_hidden_thinking_exhausted(
                request=request,
                visibility=application.config.presentation.visibility,
                presented=terminal.presented,
                finish_reason=finish_reason,
            )
            return 0
        except KeyboardInterrupt:
            stream.cancel()
            terminal = presentation.finish()
            for display_delta in terminal.display_deltas:
                print(display_delta, end="", flush=True)
            print(file=sys.stderr)
            print("Generation cancelled.", file=sys.stderr)
            return 130


def _print_model_info(application: Phase1Application) -> int:
    runtime_info = application.service.runtime_info
    if runtime_info is None:
        raise InferenceError(
            code=InferenceErrorCode.MODEL_NOT_LOADED,
            safe_message="The model is not loaded.",
        )
    payload = {
        "runtime": runtime_info.model_dump(mode="json"),
        "effective_config": {
            "application_schema_version": application.config.application_schema_version,
            "application_key": application.config.application_key,
            "profile_key": application.config.profile_key,
            "selected_model": application.config.selected_model,
            "load": application.config.load.model_dump(mode="json"),
            "generation": application.config.generation.model_dump(mode="json"),
            "response": application.config.response.model_dump(mode="json"),
            "presentation": {"thinking": application.config.presentation.model_dump(mode="json")},
            "applied_sources": application.config.applied_sources,
        },
        "model_output_protocol": {
            "model_definition_schema_version": application.definition.schema_version,
            "thinking": application.definition.output_protocol.thinking.model_dump(mode="json"),
        },
        "deployment": {
            "verification_state": application.config.verification_state.value,
            "host": application.config.host.model_dump(mode="json"),
            "compute": application.config.compute.model_dump(mode="json"),
            "backend_runtime": application.config.backend_runtime.model_dump(mode="json"),
            "runtime_requirements": application.config.runtime_requirements.model_dump(mode="json"),
            "profile_resolution_source": application.config.profile_resolution_source,
            "runtime_observation": application.runtime_observation.model_dump(mode="json"),
        },
        "provenance": {
            "distribution_repository": application.definition.source.distribution_repository,
            "upstream_model": application.definition.source.upstream_model,
            "revision": application.definition.source.revision,
            "complete": application.definition.verification.provenance_complete,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _generation_overrides(args: argparse.Namespace) -> dict[str, object]:
    if args.command != "generate":
        return {}
    thinking_mode: ThinkingMode | None = None
    if args.thinking:
        thinking_mode = ThinkingMode.ENABLED
    elif args.no_thinking:
        thinking_mode = ThinkingMode.DISABLED
    values: dict[str, object | None] = {
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "min_p": args.min_p,
        "presence_penalty": args.presence_penalty,
        "frequency_penalty": args.frequency_penalty,
        "repeat_penalty": args.repeat_penalty,
        "seed": args.seed,
        "stop_sequences": tuple(args.stop) if args.stop else None,
        "thinking_mode": thinking_mode,
    }
    return _without_none(values)


def _without_none(values: Mapping[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in values.items() if value is not None}


def _thinking_visibility_override(args: argparse.Namespace) -> ThinkingVisibility | None:
    if args.command != "generate":
        return None
    if args.show_thinking:
        return ThinkingVisibility.VISIBLE
    if args.hide_thinking:
        return ThinkingVisibility.HIDDEN
    return None


def _warn_if_hidden_thinking_exhausted(
    *,
    request: GenerationRequest,
    visibility: ThinkingVisibility,
    presented: PresentedThinkingOutput,
    finish_reason: FinishReason | None,
) -> None:
    normalized = presented.normalized
    if (
        request.parameters.thinking_mode is ThinkingMode.ENABLED
        and visibility is ThinkingVisibility.HIDDEN
        and finish_reason is FinishReason.LENGTH
        and normalized.reasoning_content is not None
        and not normalized.final_content.strip()
    ):
        print(f"warning: {HIDDEN_THINKING_TOKEN_LIMIT_WARNING}", file=sys.stderr)


def _exit_code_for_error(code: InferenceErrorCode) -> int:
    if code in {
        InferenceErrorCode.INVALID_REQUEST,
        InferenceErrorCode.INVALID_CONFIGURATION,
        InferenceErrorCode.INVALID_MODEL_DEFINITION,
        InferenceErrorCode.UNSUPPORTED_PLATFORM,
        InferenceErrorCode.PROFILE_REQUIRED,
        InferenceErrorCode.MODEL_NOT_FOUND,
        InferenceErrorCode.MODEL_INTEGRITY_MISMATCH,
        InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED,
        InferenceErrorCode.UNSUPPORTED_CAPABILITY,
    }:
        return 2
    if code in {
        InferenceErrorCode.BACKEND_UNAVAILABLE,
        InferenceErrorCode.MODEL_LOAD_FAILED,
        InferenceErrorCode.MODEL_UNLOAD_FAILED,
    }:
        return 3
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
