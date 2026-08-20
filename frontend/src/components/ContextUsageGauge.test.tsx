import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import ContextUsageGauge from "./ContextUsageGauge";
import type { ContextUsage } from "../types";

const USAGE: ContextUsage = {
  prompt_tokens: 100,
  completion_tokens: 20,
  total_tokens: 120,
  loaded_context_size: 4096,
  usage_ratio: 0.029296875,
  breakdown: {
    conversation_history_tokens: 43,
    system_prompt_tokens: 57,
    rag_context_tokens: 0,
    free_tokens: 3976,
  },
};

describe("ContextUsageGauge", () => {
  test("is disabled and shows the unavailable tooltip before any usage data arrives", () => {
    render(<ContextUsageGauge language="en" usage={null} />);
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveAccessibleName("Context usage is not available yet");
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  test("shows the show/hide tooltip and opens the breakdown panel on click", () => {
    render(<ContextUsageGauge language="en" usage={USAGE} />);
    const button = screen.getByRole("button");
    expect(button).not.toBeDisabled();
    expect(button).toHaveAccessibleName("Show context status");
    expect(screen.queryByRole("dialog")).toBeNull();

    fireEvent.click(button);

    expect(button).toHaveAccessibleName("Hide context status");
    const panel = screen.getByRole("dialog");
    expect(panel).toHaveTextContent("3%");
    expect(panel).toHaveTextContent("43");
    expect(panel).toHaveTextContent("57");
    expect(panel).toHaveTextContent("3,976");
    expect(panel).toHaveTextContent("120 / 4,096 tokens");

    fireEvent.click(button);
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(button).toHaveAccessibleName("Show context status");
  });

  test("renders the Japanese breakdown labels", () => {
    render(<ContextUsageGauge language="ja" usage={USAGE} />);
    fireEvent.click(screen.getByRole("button"));
    const panel = screen.getByRole("dialog");
    expect(panel).toHaveTextContent("会話履歴");
    expect(panel).toHaveTextContent("System Prompt");
    expect(panel).toHaveTextContent("RAG Context");
    expect(panel).toHaveTextContent("残り");
  });

  test("keeps the hover tooltip in the DOM while the panel is open", () => {
    render(<ContextUsageGauge language="en" usage={USAGE} />);
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByRole("tooltip")).toHaveTextContent("Hide context status");
  });

  test("closes the panel on an outside click", () => {
    render(
      <div>
        <button type="button">outside</button>
        <ContextUsageGauge language="en" usage={USAGE} />
      </div>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Show context status" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    fireEvent.mouseDown(screen.getByRole("button", { name: "outside" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
