"""Normalized Governance IR (architecture §5.4/§6.3).

Deliberately structural rather than deeply semantic: each source
definition's top-level sections are preserved by name and immediate
child-key shape (`IrSection`), traceable back to the source via
`source_object_pointer` — but this Adapter generation does not claim to
understand what each section's Rules/Evaluators/Actions *mean* well
enough to type them individually. P3-IR-005 forbids guessing at missing
Rule/Priority/Authority/Action semantics; a faithful structural passthrough
with an explicit `normalization_warnings` entry is the honest choice over
a deeper mapping this Adapter generation cannot yet justify field-by-field
for content it has not exhaustively read. Deeper per-section typed
extraction is future work, tracked as a Deferred Evidence item, not
silently assumed complete.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .limits import (
    MAX_COLLECTION_LENGTH,
    MAX_IR_SECTION_CHILD_KEY_COUNT,
    MAX_IR_SECTION_COUNT,
    MAX_STRING_LENGTH,
)

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_OBJECT_POINTER_PATTERN = r"^\$(\.[A-Za-z0-9_]+)+$"
_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"

_BoundedString = Annotated[str, Field(max_length=MAX_STRING_LENGTH)]


class IrIdentity(ImmutableContract):
    definition_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    definition_version: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    display_name: str = Field(min_length=1, max_length=256)


class IrSourceProvenance(ImmutableContract):
    source_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_object_pointer: str = Field(pattern=_OBJECT_POINTER_PATTERN)
    content_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


class IrSection(ImmutableContract):
    """One top-level key of the source definition object, kept as a
    structural fingerprint (its own key plus its immediate children's
    key names) rather than parsed into typed Rule/Evaluator/Action
    objects."""

    section_key: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    child_keys: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_IR_SECTION_CHILD_KEY_COUNT
    )
    value_kind: str = Field(min_length=1, max_length=16, pattern=_IDENTIFIER_PATTERN)


class NormalizedGovernanceDefinition(ImmutableContract):
    ir_schema_version: str = Field(default="1", pattern=r"^[0-9]+$")
    ir_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    identity: IrIdentity
    source_provenance: IrSourceProvenance
    domain: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    sections: tuple[IrSection, ...] = Field(max_length=MAX_IR_SECTION_COUNT)
    dependencies: tuple[_BoundedString, ...] = Field(default=(), max_length=MAX_COLLECTION_LENGTH)
    conflicts: tuple[_BoundedString, ...] = Field(default=(), max_length=MAX_COLLECTION_LENGTH)
    non_targets: tuple[_BoundedString, ...] = Field(default=(), max_length=MAX_COLLECTION_LENGTH)
    normalization_warnings: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COLLECTION_LENGTH
    )
    unsupported_source_pointers: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COLLECTION_LENGTH
    )


def ir_payload_for_digest(ir: NormalizedGovernanceDefinition) -> dict[str, object]:
    return ir.model_dump(mode="json")


def ir_digest_sha512(ir: NormalizedGovernanceDefinition) -> str:
    canonical = json.dumps(
        ir_payload_for_digest(ir),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


class DigestedNormalizedGovernanceDefinition(ImmutableContract):
    ir: NormalizedGovernanceDefinition
    ir_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


def digest_ir(ir: NormalizedGovernanceDefinition) -> DigestedNormalizedGovernanceDefinition:
    return DigestedNormalizedGovernanceDefinition(ir=ir, ir_digest_sha512=ir_digest_sha512(ir))


def verify_digested_ir(digested: DigestedNormalizedGovernanceDefinition) -> bool:
    return ir_digest_sha512(digested.ir) == digested.ir_digest_sha512
