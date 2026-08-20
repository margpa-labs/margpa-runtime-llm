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
    turnActions: [],
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
