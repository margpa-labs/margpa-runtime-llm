"""Fast checks for the Phase 1 package metadata."""

import margpa_runtime_llm


def test_package_import_and_placeholder_version() -> None:
    assert margpa_runtime_llm.__version__ == "0.0.0"
