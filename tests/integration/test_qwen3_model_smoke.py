"""Opt-in test for the local Qwen3 GGUF artifact and Metal backend."""

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.metal_smoke import (
    MetalSmokeConfig,
    run_metal_smoke,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 1 model smoke requires Apple Silicon",
)
def test_qwen3_model_load_generation_stop_and_unload() -> None:
    if not MODEL_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {MODEL_PATH}")

    result = run_metal_smoke(
        MetalSmokeConfig(
            model_path=MODEL_PATH,
            max_tokens=48,
            verbose=False,
        )
    )

    assert result.success
    assert result.llama_cpp_python_version == "0.3.34"
    assert result.gpu_offload_supported
    assert "MTL" in result.backend_system_info
    assert result.metadata_architecture == "qwen3"
    assert result.metadata_chat_template_present
    assert result.first_content_latency_seconds > 0
    assert result.stop_sequence_finish_reason == "stop"
