import { useMemo } from "react";
import { translate } from "../i18n/translations";
import { containsTable, parseSafeMarkdown, renderSafeMarkdownBlocks } from "../lib/safeMarkdown";
import type { DisplayMessage, LiveJudgeBadge, UiLanguage } from "../types";
import CopyButton from "./CopyButton";
import CitationsSection from "./CitationsSection";
import WebCitationsSection from "./WebCitationsSection";

interface MessageBubbleProps {
  language: UiLanguage;
  message: DisplayMessage;
  onTurnAction?: (turnId: string, kind: "retry" | "regenerate" | "selectBranch") => void;
  // P6-CODEX-024 (Third Rework): already correlated to this exact
  // `message` by the caller (`MessageList`) — this component only ever
  // decides *how* to render it, never re-checks *whether* it applies.
  judgeBadge?: LiveJudgeBadge | null;
  // P8-B (P8-REQ-009): a purely Presentation-layer Boundary — `message.
  // turnActions` itself always carries the real, complete Branch data
  // (`persistentDetailProjection.ts` is unchanged), so Branch Data/API/
  // History stay fully intact either way (P8-REQ-009's own "既定非表示"
  // is a display default, never a data deletion). Defaults to hidden.
  branchUiVisible?: boolean;
}

// P6-CODEX-024, updated P6-CODEX-031 (Fourth Rework): a deliberately
// curated subset of the full backend Judge Run vocabulary (idle/
// queued_or_skipped/judging/repairing/rejudging/completed/failed/
// cancelled/degraded — see `JudgeGovernanceComposition`) — `idle`/
// `queued_or_skipped`/`failed`/`cancelled` are Judge-internal outcomes
// that do not change anything about the Canonical Answer already shown
// and would only add noise to the Chat surface for the common case; the
// full vocabulary (including the distinct judging/repairing/rejudging
// sub-states) remains fully visible in the Feature Modes Panel for
// debugging/Observability (P6-OBS-004 is satisfied there). This is a
// disclosed scope choice (see the Fourth Rework Candidate Handoff), not
// a hidden gap — the three in-flight sub-states collapse to one Chat
// Bubble label deliberately, not because the distinction is unknown here.
function judgeBadgeLabelKey(
  badge: LiveJudgeBadge,
): "chatLiveJudgeRunning" | "chatLiveJudgeImproved" | "chatLiveJudgeDegraded" | null {
  if (badge.state === "judging" || badge.state === "repairing" || badge.state === "rejudging") {
    return "chatLiveJudgeRunning";
  }
  if (badge.state === "degraded") {
    return "chatLiveJudgeDegraded";
  }
  if (badge.state === "completed" && badge.repairAccepted === true) {
    return "chatLiveJudgeImproved";
  }
  return null;
}

export default function MessageBubble({
  language,
  message,
  onTurnAction,
  judgeBadge = null,
  branchUiVisible = false,
}: MessageBubbleProps) {
  const judgeBadgeLabel = judgeBadge === null ? null : judgeBadgeLabelKey(judgeBadge);
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
  const showWebCitations = isAssistant && message.webCitations !== null;
  const showCopy = !isAssistant || message.isFinal;
  // P8-B (P8-REQ-009): filters the rendered Buttons only — `message.
  // turnActions` (the Data) is never mutated.
  const visibleTurnActions = message.turnActions.filter(
    (action) => action.kind !== "selectBranch" || branchUiVisible,
  );

  return (
    <div id={message.id} className={classNames} data-request-id={message.requestId ?? undefined}>
      {showThinking ? (
        <section className="message-thinking">
          <div className="message-thinking-label">{translate(language, "thinkingRegionLabel")}</div>
          <div className="message-thinking-content">{message.thinkingText}</div>
        </section>
      ) : null}
      <div className={`message-content${markdown?.ok ? " message-markdown" : " message-final"}`}>
        {markdown !== null && markdown.ok ? markdown.node : message.content}
      </div>
      {judgeBadgeLabel !== null ? (
        <p
          id={`${message.id}-judge-badge`}
          className={`message-judge-badge message-judge-badge-${judgeBadge?.state ?? "unknown"}`}
          aria-live="polite"
        >
          {translate(language, judgeBadgeLabel)}
        </p>
      ) : null}
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
      {showWebCitations && message.webCitations !== null ? (
        <WebCitationsSection language={language} evidence={message.webCitations} />
      ) : null}
      {showCopy || visibleTurnActions.length > 0 ? (
        <div className="message-actions">
          {/* DOM order determines left-to-right position under
              justify-content: flex-end — branch-select/retry first,
              regenerate next, Copy last so it lands rightmost. */}
          {visibleTurnActions.map((action) => (
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
