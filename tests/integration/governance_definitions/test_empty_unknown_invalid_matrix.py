"""End-to-end Empty/Unknown/Invalid Compile Matrix (P3-E-WU-003):
Provider -> verify -> resolve -> normalize -> compile, across scenarios,
with the Main Runtime (this whole pipeline) never raising uncaught."""

from __future__ import annotations

import json
from pathlib import Path

from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import LocalJsonlEvidenceStore
from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.adapters.governance_definitions.reference_bundle_adapters import (
    ArgdDagdCombinedAdapter,
    CdogdAdapter,
    CommonDomainExtensionAdapter,
)
from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    AdapterDescriptor,
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.application import (
    EmptyDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    CompilerInput,
    DefinitionState,
    PackageState,
    ProviderState,
    compile_plan,
    digest_ir,
    resolve_definition_states,
)
from margpa_runtime_llm.modules.governance_definitions.ports import PackageLoadRequest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"

_CAP_DIGEST = "a" * 128
_AUTH_DIGEST = "b" * 128


def _real_registry() -> TrustedAdapterRegistry:
    registry = TrustedAdapterRegistry()
    registry.register(
        AdapterDescriptor(
            adapter_id="argd_dagd_combined_v1",
            schema_id="combined_argd_dagd_v1",
            adapter_version="1",
        ),
        ArgdDagdCombinedAdapter(),
    )
    registry.register(
        AdapterDescriptor(adapter_id="cdogd_v1", schema_id="cdogd_v1", adapter_version="1"),
        CdogdAdapter(),
    )
    registry.register(
        AdapterDescriptor(
            adapter_id="common_domain_extension_v1",
            schema_id="common_domain_extension_v1",
            adapter_version="1",
        ),
        CommonDomainExtensionAdapter(),
    )
    return registry


def test_scenario_empty_provider_produces_a_valid_empty_unbound_plan() -> None:
    provider = EmptyDefinitionProvider()
    assert provider.describe().state is ProviderState.EMPTY

    result = provider.load_package(PackageLoadRequest())
    assert result.found is False  # nothing to compile — not an error

    plan = compile_plan(
        compiler_input=CompilerInput(
            normalized_ir_refs=(),
            normalized_ir_digests=(),
            runtime_capability_snapshot_digest=_CAP_DIGEST,
            authority_snapshot_digest=_AUTH_DIGEST,
        ),
        definitions=(),
    )
    assert plan.binding_state == "unbound"
    assert plan.selected_rule_refs == ()


def test_scenario_unknown_adapter_yields_unsupported_not_a_crash() -> None:
    provider = FilesystemDefinitionProvider(root=DEFINITIONS_ROOT)
    result = provider.load_package(PackageLoadRequest())
    assert result.manifest is not None
    manifest = result.manifest

    # Deliberately empty registry: nothing is registered for any schema_id.
    empty_registry = TrustedAdapterRegistry()
    verifications = provider.verify_sources(provider._load_signed_manifest())
    definition_states = resolve_definition_states(manifest, verifications)

    for definition in manifest.definition_entries:
        source_entry = next(
            s for s in manifest.source_entries if s.source_id == definition.source_id
        )
        adapter = empty_registry.resolve(
            schema_id=source_entry.schema_id,
            adapter_id=source_entry.trusted_adapter_id,
            source_media_type=source_entry.media_type,
        )
        assert adapter is None  # unsupported — reported, not raised
    # Repository policy already classified every definition as VALIDATED
    # at the Source level; adapter-unavailability is a separate axis
    # (Trusted Adapter Registry resolution), checked above without a crash.
    assert all(state is DefinitionState.VALIDATED for state in definition_states.values())


