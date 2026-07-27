"""Backend-independent response language policy contracts."""

from enum import StrEnum

from .base import ImmutableContract


class ResponseLanguage(StrEnum):
    JA = "ja"
    EN = "en"
    AUTO = "auto"


class ResponseLanguageSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    APPLICATION = "application"
    ENVIRONMENT = "environment"
    EXPLICIT = "explicit"


class ResponsePolicyConfig(ImmutableContract):
    language: ResponseLanguage = ResponseLanguage.JA


class ResolvedResponseLanguagePolicy(ImmutableContract):
    language: ResponseLanguage
    source: ResponseLanguageSource
