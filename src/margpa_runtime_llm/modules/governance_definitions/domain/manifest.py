"""Package Manifest contracts (architecture §5.2).

The Manifest is the one place Reference Bundle identity (ARGD, DAGD, CDOGD,
the 15 domain extensions) is allowed to appear as data — never as a Core
Enum, Filename inference, or hardcoded Python constant (P3-DEF-003,
ADR-3-005). This module defines the *shape*; the actual 17-source/
18-definition catalog lives in `definitions/manifest.json`, produced from
the observed `phase_3_definition_source_inventory_ja.md` baseline.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .limits import MAX_DEFINITION_ENTRY_COUNT, MAX_RELATIVE_PATH_DEPTH, MAX_SOURCE_ENTRY_COUNT

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_RELATIVE_PATH_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$"
_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"
_OBJECT_POINTER_PATTERN = r"^\$(\.[A-Za-z0-9_]+)+$"
_MEDIA_TYPE_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9.+-]*/[A-Za-z0-9][A-Za-z0-9.+-]*$"

_BoundedIdentifier = Annotated[
    str, Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
]


class SourceEntry(ImmutableContract):
    source_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    relative_path: str = Field(min_length=1, max_length=256, pattern=_RELATIVE_PATH_PATTERN)
    media_type: str = Field(min_length=1, max_length=64, pattern=_MEDIA_TYPE_PATTERN)
    byte_length: int = Field(ge=0)
    content_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    schema_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    trusted_adapter_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    logical_definition_ids: tuple[_BoundedIdentifier, ...] = Field(
        min_length=1, max_length=MAX_DEFINITION_ENTRY_COUNT
    )

    @field_validator("relative_path")
    @classmethod
    def _bounded_path_depth(cls, value: str) -> str:
        if len(value.split("/")) > MAX_RELATIVE_PATH_DEPTH:
            raise ValueError("relative_path exceeds the maximum path depth")
        return value


class DefinitionEntry(ImmutableContract):
    definition_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    definition_version: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    display_name: str = Field(min_length=1, max_length=256)
    domain: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_object_pointer: str = Field(pattern=_OBJECT_POINTER_PATTERN)
    extension_archetype: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    # Deeper semantic fields (capability_kinds, role_kinds, activation
    # patterns, governed object types, non-targets, dependencies,
    # conflicts) are Normalized-IR concerns — extracted per-definition
    # from source content in Phase 3-D, not authored by hand here. An
    # empty tuple at this layer means "not yet extracted", not "none".
    dependencies: tuple[_BoundedIdentifier, ...] = Field(
        default=(), max_length=MAX_DEFINITION_ENTRY_COUNT
    )
    conflicts: tuple[_BoundedIdentifier, ...] = Field(
        default=(), max_length=MAX_DEFINITION_ENTRY_COUNT
    )


class PackageManifest(ImmutableContract):
    manifest_format_version: str = Field(default="1", pattern=r"^[0-9]+$")
    package_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    package_version: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    publisher: str = Field(min_length=1, max_length=128)
    license: str = Field(min_length=1, max_length=64)
    source_entries: tuple[SourceEntry, ...] = Field(min_length=1, max_length=MAX_SOURCE_ENTRY_COUNT)
    definition_entries: tuple[DefinitionEntry, ...] = Field(
        min_length=1, max_length=MAX_DEFINITION_ENTRY_COUNT
    )
    dependencies: tuple[_BoundedIdentifier, ...] = Field(
        default=(), max_length=MAX_SOURCE_ENTRY_COUNT
    )
    signatures: tuple[str, ...] = Field(default=(), max_length=MAX_SOURCE_ENTRY_COUNT)


def manifest_payload_for_digest(manifest: PackageManifest) -> dict[str, object]:
    """The Manifest's own payload is hashed *without* its digest field
    (P3-PKG-003) — this function is the canonical exclusion point, called
    both when computing and when verifying `manifest_digest_sha512`."""

    return manifest.model_dump(mode="json")


def manifest_digest_sha512(manifest: PackageManifest) -> str:
    canonical = json.dumps(
        manifest_payload_for_digest(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


class SignedPackageManifest(ImmutableContract):
    """A `PackageManifest` paired with its own digest — digest computed
    over the manifest alone, so the digest field is never part of its own
    input (mirrors `audit_evidence.canonicalization.CanonicalAuditEvent`)."""

    manifest: PackageManifest
    manifest_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


def sign_manifest(manifest: PackageManifest) -> SignedPackageManifest:
    return SignedPackageManifest(
        manifest=manifest,
        manifest_digest_sha512=manifest_digest_sha512(manifest),
    )


def verify_signed_manifest(signed: SignedPackageManifest) -> bool:
    return manifest_digest_sha512(signed.manifest) == signed.manifest_digest_sha512
