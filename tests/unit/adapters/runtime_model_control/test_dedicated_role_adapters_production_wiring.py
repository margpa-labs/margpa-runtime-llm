"""P9-1-A-WU-002/WU-003/WU-004 (Phase 9-1): proves the dedicated Selene/
Qwen3Guard Production wiring -- Authority-granted Preflight -> Candidate
Load -> Strict Decode -> Evidence -- actually connects end to end, using a
Fixture ModelPort double in place of `LlamaCppModelAdapter`.

`test_dedicated_role_adapters.py` (P6-RR-L) proves the Authority gate itself
fails closed and never touches a real Backend. Every `authority_granted=True`
case there deliberately stops at `ModelDefinitionNotRegistered`, before a
real Backend/Service is ever constructed. This file is the complement: it
grants Authority only inside this Fixture-only Test scope (never in any
Production Composition Root -- `web_application.py` still hardcodes
`dedicated_model_authority_granted=False`, untouched by this package) and
proves the rest of the chain -- Candidate Load, `InferenceService` wiring,
Strict Prompt/Output Decode, Evidence -- is genuinely connected rather than
merely non-raising.

The final section (P9-1-A-WU-004) plugs the same real `SeleneRoleAdapter`
through the real, Preserved-As-built `RoleProviderLifecycleManager` (never
re-implemented here) to prove Mode ON Atomic Commit, a live Turn Lease, and
Mode OFF Unload compose correctly with a genuinely working dedicated Role --
`RoleProviderLifecycleManager`'s own existing Test suite already proves the
Protocol-level Atomic Commit/Lease/Failure-Recovery machinery is correct for
any `RoleProviderAdapterPort`; nothing here duplicates that."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from margpa_runtime_llm.adapters.guardrail_governance import (
    qwen3guard_manifest as _qwen3guard_manifest_module,
)
from margpa_runtime_llm.adapters.runtime_model_control import dedicated_role_adapters
from margpa_runtime_llm.adapters.runtime_model_control.dedicated_role_adapters import (
    ProductionRoleAdapterFactory,
    Qwen3GuardRoleAdapter,
    SeleneRoleAdapter,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    ModelDefinitionNotRegistered,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import DetectionOutcome
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import MODEL_REQUIRED_CAPABILITIES
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ModelArtifactDefinition,
    ModelBackendDefinition,
    ModelDefinition,
    ModelExpectedCapabilities,
    ModelMetadataDefinition,
    ModelOutputProtocolDefinition,
    ModelSourceDefinition,
    ModelVerificationDefinition,
    ThinkingOutputProtocolDefinition,
)
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationStage,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    QWEN3_GUARD,
    SELENE_JUDGE,
    ProviderSelectionController,
    RoleProviderLifecycleManager,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderRuntimeState,
)

_SHA512_FILLER = "a" * 128


def _make_model_definition(*, model_key: str, native_context_limit: int = 8192) -> ModelDefinition:
    return ModelDefinition(
        model_key=model_key,
        logical_role="dedicated",
        enabled=True,
        source=ModelSourceDefinition(
            provider="huggingface",
            distribution_repository="test-org/test-model",
            upstream_model="test-model",
        ),
        artifact=ModelArtifactDefinition(
            relative_path=Path(f"dedicated/{model_key}/gguf/{model_key}.gguf"),
            file_name=f"{model_key}.gguf",
            format="gguf",
            quantization="Q4_K_M",
            size_bytes=1,
            sha512=_SHA512_FILLER,
        ),
        backend=ModelBackendDefinition(backend_key="llama_cpp", required_version=">=0.3.0"),
        model=ModelMetadataDefinition(
            architecture="test-arch",
            native_context_limit=native_context_limit,
            chat_template_source="embedded",
        ),
        capabilities=ModelExpectedCapabilities(required_features=MODEL_REQUIRED_CAPABILITIES),
        verification=ModelVerificationDefinition(state="verified", provenance_complete=True),
        output_protocol=ModelOutputProtocolDefinition(
            thinking=ThinkingOutputProtocolDefinition(parser_key="plain_text_v1")
        ),
        definition_file_sha512=_SHA512_FILLER,
    )


class _FakeDefinitionResolver:
    def __init__(self, definitions: dict[str, ModelDefinition]) -> None:
        self._definitions = definitions

    def resolve(self, *, model_key: str) -> ModelDefinition:
        try:
            return self._definitions[model_key]
        except KeyError:
            raise ModelDefinitionNotRegistered(model_key=model_key) from None

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(self._definitions.values())


def _fake_model_port_class(*, generated_content: str) -> tuple[type, list[Any]]:
    """Builds a fresh `ModelPort`-shaped Fake class per Test, closing over
    the exact Decode payload this Test wants `generate()` to return, and a
    `created` list the Test can inspect afterwards. Never touches a real
    file or the `llama_cpp` library -- `model_root` is accepted (mirroring
    `LlamaCppModelAdapter`'s own constructor) but unused. Monkeypatched in
    place of `LlamaCppModelAdapter` inside the `dedicated_role_adapters`
    module -- `LlamaCppRuntimeModelBackend` itself is never patched: its
    `probe_capability()` is pure computation over the Definition/Load
    Config, and its `load()`/`unload()` only ever delegate to whichever
    Adapter it was constructed with, so wrapping this Fake is sufficient
    to keep every real file/library boundary untouched."""

    created: list[object] = []

    class _FakePort:
        def __init__(self, *, model_root: Path) -> None:
            self.model_root = model_root
            self._state = ModelLifecycleState.UNLOADED
            self._runtime_info: ModelRuntimeInfo | None = None
            self.generate_calls: list[GenerationRequest] = []
            self.unload_calls = 0
            created.append(self)

        @property
        def state(self) -> ModelLifecycleState:
            return self._state

        @property
        def runtime_info(self) -> ModelRuntimeInfo | None:
            return self._runtime_info

        def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
            capabilities = ModelCapabilities(
                features=MODEL_REQUIRED_CAPABILITIES,
                native_context_limit=definition.model.native_context_limit,
                loaded_context_size=config.context_size,
                supported_message_roles=frozenset(
                    {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
                ),
            )
            self._runtime_info = ModelRuntimeInfo(
                load_instance_id="fixture-load-1",
                model_key=definition.model_key,
                backend_key="fixture_backend",
                backend_version="0.0.0-fixture",
                model_architecture=definition.model.architecture,
                format=definition.artifact.format,
                quantization=definition.artifact.quantization,
                artifact_size_bytes=definition.artifact.size_bytes,
                artifact_digest=ModelDigest(value=definition.artifact.sha512),
                definition_file_sha512=definition.definition_file_sha512,
                loaded_context_size=config.context_size,
                effective_capabilities=capabilities,
                chat_template_source="fixture",
                chat_template_digest=ModelDigest(value="b" * 128),
                device="cpu",
                device_kind="cpu",
                acceleration_api="none",
                gpu_offload=False,
                gpu_offload_evidence=GpuOffloadEvidence(
                    supported=False,
                    requested=False,
                    observed=False,
                    observation_source="not_requested",
                ),
            )
            self._state = ModelLifecycleState.LOADED
            return self._runtime_info

        def unload(self) -> None:
            self.unload_calls += 1
            self._state = ModelLifecycleState.UNLOADED
            self._runtime_info = None

        def capabilities(self) -> ModelCapabilities:
            assert self._runtime_info is not None
            return self._runtime_info.effective_capabilities

        def generate(
            self, request: GenerationRequest, *, cancellation: object | None = None
        ) -> GenerationResult:
            del cancellation
            self.generate_calls.append(request)
            assert self._runtime_info is not None
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content=generated_content,
                finish_reason=FinishReason.STOP,
                timing=GenerationTiming(total_generation_seconds=0.001),
                runtime_info=self._runtime_info.reference(),
            )

    return _FakePort, created


# ---------------------------------------------------------------------------
# Selene
# ---------------------------------------------------------------------------


def _selene_request() -> SemanticEvaluationRequest:
    criterion = SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512=_SHA512_FILLER,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512=_SHA512_FILLER,
        instruction="Do not contradict cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )
    frozen = freeze_semantic_turn(
        request_id="p9-1-a-wiring-selene",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=SELENE_JUDGE,
        active_provider=SELENE_JUDGE,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    return SemanticEvaluationRequest(
        snapshot=frozen.snapshot,
        stage="post",
        user_input="QUERY SENTINEL",
        candidate_answer="CANDIDATE SENTINEL",
        evidence_context=("REFERENCE SENTINEL",),
    )


def _write_selene_manifest(tmp_path: Path) -> Path:
    template = (
        "Query:\n{{query}}\nCandidate:\n{{candidate}}\nReference:\n{{reference}}\n"
        "Criteria:\n{{criteria}}\nSchema:\n{{response_schema}}\n"
    )
    template_path = tmp_path / "official-fixture.txt"
    template_path.write_text(template, encoding="utf-8")
    manifest_path = tmp_path / "selene-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "provider_id": SELENE_JUDGE,
                "template_type": "verified_test_fixture",
                "upstream_repository_url": "https://example.invalid/fixture",
                "upstream_revision": "f" * 40,
                "template_file": template_path.name,
                "template_sha512": hashlib.sha512(template.encode()).hexdigest(),
                "retrieval_status": "verified_test_fixture_only",
                "verified_official_copy": True,
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


def _write_unresolved_selene_manifest(tmp_path: Path) -> Path:
    manifest_path = tmp_path / "selene-manifest-unresolved.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "provider_id": SELENE_JUDGE,
                "template_type": "official_selene_prompt_template_unresolved",
                "upstream_repository_url": "https://example.invalid/unavailable",
                "upstream_revision": None,
                "template_file": None,
                "template_sha512": None,
                "retrieval_status": "unavailable_network_prohibited_by_exact_resume_authority",
                "verified_official_copy": False,
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


def _selene_decode_output() -> str:
    return json.dumps(
        {
            "recommendation": "accept",
            "confidence": 0.93,
            "reasoning": "fixture",
            "criterion_results": [
                {
                    "criterion_id": "semantic.argd.evidence.1",
                    "disposition": "pass",
                    "confidence": 0.91,
                    "reason_code": "fixture_result",
                    "evidence_refs": ["REFERENCE SENTINEL"],
                }
            ],
        }
    )


def test_selene_authority_granted_preflight_load_and_evaluate_wire_correctly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P9-1-A-WU-002: with Authority granted and a Fixture Backend standing
    in for the real (Project-Root-external) Artifact Load, the whole
    Candidate Load -> Strict Decode -> Inference -> Evidence chain that
    `SeleneRoleAdapter` wires must actually work -- not merely construct
    without raising."""
    definition = _make_model_definition(model_key=SELENE_JUDGE)
    fake_port_class, _created = _fake_model_port_class(generated_content=_selene_decode_output())
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_port_class)
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_FakeDefinitionResolver({SELENE_JUDGE: definition}),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(context_size=4096),
        authority_granted=True,
        prompt_manifest_path=_write_selene_manifest(tmp_path),
    )
    ready, reason = adapter.preflight()
    assert ready is True
    assert reason is None
    assert adapter.semantic_evaluator is None  # not constructed until load()

    adapter.load()
    assert adapter.semantic_evaluator is not None

    response = adapter.semantic_evaluator.evaluate(request=_selene_request())
    assert response.provider_state is SemanticProviderState.ACTIVE
    assert response.provider_id == SELENE_JUDGE
    assert response.results[0].disposition is SemanticCriterionDisposition.PASS

    adapter.unload()
    assert adapter.semantic_evaluator is None
    assert _created[0].unload_calls == 1


