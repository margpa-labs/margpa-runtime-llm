import { render } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import MessageList from "./MessageList";
import type { DisplayMessage } from "../types";

function message(overrides: Partial<DisplayMessage> = {}): DisplayMessage {
  return {
    id: "msg-1",
    role: "user",
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

function findSentinel(root: HTMLElement): HTMLElement {
  return root.querySelector(".messages > div:not([class])") as HTMLElement;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("MessageList", () => {
  test("with no pinned message, scrolls the trailing sentinel into view", () => {
    const spy = vi.spyOn(Element.prototype, "scrollIntoView");
    render(
      <MessageList
        language="en"
        messages={[message({ id: "conv-1-turn-user" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId={null}
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(spy).toHaveBeenCalledWith({ block: "end" });
  });

  test("once generation stops and .main-content isn't found, nothing happens", () => {
    const spy = vi.spyOn(Element.prototype, "scrollIntoView");
    render(
      <MessageList
        language="en"
        messages={[
          message({ id: "conv-1-turn-user", role: "user" }),
          message({ id: "conv-1-turn-assistant", role: "assistant", isFinal: true }),
        ]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(spy).not.toHaveBeenCalled();
  });

  test("while actively pinning, renders the gap-filler that guarantees scrollable range", () => {
    const { container } = render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(container.querySelector(".messages-gap-filler")).not.toBeNull();
  });

  test("the gap-filler survives generation stopping (only pinnedMessageId clearing removes it)", () => {
    const { container, rerender } = render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(container.querySelector(".messages-gap-filler")).not.toBeNull();

    // Generation stopping alone (active -> false) must NOT remove it: doing
    // so would shrink .main-content back down and let the browser auto-clamp
    // scrollTop toward 0, undoing the pin right as it was meant to settle.
    rerender(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(container.querySelector(".messages-gap-filler")).not.toBeNull();

    // Only clearing pinnedMessageId itself (next send, conversation switch,
    // new chat, retry/regenerate) removes it.
    rerender(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId={null}
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );
    expect(container.querySelector(".messages-gap-filler")).toBeNull();
  });

  test("while pinning, with the reply not yet reaching the composer, scrolls to a fixed gap below the top", () => {
    const main = document.createElement("main");
    main.className = "main-content";
    main.getBoundingClientRect = () => ({ top: 0, bottom: 700 }) as DOMRect;
    document.body.appendChild(main);
    const composer = document.createElement("div");
    composer.className = "composer";
    composer.getBoundingClientRect = () => ({ top: 650 }) as DOMRect;
    document.body.appendChild(composer);
    const mountPoint = main.appendChild(document.createElement("div"));

    const { rerender } = render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user", content: "question" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
      { container: mountPoint },
    );
    document.getElementById("msg-1")!.getBoundingClientRect = () => ({ top: 200 }) as DOMRect;
    findSentinel(mountPoint).getBoundingClientRect = () => ({ bottom: 300 }) as DOMRect; // well clear of the composer

    rerender(
      <MessageList
        language="en"
        messages={[
          message({ id: "msg-1", role: "user", content: "question" }),
          message({ id: "msg-2", role: "assistant", content: "short reply", isFinal: false }),
        ]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );

    // 0 (initial scrollTop) + (200 - 0) - 76 top gap = 124; no composer
    // overflow correction on top of that.
    expect(main.scrollTop).toBe(124);
    document.body.removeChild(main);
    document.body.removeChild(composer);
  });

  test("while pinning, once the growing reply reaches the composer, scrolls further to keep its tail clear", () => {
    const main = document.createElement("main");
    main.className = "main-content";
    main.getBoundingClientRect = () => ({ top: 0, bottom: 700 }) as DOMRect;
    document.body.appendChild(main);
    const composer = document.createElement("div");
    composer.className = "composer";
    composer.getBoundingClientRect = () => ({ top: 650 }) as DOMRect;
    document.body.appendChild(composer);
    const mountPoint = main.appendChild(document.createElement("div"));

    const { rerender } = render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user", content: "question" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
      { container: mountPoint },
    );
    document.getElementById("msg-1")!.getBoundingClientRect = () => ({ top: 200 }) as DOMRect;
    // Tail sits 60px past where it should stop (650 - 16 gap = 634 target).
    findSentinel(mountPoint).getBoundingClientRect = () => ({ bottom: 694 }) as DOMRect;

    rerender(
      <MessageList
        language="en"
        messages={[
          message({ id: "msg-1", role: "user", content: "question" }),
          message({ id: "msg-2", role: "assistant", content: "a much longer reply", isFinal: false }),
        ]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={true}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );

    // Pin target (124) plus the 60px needed to clear the composer.
    expect(main.scrollTop).toBe(124 + 60);
    document.body.removeChild(main);
    document.body.removeChild(composer);
  });

  test("once generation stops, a tail left behind the composer is still pulled clear (no re-anchoring to the top)", () => {
    const main = document.createElement("main");
    main.className = "main-content";
    main.getBoundingClientRect = () => ({ top: 0, bottom: 700 }) as DOMRect;
    document.body.appendChild(main);
    const composer = document.createElement("div");
    composer.className = "composer";
    composer.getBoundingClientRect = () => ({ top: 650 }) as DOMRect;
    document.body.appendChild(composer);
    const mountPoint = main.appendChild(document.createElement("div"));

    const { rerender } = render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "user", content: "question" })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
      { container: mountPoint },
    );
    main.scrollTop = 124;
    findSentinel(mountPoint).getBoundingClientRect = () => ({ bottom: 694 }) as DOMRect;

    rerender(
      <MessageList
        language="en"
        messages={[
          message({ id: "msg-1", role: "user", content: "question" }),
          message({ id: "msg-2", role: "assistant", content: "final rendered reply", isFinal: true }),
        ]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId="msg-1"
        active={false}
        liveJudgeBadge={null}
        branchUiVisible={false}
      />,
    );

    // Not pinning, so no re-anchoring to the top gap — but still pulled down
    // by exactly the composer-overflow amount from wherever it already was.
    expect(main.scrollTop).toBe(124 + 60);
    document.body.removeChild(main);
    document.body.removeChild(composer);
  });
});

describe("MessageList Live Judge badge correlation (P6-CODEX-024)", () => {
  test("only the message whose requestId matches the badge's requestId receives it", () => {
    render(
      <MessageList
        language="en"
        messages={[
          message({ id: "msg-1", role: "assistant", content: "turn one", requestId: "req-1" }),
          message({ id: "msg-2", role: "assistant", content: "turn two", requestId: "req-2" }),
        ]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId={null}
        active={false}
        liveJudgeBadge={{ requestId: "req-2", state: "judging", repairAccepted: null }}
        branchUiVisible={false}
      />,
    );

    expect(document.getElementById("msg-1-judge-badge")).toBeNull();
    expect(document.getElementById("msg-2-judge-badge")).not.toBeNull();
  });

  test("a message with a null requestId never receives the badge, even if the badge's requestId is null-ish", () => {
    render(
      <MessageList
        language="en"
        messages={[message({ id: "msg-1", role: "assistant", content: "reloaded turn", requestId: null })]}
        emptyTitleKey="persistentEmptyTitle"
        emptyNoteKey="persistentEmptyNote"
        onTurnAction={vi.fn()}
        pinnedMessageId={null}
        active={false}
        liveJudgeBadge={{ requestId: "req-1", state: "judging", repairAccepted: null }}
        branchUiVisible={false}
      />,
    );

    expect(document.getElementById("msg-1-judge-badge")).toBeNull();
  });
});
