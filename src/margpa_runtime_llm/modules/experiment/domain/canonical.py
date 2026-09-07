"""The one shared Canonical JSON encoder for every Digest in this module
(Design §5: "Canonical JSONとDigest規約を一つにし, Dict順序、時刻または
Process固有値で同一PlanのDigestが揺れないようにする"). Deliberately not
imported from `modules.audit_evidence`: that module's own
`canonical_json_bytes` is an unrelated bounded context's encoder for a
different Contract family -- Experiment Core pins its own copy of the
same policy (UTF-8, lexicographic key sort, compact separators,
NaN/Infinity rejected) once, here, so every Digest in this module shares
exactly one definition without depending on `audit_evidence`."""

from __future__ import annotations

import json


def canonical_json_bytes(payload: dict[str, object]) -> bytes:
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except ValueError as error:
        raise ValueError("payload contains a non-finite number") from error
