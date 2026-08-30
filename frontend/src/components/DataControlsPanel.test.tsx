import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import DataControlsPanel, { type DataControlsState } from "./DataControlsPanel";

const readyState: DataControlsState = {
  capability: "ready",
  consent: {
    external_query_transmission_consent: false,
    feedback_research_use: false,
    synthetic_data_use: false,
    future_training_export: false,
  },
  retentionFacts: [
    { source_class: "public_web", retained: false, description: "not persisted" },
    { source_class: "user_provided", retained: true, description: "kept indefinitely" },
  ],
  resultText: "",
};

describe("DataControlsPanel", () => {
  test("renders nothing when not visible", () => {
    const { container } = render(
      <DataControlsPanel
        language="en"
        visible={false}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("all consent toggles default to unchecked (OFF)", () => {
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
      />,
    );
    for (const checkbox of screen.getAllByRole("checkbox")) {
      expect(checkbox).not.toBeChecked();
    }
  });

  test("toggling a consent checkbox calls onToggle with the field key and new value", () => {
    const onToggle = vi.fn();
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={onToggle}
        onReset={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByText("Research use of Feedback"));
    expect(onToggle).toHaveBeenCalledWith("feedback_research_use", true);
  });

  test("renders retention facts as read-only informational rows", () => {
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
      />,
    );
    expect(screen.getByText(/not persisted/)).toBeInTheDocument();
    expect(screen.getByText(/kept indefinitely/)).toBeInTheDocument();
  });

  test("clicking Reset calls onReset", () => {
    const onReset = vi.fn();
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={onReset}
      />,
    );
    fireEvent.click(screen.getByText("Reset to defaults"));
    expect(onReset).toHaveBeenCalledOnce();
  });
});
