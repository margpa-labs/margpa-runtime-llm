import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import GovernancePanel, { type GovernanceControlState } from "./GovernancePanel";
import type { GovernanceStatus } from "../types";

const offStatus: GovernanceStatus = {
  mode: {
    revision: 1,
    digest_sha512: "deadbeef",
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
};

const observeStatus: GovernanceStatus = {
  mode: { ...offStatus.mode, revision: 2, current_mode: "observe" },
  observe_summary: {
    provider_state: "loaded",
    package_found: true,
    package_state: "valid",
    definition_count: 18,
    valid_definition_count: 18,
    invalid_definition_count: 0,
    unsupported_definition_count: 0,
    compiled_plan_id: "plan-abc",
  },
};

function readyState(overrides: Partial<GovernanceControlState> = {}): GovernanceControlState {
  return { capability: "ready", status: offStatus, resultText: "", ...overrides };
}

describe("GovernancePanel", () => {
  test("renders nothing when not visible, even with a ready status (bootstrap-gated)", () => {
    const { container } = render(
      <GovernancePanel language="en" visible={false} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("Enforce is disabled when the Definitions surface reports it unavailable", () => {
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "Enforce" })).toBeDisabled();
  });

  test("Off and Observe stay enabled and reflect the current mode as checked", () => {
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "OFF" })).not.toBeDisabled();
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
  });

  test("clicking Observe immediately calls onApply and keeps server-canonical selection", () => {
    const onApply = vi.fn();
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={onApply} />);
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");

    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));

    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith("observe");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
    expect(document.querySelector("#governance-apply")).toBeNull();
  });

  // P4-CODEX-013: a fresh Mount that already has a non-off Server Status
  // (e.g. reopening the Settings Modal, which fully unmounts/remounts
  // this component) must select the real Current Mode immediately, not
  // reset to OFF and only fix itself on the next Revision change.
  test("mounting directly with an Observe status selects Observe, not Off", () => {
    render(
      <GovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: observeStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
  });

  test("a new Status Revision re-syncs the selected Mode to the Server's Current Mode", () => {
    const { rerender } = render(
      <GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");

    rerender(
      <GovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: observeStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
  });

  test("Enforce stays unselectable and never reaches the mutation callback", () => {
    const onApply = vi.fn();
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={onApply} />);

    fireEvent.click(screen.getByRole("radio", { name: "Enforce" }));
    expect(screen.getByRole("radio", { name: "Enforce" })).toHaveAttribute("aria-checked", "false");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");

    expect(onApply).not.toHaveBeenCalled();
    expect(onApply).not.toHaveBeenCalledWith("enforce");
  });

  test("renders the Observe summary counts only once a summary is present", () => {
    const { rerender } = render(
      <GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />,
    );
    expect(screen.queryByText("plan-abc")).toBeNull();

    rerender(
      <GovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: observeStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByText("plan-abc")).toBeInTheDocument();
    expect(screen.getAllByText("18")).toHaveLength(2);
  });

  test("Mode selectors are disabled while a refresh is in flight", () => {
    render(
      <GovernancePanel
        language="en"
        visible={true}
        state={readyState({ capability: "loading" })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toBeDisabled();
    expect(screen.getByRole("radio", { name: "Observe" })).toBeDisabled();
  });

  test("renders nothing about the status before the first successful load", () => {
    render(
      <GovernancePanel
        language="en"
        visible={true}
        state={{ capability: "loading", status: null, resultText: "" }}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("deadbeef")).toBeNull();
  });
});
