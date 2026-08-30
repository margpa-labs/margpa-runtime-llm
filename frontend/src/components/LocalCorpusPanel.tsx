import { useState } from "react";
import type { SyntheticEvent } from "react";

import { translate } from "../i18n/translations";
import type { LocalCorpusDocumentSummary, UiLanguage } from "../types";

export interface LocalCorpusState {
  capability: "loading" | "ready" | "failed" | "disabled";
  documents: LocalCorpusDocumentSummary[];
  resultText: string;
}

interface LocalCorpusPanelProps {
  language: UiLanguage;
  visible: boolean;
  state: LocalCorpusState;
  onRefresh: () => void;
  onRegister: (title: string, content: string) => void;
  onUpdate: (documentId: string, title: string, content: string) => void;
  onDelete: (documentId: string) => void;
  onEditRequest: (documentId: string) => Promise<{ title: string; content: string } | null>;
}

export default function LocalCorpusPanel({
  language,
  visible,
  state,
  onRefresh,
  onRegister,
  onUpdate,
  onDelete,
  onEditRequest,
}: LocalCorpusPanelProps) {
  const [editingDocumentId, setEditingDocumentId] = useState<string | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formContent, setFormContent] = useState("");

  if (!visible) {
    return null;
  }

  const statusKey =
    state.capability === "loading"
      ? "localCorpusLoading"
      : state.capability === "ready"
        ? "localCorpusReady"
        : "localCorpusFailed";

  const resetForm = () => {
    setEditingDocumentId(null);
    setFormTitle("");
    setFormContent("");
  };

  const handleSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    const title = formTitle.trim();
    const content = formContent.trim();
    if (!title || !content) {
      return;
    }
    if (editingDocumentId !== null) {
      onUpdate(editingDocumentId, title, content);
    } else {
      onRegister(title, content);
    }
    resetForm();
  };

  const handleEdit = async (documentId: string) => {
    const document = await onEditRequest(documentId);
    if (document === null) {
      return;
    }
    setEditingDocumentId(documentId);
    setFormTitle(document.title);
    setFormContent(document.content);
  };

  return (
    <section id="local-corpus-panel" className="local-corpus-panel" aria-label={translate(language, "localCorpusTitle")}>
      <div className="local-corpus-panel-header">
        <div>
          <h2 id="local-corpus-title">{translate(language, "localCorpusTitle")}</h2>
          <p id="local-corpus-note">{translate(language, "localCorpusNote")}</p>
        </div>
        <button
          id="local-corpus-refresh"
          className="secondary"
          type="button"
          disabled={state.capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "localCorpusRefresh")}
        </button>
      </div>
      <p id="local-corpus-status">{translate(language, statusKey)}</p>
      <form className="local-corpus-form" onSubmit={handleSubmit}>
        <label htmlFor="local-corpus-form-title">{translate(language, "localCorpusFormTitleLabel")}</label>
        <input
          id="local-corpus-form-title"
          type="text"
          value={formTitle}
          maxLength={200}
          onChange={(event) => {
            setFormTitle(event.target.value);
          }}
        />
        <label htmlFor="local-corpus-form-content">{translate(language, "localCorpusFormContentLabel")}</label>
        <textarea
          id="local-corpus-form-content"
          value={formContent}
          rows={6}
          onChange={(event) => {
            setFormContent(event.target.value);
          }}
        />
        <div className="local-corpus-form-actions">
          <button type="submit" className="secondary">
            {translate(
              language,
              editingDocumentId !== null ? "localCorpusFormUpdate" : "localCorpusFormRegister",
            )}
          </button>
          {editingDocumentId !== null ? (
            <button type="button" className="secondary" onClick={resetForm}>
              {translate(language, "localCorpusFormCancel")}
            </button>
          ) : null}
        </div>
      </form>
      <ul className="local-corpus-list" role="list">
        {state.documents.map((item) => (
          <li className="local-corpus-list-item" role="listitem" key={item.document_id}>
            <strong>{item.title}</strong>
            <small>
              rev {item.current_revision} · {item.character_count} chars
            </small>
            <div className="local-corpus-list-actions">
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  void handleEdit(item.document_id);
                }}
              >
                {translate(language, "localCorpusEdit")}
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  onDelete(item.document_id);
                }}
              >
                {translate(language, "localCorpusDelete")}
              </button>
            </div>
          </li>
        ))}
      </ul>
      <pre id="local-corpus-result" className="local-corpus-result" aria-live="polite">
        {state.resultText}
      </pre>
    </section>
  );
}
