import { useEffect, useState } from "react";
import { fetchConstitutionModePreview, fetchConstitutionRuntime } from "../api/client";
import { translate, type TranslationKey } from "../i18n/translations";
import type {
  ConstitutionActionPermission,
  ConstitutionEvaluationDisposition,
  ConstitutionModePreview,
  ConstitutionRuntime,
  ConstitutionViolationPresentation,
  UiLanguage,
} from "../types";

// P8-RW7-B (P8-CODEX-012): Label Keys for the Exact Handoff's 3-axis
// comparison — every possible axis value maps to its own explicit,
// human-readable Label, in both ja/en, never left as a bare Enum string.
const EVALUATION_DISPOSITION_LABEL_KEYS: Record<
  ConstitutionEvaluationDisposition,
  TranslationKey
> = {
  not_evaluated: "constitutionEvaluationDispositionNotEvaluated",
  evaluate_record_only: "constitutionEvaluationDispositionEvaluateRecordOnly",
  evaluate_and_apply_supported_action:
    "constitutionEvaluationDispositionEvaluateAndApplySupportedAction",
};

const ACTION_PERMISSION_LABEL_KEYS: Record<ConstitutionActionPermission, TranslationKey> = {
  no_constitution_action: "constitutionActionPermissionNoConstitutionAction",
  no_block_no_authority_change: "constitutionActionPermissionNoBlockNoAuthorityChange",
  supported_actions_only_no_authority_expansion:
    "constitutionActionPermissionSupportedActionsOnlyNoAuthorityExpansion",
};

const VIOLATION_PRESENTATION_LABEL_KEYS: Record<
  ConstitutionViolationPresentation,
  TranslationKey
> = {
  not_evaluated: "constitutionViolationPresentationNotEvaluated",
  observation_only: "constitutionViolationPresentationObservationOnly",
  enforced: "constitutionViolationPresentationEnforced",
  typed_unsupported: "constitutionViolationPresentationTypedUnsupported",
};

// Self-contained fetch, same rationale as `FeatureModesPanel` — a purely
// Read-only Research Preview with nothing else on the page depending on
// its result. No polling interval (unlike Feature Modes): the Constitution
// Manifest is a static local File, not a live-mutable Runtime Mode.
interface ConstitutionPanelProps {
  language: UiLanguage;
  visible: boolean;
}

type LoadCapability = "loading" | "ready" | "failed";

function shortenDigest(value: string): string {
  return value.length <= 16 ? value : `${value.slice(0, 16)}…`;
}