def test_selene_preflight_fails_when_prompt_contract_is_unresolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    definition = _make_model_definition(model_key=SELENE_JUDGE)
    fake_port_class, _created = _fake_model_port_class(generated_content=_selene_decode_output())
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_port_class)
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_FakeDefinitionResolver({SELENE_JUDGE: definition}),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(context_size=4096),
        authority_granted=True,
        prompt_manifest_path=_write_unresolved_selene_manifest(tmp_path),
    )
    ready, reason = adapter.preflight()
    assert ready is False
    assert reason == "selene_prompt_contract_unavailable:SelenePromptUnavailable"
    assert adapter.semantic_evaluator is None


def test_selene_candidate_load_binds_to_configured_context_size_not_native_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P9-1-A-WU-001/002: the shared Preflight Contract's Digest/
    Quantization/Backend/Hardware probe is informational at Preflight time
    (a Definition claiming more Native Context than this deployment's
    `ModelLoadConfig.context_size` still clears Preflight), but the actual
    Candidate Load stays bound to the configured `context_size` -- proving
    the Preflight Contract's output and the real Load are not silently
    decoupled."""
    definition = _make_model_definition(model_key=SELENE_JUDGE, native_context_limit=32768)
    fake_port_class, _created = _fake_model_port_class(generated_content=_selene_decode_output())
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_port_class)
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_FakeDefinitionResolver({SELENE_JUDGE: definition}),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(context_size=4096),
        authority_granted=True,
        prompt_manifest_path=_write_selene_manifest(tmp_path),
    )
    ready, _reason = adapter.preflight()
    assert ready is True
    adapter.load()
    assert adapter.semantic_evaluator is not None
    runtime_info = adapter.semantic_evaluator.inference_service.runtime_info
    assert runtime_info is not None
    assert runtime_info.loaded_context_size == 4096


# ---------------------------------------------------------------------------
# Qwen3Guard
# ---------------------------------------------------------------------------


def _write_qwen3guard_manifest(tmp_path: Path) -> Path:
    assert QWEN3_GUARD == _qwen3guard_manifest_module._EXPECTED_PROVIDER_ID
    category_mapping = {
        label: label.lower().replace(" ", "_").replace("&", "and")
        for label in _qwen3guard_manifest_module._EXPECTED_CATEGORY_UNION
    }
    manifest = {
        "schema_version": "1",
        "provider_id": QWEN3_GUARD,
        "label_schema_id": _qwen3guard_manifest_module._EXPECTED_LABEL_SCHEMA_ID,
        "verified_official_contract": True,
        "retrieval_status": "test_fixture",
        "huggingface_source": {
            "repository": _qwen3guard_manifest_module._OFFICIAL_HUGGINGFACE_REPOSITORY,
            "source_url": "https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B",
            "exact_revision": "a" * 40,
            "source_file": "tokenizer_config.json",
            "source_sha512": "a" * 128,
        },
        "github_source": {
            "repository": _qwen3guard_manifest_module._OFFICIAL_GITHUB_REPOSITORY,
            "source_url": "https://github.com/QwenLM/Qwen3Guard",
            "exact_revision": "d" * 40,
            "source_file": "README.md",
            "source_sha512": "e" * 128,
        },
        "input_context_categories": list(
            _qwen3guard_manifest_module._EXPECTED_INPUT_CONTEXT_CATEGORIES
        ),
        "output_candidate_categories": list(
            _qwen3guard_manifest_module._EXPECTED_OUTPUT_CANDIDATE_CATEGORIES
        ),
        "category_id_mapping": category_mapping,
    }
    manifest_path = tmp_path / "qwen3guard-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_qwen3guard_authority_granted_preflight_load_and_classify_wire_correctly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P9-1-A-WU-003: mirrors the Selene proof above for the dedicated
    Qwen3Guard Role -- Authority-granted Preflight -> Candidate Load ->
    Strict Line-Protocol Decode -> Evidence must actually connect, and the
    Artifact Digest the Preflight Contract resolved must reach the
    classification Evidence unchanged."""
    definition = _make_model_definition(model_key=QWEN3_GUARD)
    fake_port_class, created = _fake_model_port_class(
        generated_content="Safety: Safe\nCategories: None"
    )
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_port_class)
    adapter = Qwen3GuardRoleAdapter(
        provider_id=QWEN3_GUARD,
        definitions=_FakeDefinitionResolver({QWEN3_GUARD: definition}),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(context_size=4096),
        authority_granted=True,
        contract_manifest_path=_write_qwen3guard_manifest(tmp_path),
    )
    ready, reason = adapter.preflight()
    assert ready is True
    assert reason is None
    assert adapter.guard_adapter is None  # not constructed until load()

    adapter.load()
    assert adapter.guard_adapter is not None

    observation = adapter.guard_adapter.classify(content="hello")
    assert observation.model_id == QWEN3_GUARD
    assert observation.raw_signal is DetectionOutcome.CLEAR
    assert observation.artifact_digest_sha512 == _SHA512_FILLER

    adapter.unload()
    assert adapter.guard_adapter is None
    assert created[0].unload_calls == 1


