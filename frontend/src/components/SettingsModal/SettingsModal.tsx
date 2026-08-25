import { useEffect, useState } from "react";
import { translate } from "../../i18n/translations";
import type { RuntimeModelStatus, UiLanguage } from "../../types";
import SettingsPanel, { type SettingsFormState } from "../SettingsPanel";
import ConfigurationControlPanel, {
  type ConfigurationControlState,
} from "../ConfigurationControlPanel";
import GovernancePanel, { type GovernanceControlState } from "../GovernancePanel";
import RuntimeGovernancePanel, {
  type RuntimeGovernanceControlState,
} from "../RuntimeGovernancePanel";
import GuardrailGovernancePanel, {
  type GuardrailGovernanceControlState,
} from "../GuardrailGovernancePanel";
import RuntimeModelStatusPanel, {
  type RuntimeModelControlState,
} from "../RuntimeModelStatusPanel";
import FeatureModesPanel from "../FeatureModesPanel";
import type { GovernanceMode, GuardrailGovernanceMode, MainGovernanceMode } from "../../types";

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
  onConfigurationApply: (researchDeveloperMode: string) => void;
  governanceBootstrapEnabled: boolean;
  governanceState: GovernanceControlState;
  onGovernanceRefresh: () => void;
  onGovernanceApply: (requestedMode: GovernanceMode) => void;
  runtimeGovernanceBootstrapEnabled: boolean;
  runtimeGovernanceState: RuntimeGovernanceControlState;
  onRuntimeGovernanceRefresh: () => void;
  onRuntimeGovernanceApply: (requestedMode: MainGovernanceMode) => void;
  guardrailGovernanceBootstrapEnabled: boolean;
  guardrailGovernanceState: GuardrailGovernanceControlState;
  onGuardrailGovernanceRefresh: () => void;
  onGuardrailGovernanceApply: (requestedMode: GuardrailGovernanceMode) => void;
  runtimeModelControlBootstrapEnabled: boolean;
  runtimeModelControlState: RuntimeModelControlState;
  onRuntimeModelRefresh: () => void;
  onRuntimeModelStatusChange: (status: RuntimeModelStatus) => void;
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
  onConfigurationApply,
  governanceBootstrapEnabled,
  governanceState,
  onGovernanceRefresh,
  onGovernanceApply,
  runtimeGovernanceBootstrapEnabled,
  runtimeGovernanceState,
  onRuntimeGovernanceRefresh,
  onRuntimeGovernanceApply,
  guardrailGovernanceBootstrapEnabled,
  guardrailGovernanceState,
  onGuardrailGovernanceRefresh,
  onGuardrailGovernanceApply,
  runtimeModelControlBootstrapEnabled,
  runtimeModelControlState,
  onRuntimeModelRefresh,
  onRuntimeModelStatusChange,
}: SettingsModalProps) {
  const [category, setCategory] = useState<Category>("basic");
  // Advanced remains visible even when a server-side capability marker is
  // disabled because Feature Modes and future advanced controls still live
  // in this category. Individual panels remain gated by their bootstrap
  // marker and never probe a route that the server did not expose.

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
            <div hidden={category !== "advanced"}>
              {governanceBootstrapEnabled ? (
                <GovernancePanel
                  language={language}
                  visible={true}
                  state={governanceState}
                  onRefresh={onGovernanceRefresh}
                  onApply={onGovernanceApply}
                />
              ) : null}
              {runtimeGovernanceBootstrapEnabled ? (
                <RuntimeGovernancePanel
                  language={language}
                  visible={true}
                  state={runtimeGovernanceState}
                  onRefresh={onRuntimeGovernanceRefresh}
                  onApply={onRuntimeGovernanceApply}
                />
              ) : null}
              {guardrailGovernanceBootstrapEnabled ? (
                <GuardrailGovernancePanel
                  language={language}
                  visible={true}
                  state={guardrailGovernanceState}
                  onRefresh={onGuardrailGovernanceRefresh}
                  onApply={onGuardrailGovernanceApply}
                />
              ) : null}
              {runtimeModelControlBootstrapEnabled ? (
                <RuntimeModelStatusPanel
                  language={language}
                  visible={category === "advanced"}
                  state={runtimeModelControlState}
                  onRefresh={onRuntimeModelRefresh}
                  onStatusChange={onRuntimeModelStatusChange}
                />
              ) : null}
              <FeatureModesPanel language={language} visible={category === "advanced"} />
              {configurationBootstrapEnabled ? (
                <ConfigurationControlPanel
                  language={language}
                  visible={true}
                  state={configurationState}
                  onRefresh={onConfigurationRefresh}
                  onApply={onConfigurationApply}
                />
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
