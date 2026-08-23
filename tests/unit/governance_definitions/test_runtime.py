"""GovernanceDefinitionsRuntime: off never touches the Provider, observe
runs the full pipeline, mode transitions are safe (P3-F-WU-002)."""

from __future__ import annotations

import threading

import pytest

from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.application import (
    EmptyDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeTransitionError,
)
from margpa_runtime_llm.modules.governance_definitions.ports import (
    PackageLoadRequest,
    PackageSourceResult,
    ProviderDescriptor,
)
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
    GovernanceObservePipelineError,
)


class _CountingProvider:
    def __init__(self) -> None:
        self.describe_calls = 0
        self.load_package_calls = 0

    def describe(self) -> ProviderDescriptor:
        self.describe_calls += 1
        from margpa_runtime_llm.modules.governance_definitions.domain import ProviderState

        return ProviderDescriptor(
            provider_id="counting-provider", provider_kind="test", state=ProviderState.EMPTY
        )

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult:
        self.load_package_calls += 1
        return PackageSourceResult(found=False, reason_code="provider_has_no_packages")


def _runtime(provider: object | None = None) -> GovernanceDefinitionsRuntime:
    return GovernanceDefinitionsRuntime(
        provider=provider or EmptyDefinitionProvider(),  # type: ignore[arg-type]
        registry=TrustedAdapterRegistry(),
    )


def test_off_mode_never_calls_the_provider() -> None:
    counting = _CountingProvider()
    runtime = _runtime(counting)

    runtime.mode_snapshot()
    runtime.status()

    assert counting.describe_calls == 0
    assert counting.load_package_calls == 0


def test_default_mode_is_off() -> None:
    runtime = _runtime()
    assert runtime.mode_snapshot().current_mode is GovernanceMode.OFF


def test_transition_to_observe_calls_the_provider_exactly_once() -> None:
    counting = _CountingProvider()
    runtime = _runtime(counting)

    runtime.apply_mode(GovernanceMode.OBSERVE)

    assert counting.describe_calls == 1
    assert counting.load_package_calls == 1


def test_transition_to_enforce_raises_and_leaves_mode_unchanged() -> None:
    runtime = _runtime()
    with pytest.raises(GovernanceModeTransitionError):
        runtime.apply_mode(GovernanceMode.ENFORCE)
    assert runtime.mode_snapshot().current_mode is GovernanceMode.OFF


def test_status_reflects_empty_provider_after_observe() -> None:
    runtime = _runtime()
    runtime.apply_mode(GovernanceMode.OBSERVE)

    status = runtime.status()
    assert status.mode.current_mode is GovernanceMode.OBSERVE
    assert status.observe_summary is not None
    assert status.observe_summary.package_found is False


def test_returning_to_off_clears_the_observe_summary() -> None:
    runtime = _runtime()
    runtime.apply_mode(GovernanceMode.OBSERVE)
    assert runtime.status().observe_summary is not None

    runtime.apply_mode(GovernanceMode.OFF)
    assert runtime.status().observe_summary is None


def test_redundant_apply_does_not_bump_revision_or_recall_provider() -> None:
    counting = _CountingProvider()
    runtime = _runtime(counting)
    runtime.apply_mode(GovernanceMode.OBSERVE)
    revision_after_first = runtime.mode_snapshot().revision
    calls_after_first = counting.load_package_calls

    runtime.apply_mode(GovernanceMode.OBSERVE)  # already observe — no-op

    assert runtime.mode_snapshot().revision == revision_after_first
    assert counting.load_package_calls == calls_after_first


# -- P3-CODEX-003: build-before-commit atomicity — a Provider/Adapter/
# Reader/Compiler fault must leave Mode/Revision/Summary untouched and
# never leak a raw exception. -------------------------------------------


class _FailingProvider:
    def describe(self) -> ProviderDescriptor:
        from margpa_runtime_llm.modules.governance_definitions.domain import ProviderState

        return ProviderDescriptor(
            provider_id="failing-provider", provider_kind="test", state=ProviderState.READY
        )

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult:
        del request
        raise RuntimeError("simulated provider fault")


def test_a_provider_fault_during_observe_never_leaks_raw_and_leaves_state_untouched() -> None:
    runtime = _runtime(_FailingProvider())
    before = runtime.mode_snapshot()

    with pytest.raises(GovernanceObservePipelineError) as excinfo:
        runtime.apply_mode(GovernanceMode.OBSERVE)

    assert "RuntimeError" not in str(excinfo.value)
    assert "simulated provider fault" not in str(excinfo.value)
    after = runtime.mode_snapshot()
    assert after.current_mode is GovernanceMode.OFF
    assert after.revision == before.revision
    assert runtime.status().observe_summary is None


class _FlakyProvider:
    """Succeeds once, then faults — models a Provider that becomes
    unavailable between two OBSERVE attempts on the same Runtime."""

    def __init__(self) -> None:
        self._calls = 0

    def describe(self) -> ProviderDescriptor:
        from margpa_runtime_llm.modules.governance_definitions.domain import ProviderState

        return ProviderDescriptor(
            provider_id="flaky-provider", provider_kind="test", state=ProviderState.EMPTY
        )

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult:
        del request
        self._calls += 1
        if self._calls == 1:
            return PackageSourceResult(found=False, reason_code="empty")
        raise RuntimeError("simulated fault on the second load")


def test_a_fault_on_reobserve_leaves_off_and_never_resurrects_the_prior_summary() -> None:
    runtime = _runtime(_FlakyProvider())
    runtime.apply_mode(GovernanceMode.OBSERVE)
    assert runtime.status().observe_summary is not None

    runtime.apply_mode(GovernanceMode.OFF)
    assert runtime.status().observe_summary is None

    with pytest.raises(GovernanceObservePipelineError):
        runtime.apply_mode(GovernanceMode.OBSERVE)  # the Provider now faults

    after = runtime.status()
    assert after.mode.current_mode is GovernanceMode.OFF
    assert after.observe_summary is None


def test_concurrent_apply_calls_are_serialized_and_leave_a_consistent_final_state() -> None:
    runtime = _runtime()
    errors: list[BaseException] = []
    barrier = threading.Barrier(4)

    def worker(mode: GovernanceMode) -> None:
        barrier.wait(timeout=5.0)
        try:
            runtime.apply_mode(mode)
        except GovernanceModeTransitionError:
            pass
        except BaseException as error:
            errors.append(error)

    threads = [
        threading.Thread(target=worker, args=(mode,))
        for mode in (
            GovernanceMode.OBSERVE,
            GovernanceMode.OFF,
            GovernanceMode.OBSERVE,
            GovernanceMode.OFF,
        )
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5.0)

    assert errors == []
    final = runtime.mode_snapshot()
    assert final.current_mode in (GovernanceMode.OFF, GovernanceMode.OBSERVE)
    # Every committed transition bumps the revision by exactly 1 — the
    # lock must never allow two threads to observe-then-both-commit the
    # same base revision (which would corrupt the digest/revision pairing).
    from margpa_runtime_llm.modules.governance_definitions.domain import (
        governance_mode_digest,
    )

    assert final.digest_sha512 == governance_mode_digest(
        revision=final.revision, current_mode=final.current_mode
    )
