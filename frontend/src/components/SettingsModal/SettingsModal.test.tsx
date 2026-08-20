import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import SettingsModal from "./SettingsModal";
import type { SettingsFormState } from "../SettingsPanel";
import type { ConfigurationControlState } from "../ConfigurationControlPanel";

const SETTINGS_FORM: SettingsFormState = {
  responseLanguage: "ja",
  maxNewTokens: "2048",
  thinkingMode: false,
  thinkingVisibility: false,
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
    onConfigurationPreview: vi.fn(),
    onConfigurationApply: vi.fn(),
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

  test("switching to Advanced Mode reveals Runtime configuration control and hides basic settings", () => {
    render(<SettingsModal {...baseProps()} />);
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    expect(document.querySelector("#configuration-panel")?.closest("div")).not.toHaveAttribute("hidden");
    expect(document.querySelector("#settings")?.closest("div")).toHaveAttribute("hidden");
  });

  test("Advanced Mode is not offered when the configuration bootstrap is disabled", () => {
    render(<SettingsModal {...baseProps({ configurationBootstrapEnabled: false })} />);
    expect(screen.queryByRole("button", { name: "Advanced Mode" })).toBeNull();
    expect(document.querySelector("#configuration-panel")).toBeNull();
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
