"""Bounded pathological-output repetition detection for local GGUF models."""

from __future__ import annotations

import re
from dataclasses import dataclass

_MAX_OBSERVATION_CHARACTERS = 8192
_MIN_REPEATED_CHARACTERS = 192
_MIN_BLOCK_CHARACTERS = 32
_MAX_BLOCK_CHARACTERS = 512


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def detect_pathological_repetition(value: str) -> bool:
    """Return True only for a long exact suffix repeated pathologically.

    The minimum trigger is 192 normalized characters (a 32-character block
    repeated six times). Ordinary repeated words, Markdown bullets, and short
    rhetorical emphasis remain below the floor. Larger blocks need three or
    four exact consecutive copies. The scan is suffix-only and bounded.
    """

    observed = _normalized(value[-_MAX_OBSERVATION_CHARACTERS:])
    maximum_block = min(_MAX_BLOCK_CHARACTERS, len(observed) // 3)
    for block_size in range(_MIN_BLOCK_CHARACTERS, maximum_block + 1):
        copies = max(3, (_MIN_REPEATED_CHARACTERS + block_size - 1) // block_size)
        required = block_size * copies
        repeated_suffix = observed[-required:]
        block = repeated_suffix[-block_size:]
        if block.strip() and repeated_suffix == block * copies:
            return True
    return False


@dataclass(slots=True)
class PathologicalRepetitionDetector:
    _observed: str = ""
    _total_characters: int = 0
    _last_scan_total: int = 0

    def feed(self, text_delta: str) -> bool:
        self._observed = (self._observed + text_delta)[-_MAX_OBSERVATION_CHARACTERS:]
        self._total_characters += len(text_delta)
        if self._total_characters - self._last_scan_total < _MIN_BLOCK_CHARACTERS:
            return False
        self._last_scan_total = self._total_characters
        return detect_pathological_repetition(self._observed)
