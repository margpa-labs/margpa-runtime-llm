"""Phase 1 probe for the local llama.cpp Metal backend.

This module deliberately stops short of implementing the production Model Port. It verifies
the backend and local Qwen3 artifact before the model-independent contract is finalized.
"""

from __future__ import annotations

import gc
import importlib.metadata
import platform
import sys
import threading
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import psutil  # type: ignore[import-untyped]
from llama_cpp import Llama, llama_cpp


@dataclass(frozen=True, slots=True)
class MetalSmokeConfig:
    """Explicit settings used only by the Phase 1 smoke test."""

    model_path: Path
    n_ctx: int = 1024
    n_batch: int = 256
    n_threads: int = 6
    max_tokens: int = 48
    seed: int = 2371
    verbose: bool = True


@dataclass(frozen=True, slots=True)
class MetalSmokeResult:
    """Observable results from a single load, generation, stop, and unload cycle."""

    success: bool
    python_version: str
    machine: str
    gil_enabled: bool | None
    llama_cpp_python_version: str
    backend_system_info: str
    gpu_offload_supported: bool
    requested_gpu_layers: int
    model_path: str
    model_size_bytes: int
    backend_cold_init_seconds: float
    model_load_after_backend_init_seconds: float
    first_content_latency_seconds: float
    total_generation_seconds: float
    unload_seconds: float
    completion_tokens: int
    tokens_per_second: float
    generated_text: str
    streaming_text_before_cancel: str
    streaming_cancel_verified: bool
    post_cancel_generation_verified: bool
    stop_sequence_finish_reason: str | None
    rss_before_load_bytes: int
    rss_after_load_bytes: int
    peak_rss_bytes: int
    rss_after_unload_bytes: int
    metadata_architecture: str | None
    metadata_chat_template_present: bool

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return asdict(self)


class _MemorySampler:
    """Sample process RSS while the native backend owns model resources."""

    def __init__(self, interval_seconds: float = 0.05) -> None:
        self._interval_seconds = interval_seconds
        self._process = psutil.Process()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self.peak_rss_bytes = self.current_rss_bytes()

    def current_rss_bytes(self) -> int:
        """Return the current resident set size."""

        return int(self._process.memory_info().rss)

    def _sample(self) -> None:
        while not self._stop_event.wait(self._interval_seconds):
            self.peak_rss_bytes = max(self.peak_rss_bytes, self.current_rss_bytes())

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        self.peak_rss_bytes = max(self.peak_rss_bytes, self.current_rss_bytes())


def _gil_enabled() -> bool | None:
    check = getattr(sys, "_is_gil_enabled", None)
    if check is None:
        return None
    return bool(check())


def _choice_text(response: dict[str, Any]) -> str:
    choices = response.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    return content if isinstance(content, str) else ""


def _stream_and_cancel(model: Llama, *, seed: int) -> tuple[str, bool, float]:
    started = time.perf_counter()
    raw_stream = model.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": "/no_think\n1から順に整数を列挙してください。",
            }
        ],
        max_tokens=64,
        temperature=0.0,
        seed=seed,
        stream=True,
    )
    stream = cast(Iterator[dict[str, Any]], raw_stream)
    pieces: list[str] = []
    received_content = False
    first_content_latency_seconds = 0.0
    for chunk in stream:
        choices = chunk.get("choices", [])
        if not choices:
            continue
        delta = choices[0].get("delta", {})
        content = delta.get("content", "")
        if isinstance(content, str) and content:
            pieces.append(content)
            received_content = True
            first_content_latency_seconds = time.perf_counter() - started
            break

    close = getattr(stream, "close", None)
    if callable(close):
        close()
    return (
        "".join(pieces),
        received_content and callable(close),
        first_content_latency_seconds,
    )


def _post_cancel_generation(model: Llama, *, seed: int) -> bool:
    raw_response = model.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": "/no_think\nOKとだけ答えてください。",
            }
        ],
        max_tokens=8,
        temperature=0.0,
        seed=seed,
        stream=False,
    )
    response = cast(dict[str, Any], raw_response)
    return bool(_choice_text(response).strip())


def _stop_sequence_probe(model: Llama, *, seed: int) -> str | None:
    raw_response = model.create_completion(
        prompt="Complete with one English word: alpha beta",
        max_tokens=16,
        temperature=0.0,
        seed=seed,
        stop=[" "],
        stream=False,
    )
    response = cast(dict[str, Any], raw_response)
    choices = response.get("choices", [])
    if not choices:
        return None
    finish_reason = choices[0].get("finish_reason")
    return finish_reason if isinstance(finish_reason, str) else None


