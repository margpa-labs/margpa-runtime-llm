import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import GuardrailGovernancePanel, {
  type GuardrailGovernanceControlState,
} from "./GuardrailGovernancePanel";
import type { GuardrailGovernanceStatus } from "../types";

const offStatus: GuardrailGovernanceStatus = {
  enabled: true,
  revision: 1,
  current_mode: "off",
  descriptors: [
    { mode: "off", availability: "available", unavailable_reason_code: null },
    { mode: "observe", availability: "available", unavailable_reason_code: null },
    { mode: "enforce", availability: "available", unavailable_reason_code: null },
  ],
  points: [],
};

const enforceReadyStatus: GuardrailGovernanceStatus = {
  ...offStatus,
  revision: 2,
  points: [
    {
      point_id: "guardrail.input",
      execution_state: "evaluated",
      severity: "high",
      recommended_action_count: 1,
      executed_action_count: 1,
      unavailable_reason_code: null,
      degraded_reason_code: null,
      latency_ms: 2,
      detection_count: 5,
      match_count: 1,
    },
  ],
};

const observeCurrentStatus: GuardrailGovernanceStatus = {
  ...offStatus,
  revision: 3,
  current_mode: "observe",
};

const enforceCurrentStatus: GuardrailGovernanceStatus = {
  ...enforceReadyStatus,
  revision: 4,
  current_mode: "enforce",
};

function readyState(
  overrides: Partial<GuardrailGovernanceControlState> = {},
): GuardrailGovernanceControlState {
  return { capability: "ready", status: offStatus, resultText: "", ...overrides };
}

describe("GuardrailGovernancePanel", () => {
  test("renders nothing when not visible, even with a ready status (bootstrap-gated)", () => {
    const { container } = render(
      <GuardrailGovernancePanel
        language="en"
        visible={false}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("Off stays enabled and reflects the current mode as checked", () => {
    render(
      <GuardrailGovernancePanel
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
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={onApply}
      />,
    );
    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));
    expect(onApply).toHaveBeenCalledTimes(1);
    expect(onApply).toHaveBeenCalledWith("observe");
    expect(screen.getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(document.querySelector("#guardrail-governance-apply")).toBeNull();
  });

  test("mounting directly with an Observe status selects Observe, not Off", () => {
    render(
      <GuardrailGovernancePanel
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
      <GuardrailGovernancePanel
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
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");

    rerender(
      <GuardrailGovernancePanel
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

  test("shows the current Safety Model boundary without a Phase suffix", () => {
    render(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(document.querySelector("#guardrail-governance-safety-model-notice")).not.toBeNull();
    expect(screen.getByText(/dedicated Safety Model/u)).toBeInTheDocument();
    expect(screen.queryByText(/Phase 6/u)).toBeNull();
  });

  test("shows the per-Point detection and match counts", () => {
    render(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    const pointRow = document.querySelector("#guardrail-governance-points dd");
    expect(pointRow?.textContent).toContain("Detections: 5");
    expect(pointRow?.textContent).toContain("Matches: 1");
    expect(pointRow?.textContent).toContain("Executed actions: 1");
  });

  test("clicking Enforce calls onApply immediately", () => {
    const onApply = vi.fn();
    render(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={onApply}
      />,
    );
    fireEvent.click(screen.getByRole("radio", { name: "Enforce" }));
    expect(onApply).toHaveBeenCalledWith("enforce");
  });

  test("Enforce is disabled when the Composition reports it unavailable", () => {
    render(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState({
          status: {
            ...offStatus,
            descriptors: [
              { mode: "off", availability: "available", unavailable_reason_code: null },
              { mode: "observe", availability: "available", unavailable_reason_code: null },
              {
                mode: "enforce",
                availability: "unavailable",
                unavailable_reason_code: "guardrail_mode_unavailable",
              },
            ],
          },
        })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByRole("radio", { name: "Enforce" })).toBeDisabled();
  });

  test("renders per-Point status only once a bound Point result is present", () => {
    const { rerender } = render(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("guardrail.input")).toBeNull();

    rerender(
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={readyState({ status: enforceReadyStatus })}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.getByText("guardrail.input")).toBeInTheDocument();
  });

  test("Mode selectors are disabled while a refresh is in flight", () => {
    render(
      <GuardrailGovernancePanel
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
      <GuardrailGovernancePanel
        language="en"
        visible={true}
        state={{ capability: "loading", status: null, resultText: "" }}
        onRefresh={vi.fn()}
        onApply={vi.fn()}
      />,
    );
    expect(screen.queryByText("guardrail.input")).toBeNull();
  });

  test("renders nothing about the status when the Composition is disabled", () => {
    render(
      <GuardrailGovernancePanel
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
