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

  test("Enforce is always disabled in Phase 3, even when selected mode is off", () => {
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "Enforce" })).toBeDisabled();
  });

  test("Off and Observe stay enabled and reflect the current mode as checked", () => {
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "OFF" })).not.toBeDisabled();
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
  });

  // P4-CODEX-012-B: clicking a Mode Radio must visibly flip aria-checked,
  // and the Mode actually clicked (not the initial one) must be what
  // Apply hands to onApply — a plain initial-DOM assertion cannot catch a
  // Selector Contract mismatch (P4-CODEX-012-A) between the Radio's own
  // aria-checked state and the CSS that is supposed to render it.
  test("clicking Observe flips its aria-checked state and clears Off's", () => {
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={vi.fn()} />);
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");

    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));

    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "true");
  });

  test("clicking Observe then Apply calls onApply with observe exactly once", () => {
    const onApply = vi.fn();
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={onApply} />);

    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));

    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith("observe");
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

  test("Enforce stays unselectable — clicking it never changes the checked Mode or reaches Apply", () => {
    const onApply = vi.fn();
    render(<GovernancePanel language="en" visible={true} state={readyState()} onRefresh={vi.fn()} onApply={onApply} />);

    fireEvent.click(screen.getByRole("radio", { name: "Enforce" }));
    expect(screen.getByRole("radio", { name: "Enforce" })).toHaveAttribute("aria-checked", "false");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");

    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).toHaveBeenCalledWith("off");
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

  test("Apply is disabled while a refresh is in flight, even with a status already loaded", () => {
    render(
      <GovernancePanel
        language="en"
        visible={true}
        state={readyState({ capability: "loading" })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Apply" })).toBeDisabled();
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
