import { translate } from "../../i18n/translations";
import type { PersistentConversationSummary, UiLanguage } from "../../types";
import ChatListItem, { type ChatListAction } from "./ChatListItem";

interface ChatListProps {
  language: UiLanguage;
  conversations: PersistentConversationSummary[];
  selectedConversationId: string | null;
  onSelect: (conversationId: string) => void;
  onAction: (conversationId: string, action: ChatListAction) => void;
  onRename: (conversationId: string, title: string) => void;
}

export default function ChatList({
  language,
  conversations,
  selectedConversationId,
  onSelect,
  onAction,
  onRename,
}: ChatListProps) {
  return (
    <nav className="chat-list" role="list" aria-label={translate(language, "persistentTitle")}>
      {conversations.map((item) => (
        <ChatListItem
          key={item.conversation_id}
          language={language}
          item={item}
          selected={item.conversation_id === selectedConversationId}
          onSelect={onSelect}
          onAction={onAction}
          onRename={onRename}
        />
      ))}
    </nav>
  );
}
