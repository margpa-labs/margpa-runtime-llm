import { useEffect, useRef, useState } from "react";
import { translate } from "../../i18n/translations";
import type { PersistentConversationSummary, UiLanguage } from "../../types";

export type ChatListAction = "resume" | "archive" | "unarchive" | "delete";

interface ChatListItemProps {
  language: UiLanguage;
  item: PersistentConversationSummary;
  selected: boolean;
  onSelect: (conversationId: string) => void;
  onAction: (conversationId: string, action: ChatListAction) => void;
  onRename: (conversationId: string, title: string) => void;
}

export default function ChatListItem({
  language,
  item,
  selected,
  onSelect,
  onAction,
  onRename,
}: ChatListItemProps) {
  const label =
    item.title ?? `${new Date(item.updated_at).toLocaleString()} · ${item.conversation_id.slice(0, 10)}`;
  const textRef = useRef<HTMLSpanElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [draftTitle, setDraftTitle] = useState(label);

  useEffect(() => {
    const node = textRef.current;
    if (node === null) {
      return;
    }
    const distance = Math.max(0, node.scrollWidth - node.clientWidth);
    node.style.setProperty("--marquee-distance", `${distance.toString()}px`);
  }, [label]);

  useEffect(() => {
    if (renaming) {
      renameInputRef.current?.focus();
      renameInputRef.current?.select();
    }
  }, [renaming]);

  function startRename(): void {
    setDraftTitle(item.title ?? "");
    setRenaming(true);
  }

  function commitRename(): void {
    setRenaming(false);
    const trimmed = draftTitle.trim();
    if (trimmed === (item.title ?? "")) {
      return;
    }
    onRename(item.conversation_id, trimmed);
  }

  function requestDelete(): void {
    if (window.confirm(translate(language, "persistentDeleteConfirm"))) {
      onAction(item.conversation_id, "delete");
    }
  }

  useEffect(() => {
    if (!menuOpen) {
      return;
    }
    const handleOutsideClick = (event: MouseEvent): void => {
      if (menuRef.current !== null && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [menuOpen]);

  const archiveActionKey = item.state === "archived" ? "persistentUnarchive" : "persistentArchive";
  const archiveAction: ChatListAction = item.state === "archived" ? "unarchive" : "archive";

  return (
    <div className="chat-list-item" role="listitem" data-selected={selected}>
      {renaming ? (
        <input
          ref={renameInputRef}
          type="text"
          className="chat-list-item-rename-input"
          value={draftTitle}
          onChange={(event) => {
            setDraftTitle(event.target.value);
          }}
          onBlur={commitRename}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              commitRename();
            } else if (event.key === "Escape") {
              event.preventDefault();
              setRenaming(false);
            }
          }}
        />
      ) : (
        <button
          type="button"
          className="chat-list-item-button"
          aria-current={selected}
          onClick={() => {
            onSelect(item.conversation_id);
          }}
        >
          <span className="chat-list-item-name">
            <span ref={textRef} className="chat-list-item-name-text">
              {label}
            </span>
          </span>
        </button>
      )}
      <div className="chat-list-item-option" ref={menuRef}>
        <button
          type="button"
          className="chat-list-item-option-button"
          aria-label={translate(language, "chatOptionsLabel")}
          aria-expanded={menuOpen}
          onClick={() => {
            setMenuOpen((previous) => !previous);
          }}
        >
          ⋮
        </button>
        {menuOpen ? (
          <div className="chat-list-item-menu" role="menu">
            {item.state === "active" && !item.has_active_session ? (
              <button
                type="button"
                role="menuitem"
                onClick={() => {
                  setMenuOpen(false);
                  onAction(item.conversation_id, "resume");
                }}
              >
                {translate(language, "persistentResume")}
              </button>
            ) : null}
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setMenuOpen(false);
                onAction(item.conversation_id, archiveAction);
              }}
            >
              {translate(language, archiveActionKey)}
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setMenuOpen(false);
                startRename();
              }}
            >
              {translate(language, "persistentRename")}
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setMenuOpen(false);
                requestDelete();
              }}
            >
              {translate(language, "persistentDelete")}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
