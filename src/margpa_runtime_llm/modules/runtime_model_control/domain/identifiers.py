"""Enums for Runtime Model Control (Phase 6 Architecture 3.1/3.2/3.3)."""

from enum import StrEnum


class ModelRole(StrEnum):
    MAIN = "main"
    JUDGE = "judge"
    GUARD = "guard"


class RuntimeState(StrEnum):
    IDLE = "idle"
    LOADING = "loading"
    ACTIVE = "active"
    UNLOADING = "unloading"
    SWITCHING = "switching"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class BindingState(StrEnum):
    UNBOUND = "unbound"
    BOUND = "bound"
    UNAVAILABLE = "unavailable"


class IndependenceClass(StrEnum):
    SHARED_ARTIFACT = "shared_artifact"
    INDEPENDENT_ARTIFACT = "independent_artifact"
    UNAVAILABLE = "unavailable"


class SwitchOutcome(StrEnum):
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED_UNAVAILABLE = "failed_unavailable"
