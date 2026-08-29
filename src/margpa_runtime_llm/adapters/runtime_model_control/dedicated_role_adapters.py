"""Production `RoleAdapterFactoryPort` for dedicated Guard/Judge providers
(P6-RR-L, Phase 6 Production Wiring Delta).

Replaces `UnavailableRoleAdapterFactory` for Selene (Judge) and Qwen3Guard
(Guard): these two roles are backed by their own, independently
loaded/unloaded `LlamaCppRuntimeModelBackend`, never by unloading or
reusing Main's own backend. An explicit Main-model Judge selection
(`main.qwen3-4b-q4-k-m` / `main.deepseek-r1-0528-qwen3-8b-q4-k-m` chosen
for the JUDGE role) is handled separately by `MainSharedJudgeRoleAdapter`,
which reuses Main's already-loaded `InferenceService` and never loads a
second concurrent copy of a Main-sized model.

Two independent Authority gates apply before any real Selene/Qwen3Guard
Artifact is touched (Base Exact Handoff §8.1, P6-RR-DELTA §8):

- `dedicated_model_authority_granted`: a human-issued Exact Model
  Authority Receipt for the dedicated Artifact path/backend Load. Absent
  by default; this module never infers it from Capability or Permission
  Mode. When absent, `preflight()` returns `False,
  "dedicated_model_authority_unavailable"` *before* touching the
  Artifact's resolved (Project-Root-external, symlinked) path in any way
  — no stat, no digest read, no Load.
- Official Contract Provenance (Selene prompt template / Qwen3Guard
  category contract): independently gated by each adapter's own checked-in
  Manifest — Selene's `verified_official_copy` (`SelenePromptManifest`,
  still `False` pending Network Authority for that specific Artifact) and
  Qwen3Guard's `verified_official_contract` (`Qwen3GuardManifest`, `True`
  as of P6-RR-R23 — Read-only Network Authority for Qwen's own official
  Hugging Face/GitHub Repositories was granted for that specific Package,
  see `config/guardrail/qwen3guard/manifest.json`). A granted Model
  Authority does not imply a granted Network Authority, or vice versa.
"""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.evaluation.selene import (
    SelenePromptAdapter,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_adapter import (
    Qwen3GuardGenAdapter,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderOption,
)
from margpa_runtime_llm.modules.runtime_model_control.ports import (
    LoadedModelHandle,
    ModelDefinitionResolverPort,
)

from .llama_cpp_backend import LlamaCppRuntimeModelBackend
from .model_definition_registry import ModelDefinitionNotRegistered
from .unavailable_role_adapters import UnavailableRoleProviderAdapter

_DEDICATED_UNAVAILABLE_REASON = "dedicated_model_authority_unavailable"


class SeleneRoleAdapter:
    """`RoleProviderAdapterPort` for the dedicated Selene Judge."""

    def __init__(
        self,
        *,
        provider_id: str,
        definitions: ModelDefinitionResolverPort,
        model_root: Path,
        load_config: ModelLoadConfig,
        authority_granted: bool,
        prompt_manifest_path: Path,
    ) -> None:
        self._provider_id = provider_id
        self._definitions = definitions
        self._model_root = model_root
        self._load_config = load_config
        self._authority_granted = authority_granted
        self._prompt_manifest_path = prompt_manifest_path
        self._llama_adapter: LlamaCppModelAdapter | None = None
        self._backend: LlamaCppRuntimeModelBackend | None = None
        self._pending_definition: ModelDefinition | None = None
        self._loaded_handle: LoadedModelHandle | None = None
        self.semantic_evaluator: SeleneSemanticEvaluator | None = None

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def preflight(self) -> tuple[bool, str | None]:
        if not self._authority_granted:
            return False, _DEDICATED_UNAVAILABLE_REASON
        try:
            definition = self._definitions.resolve(model_key=self._provider_id)
        except ModelDefinitionNotRegistered:
            return False, "dedicated_model_definition_not_registered"
        llama_adapter = LlamaCppModelAdapter(model_root=self._model_root)
        backend = LlamaCppRuntimeModelBackend(
            adapter=llama_adapter, base_load_config=self._load_config
        )
        try:
            backend.probe_capability(definition=definition)
        except Exception as exc:
            return False, f"capability_probe_failed:{type(exc).__name__}"
        self._llama_adapter = llama_adapter
        self._backend = backend
        self._pending_definition = definition
        return True, None

    def load(self) -> None:
        if self._backend is None or self._pending_definition is None or self._llama_adapter is None:
            raise RuntimeError("preflight must succeed before load")
        self._loaded_handle = self._backend.load(
            definition=self._pending_definition,
            context_size=self._load_config.context_size,
        )
        inference_service = InferenceService(port=self._llama_adapter)
        self.semantic_evaluator = SeleneSemanticEvaluator(
            service=inference_service,
            model_key=self._provider_id,
            prompt_adapter=SelenePromptAdapter(manifest_path=self._prompt_manifest_path),
        )

    def unload(self) -> None:
        if self._backend is not None:
            self._backend.unload()
        self.semantic_evaluator = None
        self._backend = None
        self._llama_adapter = None
        self._pending_definition = None


class Qwen3GuardRoleAdapter:
    """`RoleProviderAdapterPort` for the dedicated Qwen3Guard-Gen Guard."""

    def __init__(
        self,
        *,
        provider_id: str,
        definitions: ModelDefinitionResolverPort,
        model_root: Path,
        load_config: ModelLoadConfig,
        authority_granted: bool,
        contract_manifest_path: Path,
    ) -> None:
        self._provider_id = provider_id
        self._definitions = definitions
        self._model_root = model_root
        self._load_config = load_config
        self._authority_granted = authority_granted
        self._contract_manifest_path = contract_manifest_path
        self._llama_adapter: LlamaCppModelAdapter | None = None
        self._backend: LlamaCppRuntimeModelBackend | None = None
        self._pending_definition: ModelDefinition | None = None
        self._loaded_handle: LoadedModelHandle | None = None
        self.guard_adapter: Qwen3GuardGenAdapter | None = None

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def preflight(self) -> tuple[bool, str | None]:
        if not self._authority_granted:
            return False, _DEDICATED_UNAVAILABLE_REASON
        try:
            definition = self._definitions.resolve(model_key=self._provider_id)
        except ModelDefinitionNotRegistered:
            return False, "dedicated_model_definition_not_registered"
        llama_adapter = LlamaCppModelAdapter(model_root=self._model_root)
        backend = LlamaCppRuntimeModelBackend(
            adapter=llama_adapter, base_load_config=self._load_config
        )
        try:
            backend.probe_capability(definition=definition)
        except Exception as exc:
            return False, f"capability_probe_failed:{type(exc).__name__}"
        self._llama_adapter = llama_adapter
        self._backend = backend
        self._pending_definition = definition
        return True, None

    def load(self) -> None:
        if self._backend is None or self._pending_definition is None or self._llama_adapter is None:
            raise RuntimeError("preflight must succeed before load")
        self._loaded_handle = self._backend.load(
            definition=self._pending_definition,
            context_size=self._load_config.context_size,
        )
        inference_service = InferenceService(port=self._llama_adapter)
        self.guard_adapter = Qwen3GuardGenAdapter(
            service=inference_service,
            model_id=self._provider_id,
            artifact_digest_sha512=self._loaded_handle.artifact_digest,
            manifest_path=self._contract_manifest_path,
        )

    def unload(self) -> None:
        if self._backend is not None:
            self._backend.unload()
        self.guard_adapter = None
        self._backend = None
        self._llama_adapter = None
        self._pending_definition = None


class MainSharedJudgeRoleAdapter:
    """`RoleProviderAdapterPort` for an explicit Main-model Judge selection
    (`main.qwen3-4b-q4-k-m` / `main.deepseek-r1-0528-qwen3-8b-q4-k-m` chosen
    as the JUDGE role's Provider).

    Never loads a second concurrent copy of a Main-sized model. Activation
    only succeeds while Main's own `RuntimeModelController` is *currently*
    running exactly this `provider_id` as its `selected_model_key`
    (P6-GOV-018 Scenario A/§7.6: an Option that cannot presently activate
    must fail with an Exact Reason, never silently execute a different
    model under the requested Identity). `load`/`unload` are no-ops —
    Main's own lifecycle, not this Role's, owns the underlying Load.

    `runtime_model_control_ref` is the same one-element mutable-box idiom
    `web_application.py` already uses for `RuntimeModelController` (built
    only after Role Provider Selection/Lifecycle, but read only much later
    at real Turn/Activation time, never during bootstrap itself)."""

    def __init__(
        self,
        *,
        provider_id: str,
        runtime_model_control_ref: list[RuntimeModelController | None],
    ) -> None:
        self._provider_id = provider_id
        self._runtime_model_control_ref = runtime_model_control_ref

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def preflight(self) -> tuple[bool, str | None]:
        controller = self._runtime_model_control_ref[0]
        if controller is None:
            return False, "main_runtime_model_control_unavailable"
        snapshot = controller.snapshot()
        if snapshot.selected_model_key != self._provider_id:
            return False, "main_model_mismatch_requires_main_switch"
        return True, None

    def load(self) -> None:
        return None

    def unload(self) -> None:
        return None


class ProductionRoleAdapterFactory:
    """`RoleAdapterFactoryPort`: dispatches Selene/Qwen3Guard to their own
    dedicated backend, an explicit Main-model Judge selection to Main's
    already-loaded runtime, and anything else registered-but-unhandled to
    the same fail-closed `UnavailableRoleProviderAdapter` the previous
    blanket Factory used (defensive default; every `ProviderOption` the
    Registry actually exposes today is one of the three cases above)."""

    def __init__(
        self,
        *,
        definitions: ModelDefinitionResolverPort,
        model_root: Path,
        load_config: ModelLoadConfig,
        runtime_model_control_ref: list[RuntimeModelController | None],
        dedicated_model_authority_granted: bool = False,
        selene_prompt_manifest_path: Path,
        qwen3guard_contract_manifest_path: Path,
    ) -> None:
        self._definitions = definitions
        self._model_root = model_root
        self._load_config = load_config
        self._runtime_model_control_ref = runtime_model_control_ref
        self._authority_granted = dedicated_model_authority_granted
        self._selene_prompt_manifest_path = selene_prompt_manifest_path
        self._qwen3guard_contract_manifest_path = qwen3guard_contract_manifest_path

    def create(
        self, *, role: ModelRole, option: ProviderOption
    ) -> (
        SeleneRoleAdapter
        | Qwen3GuardRoleAdapter
        | MainSharedJudgeRoleAdapter
        | UnavailableRoleProviderAdapter
    ):
        if option.provider_id == SELENE_JUDGE:
            return SeleneRoleAdapter(
                provider_id=option.provider_id,
                definitions=self._definitions,
                model_root=self._model_root,
                load_config=self._load_config,
                authority_granted=self._authority_granted,
                prompt_manifest_path=self._selene_prompt_manifest_path,
            )
        if option.provider_id == QWEN3_GUARD:
            return Qwen3GuardRoleAdapter(
                provider_id=option.provider_id,
                definitions=self._definitions,
                model_root=self._model_root,
                load_config=self._load_config,
                authority_granted=self._authority_granted,
                contract_manifest_path=self._qwen3guard_contract_manifest_path,
            )
        if role is ModelRole.JUDGE and option.provider_id in (QWEN_MAIN, DEEPSEEK_MAIN):
            return MainSharedJudgeRoleAdapter(
                provider_id=option.provider_id,
                runtime_model_control_ref=self._runtime_model_control_ref,
            )
        return UnavailableRoleProviderAdapter(
            provider_id=option.provider_id,
            reason="dedicated_provider_not_registered_in_production_factory",
        )


__all__ = [
    "MainSharedJudgeRoleAdapter",
    "ProductionRoleAdapterFactory",
    "Qwen3GuardRoleAdapter",
    "SeleneRoleAdapter",
]
