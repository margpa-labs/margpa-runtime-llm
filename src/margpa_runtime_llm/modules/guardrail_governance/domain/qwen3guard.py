"""Typed Qwen3Guard-Gen output contract and strict decoder."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .results import DetectionOutcome, GuardDetection, Severity
from .safety_model import SafetyModelFailureKind
from .taxonomy import CATEGORY_UNKNOWN_UNRESOLVED, CATEGORY_UNSAFE_CONTENT


class Qwen3GuardTarget(StrEnum):
    INPUT = "guardrail.input"
    OUTPUT_CANDIDATE = "guardrail.output_candidate"
    CONTEXT_SOURCE = "guardrail.context_source"


class Qwen3GuardSafety(StrEnum):
    SAFE = "Safe"
    CONTROVERSIAL = "Controversial"
    UNSAFE = "Unsafe"


class Qwen3GuardRefusal(StrEnum):
    YES = "Yes"
    NO = "No"


class Qwen3GuardClassification(ImmutableContract):
    model_id: str = Field(min_length=1, max_length=128)
    exact_revision: str = Field(min_length=1, max_length=128)
    artifact_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    label_schema_id: str = Field(min_length=1, max_length=128)
    # P6-RR-R23 (Post-Codex Independent Review Rework, resolves P6-CODEX-087
    # contract item 6): the exact checked-in `manifest.json`'s own content
    # digest — pins precisely which Contract Manifest (Category Set, Line
    # Protocol, official Source Identity) this specific Classification was
    # produced under, independent of `exact_revision` (the upstream Model
    # Repository's own revision).
    contract_manifest_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    target: Qwen3GuardTarget
    safety: Qwen3GuardSafety | None = None
    categories: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    mapped_category_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    refusal: Qwen3GuardRefusal | None = None
    detections: tuple[GuardDetection, ...] = Field(default_factory=tuple, max_length=64)
    failure: SafetyModelFailureKind = SafetyModelFailureKind.NONE
    latency_ms: int = Field(default=0, ge=0)
    call_count: int = Field(default=1, ge=0)
    token_count: int = Field(default=0, ge=0)


@dataclass(frozen=True, slots=True)
class Qwen3GuardDecodeError(Exception):
    reason: str

    def __str__(self) -> str:
        return f"Qwen3Guard output decode failed: {self.reason}"


_DEFAULT_LABEL_SCHEMA_ID = "qwen3guard_gen_frozen_line_protocol_v1"


def decode_qwen3guard_output(
    *,
    raw_text: str,
    target: Qwen3GuardTarget,
    category_mapping: dict[str, str],
    model_id: str,
    exact_revision: str,
    artifact_digest_sha512: str | None,
    contract_manifest_digest_sha512: str | None = None,
    # P6-RR-R27 (Post-Codex Independent Review Rework, resolves the
    # `label_schema_id` half of P6-CODEX-090): previously hardcoded at
    # both `Qwen3GuardClassification(...)` construction sites below —
    # `Qwen3GuardGenAdapter` now projects this from its own verified
    # Manifest (`manifest.label_schema_id`, itself already constrained to
    # `_EXPECTED_LABEL_SCHEMA_ID` by the Manifest's own Cross-field
    # Validator) rather than a second, independent literal that could
    # silently drift out of sync with the Manifest's own claim. The
    # default here exists only for direct-Decoder callers (Tests) that
    # never construct a Manifest at all.
    label_schema_id: str = _DEFAULT_LABEL_SCHEMA_ID,
    latency_ms: int = 0,
    token_count: int = 0,
) -> Qwen3GuardClassification:
    """Decode only the frozen Gen line protocol; never infer unknown values."""
    stripped = raw_text.strip()
    if not stripped:
        raise Qwen3GuardDecodeError("empty_output")
    lines = stripped.splitlines()
    if any(not line or line != line.strip() for line in lines):
        raise Qwen3GuardDecodeError("non_canonical_whitespace_or_blank_line")
    parsed: list[tuple[str, str]] = []
    for line in lines:
        if line.count(": ") != 1:
            raise Qwen3GuardDecodeError("line_must_contain_one_colon_space")
        field, value = line.split(": ", 1)
        if not value:
            raise Qwen3GuardDecodeError("empty_field_value")
        parsed.append((field, value))
    fields = [field for field, _ in parsed]
    if len(fields) != len(set(fields)):
        raise Qwen3GuardDecodeError("duplicate_field")
    allowed = {"Safety", "Categories"}
    if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
        allowed.add("Refusal")
    if set(fields) - allowed:
        raise Qwen3GuardDecodeError("unexpected_field")
    if not fields or fields[0] != "Safety":
        raise Qwen3GuardDecodeError("safety_must_be_first")
    # P6-RR-R23 (Post-Codex Independent Review Rework, resolves the
    # Decoder-Contract half of P6-CODEX-087): `Categories` is now
    # unconditionally required for both Targets, matching Qwen's own
    # official `tokenizer_config.json` Chat Template instructions ("The
    # second line should start with 'Categories:' ... If the content is
    # safe, use 'Categories: None'.") — a Safe result with `Categories`
    # simply omitted (the previous behavior here) silently accepted an
    # incomplete Line Protocol the official Contract never permits.
    expected_order = ["Safety", "Categories"]
    if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
        expected_order.append("Refusal")
    if fields != expected_order:
        raise Qwen3GuardDecodeError("field_order_or_presence_mismatch")

    values = dict(parsed)
    try:
        safety = Qwen3GuardSafety(values["Safety"])
    except ValueError:
        raise Qwen3GuardDecodeError("unknown_safety_label") from None
    refusal: Qwen3GuardRefusal | None = None
    if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
        try:
            refusal = Qwen3GuardRefusal(values["Refusal"])
        except ValueError:
            raise Qwen3GuardDecodeError("unknown_refusal_label") from None

    category_value = values.get("Categories")
    categories = () if category_value in (None, "None") else tuple(category_value.split(", "))
    if any(not category or category.strip() != category for category in categories):
        raise Qwen3GuardDecodeError("malformed_categories")
    if len(categories) != len(set(categories)):
        raise Qwen3GuardDecodeError("duplicate_category")
    if safety is Qwen3GuardSafety.SAFE and categories:
        raise Qwen3GuardDecodeError("safe_output_must_not_list_risk_categories")
    unknown = tuple(category for category in categories if category not in category_mapping)
    mapped = tuple(
        dict.fromkeys(category_mapping[item] for item in categories if item not in unknown)
    )
    if unknown:
        return Qwen3GuardClassification(
            model_id=model_id,
            exact_revision=exact_revision,
            artifact_digest_sha512=artifact_digest_sha512,
            contract_manifest_digest_sha512=contract_manifest_digest_sha512,
            label_schema_id=label_schema_id,
            target=target,
            safety=safety,
            categories=categories,
            mapped_category_ids=mapped,
            refusal=refusal,
            detections=(
                _detection(
                    category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                    outcome=DetectionOutcome.UNKNOWN,
                ),
            ),
            failure=SafetyModelFailureKind.UNKNOWN_LABEL,
            latency_ms=latency_ms,
            token_count=token_count,
        )
    detections: tuple[GuardDetection, ...]
    if safety is Qwen3GuardSafety.SAFE:
        detections = (
            _detection(category_id=CATEGORY_UNSAFE_CONTENT, outcome=DetectionOutcome.CLEAR),
        )
    else:
        category_ids = mapped or (CATEGORY_UNSAFE_CONTENT,)
        severity = Severity.MODERATE if safety is Qwen3GuardSafety.CONTROVERSIAL else Severity.HIGH
        detections = tuple(
            _detection(
                category_id=category_id,
                outcome=DetectionOutcome.MATCH,
                severity=severity,
            )
            for category_id in category_ids
        )
    return Qwen3GuardClassification(
        model_id=model_id,
        exact_revision=exact_revision,
        artifact_digest_sha512=artifact_digest_sha512,
        contract_manifest_digest_sha512=contract_manifest_digest_sha512,
        label_schema_id=label_schema_id,
        target=target,
        safety=safety,
        categories=categories,
        mapped_category_ids=mapped,
        refusal=refusal,
        detections=detections,
        latency_ms=latency_ms,
        token_count=token_count,
    )


def _detection(
    *,
    category_id: str,
    outcome: DetectionOutcome,
    severity: Severity = Severity.NONE,
) -> GuardDetection:
    return GuardDetection(
        detection_id=str(uuid4()),
        detector_id="safety_model.qwen3guard_gen",
        category_id=category_id,
        outcome=outcome,
        severity=severity,
    )