export default function ConstitutionPanel({ language, visible }: ConstitutionPanelProps) {
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [runtime, setRuntime] = useState<ConstitutionRuntime | null>(null);
  const [preview, setPreview] = useState<ConstitutionModePreview | null>(null);

  useEffect(() => {
    if (!visible) return;
    fetchConstitutionRuntime()
      .then((next) => {
        setRuntime(next);
        setCapability("ready");
      })
      .catch(() => {
        setRuntime(null);
        setCapability("failed");
      });
    // P8-RW6-D (P8-CODEX-008): fetched independently of `runtime` above —
    // a failed Preview fetch must never hide the (already-working) Runtime
    // Capability View section, and vice versa.
    fetchConstitutionModePreview()
      .then(setPreview)
      .catch(() => {
        setPreview(null);
      });
  }, [visible]);

  if (!visible) {
    return null;
  }

  // P8-REQ-013: a Research Preview, silently absent (never a scary error)
  // when this Task's Provisional `constitution/` was never composed —
  // mirrors how every other optional Panel here degrades.
  if (capability === "failed") {
    return null;
  }

  return (
    <section
      id="constitution-panel"
      className="constitution-panel"
      aria-label={translate(language, "constitutionTitle")}
    >
      <h3 id="constitution-title">{translate(language, "constitutionTitle")}</h3>
      <p id="constitution-note">{translate(language, "constitutionNote")}</p>
      {capability === "loading" || runtime === null ? (
        <p id="constitution-status">{translate(language, "constitutionLoading")}</p>
      ) : (
        <>
          <p id="constitution-manifest-summary">
            {translate(language, "constitutionRevisionLabel")} {runtime.revision} ·{" "}
            {translate(language, "constitutionDigestLabel")}{" "}
            <code title={runtime.digest_sha512}>{shortenDigest(runtime.digest_sha512)}</code> ·{" "}
            {runtime.rule_count} {translate(language, "constitutionRuleCountLabel")}
          </p>
          <ul id="constitution-views" role="list">
            {runtime.views.map((view) => (
              <li role="listitem" key={view.view} className="constitution-view-row">
                <span className="constitution-view-name">{view.view}</span>
                {/* P8-REQ-016/P8-ACC-021: OFF/OBSERVE/ENFORCE rendered as its
                    own explicit, distinguishable value — never collapsed to
                    a generic "active"/"inactive" label. */}
                <span className={`constitution-view-mode constitution-view-mode-${view.mode}`}>
                  {translate(
                    language,
                    view.mode === "off"
                      ? "constitutionModeOff"
                      : view.mode === "observe"
                        ? "constitutionModeObserve"
                        : "constitutionModeEnforce",
                  )}
                </span>
                <span className="constitution-view-rule-count">{view.rule_ids.length}</span>
              </li>
            ))}
          </ul>
          {preview !== null ? (
            <div id="constitution-preview" className="constitution-preview">
              <h4 id="constitution-preview-title">
                {translate(language, "constitutionPreviewTitle")}
              </h4>
              {/* P8-CODEX-008: explicit, unmissable non-Activation disclaimer
                  — this Section must never be mistaken for the Production
                  Active Mode rendered above. */}
              <p id="constitution-preview-disclaimer" className="constitution-preview-disclaimer">
                {translate(language, "constitutionPreviewDisclaimer")}
              </p>
              <p id="constitution-preview-active-mode">
                {translate(language, "constitutionPreviewActiveModeLabel")}{" "}
                <strong>{preview.active_production_mode}</strong>
              </p>
              {preview.views.map((view) => (
                <div
                  key={view.view}
                  id={`constitution-preview-view-${view.view}`}
                  className="constitution-preview-view"
                >
                  <span className="constitution-preview-view-name">{view.view}</span>
                  <ul role="list" className="constitution-preview-modes">
                    {view.modes.map((modeEntry) => (
                      <li
                        role="listitem"
                        key={modeEntry.mode}
                        className={`constitution-preview-mode-row constitution-preview-mode-${modeEntry.mode}`}
                      >
                        {/* P8-MR4 (P8-MANUAL-004): the Mode Name is its own
                            Header line — Decision and the other 3 axes are
                            never packed onto the same line as the Mode
                            Name, each getting its own row below it. Backend
                            Contract/Semantics/Production OFF are unchanged
                            by this Frontend-only layout fix. */}
                        <h5 className="constitution-preview-mode-name">{modeEntry.mode}</h5>
                        <div className="constitution-preview-mode-details">
                          <div className="constitution-preview-mode-decisions">
                            {translate(language, "constitutionPreviewDecisionLabel")}{" "}
                            {modeEntry.decisions.length === 0
                              ? "—"
                              : modeEntry.decisions.map((d) => d.outcome).join(", ")}
                          </div>
                          {/* P8-RW7-B (P8-CODEX-012): the Exact Handoff's
                              3-axis comparison — never limited to
                              enumerating Decision Outcomes alone. */}
                          <div className="constitution-preview-mode-evaluation-disposition">
                            {translate(language, "constitutionPreviewEvaluationDispositionLabel")}{" "}
                            {translate(
                              language,
                              EVALUATION_DISPOSITION_LABEL_KEYS[modeEntry.evaluation_disposition],
                            )}
                          </div>
                          <div className="constitution-preview-mode-action-permission">
                            {translate(language, "constitutionPreviewActionPermissionLabel")}{" "}
                            {translate(
                              language,
                              ACTION_PERMISSION_LABEL_KEYS[modeEntry.action_permission],
                            )}
                          </div>
                          <div className="constitution-preview-mode-violation-presentation">
                            {translate(language, "constitutionPreviewViolationPresentationLabel")}{" "}
                            {translate(
                              language,
                              VIOLATION_PRESENTATION_LABEL_KEYS[modeEntry.violation_presentation],
                            )}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : null}
        </>
      )}
    </section>
  );
}
