import { translate, knownServerMessages } from "../i18n/translations";
import type { CitationEvidence, UiLanguage } from "../types";
import CopyButton from "./CopyButton";

// Mirrors `LOCAL_CORPUS_SOURCE_CLASS` in
// `modules/documentation_rag/local_corpus_contracts.py` — every other
// `source_class` value (Project Docs) renders as "Project Docs".
const LOCAL_CORPUS_SOURCE_CLASS = "local_corpus";

interface CitationsSectionProps {
  language: UiLanguage;
  evidence: CitationEvidence;
}

function shortenIdentity(value: string): string {
  return value.length <= 12 ? value : `${value.slice(0, 12)}…`;
}

export default function CitationsSection({ language, evidence }: CitationsSectionProps) {
  const citations = evidence.citations;
  return (
    <section className="message-citations">
      <div className="message-citations-label">{translate(language, "citationsLabel")}</div>
      <div className="message-citations-list">
        {citations.length === 0 ? <EmptyCitations language={language} evidence={evidence} /> : null}
        {citations.map((citation, index) => {
          const isLocalCorpus = citation.source_class === LOCAL_CORPUS_SOURCE_CLASS;
          // P7-RW5-C (P7-CODEX-016): the real backing storage File for a
          // Local Corpus Citation - `project_relative_path` stays the
          // Synthetic `local-corpus/<slug>.md` Citation identity, never
          // shown to the User. Falls back to `project_relative_path` for
          // Project Docs (always `null` here) and for any Local Corpus
          // Citation persisted before this field existed.
          const displayPath = citation.storage_display_path ?? citation.project_relative_path;
          return (
            <div className="message-citation" key={`${citation.chunk_id}-${index.toString()}`}>
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "citationFieldSource")}
                </span>
                <span
                  className={
                    isLocalCorpus
                      ? "message-citation-source message-citation-source-local"
                      : "message-citation-source message-citation-source-project"
                  }
                >
                  {translate(
                    language,
                    isLocalCorpus ? "citationSourceLocalCorpus" : "citationSourceProjectDocs",
                  )}
                </span>
              </div>
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, isLocalCorpus ? "citationFieldTitle" : "citationFieldHeading")}
                </span>
                {/* P7-RW5-B (P7-CODEX-015): Local Corpus shows the
                registered Document Title (never an empty Markdown
                Heading, which this Source never has); Project Docs keeps
                its existing Heading Breadcrumb. */}
                <span>{(isLocalCorpus ? citation.document_title : citation.heading_breadcrumb) ?? ""}</span>
              </div>
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "citationFieldPath")}
                </span>
                <code>{displayPath}</code>
                <CopyButton
                  language={language}
                  text={displayPath}
                  translationKey="copyPath"
                  className="message-copy secondary"
                />
              </div>
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "citationFieldChunkId")}
                </span>
                <code className="message-citation-identity" title={citation.chunk_id}>
                  {shortenIdentity(citation.chunk_id)}
                </code>
                <CopyButton
                  language={language}
                  text={citation.chunk_id}
                  translationKey="copyChunkId"
                  className="message-copy secondary"
                />
              </div>
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "citationFieldDocumentDigest")}
                </span>
                <code className="message-citation-identity" title={citation.document_sha512}>
                  {shortenIdentity(citation.document_sha512)}
                </code>
                <CopyButton
                  language={language}
                  text={citation.document_sha512}
                  translationKey="copyDocumentDigest"
                  className="message-copy secondary"
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function EmptyCitations({ language, evidence }: CitationsSectionProps) {
  const reason = evidence.warnings.find((warning) => knownServerMessages[warning.code] !== undefined);
  if (reason === undefined) {
    return <div className="message-citation-empty">{translate(language, "noCitations")}</div>;
  }
  const key = knownServerMessages[reason.code];
  const text = key !== undefined ? translate(language, key) : reason.message;
  return <div className="message-citation-empty">{text}</div>;
}
