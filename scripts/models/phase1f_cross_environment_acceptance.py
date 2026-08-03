"""Run a bounded Phase 1-F native runtime acceptance probe."""

from __future__ import annotations

import argparse
import gc
import json
import time
from collections.abc import Mapping
from pathlib import Path
from uuid import uuid4

import psutil  # type: ignore[import-untyped]

from margpa_runtime_llm.bootstrap.phase1_application import build_phase1_application
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ThinkingParseStatus,
    ThinkingVisibility,
)
from margpa_runtime_llm.orchestration.response_language import (
    ENGLISH_RESPONSE_INSTRUCTION,
    JAPANESE_RESPONSE_INSTRUCTION,
    compose_generation_messages,
    resolve_response_policy,
)
from margpa_runtime_llm.orchestration.thinking_presentation import (
    resolve_thinking_presentation_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
JAPANESE_MARKER = "日本語確認"
ENGLISH_MARKER = "ENGLISH-CHECK"
STREAM_MARKER = "STREAM-CHECK"
POST_CANCEL_MARKER = "POST-CANCEL-CHECK"
THINKING_FINAL_MARKER = "FINAL-CHECK"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument(
        "--model-root",
        type=Path,
        default=None,
        help="Model Root used to resolve the Registry artifact (never downloaded)",
    )
    return parser.parse_args()


def runtime_evidence_matches_profile(
    *,
    expected_compute_kind: str,
    expected_acceleration_api: str,
    runtime_device_kind: str,
    runtime_acceleration_api: str,
    runtime_gpu_offload: bool,
    gpu_offload_supported: bool,
    gpu_offload_requested: bool,
    gpu_offload_observed: bool,
) -> bool:
    if runtime_acceleration_api != expected_acceleration_api:
        return False
    if expected_compute_kind == "gpu":
        return (
            gpu_offload_supported
            and gpu_offload_requested
            and gpu_offload_observed
            and runtime_gpu_offload
            and runtime_device_kind == "gpu"
        )
    if expected_compute_kind == "cpu":
        return (
            not gpu_offload_requested
            and not gpu_offload_observed
            and not runtime_gpu_offload
            and runtime_device_kind == "cpu"
        )
    return False


def all_required_checks_passed(required_checks: Mapping[str, bool]) -> bool:
    return bool(required_checks) and all(required_checks.values())


def request(
    *,
    model_key: str,
    messages: tuple[ChatMessage, ...],
    max_new_tokens: int,
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED,
) -> GenerationRequest:
    return GenerationRequest(
        request_id=str(uuid4()),
        model_key=model_key,
        messages=messages,
        parameters=GenerationParameters(
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            min_p=0.0,
            presence_penalty=1.5,
            seed=2371,
            thinking_mode=thinking_mode,
        ),
    )


def main() -> int:
    args = parse_args()
    process = psutil.Process()
    rss_before_load = int(process.memory_info().rss)
    application = None
    try:
        load_started = time.perf_counter()
        application = build_phase1_application(
            project_root=PROJECT_ROOT,
            profile_path=args.profile,
            registry_path=args.registry,
            cli_model_root=args.model_root,
            generation_overrides={"max_new_tokens": 48, "seed": 2371},
        )
        load_seconds = time.perf_counter() - load_started
        rss_after_load = int(process.memory_info().rss)
        runtime = application.service.runtime_info
        if runtime is None:
            raise RuntimeError("runtime info was unavailable after a successful load")

        japanese_messages = tuple(
            compose_generation_messages(
                user_prompt=f"次の文字列をそのまま含めて答えてください: {JAPANESE_MARKER}",
                user_system_message=None,
                policy=application.config.response,
            )
        )
        non_stream = request(
            model_key=application.config.selected_model,
            max_new_tokens=24,
            messages=japanese_messages,
        )
        non_stream_result = application.service.generate(non_stream)

        english_policy = resolve_response_policy(
            application_policy=None,
            environment={},
            explicit_language=ResponseLanguage.EN,
        )
        english_messages = tuple(
            compose_generation_messages(
                user_prompt=f"Include this exact marker in your reply: {ENGLISH_MARKER}",
                user_system_message=None,
                policy=english_policy,
            )
        )
        english_result = application.service.generate(
            request(
                model_key=application.config.selected_model,
                max_new_tokens=24,
                messages=english_messages,
            )
        )

        completed_stream = application.service.stream(
            request(
                model_key=application.config.selected_model,
                messages=tuple(
                    compose_generation_messages(
                        user_prompt=f"Reply with this exact marker: {STREAM_MARKER}",
                        user_system_message=None,
                        policy=english_policy,
                    )
                ),
                max_new_tokens=32,
            )
        )
        completed_chunks = list(completed_stream)

        cancelled_stream = application.service.stream(
            request(
                model_key=application.config.selected_model,
                messages=tuple(
                    compose_generation_messages(
                        user_prompt="Count integers in order.",
                        user_system_message=None,
                        policy=english_policy,
                    )
                ),
                max_new_tokens=64,
            )
        )
        first_cancel_delta = ""
        for chunk in cancelled_stream:
            if chunk.text_delta:
                first_cancel_delta = chunk.text_delta
                cancelled_stream.cancel()
                break

        post_cancel = application.service.generate(
            request(
                model_key=application.config.selected_model,
                messages=tuple(
                    compose_generation_messages(
                        user_prompt=(f"Reply with this exact marker: {POST_CANCEL_MARKER}"),
                        user_system_message=None,
                        policy=english_policy,
                    )
                ),
                max_new_tokens=24,
            )
        )

        thinking_result = application.service.generate(
            request(
                model_key=application.config.selected_model,
                messages=tuple(
                    compose_generation_messages(
                        user_prompt=(
                            "Think briefly about 1+1, then include this exact marker "
                            f"in the final answer: {THINKING_FINAL_MARKER}"
                        ),
                        user_system_message=None,
                        policy=english_policy,
                    )
                ),
                max_new_tokens=1024,
                thinking_mode=ThinkingMode.ENABLED,
            )
        )
        hidden = application.presentation_service.present_text(
            thinking_result.content,
            application.config.presentation,
        )
        visible_policy = resolve_thinking_presentation_policy(
            application_policy=None,
            environment={},
            explicit_visibility=ThinkingVisibility.VISIBLE,
            explicit_display_label=None,
        )
        visible = application.presentation_service.present_text(
            thinking_result.content,
            visible_policy,
        )

        application.close()
        gc.collect()
        rss_after_unload = int(process.memory_info().rss)
        completed_terminal = completed_chunks[-1] if completed_chunks else None
        runtime_evidence = runtime.gpu_offload_evidence
        runtime_matches_profile = runtime_evidence_matches_profile(
            expected_compute_kind=application.config.compute.compute_kind_key,
            expected_acceleration_api=application.config.compute.acceleration_api_key,
            runtime_device_kind=runtime.device_kind,
            runtime_acceleration_api=runtime.acceleration_api,
            runtime_gpu_offload=runtime.gpu_offload,
            gpu_offload_supported=runtime_evidence.supported,
            gpu_offload_requested=runtime_evidence.requested,
            gpu_offload_observed=runtime_evidence.observed,
        )
        japanese_system_message = japanese_messages[0]
        english_system_message = english_messages[0]
        reasoning_content = hidden.normalized.reasoning_content or ""
        final_content = hidden.normalized.final_content
        required_checks = {
            "artifact_sha512_matches_definition": (
                runtime.artifact_digest.value == application.definition.artifact.sha512
            ),
            "runtime_evidence_matches_profile": runtime_matches_profile,
            "japanese_policy_resolved": (
                application.config.response.language is ResponseLanguage.JA
            ),
            "japanese_system_message_injected": (
                japanese_system_message.role is MessageRole.SYSTEM
                and japanese_system_message.content == JAPANESE_RESPONSE_INSTRUCTION
            ),
            "japanese_marker_generated": JAPANESE_MARKER in non_stream_result.content,
            "english_policy_resolved": english_policy.language is ResponseLanguage.EN,
            "english_system_message_injected": (
                english_system_message.role is MessageRole.SYSTEM
                and english_system_message.content == ENGLISH_RESPONSE_INSTRUCTION
            ),
            "english_marker_generated": ENGLISH_MARKER in english_result.content,
            "completed_stream_has_marker": (
                STREAM_MARKER in "".join(chunk.text_delta for chunk in completed_chunks)
            ),
            "completed_stream_has_terminal_chunk": (
                completed_terminal is not None
                and completed_terminal.is_final
                and completed_terminal.finish_reason is not None
            ),
            "cancel_produced_content": bool(first_cancel_delta),
            "cancel_terminal_state_is_cancelled": (
                cancelled_stream.terminal_state.value == "cancelled"
            ),
            "post_cancel_marker_generated": POST_CANCEL_MARKER in post_cancel.content,
            "thinking_finished_without_length_cutoff": (
                thinking_result.finish_reason is not FinishReason.LENGTH
            ),
            "thinking_protocol_complete": (
                hidden.normalized.parse_status is ThinkingParseStatus.COMPLETE
            ),
            "thinking_reasoning_segment_present": bool(reasoning_content.strip()),
            "thinking_final_segment_present": bool(final_content.strip()),
            "thinking_final_marker_generated": THINKING_FINAL_MARKER in final_content,
            "hidden_thinking_not_displayed": (
                hidden.display_content == final_content
                and "<think>" not in hidden.display_content
                and "</think>" not in hidden.display_content
            ),
            "visible_thinking_label_applied": (
                visible.display_content.startswith("<推論過程>")
                and "</推論過程>" in visible.display_content
            ),
            "visible_reasoning_and_final_are_separate": (
                reasoning_content in visible.display_content
                and final_content in visible.display_content
                and visible.display_content.endswith(final_content)
            ),
            "unload_completed": application.service.state is ModelLifecycleState.UNLOADED,
        }
        checks_passed = all_required_checks_passed(required_checks)
        resolved_model_artifact = (
            application.config.model_root / application.definition.artifact.relative_path
        ).resolve()
        report = {
            "success": checks_passed,
            "all_required_checks_passed": checks_passed,
            "profile_key": application.config.profile_key,
            "model_artifact_path": str(resolved_model_artifact),
            "load_seconds_including_sha512": round(load_seconds, 4),
            "rss_before_load_bytes": rss_before_load,
            "rss_after_load_bytes": rss_after_load,
            "rss_after_unload_bytes": rss_after_unload,
            "runtime": runtime.model_dump(mode="json"),
            "runtime_observation": application.runtime_observation.model_dump(mode="json"),
            "required_checks": required_checks,
            "observations": {
                "non_stream_content_chars": len(non_stream_result.content),
                "non_stream_finish_reason": non_stream_result.finish_reason.value,
                "english_content_chars": len(english_result.content),
                "stream_content_chars": sum(len(chunk.text_delta) for chunk in completed_chunks),
                "stream_finish_reason": (
                    completed_terminal.finish_reason.value
                    if completed_terminal is not None
                    and completed_terminal.finish_reason is not None
                    else None
                ),
                "cancel_first_delta_chars": len(first_cancel_delta),
                "cancel_terminal_state": cancelled_stream.terminal_state.value,
                "post_cancel_content_chars": len(post_cancel.content),
                "thinking_parse_status": hidden.normalized.parse_status.value,
                "thinking_finish_reason": thinking_result.finish_reason.value,
                "thinking_reasoning_chars": len(reasoning_content),
                "thinking_final_chars": len(final_content),
                "visible_thinking_chars": len(visible.display_content),
            },
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if checks_passed else 1
    except InferenceError as exc:
        print(json.dumps({"success": False, "error": exc.to_safe_dict()}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": {
                        "safe_message": "The native acceptance probe failed unexpectedly.",
                        "exception_type": type(exc).__name__,
                    },
                },
                ensure_ascii=False,
            )
        )
        return 1
    finally:
        if application is not None:
            application.close()


if __name__ == "__main__":
    raise SystemExit(main())
