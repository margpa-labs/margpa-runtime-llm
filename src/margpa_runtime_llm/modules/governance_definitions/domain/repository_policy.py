"""Repository State resolution: per-source verification -> per-Package and
per-Definition state, with a Partial Acceptance Policy (P3-C-WU-004).

Key design point: a single bad source must not silently take down its
valid siblings (P3-PRV-006). Package-level `QUARANTINED` is reserved for
package-wide trust problems (the Manifest's own digest not matching, or a
source failing for a *structural* reason such as a path-safety violation)
— an ordinary digest/size drift on one source instead demotes only that
source's Definition(s) to `INVALID`, leaving the Package `VALIDATED` and
every other Definition unaffected.
"""

from __future__ import annotations

from .manifest import PackageManifest, SignedPackageManifest
from .manifest import verify_signed_manifest as _verify_signed_manifest
from .source_verification import SourceVerification
from .states import DefinitionState, PackageState, SourceState

# The Reference Bundle's own three Trusted Adapter classes (architecture
# §6.2). A schema_id outside this set is `unsupported` — not because the
# schema is malformed, but because no Trusted Adapter is registered for
# it yet (P3-PRV-005). This list grows only when a new Adapter is
# registered (Phase 3-D), never inferred from a Manifest's own claims.
KNOWN_SCHEMA_IDS = frozenset({"combined_argd_dagd_v1", "cdogd_v1", "common_domain_extension_v1"})

# Source-level problems severe enough to be a package-wide trust concern
# rather than an isolated per-definition failure.
_STRUCTURAL_SOURCE_STATES = frozenset({SourceState.INVALID})


def resolve_package_state(
    signed: SignedPackageManifest, verifications: tuple[SourceVerification, ...]
) -> PackageState:
    if not _verify_signed_manifest(signed):
        return PackageState.QUARANTINED
    if any(v.state in _STRUCTURAL_SOURCE_STATES for v in verifications):
        return PackageState.QUARANTINED
    return PackageState.VALIDATED


def resolve_definition_states(
    manifest: PackageManifest, verifications: tuple[SourceVerification, ...]
) -> dict[str, DefinitionState]:
    verification_by_source = {v.source_id: v for v in verifications}
    source_by_id = {entry.source_id: entry for entry in manifest.source_entries}

    states: dict[str, DefinitionState] = {}
    for definition in manifest.definition_entries:
        source = source_by_id.get(definition.source_id)
        if source is None or source.schema_id not in KNOWN_SCHEMA_IDS:
            states[definition.definition_id] = DefinitionState.UNSUPPORTED
            continue

        verification = verification_by_source.get(definition.source_id)
        if verification is None or verification.state is not SourceState.LOADED:
            states[definition.definition_id] = DefinitionState.INVALID
            continue

        states[definition.definition_id] = DefinitionState.VALIDATED
    return states
