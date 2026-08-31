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
      requested_url: "https://example.org/",
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
      transformation: "html_text_extracted",
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

  test("fetched Search evidence is explicitly labelled Untrusted External Content", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={readyState()}
        onSearch={vi.fn()}
      />,
    );
    // P8-MR9-3 (P8-CODEX-011/UF-UI-012): shares its Semantic Class with the
    // Chat Citation Card's Untrusted Label, so both get the same unified
    // caution-Token color from app.css.
    expect(screen.getByText("Untrusted External Content")).toHaveClass(
      "web-search-panel-untrusted-label",
    );
  });

  test("submitting a Direct URL while the toggle is ON calls onFetchDirectUrl", () => {
    const onFetchDirectUrl = vi.fn();
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={vi.fn()}
        onFetchDirectUrl={onFetchDirectUrl}
      />,
    );
    fireEvent.change(screen.getByLabelText("URL to fetch"), {
      target: { value: "https://example.org/article" },
    });
    fireEvent.click(screen.getByText("Fetch"));
    expect(onFetchDirectUrl).toHaveBeenCalledWith("https://example.org/article");
  });

  test("the Direct URL input and Fetch button are disabled when the Settings toggle is OFF", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={false}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={vi.fn()}
        onFetchDirectUrl={vi.fn()}
      />,
    );
    expect(screen.getByLabelText("URL to fetch")).toBeDisabled();
    expect(screen.getByText("Fetch")).toBeDisabled();
  });

  test("the Fetch button is disabled when no onFetchDirectUrl handler is supplied", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={{ capability: "idle", result: null, resultText: "" }}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.getByText("Fetch")).toBeDisabled();
  });

  // -- P8-RW6-A (P8-CODEX-005): Requested vs Canonical URL display --------

  test("shows no Redirected-from note when requested_url equals canonical_url", () => {
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={readyState()}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.queryByText(/Redirected from/)).toBeNull();
  });

  test("shows a Redirected-from note when requested_url differs from canonical_url", () => {
    const redirectedResult: WebSearchResult = {
      ...result,
      evidence: [
        {
          ...result.evidence[0]!,
          requested_url: "https://agency.gov/start",
          canonical_url: "https://example.org/final",
        },
      ],
    };
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={readyState({ result: redirectedResult })}
        onSearch={vi.fn()}
      />,
    );
    expect(screen.getByText(/Redirected from/)).toBeInTheDocument();
    expect(screen.getByText(/https:\/\/agency\.gov\/start/)).toBeInTheDocument();
  });

  test("renders the Direct URL fetch result independently of the Search result", () => {
    const directUrlResult: WebSearchResult = {
      ...result,
      evidence: [
        {
          ...result.evidence[0]!,
          evidence_id: "b".repeat(128),
          title: "Direct URL Result",
          fetched_content: "direct url body text",
        },
      ],
    };
    render(
      <WebSearchPanel
        language="en"
        visible={true}
        toggleEnabled={true}
        state={{
          capability: "idle",
          result: null,
          resultText: "",
          directUrl: { capability: "ready", result: directUrlResult, resultText: "" },
        }}
        onSearch={vi.fn()}
        onFetchDirectUrl={vi.fn()}
      />,
    );
    expect(screen.getByText("Direct URL Result")).toBeInTheDocument();
    expect(screen.getByText("direct url body text")).toBeInTheDocument();
    // The (idle, empty) Search result must not be affected by the Direct
    // URL result being present.
    expect(screen.queryByText("Example Result")).toBeNull();
  });
});
