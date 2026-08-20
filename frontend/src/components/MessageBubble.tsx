import { useMemo } from "react";
import { translate } from "../i18n/translations";
import { containsTable, parseSafeMarkdown, renderSafeMarkdownBlocks } from "../lib/safeMarkdown";
import type { DisplayMessage, UiLanguage } from "../types";
import CopyButton from "./CopyButton";
import CitationsSection from "./CitationsSection";

interface MessageBubbleProps {
  language: UiLanguage;
  message: DisplayMessage;
  onTurnAction?: (turnId: string, kind: "retry" | "regenerate" | "selectBranch") => void;
}

export default function MessageBubble({ language, message, onTurnAction }: MessageBubbleProps) {
  const isAssistant = message.role === "assistant";
  // Rendered progressively while streaming too (not gated on isFinal
  // anymore) — the source itself (message.content) is untouched either way,
  // so Copy (wired to message.content, not this rendered view) always still
  // yields the raw markdown regardless of when it's clicked.
  const rendersMarkdown = isAssistant && !message.isError && !message.isIncomplete;

  const markdown = useMemo(() => {
    if (!rendersMarkdown) {
      return null;
    }
    try {
      const blocks = parseSafeMarkdown(message.content);
      return { node: renderSafeMarkdownBlocks(blocks), ok: true as const, hasTable: containsTable(blocks) };
    } catch {
      return { node: null, ok: false as const, hasTable: false };
    }
  }, [rendersMarkdown, message.content]);

  const classNames = [
    "message",
    `message-${message.role}`,
    isAssistant && message.isError ? "message-error" : "",
    isAssistant && message.isIncomplete ? "message-incomplete" : "",
    markdown?.hasTable ? "message-wide" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const showThinking = isAssistant && message.thinkingText.length > 0;
  const showCitations = isAssistant && message.citations !== null;
  const showCopy = !isAssistant || message.isFinal;

  return (
    <div id={message.id} className={classNames}>
      {showThinking ? (
        <section className="message-thinking">
          <div className="message-thinking-label">{translate(language, "thinkingRegionLabel")}</div>
          <div className="message-thinking-content">{message.thinkingText}</div>
        </section>
      ) : null}
      <div className={`message-content${markdown?.ok ? " message-markdown" : " message-final"}`}>
        {markdown !== null && markdown.ok ? markdown.node : message.content}
      </div>
      {/* Suppressed until isFinal: a still-streaming answer routinely has a
          transiently unparsable tail (e.g. an unclosed code fence waiting on
          more tokens) — that's expected mid-stream, not a genuine failure,
          so this note would otherwise flash on/off throughout the stream. */}
      {rendersMarkdown && message.isFinal && markdown !== null && !markdown.ok ? (
        <p className="setting-note">{translate(language, "markdownFallback")}</p>
      ) : null}
      {showCitations && message.citations !== null ? (
        <CitationsSection language={language} evidence={message.citations} />
      ) : null}
      {showCopy || message.turnActions.length > 0 ? (
        <div className="message-actions">
          {/* DOM order determines left-to-right position under
              justify-content: flex-end — branch-select/retry first,
              regenerate next, Copy last so it lands rightmost. */}
          {message.turnActions.map((action) => (
            <button
              type="button"
              className="message-copy secondary"
              key={action.kind}
              onClick={() => {
                onTurnAction?.(action.turnId, action.kind);
              }}
            >
              {translate(
                language,
                action.kind === "retry"
                  ? "persistentRetry"
                  : action.kind === "regenerate"
                    ? "persistentRegenerate"
                    : "persistentSelectBranch",
              )}
            </button>
          ))}
          {showCopy ? <CopyButton language={language} text={message.content} /> : null}
        </div>
      ) : null}
    </div>
  );
}
