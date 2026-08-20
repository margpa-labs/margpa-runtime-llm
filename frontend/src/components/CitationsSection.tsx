import { translate, knownServerMessages } from "../i18n/translations";
import type { CitationEvidence, UiLanguage } from "../types";
import CopyButton from "./CopyButton";

interface CitationsSectionProps {
  language: UiLanguage;
  evidence: CitationEvidence;
}

export default function CitationsSection({ language, evidence }: CitationsSectionProps) {
  const citations = evidence.citations;
  return (
    <section className="message-citations">
      <div className="message-citations-label">{translate(language, "citationsLabel")}</div>
      <div className="message-citations-list">
        {citations.length === 0 ? <EmptyCitations language={language} evidence={evidence} /> : null}
        {citations.map((citation, index) => (
          <div className="message-citation" key={`${citation.project_relative_path}-${index.toString()}`}>
            <code>{citation.project_relative_path}</code>
            <span>{citation.heading_breadcrumb ?? ""}</span>
            <CopyButton
              language={language}
              text={citation.project_relative_path}
              translationKey="copyPath"
              className="message-copy secondary"
            />
          </div>
        ))}
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
