"""Phase 8 (P8-C): fail-closed JSON-file-backed Constitution Provider.

Reads `<project_root>/constitution/manifest.json`, a single Immutable
Manifest listing every Rule's Stable ID/Revision/applies_to/`source_pointer`
(the actual prose lives in separate Markdown files under `constitution/
rules/`, which this Provider never parses — only the structured Manifest is
load-bearing here). `project_root` is always received via constructor, never
hard-coded (P8-REQ-019).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from margpa_runtime_llm.modules.constitution.contracts import (
    ConstitutionManifest,
    ConstitutionManifestUnavailable,
    ConstitutionRule,
    compute_manifest_digest,
)


class JsonFileConstitutionProvider:
    def __init__(self, *, project_root: Path) -> None:
        self._manifest_path = project_root / "constitution" / "manifest.json"

    def load_manifest(self) -> ConstitutionManifest | ConstitutionManifestUnavailable:
        try:
            raw = self._manifest_path.read_text(encoding="utf-8")
        except OSError:
            return ConstitutionManifestUnavailable(reason="not_present")
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, ValueError):
            return ConstitutionManifestUnavailable(reason="corrupt_manifest")
        if not isinstance(payload, dict):
            return ConstitutionManifestUnavailable(reason="corrupt_manifest")
        try:
            revision = payload["revision"]
            declared_digest = payload["digest_sha512"]
            rules = tuple(ConstitutionRule.model_validate(item) for item in payload["rules"])
        except (KeyError, TypeError, ValidationError):
            return ConstitutionManifestUnavailable(reason="corrupt_manifest")
        # P8-ACC-019/024: the Digest is independently recomputed here, never
        # merely trusted because the on-disk file claims a given value — a
        # Manifest tampered with (or corrupted) after the fact fails closed
        # rather than being silently accepted.
        recomputed_digest = compute_manifest_digest(rules)
        if recomputed_digest != declared_digest:
            return ConstitutionManifestUnavailable(reason="digest_mismatch")
        try:
            return ConstitutionManifest(
                revision=revision,
                digest_sha512=declared_digest,
                rules=rules,
            )
        except ValidationError:
            return ConstitutionManifestUnavailable(reason="corrupt_manifest")
