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
                    aria-checked={status.mode.current_mode === descriptor.mode}
                    disabled={unavailable || state.capability !== "ready"}
                    title={
                      unavailable && descriptor.mode === "enforce"
                        ? translate(language, "governanceModeUnavailableEnforce")
                        : undefined
                    }
                    onClick={() => {
                      if (status.mode.current_mode !== descriptor.mode) {
                        onApply(descriptor.mode);
                      }
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
        </>
      )}
      <pre id="governance-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
