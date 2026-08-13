"""Opaque identities for the persistent conversation domain."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class _OpaqueIdentifier(ImmutableContract):
    value: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)


class ConversationScopeId(_OpaqueIdentifier):
    """Storage namespace identity; it is not an authentication credential."""


class ConversationId(_OpaqueIdentifier):
    """Identity of one persistent conversation aggregate."""


class ConversationSessionId(_OpaqueIdentifier):
    """Identity of one interaction episode with a conversation."""


class ConversationTurnId(_OpaqueIdentifier):
    """Identity of one user submission and its optional canonical result."""


class ConversationMessageId(_OpaqueIdentifier):
    """Identity of one immutable canonical message."""


class ConversationOperationId(_OpaqueIdentifier):
    """Idempotency identity for one repository commit."""
