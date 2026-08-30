import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import ChatListItem from "./ChatListItem";
import type { PersistentConversationSummary } from "../../types";

function item(overrides: Partial<PersistentConversationSummary> = {}): PersistentConversationSummary {
  return {
    conversation_id: "conversation-abcdef0123",
    updated_at: "2024-01-01T00:00:00Z",
    state: "active",
    title: null,
    has_active_session: false,
    ...overrides,
  };
}

describe("ChatListItem", () => {
  test("clicking the row selects the conversation", () => {
    const onSelect = vi.fn();
    render(
      <ChatListItem
        language="en"
        item={item()}
        selected={false}
        onSelect={onSelect}
        onAction={vi.fn()}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /conversati/ }));
    expect(onSelect).toHaveBeenCalledWith("conversation-abcdef0123");
  });

  test("a custom title is shown instead of the auto-generated label", () => {
    render(
      <ChatListItem
        language="en"
        item={item({ title: "My renamed chat" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={vi.fn()}
        onRename={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "My renamed chat" })).toBeInTheDocument();
  });

  test("an active conversation's menu offers Archive, Rename, and Delete", () => {
    render(
      <ChatListItem
        language="en"
        item={item({ state: "active" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={vi.fn()}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    expect(screen.getByRole("menuitem", { name: "Archive" })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Rename" })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Delete" })).toBeInTheDocument();
  });

  test("an archived conversation's menu offers only Unarchive", () => {
    render(
      <ChatListItem
        language="en"
        item={item({ state: "archived" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={vi.fn()}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    expect(screen.getByRole("menuitem", { name: "Unarchive" })).toBeInTheDocument();
  });

  test("choosing a menu action calls onAction with the conversation id and closes the menu", () => {
    const onAction = vi.fn();
    render(
      <ChatListItem
        language="en"
        item={item({ state: "active" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={onAction}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Archive" }));
    expect(onAction).toHaveBeenCalledWith("conversation-abcdef0123", "archive");
    expect(screen.queryByRole("menuitem", { name: "Archive" })).toBeNull();
  });

  test("clicking outside the open menu closes it without triggering an action", () => {
    const onAction = vi.fn();
    render(
      <div>
        <ChatListItem
          language="en"
          item={item({ state: "active" })}
          selected={false}
          onSelect={vi.fn()}
          onAction={onAction}
          onRename={vi.fn()}
        />
        <button type="button">outside</button>
      </div>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    expect(screen.getByRole("menuitem", { name: "Archive" })).toBeInTheDocument();
    fireEvent.mouseDown(screen.getByRole("button", { name: "outside" }));
    expect(screen.queryByRole("menuitem", { name: "Archive" })).toBeNull();
    expect(onAction).not.toHaveBeenCalled();
  });

  test("choosing Rename swaps the row for an editable input seeded with the current title", () => {
    const onRename = vi.fn();
    render(
      <ChatListItem
        language="en"
        item={item({ title: "Old title" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={vi.fn()}
        onRename={onRename}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Rename" }));
    const input = screen.getByDisplayValue("Old title");
    fireEvent.change(input, { target: { value: "New title" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onRename).toHaveBeenCalledWith("conversation-abcdef0123", "New title");
  });

  test("pressing Escape while renaming cancels without calling onRename", () => {
    const onRename = vi.fn();
    render(
      <ChatListItem
        language="en"
        item={item({ title: "Old title" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={vi.fn()}
        onRename={onRename}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Rename" }));
    const input = screen.getByDisplayValue("Old title");
    fireEvent.change(input, { target: { value: "Discarded" } });
    fireEvent.keyDown(input, { key: "Escape" });
    expect(screen.queryByDisplayValue("Discarded")).toBeNull();
    expect(screen.getByRole("button", { name: "Old title" })).toBeInTheDocument();
    expect(onRename).not.toHaveBeenCalled();
  });

  test("choosing Delete confirms before calling onAction with delete", () => {
    const onAction = vi.fn();
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
    render(
      <ChatListItem
        language="en"
        item={item({ state: "active" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={onAction}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete" }));
    expect(confirmSpy).toHaveBeenCalled();
    expect(onAction).toHaveBeenCalledWith("conversation-abcdef0123", "delete");
    vi.restoreAllMocks();
  });

  test("declining the Delete confirmation does not call onAction", () => {
    const onAction = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    render(
      <ChatListItem
        language="en"
        item={item({ state: "active" })}
        selected={false}
        onSelect={vi.fn()}
        onAction={onAction}
        onRename={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Chat options" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Delete" }));
    expect(onAction).not.toHaveBeenCalled();
    vi.restoreAllMocks();
  });
});
