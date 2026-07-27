"""Resolve response language policy and compose backend-independent messages."""

from __future__ import annotations

import os
from collections.abc import Mapping

from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationMessage,
    ConversationRole,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResolvedResponseLanguagePolicy,
    ResponseLanguage,
    ResponseLanguageSource,
    ResponsePolicyConfig,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)

JAPANESE_RESPONSE_INSTRUCTION = (
    "回答は原則として日本語で行ってください。\n"
    "ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。"
)
ENGLISH_RESPONSE_INSTRUCTION = (
    "Respond in English by default.\n"
    "If the user explicitly requests a different response language, follow that request."
)


def resolve_response_policy(
    *,
    application_policy: ResponsePolicyConfig | None,
    environment: Mapping[str, str] | None,
    explicit_language: ResponseLanguage | str | None,
) -> ResolvedResponseLanguagePolicy:
    current_environment = os.environ if environment is None else environment
    if explicit_language is not None:
        return ResolvedResponseLanguagePolicy(
            language=_validate_language(explicit_language),
            source=ResponseLanguageSource.EXPLICIT,
        )
    if "MARGPA_RESPONSE_LANGUAGE" in current_environment:
        return ResolvedResponseLanguagePolicy(
            language=_validate_language(current_environment["MARGPA_RESPONSE_LANGUAGE"]),
            source=ResponseLanguageSource.ENVIRONMENT,
        )
    if application_policy is not None:
        return ResolvedResponseLanguagePolicy(
            language=application_policy.language,
            source=ResponseLanguageSource.APPLICATION,
        )
    return ResolvedResponseLanguagePolicy(
        language=ResponseLanguage.JA,
        source=ResponseLanguageSource.BUILT_IN_DEFAULT,
    )


def compose_generation_messages(
    *,
    user_prompt: str,
    user_system_message: str | None,
    policy: ResolvedResponseLanguagePolicy,
) -> tuple[ChatMessage, ...]:
    instruction = _instruction_for(policy.language)
    system_content = _compose_system_content(instruction, user_system_message)
    messages: list[ChatMessage] = []
    if system_content is not None:
        messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_content))
    messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))
    return tuple(messages)


def compose_conversation_generation_messages(
    *,
    messages: tuple[ConversationMessage, ...],
    policy: ResolvedResponseLanguagePolicy,
) -> tuple[ChatMessage, ...]:
    """Prepend only the server-owned policy while preserving validated history order."""

    output: list[ChatMessage] = []
    instruction = _instruction_for(policy.language)
    if instruction is not None:
        output.append(ChatMessage(role=MessageRole.SYSTEM, content=instruction))
    output.extend(
        ChatMessage(
            role=(
                MessageRole.USER if message.role is ConversationRole.USER else MessageRole.ASSISTANT
            ),
            content=message.content,
        )
        for message in messages
    )
    return tuple(output)


def _validate_language(value: ResponseLanguage | str) -> ResponseLanguage:
    try:
        return ResponseLanguage(value)
    except ValueError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The configured response language is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc


def _instruction_for(language: ResponseLanguage) -> str | None:
    if language is ResponseLanguage.JA:
        return JAPANESE_RESPONSE_INSTRUCTION
    if language is ResponseLanguage.EN:
        return ENGLISH_RESPONSE_INSTRUCTION
    return None


def _compose_system_content(instruction: str | None, user_system: str | None) -> str | None:
    if instruction is None:
        return user_system
    if user_system is None:
        return instruction
    return f"{instruction}\n\n{user_system}"
