import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import CitationsSection from "./CitationsSection";
import type { Citation, CitationEvidence } from "../types";

function citation(overrides: Partial<Citation> = {}): Citation {
  return {
    source_class: "documentation_rag_citation",
    project_relative_path: "docs/public/overview_ja.md",
    heading_breadcrumb: "Overview",
    chunk_id: "a".repeat(128),
    document_sha512: "b".repeat(128),
    retrieval_score: 1.0,
    selected_order: 1,
    truncated: false,
    document_title: null,
    storage_display_path: null,
    ...overrides,
  };
}

function evidence(citations: Citation[]): CitationEvidence {
  return { citations, warnings: [] };
}

describe("CitationsSection", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("distinguishes Local Corpus from Project Docs by source_class", () => {
    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({ source_class: "documentation_rag_citation" }),
          citation({
            source_class: "local_corpus",
            project_relative_path: "local-corpus/probe-7.md",
            chunk_id: "c".repeat(128),
            document_sha512: "d".repeat(128),
            selected_order: 2,
          }),
        ])}
      />,
    );

    const rows = document.querySelectorAll(".message-citation");
    expect(rows).toHaveLength(2);
    expect(within(rows[0] as HTMLElement).getByText("Project Docs")).toBeTruthy();
    expect(within(rows[1] as HTMLElement).getByText("Local Corpus")).toBeTruthy();
  });

  test("renders a shortened Chunk ID / Document Digest but keeps the full value available", () => {
    const fullChunkId = "e".repeat(128);
    const fullDigest = "f".repeat(128);
    render(
      <CitationsSection
        language="en"
        evidence={evidence([citation({ chunk_id: fullChunkId, document_sha512: fullDigest })])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    const shortened = within(row).getByTitle(fullChunkId);
    expect(shortened.textContent).not.toBe(fullChunkId);
    expect(shortened.textContent.length).toBeLessThan(fullChunkId.length);
    expect(within(row).getByTitle(fullDigest)).toBeTruthy();
  });

  test("copies the full, unshortened Chunk ID and Document Digest", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const fullChunkId = "1".repeat(128);
    const fullDigest = "2".repeat(128);

    render(
      <CitationsSection
        language="en"
        evidence={evidence([citation({ chunk_id: fullChunkId, document_sha512: fullDigest })])}
      />,
    );

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Copy chunk ID" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenCalledWith(fullChunkId);

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Copy document digest" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenCalledWith(fullDigest);
  });

  test("shows the empty-citations message when there are no citations", () => {
    render(<CitationsSection language="en" evidence={evidence([])} />);
    expect(screen.getByText("No reference documents")).toBeTruthy();
  });

  // --- P7-RW3-A (P7-CODEX-011): the User Mac Manual Probe found the Field
  // Labels missing and the three Copy Buttons stacked on top of each
  // other (a shared CSS Grid Cell) - only the last Button ever rendered,
  // and the two visible shortened Hashes had no Label distinguishing
  // Chunk ID from Document Digest. ---

  test("shows a distinct, labeled row for every required Citation field", () => {
    render(
      <CitationsSection
        language="en"
        evidence={evidence([citation({ heading_breadcrumb: "Overview > Scope" })])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    for (const label of ["Source", "Path", "Heading", "Chunk ID", "Document Digest"]) {
      expect(within(row).getByText(label)).toBeTruthy();
    }
    expect(within(row).getByText("Overview > Scope")).toBeTruthy();
  });

  test("renders three distinct, visible Copy Buttons that each copy their own field", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const path = "docs/public/overview_ja.md";
    const fullChunkId = "3".repeat(128);
    const fullDigest = "4".repeat(128);

    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({
            project_relative_path: path,
            chunk_id: fullChunkId,
            document_sha512: fullDigest,
          }),
        ])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    const buttons = within(row).getAllByRole("button");
    // Three separate Elements - never the same overlapping Node the
    // previous shared Grid Cell collapsed them into.
    expect(new Set(buttons)).toHaveProperty("size", 3);
    expect(buttons.map((button) => button.textContent)).toEqual([
      "Copy path",
      "Copy chunk ID",
      "Copy document digest",
    ]);

    await act(async () => {
      fireEvent.click(within(row).getByRole("button", { name: "Copy path" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenLastCalledWith(path);

    await act(async () => {
      fireEvent.click(within(row).getByRole("button", { name: "Copy chunk ID" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenLastCalledWith(fullChunkId);

    await act(async () => {
      fireEvent.click(within(row).getByRole("button", { name: "Copy document digest" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenLastCalledWith(fullDigest);
  });

  test("shows distinct Chunk IDs sharing the same Document Digest for two chunks of one document", () => {
    const sharedDigest = "5".repeat(128);
    const firstChunkId = "6".repeat(128);
    const secondChunkId = "7".repeat(128);
    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({ chunk_id: firstChunkId, document_sha512: sharedDigest, selected_order: 1 }),
          citation({ chunk_id: secondChunkId, document_sha512: sharedDigest, selected_order: 2 }),
        ])}
      />,
    );

    const rows = document.querySelectorAll(".message-citation");
    expect(rows).toHaveLength(2);
    const firstRow = rows[0] as HTMLElement;
    const secondRow = rows[1] as HTMLElement;
    expect(within(firstRow).getByTitle(firstChunkId)).toBeTruthy();
    expect(within(secondRow).getByTitle(secondChunkId)).toBeTruthy();
    expect(within(firstRow).getByTitle(sharedDigest)).toBeTruthy();
    expect(within(secondRow).getByTitle(sharedDigest)).toBeTruthy();
    expect(within(firstRow).getByTitle(firstChunkId).textContent).not.toBe(
      within(secondRow).getByTitle(secondChunkId).textContent,
    );
  });

  // --- P7-RW5-B (P7-CODEX-015)/P7-RW5-C (P7-CODEX-016): the User Mac
  // Manual Probe found a Local Corpus Citation showing an empty Heading
  // row and a Synthetic `local-corpus/<slug>.md` Path that is not a real
  // Filesystem location. ---

  test("shows a Title row (not Heading) with the registered Document Title for a Local Corpus citation", () => {
    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({
            source_class: "local_corpus",
            heading_breadcrumb: "",
            document_title: "MARGPA Manual Probe 9",
          }),
        ])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    expect(within(row).getByText("Title")).toBeTruthy();
    expect(within(row).queryByText("Heading")).toBeNull();
    expect(within(row).getByText("MARGPA Manual Probe 9")).toBeTruthy();
  });

  test("keeps the Heading row (not Title) for a Project Docs citation", () => {
    render(
      <CitationsSection
        language="en"
        evidence={evidence([citation({ heading_breadcrumb: "Overview > Scope" })])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    expect(within(row).getByText("Heading")).toBeTruthy();
    expect(within(row).queryByText("Title")).toBeNull();
  });

  test("shows and copies the real storage Path for a Local Corpus citation, not the synthetic slug", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const realPath = "runtime_data/persistent/mac-local-primary/local_corpus/documents.json";

    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({
            source_class: "local_corpus",
            project_relative_path: "local-corpus/margpa-manual-probe-9-e51ed2fa.md",
            storage_display_path: realPath,
          }),
        ])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    expect(within(row).getByText(realPath)).toBeTruthy();
    expect(within(row).queryByText("local-corpus/margpa-manual-probe-9-e51ed2fa.md")).toBeNull();

    await act(async () => {
      fireEvent.click(within(row).getByRole("button", { name: "Copy path" }));
      await Promise.resolve();
    });
    expect(writeText).toHaveBeenCalledWith(realPath);
  });

  test("falls back to project_relative_path for a Local Corpus citation with no storage_display_path (legacy record)", () => {
    render(
      <CitationsSection
        language="en"
        evidence={evidence([
          citation({
            source_class: "local_corpus",
            project_relative_path: "local-corpus/legacy-doc-11223344.md",
            storage_display_path: null,
          }),
        ])}
      />,
    );

    const row = document.querySelector(".message-citation") as HTMLElement;
    expect(within(row).getByText("local-corpus/legacy-doc-11223344.md")).toBeTruthy();
  });
});
