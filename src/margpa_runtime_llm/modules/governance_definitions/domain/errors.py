"""Safe errors for the governance-definitions domain."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

type GovernanceDefinitionSafeDetail = str | int | float | bool | None


class GovernanceDefinitionErrorCode(StrEnum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    INVALID_PACKAGE_REQUEST = "invalid_package_request"
    UNSUPPORTED_SCHEMA = "unsupported_schema"


class GovernanceDefinitionError(Exception):
    """Storage/provider-independent error; never carries a raw path or exception."""

    def __init__(
        self,
        *,
        code: GovernanceDefinitionErrorCode,
        safe_message: str,
        details: Mapping[str, GovernanceDefinitionSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.details: Mapping[str, GovernanceDefinitionSafeDetail] = MappingProxyType(
            dict(details or {})
        )

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "details": dict(self.details),
        }
