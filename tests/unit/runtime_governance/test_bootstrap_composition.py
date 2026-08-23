"""Bootstrap composition: end-to-end wiring of Binder + Deterministic
Evaluator + Action Resolver against the real Reference Bundle
(P4-C-WU-002, P4-ACC-010, P4-GD-005, P4-CODEX-004 Rework)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    _ARGD_DAGD_SOURCE_ID,
    RuntimeGovernanceComposition,
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    PackageManifest,
    SourceEntry,
    sign_manifest,
)
from margpa_runtime_llm.modules.governance_definitions.ports import PackageLoadRequest
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    MAIN_MODEL_PRE_POINT_ID,
    STAGE_POST,
    STAGE_PRE,
    EvaluationMethod,
    ExecutionDescriptor,
    ExecutionState,
    RuntimeCapabilitySnapshot,
)

_DEFINITIONS_ROOT = Path(__file__).resolve().parents[3] / "definitions"


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor(descriptor_id: str = "argd.rule-1") -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id=descriptor_id,
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def test_load_reference_descriptors_returns_empty_without_error_when_root_is_none() -> None:
    result = load_reference_descriptors(
        definitions_root=None, capability=_capability(), authority=default_authority()
    )
    assert result.descriptors == ()
    assert result.state == "no_provider"
    assert result.reason_code is not None
    assert result.source_plan_id is None
    assert result.source_plan_digest_sha512 is None


def test_load_reference_descriptors_reads_the_real_bundle() -> None:
    result = load_reference_descriptors(
        definitions_root=_DEFINITIONS_ROOT, capability=_capability(), authority=default_authority()
    )
    assert result.state == "loaded"
    assert result.reason_code is None
    assert len(result.descriptors) > 0
    assert all(d.source_definition_id in {"argd", "dagd"} for d in result.descriptors)
    # P4-CODEX-008: a Binding with non-empty Descriptors must be traceable
    # back to a real Phase 3 Unbound Plan Identity, not a hardcoded None.
    assert result.source_plan_id is not None
    assert result.source_plan_id.startswith("plan-")
    assert result.source_plan_digest_sha512 is not None
    assert len(result.source_plan_digest_sha512) == 128


def test_load_reference_descriptors_source_plan_is_deterministic_for_the_same_bundle() -> None:
    first = load_reference_descriptors(
        definitions_root=_DEFINITIONS_ROOT, capability=_capability(), authority=default_authority()
    )
    second = load_reference_descriptors(
        definitions_root=_DEFINITIONS_ROOT, capability=_capability(), authority=default_authority()
    )
    assert first.source_plan_id == second.source_plan_id
    assert first.source_plan_digest_sha512 == second.source_plan_digest_sha512


def _build_argd_dagd_bundle(base: Path, *, source_bytes: bytes) -> Path:
    """Writes a minimal on-disk Definition Package whose single ARGD/DAGD
    Source is exactly `source_bytes`, correctly digested and signed —
    mirrors the real `definitions/` layout closely enough for
    `load_reference_descriptors()` to normalize/compile it for real."""

    root = base / "definitions"
    relative = "core_governance/argd_v0.3.1_en_dagd_v0.4.4_en.json"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(source_bytes)
    manifest = PackageManifest(
        package_id="valid-bundle-test",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=(
            SourceEntry(
                source_id=_ARGD_DAGD_SOURCE_ID,
                relative_path=f"definitions/{relative}",
                media_type="application/json",
                byte_length=len(source_bytes),
                content_digest_sha512=hashlib.sha512(source_bytes).hexdigest(),
                schema_id="combined_argd_dagd_v1",
                trusted_adapter_id="argd_dagd_combined_v1",
                logical_definition_ids=("argd", "dagd"),
            ),
        ),
        definition_entries=(
            DefinitionEntry(
                definition_id="argd",
                definition_version="1",
                display_name="ARGD",
                domain="reasoning_governance",
                source_id=_ARGD_DAGD_SOURCE_ID,
                source_object_pointer="$.argd.axiomatic_reasoning_governance_definition",
                extension_archetype="combined_argd_dagd",
            ),
            DefinitionEntry(
                definition_id="dagd",
                definition_version="1",
                display_name="DAGD",
                domain="reasoning_governance",
                source_id=_ARGD_DAGD_SOURCE_ID,
                source_object_pointer="$.dagd.declarative_ai_governance_definition",
                extension_archetype="combined_argd_dagd",
            ),
        ),
    )
    (root / "manifest.json").write_text(sign_manifest(manifest).model_dump_json(), encoding="utf-8")
    return root


def test_load_reference_descriptors_source_plan_changes_when_bundle_content_changes(
    tmp_path: Path,
) -> None:
    # P4-CODEX-008 Required Correction: a Bundle content change must
    # invalidate the old Source Plan/Binding — never a stale Cache Hit.
    original_bytes = (
        _DEFINITIONS_ROOT / "core_governance" / "argd_v0.3.1_en_dagd_v0.4.4_en.json"
    ).read_bytes()
    original_content = json.loads(original_bytes)
    modified_content = copy.deepcopy(original_content)
    argd_node = modified_content["argd"]["axiomatic_reasoning_governance_definition"]
    del argd_node["description"]
    modified_bytes = json.dumps(modified_content, ensure_ascii=False).encode("utf-8")

    original_root = _build_argd_dagd_bundle(tmp_path / "original", source_bytes=original_bytes)
    modified_root = _build_argd_dagd_bundle(tmp_path / "modified", source_bytes=modified_bytes)

    original_loaded = load_reference_descriptors(
        definitions_root=original_root, capability=_capability(), authority=default_authority()
    )
    modified_loaded = load_reference_descriptors(
        definitions_root=modified_root, capability=_capability(), authority=default_authority()
    )
    assert original_loaded.state == "loaded"
    assert modified_loaded.state == "loaded"
    assert original_loaded.source_plan_id is not None
    assert modified_loaded.source_plan_id is not None
    assert original_loaded.source_plan_digest_sha512 != modified_loaded.source_plan_digest_sha512
    assert len(original_loaded.descriptors) > 0
    assert len(modified_loaded.descriptors) > 0

    original_composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=original_loaded.descriptors,
        source_plan_id=original_loaded.source_plan_id,
        source_plan_digest_sha512=original_loaded.source_plan_digest_sha512,
    )
    modified_composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=modified_loaded.descriptors,
        source_plan_id=modified_loaded.source_plan_id,
        source_plan_digest_sha512=modified_loaded.source_plan_digest_sha512,
    )
    original_binding = original_composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    modified_binding = modified_composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    assert original_binding.executable is True
    assert modified_binding.executable is True
    assert original_binding.binding_digest_sha512 != modified_binding.binding_digest_sha512
    # A cache keyed by the old Binding's digest must miss for the new one.
    assert original_composition.plan_cache.get(modified_binding.binding_digest_sha512) is None


def test_composition_runs_off_observe_enforce_with_real_descriptors() -> None:
    loaded = load_reference_descriptors(
        definitions_root=_DEFINITIONS_ROOT, capability=_capability(), authority=default_authority()
    )
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=loaded.descriptors,
        descriptor_unavailable_reason_code=loaded.reason_code,
        source_plan_id=loaded.source_plan_id,
        source_plan_digest_sha512=loaded.source_plan_digest_sha512,
    )

    off_result = composition.point_runtime.invoke(
        invocation_id="inv-off",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="off",
        snapshot="an answer",
        binding=None,
        descriptors=composition.descriptors,
        budget=composition.budget,
    )
    assert off_result.execution_state is ExecutionState.NOT_EVALUATED

    observe_result = composition.point_runtime.invoke(
        invocation_id="inv-observe",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="",  # empty -> a real structural deviation
        binding=None,
        descriptors=composition.descriptors,
        budget=composition.budget,
    )
    assert observe_result.execution_state is ExecutionState.EVALUATED
    assert observe_result.executed_actions == ()
    assert any(d.detail_code == "empty_output" for d in observe_result.deviations)

    binding = composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    assert binding.executable is True
    enforce_result = composition.point_runtime.invoke(
        invocation_id="inv-enforce",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="enforce",
        snapshot="",
        binding=binding,
        descriptors=composition.descriptors,
        budget=composition.budget,
        resolve_actions=composition.resolver_for(
            point_id=MAIN_MODEL_POST_POINT_ID, stage=STAGE_POST, binding=binding
        ),
    )
    assert enforce_result.execution_state is ExecutionState.EVALUATED
    assert any(
        action.action_id == "reject_output" and action.executed
        for action in enforce_result.executed_actions
    )


def test_pre_point_stop_before_generation_is_scoped_to_pre() -> None:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(),),
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    binding = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    assert binding.executable is True
    result = composition.point_runtime.invoke(
        invocation_id="inv-pre",
        point_id=MAIN_MODEL_PRE_POINT_ID,
        stage=STAGE_PRE,
        mode="enforce",
        snapshot='{"total_chars": 1000000, "generation_config_fields": []}',
        binding=binding,
        descriptors=composition.descriptors,
        budget=composition.budget,
        resolve_actions=composition.resolver_for(
            point_id=MAIN_MODEL_PRE_POINT_ID, stage=STAGE_PRE, binding=binding
        ),
    )
    assert any(
        action.action_id == "stop_before_generation" and action.executed
        for action in result.executed_actions
    )


def test_enforce_with_zero_descriptors_is_unavailable_and_executes_nothing() -> None:
    # P4-CODEX-004 Rework: the Definitions-0 Baseline (P4-GD-005) must
    # never let a Core-only structural check fire in Enforce — this is
    # the direct Negative counterpart to the old (inverted) assumption
    # that Enforce could act on zero bound Descriptors.
    composition = RuntimeGovernanceComposition(capability=_capability())
    binding = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    assert binding.executable is False
    assert binding.unavailable_reason_code == "no_definitions"
    result = composition.point_runtime.invoke(
        invocation_id="inv-pre-empty",
        point_id=MAIN_MODEL_PRE_POINT_ID,
        stage=STAGE_PRE,
        mode="enforce",
        snapshot='{"total_chars": 1000000, "generation_config_fields": []}',
        binding=binding,
        descriptors=composition.descriptors,
        budget=composition.budget,
        resolve_actions=composition.resolver_for(
            point_id=MAIN_MODEL_PRE_POINT_ID, stage=STAGE_PRE, binding=binding
        ),
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.unavailable_reason_code == "no_definitions"
    assert result.executed_actions == ()


def test_binding_is_cached_across_repeated_binds() -> None:
    composition = RuntimeGovernanceComposition(capability=_capability())
    first = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    second = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    assert first == second
    assert composition.plan_cache.size() == 1


def test_rebind_capability_is_reflected_by_the_next_bind_point_call() -> None:
    """P6-CODEX-036 (Fifth Rework): before this fix, `capability` was set
    once in `__init__` and never updated — a Runtime Model Switch/Context
    Reload had no way to make Governance Binding reflect the new Model.
    `bind_point()` already reads `self.capability` fresh on every call (it
    is not cached at construction time), so `rebind_capability()` alone is
    sufficient to make the very next `bind_point()` call see the new
    value — proven here directly against the Binding it actually
    produces, not merely against the stored attribute."""
    composition = RuntimeGovernanceComposition(capability=_capability())
    original_binding = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    assert original_binding.capability_snapshot_digest_sha512 == _capability().digest_sha512

    switched_capability = RuntimeCapabilitySnapshot(
        model_key="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )
    composition.rebind_capability(capability=switched_capability)

    rebound_binding = composition.bind_point(point_id=MAIN_MODEL_PRE_POINT_ID)
    assert composition.capability == switched_capability
    assert rebound_binding.capability_snapshot_digest_sha512 == switched_capability.digest_sha512
    assert (
        rebound_binding.capability_snapshot_digest_sha512
        != original_binding.capability_snapshot_digest_sha512
    )


def test_load_reference_descriptors_returns_empty_when_no_manifest_exists(
    tmp_path: Path,
) -> None:
    # An existing, empty directory: `FilesystemDefinitionProvider` reports
    # `found=False` rather than raising — Phase 4 must degrade to zero
    # Descriptors here too, not just for a `None` root (P4-GD-005).
    result = load_reference_descriptors(
        definitions_root=tmp_path, capability=_capability(), authority=default_authority()
    )
    assert result.descriptors == ()
    assert result.state == "no_provider"


def test_load_reference_descriptors_returns_empty_for_an_invalid_bundle(
    tmp_path: Path,
) -> None:
    # A real on-disk Manifest that *references* the exact Phase 4 Source
    # ID, but whose Source bytes fail digest verification — the
    # "Invalid Bundle" Golden Matrix scenario (P4-G-WU-001). The failed
    # Source is isolated (Package as a whole still Validates, mirroring
    # Phase 3's Invalid-Sibling behavior), so `verified_source_json` never
    # contains this Source's content, and Phase 4 must fall back to zero
    # Descriptors with a Typed `invalid_bundle` state — distinct from
    # `no_provider` (P4-CODEX-004 Rework §5) — rather than fabricating or
    # crashing.
    root = tmp_path / "definitions"
    relative = "core_governance/argd_v0.3.1_en_dagd_v0.4.4_en.json"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"argd": {}, "dagd": {}}).encode()
    path.write_bytes(payload)

    manifest = PackageManifest(
        package_id="invalid-bundle-test",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=(
            SourceEntry(
                source_id=_ARGD_DAGD_SOURCE_ID,
                relative_path=f"definitions/{relative}",
                media_type="application/json",
                byte_length=len(payload),
                # Deliberately wrong digest -> fails verification ->
                # this Source is excluded from Verified Source content.
                content_digest_sha512=hashlib.sha512(b"tampered").hexdigest(),
                schema_id="combined_argd_dagd_v1",
                trusted_adapter_id="argd_dagd_combined_v1",
                logical_definition_ids=("argd", "dagd"),
            ),
        ),
        definition_entries=(
            DefinitionEntry(
                definition_id="argd",
                definition_version="1",
                display_name="ARGD",
                domain="reasoning_governance",
                source_id=_ARGD_DAGD_SOURCE_ID,
                source_object_pointer="$.argd",
                extension_archetype="combined_argd_dagd",
            ),
        ),
    )
    (root / "manifest.json").write_text(sign_manifest(manifest).model_dump_json(), encoding="utf-8")

    provider = FilesystemDefinitionProvider(root=root)
    provider_result = provider.load_package(PackageLoadRequest())
    # The Package as a whole survives (single-Source isolation, matching
    # Phase 3's Invalid-Sibling behavior) but this specific Source failed
    # digest verification and is excluded from Verified Source content.
    assert _ARGD_DAGD_SOURCE_ID not in provider_result.verified_source_json

    loaded = load_reference_descriptors(
        definitions_root=root, capability=_capability(), authority=default_authority()
    )
    assert loaded.descriptors == ()
    assert loaded.state == "invalid_bundle"
    assert loaded.reason_code is not None
    assert loaded.source_plan_id is None
    assert loaded.source_plan_digest_sha512 is None

    # The Composition itself stays fully operable across OFF/OBSERVE —
    # an Invalid Bundle never blocks Main Model Runtime — but ENFORCE
    # must be Unavailable with zero mutation, never a Core-only
    # structural check firing in its place (P4-CODEX-004 Rework).
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=loaded.descriptors,
        descriptor_unavailable_reason_code=loaded.reason_code,
        source_plan_id=loaded.source_plan_id,
        source_plan_digest_sha512=loaded.source_plan_digest_sha512,
    )
    binding = composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    assert binding.executable is False
    assert binding.unavailable_reason_code == loaded.reason_code
    result = composition.point_runtime.invoke(
        invocation_id="inv-invalid-bundle",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="enforce",
        snapshot="",
        binding=binding,
        descriptors=composition.descriptors,
        budget=composition.budget,
        resolve_actions=composition.resolver_for(
            point_id=MAIN_MODEL_POST_POINT_ID, stage=STAGE_POST, binding=binding
        ),
    )
    assert result.execution_state is ExecutionState.UNAVAILABLE
    assert result.executed_actions == ()

    # P4-CODEX-011 §1.1/Required Test 4: Observe now Binds too, and must
    # surface this Binding's own real `invalid_bundle` reason — never
    # collapse it to the generic `no_definitions` string — while still
    # never mutating Output.
    observe_binding = composition.bind_point(point_id=MAIN_MODEL_POST_POINT_ID)
    observe_result = composition.point_runtime.invoke(
        invocation_id="inv-invalid-bundle-observe",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage=STAGE_POST,
        mode="observe",
        snapshot="",
        binding=observe_binding,
        descriptors=composition.descriptors,
        budget=composition.budget,
    )
    assert observe_result.execution_state is ExecutionState.INACTIVE_NO_DEFINITIONS
    assert observe_result.unavailable_reason_code == loaded.reason_code
    assert observe_result.unavailable_reason_code != "no_definitions"
    assert observe_result.executed_actions == ()
