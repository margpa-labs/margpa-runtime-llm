import {
  translate,
  knownServerMessages,
  isSafetyRejectCode,
  type TranslationKey,
} from "../i18n/translations";
import type {
  DisplayMessage,
  PersistentConversationDetail,
  PersistentTurn,
  UiLanguage,
} from "../types";

/** P6-CODEX-015 (Second Rework): a `guardrail_*`/`governance_*` code not yet
 * in the explicit `knownServerMessages` table must still resolve to the
 * fixed Safe Refusal sentence, never fall through to a raw-code-bearing
 * fallback string — mirrors `is_safety_reject_code()` in
 * `runtime_observability/presentation/safe_refusal.py` so a new reason_code
 * introduced on the backend is safe-by-default on the frontend too. */
function resolvedMessageKey(code: string): TranslationKey | undefined {
  const explicit = knownServerMessages[code];
  if (explicit !== undefined) {
    return explicit;
  }
  return isSafetyRejectCode(code) ? "safeRefusalMessage" : undefined;
}

export function translatedServerMessage(
  language: UiLanguage,
  code: string,
  fallback: string,
): string {
  const key = resolvedMessageKey(code);
  return key === undefined
    ? fallback || translate(language, "genericError")
    : translate(language, key);
}

export function knownMessageText(
  language: UiLanguage,
  code: string | null,
  fallback: string,
): string {
  if (code !== null) {
    const key = resolvedMessageKey(code);
    if (key !== undefined) {
      return translate(language, key);
    }
  }
  return fallback || translate(language, "genericError");
}

export function emptyMessage(
  role: "user" | "assistant",
  content: string,
  id: string,
): DisplayMessage {
  return {
    id,
    role,
    content,
    isFinal: role === "user",
    isError: false,
    isIncomplete: false,
    errorCode: null,
    errorMessage: null,
    thinkingText: "",
    thinkingVisible: false,
    citations: null,
    webCitations: null,
    turnActions: [],
    requestId: null,
  };
}

function buildTurnActions(
  turn: PersistentTurn,
  detail: PersistentConversationDetail,
): DisplayMessage["turnActions"] {
  // Order matches the display row's left-to-right layout (right-aligned,
  // Copy always last/rightmost): branch-select, then regenerate.
  const actions: DisplayMessage["turnActions"] = [];
  if (["failed", "cancelled", "interrupted"].includes(turn.state)) {
    actions.push({ kind: "retry", turnId: turn.turn_id });
  }
  if (turn.state === "completed") {
    if (turn.turn_id !== detail.head_turn_id) {
      actions.push({ kind: "selectBranch", turnId: turn.turn_id });
    }
    actions.push({ kind: "regenerate", turnId: turn.turn_id });
  }
  return actions;
}

export function detailToMessages(
  detail: PersistentConversationDetail,
  uiLanguage: UiLanguage,
): DisplayMessage[] {
  const out: DisplayMessage[] = [];
  for (const turn of detail.turns) {
    const user = turn.messages.find((message) => message.role === "user");
    const assistant = turn.messages.find((message) => message.role === "assistant");
    if (user !== undefined) {
      out.push(emptyMessage("user", user.content, `${turn.turn_id}-user`));
    }
    if (assistant !== undefined) {
      const turnActions = buildTurnActions(turn, detail);
      out.push({
        ...emptyMessage("assistant", assistant.content, `${turn.turn_id}-assistant`),
        isFinal: true,
        citations:
          turn.citations?.available === true
            ? {
                citations: turn.citations.citations,
                // P7-RW5-A (P7-CODEX-014): reconstructs a NO_HIT "no
                // current grounds" display from the persisted
                // `warning_codes` alone - `citations` itself stays empty
                // for that Grounding State, and `CitationsSection`'s
                // `EmptyCitations` already resolves a known code (e.g.
                // `documentation_no_hit`) through the same
                // `knownServerMessages` table the Live SSE path uses, so
                // an empty `message` here is never actually shown. When
                // `citations` is non-empty (the ordinary Grounded case),
                // this array is unused by the rendering logic below.
                warnings: turn.citations.warning_codes.map((code) => ({ code, message: "" })),
              }
            : null,
        webCitations:
          turn.web_citations?.available === true
            ? {
                available: true,
                citations: turn.web_citations.citations,
                failure_reason: turn.web_citations.failure_reason,
                specific_failure_reason: turn.web_citations.specific_failure_reason,
              }
            : null,
        turnActions,
        requestId: turn.request_id ?? null,
      });
    } else if (turn.state === "failed" && turn.failure_reason_code) {
      // P6-CODEX-003: a Guardrail/Governance reject never persists a real
      // Assistant Message (P6-ACC-042 — Safe Refusal must never become
      // Assistant Authority), so Reload/Resume reconstructs the same fixed
      // Safe Refusal sentence the live SSE stream showed, purely for
      // client-side display — this synthesized bubble is never appended to
      // chatHistoryRef and so never re-enters the next Generation's Context.
      const turnActions = buildTurnActions(turn, detail);
      out.push({
        ...emptyMessage("assistant", "", `${turn.turn_id}-assistant`),
        isFinal: true,
        isError: true,
        content: knownMessageText(uiLanguage, turn.failure_reason_code, ""),
        turnActions,
      });
    } else {
      // A turn without a completed assistant message (cancelled/interrupted
      // before any content) still needs somewhere to host retry/regenerate actions.
      const turnActions = buildTurnActions(turn, detail);
      if (turnActions.length > 0) {
        const last = out.at(-1);
        if (last !== undefined) {
          last.turnActions = turnActions;
        }
      }
    }
  }
  return out;
}

export type { TranslationKey };
