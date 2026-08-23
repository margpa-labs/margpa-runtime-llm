"""Opt-in Manual Load Evidence for RuntimeModelController against the real
Qwen3 GGUF artifact and Metal backend (Phase 6-B-WU-007).

Unlike tests/integration/test_qwen3_model_smoke.py (which drives the raw
llama.cpp adapter directly), this exercises the actual Phase 6 abstraction
stack end-to-end: DirectoryModelDefinitionRegistry -> LlamaCppRuntimeModelBackend
-> RuntimeModelController.begin_switch()/request_context_change() against a
real, loaded model. This is the first real-hardware evidence that the
Fake-only unit tests correctly model the real adapter's behavior.
"""

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.llama_cpp_backend import (
    LlamaCppRuntimeModelBackend,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import RuntimeState
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import (
    RuntimeModelSnapshot,
    compute_runtime_model_snapshot_digest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"
QWEN_ARTIFACT_SHA512 = (
    "f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3d"
    "d8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb"
)


class _AlwaysFreeAccessLease:
    """P6-CODEX-034 (Fifth Rework): replaces the retired `_NeverBusyGate` —
    mirrors the real `ModelAccessCoordinator`'s exclusive-lease Port."""

    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        return True

    def release_switch_lease(self, *, task_id: str) -> None:
        pass


def _empty_initial_snapshot() -> RuntimeModelSnapshot:
    """Placeholder pre-load Snapshot: no model bound yet (revision 0)."""
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key="none",
        role_bindings=(),
        artifact_identity="none",
        artifact_digest="0" * 128,
        backend_identity="none",
        runtime_state=RuntimeState.IDLE,
        loaded_context_size=0,
        current_max_new_tokens=256,
    )
    return RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key="none",
        role_bindings=(),
        artifact_identity="none",
        artifact_digest="0" * 128,
        backend_identity="none",
        runtime_state=RuntimeState.IDLE,
        loaded_context_size=0,
        model_native_context_limit=1,
        backend_context_limit=1,
        deployment_verified_context_limit=1,
        max_output_token_limit=256,
        current_max_new_tokens=256,
        last_transition_receipt=None,
    )


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6 model smoke requires Apple Silicon",
)
def test_runtime_model_controller_loads_the_real_qwen_artifact_and_resizes_context() -> None:
    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    qwen_definition = definitions.resolve(model_key=QWEN_MODEL_KEY)

    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    backend = LlamaCppRuntimeModelBackend(
        adapter=adapter,
        base_load_config=ModelLoadConfig(context_size=4096, gpu_layers=-1),
        default_max_new_tokens=256,
    )
    controller = RuntimeModelController(
        initial_snapshot=_empty_initial_snapshot(),
        backend=backend,
        access_lease=_AlwaysFreeAccessLease(),
        definitions=definitions,
    )

    try:
        initial = controller.snapshot()
        loaded = controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="smoke-load-1",
            target_definition=qwen_definition,
            requested_context_size=4096,
        )

        assert loaded.selected_model_key == QWEN_MODEL_KEY
        assert loaded.runtime_state is RuntimeState.ACTIVE
        assert loaded.loaded_context_size == 4096
        assert loaded.artifact_digest == QWEN_ARTIFACT_SHA512
        assert loaded.model_native_context_limit == qwen_definition.model.native_context_limit

        resized = controller.request_context_change(
            expected_revision=loaded.revision,
            expected_digest=loaded.digest_sha512,
            transition_id="smoke-resize-1",
            requested_context_size=2048,
        )

        assert resized.selected_model_key == QWEN_MODEL_KEY
        assert resized.loaded_context_size == 2048
        assert resized.runtime_state is RuntimeState.ACTIVE
    finally:
        backend.unload()
