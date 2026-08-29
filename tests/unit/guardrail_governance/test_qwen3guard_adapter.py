"""P6-RR-R23 (Post-Codex Independent Review Rework, resolves P6-CODEX-087):
`decode_qwen3guard_output()` must now unconditionally require the
`Categories:` line for both Targets (mirroring Qwen's own official
`tokenizer_config.json` Chat Template, which never treats it as optional
— even a `Safe` result must say `Categories: None`), and
`Qwen3GuardGenAdapter` must source both its per-Target Category Set and
its `verified_official_contract` gate from a loaded, validated
`Qwen3GuardManifest` rather than caller-injected parameters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.guardrail_governance import qwen3guard_manifest as _manifest_module
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_adapter import (
    Qwen3GuardGenAdapter,
)
from margpa_runtime_llm.adapters.guardrail_governance.safety_model_adapters import (
    SafetyModelDetectorAdapter,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_JAILBREAK,
    CATEGORY_SECRET,
    CATEGORY_UNSAFE_CONTENT,
    DetectionOutcome,
    GuardDetection,
    Qwen3GuardClassification,
    Qwen3GuardDecodeError,
    Qwen3GuardRefusal,
    Qwen3GuardSafety,
    Qwen3GuardTarget,
    SafetyModelFailureKind,
    Severity,
    decode_qwen3guard_output,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import SafetyModelUnavailable
from margpa_runtime_llm.modules.inference.contracts.generation import GenerationRequest

_MODEL = "guard.qwen3guard-gen-0.6b-q8-0"
_REVISION = "test.fixture.revision.1"
_DIGEST = "b" * 128
_MAPPING = {"Jailbreak": CATEGORY_JAILBREAK, "Privacy": CATEGORY_SECRET}


def _decode(raw_text: str, target: Qwen3GuardTarget) -> Qwen3GuardClassification:
    return decode_qwen3guard_output(
        raw_text=raw_text,
        target=target,
        category_mapping=_MAPPING,
        model_id=_MODEL,
        exact_revision=_REVISION,
        artifact_digest_sha512=_DIGEST,
    )


def test_official_valid_input_format_decodes_clear() -> None:
    """Official Valid (P6-RR-R23 Fixture item 1): the frozen 2-line
    Input/Context shape, `Categories: None` present exactly as Qwen's own
    official Chat Template mandates for a Safe result."""
    result = _decode("Safety: Safe\nCategories: None", Qwen3GuardTarget.INPUT)
    assert result.safety is Qwen3GuardSafety.SAFE
    assert result.detections[0].outcome is DetectionOutcome.CLEAR
    assert result.detections[0].category_id == CATEGORY_UNSAFE_CONTENT


def test_official_valid_output_candidate_preserves_categories_and_refusal() -> None:
    """Official Valid (Output Candidate half): the frozen 3-line shape."""
    result = _decode(
        "Safety: Unsafe\nCategories: Jailbreak, Privacy\nRefusal: Yes",
        Qwen3GuardTarget.OUTPUT_CANDIDATE,
    )
    assert result.safety is Qwen3GuardSafety.UNSAFE
    assert result.refusal is Qwen3GuardRefusal.YES
    assert result.categories == ("Jailbreak", "Privacy")
    assert result.mapped_category_ids == (CATEGORY_JAILBREAK, CATEGORY_SECRET)
    assert all(detection.outcome is DetectionOutcome.MATCH for detection in result.detections)


def test_controversial_context_with_required_categories_none_is_a_match() -> None:
    result = _decode("Safety: Controversial\nCategories: None", Qwen3GuardTarget.CONTEXT_SOURCE)
    assert result.safety is Qwen3GuardSafety.CONTROVERSIAL
    assert result.detections[0].severity is Severity.MODERATE


@pytest.mark.parametrize(
    "raw_text,target",
    [
        # Missing Categories (P6-RR-R23 Fixture item 2): the official Line
        # Protocol never treats `Categories:` as optional, even for Safe.
        ("Safety: Safe", Qwen3GuardTarget.INPUT),
        ("Safety: Unsafe\nRefusal: Yes", Qwen3GuardTarget.OUTPUT_CANDIDATE),
        # Wrong Order (P6-RR-R23 Fixture item 3).
        ("Categories: None\nSafety: Safe", Qwen3GuardTarget.INPUT),
        ("Safety: Unsafe\nRefusal: No\nCategories: None", Qwen3GuardTarget.OUTPUT_CANDIDATE),
        ("Safety: Maybe\nCategories: None", Qwen3GuardTarget.INPUT),
        ("Safety: Unsafe\nCategories: Jailbreak", Qwen3GuardTarget.OUTPUT_CANDIDATE),
        (
            "Safety: Safe\nCategories: None\nRefusal: Maybe",
            Qwen3GuardTarget.OUTPUT_CANDIDATE,
        ),
        ("Categories: Jailbreak\nSafety: Unsafe", Qwen3GuardTarget.INPUT),
        ("Safety: Safe\nCategories: Jailbreak", Qwen3GuardTarget.INPUT),
        ("Safety: Unsafe\nCategories: Jailbreak, Jailbreak", Qwen3GuardTarget.INPUT),
    ],
)
def test_malformed_or_contradictory_output_is_rejected(
    raw_text: str, target: Qwen3GuardTarget
) -> None:
    """Malformed / Missing Categories / Wrong Order (P6-RR-R23 Fixture
    items 2, 3, 5)."""
    with pytest.raises(Qwen3GuardDecodeError):
        _decode(raw_text, target)


def test_unknown_official_category_is_typed_unknown_not_safe() -> None:
    """Unknown (P6-RR-R23 Fixture item 6): an unrecognized label is never
    silently collapsed to Safe."""
    result = _decode("Safety: Unsafe\nCategories: Unverified Category", Qwen3GuardTarget.INPUT)
    assert result.failure is SafetyModelFailureKind.UNKNOWN_LABEL
    assert result.detections[0].outcome is DetectionOutcome.UNKNOWN


def test_wrong_target_category_is_typed_unknown_not_silently_accepted() -> None:
    """Wrong Target Category (P6-RR-R23 Fixture item 4): `Jailbreak` is a
    genuinely known official label (present in `_MAPPING`), but a
    caller-scoped Output-Candidate mapping (mirroring `Qwen3GuardManifest.
    category_mapping_for(OUTPUT_CANDIDATE)`, which never includes
    `Jailbreak`) must still reject it as unknown — never silently accept
    an Input-only label on Output."""
    output_scoped_mapping = {"Privacy": CATEGORY_SECRET}  # Jailbreak deliberately excluded
    result = decode_qwen3guard_output(
        raw_text="Safety: Unsafe\nCategories: Jailbreak\nRefusal: No",
        target=Qwen3GuardTarget.OUTPUT_CANDIDATE,
        category_mapping=output_scoped_mapping,
        model_id=_MODEL,
        exact_revision=_REVISION,
        artifact_digest_sha512=_DIGEST,
    )
    assert result.failure is SafetyModelFailureKind.UNKNOWN_LABEL
    assert result.detections[0].outcome is DetectionOutcome.UNKNOWN


def test_contract_manifest_digest_is_carried_onto_the_classification() -> None:
    result = decode_qwen3guard_output(
        raw_text="Safety: Safe\nCategories: None",
        target=Qwen3GuardTarget.INPUT,
        category_mapping=_MAPPING,
        model_id=_MODEL,
        exact_revision=_REVISION,
        artifact_digest_sha512=_DIGEST,
        contract_manifest_digest_sha512="c" * 128,
    )
    assert result.contract_manifest_digest_sha512 == "c" * 128


@dataclass(frozen=True)
class _Usage:
    completion_tokens: int = 9


@dataclass(frozen=True)
class _Generated:
    content: str
    usage: _Usage | None = _Usage()


class _FakeService:
    def __init__(self, content: str | BaseException) -> None:
        self.content = content
        self.requests: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> _Generated:
        self.requests.append(request)
        if isinstance(self.content, BaseException):
            raise self.content
        return _Generated(self.content)


def _write_manifest(path: Path, *, verified: bool = True) -> None:
    """P6-RR-R27 (resolves P6-CODEX-090): when `verified=True`, the
    written Manifest must match `qwen3guard_manifest`'s own `_EXPECTED_*`
    Exact Contract constants exactly, or Construction itself now fails
    (the Cross-field Validator) — `_MODEL` (used as `provider_id` here)
    is asserted equal to the real expected value below so this fixture
    can never silently drift out of sync with the Adapter's own
    Construction-time `provider_id`/`model_id` match requirement (item 3)."""
    assert _MODEL == _manifest_module._EXPECTED_PROVIDER_ID
    category_mapping = {
        label: label.lower().replace(" ", "_").replace("&", "and")
        for label in _manifest_module._EXPECTED_CATEGORY_UNION
    }
    manifest = {
        "schema_version": "1",
        "provider_id": _MODEL,
        "label_schema_id": _manifest_module._EXPECTED_LABEL_SCHEMA_ID,
        "verified_official_contract": verified,
        "retrieval_status": "test_fixture",
        "huggingface_source": {
            "repository": _manifest_module._OFFICIAL_HUGGINGFACE_REPOSITORY,
            "source_url": "https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B",
            "exact_revision": ("a" * 40) if verified else None,
            "source_file": "tokenizer_config.json",
            "source_sha512": ("a" * 128) if verified else None,
        },
        "github_source": {
            "repository": _manifest_module._OFFICIAL_GITHUB_REPOSITORY,
            "source_url": "https://github.com/QwenLM/Qwen3Guard",
            "exact_revision": ("d" * 40) if verified else None,
            "source_file": "README.md",
            "source_sha512": ("e" * 128) if verified else None,
        },
        "input_context_categories": list(_manifest_module._EXPECTED_INPUT_CONTEXT_CATEGORIES),
        "output_candidate_categories": list(_manifest_module._EXPECTED_OUTPUT_CANDIDATE_CATEGORIES),
        "category_id_mapping": category_mapping,
    }
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _adapter(
    content: str | BaseException, *, verified: bool = True, tmp_path: Path
) -> tuple[Qwen3GuardGenAdapter, _FakeService]:
    service = _FakeService(content)
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, verified=verified)
    return (
        Qwen3GuardGenAdapter(
            service=service,  # type: ignore[arg-type]
            model_id=_MODEL,
            artifact_digest_sha512=_DIGEST,
            manifest_path=manifest_path,
        ),
        service,
    )


def test_output_candidate_binding_uses_user_then_assistant_roles(tmp_path: Path) -> None:
    adapter, service = _adapter("Safety: Safe\nCategories: None\nRefusal: No", tmp_path=tmp_path)
    result = adapter.classify_point(
        target=Qwen3GuardTarget.OUTPUT_CANDIDATE,
        query="user question",
        content="candidate answer",
    )
    assert result.target is Qwen3GuardTarget.OUTPUT_CANDIDATE
    assert [message.role.value for message in service.requests[0].messages] == [
        "user",
        "assistant",
    ]
    assert [message.content for message in service.requests[0].messages] == [
        "user question",
        "candidate answer",
    ]
    assert result.contract_manifest_digest_sha512 == adapter.manifest_digest_sha512


def test_output_candidate_rejects_input_only_jailbreak_category(tmp_path: Path) -> None:
    """Wrong Target Category, end-to-end through the real Adapter+Manifest
    pipeline (P6-RR-R23 Fixture item 4): the fixture Manifest's
    `output_candidate_categories` never includes `Jailbreak` (mirroring
    the real checked-in Manifest's official Category Set), so the Adapter
    must reject it exactly like an Unknown label — never silently accept
    an Input-only label on an Output Candidate."""
    adapter, _ = _adapter("Safety: Unsafe\nCategories: Jailbreak\nRefusal: No", tmp_path=tmp_path)
    result = adapter.classify_point(target=Qwen3GuardTarget.OUTPUT_CANDIDATE, content="x")
    assert result.failure is SafetyModelFailureKind.UNKNOWN_LABEL
    assert result.detections[0].outcome is DetectionOutcome.UNKNOWN


def test_timeout_and_malformed_are_typed_unknown_never_safe(tmp_path: Path) -> None:
    timeout_adapter, _ = _adapter(TimeoutError(), tmp_path=tmp_path)
    malformed_adapter, _ = _adapter("not the line protocol", tmp_path=tmp_path)
    for adapter, failure in (
        (timeout_adapter, SafetyModelFailureKind.TIMEOUT),
        (malformed_adapter, SafetyModelFailureKind.MALFORMED_RESPONSE),
    ):
        result = adapter.classify_point(target=Qwen3GuardTarget.INPUT, content="x")
        assert result.failure is failure
        assert result.detections[0].outcome is DetectionOutcome.UNKNOWN


def test_unverified_production_contract_is_unavailable_without_model_call(
    tmp_path: Path,
) -> None:
    adapter, service = _adapter("Safety: Safe\nCategories: None", verified=False, tmp_path=tmp_path)
    with pytest.raises(SafetyModelUnavailable):
        adapter.classify(content="x")
    assert service.requests == []


def test_bridge_adds_model_detection_without_erasing_deterministic_match(
    tmp_path: Path,
) -> None:
    adapter, _ = _adapter("Safety: Safe\nCategories: None", tmp_path=tmp_path)
    model_detection = SafetyModelDetectorAdapter(safety_model=adapter).detect(content="x")
    deterministic = GuardDetection(
        detection_id="deterministic-1",
        detector_id="deterministic.secret_pattern",
        category_id=CATEGORY_SECRET,
        outcome=DetectionOutcome.MATCH,
        severity=Severity.CRITICAL,
    )
    merged = (deterministic, model_detection)
    assert model_detection.outcome is DetectionOutcome.CLEAR
    assert any(item.outcome is DetectionOutcome.MATCH for item in merged)
    assert merged[0] == deterministic
