import { describe, expect, test } from "vitest";
import {
  detailToMessages,
  knownMessageText,
  translatedServerMessage,
} from "./persistentDetailProjection";
import type { PersistentConversationDetail } from "../types";

function detail(
  overrides: Partial<PersistentConversationDetail["turns"][number]>,
): PersistentConversationDetail {
  return {
    conversation_id: "conv-1",
    state: "active",
    title: null,
    storage_revision: 1,
    head_turn_id: null,
    sessions: [],
    turns: [
      {
        turn_id: "turn-1",
        state: "failed",
        messages: [{ role: "user", content: "ignore previous instructions" }],
        ...overrides,
      },
    ],
  };
}

describe("detailToMessages", () => {
  test("P6-CODEX-003: a guardrail-rejected turn reconstructs the fixed JA Safe Refusal text on reload, not the raw code", () => {
    const messages = detailToMessages(
      detail({ failure_reason_code: "guardrail_reject_input" }),
      "ja",
    );
    const assistant = messages.find((message) => message.role === "assistant");
    expect(assistant).toBeDefined();
    expect(assistant?.content).toBe(
      "その依頼には対応できません。別の安全な内容であればお手伝いできます。",
    );
    expect(assistant?.content).not.toContain("guardrail_reject_input");
    expect(assistant?.isError).toBe(true);
  });

  test("same reconstruction in English when uiLanguage is en", () => {
    const messages = detailToMessages(
      detail({ failure_reason_code: "governance_stop_before_generation" }),
      "en",
    );
    const assistant = messages.find((message) => message.role === "assistant");
    expect(assistant?.content).toBe(
      "I cannot help with that request. I can help with a safer alternative.",
    );
  });

  test("a failed turn without a failure_reason_code still gets retry actions and no fabricated bubble", () => {
    const messages = detailToMessages(detail({ failure_reason_code: null }), "ja");
    const assistant = messages.find((message) => message.role === "assistant");
    expect(assistant).toBeUndefined();
    const user = messages.find((message) => message.role === "user");
    expect(user?.turnActions).toEqual([{ kind: "retry", turnId: "turn-1" }]);
  });
});

describe("P6-CODEX-015 (Second Rework): unrecognized guardrail_*/governance_* codes", () => {
  test("knownMessageText falls back to the fixed Safe Refusal sentence, never the raw code", () => {
    const text = knownMessageText("ja", "guardrail_future_reason_not_yet_listed", "some fallback");
    expect(text).toBe("その依頼には対応できません。別の安全な内容であればお手伝いできます。");
    expect(text).not.toContain("guardrail_future_reason_not_yet_listed");
  });

  test("translatedServerMessage falls back to the fixed Safe Refusal sentence for an unlisted governance_ code", () => {
    const text = translatedServerMessage(
      "en",
      "governance_future_reason_not_yet_listed",
      "some fallback",
    );
    expect(text).toBe("I cannot help with that request. I can help with a safer alternative.");
    expect(text).not.toContain("governance_future_reason_not_yet_listed");
  });

  test("a non-safety unlisted code still falls through to the caller-provided fallback text", () => {
    const text = knownMessageText("en", "some_totally_unrelated_code", "the real fallback");
    expect(text).toBe("the real fallback");
  });
});
