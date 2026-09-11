"""`ModelContextCapacityPort` over the always-loaded base `ModelPort`.

Reads live -- never caches `runtime_info`/token counts across calls -- so a
Runtime Model Switch (context size, tokenizer) is reflected on the very
next Budget computation, exactly like `ConversationGenerationService`'s own
`_effective_context_size`/`_text_token_counter` are re-read from the same
underlying `application.service` at Bootstrap time (never a Provider/Path
Hard-coded into this adapter, per Invariant 14).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class _LoadedModelService(Protocol):
    @property
    def runtime_info(self) -> object | None: ...

    def count_text_tokens(self, text: str) -> int: ...


class LoadedServiceModelContextAdapter:
    def __init__(self, *, service: _LoadedModelService) -> None:
        self._service = service

    def loaded_context_capacity(self) -> int | None:
        info = self._service.runtime_info
        if info is None:
            return None
        return int(info.loaded_context_size)  # type: ignore[attr-defined]

    def loaded_model_identity(self) -> str | None:
        info = self._service.runtime_info
        if info is None:
            return None
        return str(info.model_key)  # type: ignore[attr-defined]

    def count_text_tokens(self, text: str) -> int | None:
        if self._service.runtime_info is None:
            return None
        try:
            return self._service.count_text_tokens(text)
        except Exception:
            # Defense in depth (matches `_context_usage`'s own established
            # posture, conversation_generation.py): a transiently busy
            # loaded Backend degrades to Unknown for this one call, never
            # raises out of a Budget computation.
            return None
