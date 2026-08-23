"""EmptyDefinitionProvider: definitions=0 is a valid Baseline, not a failure
or an unavailable state (P3-C-WU-002)."""

from __future__ import annotations

from margpa_runtime_llm.modules.governance_definitions.application import (
    EmptyDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import ProviderState
from margpa_runtime_llm.modules.governance_definitions.ports import (
    DefinitionProviderPort,
    PackageLoadRequest,
)


def test_empty_provider_satisfies_the_port_protocol() -> None:
    assert isinstance(EmptyDefinitionProvider(), DefinitionProviderPort)


def test_empty_provider_reports_empty_not_unavailable_or_failed() -> None:
    descriptor = EmptyDefinitionProvider().describe()
    # `is EMPTY` alone already proves it is neither UNAVAILABLE nor FAILED —
    # ProviderState is a closed enum, so this one identity check subsumes
    # the pairwise-distinct assertions P3-PRV-007 cares about.
    assert descriptor.state is ProviderState.EMPTY
    assert descriptor.unavailable_reason_code is None


def test_empty_provider_load_package_reports_not_found_without_raising() -> None:
    result = EmptyDefinitionProvider().load_package(PackageLoadRequest())
    assert result.found is False
    assert result.package_state is None
    assert result.manifest is None
    assert result.reason_code == "provider_has_no_packages"


def test_empty_provider_load_package_ignores_requested_package_id() -> None:
    result = EmptyDefinitionProvider().load_package(
        PackageLoadRequest(requested_package_id="anything")
    )
    assert result.found is False
