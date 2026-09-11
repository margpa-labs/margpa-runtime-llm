"""Read-only access to the loaded Model's Context Capacity/Tokenizer.

Wraps the SAME always-loaded base `application.service` a Conversation
Generation Attempt itself uses (`bootstrap/web_application.py`'s own
`application.service.count_text_tokens`/`runtime_info.loaded_context_size`),
never a Provider- or Path-specific value Hard-coded into the Domain Core
(Invariant 14).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ModelContextCapacityPort(Protocol):
    def loaded_context_capacity(self) -> int | None:
        """`None` exactly when no Model is currently loaded."""
        ...

    def loaded_model_identity(self) -> str | None:
        """`None` exactly when no Model is currently loaded."""
        ...

    def count_text_tokens(self, text: str) -> int | None:
        """`None` when the loaded Backend cannot count tokens right now
        (e.g. transiently busy) -- never coerced to 0 (Invariant 13)."""
        ...
