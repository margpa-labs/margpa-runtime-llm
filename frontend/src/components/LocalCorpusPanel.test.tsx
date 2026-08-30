import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import LocalCorpusPanel, { type LocalCorpusState } from "./LocalCorpusPanel";
import type { LocalCorpusDocumentSummary } from "../types";

const document1: LocalCorpusDocumentSummary = {
  document_id: "a".repeat(32),
  state: "active",
  title: "研究メモ",
  content_sha512: "deadbeef",
  character_count: 42,
  current_revision: 1,
  created_at: "2026-08-29T00:00:00Z",
  updated_at: "2026-08-29T00:00:00Z",
};

function readyState(overrides: Partial<LocalCorpusState> = {}): LocalCorpusState {
  return { capability: "ready", documents: [document1], resultText: "", ...overrides };
}

describe("LocalCorpusPanel", () => {
  test("renders nothing when not visible, even with ready documents (bootstrap-gated)", () => {
    const { container } = render(
      <LocalCorpusPanel
        language="en"
        visible={false}
        state={readyState()}
        onRefresh={vi.fn()}
        onRegister={vi.fn()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onEditRequest={vi.fn()}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("renders the document list", () => {
    render(
      <LocalCorpusPanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onRegister={vi.fn()}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onEditRequest={vi.fn()}
      />,
    );
    expect(screen.getByText("研究メモ")).toBeInTheDocument();
  });

  test("submitting the form with title and content calls onRegister and clears the form", () => {
    const onRegister = vi.fn();
    render(
      <LocalCorpusPanel
        language="en"
        visible={true}
        state={readyState({ documents: [] })}
        onRefresh={vi.fn()}
        onRegister={onRegister}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onEditRequest={vi.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "New Doc" } });
    fireEvent.change(screen.getByLabelText("Content (text / Markdown)"), {
      target: { value: "Body text" },
    });
    fireEvent.click(screen.getByText("Register"));

    expect(onRegister).toHaveBeenCalledWith("New Doc", "Body text");
    expect(screen.getByLabelText<HTMLInputElement>("Title").value).toBe("");
  });

  test("submitting a blank form calls neither onRegister nor onUpdate", () => {
    const onRegister = vi.fn();
    render(
      <LocalCorpusPanel
        language="en"
        visible={true}
        state={readyState({ documents: [] })}
        onRefresh={vi.fn()}
        onRegister={onRegister}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
        onEditRequest={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByText("Register"));
    expect(onRegister).not.toHaveBeenCalled();
  });

  test("clicking Edit loads content via onEditRequest, prefills the form, and Update calls onUpdate", async () => {
    const onUpdate = vi.fn();
    const onEditRequest = vi.fn().mockResolvedValue({ title: "研究メモ", content: "既存本文" });
    render(
      <LocalCorpusPanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onRegister={vi.fn()}
        onUpdate={onUpdate}
        onDelete={vi.fn()}
        onEditRequest={onEditRequest}
      />,
    );

    fireEvent.click(screen.getByText("Edit"));
    expect(onEditRequest).toHaveBeenCalledWith(document1.document_id);
    expect(await screen.findByDisplayValue("既存本文")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Update"));
    expect(onUpdate).toHaveBeenCalledWith(document1.document_id, "研究メモ", "既存本文");
  });

  test("clicking Delete calls onDelete with the document id", () => {
    const onDelete = vi.fn();
    render(
      <LocalCorpusPanel
        language="en"
        visible={true}
        state={readyState()}
        onRefresh={vi.fn()}
        onRegister={vi.fn()}
        onUpdate={vi.fn()}
        onDelete={onDelete}
        onEditRequest={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByText("Delete"));
    expect(onDelete).toHaveBeenCalledWith(document1.document_id);
  });
});
