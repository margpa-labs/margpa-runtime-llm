import { translate } from "../../i18n/translations";
import type { UiLanguage } from "../../types";

interface AccountFooterProps {
  language: UiLanguage;
  onOpenSettings: () => void;
}

// A single generic "Account" entry for now. Structured as its own
// component/button (rather than folded into SidebarHeader) so a future
// multi-user identity (name, avatar, switcher) has an obvious place to grow
// into without reshaping the rest of the sidebar.
export default function AccountFooter({ language, onOpenSettings }: AccountFooterProps) {
  return (
    <button id="account-footer" type="button" className="sidebar-account-footer" onClick={onOpenSettings}>
      {translate(language, "accountLabel")}
    </button>
  );
}
