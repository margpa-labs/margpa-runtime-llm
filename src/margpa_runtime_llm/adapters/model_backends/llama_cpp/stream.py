"""Model-independent streaming handle over a llama.cpp native iterator."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from types import TracebackType
from typing import Any

from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationChunk,
    GenerationTerminalState,
    GenerationTiming,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)

from .error_mapping import map_finish_reason, parse_token_usage, raise_mapped_backend_error
from .repetition import PathologicalRepetitionDetector


class LlamaCppGenerationStream:
    def __init__(
        self,
        *,
        generation_id: str,
        request_id: str,
        model_key: str,
        native_stream: Iterator[dict[str, Any]],
        on_terminal: Callable[[], None],
        fallback_prompt_tokens: int,
        completion_text_token_counter: Callable[[str], int],
        repetition_detector: PathologicalRepetitionDetector | None = None,
        on_pathological_output: Callable[[], None] | None = None,
    ) -> None:
        self._generation_id = generation_id
        self._request_id = request_id
        self._model_key = model_key
        self._native_stream = native_stream
        self._on_terminal = on_terminal
        self._fallback_prompt_tokens = fallback_prompt_tokens
        self._completion_text_token_counter = completion_text_token_counter
        self._terminal_state = GenerationTerminalState.ACTIVE
        self._iteration_started = False
        self._started = time.perf_counter()
        self._first_content_latency: float | None = None
        self._timing: GenerationTiming | None = None
        self._usage: TokenUsage | None = None
        self._completion_text_parts: list[str] = []
        self._repetition_detector = repetition_detector
        self._on_pathological_output = on_pathological_output

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return self._terminal_state

    @property
    def timing(self) -> GenerationTiming | None:
        return self._timing

    def __iter__(self) -> Iterator[GenerationChunk]:
        if self._iteration_started:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_REQUEST,
                safe_message="A generation stream can only be consumed once.",
                request_id=self._request_id,
                model_key=self._model_key,
            )
        self._iteration_started = True
        sequence = 0
        try:
            for payload in self._native_stream:
                choices = payload.get("choices")
                if not isinstance(choices, list) or not choices:
                    continue
                choice = choices[0]
                if not isinstance(choice, dict):
                    continue
                delta = choice.get("delta")
                text_delta = delta.get("content", "") if isinstance(delta, dict) else ""
                if not isinstance(text_delta, str):
                    text_delta = ""
                raw_finish_reason = choice.get("finish_reason")

                if text_delta:
                    if self._repetition_detector is not None and self._repetition_detector.feed(
                        text_delta
                    ):
                        self._close_native()
                        if self._on_pathological_output is not None:
                            self._on_pathological_output()
                        raise InferenceError(
                            code=InferenceErrorCode.GENERATION_FAILED,
                            safe_message=(
                                "The model produced an unstable repetitive response and was "
                                "stopped safely."
                            ),
                            retryable=True,
                            request_id=self._request_id,
                            model_key=self._model_key,
                            details={"reason": "pathological_repetition_detected"},
                        )
                    if self._first_content_latency is None:
                        self._first_content_latency = time.perf_counter() - self._started
                    self._completion_text_parts.append(text_delta)
                    yield GenerationChunk(
                        request_id=self._request_id,
                        sequence=sequence,
                        text_delta=text_delta,
                        is_final=False,
                    )
                    sequence += 1

                if raw_finish_reason is not None:
                    finish_reason, _ = map_finish_reason(raw_finish_reason)
                    self._usage = parse_token_usage(payload) or self._fallback_usage()
                    self._finish(GenerationTerminalState.COMPLETED)
                    yield GenerationChunk(
                        request_id=self._request_id,
                        sequence=sequence,
                        text_delta="",
                        is_final=True,
                        finish_reason=finish_reason,
                        usage=self._usage,
                    )
                    return

            if self._terminal_state is GenerationTerminalState.ACTIVE:
                raise InferenceError(
                    code=InferenceErrorCode.BACKEND_PROTOCOL_ERROR,
                    safe_message="The model backend ended a stream without a terminal chunk.",
                    request_id=self._request_id,
                    model_key=self._model_key,
                )
        except GeneratorExit:
            self.close()
            raise
        except InferenceError:
            self._finish(GenerationTerminalState.FAILED)
            raise
        except Exception as exc:
            self._finish(GenerationTerminalState.FAILED)
            raise_mapped_backend_error(
                "stream",
                exc,
                request_id=self._request_id,
                model_key=self._model_key,
            )

    def cancel(self) -> None:
        if self._terminal_state is not GenerationTerminalState.ACTIVE:
            return
        self._close_native()
        self._finish(GenerationTerminalState.CANCELLED)

    def close(self) -> None:
        if self._terminal_state is not GenerationTerminalState.ACTIVE:
            return
        self._close_native()
        self._finish(GenerationTerminalState.CLOSED_BY_CONSUMER)

    def __enter__(self) -> LlamaCppGenerationStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _fallback_usage(self) -> TokenUsage:
        """llama.cpp's streaming chat format never reports `usage` per-chunk
        (unlike its non-streaming response), so approximate it from the
        prompt token count already computed for the Fail-closed context
        check, plus a fresh tokenization of the accumulated completion text."""

        completion_text = "".join(self._completion_text_parts)
        completion_tokens = self._completion_text_token_counter(completion_text)
        return TokenUsage(
            prompt_tokens=self._fallback_prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=self._fallback_prompt_tokens + completion_tokens,
        )

    def _close_native(self) -> None:
        close = getattr(self._native_stream, "close", None)
        if callable(close):
            close()

    def _finish(self, terminal_state: GenerationTerminalState) -> None:
        if self._terminal_state is not GenerationTerminalState.ACTIVE:
            return
        self._terminal_state = terminal_state
        total_seconds = time.perf_counter() - self._started
        tokens_per_second = (
            self._usage.completion_tokens / total_seconds
            if self._usage is not None and total_seconds > 0
            else None
        )
        self._timing = GenerationTiming(
            first_content_latency_seconds=self._first_content_latency,
            total_generation_seconds=total_seconds,
            tokens_per_second=tokens_per_second,
        )
        self._on_terminal()
