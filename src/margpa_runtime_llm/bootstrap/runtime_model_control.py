"""Composition root for Runtime Model Control (Phase 6-B-WU-006).

Wires the already-loaded Phase1Application's adapter/definition into a
RuntimeModelController without constructing a second, conflicting
LlamaCppModelAdapter bound to the same model_root.
"""

from collections.abc import Callable
from pathlib import Path

from margpa_runtime_llm.adapters.runtime_model_control.llama_cpp_backend import (
    LlamaCppRuntimeModelBackend,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError, InferenceErrorCode
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import (
    RoleBinding,
    RuntimeModelSnapshot,
    compute_runtime_model_snapshot_digest,
)

from .phase1_application import Phase1Application

DEFAULT_MODEL_REGISTRY_DIR = Path("config/models")


def build_runtime_model_controller(
    *,
    application: Phase1Application,
    model_access_coordinator: ModelAccessCoordinator,
    project_root: Path,
    model_registry_dir: Path | None = None,
    on_commit: Callable[[RuntimeModelSnapshot], None] | None = None,
) -> RuntimeModelController:
    runtime_info = application.service.runtime_info
    if runtime_info is None:
        raise InferenceError(
            code=InferenceErrorCode.MODEL_NOT_LOADED,
            safe_message="The model runtime information is unavailable.",
            model_key=application.definition.model_key,
        )

    registry_dir = model_registry_dir or (project_root / DEFAULT_MODEL_REGISTRY_DIR)
    definitions = DirectoryModelDefinitionRegistry(registry_dir=registry_dir)
    backend = LlamaCppRuntimeModelBackend(
        adapter=application.adapter,
        base_load_config=application.config.load,
    )
    capability = backend.probe_capability(definition=application.definition)
    backend_identity = f"{runtime_info.backend_key}:{runtime_info.backend_version}"
    artifact_digest = runtime_info.artifact_digest.value
    capability_digest = capability.capability_digest
    max_output_token_limit = min(
        capability.max_output_token_limit,
        max(1, runtime_info.loaded_context_size - 1),
    )
    current_max_new_tokens = min(
        application.config.generation.max_new_tokens,
        max_output_token_limit,
    )
    role_binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity=application.definition.model_key,
        artifact_digest=artifact_digest,
        backend_identity=backend_identity,
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=capability_digest,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key=application.definition.model_key,
        role_bindings=(role_binding,),
        artifact_identity=application.definition.model_key,
        artifact_digest=artifact_digest,
        backend_identity=backend_identity,
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=runtime_info.loaded_context_size,
        current_max_new_tokens=current_max_new_tokens,
    )
    initial_snapshot = RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key=application.definition.model_key,
        role_bindings=(role_binding,),
        artifact_identity=application.definition.model_key,
        artifact_digest=artifact_digest,
        backend_identity=backend_identity,
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=runtime_info.loaded_context_size,
        model_native_context_limit=application.definition.model.native_context_limit,
        backend_context_limit=capability.backend_context_limit,
        deployment_verified_context_limit=capability.deployment_verified_context_limit,
        max_output_token_limit=max_output_token_limit,
        current_max_new_tokens=current_max_new_tokens,
        last_transition_receipt=None,
    )
    return RuntimeModelController(
        initial_snapshot=initial_snapshot,
        backend=backend,
        access_lease=model_access_coordinator,
        definitions=definitions,
        on_commit=on_commit,
        default_max_new_tokens=application.config.generation.max_new_tokens,
    )
