import { render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import ConfigurationControlPanel, { type ConfigurationControlState } from "./ConfigurationControlPanel";
import type { ConfigurationSnapshot } from "../types";

const snapshot: ConfigurationSnapshot = {
  schema_version: "1",
  revision: 3,
  digest_sha512: "deadbeef",
  fields: [
    { key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" },
    { key: "selected_model", value: "main.qwen3-4b-q4-k-m", source: "default", apply_disposition: "restart_required" },
  ],
  feature_hooks: [],
  recording_hooks: [],
};

function readyState(overrides: Partial<ConfigurationControlState> = {}): ConfigurationControlState {
  return { capability: "ready", snapshot, resultText: "", ...overrides };
}

describe("ConfigurationControlPanel", () => {
  test("renders nothing when not visible, even with a ready snapshot (bootstrap-gated)", () => {
    const { container } = render(
      <ConfigurationControlPanel
        language="en"
        visible={false}
        state={readyState()}
        onRefresh={vi.fn()}
        onPreview={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("hides developer detail fields (revision, digest, model, context) until research mode is toggled on", () => {
    const { container } = render(
      <ConfigurationControlPanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onPreview={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByText("deadbeef").closest("dl")).toHaveAttribute("hidden");
    expect(container.querySelector("#configuration-preview")).toHaveAttribute("hidden");
  });

  test("never renders the raw snapshot into an input value usable for silent submission of secrets", () => {
    render(
      <ConfigurationControlPanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onPreview={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    // The digest appears only as read-only display text, never inside a form
    // input/textarea value that could be blindly resubmitted.
    const inputs = screen.queryAllByRole("textbox");
    for (const input of inputs) {
      expect((input as HTMLInputElement).value).not.toContain("deadbeef");
    }
  });

  test("Apply is disabled while a refresh is in flight, even with a snapshot already loaded", () => {
    render(
      <ConfigurationControlPanel
        language="en"
        visible={true}
        state={readyState({ capability: "loading" })}
        onRefresh={vi.fn()}
        onPreview={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Apply Research Mode" })).toBeDisabled();
  });

  test("renders nothing about the snapshot before the first successful load", () => {
    render(
      <ConfigurationControlPanel
        language="en"
        visible={true}
        state={{ capability: "loading", snapshot: null, resultText: "" }}
        onRefresh={vi.fn()}
        onPreview={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("deadbeef")).toBeNull();
  });
});
