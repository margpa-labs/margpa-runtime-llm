"""Fast integration checks that do not load the multi-gigabyte model."""

import platform

import pytest
from llama_cpp import llama_cpp


@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 1 local Metal profile requires Apple Silicon",
)
def test_llama_cpp_was_built_with_gpu_offload() -> None:
    assert llama_cpp.llama_supports_gpu_offload()
    system_info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace")
    assert "MTL" in system_info
