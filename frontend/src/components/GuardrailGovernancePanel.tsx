import { useState } from "react";
import { translate } from "../i18n/translations";
import type { GuardrailGovernanceMode, GuardrailGovernanceStatus, UiLanguage } from "../types";

export interface GuardrailGovernanceControlState {
  capability: "loading" | "ready" | "failed" | "disabled";
  status: GuardrailGovernanceStatus | null;
  resultText: string;
}

interface GuardrailGovernancePanelProps {
  language: UiLanguage;
  visible: boolean;
  state: GuardrailGovernanceControlState;
  onRefresh: () => void;
  onApply: (requestedMode: GuardrailGovernanceMode) => void;
}

const MODE_LABEL_KEYS: Record<
  GuardrailGovernanceMode,
  "guardrailGovernanceModeOff" | "guardrailGovernanceModeObserve" | "guardrailGovernanceModeEnforce"
> = {
  off: "guardrailGovernanceModeOff",
  observe: "guardrailGovernanceModeObserve",
  enforce: "guardrailGovernanceModeEnforce",
};

export default function GuardrailGovernancePanel({
  language,
  visible,
  state,
  onRefresh,
  onApply,
}: GuardrailGovernancePanelProps) {
  const status = state.status;
  // Same lazy-initializer / re-sync pattern as RuntimeGovernancePanel
  // (P4-CODEX-013 lineage): a Mount that already has a Server Status
  // available (e.g. reopening the Settings Modal, which fully
  // unmounts/remounts this component) starts selected on the real
  // Current Mode instead of always resetting to "off".
  const [selectedMode, setSelectedMode] = useState<GuardrailGovernanceMode>(
    () => status?.current_mode ?? "off",
  );

  const [syncedRevision, setSyncedRevision] = useState(status?.revision);
  if (status?.revision !== syncedRevision) {
    setSyncedRevision(status?.revision);
    if (status !== null && status.current_mode !== null) {
      setSelectedMode(status.current_mode);
    }
  }

  const statusKey =
    state.capability === "loading"
      ? "guardrailGovernanceLoading"
      : state.capability === "ready"
        ? "guardrailGovernanceReady"
        : "guardrailGovernanceFailed";

  if (!visible) {
    return null;
  }

  return (
    <section
      id="guardrail-governance-panel"
      className="configuration-panel"
      aria-label={translate(language, "guardrailGovernanceTitle")}
    >
      <div className="configuration-panel-header">
        <div>
          <h2 id="guardrail-governance-title">{translate(language, "guardrailGovernanceTitle")}</h2>
          <p id="guardrail-governance-note">{translate(language, "guardrailGovernanceNote")}</p>
          <p id="guardrail-governance-safety-model-notice">
            {translate(language, "guardrailGovernanceSafetyModelNotice")}
          </p>
        </div>
        <button
          id="guardrail-governance-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "guardrailGovernanceRefresh")}
        </button>
      </div>
      <p id="guardrail-governance-status">{translate(language, statusKey)}</p>
      {status === null || !status.enabled ? null : (
        <>
          <dl className="configuration-meta">
            <dt>{translate(language, "guardrailGovernanceRevision")}</dt>
            <dd>{status.revision}</dd>
          </dl>
          <div className="configuration-controls">
            <div
              className="configuration-toggle"
              role="radiogroup"
              aria-label={translate(language, "guardrailGovernanceModeLabel")}
            >
              <span id="guardrail-governance-mode-label">
                {translate(language, "guardrailGovernanceModeLabel")}
              </span>
              {status.descriptors.map((descriptor) => {
                const unavailable = descriptor.availability === "unavailable";
                return (
                  <button
                    key={descriptor.mode}
                    id={`guardrail-governance-mode-${descriptor.mode}`}
                    className="secondary"
                    type="button"
                    role="radio"
                    aria-checked={selectedMode === descriptor.mode}
                    disabled={unavailable}
                    title={
                      unavailable && descriptor.unavailable_reason_code !== null
                        ? descriptor.unavailable_reason_code
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
          {status.points.length === 0 ? null : (
            <dl className="configuration-meta" id="guardrail-governance-points">
              {status.points.map((point) => (
                <div key={point.point_id}>
                  <dt>{point.point_id}</dt>
                  <dd>
                    {translate(language, "guardrailGovernancePointExecutionState")}
                    {": "}
                    {point.execution_state ?? "—"}
                    {" · "}
                    {translate(language, "guardrailGovernancePointSeverity")}
                    {": "}
                    {point.severity ?? "—"}
                    {" · "}
                    {translate(language, "guardrailGovernancePointDetectionCount")}
                    {": "}
                    {point.detection_count ?? "—"}
                    {" · "}
                    {translate(language, "guardrailGovernancePointMatchCount")}
                    {": "}
                    {point.match_count ?? "—"}
                    {" · "}
                    {translate(language, "guardrailGovernancePointExecutedCount")}
                    {": "}
                    {point.executed_action_count ?? "—"}
                    {point.unavailable_reason_code === null
                      ? null
                      : ` · ${translate(language, "guardrailGovernancePointUnavailableReason")}: ${point.unavailable_reason_code}`}
                    {point.degraded_reason_code === null
                      ? null
                      : ` · ${translate(language, "guardrailGovernancePointDegradedReason")}: ${point.degraded_reason_code}`}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          <div className="configuration-actions">
            <button
              id="guardrail-governance-apply"
              className="primary"
              type="button"
              disabled={state.capability !== "ready"}
              onClick={() => {
                onApply(selectedMode);
              }}
            >
              {translate(language, "guardrailGovernanceApply")}
            </button>
          </div>
        </>
      )}
      <pre id="guardrail-governance-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
