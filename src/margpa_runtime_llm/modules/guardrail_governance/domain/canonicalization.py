"""Canonical SHA-512 digest of a `GuardrailResult` (P5-A-WU-002)."""

from __future__ import annotations

import hashlib
import json

from .results import GuardrailResult


def canonical_result_payload(result: GuardrailResult) -> dict[str, object]:
    return result.model_dump(mode="json")


def guardrail_result_digest_sha512(result: GuardrailResult) -> str:
    canonical = json.dumps(
        canonical_result_payload(result),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()
