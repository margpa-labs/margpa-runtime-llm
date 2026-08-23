import { useEffect, useState } from "react";
import { translate } from "../../i18n/translations";
import type { UiLanguage } from "../../types";
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
import RuntimeModelStatusPanel from "../RuntimeModelStatusPanel";
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
  onConfigurationPreview: (patch: Record<string, unknown>) => void;
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
}: SettingsModalProps) {
  const [category, setCategory] = useState<Category>("basic");
  // The Advanced tab is unconditionally shown: RuntimeModelStatusPanel has
  // no bootstrap flag of its own (Phase 6: always available, unlike the
  // Phase 4/5 features below which can be entirely disabled), so it alone
  // is enough to keep the tab visible even when every other Governance
  // feature is off.

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
              {configurationBootstrapEnabled ? (
                <ConfigurationControlPanel
                  language={language}
                  visible={true}
                  state={configurationState}
                  onRefresh={onConfigurationRefresh}
                  onPreview={onConfigurationPreview}
                  onApply={onConfigurationApply}
                />
              ) : null}
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
              <RuntimeModelStatusPanel language={language} visible={category === "advanced"} />
              <FeatureModesPanel language={language} visible={category === "advanced"} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
