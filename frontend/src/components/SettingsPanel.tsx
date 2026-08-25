import { translate } from "../i18n/translations";
import type { UiLanguage } from "../types";

export interface SettingsFormState {
  responseLanguage: string;
  maxNewTokens: string;
  thinkingMode: boolean;
  thinkingVisibility: boolean;
  summaryMode: string;
  documentationRagMode: string;
  injectContextUsage: boolean;
  showContextUsage: boolean;
  expressiveMode: boolean;
}

interface SettingsPanelProps {
  language: UiLanguage;
  form: SettingsFormState;
  onChange: (next: SettingsFormState) => void;
  thinkingControlAvailable: boolean;
  active: boolean;
  documentationRagControlAvailable: boolean;
  documentationRagDenied: boolean;
  documentationRagNoteText: string;
}

export default function SettingsPanel({
  language,
  form,
  onChange,
  thinkingControlAvailable,
  active,
  documentationRagControlAvailable,
  documentationRagDenied,
  documentationRagNoteText,
}: SettingsPanelProps) {
  const thinkingModeDisabled = !(thinkingControlAvailable && !active);
  const thinkingEnabled = thinkingControlAvailable && form.thinkingMode;
  const thinkingVisibilityDisabled = active || !thinkingEnabled;
  const documentationDisabled = active || !documentationRagControlAvailable;

  return (
    <section id="settings" className="settings" aria-label={translate(language, "settingsLabel")}>
      <h2 id="settings-title">{translate(language, "settingsTitle")}</h2>
      <div className="settings-columns">
        <div className="settings-column settings-column-left">
          <div className="settings-inline-pair">
            <label>
              <span id="response-language-label">{translate(language, "responseLanguageLabel")}</span>
              <select
                id="response-language"
                value={form.responseLanguage}
                onChange={(event) => {
                  onChange({ ...form, responseLanguage: event.target.value });
                }}
              >
                <option id="response-language-ja" value="ja">
                  {translate(language, "responseJa")}
                </option>
                <option id="response-language-en" value="en">
                  {translate(language, "responseEn")}
                </option>
                <option id="response-language-auto" value="auto">
                  {translate(language, "responseAuto")}
                </option>
              </select>
            </label>
          </div>
          <div className="settings-inline-pair">
            <label className="switch-row">
              <input
                id="thinking-mode"
                type="checkbox"
                checked={form.thinkingMode}
                disabled={thinkingModeDisabled}
                title={thinkingControlAvailable ? "" : translate(language, "thinkingUnavailable")}
                onChange={(event) => {
                  onChange({ ...form, thinkingMode: event.target.checked });
                }}
              />
              <span id="thinking-mode-label">{translate(language, "thinkingModeLabel")}</span>
            </label>
            <label className="switch-row">
              <input
                id="thinking-visibility"
                type="checkbox"
                checked={form.thinkingVisibility}
                disabled={thinkingVisibilityDisabled}
                onChange={(event) => {
                  onChange({ ...form, thinkingVisibility: event.target.checked });
                }}
              />
              <span id="thinking-visibility-label">{translate(language, "thinkingVisibilityLabel")}</span>
            </label>
          </div>
          <p id="thinking-note" className="setting-note">
            {translate(language, "thinkingNote")}
          </p>
          <label className="switch-row">
            <input
              id="inject-context-usage"
              type="checkbox"
              checked={form.injectContextUsage}
              onChange={(event) => {
                onChange({ ...form, injectContextUsage: event.target.checked });
              }}
            />
            <span id="inject-context-usage-label">{translate(language, "injectContextUsageLabel")}</span>
          </label>
          <p id="inject-context-usage-note" className="setting-note">
            {translate(language, "injectContextUsageNote")}
          </p>
          <label className="switch-row">
            <input
              id="show-context-usage"
              type="checkbox"
              checked={form.showContextUsage}
              onChange={(event) => {
                onChange({ ...form, showContextUsage: event.target.checked });
              }}
            />
            <span id="show-context-usage-label">{translate(language, "showContextUsageLabel")}</span>
          </label>
          <p id="show-context-usage-note" className="setting-note">
            {translate(language, "showContextUsageNote")}
          </p>
          <label className="switch-row">
            <input
              id="expressive-mode"
              type="checkbox"
              checked={form.expressiveMode}
              onChange={(event) => {
                onChange({ ...form, expressiveMode: event.target.checked });
              }}
            />
            <span id="expressive-mode-label">{translate(language, "expressiveModeLabel")}</span>
          </label>
          <p id="expressive-mode-note" className="setting-note">
            {translate(language, "expressiveModeNote")}
          </p>
        </div>
        <div className="settings-column settings-column-right">
          <fieldset className="summary-control">
            <legend id="summary-mode-label">{translate(language, "summaryModeLabel")}</legend>
            <div className="segmented-control">
              <label>
                <input
                  type="radio"
                  name="summary-mode"
                  value="off"
                  checked={form.summaryMode === "off"}
                  onChange={() => {
                    onChange({ ...form, summaryMode: "off" });
                  }}
                />
                <span id="summary-mode-off">{translate(language, "summaryOff")}</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="summary-mode"
                  value="on"
                  checked={form.summaryMode === "on"}
                  onChange={() => {
                    onChange({ ...form, summaryMode: "on" });
                  }}
                />
                <span id="summary-mode-on">{translate(language, "summaryOn")}</span>
              </label>
            </div>
          </fieldset>
          <p id="summary-note" className="setting-note">
            {translate(language, "summaryNote")}
          </p>
          <fieldset
            id="documentation-rag-control"
            className="summary-control"
            hidden={documentationRagDenied}
            title={documentationRagControlAvailable ? "" : translate(language, "documentationRagUnavailable")}
          >
            <legend id="documentation-rag-mode-label">{translate(language, "documentationRagModeLabel")}</legend>
            <div className="segmented-control">
              <label>
                <input
                  type="radio"
                  name="documentation-rag-mode"
                  value="disabled"
                  checked={form.documentationRagMode === "disabled"}
                  disabled={documentationDisabled}
                  onChange={() => {
                    onChange({ ...form, documentationRagMode: "disabled" });
                  }}
                />
                <span id="documentation-rag-mode-off">{translate(language, "documentationRagOff")}</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="documentation-rag-mode"
                  value="enabled"
                  checked={form.documentationRagMode === "enabled"}
                  disabled={documentationDisabled}
                  onChange={() => {
                    onChange({ ...form, documentationRagMode: "enabled" });
                  }}
                />
                <span id="documentation-rag-mode-on">{translate(language, "documentationRagOn")}</span>
              </label>
            </div>
          </fieldset>
          <p id="documentation-rag-note" className="setting-note" hidden={documentationRagDenied}>
            {documentationRagNoteText}
          </p>
        </div>
      </div>
    </section>
  );
}
