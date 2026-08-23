"""Reference Bundle Trusted Adapters (architecture §6.2, P3-D-WU-002/003).

Three adapter *identities* — `ArgdDagdCombinedAdapter`, `CdogdAdapter`,
`CommonDomainExtensionAdapter` — share one structural-passthrough
normalizer (`_normalize_generic`), since the 17 Reference Bundle sources
turned out (per the Definition Source Inventory's own observation) to
share a common top-level shape closely enough that no adapter-specific
field mapping has been justified yet. Each class stays a distinct,
separately-registered Adapter rather than one shared instance, so a
future divergence (e.g. CDOGD needing real Orchestration-graph parsing)
can specialize one class without touching the others (ADR-3-005: Reference
Bundle Adapters live outside Generic Core, exactly so this kind of
divergence is cheap).
"""

from __future__ import annotations

from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    IrIdentity,
    IrSection,
    IrSourceProvenance,
    NormalizedGovernanceDefinition,
    SourceEntry,
)

# Object-pointer path segments the generic normalizer treats as forward
# references to *other* definitions (dependency/orchestration edges)
# rather than opaque leaf content — used only to populate
# `dependencies`/`non_targets` when the source itself names another
# known definition_id. Kept intentionally small and explicit rather than
# inferred, per P3-IR-005.
_KNOWN_REFERENCE_KEYS = frozenset({"orchestration_reference", "cross_domain_interference_policy"})


def _value_kind(value: object) -> str:
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if value is None:
        return "null"
    return "unknown"


def _child_keys(value: object) -> tuple[str, ...]:
    if isinstance(value, dict):
        return tuple(str(key) for key in value)
    return ()


def _resolve_pointer(source_json: dict[str, object], pointer: str) -> object:
    node: object = source_json
    for part in pointer.removeprefix("$.").split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(pointer)
        node = node[part]
    return node


def _normalize_generic(
    *,
    source_json: dict[str, object],
    source_entry: SourceEntry,
    definition_entry: DefinitionEntry,
) -> NormalizedGovernanceDefinition:
    node = _resolve_pointer(source_json, definition_entry.source_object_pointer)
    warnings: list[str] = []
    unsupported_pointers: list[str] = []

    if not isinstance(node, dict):
        warnings.append("source_object_pointer did not resolve to an object")
        sections: tuple[IrSection, ...] = ()
    else:
        sections = tuple(
            IrSection(
                section_key=key,
                child_keys=_child_keys(value),
                value_kind=_value_kind(value),
            )
            for key, value in node.items()
        )
        warnings.append(
            "structural passthrough only: section contents are preserved by key "
            "shape, not parsed into typed Rule/Evaluator/Action semantics "
            "(Phase 3-D scope decision, see phase_3_d adapter module docstring)"
        )
        for key in _KNOWN_REFERENCE_KEYS:
            if key not in node:
                unsupported_pointers.append(
                    f"{definition_entry.source_object_pointer}.{key} (absent)"
                )

    return NormalizedGovernanceDefinition(
        ir_id=f"{definition_entry.definition_id}-ir",
        identity=IrIdentity(
            definition_id=definition_entry.definition_id,
            definition_version=definition_entry.definition_version,
            display_name=definition_entry.display_name,
        ),
        source_provenance=IrSourceProvenance(
            source_id=source_entry.source_id,
            source_object_pointer=definition_entry.source_object_pointer,
            content_digest_sha512=source_entry.content_digest_sha512,
        ),
        domain=definition_entry.domain,
        sections=sections,
        dependencies=definition_entry.dependencies,
        conflicts=definition_entry.conflicts,
        normalization_warnings=tuple(warnings),
        unsupported_source_pointers=tuple(unsupported_pointers),
    )


class ArgdDagdCombinedAdapter:
    """One source, two logical definitions (ARGD + DAGD), each addressed
    by its own `source_object_pointer` — never by re-deriving a pointer
    from a filename or definition_id (P3-D-WU-002: Source Rewrite 0)."""

    def normalize(
        self,
        *,
        source_json: dict[str, object],
        source_entry: SourceEntry,
        definition_entry: DefinitionEntry,
    ) -> NormalizedGovernanceDefinition:
        return _normalize_generic(
            source_json=source_json, source_entry=source_entry, definition_entry=definition_entry
        )


class CdogdAdapter:
    """Converts the Orchestration definition without executing any
    routing or activation it describes (P3-D-WU-003: Routing/Activation
    実行0)."""

    def normalize(
        self,
        *,
        source_json: dict[str, object],
        source_entry: SourceEntry,
        definition_entry: DefinitionEntry,
    ) -> NormalizedGovernanceDefinition:
        return _normalize_generic(
            source_json=source_json, source_entry=source_entry, definition_entry=definition_entry
        )


class CommonDomainExtensionAdapter:
    """The 15 domain-extension definitions share this one Adapter
    identity because they share the common structural shape documented
    in the Definition Source Inventory §3.3 — decision-pipeline ordering
    (SPPGD→DAAGD→SDAGD, conditional SDMRGD) and orchestration references
    are preserved as IR sections, not executed."""

    def normalize(
        self,
        *,
        source_json: dict[str, object],
        source_entry: SourceEntry,
        definition_entry: DefinitionEntry,
    ) -> NormalizedGovernanceDefinition:
        return _normalize_generic(
            source_json=source_json, source_entry=source_entry, definition_entry=definition_entry
        )
