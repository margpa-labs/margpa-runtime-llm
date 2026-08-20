import { translate, type TranslationKey } from "../../i18n/translations";
import type { UiLanguage } from "../../types";

interface SidebarHeaderProps {
  language: UiLanguage;
  runtimeStatus: { kind: "loading" | "metadata" | "known_error"; text: string | null };
}

export default function SidebarHeader({ language, runtimeStatus }: SidebarHeaderProps) {
  const t = (key: TranslationKey): string => translate(language, key);

  let modelLine: string;
  let profileLine: string | null;
  if (runtimeStatus.kind === "metadata" && runtimeStatus.text !== null) {
    const parts = runtimeStatus.text.split(" · ");
    modelLine = parts[0] ?? "";
    profileLine = parts.slice(1).join(" · ") || null;
  } else {
    modelLine = t(runtimeStatus.kind === "loading" ? "runtimeLoading" : "runtimeLoadFailed");
    profileLine = null;
  }

  return (
    <div className="sidebar-header">
      <div className="sidebar-title-block">
        <p className="eyebrow">Nazuna Research Governance LLM</p>
        <h1>MARGPA Runtime LLM</h1>
        <p id="runtime-status" className="runtime-status">
          {modelLine}
        </p>
        {profileLine !== null ? <p className="runtime-status">{profileLine}</p> : null}
      </div>
      <div className="sidebar-preview-note" aria-label={t("previewLabel")}>
        <p>{t("previewNoteLine1")}</p>
        <p>{t("previewNoteLine2")}</p>
        <p>{t("previewNoteLine3")}</p>
      </div>
    </div>
  );
}
