"""Repository State resolution / Partial Acceptance Policy (P3-C-WU-004)."""

from __future__ import annotations

from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    DefinitionState,
    PackageManifest,
    PackageState,
    SourceEntry,
    SourceState,
    SourceVerification,
    resolve_definition_states,
    resolve_package_state,
    sign_manifest,
)

_KNOWN_SCHEMA = "common_domain_extension_v1"


def _source(source_id: str, *, schema_id: str = _KNOWN_SCHEMA) -> SourceEntry:
    return SourceEntry(
        source_id=source_id,
        relative_path=f"definitions/{source_id}.json",
        media_type="application/json",
        byte_length=10,
        content_digest_sha512="0" * 128,
        schema_id=schema_id,
        trusted_adapter_id=schema_id,
        logical_definition_ids=(source_id,),
    )


def _definition(definition_id: str, source_id: str) -> DefinitionEntry:
    return DefinitionEntry(
        definition_id=definition_id,
        definition_version="1",
        display_name=definition_id.upper(),
        domain=f"{definition_id}_domain",
        source_id=source_id,
        source_object_pointer=f"$.{definition_id}",
        extension_archetype="common_domain_extension",
    )


def _manifest(source_ids: list[str]) -> PackageManifest:
    return PackageManifest(
        package_id="policy-test",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=tuple(_source(sid) for sid in source_ids),
        definition_entries=tuple(_definition(sid, sid) for sid in source_ids),
    )


def test_all_sources_loaded_yields_validated_package_and_definitions() -> None:
    manifest = _manifest(["a", "b"])
    signed = sign_manifest(manifest)
    verifications = (
        SourceVerification(source_id="a", state=SourceState.LOADED),
        SourceVerification(source_id="b", state=SourceState.LOADED),
    )

    assert resolve_package_state(signed, verifications) is PackageState.VALIDATED
    states = resolve_definition_states(manifest, verifications)
    assert states == {"a": DefinitionState.VALIDATED, "b": DefinitionState.VALIDATED}


def test_one_digest_mismatch_invalidates_only_that_definition_valid_sibling_preserved() -> None:
    manifest = _manifest(["a", "b"])
    signed = sign_manifest(manifest)
    verifications = (
        SourceVerification(source_id="a", state=SourceState.DIGEST_MISMATCH),
        SourceVerification(source_id="b", state=SourceState.LOADED),
    )

    # Package-level: an ordinary digest drift on one source is not a
    # whole-package trust problem.
    assert resolve_package_state(signed, verifications) is PackageState.VALIDATED

    states = resolve_definition_states(manifest, verifications)
    assert states["a"] is DefinitionState.INVALID
    assert states["b"] is DefinitionState.VALIDATED  # sibling preserved


def test_structural_source_violation_quarantines_the_whole_package() -> None:
    manifest = _manifest(["a", "b"])
    signed = sign_manifest(manifest)
    verifications = (
        SourceVerification(source_id="a", state=SourceState.INVALID, reason_code="path_unsafe"),
        SourceVerification(source_id="b", state=SourceState.LOADED),
    )

    assert resolve_package_state(signed, verifications) is PackageState.QUARANTINED


def test_tampered_manifest_digest_quarantines_the_package() -> None:
    manifest = _manifest(["a"])
    signed = sign_manifest(manifest)
    tampered = signed.model_copy(update={"manifest_digest_sha512": "1" * 128})

    verifications = (SourceVerification(source_id="a", state=SourceState.LOADED),)
    assert resolve_package_state(tampered, verifications) is PackageState.QUARANTINED


def test_unknown_schema_id_yields_unsupported_definition_state() -> None:
    manifest = PackageManifest(
        package_id="policy-test",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=(_source("a", schema_id="some_future_schema_v9"),),
        definition_entries=(_definition("a", "a"),),
    )
    verifications = (SourceVerification(source_id="a", state=SourceState.LOADED),)

    states = resolve_definition_states(manifest, verifications)
    assert states["a"] is DefinitionState.UNSUPPORTED


def test_missing_verification_for_a_definitions_source_yields_invalid_not_silent_empty() -> None:
    manifest = _manifest(["a"])
    # No SourceVerification supplied at all for "a" — must not be treated
    # as an empty/absent definition; it must show up as INVALID.
    states = resolve_definition_states(manifest, verifications=())
    assert states["a"] is DefinitionState.INVALID
    assert len(states) == 1  # every definition_entry still gets a verdict
