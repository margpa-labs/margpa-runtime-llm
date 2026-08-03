"""Run a bounded Phase 1-B production runtime acceptance probe."""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path
from uuid import uuid4

import psutil  # type: ignore[import-untyped]

from margpa_runtime_llm.bootstrap.phase1_application import build_phase1_application
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    return parser.parse_args()


def make_request(request_id: str, prompt: str, max_new_tokens: int) -> GenerationRequest:
    return GenerationRequest(
        request_id=request_id,
        model_key="main.qwen3-4b-q4-k-m",
        messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
        parameters=GenerationParameters(
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            min_p=0.0,
            presence_penalty=1.5,
            seed=2371,
            thinking_mode=ThinkingMode.DISABLED,
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
            generation_overrides={"max_new_tokens": 48, "seed": 2371},
        )
        load_seconds = time.perf_counter() - load_started
        rss_after_load = int(process.memory_info().rss)
        runtime = application.service.runtime_info
        if runtime is None:
            raise RuntimeError("runtime info was unavailable after a successful load")

        result = application.service.generate(
            make_request(
                str(uuid4()),
                "日本語で『Phase 1-B Production Runtime成功』と短く答えてください。",
                48,
            )
        )
        rss_after_generation = int(process.memory_info().rss)

        stream = application.service.stream(
            make_request(str(uuid4()), "1から順に整数を列挙してください。", 64)
        )
        first_stream_text = ""
        for chunk in stream:
            if chunk.text_delta:
                first_stream_text = chunk.text_delta
                stream.cancel()
                break

        post_cancel = application.service.generate(
            make_request(str(uuid4()), "日本語でOKとだけ答えてください。", 16)
        )
        unload_started = time.perf_counter()
        application.close()
        unload_seconds = time.perf_counter() - unload_started
        gc.collect()
        time.sleep(0.25)
        rss_after_unload = int(process.memory_info().rss)

        report = {
            "success": True,
            "load_seconds_including_sha512": round(load_seconds, 4),
            "unload_seconds": round(unload_seconds, 4),
            "rss_before_load_bytes": rss_before_load,
            "rss_after_load_bytes": rss_after_load,
            "rss_after_generation_bytes": rss_after_generation,
            "rss_after_unload_bytes": rss_after_unload,
            "runtime": runtime.model_dump(mode="json"),
            "deployment": {
                "application_key": application.config.application_key,
                "profile_key": application.config.profile_key,
                "verification_state": application.config.verification_state.value,
                "profile_resolution_source": application.config.profile_resolution_source,
                "response": application.config.response.model_dump(mode="json"),
                "applied_sources": application.config.applied_sources,
                "runtime_observation": application.runtime_observation.model_dump(mode="json"),
            },
            "generation": {
                "content": result.content,
                "finish_reason": result.finish_reason.value,
                "usage": result.usage.model_dump(mode="json") if result.usage else None,
                "timing": result.timing.model_dump(mode="json"),
                "thinking_tags_absent": "<think>" not in result.content
                and "</think>" not in result.content,
            },
            "stream": {
                "first_text_delta": first_stream_text,
                "terminal_state": stream.terminal_state.value,
                "timing": stream.timing.model_dump(mode="json") if stream.timing else None,
            },
            "post_cancel": {
                "content": post_cancel.content,
                "finish_reason": post_cancel.finish_reason.value,
            },
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except InferenceError as exc:
        print(json.dumps({"success": False, "error": exc.to_safe_dict()}, ensure_ascii=False))
        return 1
    finally:
        if application is not None:
            application.close()


if __name__ == "__main__":
    raise SystemExit(main())
