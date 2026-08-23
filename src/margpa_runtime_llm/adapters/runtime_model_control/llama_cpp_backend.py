"""ModelBackendPort adapter wrapping the existing LlamaCppModelAdapter (Phase 6-B-WU-002).

`probe_capability` reports the statically-declared/deployment-configured capability
(no model need be loaded to compute it); `load` reports the actually-measured
capability from the real llama.cpp runtime after a successful load, matching
Architecture 3.2's "Capability実測照合" step.
"""

from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.runtime_model_control.ports import (
    CapabilityProbeResult,
    LoadedModelHandle,
)

from ...modules.runtime_model_control.domain.canonicalization import runtime_model_snapshot_digest
from ..model_backends.llama_cpp.adapter import LlamaCppModelAdapter


def compute_capability_digest(
    *, native: int, backend: int, deployment_verified: int, max_output: int
) -> str:
    return runtime_model_snapshot_digest(
        payload={
            "native_context_limit": native,
            "backend_context_limit": backend,
            "deployment_verified_context_limit": deployment_verified,
            "max_output_token_limit": max_output,
        }
    )


class LlamaCppRuntimeModelBackend:
    """Owns one `LlamaCppModelAdapter` instance (one loaded model at a time, as today)."""

    def __init__(
        self,
        *,
        adapter: LlamaCppModelAdapter,
        base_load_config: ModelLoadConfig,
        default_max_new_tokens: int,
    ) -> None:
        self._adapter = adapter
        self._base_load_config = base_load_config
        self._default_max_new_tokens = default_max_new_tokens

    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        declared = definition.model.native_context_limit
        deployment_verified = min(declared, self._base_load_config.context_size)
        return CapabilityProbeResult(
            native_context_limit=declared,
            backend_context_limit=declared,
            deployment_verified_context_limit=deployment_verified,
            max_output_token_limit=self._default_max_new_tokens,
            capability_digest=compute_capability_digest(
                native=declared,
                backend=declared,
                deployment_verified=deployment_verified,
                max_output=self._default_max_new_tokens,
            ),
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        load_config = self._base_load_config.model_copy(update={"context_size": context_size})
        runtime_info = self._adapter.load(definition, load_config)
        deployment_verified = min(runtime_info.loaded_context_size, context_size)
        capability = CapabilityProbeResult(
            native_context_limit=definition.model.native_context_limit,
            backend_context_limit=runtime_info.loaded_context_size,
            deployment_verified_context_limit=deployment_verified,
            max_output_token_limit=self._default_max_new_tokens,
            capability_digest=compute_capability_digest(
                native=definition.model.native_context_limit,
                backend=runtime_info.loaded_context_size,
                deployment_verified=deployment_verified,
                max_output=self._default_max_new_tokens,
            ),
        )
        return LoadedModelHandle(
            backend_identity=f"{runtime_info.backend_key}:{runtime_info.backend_version}",
            artifact_digest=runtime_info.artifact_digest.value,
            loaded_context_size=runtime_info.loaded_context_size,
            capability=capability,
        )

    def unload(self) -> None:
        self._adapter.unload()
