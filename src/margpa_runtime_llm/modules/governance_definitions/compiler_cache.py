"""Process-local Compiled Plan Cache (architecture §7.2, P3-E-WU-002).

Cache Hit requires an *exact* key match — the key is
`plan_cache_key(compiler_input)`, which already folds in Compiler
identity/version, Definition/IR refs, Profile, Binding Candidate, and the
Capability/Authority snapshot digests (P3-CMP-004). A Cache Miss always
recompiles; nothing here re-derives or repairs a stale entry (P3-CMP-005).
"""

from __future__ import annotations

import threading

from .domain.compiler import CompiledPlan, CompilerInput, plan_cache_key


class CompiledPlanCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, CompiledPlan] = {}

    def get(self, compiler_input: CompilerInput) -> CompiledPlan | None:
        key = plan_cache_key(compiler_input)
        with self._lock:
            return self._entries.get(key)

    def put(self, compiler_input: CompilerInput, plan: CompiledPlan) -> None:
        key = plan_cache_key(compiler_input)
        with self._lock:
            self._entries[key] = plan

    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
