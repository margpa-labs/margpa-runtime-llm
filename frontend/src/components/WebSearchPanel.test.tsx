import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import WebSearchPanel, { type WebSearchPanelState } from "./WebSearchPanel";
import type { WebSearchResult } from "../types";

const result: WebSearchResult = {
  request_id: "req-1",
  activation: "manual",
  governance_mode: "off",
  evidence: [
    {
      evidence_id: "a".repeat(128),
      canonical_url: "https://example.org/",
      title: "Example Result",
      provider_key: "fixture_search",
      source_authority: "general",
      snippet: "a snippet",
      fetched: true,
      fetched_content: "fetched body text",
      withheld_by_governance: false,
      fetched_at: "2026-08-29T00:00:00Z",
      content_type: "text/html",
      prompt_injection_detected: false,
      rejected: false,
      rejection_reason: null,
    },
  ],
  citations: [],
  should_generate_with_evidence: true,
  failure_reason: null,
  network_calls_made: 2,
};

function readyState(overrides: Partial<WebSearchPanelState> = {}): WebSearchPanelState {
  return { capability: "ready", result, resultText: "", ...overrides };
}

describe("WebSearchPanel", () => {
  test("renders nothing when not visible (bootstrap-gated)", () => {
    const { container } = render(
      <WebSearchPanel
        language="en"
        visible={false}
        toggleEnabled={true}
        state={readyState()}
        onSearch={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("shows an OFF note and disables input/search when the Settings toggle is OFF", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={false}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.getByText("Web search is OFF in Settings. Turn it ON to run a search.")).toBeInTheDocument();
    expect(screen.getByLabelText("Query")).toBeDisabled();
    expect(screen.getByText("Search")).toBeDisabled();
  });

  test("submitting a query while the toggle is ON calls onSearch", () => {
    const onSearch = vi.fn();
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={onSearch}
      />,
    );
    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "python" } });
    fireEvent.click(screen.getByText("Search"));
    expect(onSearch).toHaveBeenCalledWith("python");
  });

  test("submitting while the toggle is OFF does not call onSearch even if forced", () => {
    const onSearch = vi.fn();
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={false}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={onSearch}
      />,
    );
    const form = document.querySelector(".web-search-panel-form")!;
    fireEvent.submit(form);
    expect(onSearch).not.toHaveBeenCalled();
  });

  test("renders fetched evidence content", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={readyState()}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.getByText("Example Result")).toBeInTheDocument();
    expect(screen.getByText("fetched body text")).toBeInTheDocument();
  });

  test("renders a withheld note instead of content when governance withheld it", () => {
    const withheldResult: WebSearchResult = {
      ...result,
      evidence: [{ ...result.evidence[0]!, fetched_content: null, withheld_by_governance: true }],
    };
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={readyState({ result: withheldResult })}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.getByText("Content withheld: Prompt Injection detected.")).toBeInTheDocument();
    expect(screen.queryByText("fetched body text")).toBeNull();
  });
});
