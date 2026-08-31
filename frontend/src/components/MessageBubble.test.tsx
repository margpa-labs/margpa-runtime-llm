import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import MessageBubble from "./MessageBubble";
import type { DisplayMessage } from "../types";

function assistantMessage(overrides: Partial<DisplayMessage> = {}): DisplayMessage {
  return {
    id: "assistant-1",
    role: "assistant",
    content: "hello",
    isFinal: true,
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
    ...overrides,
  };
}

describe("MessageBubble action row", () => {
  test("Copy, Regenerate, and branch-select share one row, same size, right-aligned in that order", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({
          turnActions: [
            { kind: "selectBranch", turnId: "turn-1" },
            { kind: "regenerate", turnId: "turn-1" },
          ],
        })}
        onTurnAction={vi.fn()}
        // P8-B (P8-REQ-009): Branch defaults to hidden — this Test
        // specifically covers the Branch button's own rendering/ordering,
        // so it opts back in explicitly.
        branchUiVisible={true}
      />,
    );

    const row = document.querySelector(".message-actions");
    expect(row).not.toBeNull();
    if (row === null) throw new Error("expected .message-actions row");

    const buttons = within(row as HTMLElement).getAllByRole("button");
    expect(buttons.map((button) => button.textContent)).toEqual([
      "Select this branch",
      "Regenerate",
      "Copy",
    ]);
    // All three must be visually identical in size — enforced by construction
    // (same classes), asserted here so a future edit can't silently diverge.
    for (const button of buttons) {
      expect(button.className).toBe("message-copy secondary");
    }
  });

  test("P8-B (P8-REQ-009): branch-select is hidden by default even though the turn action data still carries it", () => {
    const message = assistantMessage({
      turnActions: [
        { kind: "selectBranch", turnId: "turn-1" },
        { kind: "regenerate", turnId: "turn-1" },
      ],
    });
    render(<MessageBubble language="en" message={message} onTurnAction={vi.fn()} />);

    expect(screen.queryByText("Select this branch")).toBeNull();
    expect(screen.getByText("Regenerate")).toBeInTheDocument();
    // The Data itself (P8-REQ-009's "Branch Data/API保持") is never mutated —
    // only the rendered Buttons are filtered.
    expect(message.turnActions).toHaveLength(2);
    expect(message.turnActions[0]?.kind).toBe("selectBranch");
  });

  test("a turn with no actions and no copy (non-final assistant message) renders no action row at all", () => {
    render(<MessageBubble language="en" message={assistantMessage({ isFinal: false })} onTurnAction={vi.fn()} />);
    expect(document.querySelector(".message-actions")).toBeNull();
  });

  test("clicking Regenerate calls onTurnAction with the turn id and kind", () => {
    const onTurnAction = vi.fn();
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ turnActions: [{ kind: "regenerate", turnId: "turn-9" }] })}
        onTurnAction={onTurnAction}
      />,
    );
    screen.getByRole("button", { name: "Regenerate" }).click();
    expect(onTurnAction).toHaveBeenCalledWith("turn-9", "regenerate");
  });
});

describe("MessageBubble markdown rendering while streaming", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders markdown progressively even before the turn is final", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ content: "**bold**", isFinal: false })}
      />,
    );
    const strong = document.querySelector(".message-content strong");
    expect(strong).not.toBeNull();
    expect(strong?.textContent).toBe("bold");
  });

  test("a transiently unparsable mid-stream tail (e.g. an open code fence) falls back to plain text silently, with no failure note", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ content: "```js\nstill typing", isFinal: false })}
      />,
    );
    expect(document.querySelector(".message-content")?.textContent).toBe("```js\nstill typing");
    expect(screen.queryByText(/Markdown rendering failed/u)).toBeNull();
  });

  test("the same unparsable content, once final, falls back to plain text WITH the failure note", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ content: "```js\nstill typing", isFinal: true })}
      />,
    );
    expect(document.querySelector(".message-content")?.textContent).toBe("```js\nstill typing");
    expect(screen.queryByText(/Markdown rendering failed/u)).not.toBeNull();
  });

  test("a message whose content contains a Markdown table gets the wider message-wide class", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({
          content: "| A | B |\n|---|---|\n| a | b |",
          isFinal: true,
        })}
      />,
    );
    expect(document.querySelector(".message")?.className).toContain("message-wide");
  });

  test("an ordinary text message does not get the message-wide class", () => {
    render(<MessageBubble language="en" message={assistantMessage({ content: "just text", isFinal: true })} />);
    expect(document.querySelector(".message")?.className).not.toContain("message-wide");
  });

  test("Copy always sends the raw markdown source, never the rendered output", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    render(<MessageBubble language="en" message={assistantMessage({ content: "**bold**", isFinal: true })} />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Copy" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenCalledWith("**bold**");
  });
});

describe("MessageBubble live Judge/Repair badge (P6-CODEX-024)", () => {
  test("no badge at all when judgeBadge is null", () => {
    render(<MessageBubble language="en" message={assistantMessage()} judgeBadge={null} />);
    expect(document.querySelector(".message-judge-badge")).toBeNull();
  });

  test("a running Judge Run shows a generic reviewing badge", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ requestId: "req-1" })}
        judgeBadge={{ requestId: "req-1", state: "judging", repairAccepted: null }}
      />,
    );
    expect(screen.getByText("Reviewing…")).not.toBeNull();
  });

  test("a completed Judge Run with an accepted Repair shows the improved badge", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ requestId: "req-1" })}
        judgeBadge={{ requestId: "req-1", state: "completed", repairAccepted: true }}
      />,
    );
    expect(screen.getByText("Answer improved")).not.toBeNull();
  });

  test("a completed Judge Run without an accepted Repair shows no badge", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ requestId: "req-1" })}
        judgeBadge={{ requestId: "req-1", state: "completed", repairAccepted: null }}
      />,
    );
    expect(document.querySelector(".message-judge-badge")).toBeNull();
  });

  test("a degraded Judge Run shows the degraded badge", () => {
    render(
      <MessageBubble
        language="en"
        message={assistantMessage({ requestId: "req-1" })}
        judgeBadge={{ requestId: "req-1", state: "degraded", repairAccepted: null }}
      />,
    );
    expect(screen.getByText("Part of the review process had a problem")).not.toBeNull();
  });

  test("idle/queued_or_skipped/failed/cancelled show no badge (curated, disclosed scope)", () => {
    for (const state of ["idle", "queued_or_skipped", "failed", "cancelled"]) {
      const { unmount } = render(
        <MessageBubble
          language="en"
          message={assistantMessage({ requestId: "req-1" })}
          judgeBadge={{ requestId: "req-1", state, repairAccepted: null }}
        />,
      );
      expect(document.querySelector(".message-judge-badge")).toBeNull();
      unmount();
    }
  });
});
