import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import SettingsModal from "./SettingsModal";
import type { SettingsFormState } from "../SettingsPanel";
import type { ConfigurationControlState } from "../ConfigurationControlPanel";
import type { GovernanceControlState } from "../GovernancePanel";
import type { RuntimeGovernanceControlState } from "../RuntimeGovernancePanel";
import type { GuardrailGovernanceControlState } from "../GuardrailGovernancePanel";

const SETTINGS_FORM: SettingsFormState = {
  responseLanguage: "ja",
  maxNewTokens: "2048",
  thinkingMode: false,
  thinkingVisibility: false,
  webSearchMode: "disabled",
  summaryMode: "off",
  documentationRagMode: "disabled",
  injectContextUsage: false,
  showContextUsage: false,
  expressiveMode: false,
};

const CONFIGURATION_STATE: ConfigurationControlState = {
  capability: "ready",
  snapshot: {
    schema_version: "1",
    revision: 1,
    digest_sha512: "abc123",
    fields: [{ key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" }],
    feature_hooks: [],
    recording_hooks: [],
  },
  resultText: "",
};

const GOVERNANCE_STATE: GovernanceControlState = {
  capability: "ready",
  status: {
    mode: {
      revision: 1,
      digest_sha512: "gov123",
      current_mode: "off",
      descriptors: [
        { mode: "off", availability: "available", apply_disposition: "hot", unavailable_reason_code: null },
        { mode: "observe", availability: "available", apply_disposition: "hot", unavailable_reason_code: null },
        {
          mode: "enforce",
          availability: "unavailable",
          apply_disposition: "rejected",
          unavailable_reason_code: "phase_3_enforce_unavailable",
        },
      ],
    },
    observe_summary: null,
  },
  resultText: "",
};

const RUNTIME_GOVERNANCE_STATE: RuntimeGovernanceControlState = {
  capability: "ready",
  status: {
    enabled: true,
    revision: 1,
    current_mode: "off",
    descriptors: [
      { mode: "off", availability: "available", unavailable_reason_code: null },
      { mode: "observe", availability: "available", unavailable_reason_code: null },
      { mode: "enforce", availability: "available", unavailable_reason_code: null },
    ],
    points: [],
    evidence: null,
  },
  resultText: "",
};

const GUARDRAIL_GOVERNANCE_STATE: GuardrailGovernanceControlState = {
  capability: "ready",
  status: {
    enabled: true,
    revision: 1,
    current_mode: "off",
    descriptors: [
      { mode: "off", availability: "available", unavailable_reason_code: null },
      { mode: "observe", availability: "available", unavailable_reason_code: null },
      { mode: "enforce", availability: "available", unavailable_reason_code: null },
    ],
    points: [],
  },
  resultText: "",
};

function baseProps(overrides: Partial<Parameters<typeof SettingsModal>[0]> = {}) {
  return {
    language: "en" as const,
    open: true,
    onClose: vi.fn(),
    settingsForm: SETTINGS_FORM,
    onSettingsChange: vi.fn(),
    thinkingControlAvailable: false,
    active: false,
    documentationRagControlAvailable: false,
    documentationRagDenied: false,
    documentationRagNoteText: "",
    configurationBootstrapEnabled: true,
    configurationState: CONFIGURATION_STATE,
    onConfigurationRefresh: vi.fn(),
    onConfigurationApply: vi.fn(),
    governanceBootstrapEnabled: true,
    governanceState: GOVERNANCE_STATE,
    onGovernanceRefresh: vi.fn(),
    onGovernanceApply: vi.fn(),
    runtimeGovernanceBootstrapEnabled: true,
    runtimeGovernanceState: RUNTIME_GOVERNANCE_STATE,
    onRuntimeGovernanceRefresh: vi.fn(),
    onRuntimeGovernanceApply: vi.fn(),
    guardrailGovernanceBootstrapEnabled: true,
    guardrailGovernanceState: GUARDRAIL_GOVERNANCE_STATE,
    onGuardrailGovernanceRefresh: vi.fn(),
    onGuardrailGovernanceApply: vi.fn(),
    runtimeModelControlBootstrapEnabled: true,
    runtimeModelControlState: { capability: "loading" as const, status: null },
    onRuntimeModelRefresh: vi.fn(),
    onRuntimeModelStatusChange: vi.fn(),
    localCorpusBootstrapEnabled: true,
    localCorpusState: { capability: "loading" as const, documents: [], resultText: "" },
    onLocalCorpusRefresh: vi.fn(),
    onLocalCorpusRegister: vi.fn(),
    onLocalCorpusUpdate: vi.fn(),
    onLocalCorpusDelete: vi.fn(),
    onLocalCorpusEditRequest: vi.fn(),
    webSearchBootstrapEnabled: true,
    webSearchToggleEnabled: false,
    webSearchState: { capability: "idle" as const, result: null, resultText: "" },
    onWebSearch: vi.fn(),
    dataControlsBootstrapEnabled: true,
    dataControlsState: {
      capability: "loading" as const,
      consent: null,
      retentionFacts: [],
      resultText: "",
    },
    onDataControlsRefresh: vi.fn(),
    onDataControlsToggle: vi.fn(),
    onDataControlsReset: vi.fn(),
    archivedChatsAvailable: false,
    archivedChatsState: { capability: "idle" as const, items: [], resultText: "" },
    onArchivedChatsLoad: vi.fn(),
    onArchivedChatsClose: vi.fn(),
    onArchivedChatsOpen: vi.fn(),
    onArchivedChatsUnarchive: vi.fn(),
    ...overrides,
  };
}

describe("SettingsModal", () => {
  test("renders nothing when closed", () => {
    const { container } = render(<SettingsModal {...baseProps({ open: false })} />);
    expect(container).toBeEmptyDOMElement();
  });

  test("opens on the basic Settings category by default, with Advanced Mode available", () => {
    render(<SettingsModal {...baseProps()} />);
    expect(document.querySelector("#settings")).not.toBeNull();
    expect(document.querySelector("#settings")?.closest("div")).not.toHaveAttribute("hidden");
    expect(document.querySelector("#configuration-panel")?.closest("div")).toHaveAttribute("hidden");
  });

  test("Web search Toggle appears in basic Settings, defaults to OFF, and sits above the Summary Mode row", () => {
    render(<SettingsModal {...baseProps()} />);
    const webSearchOff = document.querySelector("#web-search-mode-off")?.closest("label")?.querySelector("input");
    expect(webSearchOff).toBeChecked();
    expect(
      document.querySelector("#web-search-mode-label")?.compareDocumentPosition(
        document.querySelector("#summary-mode-label") as Node,
      ),
    ).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  test("switching to Advanced Mode reveals Runtime configuration control and hides basic settings", () => {
    render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#configuration-panel")?.closest("div")).not.toHaveAttribute("hidden");
    expect(document.querySelector("#settings")?.closest("div")).toHaveAttribute("hidden");
  });

  test("Advanced places Research Mode last and Basic has no duplicate Max New Tokens input", () => {
    render(<SettingsModal {...baseProps()} />);
    expect(document.querySelector("#max-new-tokens")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    const featureModes = document.querySelector("#feature-modes-panel");
    const configuration = document.querySelector("#configuration-panel");
    expect(featureModes).not.toBeNull();
    expect(configuration).not.toBeNull();
    expect(
      featureModes?.compareDocumentPosition(configuration as Node) ?? 0,
    ).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  test("Advanced Mode still appears when all four Governance bootstraps are disabled, showing only Runtime Model Status", () => {
    render(
      <SettingsModal
        {...baseProps({
          configurationBootstrapEnabled: false,
          governanceBootstrapEnabled: false,
          runtimeGovernanceBootstrapEnabled: false,
          guardrailGovernanceBootstrapEnabled: false,
        })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#configuration-panel")).toBeNull();
    expect(document.querySelector("#governance-panel")).toBeNull();
    expect(document.querySelector("#runtime-governance-panel")).toBeNull();
    expect(document.querySelector("#guardrail-governance-panel")).toBeNull();
    expect(document.querySelector("#runtime-model-status-panel")).not.toBeNull();
  });

  test("Advanced Mode still appears with only Governance enabled, and only renders the Governance panel", () => {
    render(
      <SettingsModal
        {...baseProps({
          configurationBootstrapEnabled: false,
          runtimeGovernanceBootstrapEnabled: false,
          guardrailGovernanceBootstrapEnabled: false,
        })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#governance-panel")).not.toBeNull();
    expect(document.querySelector("#configuration-panel")).toBeNull();
    expect(document.querySelector("#runtime-governance-panel")).toBeNull();
    expect(document.querySelector("#guardrail-governance-panel")).toBeNull();
  });

  test("Advanced Mode still appears with only Runtime Governance enabled, and only renders that panel", () => {
    render(
      <SettingsModal
        {...baseProps({
          configurationBootstrapEnabled: false,
          governanceBootstrapEnabled: false,
          guardrailGovernanceBootstrapEnabled: false,
        })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    expect(document.querySelector("#configuration-panel")).toBeNull();
    expect(document.querySelector("#governance-panel")).toBeNull();
    expect(document.querySelector("#guardrail-governance-panel")).toBeNull();
  });

  test("Advanced Mode still appears with only Guardrail Governance enabled, and only renders that panel", () => {
    render(
      <SettingsModal
        {...baseProps({
          configurationBootstrapEnabled: false,
          governanceBootstrapEnabled: false,
          runtimeGovernanceBootstrapEnabled: false,
        })}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#guardrail-governance-panel")).not.toBeNull();
    expect(document.querySelector("#configuration-panel")).toBeNull();
    expect(document.querySelector("#governance-panel")).toBeNull();
    expect(document.querySelector("#runtime-governance-panel")).toBeNull();
  });

  test("Advanced Mode renders the Local Corpus panel when its bootstrap is enabled", () => {
    render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#local-corpus-panel")).not.toBeNull();
  });

  test("Advanced Mode omits the Local Corpus panel when its bootstrap is disabled", () => {
    render(<SettingsModal {...baseProps({ localCorpusBootstrapEnabled: false })} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#local-corpus-panel")).toBeNull();
  });

  test("Advanced Mode renders the Web Search panel when its bootstrap is enabled", () => {
    render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#web-search-panel")).not.toBeNull();
  });

  test("Advanced Mode omits the Web Search panel when its bootstrap is disabled", () => {
    render(<SettingsModal {...baseProps({ webSearchBootstrapEnabled: false })} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#web-search-panel")).toBeNull();
  });

  test("Data Controls nav tab renders when its bootstrap is enabled and switches content", () => {
    render(<SettingsModal {...baseProps()} />);
    expect(screen.getByRole("button", { name: "Data controls" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Data controls" }));
    expect(document.querySelector("#data-controls-panel")).not.toBeNull();
    expect(document.querySelector("#settings")?.closest("div")).toHaveAttribute("hidden");
  });

  test("Data Controls nav tab is omitted when its bootstrap is disabled", () => {
    render(<SettingsModal {...baseProps({ dataControlsBootstrapEnabled: false })} />);
    expect(screen.queryByRole("button", { name: "Data controls" })).toBeNull();
  });

  test("switching to Advanced Mode reveals the Governance Definitions panel", () => {
    render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#governance-panel")?.closest("div")).not.toHaveAttribute("hidden");
  });

  test("the close button calls onClose", () => {
    const onClose = vi.fn();
    render(<SettingsModal {...baseProps({ onClose })} />);
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalled();
  });

  test("clicking the backdrop (outside the dialog) calls onClose", () => {
    const onClose = vi.fn();
    render(<SettingsModal {...baseProps({ onClose })} />);
    fireEvent.click(document.querySelector(".settings-modal-backdrop")!);
    expect(onClose).toHaveBeenCalled();
  });

  test("clicking inside the dialog does not call onClose", () => {
    const onClose = vi.fn();
    render(<SettingsModal {...baseProps({ onClose })} />);
    fireEvent.click(screen.getByRole("dialog"));
    expect(onClose).not.toHaveBeenCalled();
  });

  test("pressing Escape calls onClose", () => {
    const onClose = vi.fn();
    render(<SettingsModal {...baseProps({ onClose })} />);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalled();
  });

  test("the expressive-mode toggle is off by default and reports the change via onSettingsChange", () => {
    const onSettingsChange = vi.fn();
    render(<SettingsModal {...baseProps({ onSettingsChange })} />);
    const toggle = screen.getByRole("checkbox", { name: "Expressive mode" });
    expect(toggle).not.toBeChecked();
    fireEvent.click(toggle);
    expect(onSettingsChange).toHaveBeenCalledWith({ ...SETTINGS_FORM, expressiveMode: true });
  });

  test("reopening the modal always resets back to the basic Settings category", () => {
    const { rerender } = render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#configuration-panel")?.closest("div")).not.toHaveAttribute("hidden");

    rerender(<SettingsModal {...baseProps({ open: false })} />);
    rerender(<SettingsModal {...baseProps({ open: true })} />);

    expect(document.querySelector("#settings")?.closest("div")).not.toHaveAttribute("hidden");
    expect(document.querySelector("#configuration-panel")?.closest("div")).toHaveAttribute("hidden");
  });
});
