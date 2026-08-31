import { useState } from "react";

import { translate } from "../i18n/translations";
import type { UiLanguage, WebSearchResult } from "../types";

export interface DirectUrlFetchState {
  capability: "idle" | "loading" | "ready" | "failed";
  result: WebSearchResult | null;
  resultText: string;
}

const IDLE_DIRECT_URL_STATE: DirectUrlFetchState = {
  capability: "idle",
  result: null,
  resultText: "",
};

export interface WebSearchPanelState {
  capability: "idle" | "loading" | "ready" | "failed";
  result: WebSearchResult | null;
  resultText: string;
  // Optional (P8-A): every pre-Phase-8 caller/Test constructs this state
  // shape without a Direct URL slice — defaulting to `IDLE_DIRECT_URL_STATE`
  // below keeps every one of those construction sites correct unchanged.
  directUrl?: DirectUrlFetchState;
}

interface WebSearchPanelProps {
  language: UiLanguage;
  visible: boolean;
  toggleEnabled: boolean;
  state: WebSearchPanelState;
  onSearch: (query: string) => void;
  onFetchDirectUrl?: ((url: string) => void) | undefined;
}

function EvidenceList({
  language,
  evidence,
}: {
  language: UiLanguage;
  evidence: WebSearchResult["evidence"];
}) {
  return (
    <ul className="web-search-panel-results" role="list">
      {evidence.map((item) => (
        <li className="web-search-panel-result-item" role="listitem" key={item.evidence_id}>
          <strong>{item.title}</strong>
          <small>
            {item.canonical_url} · {item.source_authority}
          </small>
          {item.requested_url !== item.canonical_url ? (
            <small className="web-search-panel-redirected-from">
              {translate(language, "webSearchPanelRedirectedFrom")}: {item.requested_url}
            </small>
          ) : null}
          {item.rejected ? (
            <p>
              {translate(language, "webSearchPanelRejected")}: {item.rejection_reason}
            </p>
          ) : item.withheld_by_governance ? (
            <p>{translate(language, "webSearchPanelWithheld")}</p>
          ) : item.fetched ? (
            <>
              {/* P8-REQ-006/P8-ACC-008: fetched external Content is always
                  explicitly labelled Untrusted — it was never authored by
                  the User or the System Prompt. */}
              <p className="web-search-panel-untrusted-label">
                {translate(language, "webSearchPanelUntrustedLabel")}
              </p>
              <p>{item.fetched_content}</p>
            </>
          ) : (
            <p>{item.snippet}</p>
          )}
        </li>
      ))}
    </ul>
  );
}

export default function WebSearchPanel({
  language,
  visible,
  toggleEnabled,
  state,
  onSearch,
  onFetchDirectUrl,
}: WebSearchPanelProps) {
  const [query, setQuery] = useState("");
  const [directUrl, setDirectUrl] = useState("");
  const directUrlState = state.directUrl ?? IDLE_DIRECT_URL_STATE;

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

  const directUrlStatusKey =
    directUrlState.capability === "loading"
      ? "webSearchPanelDirectUrlLoading"
      : directUrlState.capability === "ready"
        ? "webSearchPanelDirectUrlReady"
        : directUrlState.capability === "failed"
          ? "webSearchPanelDirectUrlFailed"
          : "webSearchPanelDirectUrlIdle";

  const handleSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !toggleEnabled) {
      return;
    }
    onSearch(trimmed);
  };

  const handleDirectUrlSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    const trimmed = directUrl.trim();
    if (!trimmed || !toggleEnabled || onFetchDirectUrl === undefined) {
      return;
    }
    onFetchDirectUrl(trimmed);
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
        <EvidenceList language={language} evidence={state.result.evidence} />
      ) : null}
      <pre id="web-search-panel-result" className="web-search-panel-result-log" aria-live="polite">
        {state.resultText}
      </pre>

      <div className="web-search-panel-direct-url-header">
        <h3 id="web-search-panel-direct-url-title">
          {translate(language, "webSearchPanelDirectUrlTitle")}
        </h3>
        <p id="web-search-panel-direct-url-note">
          {translate(language, "webSearchPanelDirectUrlNote")}
        </p>
      </div>
      <form
        className="web-search-panel-direct-url-form"
        onSubmit={(event) => {
          handleDirectUrlSubmit(event);
        }}
      >
        <label htmlFor="web-search-panel-direct-url">
          {translate(language, "webSearchPanelDirectUrlLabel")}
        </label>
        <input
          id="web-search-panel-direct-url"
          type="url"
          value={directUrl}
          disabled={!toggleEnabled}
          onChange={(event) => {
            setDirectUrl(event.target.value);
          }}
        />
        <button
          type="submit"
          className="secondary"
          disabled={
            !toggleEnabled ||
            directUrlState.capability === "loading" ||
            onFetchDirectUrl === undefined
          }
        >
          {translate(language, "webSearchPanelDirectUrlFetch")}
        </button>
      </form>
      <p id="web-search-panel-direct-url-status">{translate(language, directUrlStatusKey)}</p>
      {directUrlState.result !== null ? (
        <EvidenceList language={language} evidence={directUrlState.result.evidence} />
      ) : null}
      <pre
        id="web-search-panel-direct-url-result"
        className="web-search-panel-result-log"
        aria-live="polite"
      >
        {directUrlState.resultText}
      </pre>
    </section>
  );
}
