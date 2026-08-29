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
  onApply: (researchDeveloperMode: string) => void;
}

// Display order deliberately doesn't mirror the snapshot's own field order.
// P6-RR-P-WU-004 (Production Wiring Delta item 5): the User-specified 3:3
// split — left groups the two conversation_storage_* fields with
// profile_key, right groups the three runtime/hardware identity fields.
// `research_developer_mode` is intentionally excluded from both columns
// (item 4): its own OFF/ON Control is hidden (item 3), not deleted, and
// its Backend Contract (`onApply`) is untouched.
const LEFT_COLUMN_FIELD_KEYS = [
  "conversation_storage_kind",
  "conversation_storage_version",
  "profile_key",
];

const RIGHT_COLUMN_FIELD_KEYS = ["acceleration_api", "backend_kind", "device_kind"];

export default function ConfigurationControlPanel({
  language,
  visible,
  state,
  onRefresh,
  onApply,
}: ConfigurationControlPanelProps) {
  const snapshot = state.snapshot;
  const researchField = snapshot?.fields.find((item) => item.key === "research_developer_mode") ?? null;

  // P6-RR-P-WU-004 (Production Wiring Delta item 3): details render
  // unconditionally now — the prior `researchField?.value === "on"` gate
  // is removed from visibility (the OFF/ON Control itself is hidden
  // below, not deleted; the Backend Toggle Contract still exists and
  // still drives `onApply`, so a future Rollback only needs to un-hide
  // the Control, not rebuild it).
  const statusKey =
    state.capability === "loading"
      ? "configurationLoading"
      : state.capability === "ready"
        ? "configurationReady"
        : "configurationFailed";

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
          <dl className="configuration-meta">
            <dt>{translate(language, "configurationRevision")}</dt>
            <dd>{snapshot.revision}</dd>
            <dt>{translate(language, "configurationDigest")}</dt>
            <dd>{snapshot.digest_sha512}</dd>
          </dl>
          <div className="configuration-fields" role="list">
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
          <div className="configuration-controls" hidden>
            <div
              className="configuration-toggle"
              role="radiogroup"
              aria-label={translate(language, "configurationResearchMode")}
            >
              <span id="configuration-research-mode-label">
                {translate(language, "configurationResearchMode")}
              </span>
              {(["off", "on"] as const).map((mode) => (
                <button
                  key={mode}
                  id={`configuration-research-mode-${mode}`}
                  className="secondary"
                  type="button"
                  role="radio"
                  aria-checked={researchField?.value === mode}
                  disabled={state.capability !== "ready"}
                  onClick={() => {
                    if (researchField?.value !== mode) {
                      onApply(mode);
                    }
                  }}
                >
                  {mode.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
      <pre id="configuration-result" className="configuration-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