# ---------------------------------------------------------------------------
# Lifecycle composition (P9-1-A-WU-004)
# ---------------------------------------------------------------------------


def test_selene_role_adapter_composes_with_the_real_lifecycle_manager(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P9-1-A-WU-004: Mode ON Candidate Preflight/Load, Atomic Commit, a
    live Turn Lease, and Mode OFF Unload must all compose correctly when
    `RoleProviderLifecycleManager` (Preserved As-built, unmodified) is
    driving a genuinely-working `SeleneRoleAdapter` rather than the generic
    `_FakeAdapter` its own unit suite uses. `RoleProviderLifecycleManager`'s
    own tests already prove the Atomic Commit/Lease/Failure-Recovery
    machinery is correct for any `RoleProviderAdapterPort` -- this proves
    the dedicated Selene Adapter this package wired is a genuine one."""
    definition = _make_model_definition(model_key=SELENE_JUDGE)
    fake_port_class, created = _fake_model_port_class(generated_content=_selene_decode_output())
    monkeypatch.setattr(dedicated_role_adapters, "LlamaCppModelAdapter", fake_port_class)
    factory = ProductionRoleAdapterFactory(
        definitions=_FakeDefinitionResolver({SELENE_JUDGE: definition}),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(context_size=4096),
        runtime_model_control_ref=[None],
        dedicated_model_authority_granted=True,
        selene_prompt_manifest_path=_write_selene_manifest(tmp_path),
        qwen3guard_contract_manifest_path=tmp_path / "unused-qwen3guard-manifest.json",
    )
    manager = RoleProviderLifecycleManager(
        selections=ProviderSelectionController(), factory=factory
    )

    snapshot = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in snapshot.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.ACTIVE
    assert judge.active_provider == SELENE_JUDGE
    active = manager.active_adapter(role=ModelRole.JUDGE)
    assert isinstance(active, SeleneRoleAdapter)
    assert active.semantic_evaluator is not None

    lease = manager.begin_turn(role=ModelRole.JUDGE)
    response = active.semantic_evaluator.evaluate(request=_selene_request())
    assert response.provider_state is SemanticProviderState.ACTIVE
    manager.end_turn(lease)

    pending = manager.deactivate(role=ModelRole.JUDGE)
    pending_judge = next(item for item in pending.selections if item.role is ModelRole.JUDGE)
    assert pending_judge.state is ProviderRuntimeState.CONFIGURED
    assert active.semantic_evaluator is None
    assert created[0].unload_calls == 1
