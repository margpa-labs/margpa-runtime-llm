import { translate } from "../i18n/translations";
import type { PersistentTurnWebCitations, UiLanguage } from "../types";
import CopyButton from "./CopyButton";

interface WebCitationsSectionProps {
  language: UiLanguage;
  evidence: PersistentTurnWebCitations;
}

function shortenDigest(value: string): string {
  return value.length <= 12 ? value : `${value.slice(0, 12)}…`;
}

type TransformationLabelKey =
  | "webCitationTransformationHtmlTextExtracted"
  | "webCitationTransformationRaw";

function transformationLabelKey(value: string): TransformationLabelKey {
  return value === "html_text_extracted"
    ? "webCitationTransformationHtmlTextExtracted"
    : "webCitationTransformationRaw";
}

// P8-A: the Manual URL Fetch analogue of `CitationsSection.tsx` — a
// structurally separate Source Class (`public_web`, never merged into the
// Documentation `Citation` shape) with its own small set of Fields
// (Canonical URL, Title, Content Type, Digest), always labelled Untrusted.
export default function WebCitationsSection({ language, evidence }: WebCitationsSectionProps) {
  const citations = evidence.citations;
  return (
    <section className="message-citations message-web-citations">
      <div className="message-citations-label">{translate(language, "webCitationsLabel")}</div>
      <div className="message-citations-list">
        {citations.length === 0 ? (
          <div className="message-citation-empty">
            {evidence.failure_reason !== null ? (
              <>
                {`${translate(language, "webSearchPanelRejected")}: ${evidence.failure_reason}`}
                {evidence.specific_failure_reason !== null ? (
                  <span className="web-citation-specific-reason">
                    {" "}
                    ({translate(language, "webCitationSpecificReasonLabel")}:{" "}
                    {evidence.specific_failure_reason})
                  </span>
                ) : null}
              </>
            ) : (
              translate(language, "webSearchPanelDirectUrlIdle")
            )}
          </div>
        ) : null}
        {citations.map((citation, index) => (
          <div className="message-citation" key={`${citation.citation_id}-${index.toString()}`}>
            <div className="message-citation-row">
              <span className="message-citation-field-label">
                {translate(language, "citationFieldSource")}
              </span>
              <span className="message-citation-source">
                {translate(language, "webCitationSourcePublicWeb")}
              </span>
            </div>
            <div className="message-citation-row">
              <span className="message-citation-field-label">
                {translate(language, "citationFieldTitle")}
              </span>
              <span>{citation.title}</span>
            </div>
            <div className="message-citation-row">
              <span className="message-citation-field-label">
                {translate(language, "webCitationFieldUrl")}
              </span>
              <code>{citation.canonical_url}</code>
              <CopyButton
                language={language}
                text={citation.canonical_url}
                translationKey="copyCanonicalUrl"
                className="message-copy secondary"
              />
            </div>
            {citation.requested_url !== citation.canonical_url ? (
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "webSearchPanelRedirectedFrom")}
                </span>
                <code>{citation.requested_url}</code>
                <CopyButton
                  language={language}
                  text={citation.requested_url}
                  translationKey="copyRequestedUrl"
                  className="message-copy secondary"
                />
              </div>
            ) : null}
            <div className="message-citation-row">
              <span className="message-citation-field-label">
                {translate(language, "webCitationFieldSourceAuthority")}
              </span>
              <span>{citation.source_authority}</span>
            </div>
            {citation.fetched_at !== null ? (
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "webCitationFieldFetchedAt")}
                </span>
                <span>{citation.fetched_at}</span>
              </div>
            ) : null}
            {citation.content_type !== null ? (
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "webCitationFieldContentType")}
                </span>
                <span>{citation.content_type}</span>
              </div>
            ) : null}
            <div className="message-citation-row">
              <span className="message-citation-field-label">
                {translate(language, "webCitationFieldTransformation")}
              </span>
              <span>{translate(language, transformationLabelKey(citation.transformation))}</span>
            </div>
            {citation.content_sha512 !== null ? (
              <div className="message-citation-row">
                <span className="message-citation-field-label">
                  {translate(language, "citationFieldDocumentDigest")}
                </span>
                <code className="message-citation-identity" title={citation.content_sha512}>
                  {shortenDigest(citation.content_sha512)}
                </code>
                <CopyButton
                  language={language}
                  text={citation.content_sha512}
                  translationKey="copyDocumentDigest"
                  className="message-copy secondary"
                />
              </div>
            ) : null}
            <p className="web-search-panel-untrusted-label">
              {translate(language, "webSearchPanelUntrustedLabel")}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
