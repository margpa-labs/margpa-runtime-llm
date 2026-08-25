"""ModelBackendPort adapter wrapping the existing LlamaCppModelAdapter (Phase 6-B-WU-002).

`probe_capability` reports the statically-declared/deployment-verified capability
(no model need be loaded to compute it). `load` returns the actual allocation
separately as `loaded_context_size`; it never promotes that one allocation into a
larger deployment/hardware verification claim.
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
    ) -> None:
        self._adapter = adapter
        self._base_load_config = base_load_config

    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        declared = definition.model.native_context_limit
        deployment_verified = min(declared, self._base_load_config.context_size)
        max_output = max(1, deployment_verified - 1)
        return CapabilityProbeResult(
            native_context_limit=declared,
            # llama.cpp does not expose a separate lower Context ceiling for
            # this loaded GGUF. Keep the backend boundary distinct from the
            # currently allocated n_ctx; the deployment/hardware verified
            # boundary below is what limits this concrete profile.
            backend_context_limit=declared,
            deployment_verified_context_limit=deployment_verified,
            max_output_token_limit=max_output,
            capability_digest=compute_capability_digest(
                native=declared,
                backend=declared,
                deployment_verified=deployment_verified,
                max_output=max_output,
            ),
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        load_config = self._base_load_config.model_copy(update={"context_size": context_size})
        runtime_info = self._adapter.load(definition, load_config)
        # Capability is independent of the *current allocation*. Reporting
        # loaded_context_size as the backend/deployment maximum made a shrink
        # irreversible and advertised Native 32K/131K as an applicable input
        # even though this deployment was verified only to the profile's 8K.
        capability = self.probe_capability(definition=definition)
        return LoadedModelHandle(
            backend_identity=f"{runtime_info.backend_key}:{runtime_info.backend_version}",
            artifact_digest=runtime_info.artifact_digest.value,
            loaded_context_size=runtime_info.loaded_context_size,
            capability=capability,
        )

    def unload(self) -> None:
        self._adapter.unload()
