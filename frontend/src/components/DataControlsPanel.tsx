import { translate, type TranslationKey } from "../i18n/translations";
import type { UiLanguage } from "../types";

export interface DataControlConsentState {
  external_query_transmission_consent: boolean;
  feedback_research_use: boolean;
  synthetic_data_use: boolean;
  future_training_export: boolean;
}

export interface DataControlsRetentionFact {
  source_class: string;
  retained: boolean;
  description: string;
}

export interface DataControlsState {
  capability: "loading" | "ready" | "failed" | "disabled";
  consent: DataControlConsentState | null;
  retentionFacts: DataControlsRetentionFact[];
  resultText: string;
}

interface DataControlsPanelProps {
  language: UiLanguage;
  visible: boolean;
  state: DataControlsState;
  onRefresh: () => void;
  onToggle: (key: keyof DataControlConsentState, value: boolean) => void;
  onReset: () => void;
}

const CONSENT_FIELDS: { key: keyof DataControlConsentState; labelKey: TranslationKey }[] = [
  {
    key: "external_query_transmission_consent",
    labelKey: "dataControlsExternalQueryTransmission",
  },
  { key: "feedback_research_use", labelKey: "dataControlsFeedbackResearchUse" },
  { key: "synthetic_data_use", labelKey: "dataControlsSyntheticDataUse" },
  { key: "future_training_export", labelKey: "dataControlsFutureTrainingExport" },
];

export default function DataControlsPanel({
  language,
  visible,
  state,
  onRefresh,
  onToggle,
  onReset,
}: DataControlsPanelProps) {
  if (!visible) {
    return null;
  }

  const statusKey =
    state.capability === "loading"
      ? "dataControlsLoading"
      : state.capability === "ready"
        ? "dataControlsReady"
        : "dataControlsFailed";

  return (
    <section id="data-controls-panel" className="data-controls-panel" aria-label={translate(language, "dataControlsTitle")}>
      <div className="data-controls-panel-header">
        <div>
          <h2 id="data-controls-title">{translate(language, "dataControlsTitle")}</h2>
          <p id="data-controls-note">{translate(language, "dataControlsNote")}</p>
        </div>
        <button
          id="data-controls-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "dataControlsRefresh")}
        </button>
      </div>
      <p id="data-controls-status">{translate(language, statusKey)}</p>
      {state.retentionFacts.length > 0 ? (
        <div id="data-controls-retention-facts">
          <h3>{translate(language, "dataControlsRetentionTitle")}</h3>
          <ul role="list">
            {state.retentionFacts.map((fact) => (
              <li role="listitem" key={fact.source_class}>
                <strong>{fact.source_class}</strong>: {fact.description}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {state.consent !== null ? (
        <div id="data-controls-consent">
          <h3>{translate(language, "dataControlsConsentTitle")}</h3>
          <p id="data-controls-consent-note">{translate(language, "dataControlsConsentNote")}</p>
          {CONSENT_FIELDS.map(({ key, labelKey }) => (
            <label className="switch-row" key={key}>
              <input
                id={`data-controls-${key}`}
                type="checkbox"
                checked={state.consent?.[key] ?? false}
                onChange={(event) => {
                  onToggle(key, event.target.checked);
                }}
              />
              <span>{translate(language, labelKey)}</span>
            </label>
          ))}
          <button id="data-controls-reset" className="secondary" type="button" onClick={onReset}>
            {translate(language, "dataControlsReset")}
          </button>
        </div>
      ) : null}
    </section>
  );
}
