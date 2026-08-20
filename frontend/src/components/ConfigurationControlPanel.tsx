import { useState } from "react";
import { translate } from "../i18n/translations";
import type { ConfigurationSnapshot, UiLanguage } from "../types";

export interface ConfigurationControlState {
  capability: "loading" | "ready" | "failed" | "disabled";
  snapshot: ConfigurationSnapshot | null;
  resultText: string;
}

interface ConfigurationControlPanelProps {
  language: UiLanguage;
  visible: boolean;
  state: ConfigurationControlState;
  onRefresh: () => void;
  onPreview: (patch: { research_developer_mode?: string; selected_model?: string; context_size?: number }) => void;
  onApply: (researchDeveloperMode: string) => void;
}

// Display order deliberately doesn't mirror the snapshot's own field order:
// related keys (the two conversation_storage_* fields, the two
// application-sourced max_new_tokens/selected_model fields) are grouped
// together, and research_developer_mode / acceleration_api lead their
// respective columns. This is why the columns are rendered explicitly by
// key instead of via a single `snapshot.fields.map(...)` pass.
const LEFT_COLUMN_FIELD_KEYS = [
  "research_developer_mode",
  "context_size",
  "max_new_tokens",
  "selected_model",
  "profile_key",
];

const RIGHT_COLUMN_FIELD_KEYS = [
  "acceleration_api",
  "backend_kind",
  "device_kind",
  "conversation_storage_kind",
  "conversation_storage_version",
];

export default function ConfigurationControlPanel({
  language,
  visible,
  state,
  onRefresh,
  onPreview,
  onApply,
}: ConfigurationControlPanelProps) {
  const snapshot = state.snapshot;
  const researchField = snapshot?.fields.find((item) => item.key === "research_developer_mode") ?? null;
  const modelField = snapshot?.fields.find((item) => item.key === "selected_model") ?? null;
  const contextField = snapshot?.fields.find((item) => item.key === "context_size") ?? null;

  const [researchPressed, setResearchPressed] = useState(false);
  const [modelValue, setModelValue] = useState("");
  const [contextValue, setContextValue] = useState("");

  // Re-sync the local editable inputs whenever a *new* snapshot arrives
  // (revision changes on every successful load/apply), mirroring the
  // original synchronizeConfigurationInputs() call inside
  // loadConfigurationControl(). Adjusted during render (React's documented
  // pattern for "reset state when a prop changes") rather than in a
  // useEffect, so it never races the parent's refresh fetch and never
  // triggers an extra commit. See:
  // https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes
  const [syncedRevision, setSyncedRevision] = useState(snapshot?.revision);
  if (snapshot?.revision !== syncedRevision) {
    setSyncedRevision(snapshot?.revision);
    setResearchPressed(researchField?.value === "on");
    setModelValue(modelField === null ? "" : String(modelField.value));
    setContextValue(contextField === null ? "" : String(contextField.value));
  }

  const developerDetailsVisible = researchField?.value === "on";
  const statusKey =
    state.capability === "loading"
      ? "configurationLoading"
      : state.capability === "ready"
        ? "configurationReady"
        : "configurationFailed";

  const handlePreview = (): void => {
    const patch: { research_developer_mode?: string; selected_model?: string; context_size?: number } =
      {};
    const researchValue = researchPressed ? "on" : "off";
    const trimmedModel = modelValue.trim();
    const numericContext = Number(contextValue);
    if (researchField !== null && researchField.value !== researchValue) {
      patch.research_developer_mode = researchValue;
    }
    if (modelField !== null && trimmedModel && modelField.value !== trimmedModel) {
      patch.selected_model = trimmedModel;
    }
    if (
      contextField !== null &&
      Number.isInteger(numericContext) &&
      contextField.value !== numericContext
    ) {
      patch.context_size = numericContext;
    }
    onPreview(Object.keys(patch).length === 0 ? { research_developer_mode: researchValue } : patch);
  };

  if (!visible) {
    return null;
  }

  return (
    <section id="configuration-panel" className="configuration-panel" aria-label={translate(language, "configurationTitle")}>
      <div className="configuration-panel-header">
        <div>
          <h2 id="configuration-title">{translate(language, "configurationTitle")}</h2>
          <p id="configuration-note">{translate(language, "configurationNote")}</p>
        </div>
        <button
          id="configuration-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "configurationRefresh")}
        </button>
      </div>
      <p id="configuration-status">{translate(language, statusKey)}</p>
      {snapshot === null ? null : (
        <>
          <dl className="configuration-meta" hidden={!developerDetailsVisible}>
            <dt>{translate(language, "configurationRevision")}</dt>
            <dd>{snapshot.revision}</dd>
            <dt>{translate(language, "configurationDigest")}</dt>
            <dd>{snapshot.digest_sha512}</dd>
          </dl>
          <div className="configuration-fields" role="list" hidden={!developerDetailsVisible}>
            {[LEFT_COLUMN_FIELD_KEYS, RIGHT_COLUMN_FIELD_KEYS].map((columnKeys, columnIndex) => (
              <div className="configuration-fields-column" key={columnIndex}>
                {columnKeys.map((key) => {
                  const item = snapshot.fields.find((field) => field.key === key);
                  if (item === undefined) {
                    return null;
                  }
                  return (
                    <div className="configuration-field" role="listitem" key={item.key}>
                      <strong>{item.key}</strong>
                      <span>{String(item.value)}</span>
                      <small>
                        {item.source} · {item.apply_disposition}
                      </small>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          <div className="configuration-controls">
            <div className="configuration-toggle">
              <span id="configuration-research-mode-label">
                {translate(language, "configurationResearchMode")}
              </span>
              <button
                id="configuration-research-mode"
                className="secondary"
                type="button"
                aria-pressed={researchPressed}
                onClick={() => {
                  setResearchPressed((previous) => !previous);
                }}
              >
                {researchPressed ? "ON" : "OFF"}
              </button>
            </div>
            <label hidden={!developerDetailsVisible}>
              <span id="configuration-model-label">{translate(language, "configurationModel")}</span>
              <input
                id="configuration-model"
                type="text"
                maxLength={128}
                value={modelValue}
                onChange={(event) => {
                  setModelValue(event.target.value);
                }}
              />
            </label>
            <label hidden={!developerDetailsVisible}>
              <span id="configuration-context-label">{translate(language, "configurationContext")}</span>
              <input
                id="configuration-context"
                type="number"
                value={contextValue}
                onChange={(event) => {
                  setContextValue(event.target.value);
                }}
              />
            </label>
          </div>
          <div className="configuration-actions">
            <button
              id="configuration-preview"
              className="secondary"
              type="button"
              hidden={!developerDetailsVisible}
              disabled={state.capability !== "ready"}
              onClick={handlePreview}
            >
              {translate(language, "configurationPreview")}
            </button>
            <button
              id="configuration-apply"
              className="primary"
              type="button"
              disabled={state.capability !== "ready"}
              onClick={() => {
                onApply(researchPressed ? "on" : "off");
              }}
            >
              {translate(language, "configurationApply")}
            </button>
          </div>
        </>
      )}
      <pre id="configuration-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
