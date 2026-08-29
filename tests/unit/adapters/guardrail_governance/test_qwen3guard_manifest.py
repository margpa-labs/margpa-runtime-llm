"""P6-RR-R23 (Post-Codex Independent Review Rework, resolves
P6-CODEX-087): `Qwen3GuardManifest` loading, completeness/verification
gating, and per-Target Category scoping — including a direct load of the
real checked-in `config/guardrail/qwen3guard/manifest.json` this Package
populated from Qwen's own official Hugging Face/GitHub Repositories under
its Read-only Network Authority grant.

P6-RR-R27 (Post-Codex Independent Review Rework, resolves P6-CODEX-090):
`_complete_manifest_dict()` now uses the real, full Exact Contract
(imported directly from `qwen3guard_manifest`'s own `_EXPECTED_*`
constants, never a hand-duplicated copy that could silently drift) —
Controller Probe C proved the previous toy 2-Category fixture shape
(`verified_official_contract=True` paired with a 2-item Category Set)
would itself now be rejected by the stricter Cross-field Validator, since
a genuinely-claimed-Verified Manifest must match the real official
Contract exactly, not merely be internally self-consistent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.adapters.guardrail_governance import qwen3guard_manifest as _manifest_module
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_manifest import (
    Qwen3GuardManifest,
    load_qwen3guard_manifest,
)
from margpa_runtime_llm.modules.guardrail_governance.domain.qwen3guard import Qwen3GuardTarget

_REPO_ROOT = Path(__file__).resolve().parents[4]
_REAL_MANIFEST_PATH = _REPO_ROOT / "config" / "guardrail" / "qwen3guard" / "manifest.json"


def _complete_manifest_dict() -> dict[str, Any]:
    """The real Exact Contract, sourced directly from `qwen3guard_
    manifest`'s own module-level constants — the same constants the
    Cross-field Validator itself checks a `verified_official_contract=
    True` Manifest against (P6-RR-R27, resolves P6-CODEX-090)."""
    category_mapping = {
        label: label.lower().replace(" ", "_").replace("&", "and")
        for label in _manifest_module._EXPECTED_CATEGORY_UNION
    }
    return {
        "schema_version": "1",
        "provider_id": _manifest_module._EXPECTED_PROVIDER_ID,
        "label_schema_id": _manifest_module._EXPECTED_LABEL_SCHEMA_ID,
        "verified_official_contract": True,
        "retrieval_status": "test_fixture",
        "huggingface_source": {
            "repository": _manifest_module._OFFICIAL_HUGGINGFACE_REPOSITORY,
            "exact_revision": "a" * 40,
            "source_sha512": "b" * 128,
        },
        "github_source": {
            "repository": _manifest_module._OFFICIAL_GITHUB_REPOSITORY,
            "exact_revision": "c" * 40,
            "source_sha512": "d" * 128,
        },
        "input_context_categories": list(_manifest_module._EXPECTED_INPUT_CONTEXT_CATEGORIES),
        "output_candidate_categories": list(_manifest_module._EXPECTED_OUTPUT_CANDIDATE_CATEGORIES),
        "category_id_mapping": category_mapping,
    }


def test_real_checked_in_manifest_loads_and_is_complete_and_verified() -> None:
    """The actual Manifest shipped in `config/guardrail/qwen3guard/
    manifest.json` — this is the direct, load-bearing proof that R23's
    real fetch from Qwen's official Sources produced a genuinely usable
    Manifest, not merely a schema-valid placeholder, and that it still
    satisfies R27's stricter Exact-Contract Cross-field Validator
    unchanged (no data correction was needed — only the Runtime Gate)."""
    manifest = load_qwen3guard_manifest(_REAL_MANIFEST_PATH)
    assert manifest.is_complete_and_verified is True
    assert manifest.huggingface_source.repository == "Qwen/Qwen3Guard-Gen-0.6B"
    assert manifest.huggingface_source.exact_revision is not None
    assert manifest.huggingface_source.exact_revision != "main"
    assert manifest.github_source.repository == "QwenLM/Qwen3Guard"
    assert manifest.github_source.exact_revision is not None
    assert manifest.github_source.exact_revision != "main"
    # The one documented Input-only Category — the exact P6-CODEX-087
    # example — is present for Input/Context and absent for Output.
    assert "Jailbreak" in manifest.allowed_categories_for(Qwen3GuardTarget.INPUT)
    assert "Jailbreak" in manifest.allowed_categories_for(Qwen3GuardTarget.CONTEXT_SOURCE)
    assert "Jailbreak" not in manifest.allowed_categories_for(Qwen3GuardTarget.OUTPUT_CANDIDATE)
    assert len(manifest.input_context_categories) == 9
    assert len(manifest.output_candidate_categories) == 8


def test_complete_and_verified_fixture_manifest_is_usable(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(_complete_manifest_dict()), encoding="utf-8")
    manifest = load_qwen3guard_manifest(path)
    assert manifest.is_complete_and_verified is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(verified_official_contract=False),
        lambda d: d["huggingface_source"].update(exact_revision=None),
        lambda d: d["huggingface_source"].update(source_sha512=None),
        lambda d: d["github_source"].update(exact_revision=None),
        lambda d: d["github_source"].update(source_sha512=None),
    ],
)
def test_incomplete_manifest_is_never_reported_verified(tmp_path: Path, mutation: object) -> None:
    """P6-CODEX-087's exact finding: `verified_official_contract=True`
    alone must never be sufficient — each of these 5 mutations (none of
    which the R27 Exact-Contract Cross-field Validator itself checks)
    still loads successfully but knocks `is_complete_and_verified` back
    to `False` via the pre-existing completeness check."""
    data = _complete_manifest_dict()
    mutation(data)  # type: ignore[operator]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    manifest = load_qwen3guard_manifest(path)
    assert manifest.is_complete_and_verified is False


@pytest.mark.parametrize(
    "mutation,expected_error",
    [
        (
            lambda d: d.update(input_context_categories=[]),
            "input_context_categories_mismatch",
        ),
        (
            lambda d: d.update(output_candidate_categories=[]),
            "output_candidate_categories_mismatch",
        ),
        (
            lambda d: d.update(category_id_mapping={}),
            "category_mapping_keys_do_not_cover_union_exactly",
        ),
        (
            lambda d: d.update(provider_id="wrong.provider"),
            "provider_id_mismatch",
        ),
        (
            lambda d: d.update(
                input_context_required_fields=["Wrong"],
                output_candidate_required_fields=["Wrong"],
            ),
            "input_context_required_fields_mismatch",
        ),
    ],
)
def test_construction_rejects_incomplete_or_wrong_exact_contract_when_claimed_verified(
    tmp_path: Path, mutation: object, expected_error: str
) -> None:
    """P6-RR-R27 (resolves P6-CODEX-090): the exact Controller Probe C
    shape — `verified_official_contract=True` paired with a wrong/
    incomplete Exact Contract field — must fail Construction itself, via
    the Cross-field Validator, never merely settle at `is_complete_and_
    verified=False` after successfully loading. `provider_id="wrong.
    provider"` here is Probe C's own literal reproduction."""
    data = _complete_manifest_dict()
    mutation(data)  # type: ignore[operator]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValidationError, match=expected_error):
        load_qwen3guard_manifest(path)


