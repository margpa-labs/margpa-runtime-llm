import { translate } from "../i18n/translations";
import type { MainGovernanceMode, RuntimeGovernanceStatus, UiLanguage } from "../types";

export interface RuntimeGovernanceControlState {
  capability: "loading" | "ready" | "failed" | "disabled";
  status: RuntimeGovernanceStatus | null;
  resultText: string;
}

interface RuntimeGovernancePanelProps {
  language: UiLanguage;
  visible: boolean;
  state: RuntimeGovernanceControlState;
  onRefresh: () => void;
  onApply: (requestedMode: MainGovernanceMode) => void;
}

const MODE_LABEL_KEYS: Record<
  MainGovernanceMode,
  "runtimeGovernanceModeOff" | "runtimeGovernanceModeObserve" | "runtimeGovernanceModeEnforce"
> = {
  off: "runtimeGovernanceModeOff",
  observe: "runtimeGovernanceModeObserve",
  enforce: "runtimeGovernanceModeEnforce",
};

export default function RuntimeGovernancePanel({
  language,
  visible,
  state,
  onRefresh,
  onApply,
}: RuntimeGovernancePanelProps) {
  const status = state.status;

  const statusKey =
    state.capability === "loading"
      ? "runtimeGovernanceLoading"
      : state.capability === "ready"
        ? "runtimeGovernanceReady"
        : "runtimeGovernanceFailed";

  if (!visible) {
    return null;
  }

  return (
    <section
      id="runtime-governance-panel"
      className="configuration-panel"
      aria-label={translate(language, "runtimeGovernanceTitle")}
    >
      <div className="configuration-panel-header">
        <div>
          <h2 id="runtime-governance-title">{translate(language, "runtimeGovernanceTitle")}</h2>
          <p id="runtime-governance-note">{translate(language, "runtimeGovernanceNote")}</p>
          <p id="runtime-governance-semantic-boundary-notice">
            {translate(language, "runtimeGovernanceSemanticBoundaryNotice")}
          </p>
        </div>
        <button
          id="runtime-governance-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "runtimeGovernanceRefresh")}
        </button>
      </div>
      <p id="runtime-governance-status">{translate(language, statusKey)}</p>
      {status === null || !status.enabled ? null : (
        <>
          <dl className="configuration-meta">
            <dt>{translate(language, "runtimeGovernanceRevision")}</dt>
            <dd>{status.revision}</dd>
          </dl>
          <div className="configuration-controls">
            <div
              className="configuration-toggle"
              role="radiogroup"
              aria-label={translate(language, "runtimeGovernanceModeLabel")}
            >
              <span id="runtime-governance-mode-label">
                {translate(language, "runtimeGovernanceModeLabel")}
              </span>
              {status.descriptors.map((descriptor) => {
                const unavailable = descriptor.availability === "unavailable";
                return (
                  <button
                    key={descriptor.mode}
                    id={`runtime-governance-mode-${descriptor.mode}`}
                    className="secondary"
                    type="button"
                    role="radio"
                    aria-checked={status.current_mode === descriptor.mode}
                    disabled={unavailable || state.capability !== "ready"}
                    title={
                      unavailable && descriptor.unavailable_reason_code !== null
                        ? descriptor.unavailable_reason_code
                        : undefined
                    }
                    onClick={() => {
                      if (status.current_mode !== descriptor.mode) {
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
          {status.points.length === 0 ? null : (
            <dl className="configuration-meta" id="runtime-governance-points">
              {status.points.map((point) => (
                <div key={point.point_id}>
                  <dt>{point.point_id}</dt>
                  <dd>
                    {translate(language, "runtimeGovernancePointExecutionState")}
                    {": "}
                    {point.execution_state ?? "—"}
                    {" · "}
                    {translate(language, "runtimeGovernancePointSelectedCount")}
                    {": "}
                    {point.selected_descriptor_count ?? "—"}
                    {" · "}
                    {translate(language, "runtimeGovernancePointSeverity")}
                    {": "}
                    {point.severity ?? "—"}
                    {" · "}
                    {translate(language, "runtimeGovernancePointExecutedCount")}
                    {": "}
                    {point.executed_action_count ?? "—"}
                    {" · "}
                    {translate(language, "runtimeGovernancePointObservationCount")}
                    {": "}
                    {point.observation_count ?? "—"}
                    {" ("}
                    {translate(language, "runtimeGovernancePointPassCount")}
                    {" "}
                    {point.pass_count ?? "—"}
                    {", "}
                    {translate(language, "runtimeGovernancePointDeviationCount")}
                    {" "}
                    {point.deviation_count ?? "—"}
                    {", "}
                    {translate(language, "runtimeGovernancePointDeferredCount")}
                    {" "}
                    {point.deferred_count ?? "—"}
                    {")"}
                    {point.unavailable_reason_code === null
                      ? null
                      : ` · ${translate(language, "runtimeGovernancePointUnavailableReason")}: ${point.unavailable_reason_code}`}
                    {point.degraded_reason_code === null
                      ? null
                      : ` · ${translate(language, "runtimeGovernancePointDegradedReason")}: ${point.degraded_reason_code}`}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          {status.evidence === null ? null : (
            <dl className="configuration-meta" id="runtime-governance-evidence">
              <dt>{translate(language, "runtimeGovernanceEvidenceDegraded")}</dt>
              <dd>
                {status.evidence.degraded
                  ? translate(language, "runtimeGovernanceEvidenceDegradedYes")
                  : translate(language, "runtimeGovernanceEvidenceDegradedNo")}
              </dd>
              {status.evidence.degraded_reason_code === null ? null : (
                <>
                  <dt>{translate(language, "runtimeGovernanceEvidenceReason")}</dt>
                  <dd>{status.evidence.degraded_reason_code}</dd>
                </>
              )}
            </dl>
          )}
        </>
      )}
      <pre id="runtime-governance-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
