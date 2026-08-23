# Reference Governance Definition Bundle

```yaml
document_id: definitions_readme
status: current
phase: phase_3
language: en
```

This directory holds the Reference Governance Definition Bundle used to
exercise Phase 3's Generic Governance Definition Platform: 17 JSON
sources containing 18 logical definitions (ARGD, DAGD, CDOGD, and 15
domain-extension GDs), organized under `core_governance/`,
`orchestration/`, and `domain_extensions/{ordinary,decision_pipelines,
conditional_watchdogs}/`.

## `manifest.json`

`manifest.json` is the versioned Package Manifest (architecture
§5.2, `src/margpa_runtime_llm/modules/governance_definitions/domain/
manifest.py`) that maps each source file to its logical definition(s) by
explicit object pointer, records byte length and SHA-512 for drift
detection, and assigns each source to one of the three Reference Bundle
Trusted Adapter classes (architecture §6.2):

- `argd_dagd_combined_v1` — the single source containing both ARGD and
  DAGD.
- `cdogd_v1` — the orchestration definition.
- `common_domain_extension_v1` — the 15 domain-extension definitions,
  which share a common structural shape.

The Manifest is data, not code: it is the one place these definition IDs
are allowed to appear as a closed catalog. The Generic Core (Provider,
Adapter Registry, Compiler) never hardcodes a definition name, file name,
or count — see `docs/project/phases/phase_3/architecture/
phase_3_architecture_ja.md` §5 and ADR-3-003/003/005.

`manifest.json`'s own `manifest_digest_sha512` is computed over the
manifest payload with the digest field itself excluded, so it cannot be
self-referential (the same pattern used for
`claude_compaction_recovery_hash_manifest_ja.md`).

## Provenance

Source content is treated as immutable input (ADR-3-006): the Filesystem
Provider (Phase 3-C-WU-003) reads only via this Manifest and rejects any
source whose observed digest does not match. Editing a source file
requires a new `manifest.json` entry recording the version bump, reason,
and semantic diff — never a silent same-version rewrite.

`.DS_Store` files that may appear under this directory are not part of
any source entry and are not read, deleted, or otherwise touched by the
Definition Provider or by this documentation.

## Regenerating `manifest.json`

The manifest is derived data — regenerate it (via
`PackageManifest`/`sign_manifest` in
`margpa_runtime_llm.modules.governance_definitions.domain`) rather than
hand-editing it, so `content_digest_sha512` and `manifest_digest_sha512`
stay exact.
