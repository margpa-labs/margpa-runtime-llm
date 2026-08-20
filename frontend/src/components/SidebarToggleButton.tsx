import { translate } from "../i18n/translations";
import type { UiLanguage } from "../types";

interface SidebarToggleButtonProps {
  language: UiLanguage;
  visible: boolean;
  onToggle: () => void;
}

// Rendered outside both the sidebar and main content, at a fixed screen
// position, so it stays in the exact same spot whether the sidebar is
// shown or hidden — matching the ChatGPT pattern the user pointed to
// (screenshots of its sidebar-open and sidebar-closed states) rather than
// a button that scrolls away with either panel.
export default function SidebarToggleButton({ language, visible, onToggle }: SidebarToggleButtonProps) {
  const label = translate(language, visible ? "sidebarToggleHide" : "sidebarToggleShow");
  return (
    <div className="sidebar-toggle-wrap">
      <button id="sidebar-toggle" type="button" className="sidebar-toggle-button" aria-pressed={visible} aria-label={label} onClick={onToggle}>
        <svg viewBox="0 0 20 20" width="20" height="20" fill="none" aria-hidden="true">
          <rect x="2.5" y="3.5" width="15" height="13" rx="2.5" stroke="currentColor" strokeWidth="1.4" />
          <line x1="7.5" y1="3.5" x2="7.5" y2="16.5" stroke="currentColor" strokeWidth="1.4" />
        </svg>
      </button>
      <span className="sidebar-toggle-tooltip" role="tooltip">
        {label}
      </span>
    </div>
  );
}
