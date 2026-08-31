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
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
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
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
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
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
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
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
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
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByText("Reset to defaults"));
    expect(onReset).toHaveBeenCalledOnce();
  });

  test("P8-B: the Archived Chats section is absent when unavailable", () => {
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={false}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    expect(document.querySelector("#data-controls-archived-chats")).toBeNull();
  });

  test("P8-B (Lazy load): shows a Load trigger, not a fetched list, until the caller reports non-idle", () => {
    const onArchivedChatsLoad = vi.fn();
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={true}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={onArchivedChatsLoad}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    expect(document.querySelector("#archived-chats-list")).toBeNull();
    fireEvent.click(screen.getByText("Show Archived Chats"));
    expect(onArchivedChatsLoad).toHaveBeenCalledOnce();
  });

  test("P8-B: renders Title/Timestamp and wires Open/Unarchive for each Archived Chat", () => {
    const onArchivedChatsOpen = vi.fn();
    const onArchivedChatsUnarchive = vi.fn();
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={true}
        archivedChatsState={{
          capability: "ready",
          items: [
            {
              conversation_id: "conv-1",
              updated_at: "2026-08-30T00:00:00Z",
              state: "archived",
              title: "Archived research thread",
              has_active_session: false,
            },
          ],
          resultText: "",
        }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={onArchivedChatsOpen}
        onArchivedChatsUnarchive={onArchivedChatsUnarchive}
      />,
    );
    expect(screen.getByText("Archived research thread")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Open"));
    expect(onArchivedChatsOpen).toHaveBeenCalledWith("conv-1");
    fireEvent.click(screen.getByText("Unarchive"));
    expect(onArchivedChatsUnarchive).toHaveBeenCalledWith("conv-1");
  });

  // -- P8-MR3 (P8-MANUAL-003): Show/Close toggle -----------------------

  test("shows a Close button once expanded, which calls onArchivedChatsClose", () => {
    const onArchivedChatsClose = vi.fn();
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={true}
        archivedChatsState={{ capability: "ready", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={onArchivedChatsClose}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    expect(document.querySelector("#archived-chats-load")).toBeNull();
    fireEvent.click(screen.getByText("Close Archived Chats"));
    expect(onArchivedChatsClose).toHaveBeenCalledOnce();
  });

  test("no Close button is shown while still idle (never fetched)", () => {
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={true}
        archivedChatsState={{ capability: "idle", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    expect(document.querySelector("#archived-chats-close")).toBeNull();
  });

  test("P8-B (P8-REQ-012): an empty Archived list never implies delete/export are implemented", () => {
    render(
      <DataControlsPanel
        language="en"
        visible={true}
        state={readyState}
        onRefresh={vi.fn()}
        onToggle={vi.fn()}
        onReset={vi.fn()}
        archivedChatsAvailable={true}
        archivedChatsState={{ capability: "ready", items: [], resultText: "" }}
        onArchivedChatsLoad={vi.fn()}
        onArchivedChatsClose={vi.fn()}
        onArchivedChatsOpen={vi.fn()}
        onArchivedChatsUnarchive={vi.fn()}
      />,
    );
    expect(screen.getByText("No Archived Chats.")).toBeInTheDocument();
    // Scoped to the Archived Chats section specifically — the pre-existing,
    // unrelated "Future Training export" consent toggle legitimately
    // contains "export" elsewhere in this same Panel.
    const section = document.querySelector("#data-controls-archived-chats");
    expect(section).not.toBeNull();
    expect(section?.textContent).not.toMatch(/delete/i);
    expect(section?.textContent).not.toMatch(/export/i);
  });
});
