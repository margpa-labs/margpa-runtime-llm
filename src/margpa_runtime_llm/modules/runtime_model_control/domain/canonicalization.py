"""Canonical digest for RuntimeModelSnapshot (module-local, matches repo-wide digest convention)."""

import hashlib
import json
from typing import Any


def runtime_model_snapshot_digest(*, payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()
