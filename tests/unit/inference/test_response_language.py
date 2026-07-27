"""Response language resolution and message composition tests."""

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
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
from margpa_runtime_llm.orchestration.response_language import (
    ENGLISH_RESPONSE_INSTRUCTION,
    JAPANESE_RESPONSE_INSTRUCTION,
    compose_generation_messages,
    resolve_response_policy,
)


@pytest.mark.parametrize(
    ("language", "user_system", "expected_system"),
    [
        (ResponseLanguage.JA, None, JAPANESE_RESPONSE_INSTRUCTION),
        (
            ResponseLanguage.JA,
            "User system",
            f"{JAPANESE_RESPONSE_INSTRUCTION}\n\nUser system",
        ),
        (ResponseLanguage.EN, None, ENGLISH_RESPONSE_INSTRUCTION),
        (
            ResponseLanguage.EN,
            "User system",
            f"{ENGLISH_RESPONSE_INSTRUCTION}\n\nUser system",
        ),
        (ResponseLanguage.AUTO, None, None),
        (ResponseLanguage.AUTO, "User system", "User system"),
    ],
)
def test_message_composition_matrix_preserves_user_content(
    language: ResponseLanguage,
    user_system: str | None,
    expected_system: str | None,
) -> None:
    prompt = "  Preserve this user prompt exactly.  "
    messages = compose_generation_messages(
        user_prompt=prompt,
        user_system_message=user_system,
        policy=ResolvedResponseLanguagePolicy(
            language=language,
            source=ResponseLanguageSource.EXPLICIT,
        ),
    )

    assert messages[-1].role is MessageRole.USER
    assert messages[-1].content == prompt
    if expected_system is None:
        assert len(messages) == 1
    else:
        assert len(messages) == 2
        assert messages[0].role is MessageRole.SYSTEM
        assert messages[0].content == expected_system
        if user_system is not None:
            assert user_system in messages[0].content


def test_response_policy_precedence_and_source_tracking() -> None:
    application = ResponsePolicyConfig(language=ResponseLanguage.JA)

    built_in = resolve_response_policy(
        application_policy=None,
        environment={},
        explicit_language=None,
    )
    application_default = resolve_response_policy(
        application_policy=application,
        environment={},
        explicit_language=None,
    )
    environment = resolve_response_policy(
        application_policy=application,
        environment={"MARGPA_RESPONSE_LANGUAGE": "en"},
        explicit_language=None,
    )
    explicit = resolve_response_policy(
        application_policy=application,
        environment={"MARGPA_RESPONSE_LANGUAGE": "en"},
        explicit_language=ResponseLanguage.AUTO,
    )

    assert (built_in.language, built_in.source) == (
        ResponseLanguage.JA,
        ResponseLanguageSource.BUILT_IN_DEFAULT,
    )
    assert (application_default.language, application_default.source) == (
        ResponseLanguage.JA,
        ResponseLanguageSource.APPLICATION,
    )
    assert (environment.language, environment.source) == (
        ResponseLanguage.EN,
        ResponseLanguageSource.ENVIRONMENT,
    )
    assert (explicit.language, explicit.source) == (
        ResponseLanguage.AUTO,
        ResponseLanguageSource.EXPLICIT,
    )


def test_unknown_response_language_is_rejected_without_alias_guessing() -> None:
    with pytest.raises(ValidationError):
        ResponsePolicyConfig.model_validate({"language": "jp"})

    with pytest.raises(InferenceError) as captured:
        resolve_response_policy(
            application_policy=ResponsePolicyConfig(),
            environment={"MARGPA_RESPONSE_LANGUAGE": "jp"},
            explicit_language=None,
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION
