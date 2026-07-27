"""Backend-independent chat message contracts."""

from enum import StrEnum

from pydantic import field_validator

from .base import ImmutableContract


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(ImmutableContract):
    role: MessageRole
    content: str
    name: str | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message content must not be blank")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("message name must not be blank")
        return value
