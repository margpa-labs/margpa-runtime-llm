import { useEffect, useState } from "react";
import { translate } from "../../i18n/translations";
import type { UiLanguage } from "../../types";
import SettingsPanel, { type SettingsFormState } from "../SettingsPanel";
import ConfigurationControlPanel, {
  type ConfigurationControlState,
} from "../ConfigurationControlPanel";

interface SettingsModalProps {
  language: UiLanguage;
  open: boolean;
  onClose: () => void;
  settingsForm: SettingsFormState;
  onSettingsChange: (next: SettingsFormState) => void;
  thinkingControlAvailable: boolean;
  active: boolean;
  documentationRagControlAvailable: boolean;
  documentationRagDenied: boolean;
  documentationRagNoteText: string;
  configurationBootstrapEnabled: boolean;
  configurationState: ConfigurationControlState;
  onConfigurationRefresh: () => void;
  onConfigurationPreview: (patch: Record<string, unknown>) => void;
  onConfigurationApply: (researchDeveloperMode: string) => void;
}

type Category = "basic" | "advanced";

// A left-nav / right-content shell, deliberately built as a small category
// list rather than a single flat panel: today it only has two entries
// (basic settings, advanced mode), but Phase 10+ is expected to add more
// categories, and this structure absorbs that without a reshape.
export default function SettingsModal({
  language,
  open,
  onClose,
  settingsForm,
  onSettingsChange,
  thinkingControlAvailable,
  active,
  documentationRagControlAvailable,
  documentationRagDenied,
  documentationRagNoteText,
  configurationBootstrapEnabled,
  configurationState,
  onConfigurationRefresh,
  onConfigurationPreview,
  onConfigurationApply,
}: SettingsModalProps) {
  const [category, setCategory] = useState<Category>("basic");

  // Reset to "basic" every time the modal opens, adjusted during render
  // (React's documented pattern for "reset state when a prop changes")
  // rather than in a useEffect — see ConfigurationControlPanel's
  // syncedRevision for the same pattern and rationale.
  const [syncedOpen, setSyncedOpen] = useState(open);
  if (open !== syncedOpen) {
    setSyncedOpen(open);
    if (open) {
      setCategory("basic");
    }
  }

  useEffect(() => {
    if (!open) {
      return;
    }
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="settings-modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="settings-modal" role="dialog" aria-modal="true" aria-label={translate(language, "settingsMenuLabel")}>
        <div className="settings-modal-header">
          <h2>{translate(language, "settingsMenuLabel")}</h2>
          <button
            type="button"
            className="secondary settings-modal-close"
            aria-label={translate(language, "closeDialog")}
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="settings-modal-body">
          <nav className="settings-modal-nav">
            <button
              type="button"
              className="secondary"
              aria-current={category === "basic"}
              onClick={() => {
                setCategory("basic");
              }}
            >
              {translate(language, "settingsMenuLabel")}
            </button>
            {configurationBootstrapEnabled ? (
              <button
                type="button"
                className="secondary"
                aria-current={category === "advanced"}
                onClick={() => {
                  setCategory("advanced");
                }}
              >
                {translate(language, "advancedModeLabel")}
              </button>
            ) : null}
          </nav>
          <div className="settings-modal-content">
            <div hidden={category !== "basic"}>
              <SettingsPanel
                language={language}
                form={settingsForm}
                onChange={onSettingsChange}
                thinkingControlAvailable={thinkingControlAvailable}
                active={active}
                documentationRagControlAvailable={documentationRagControlAvailable}
                documentationRagDenied={documentationRagDenied}
                documentationRagNoteText={documentationRagNoteText}
              />
            </div>
            {configurationBootstrapEnabled ? (
              <div hidden={category !== "advanced"}>
                <ConfigurationControlPanel
                  language={language}
                  visible={true}
                  state={configurationState}
                  onRefresh={onConfigurationRefresh}
                  onPreview={onConfigurationPreview}
                  onApply={onConfigurationApply}
                />
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
