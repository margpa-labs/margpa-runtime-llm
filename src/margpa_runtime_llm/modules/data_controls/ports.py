"""Phase 7 (P7-G): replaceable storage boundary for Data Control Consent."""

from __future__ import annotations

from typing import Protocol

from .contracts import DataControlConsent, DataControlConsentUpdate


class DataControlConsentStorePort(Protocol):
    def get(self) -> DataControlConsent: ...

    def update(self, patch: DataControlConsentUpdate) -> DataControlConsent: ...

    def reset_to_defaults(self) -> DataControlConsent: ...
