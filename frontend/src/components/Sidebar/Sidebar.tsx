import { translate } from "../../i18n/translations";
import type { PersistentConversationSummary, UiLanguage } from "../../types";
import SidebarHeader from "./SidebarHeader";
import ChatList from "./ChatList";
import AccountFooter from "./AccountFooter";
import type { ChatListAction } from "./ChatListItem";

interface SidebarProps {
  language: UiLanguage;
  visible: boolean;
  runtimeStatus: { kind: "loading" | "metadata" | "known_error"; text: string | null };
  conversations: PersistentConversationSummary[];
  selectedConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onConversationAction: (conversationId: string, action: ChatListAction) => void;
  onConversationRename: (conversationId: string, title: string) => void;
  onNewChat: () => void;
  newChatDisabled: boolean;
  onOpenSettings: () => void;
}

export default function Sidebar({
  language,
  visible,
  runtimeStatus,
  conversations,
  selectedConversationId,
  onSelectConversation,
  onConversationAction,
  onConversationRename,
  onNewChat,
  newChatDisabled,
  onOpenSettings,
}: SidebarProps) {
  return (
    <aside id="sidebar" className="sidebar" data-visible={visible} aria-hidden={!visible}>
      <SidebarHeader language={language} runtimeStatus={runtimeStatus} />
      <hr className="sidebar-divider" />
      <button
        id="new-chat"
        className="sidebar-new-chat"
        type="button"
        disabled={newChatDisabled}
        onClick={onNewChat}
      >
        {translate(language, "newChat")}
      </button>
      <hr className="sidebar-divider" />
      <ChatList
        language={language}
        conversations={conversations}
        selectedConversationId={selectedConversationId}
        onSelect={onSelectConversation}
        onAction={onConversationAction}
        onRename={onConversationRename}
      />
      <hr className="sidebar-divider" />
      <AccountFooter language={language} onOpenSettings={onOpenSettings} />
    </aside>
  );
}
