import { translate, type TranslationKey } from "../i18n/translations";
import type { PersistentConversationSummary, UiLanguage } from "../types";

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

// P8-B (P8-REQ-010): "idle" (never yet requested — the Lazy default) is a
// distinct state from "loading", so the section can render a plain
// "Show Archived Chats" trigger without pretending a fetch is already
// in flight.
export interface ArchivedChatsState {
  capability: "idle" | "loading" | "ready" | "failed";
  items: PersistentConversationSummary[];
  resultText: string;
}

interface DataControlsPanelProps {
  language: UiLanguage;
  visible: boolean;
  state: DataControlsState;
  onRefresh: () => void;
  onToggle: (key: keyof DataControlConsentState, value: boolean) => void;
  onReset: () => void;
  // P8-B: Archived Chats only exist when Persistent Conversation Mode is
  // active (a different capability than Data Controls/consent itself,
  // which this whole Panel is already separately gated on).
  archivedChatsAvailable: boolean;
  archivedChatsState: ArchivedChatsState;
  onArchivedChatsLoad: () => void;
  onArchivedChatsClose: () => void;
  onArchivedChatsOpen: (conversationId: string) => void;
  onArchivedChatsUnarchive: (conversationId: string) => void;
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
  archivedChatsAvailable,
  archivedChatsState,
  onArchivedChatsLoad,
  onArchivedChatsClose,
  onArchivedChatsOpen,
  onArchivedChatsUnarchive,
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

  const archivedStatusKey =
    archivedChatsState.capability === "loading"
      ? "archivedChatsLoading"
      : archivedChatsState.capability === "failed"
        ? "archivedChatsFailed"
        : null;

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
      {archivedChatsAvailable ? (
        <div id="data-controls-archived-chats">
          <h3>{translate(language, "archivedChatsTitle")}</h3>
          <p id="archived-chats-note">{translate(language, "archivedChatsNote")}</p>
          {archivedChatsState.capability === "idle" ? (
            <button
              id="archived-chats-load"
              className="secondary"
              type="button"
              onClick={onArchivedChatsLoad}
            >
              {translate(language, "archivedChatsShow")}
            </button>
          ) : (
            <>
              <button
                id="archived-chats-close"
                className="secondary"
                type="button"
                onClick={onArchivedChatsClose}
              >
                {translate(language, "archivedChatsClose")}
              </button>
              {archivedStatusKey !== null ? (
                <p id="archived-chats-status">{translate(language, archivedStatusKey)}</p>
              ) : null}
              {archivedChatsState.capability === "ready" && archivedChatsState.items.length === 0 ? (
                <p id="archived-chats-empty">{translate(language, "archivedChatsEmpty")}</p>
              ) : null}
              {archivedChatsState.items.length > 0 ? (
                <ul id="archived-chats-list" role="list">
                  {archivedChatsState.items.map((item) => (
                    <li role="listitem" key={item.conversation_id} className="archived-chat-item">
                      {/* Mirrors `ChatListItem.tsx`'s own untitled-chat fallback exactly
                          (no dedicated "Untitled" translation key exists there either). */}
                      <div className="archived-chat-item-title">
                        {item.title ??
                          `${new Date(item.updated_at).toLocaleString()} · ${item.conversation_id.slice(0, 10)}`}
                      </div>
                      <div className="archived-chat-item-timestamp">
                        {new Date(item.updated_at).toLocaleString(language)}
                      </div>
                      <div className="archived-chat-item-actions">
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => {
                            onArchivedChatsOpen(item.conversation_id);
                          }}
                        >
                          {translate(language, "archivedChatsOpen")}
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => {
                            onArchivedChatsUnarchive(item.conversation_id);
                          }}
                        >
                          {translate(language, "persistentUnarchive")}
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : null}
            </>
          )}
        </div>
      ) : null}
    </section>
  );
}
