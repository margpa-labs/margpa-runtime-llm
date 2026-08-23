"""Shared finite resource limits for the Governance Definition Platform
(P3-PER-001, P3-CODEX-004 rework).

Every number here is a deliberately generous ceiling relative to the real
Reference Bundle (17 sources / 18 definitions, files in the tens of KB):
large enough that legitimate content never hits it, small enough that a
malformed or hostile Manifest/Source/IR/Plan cannot force unbounded
memory or CPU work. Exceeding any of these must fail closed into a Typed
Invalid/Unsupported state — never an uncaught exception.
"""

from __future__ import annotations

MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_SOURCE_ENTRY_COUNT = 2_000
MAX_DEFINITION_ENTRY_COUNT = 2_000
MAX_RELATIVE_PATH_DEPTH = 32

MAX_COLLECTION_LENGTH = 10_000
MAX_STRING_LENGTH = 65_536

MAX_IR_SECTION_COUNT = 10_000
MAX_IR_SECTION_CHILD_KEY_COUNT = MAX_COLLECTION_LENGTH

MAX_COMPILED_PLAN_ITEM_COUNT = 20_000
