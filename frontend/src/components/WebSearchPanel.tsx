import { useState } from "react";

import { translate } from "../i18n/translations";
import type { UiLanguage, WebSearchResult } from "../types";

export interface WebSearchPanelState {
  capability: "idle" | "loading" | "ready" | "failed";
  result: WebSearchResult | null;
  resultText: string;
}

interface WebSearchPanelProps {
  language: UiLanguage;
  visible: boolean;
  toggleEnabled: boolean;
  state: WebSearchPanelState;
  onSearch: (query: string) => void;
}

export default function WebSearchPanel({
  language,
  visible,
  toggleEnabled,
  state,
  onSearch,
}: WebSearchPanelProps) {
  const [query, setQuery] = useState("");

  if (!visible) {
    return null;
  }

  const statusKey =
    state.capability === "loading"
      ? "webSearchPanelLoading"
      : state.capability === "ready"
        ? "webSearchPanelReady"
        : state.capability === "failed"
          ? "webSearchPanelFailed"
          : "webSearchPanelIdle";

  const handleSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !toggleEnabled) {
      return;
    }
    onSearch(trimmed);
  };

  return (
    <section id="web-search-panel" className="web-search-panel" aria-label={translate(language, "webSearchPanelTitle")}>
      <div className="web-search-panel-header">
        <div>
          <h2 id="web-search-panel-title">{translate(language, "webSearchPanelTitle")}</h2>
          <p id="web-search-panel-note">{translate(language, "webSearchPanelNote")}</p>
        </div>
      </div>
      {!toggleEnabled ? (
        <p id="web-search-panel-off-note">{translate(language, "webSearchPanelToggleOff")}</p>
      ) : null}
      <form
        className="web-search-panel-form"
        onSubmit={(event) => {
          handleSubmit(event);
        }}
      >
        <label htmlFor="web-search-panel-query">{translate(language, "webSearchPanelQueryLabel")}</label>
        <input
          id="web-search-panel-query"
          type="text"
          value={query}
          disabled={!toggleEnabled}
          onChange={(event) => {
            setQuery(event.target.value);
          }}
        />
        <button
          type="submit"
          className="secondary"
          disabled={!toggleEnabled || state.capability === "loading"}
        >
          {translate(language, "webSearchPanelSearch")}
        </button>
      </form>
      <p id="web-search-panel-status">{translate(language, statusKey)}</p>
      {state.result !== null ? (
        <ul className="web-search-panel-results" role="list">
          {state.result.evidence.map((item) => (
            <li className="web-search-panel-result-item" role="listitem" key={item.evidence_id}>
              <strong>{item.title}</strong>
              <small>
                {item.canonical_url} · {item.source_authority}
              </small>
              {item.rejected ? (
                <p>
                  {translate(language, "webSearchPanelRejected")}: {item.rejection_reason}
                </p>
              ) : item.withheld_by_governance ? (
                <p>{translate(language, "webSearchPanelWithheld")}</p>
              ) : item.fetched ? (
                <p>{item.fetched_content}</p>
              ) : (
                <p>{item.snippet}</p>
              )}
            </li>
          ))}
        </ul>
      ) : null}
      <pre id="web-search-panel-result" className="web-search-panel-result-log" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
