"""Phase 8 (P8-C): `JsonFileConstitutionProvider` fail-closed loading tests."""

from __future__ import annotations

import json
from pathlib import Path

from margpa_runtime_llm.adapters.constitution import JsonFileConstitutionProvider
from margpa_runtime_llm.modules.constitution import (
    ConstitutionManifest,
    ConstitutionManifestUnavailable,
    ConstitutionRule,
    compute_manifest_digest,
)


def _write_manifest(
    project_root: Path, rules: tuple[ConstitutionRule, ...], *, digest: str | None = None
) -> None:
    manifest_dir = project_root / "constitution"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "revision": 1,
        "digest_sha512": digest if digest is not None else compute_manifest_digest(rules),
        "rules": [json.loads(rule.model_dump_json()) for rule in rules],
    }
    (manifest_dir / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")


def _rule(rule_id: str = "example-rule") -> ConstitutionRule:
    return ConstitutionRule(
        rule_id=rule_id,
        revision=1,
        title="Example Rule",
        summary="A minimal Rule used only by this Test.",
        applies_to=("chat",),
        source_pointer=f"rules/{rule_id}.md",
    )


def test_missing_manifest_reports_not_present(tmp_path: Path) -> None:
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifestUnavailable)
    assert result.reason == "not_present"


def test_valid_manifest_loads_and_digest_matches(tmp_path: Path) -> None:
    rules = (_rule("rule-a"), _rule("rule-b"))
    _write_manifest(tmp_path, rules)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifest)
    assert result.revision == 1
    assert {rule.rule_id for rule in result.rules} == {"rule-a", "rule-b"}


def test_tampered_digest_fails_closed_not_silently_accepted(tmp_path: Path) -> None:
    rules = (_rule("rule-a"),)
    _write_manifest(tmp_path, rules, digest="f" * 128)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifestUnavailable)
    assert result.reason == "digest_mismatch"


def test_corrupt_json_fails_closed(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "constitution"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text("not json{{{", encoding="utf-8")
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifestUnavailable)
    assert result.reason == "corrupt_manifest"


def test_missing_required_field_fails_closed(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "constitution"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps({"revision": 1, "rules": []}), encoding="utf-8"
    )
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifestUnavailable)
    assert result.reason == "corrupt_manifest"


def test_malformed_rule_entry_fails_closed(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "constitution"
    manifest_dir.mkdir(parents=True)
    payload = {
        "revision": 1,
        "digest_sha512": "a" * 128,
        "rules": [{"rule_id": "not-enough-fields"}],
    }
    (manifest_dir / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifestUnavailable)
    assert result.reason == "corrupt_manifest"


def test_real_repository_manifest_loads_and_verifies() -> None:
    """The actual `constitution/manifest.json` this Task shipped — proves
    the real on-disk artifact (not just a Test fixture) round-trips."""

    project_root = Path(__file__).resolve().parents[3]
    provider = JsonFileConstitutionProvider(project_root=project_root)
    result = provider.load_manifest()
    assert isinstance(result, ConstitutionManifest)
    assert result.revision == 1
    assert len(result.rules) == 3
    rule_ids = {rule.rule_id for rule in result.rules}
    assert rule_ids == {
        "no-secrets-in-external-evidence",
        "untrusted-content-never-instruction-authority",
        "external-write-requires-human-gate",
    }