def test_unverified_manifest_with_wrong_fields_still_constructs_as_placeholder(
    tmp_path: Path,
) -> None:
    """The Cross-field Validator is deliberately exempt when `verified_
    official_contract=False` — a not-yet-fetched placeholder Manifest
    (mirroring `SelenePromptManifest`'s identical "not yet Verified"
    shape) must remain constructible even with garbage/absent Contract
    fields; it simply stays unusable (`is_complete_and_verified=False`),
    never a hard Construction failure."""
    data = _complete_manifest_dict()
    data["verified_official_contract"] = False
    data["provider_id"] = "not.yet.known"
    data["input_context_categories"] = []
    data["category_id_mapping"] = {}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    manifest = load_qwen3guard_manifest(path)
    assert manifest.is_complete_and_verified is False


def test_category_mapping_for_excludes_jailbreak_on_output_candidate() -> None:
    manifest = Qwen3GuardManifest.model_validate(_complete_manifest_dict())
    input_mapping = manifest.category_mapping_for(Qwen3GuardTarget.INPUT)
    output_mapping = manifest.category_mapping_for(Qwen3GuardTarget.OUTPUT_CANDIDATE)
    assert "Jailbreak" in input_mapping
    assert "Jailbreak" not in output_mapping
    assert set(output_mapping) == set(_manifest_module._EXPECTED_OUTPUT_CANDIDATE_CATEGORIES)


def test_context_source_uses_the_same_scoping_as_input() -> None:
    manifest = Qwen3GuardManifest.model_validate(_complete_manifest_dict())
    assert manifest.category_mapping_for(
        Qwen3GuardTarget.CONTEXT_SOURCE
    ) == manifest.category_mapping_for(Qwen3GuardTarget.INPUT)


def test_required_fields_for_matches_frozen_line_protocol() -> None:
    manifest = Qwen3GuardManifest.model_validate(_complete_manifest_dict())
    assert manifest.required_fields_for(Qwen3GuardTarget.INPUT) == ("Safety", "Categories")
    assert manifest.required_fields_for(Qwen3GuardTarget.CONTEXT_SOURCE) == (
        "Safety",
        "Categories",
    )
    assert manifest.required_fields_for(Qwen3GuardTarget.OUTPUT_CANDIDATE) == (
        "Safety",
        "Categories",
        "Refusal",
    )


def test_manifest_schema_forbids_unknown_fields() -> None:
    """P6-RR-R23 (resolves the "Manifest Validation success as a
    precondition" half of P6-CODEX-087): a Manifest with an unexpected
    extra field fails Pydantic schema validation outright — the same
    fail-fast-at-load discipline `SelenePromptManifest` already has."""
    data = _complete_manifest_dict()
    data["unexpected_field"] = "should never be accepted"
    with pytest.raises(ValidationError):
        Qwen3GuardManifest.model_validate(data)
