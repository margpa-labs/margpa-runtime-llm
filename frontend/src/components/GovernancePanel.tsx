import { useState } from "react";
import { translate } from "../i18n/translations";
import type { GovernanceMode, GovernanceStatus, UiLanguage } from "../types";

export interface GovernanceControlState {
  capability: "loading" | "ready" | "failed" | "disabled";
  status: GovernanceStatus | null;
  resultText: string;
}

interface GovernancePanelProps {
  language: UiLanguage;
  visible: boolean;
  state: GovernanceControlState;
  onRefresh: () => void;
  onApply: (requestedMode: GovernanceMode) => void;
}

const MODE_LABEL_KEYS: Record<GovernanceMode, "governanceModeOff" | "governanceModeObserve" | "governanceModeEnforce"> = {
  off: "governanceModeOff",
  observe: "governanceModeObserve",
  enforce: "governanceModeEnforce",
};

export default function GovernancePanel({ language, visible, state, onRefresh, onApply }: GovernancePanelProps) {
  const status = state.status;
  // P4-CODEX-013: initialized from `status` — not a hardcoded "off" — so
  // a Mount that already has a Server Status available (e.g. reopening
  // the Settings Modal, which fully unmounts/remounts this component)
  // starts selected on the real Current Mode instead of always resetting
  // to "off". Lazy initializer avoids re-deriving this on every render.
  const [selectedMode, setSelectedMode] = useState<GovernanceMode>(
    () => status?.mode.current_mode ?? "off",
  );

  // Re-sync the selected Mode button whenever a *new* status arrives
  // (revision changes on every successful load/apply), mirroring the same
  // "adjust during render" pattern used by ConfigurationControlPanel's
  // syncedRevision — never in a useEffect, so it can't race the parent's
  // refresh fetch. See:
  // https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes
  const [syncedRevision, setSyncedRevision] = useState(status?.mode.revision);
  if (status?.mode.revision !== syncedRevision) {
    setSyncedRevision(status?.mode.revision);
    if (status !== null) {
      setSelectedMode(status.mode.current_mode);
    }
  }

  const statusKey =
    state.capability === "loading"
      ? "governanceLoading"
      : state.capability === "ready"
        ? "governanceReady"
        : "governanceFailed";

  if (!visible) {
    return null;
  }

  const observeSummary = status?.observe_summary ?? null;

  return (
    <section id="governance-panel" className="configuration-panel" aria-label={translate(language, "governanceTitle")}>
      <div className="configuration-panel-header">
        <div>
          <h2 id="governance-title">{translate(language, "governanceTitle")}</h2>
          <p id="governance-note">{translate(language, "governanceNote")}</p>
        </div>
        <button
          id="governance-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "governanceRefresh")}
        </button>
      </div>
      <p id="governance-status">{translate(language, statusKey)}</p>
      {status === null ? null : (
        <>
          <dl className="configuration-meta">
            <dt>{translate(language, "governanceRevision")}</dt>
            <dd>{status.mode.revision}</dd>
            <dt>{translate(language, "governanceDigest")}</dt>
            <dd>{status.mode.digest_sha512}</dd>
          </dl>
          <div className="configuration-controls">
            <div className="configuration-toggle" role="radiogroup" aria-label={translate(language, "governanceModeLabel")}>
              <span id="governance-mode-label">{translate(language, "governanceModeLabel")}</span>
              {status.mode.descriptors.map((descriptor) => {
                const unavailable = descriptor.availability === "unavailable";
                return (
                  <button
                    key={descriptor.mode}
                    id={`governance-mode-${descriptor.mode}`}
                    className="secondary"
                    type="button"
                    role="radio"
                    aria-checked={selectedMode === descriptor.mode}
                    disabled={unavailable}
                    title={
                      unavailable && descriptor.mode === "enforce"
                        ? translate(language, "governanceModeUnavailableEnforce")
                        : undefined
                    }
                    onClick={() => {
                      setSelectedMode(descriptor.mode);
                    }}
                  >
                    {translate(language, MODE_LABEL_KEYS[descriptor.mode])}
                  </button>
                );
              })}
            </div>
          </div>
          {observeSummary === null ? null : (
            <dl className="configuration-meta" id="governance-observe-summary">
              <dt>{translate(language, "governanceSummaryProviderState")}</dt>
              <dd>{observeSummary.provider_state}</dd>
              <dt>{translate(language, "governanceSummaryPackageFound")}</dt>
              <dd>
                {observeSummary.package_found
                  ? translate(language, "governanceSummaryPackageFoundYes")
                  : translate(language, "governanceSummaryPackageFoundNo")}
              </dd>
              <dt>{translate(language, "governanceSummaryDefinitionCount")}</dt>
              <dd>{observeSummary.definition_count}</dd>
              <dt>{translate(language, "governanceSummaryValidCount")}</dt>
              <dd>{observeSummary.valid_definition_count}</dd>
              <dt>{translate(language, "governanceSummaryInvalidCount")}</dt>
              <dd>{observeSummary.invalid_definition_count}</dd>
              <dt>{translate(language, "governanceSummaryUnsupportedCount")}</dt>
              <dd>{observeSummary.unsupported_definition_count}</dd>
              {observeSummary.compiled_plan_id === null ? null : (
                <>
                  <dt>{translate(language, "governanceSummaryPlanId")}</dt>
                  <dd>{observeSummary.compiled_plan_id}</dd>
                </>
              )}
            </dl>
          )}
          <div className="configuration-actions">
            <button
              id="governance-apply"
              className="primary"
              type="button"
              disabled={state.capability !== "ready"}
              onClick={() => {
                onApply(selectedMode);
              }}
            >
              {translate(language, "governanceApply")}
            </button>
          </div>
        </>
      )}
      <pre id="governance-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