def test_scenario_invalid_sibling_does_not_block_valid_definitions(tmp_path: Path) -> None:
    # A tiny synthetic bundle: one source is corrupted, one is intact.
    root = tmp_path / "definitions"
    good_relative = "good.json"
    good_path = root / good_relative
    good_path.parent.mkdir(parents=True, exist_ok=True)
    good_payload = json.dumps({"good": {"domain_scope": {"domain": "x"}}}).encode()
    good_path.write_bytes(good_payload)

    import hashlib

    from margpa_runtime_llm.modules.governance_definitions.domain import (
        DefinitionEntry,
        PackageManifest,
        SourceEntry,
        sign_manifest,
    )

    good_digest = hashlib.sha512(good_payload).hexdigest()
    manifest = PackageManifest(
        package_id="matrix-test",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=(
            SourceEntry(
                source_id="good",
                relative_path=f"definitions/{good_relative}",
                media_type="application/json",
                byte_length=len(good_payload),
                content_digest_sha512=good_digest,
                schema_id="common_domain_extension_v1",
                trusted_adapter_id="common_domain_extension_v1",
                logical_definition_ids=("good",),
            ),
            SourceEntry(
                source_id="bad",
                relative_path="definitions/bad.json",  # never written -> missing file
                media_type="application/json",
                byte_length=1,
                content_digest_sha512="f" * 128,
                schema_id="common_domain_extension_v1",
                trusted_adapter_id="common_domain_extension_v1",
                logical_definition_ids=("bad",),
            ),
        ),
        definition_entries=(
            DefinitionEntry(
                definition_id="good",
                definition_version="1",
                display_name="Good",
                domain="good_domain",
                source_id="good",
                source_object_pointer="$.good",
                extension_archetype="common_domain_extension",
            ),
            DefinitionEntry(
                definition_id="bad",
                definition_version="1",
                display_name="Bad",
                domain="bad_domain",
                source_id="bad",
                source_object_pointer="$.bad",
                extension_archetype="common_domain_extension",
            ),
        ),
    )
    (root / "manifest.json").write_text(sign_manifest(manifest).model_dump_json(), encoding="utf-8")

    provider = FilesystemDefinitionProvider(root=root)
    result = provider.load_package(PackageLoadRequest())
    assert result.found is True
    assert result.package_state is PackageState.VALIDATED  # whole package survives
    assert result.manifest is not None

    verifications = provider.verify_sources(provider._load_signed_manifest())
    states = resolve_definition_states(result.manifest, verifications)
    assert states["good"] is DefinitionState.VALIDATED
    assert states["bad"] is DefinitionState.INVALID  # isolated, sibling preserved

    registry = _real_registry()
    good_source = next(s for s in result.manifest.source_entries if s.source_id == "good")
    good_definition = next(
        d for d in result.manifest.definition_entries if d.definition_id == "good"
    )
    adapter = registry.resolve(
        schema_id=good_source.schema_id,
        adapter_id=good_source.trusted_adapter_id,
        source_media_type=good_source.media_type,
    )
    assert adapter is not None
    source_json = json.loads(good_path.read_bytes())
    ir = adapter.normalize(
        source_json=source_json, source_entry=good_source, definition_entry=good_definition
    )
    digested = digest_ir(ir)
    plan = compile_plan(
        compiler_input=CompilerInput(
            normalized_ir_refs=(ir.ir_id,),
            normalized_ir_digests=(digested.ir_digest_sha512,),
            runtime_capability_snapshot_digest=_CAP_DIGEST,
            authority_snapshot_digest=_AUTH_DIGEST,
        ),
        definitions=(digested,),
    )
    assert plan.binding_state == "unbound"
    assert len(plan.selected_rule_refs) >= 1


def test_scenario_real_reference_bundle_compiles_all_18_into_one_unbound_plan() -> None:
    provider = FilesystemDefinitionProvider(root=DEFINITIONS_ROOT)
    result = provider.load_package(PackageLoadRequest())
    assert result.package_state is PackageState.VALIDATED
    manifest = result.manifest
    assert manifest is not None

    registry = _real_registry()
    digested_irs = []
    for definition in manifest.definition_entries:
        source_entry = next(
            s for s in manifest.source_entries if s.source_id == definition.source_id
        )
        adapter = registry.resolve(
            schema_id=source_entry.schema_id,
            adapter_id=source_entry.trusted_adapter_id,
            source_media_type=source_entry.media_type,
        )
        assert adapter is not None
        source_json = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
        ir = adapter.normalize(
            source_json=source_json, source_entry=source_entry, definition_entry=definition
        )
        digested_irs.append(digest_ir(ir))

    plan = compile_plan(
        compiler_input=CompilerInput(
            normalized_ir_refs=tuple(d.ir.ir_id for d in digested_irs),
            normalized_ir_digests=tuple(d.ir_digest_sha512 for d in digested_irs),
            runtime_capability_snapshot_digest=_CAP_DIGEST,
            authority_snapshot_digest=_AUTH_DIGEST,
        ),
        definitions=tuple(digested_irs),
    )
    assert plan.binding_state == "unbound"
    assert plan.executable is False
    assert plan.unresolved_dependencies == ()
    assert len(plan.source_definition_digests) == 18


def test_evidence_store_records_a_governance_plan_compiled_event(tmp_path: Path) -> None:
    """Sanity check that Phase 3-B's Evidence Store and Phase 3-E's
    Compiler Output can be wired together without either module reaching
    into the other's internals (loose coupling, architecture §4)."""

    from datetime import UTC, datetime

    from margpa_runtime_llm.modules.audit_evidence.domain import (
        AuditEventEnvelope,
        AuditEventId,
        AuditEventKind,
        AuditEventProvenance,
        AuditRunId,
        GovernancePlanCompiledPayload,
        canonicalize_event,
    )

    store = LocalJsonlEvidenceStore(
        anchor=tmp_path, relative_root="evidence", scope="compile-evidence"
    )
    envelope = AuditEventEnvelope(
        event_id=AuditEventId(value="event-0001"),
        run_id=AuditRunId(value="run-0001"),
        occurred_at_utc=datetime(2026, 8, 21, 20, 30, 0, tzinfo=UTC),
        source_component="governance_definitions.compiler",
        event_kind=AuditEventKind.GOVERNANCE_PLAN_COMPILED,
        provenance=AuditEventProvenance.SYSTEM_TRACE,
        safe_payload=GovernancePlanCompiledPayload(
            compiled_plan_id="plan-0001", binding_state="unbound", executable=False
        ),
    )
    receipt = store.append(canonicalize_event(envelope))
    assert receipt.position == 0
    assert store.status().event_count == 1
