"""Resolve backend-independent thinking presentation policy."""

from __future__ import annotations

import os
from collections.abc import Mapping

from pydantic import ValidationError

from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    DEFAULT_THINKING_DISPLAY_LABEL,
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationConfig,
    ThinkingPresentationSource,
    ThinkingVisibility,
)


def resolve_thinking_presentation_policy(
    *,
    application_policy: ThinkingPresentationConfig | None,
    environment: Mapping[str, str] | None,
    explicit_visibility: ThinkingVisibility | str | None,
    explicit_display_label: str | None,
) -> ResolvedThinkingPresentationPolicy:
    current_environment = os.environ if environment is None else environment

    visibility: ThinkingVisibility | str = ThinkingVisibility.HIDDEN
    visibility_source = ThinkingPresentationSource.BUILT_IN_DEFAULT
    display_label = DEFAULT_THINKING_DISPLAY_LABEL
    display_label_source = ThinkingPresentationSource.BUILT_IN_DEFAULT
    persistence = ThinkingPersistence.DISABLED
    persistence_source = ThinkingPresentationSource.BUILT_IN_DEFAULT

    if application_policy is not None:
        visibility = application_policy.visibility
        visibility_source = ThinkingPresentationSource.APPLICATION
        display_label = application_policy.display_label
        display_label_source = ThinkingPresentationSource.APPLICATION
        persistence = application_policy.persistence
        persistence_source = ThinkingPresentationSource.APPLICATION
    if "MARGPA_THINKING_VISIBILITY" in current_environment:
        visibility = current_environment["MARGPA_THINKING_VISIBILITY"]
        visibility_source = ThinkingPresentationSource.ENVIRONMENT
    if "MARGPA_THINKING_LABEL" in current_environment:
        display_label = current_environment["MARGPA_THINKING_LABEL"]
        display_label_source = ThinkingPresentationSource.ENVIRONMENT
    if explicit_visibility is not None:
        visibility = explicit_visibility
        visibility_source = ThinkingPresentationSource.EXPLICIT
    if explicit_display_label is not None:
        display_label = explicit_display_label
        display_label_source = ThinkingPresentationSource.EXPLICIT

    try:
        validated = ThinkingPresentationConfig(
            visibility=ThinkingVisibility(visibility),
            display_label=display_label,
            persistence=persistence,
        )
        return ResolvedThinkingPresentationPolicy(
            visibility=validated.visibility,
            display_label=validated.display_label,
            persistence=validated.persistence,
            visibility_source=visibility_source,
            display_label_source=display_label_source,
            persistence_source=persistence_source,
        )
    except (ValidationError, ValueError) as exc:
        code = (
            InferenceErrorCode.INVALID_REQUEST
            if explicit_visibility is not None or explicit_display_label is not None
            else InferenceErrorCode.INVALID_CONFIGURATION
        )
        raise InferenceError(
            code=code,
            safe_message="The thinking presentation policy is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc
