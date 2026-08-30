"""Phase 7 (P7-G): Data Controls — Source Class, Retention facts, and
per-Purpose Consent, kept structurally separate (ADR-7-006: "Conversation
保存、Evaluation、Dataset Export、将来Trainingを一つのONへまとめない").

`DataRetentionFacts` documents *actual current system behavior* — it is
read-only, not a user-adjustable setting, because no TTL/retention-limit
mechanism exists anywhere in this codebase to back an adjustable value
(honest MVP scope, not a placeholder for a feature this Task doesn't
build). `DataControlConsent` is the genuinely adjustable, persisted part:
independent per-Purpose opt-in flags, all Default OFF (P7-REQ-019).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract


class SourceClass(StrEnum):
    """P7-REQ-020."""

    PUBLIC_WEB = "public_web"
    LOCAL_CORPUS = "local_corpus"
    PUBLIC_PROJECT_CORPUS = "public_project_corpus"
    USER_PROVIDED = "user_provided"
    HUMAN_FEEDBACK = "human_feedback"
    SYNTHETIC_GENERATED = "synthetic_generated"
    PARTNER_LICENSED = "partner_licensed"
    """Schema Seam only — Unavailable in Phase 7 (Requirements §3)."""


class RetentionFact(ImmutableContract):
    source_class: SourceClass
    retained: bool
    description: str


DATA_RETENTION_FACTS: tuple[RetentionFact, ...] = (
    RetentionFact(
        source_class=SourceClass.USER_PROVIDED,
        retained=True,
        description=(
            "Conversation Turnは local SQLite Storeへ無期限保存される"
            "(Phase 2 Persistent Conversation。TTL/自動削除機構は未実装)。"
        ),
    ),
    RetentionFact(
        source_class=SourceClass.LOCAL_CORPUS,
        retained=True,
        description=(
            "Local Corpus Documentは登録したRevisionを含め無期限保存される"
            "(P7-B。削除はSoft-deleteでHistorical Evidenceを保持)。"
        ),
    ),
    RetentionFact(
        source_class=SourceClass.PUBLIC_WEB,
        retained=False,
        description=(
            "Web Search/Fetch結果はHTTP Responseとしてのみ返され、"
            "Server側には一切永続化されない(P7-E/F)。"
        ),
    ),
    RetentionFact(
        source_class=SourceClass.HUMAN_FEEDBACK,
        retained=False,
        description="Feedback収集機構自体が本Projectに未実装のため、保存対象が存在しない。",
    ),
    RetentionFact(
        source_class=SourceClass.SYNTHETIC_GENERATED,
        retained=False,
        description="Synthetic Data生成機構自体が本Projectに未実装のため、保存対象が存在しない。",
    ),
)


class DataControlConsent(ImmutableContract):
    """All Default OFF (P7-REQ-019). Saving `True` here is a stored Consent
    Preference only — it never means Training/Weight-update happened
    (P7-REQ-021); no Training pipeline exists in this Project to consume
    this flag yet."""

    schema_version: Literal["1"] = "1"
    external_query_transmission_consent: bool = False
    """Consent to send raw Chat/Search query text to an external Web
    Search Provider when Web Search is explicitly used (P7-E). Independent
    of whether Web Search itself is toggled ON — this documents *consent*,
    the Search Toggle documents *activation*."""

    feedback_research_use: bool = False
    synthetic_data_use: bool = False
    future_training_export: bool = False
    updated_at: datetime


class DataControlConsentUpdate(ImmutableContract):
    """Partial update — every field optional; unset fields are unchanged."""

    external_query_transmission_consent: bool | None = None
    feedback_research_use: bool | None = None
    synthetic_data_use: bool | None = None
    future_training_export: bool | None = None


class DataControlPolicySnapshot(ImmutableContract):
    consent: DataControlConsent
    retention_facts: tuple[RetentionFact, ...] = Field(default=DATA_RETENTION_FACTS)
