import { useEffect, useRef } from "react";
import { translate, type TranslationKey } from "../i18n/translations";
import type { DisplayMessage, LiveJudgeBadge, UiLanguage } from "../types";
import MessageBubble from "./MessageBubble";

interface MessageListProps {
  language: UiLanguage;
  messages: DisplayMessage[];
  emptyTitleKey: TranslationKey;
  emptyNoteKey: TranslationKey;
  onTurnAction: (turnId: string, kind: "retry" | "regenerate" | "selectBranch") => void;
  pinnedMessageId: string | null;
  active: boolean;
  // P6-CODEX-024 (Third Rework): Current-Request-correlated, never a
  // fabricated "current" state for any Turn other than the one it actually
  // names — `MessageBubble` itself does the exact-match check.
  liveJudgeBadge: LiveJudgeBadge | null;
}

// Clearance kept between the fixed top-right topbar pill and a pinned
// question, in pixels.
const PINNED_TOP_GAP_PX = 76;
// Clearance kept between the tail of the answer and the fixed composer
// overlaying the bottom of the viewport, in pixels.
const COMPOSER_BOTTOM_GAP_PX = 16;

export default function MessageList({
  language,
  messages,
  emptyTitleKey,
  emptyNoteKey,
  onTurnAction,
  pinnedMessageId,
  active,
  liveJudgeBadge,
}: MessageListProps) {
  // .messages no longer scrolls internally (it grows to fit its content,
  // and the page itself scrolls) — so "scroll to latest" means scrolling a
  // trailing sentinel into view within whatever ancestor actually scrolls,
  // rather than setting scrollTop on this element directly.
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // A live send only actively re-anchors the scroll position while
  // generating — pinnedMessageId itself stays set after completion (see
  // App.tsx) so that once generation stops, the view is meant to stay
  // exactly where the stream left it rather than jump anywhere.
  const isPinning = active && pinnedMessageId !== null;
  // The gap-filler, however, must keep existing after generation stops too:
  // it is what made the pinned scrollTop reachable in the first place, and
  // removing it the instant generation ends would shrink the container back
  // down, making the browser auto-clamp scrollTop back toward 0 and silently
  // undo the pin right as it settles — exactly the moment it needs to hold.
  // It only clears once pinnedMessageId itself is cleared or replaced (next
  // send, conversation switch, new chat, retry/regenerate — see App.tsx).
  const reservesGap = pinnedMessageId !== null;

  // Three scroll modes.
  // - Not pinning, no target id (conversation load/switch/new chat): jump to
  //   the trailing sentinel, showing the tail of history as before.
  // - Not pinning, but a target id lingers from the turn that just finished:
  //   don't re-anchor to the top — leave the view where it settled during
  //   the stream — but still run the composer-clearance check below, so a
  //   long answer's final tail isn't left hidden behind the fixed composer.
  // - Pinning: re-anchor the question near the top on every update via an
  //   explicit scrollTop computation. scrollIntoView's own block:"start"
  //   was tried first but .main-content's own top padding (kept for the
  //   topbar's general clearance) leaves no scrollable range to move into
  //   when the conversation is still short — no amount of computed target
  //   can scroll past content that isn't there. The gapFiller div rendered
  //   below, present whenever pinnedMessageId is set, exists purely to
  //   guarantee that scrollable range regardless of how little has streamed
  //   in so far.
  useEffect(() => {
    if (pinnedMessageId === null) {
      bottomRef.current?.scrollIntoView({ block: "end" });
      return;
    }
    const container = document.querySelector<HTMLElement>(".main-content");
    if (container === null) {
      return;
    }
    if (isPinning) {
      const pinned = document.getElementById(pinnedMessageId);
      if (pinned !== null) {
        const containerRect = container.getBoundingClientRect();
        const pinnedRect = pinned.getBoundingClientRect();
        const targetScrollTop =
          container.scrollTop + (pinnedRect.top - containerRect.top) - PINNED_TOP_GAP_PX;
        container.scrollTop = Math.max(0, targetScrollTop);
      }
    }

    // Keep the answer's tail clear of the fixed composer — both while still
    // pinning (a long, still-growing answer needs to follow its own tail
    // downward, which naturally scrolls the pinned question up and out of
    // view) and once settled (the reload after completion can render the
    // final markdown slightly taller than the last streamed chunk did).
    const composer = document.querySelector<HTMLElement>(".composer");
    const sentinel = bottomRef.current;
    if (composer !== null && sentinel !== null) {
      const composerRect = composer.getBoundingClientRect();
      const sentinelRect = sentinel.getBoundingClientRect();
      const overflowBy = sentinelRect.bottom - (composerRect.top - COMPOSER_BOTTOM_GAP_PX);
      if (overflowBy > 0) {
        container.scrollTop += overflowBy;
      }
    }
  }, [messages, pinnedMessageId, isPinning]);

  return (
    <div id="messages" className="messages" role="log" aria-label={translate(language, "messagesLabel")}>
      {messages.length === 0 ? (
        <div className="empty-state-wrap">
          <div className="empty-state">
            <h2>{translate(language, emptyTitleKey)}</h2>
            <p>{translate(language, emptyNoteKey)}</p>
          </div>
          <p className="empty-state-greeting">{translate(language, "emptyStateGreeting")}</p>
        </div>
      ) : (
        messages.map((message) => (
          <MessageBubble
            key={message.id}
            language={language}
            message={message}
            onTurnAction={onTurnAction}
            judgeBadge={
              message.requestId !== null && liveJudgeBadge?.requestId === message.requestId
                ? liveJudgeBadge
                : null
            }
          />
        ))
      )}
      <div ref={bottomRef} />
      {reservesGap && <div className="messages-gap-filler" aria-hidden="true" />}
    </div>
  );
}
