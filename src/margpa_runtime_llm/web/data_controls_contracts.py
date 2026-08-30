"""Bounded HTTP contracts for Data Controls (P7-G)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.data_controls.contracts import (
    DataControlConsent,
    DataControlPolicySnapshot,
    RetentionFact,
)


class _DataControlsContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DataControlConsentUpdateRequest(_DataControlsContract):
    external_query_transmission_consent: bool | None = None
    feedback_research_use: bool | None = None
    synthetic_data_use: bool | None = None
    future_training_export: bool | None = None


class DataControlConsentResponse(_DataControlsContract):
    external_query_transmission_consent: bool
    feedback_research_use: bool
    synthetic_data_use: bool
    future_training_export: bool
    updated_at: datetime


class RetentionFactResponse(_DataControlsContract):
    source_class: str
    retained: bool
    description: str


class DataControlPolicyResponse(_DataControlsContract):
    consent: DataControlConsentResponse
    retention_facts: tuple[RetentionFactResponse, ...]


def project_consent(value: DataControlConsent) -> DataControlConsentResponse:
    return DataControlConsentResponse(
        external_query_transmission_consent=value.external_query_transmission_consent,
        feedback_research_use=value.feedback_research_use,
        synthetic_data_use=value.synthetic_data_use,
        future_training_export=value.future_training_export,
        updated_at=value.updated_at,
    )


def project_policy(value: DataControlPolicySnapshot) -> DataControlPolicyResponse:
    return DataControlPolicyResponse(
        consent=project_consent(value.consent),
        retention_facts=tuple(_project_fact(fact) for fact in value.retention_facts),
    )


def _project_fact(fact: RetentionFact) -> RetentionFactResponse:
    return RetentionFactResponse(
        source_class=fact.source_class.value,
        retained=fact.retained,
        description=fact.description,
    )
