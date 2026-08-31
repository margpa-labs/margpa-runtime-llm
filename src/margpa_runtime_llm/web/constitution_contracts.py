"""Local-private `/api/v2/constitution` response contracts (P8-C/P8-RW6-D)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.constitution import (
    CapabilityView,
    ConstitutionActionPermission,
    ConstitutionDecision,
    ConstitutionDecisionOutcome,
    ConstitutionEvaluationDisposition,
    ConstitutionManifest,
    ConstitutionMode,
    ConstitutionModePreview,
    ConstitutionView,
    ConstitutionViolationPresentation,
)


class _ConstitutionContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ConstitutionCapabilityViewResponse(_ConstitutionContract):
    view: ConstitutionView
    mode: ConstitutionMode
    rule_ids: tuple[str, ...]


class ConstitutionRuntimeResponse(_ConstitutionContract):
    revision: int
    digest_sha512: str
    rule_count: int
    # P8-REQ-016/P8-ACC-021: OFF/OBSERVE/ENFORCE must be distinguishable
    # from Evidence a real caller can inspect — every View is projected
    # with its actual resolved Mode, never omitted or collapsed to one
    # summary value.
    views: tuple[ConstitutionCapabilityViewResponse, ...]


def project_capability_views(
    manifest: ConstitutionManifest,
    views: tuple[CapabilityView, ...],
) -> ConstitutionRuntimeResponse:
    return ConstitutionRuntimeResponse(
        revision=manifest.revision,
        digest_sha512=manifest.digest_sha512,
        rule_count=len(manifest.rules),
        views=tuple(
            ConstitutionCapabilityViewResponse(
                view=view.view, mode=view.mode, rule_ids=view.rule_ids
            )
            for view in views
        ),
    )


class ConstitutionDecisionResponse(_ConstitutionContract):
    rule_id: str
    mode: ConstitutionMode
    outcome: ConstitutionDecisionOutcome
    reason: str


class ConstitutionModePreviewEntryResponse(_ConstitutionContract):
    mode: ConstitutionMode
    rule_ids: tuple[str, ...]
    decisions: tuple[ConstitutionDecisionResponse, ...]
    # P8-RW7-A (P8-CODEX-012): the Exact Handoff's required 3-axis
    # comparison, alongside the pre-existing per-Rule `decisions` — a
    # caller must never be limited to enumerating Decision Outcomes alone.
    evaluation_disposition: ConstitutionEvaluationDisposition
    action_permission: ConstitutionActionPermission
    violation_presentation: ConstitutionViolationPresentation


class ConstitutionViewModePreviewResponse(_ConstitutionContract):
    view: ConstitutionView
    modes: tuple[ConstitutionModePreviewEntryResponse, ...]


class ConstitutionModePreviewResponse(_ConstitutionContract):
    """P8-RW6-D (P8-CODEX-008): the whole Response is explicitly marked
    `is_preview=True` and carries `active_production_mode` alongside the
    comparison itself, so a caller/UI never has to infer — from data shape
    alone — that this is Pure Evaluation Output, not the Production Active
    Constitution Mode (`active_production_mode` is that real value, always
    `off` for this Bounded Task, completely unaffected by what this
    Response's `views` show for OBSERVE/ENFORCE)."""

    revision: int
    digest_sha512: str
    is_preview: bool = True
    active_production_mode: ConstitutionMode
    views: tuple[ConstitutionViewModePreviewResponse, ...]


def project_mode_previews(
    manifest: ConstitutionManifest,
    previews: tuple[ConstitutionModePreview, ...],
    *,
    active_production_mode: ConstitutionMode,
) -> ConstitutionModePreviewResponse:
    def _decision(decision: ConstitutionDecision) -> ConstitutionDecisionResponse:
        return ConstitutionDecisionResponse(
            rule_id=decision.rule_id,
            mode=decision.mode,
            outcome=decision.outcome,
            reason=decision.reason,
        )

    return ConstitutionModePreviewResponse(
        revision=manifest.revision,
        digest_sha512=manifest.digest_sha512,
        active_production_mode=active_production_mode,
        views=tuple(
            ConstitutionViewModePreviewResponse(
                view=preview.view,
                modes=tuple(
                    ConstitutionModePreviewEntryResponse(
                        mode=entry.mode,
                        rule_ids=entry.rule_ids,
                        decisions=tuple(_decision(d) for d in entry.decisions),
                        evaluation_disposition=entry.evaluation_disposition,
                        action_permission=entry.action_permission,
                        violation_presentation=entry.violation_presentation,
                    )
                    for entry in preview.modes
                ),
            )
            for preview in previews
        ),
    )
