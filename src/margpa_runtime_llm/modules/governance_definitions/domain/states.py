"""Repository state enums (architecture §5.3).

Each entity (Provider/Package/Source/Definition) has its *own* closed state
set — never collapsed into one shared status string, so e.g. a Provider
being `failed` cannot be confused with a Definition being `invalid`
(P3-PRV-007: Provider Failure and Definition-count-0 are not the same
state)."""

from enum import StrEnum


class ProviderState(StrEnum):
    NOT_CONFIGURED = "not_configured"
    UNAVAILABLE = "unavailable"
    EMPTY = "empty"
    READY = "ready"
    FAILED = "failed"


class PackageState(StrEnum):
    DISCOVERED = "discovered"
    LOADED = "loaded"
    VALIDATED = "validated"
    INVALID = "invalid"
    QUARANTINED = "quarantined"
    DISABLED = "disabled"


class SourceState(StrEnum):
    LOADED = "loaded"
    DIGEST_MISMATCH = "digest_mismatch"
    SIZE_MISMATCH = "size_mismatch"
    INVALID = "invalid"
    UNSUPPORTED = "unsupported"


class DefinitionState(StrEnum):
    VALIDATED = "validated"
    UNSUPPORTED = "unsupported"
    INVALID = "invalid"
    DISABLED = "disabled"
    NORMALIZED = "normalized"
