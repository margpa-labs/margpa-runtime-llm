import { translate } from "../i18n/translations";
import type { UiLanguage, UiTheme } from "../types";

interface TopBarProps {
  language: UiLanguage;
  theme: UiTheme;
  onLanguageChange: (language: UiLanguage) => void;
  onThemeChange: (theme: UiTheme) => void;
}

export default function TopBar({ language, theme, onLanguageChange, onThemeChange }: TopBarProps) {
  return (
    <header className="topbar">
      <div className="topbar-actions">
        <div id="ui-theme-switcher" className="theme-switcher" role="group" aria-label={translate(language, "uiThemeLabel")}>
          <button
            id="ui-theme-white"
            className="theme-button"
            type="button"
            aria-pressed={theme === "white"}
            onClick={() => {
              onThemeChange("white");
            }}
          >
            White
          </button>
          <span aria-hidden="true">|</span>
          <button
            id="ui-theme-dark"
            className="theme-button"
            type="button"
            aria-pressed={theme === "dark"}
            onClick={() => {
              onThemeChange("dark");
            }}
          >
            Dark
          </button>
        </div>
        <div
          id="ui-language-switcher"
          className="language-switcher"
          role="group"
          aria-label={translate(language, "uiLanguageLabel")}
        >
          <button
            id="ui-language-ja"
            className="language-button"
            type="button"
            aria-pressed={language === "ja"}
            onClick={() => {
              onLanguageChange("ja");
            }}
          >
            日本語
          </button>
          <span aria-hidden="true">|</span>
          <button
            id="ui-language-en"
            className="language-button"
            type="button"
            aria-pressed={language === "en"}
            onClick={() => {
              onLanguageChange("en");
            }}
          >
            English
          </button>
        </div>
      </div>
    </header>
  );
}
