"""Domain-level Failure contracts for Runtime Model Control (Architecture 3.2, 12)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimeModelRevisionConflict(Exception):
    """CAS mismatch: caller's expected (revision, digest) is stale."""

    expected_revision: int
    expected_digest: str
    current_revision: int
    current_digest: str

    def __str__(self) -> str:
        return (
            "runtime model revision conflict: "
            f"expected=({self.expected_revision}, {self.expected_digest}) "
            f"current=({self.current_revision}, {self.current_digest})"
        )


@dataclass(frozen=True, slots=True)
class RuntimeModelBusyError(Exception):
    """Switch/Reload rejected because an Active Generation lease is held (Architecture 3.2)."""

    reason: str

    def __str__(self) -> str:
        return f"runtime model busy: {self.reason}"


@dataclass(frozen=True, slots=True)
class RuntimeModelLoadFailure(Exception):
    """Candidate Load failed; caller must roll back to the Previous Runtime Receipt."""

    model_key: str
    reason: str

    def __str__(self) -> str:
        return f"runtime model load failed for {self.model_key}: {self.reason}"


@dataclass(frozen=True, slots=True)
class RuntimeModelContextLimitExceeded(Exception):
    """Requested Context Size is outside the effective range; no reload attempted."""

    requested_context_size: int
    effective_max_context_size: int
    minimum_context_size: int = 512
    reason_code: str = "outside_effective_context_range"

    def __str__(self) -> str:
        return (
            f"requested context size {self.requested_context_size} is outside "
            f"the effective range {self.minimum_context_size}.."
            f"{self.effective_max_context_size} ({self.reason_code})"
        )


@dataclass(frozen=True, slots=True)
class RuntimeModelMaxNewTokensExceeded(Exception):
    """Requested Max New Tokens exceeds max_output_token_limit (Architecture 5.2)."""

    requested_max_new_tokens: int
    max_output_token_limit: int

    def __str__(self) -> str:
        return (
            f"requested max_new_tokens {self.requested_max_new_tokens} exceeds "
            f"max_output_token_limit {self.max_output_token_limit}"
        )


@dataclass(frozen=True, slots=True)
class RuntimeModelTargetNotRegistered(Exception):
    """Requested switch `target_model_key` has no registered Definition
    (Fourth Rework, P6-CODEX-026) — never attempted as a fabricated Load."""

    target_model_key: str

    def __str__(self) -> str:
        return f"no registered model definition for target_model_key={self.target_model_key!r}"


@dataclass(frozen=True, slots=True)
class RuntimeModelRollbackFailure(Exception):
    """Rollback itself failed after a Load failure.

    Architecture 3.2: on double failure the Runtime must become Unavailable
    rather than silently reverting to an unverified previous value.
    """

    reason: str

    def __str__(self) -> str:
        return f"runtime model rollback failed, runtime is now unavailable: {self.reason}"
