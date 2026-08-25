from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.model_backends.llama_cpp.repetition import (
    PathologicalRepetitionDetector,
    detect_pathological_repetition,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.stream import LlamaCppGenerationStream
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState


def test_short_repetition_and_normal_repeated_structure_do_not_trigger() -> None:
    assert detect_pathological_repetition("ha " * 20) is False
    assert (
        detect_pathological_repetition(
            "1. Check the source.\n2. Check the date.\n3. Check the author.\n" * 2
        )
        is False
    )


def test_long_exact_repeated_suffix_triggers_at_the_bounded_floor() -> None:
    block = "pathological repeated answer unit!!"
    assert len(block) == 35
    assert detect_pathological_repetition(block * 5) is False
    assert detect_pathological_repetition(block * 6) is True


def test_incremental_detector_catches_repetition_across_chunk_boundaries() -> None:
    detector = PathologicalRepetitionDetector()
    block = "This answer is repeating without adding value. "
    states = [detector.feed(fragment) for fragment in (block, block * 2, block * 3)]
    assert states[-1] is True


def test_stream_stops_with_typed_safe_failure_before_backend_terminal() -> None:
    block = "This answer is repeating without adding value. "
    native = iter(
        [{"choices": [{"delta": {"content": block}, "finish_reason": None}]} for _ in range(8)]
    )
    terminal_states: list[str] = []
    unavailable_states: list[str] = []
    stream = LlamaCppGenerationStream(
        generation_id="generation-1",
        request_id="request-1",
        model_key="main.test",
        native_stream=native,
        on_terminal=lambda: terminal_states.append("released"),
        fallback_prompt_tokens=1,
        completion_text_token_counter=len,
        repetition_detector=PathologicalRepetitionDetector(),
        on_pathological_output=lambda: unavailable_states.append("unavailable"),
    )

    with pytest.raises(InferenceError) as raised:
        list(stream)

    assert raised.value.code is InferenceErrorCode.GENERATION_FAILED
    assert raised.value.details["reason"] == "pathological_repetition_detected"
    assert terminal_states == ["released"]
    assert unavailable_states == ["unavailable"]


def test_adapter_circuit_breaker_survives_generation_terminal_cleanup(tmp_path: Path) -> None:
    adapter = LlamaCppModelAdapter(model_root=tmp_path)
    adapter._state = ModelLifecycleState.GENERATING

    adapter._mark_generation_unavailable()
    adapter._end_generation()

    assert adapter.state is ModelLifecycleState.FAILED
