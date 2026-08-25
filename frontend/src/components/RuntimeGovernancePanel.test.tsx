import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import RuntimeGovernancePanel, {
  type RuntimeGovernanceControlState,
} from "./RuntimeGovernancePanel";
import type { RuntimeGovernanceStatus } from "../types";

const offStatus: RuntimeGovernanceStatus = {
  enabled: true,
  revision: 1,
  current_mode: "off",
  descriptors: [
    { mode: "off", availability: "available", unavailable_reason_code: null },
    { mode: "observe", availability: "available", unavailable_reason_code: null },
    { mode: "enforce", availability: "unavailable", unavailable_reason_code: "no_definitions" },
  ],
  points: [],
  evidence: null,
};

const enforceReadyStatus: RuntimeGovernanceStatus = {
  ...offStatus,
  revision: 2,
  descriptors: [
    { mode: "off", availability: "available", unavailable_reason_code: null },
    { mode: "observe", availability: "available", unavailable_reason_code: null },
    { mode: "enforce", availability: "available", unavailable_reason_code: null },
  ],
  points: [
    {
      point_id: "main_model.post",
      execution_state: "evaluated",
      selected_descriptor_count: 3,
      severity: "high",
      recommended_action_count: 1,
      executed_action_count: 1,
      unavailable_reason_code: null,
      degraded_reason_code: null,
      latency_ms: 2,
      observation_count: 3,
      pass_count: 1,
      deviation_count: 1,
      deferred_count: 1,
    },
  ],
  evidence: { degraded: false, degraded_reason_code: null, degraded_event_count: 0 },
};

const observeCurrentStatus: RuntimeGovernanceStatus = {
  ...offStatus,
  revision: 3,
  current_mode: "observe",
};

const enforceCurrentStatus: RuntimeGovernanceStatus = {
  ...enforceReadyStatus,
  revision: 4,
  current_mode: "enforce",
};

function readyState(
  overrides: Partial<RuntimeGovernanceControlState> = {},
): RuntimeGovernanceControlState {
  return { capability: "ready", status: offStatus, resultText: "", ...overrides };
}

describe("RuntimeGovernancePanel", () => {
  test("renders nothing when not visible, even with a ready status (bootstrap-gated)", () => {
    const { container } = render(
      <RuntimeGovernancePanel
        language="en"
        visible={false}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("Enforce is disabled when the Composition reports it unavailable", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).toBeDisabled();
  });

  test("Enforce becomes selectable once the Composition reports it available", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).not.toBeDisabled();
  });

  test("Off stays enabled and reflects the current mode as checked", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute(
      "aria-checked",
      "false",
    );
  });

  test("clicking Observe immediately mutates while selection stays server-canonical", () => {
    const onApply = vi.fn();
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={onApply}
      />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute(
      "aria-checked",
      "false",
    );

    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));

    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith("observe");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
    expect(document.querySelector("#runtime-governance-apply")).toBeNull();
  });

  // P4-CODEX-013: a fresh Mount that already has a non-off Server Status
  // (e.g. reopening the Settings Modal, which fully unmounts/remounts
  // this component) must select the real Current Mode immediately.
  test("mounting directly with an Observe status selects Observe, not Off", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: observeCurrentStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
  });

  test("mounting directly with an Enforce status selects Enforce, not Off", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceCurrentStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
  });

  test("a new Status Revision re-syncs the selected Mode to the Server's Current Mode", () => {
    const { rerender } = render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");

    rerender(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: observeCurrentStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "false");
  });

  test("shows the Semantic Boundary notice — Enforce only intervenes on structural Deviations today", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(document.querySelector("#runtime-governance-semantic-boundary-notice")).not.toBeNull();
    expect(screen.getByText(/Deferred/u)).toBeInTheDocument();
    expect(screen.queryByText(/Phase 6/u)).toBeNull();
  });

  test("shows the per-Point Observation pass/deviation/deferred breakdown", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    const pointRow = document.querySelector("#runtime-governance-points dd");
    expect(pointRow?.textContent).toContain("Observations: 3");
    expect(pointRow?.textContent).toContain("Pass 1");
    expect(pointRow?.textContent).toContain("Deviation 1");
    expect(pointRow?.textContent).toContain("Deferred (awaiting semantic evaluation) 1");
  });

  test("with an Enforce-ready Snapshot, clicking Enforce calls onApply immediately", () => {
    const onApply = vi.fn();
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={onApply}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).not.toBeDisabled();

    fireEvent.click(screen.getByRole("radio", { name: "Enforce" }));
    expect(onApply).toHaveBeenCalledWith("enforce");
    expect(screen.getByRole("radio", { name: "Enforce" })).toHaveAttribute("aria-checked", "false");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
  });

  test("with an Enforce-unavailable Snapshot, Enforce stays disabled and unselectable", () => {
    const onApply = vi.fn();
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={onApply}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).toBeDisabled();

    fireEvent.click(screen.getByRole("radio", { name: "Enforce" }));
    expect(screen.getByRole("radio", { name: "Enforce" })).toHaveAttribute("aria-checked", "false");

    expect(onApply).not.toHaveBeenCalled();
    expect(onApply).not.toHaveBeenCalledWith("enforce");
  });

  test("renders per-Point status only once a bound Point result is present", () => {
    const { rerender } = render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("main_model.post")).toBeNull();

    rerender(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByText("main_model.post")).toBeInTheDocument();
  });

  test("shows the Evidence Degraded status once present", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({
          status: {
            ...enforceReadyStatus,
            evidence: {
              degraded: true,
              degraded_reason_code: "evidence_write_failed",
              degraded_event_count: 3,
            },
          },
        })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByText("Degraded")).toBeInTheDocument();
    expect(screen.getByText("evidence_write_failed")).toBeInTheDocument();
  });

  test("Mode selectors are disabled while a refresh is in flight", () => {
    render(
      <RuntimeGovernancePanel
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
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={{ capability: "loading", status: null, resultText: "" }}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("main_model.post")).toBeNull();
  });

  test("renders nothing about the status when the Composition is disabled", () => {
    render(
      <RuntimeGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: { ...offStatus, enabled: false } })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByRole("radio", { name: "OFF" })).toBeNull();
  });
});