def run_metal_smoke(config: MetalSmokeConfig) -> MetalSmokeResult:
    """Run the bounded Phase 1 Qwen3 and Metal smoke test."""

    model_path = config.model_path.expanduser().resolve(strict=True)
    if not model_path.is_file():
        raise ValueError(f"Model path is not a file: {model_path}")
    if platform.machine() != "arm64":
        raise RuntimeError(f"Expected ARM64 Python, got: {platform.machine()}")

    backend_init_started = time.perf_counter()
    system_info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace")
    gpu_offload_supported = bool(llama_cpp.llama_supports_gpu_offload())
    backend_cold_init_seconds = time.perf_counter() - backend_init_started
    if not gpu_offload_supported:
        raise RuntimeError("llama.cpp reports that GPU offload is unavailable")

    sampler = _MemorySampler()
    rss_before_load = sampler.current_rss_bytes()
    sampler.start()
    model: Llama | None = None

    try:
        load_started = time.perf_counter()
        model = Llama(
            model_path=str(model_path),
            n_gpu_layers=-1,
            n_ctx=config.n_ctx,
            n_batch=config.n_batch,
            n_threads=config.n_threads,
            n_threads_batch=config.n_threads,
            seed=config.seed,
            verbose=config.verbose,
        )
        model_load_after_backend_init_seconds = time.perf_counter() - load_started
        rss_after_load = sampler.current_rss_bytes()

        metadata = model.metadata or {}
        metadata_architecture = metadata.get("general.architecture")
        if not isinstance(metadata_architecture, str):
            metadata_architecture = None
        metadata_chat_template_present = isinstance(metadata.get("tokenizer.chat_template"), str)

        (
            streaming_text,
            streaming_cancel_verified,
            first_content_latency_seconds,
        ) = _stream_and_cancel(model, seed=config.seed)
        post_cancel_generation_verified = _post_cancel_generation(model, seed=config.seed)

        generation_started = time.perf_counter()
        raw_response = model.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "あなたはPhase 1の短い動作確認を行っています。",
                },
                {
                    "role": "user",
                    "content": "/no_think\n日本語で「Metal Smoke Test成功」と短く答えてください。",
                },
            ],
            max_tokens=config.max_tokens,
            temperature=0.0,
            seed=config.seed,
            stream=False,
        )
        response = cast(dict[str, Any], raw_response)
        total_generation_seconds = time.perf_counter() - generation_started
        generated_text = _choice_text(response).strip()
        usage = response.get("usage", {})
        completion_tokens_raw = usage.get("completion_tokens", 0)
        completion_tokens = (
            int(completion_tokens_raw) if isinstance(completion_tokens_raw, int) else 0
        )
        tokens_per_second = (
            completion_tokens / total_generation_seconds if total_generation_seconds > 0 else 0.0
        )

        stop_sequence_finish_reason = _stop_sequence_probe(model, seed=config.seed)

        success = all(
            (
                bool(generated_text),
                gpu_offload_supported,
                metadata_architecture == "qwen3",
                metadata_chat_template_present,
                streaming_cancel_verified,
                post_cancel_generation_verified,
                stop_sequence_finish_reason == "stop",
            )
        )
    finally:
        unload_started = time.perf_counter()
        if model is not None:
            model.close()
        model = None
        gc.collect()
        unload_seconds = time.perf_counter() - unload_started
        time.sleep(0.25)
        rss_after_unload = sampler.current_rss_bytes()
        sampler.stop()

    return MetalSmokeResult(
        success=success,
        python_version=platform.python_version(),
        machine=platform.machine(),
        gil_enabled=_gil_enabled(),
        llama_cpp_python_version=importlib.metadata.version("llama-cpp-python"),
        backend_system_info=system_info,
        gpu_offload_supported=gpu_offload_supported,
        requested_gpu_layers=-1,
        model_path=str(model_path),
        model_size_bytes=model_path.stat().st_size,
        backend_cold_init_seconds=round(backend_cold_init_seconds, 4),
        model_load_after_backend_init_seconds=round(model_load_after_backend_init_seconds, 4),
        first_content_latency_seconds=round(first_content_latency_seconds, 4),
        total_generation_seconds=round(total_generation_seconds, 4),
        unload_seconds=round(unload_seconds, 4),
        completion_tokens=completion_tokens,
        tokens_per_second=round(tokens_per_second, 4),
        generated_text=generated_text,
        streaming_text_before_cancel=streaming_text,
        streaming_cancel_verified=streaming_cancel_verified,
        post_cancel_generation_verified=post_cancel_generation_verified,
        stop_sequence_finish_reason=stop_sequence_finish_reason,
        rss_before_load_bytes=rss_before_load,
        rss_after_load_bytes=rss_after_load,
        peak_rss_bytes=sampler.peak_rss_bytes,
        rss_after_unload_bytes=rss_after_unload,
        metadata_architecture=metadata_architecture,
        metadata_chat_template_present=metadata_chat_template_present,
    )
