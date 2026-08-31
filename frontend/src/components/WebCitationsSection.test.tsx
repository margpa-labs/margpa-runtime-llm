import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import WebCitationsSection from "./WebCitationsSection";
import type { PersistentTurnWebCitations } from "../types";

function evidence(overrides: Partial<PersistentTurnWebCitations> = {}): PersistentTurnWebCitations {
  return {
    available: true,
    citations: [
      {
        citation_id: "web-citation-1",
        requested_url: "https://example.org/article",
        canonical_url: "https://example.org/article",
        title: "https://example.org/article",
        provider_key: "direct_url",
        source_authority: "general",
        fetched_at: "2026-08-30T00:00:00Z",
        content_type: "text/html",
        transformation: "html_text_extracted",
        content_sha512: "a".repeat(128),
        source_class: "public_web",
        selected_order: 1,
      },
    ],
    failure_reason: null,
    specific_failure_reason: null,
    ...overrides,
  };
}

describe("WebCitationsSection", () => {
  test("renders the Canonical URL, Public Web Source label, and Untrusted label", () => {
    render(<WebCitationsSection language="en" evidence={evidence()} />);
    // Title and URL are the same string for a Direct URL Fetch
    // (`fetch_direct_url()` sets `title=url`), so both rows render it.
    expect(screen.getAllByText("https://example.org/article")).toHaveLength(2);
    expect(screen.getByText("Public Web")).toBeInTheDocument();
    // P8-MR9-3 (P8-CODEX-011/UF-UI-012): the Untrusted Label carries its own
    // Semantic Class so app.css can give it the app's caution Token, unified
    // with the rest of this Citation Card's Fields instead of an inherited
    // default color.
    expect(screen.getByText("Untrusted External Content")).toHaveClass(
      "web-search-panel-untrusted-label",
    );
  });

  test("renders the failure reason instead of a Citation when the Fetch failed", () => {
    render(
      <WebCitationsSection
        language="en"
        evidence={evidence({ citations: [], failure_reason: "url_rejected" })}
      />,
    );
    expect(screen.getByText("Fetch rejected: url_rejected")).toBeInTheDocument();
    expect(screen.queryByText("Public Web")).toBeNull();
  });

  // -- P8-MR2 (P8-MANUAL-002) / UF-P8-007: Specific Failure Reason ---------

  test("renders the Specific Failure Reason alongside the Aggregate one", () => {
    render(
      <WebCitationsSection
        language="en"
        evidence={evidence({
          citations: [],
          failure_reason: "url_rejected",
          specific_failure_reason: "private_or_loopback_address",
        })}
      />,
    );
    expect(screen.getByText("Fetch rejected: url_rejected", { exact: false })).toBeInTheDocument();
    expect(screen.getByText(/private_or_loopback_address/)).toBeInTheDocument();
    expect(screen.getByText(/Specific Reason/)).toBeInTheDocument();
  });

  test("omits the Specific Reason row when only the Aggregate Reason is known", () => {
    render(
      <WebCitationsSection
        language="en"
        evidence={evidence({ citations: [], failure_reason: "url_rejected" })}
      />,
    );
    expect(screen.queryByText(/Specific Reason/)).toBeNull();
  });

  // -- P8-RW6-A (P8-CODEX-005): Requested vs Canonical URL display --------

  test("shows no Redirected-from row when requested_url equals canonical_url", () => {
    render(<WebCitationsSection language="en" evidence={evidence()} />);
    expect(screen.queryByText("Redirected from")).toBeNull();
  });

  test("shows a Redirected-from row when requested_url differs from canonical_url", () => {
    const redirected = evidence({
      citations: [
        {
          ...evidence().citations[0]!,
          requested_url: "https://agency.gov/start",
          canonical_url: "https://example.org/final",
        },
      ],
    });
    render(<WebCitationsSection language="en" evidence={redirected} />);
    expect(screen.getByText("Redirected from")).toBeInTheDocument();
    expect(screen.getByText("https://agency.gov/start")).toBeInTheDocument();
  });

  // -- P8-MR2 (P8-MANUAL-002): required Metadata display -------------------

  test("renders Source Authority, Fetched At, Content Type, and Transformation", () => {
    render(<WebCitationsSection language="en" evidence={evidence()} />);
    expect(screen.getByText("Source Authority")).toBeInTheDocument();
    expect(screen.getByText("general")).toBeInTheDocument();
    expect(screen.getByText("Fetched At")).toBeInTheDocument();
    expect(screen.getByText("2026-08-30T00:00:00Z")).toBeInTheDocument();
    expect(screen.getByText("Content Type")).toBeInTheDocument();
    expect(screen.getByText("text/html")).toBeInTheDocument();
    expect(screen.getByText("Transformation")).toBeInTheDocument();
    expect(screen.getByText("HTML text extracted")).toBeInTheDocument();
  });

  test("the Canonical URL Copy button is never mislabelled as a generic Path", () => {
    render(<WebCitationsSection language="en" evidence={evidence()} />);
    expect(screen.getByText("Copy Canonical URL")).toBeInTheDocument();
    expect(screen.queryByText("Copy path")).toBeNull();
  });

  test("the Requested URL row also offers its own Copy button when redirected", () => {
    const redirected = evidence({
      citations: [
        {
          ...evidence().citations[0]!,
          requested_url: "https://agency.gov/start",
          canonical_url: "https://example.org/final",
        },
      ],
    });
    render(<WebCitationsSection language="en" evidence={redirected} />);
    expect(screen.getByText("Copy Requested URL")).toBeInTheDocument();
  });
});
