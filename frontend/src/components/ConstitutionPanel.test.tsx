import { render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import type { ConstitutionModePreview, ConstitutionRuntime } from "../types";
import ConstitutionPanel from "./ConstitutionPanel";

const runtimeV1: ConstitutionRuntime = {
  revision: 1,
  digest_sha512: "a".repeat(128),
  rule_count: 2,
  views: [
    { view: "chat", mode: "observe", rule_ids: ["no-secrets-in-external-evidence"] },
    { view: "agent", mode: "off", rule_ids: [] },
    { view: "tool", mode: "enforce", rule_ids: ["external-write-requires-human-gate"] },
  ],
};

const previewV1: ConstitutionModePreview = {
  revision: 1,
  digest_sha512: "a".repeat(128),
  is_preview: true,
  active_production_mode: "off",
  views: [
    {
      view: "chat",
      modes: [
        {
          mode: "off",
          rule_ids: ["no-secrets-in-external-evidence"],
          decisions: [],
          evaluation_disposition: "not_evaluated",
          action_permission: "no_constitution_action",
          violation_presentation: "not_evaluated",
        },
        {
          mode: "observe",
          rule_ids: ["no-secrets-in-external-evidence"],
          decisions: [
            {
              rule_id: "no-secrets-in-external-evidence",
              mode: "observe",
              outcome: "unsupported_action",
              reason: "This Bounded Resolver has no executable logic for this Rule yet.",
            },
          ],
          evaluation_disposition: "evaluate_record_only",
          action_permission: "no_block_no_authority_change",
          violation_presentation: "typed_unsupported",
        },
        {
          mode: "enforce",
          rule_ids: ["no-secrets-in-external-evidence"],
          decisions: [
            {
              rule_id: "no-secrets-in-external-evidence",
              mode: "enforce",
              outcome: "unsupported_action",
              reason: "This Bounded Resolver has no executable logic for this Rule yet.",
            },
          ],
          evaluation_disposition: "evaluate_and_apply_supported_action",
          action_permission: "supported_actions_only_no_authority_expansion",
          violation_presentation: "typed_unsupported",
        },
      ],
    },
    { view: "agent", modes: [] },
    { view: "tool", modes: [] },
  ],
};

function stubFetchByUrl(): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn((url: string) => {
    if (url.includes("/preview")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(previewV1) });
    }
    if (url.includes("/runtime")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(runtimeV1) });
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("ConstitutionPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders nothing when not visible, even without a fetch", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<ConstitutionPanel language="en" visible={false} />);
    expect(document.querySelector("#constitution-panel")).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("renders revision, shortened digest, rule count, and per-view mode/rule_ids", async () => {
    stubFetchByUrl();
    render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-manifest-summary")).not.toBeNull();
    });
    const summaryText = document.querySelector("#constitution-manifest-summary")?.textContent;
    expect(summaryText).toContain("1");
    expect(summaryText).toContain("2");
    expect(summaryText).not.toContain("a".repeat(128));
    const viewsText = document.querySelector("#constitution-views")?.textContent;
    expect(viewsText).toContain("chat");
    expect(viewsText).toContain("OBSERVE");
    expect(viewsText).toContain("agent");
    expect(viewsText).toContain("OFF");
    expect(viewsText).toContain("tool");
    expect(viewsText).toContain("ENFORCE");
  });

  test("a failed fetch degrades to silently absent, not an error banner", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }));
    const { container } = render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(container.textContent).toBe("");
    });
    expect(document.querySelector("#constitution-panel")).toBeNull();
  });

  // -- P8-MR4 (P8-MANUAL-004): Mode Name Header layout ----------------------

  test("renders the Mode Name as its own Header, structurally separate from the 3-axis detail rows", async () => {
    stubFetchByUrl();
    render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-preview")).not.toBeNull();
    });

    const offRow = document.querySelector(".constitution-preview-mode-off");
    const heading = offRow?.querySelector("h5.constitution-preview-mode-name");
    expect(heading).not.toBeNull();
    expect(heading?.textContent).toBe("off");
    // Decision/Evaluation/Action Permission/Violation Presentation must
    // live in their own details block, never inside the Header itself —
    // the exact bug the User reported (Mode Name and Decision packed onto
    // one line).
    expect(heading?.querySelector(".constitution-preview-mode-decisions")).toBeNull();
    const details = offRow?.querySelector(".constitution-preview-mode-details");
    expect(details).not.toBeNull();
    expect(details?.querySelector(".constitution-preview-mode-decisions")).not.toBeNull();
    expect(
      details?.querySelector(".constitution-preview-mode-evaluation-disposition"),
    ).not.toBeNull();
    expect(details?.querySelector(".constitution-preview-mode-action-permission")).not.toBeNull();
    expect(
      details?.querySelector(".constitution-preview-mode-violation-presentation"),
    ).not.toBeNull();
  });

  // -- P8-RW6-D (P8-CODEX-008): Constitution Mode Comparison Preview -------

  test("renders the non-Activation Preview comparing all three Modes, with an explicit disclaimer", async () => {
    stubFetchByUrl();
    render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-preview")).not.toBeNull();
    });

    const disclaimer = document.querySelector("#constitution-preview-disclaimer")?.textContent;
    expect(disclaimer).toContain("Preview");
    expect(disclaimer).toContain("not the Active Runtime Mode");

    const activeMode = document.querySelector("#constitution-preview-active-mode")?.textContent;
    expect(activeMode).toContain("off");

    const chatView = document.querySelector("#constitution-preview-view-chat")?.textContent;
    expect(chatView).toContain("off");
    expect(chatView).toContain("observe");
    expect(chatView).toContain("enforce");
    expect(chatView).toContain("unsupported_action");
  });

  // -- P8-RW7-B (P8-CODEX-012): 3-axis comparison display -------------------

  test("renders Evaluation, Action Permission, and Violation Presentation per Mode (en)", async () => {
    stubFetchByUrl();
    render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-preview")).not.toBeNull();
    });

    const chatView = document.querySelector("#constitution-preview-view-chat")?.textContent;
    // OFF: no Constitution Action, nothing evaluated.
    expect(chatView).toContain("No Constitution Action");
    // OBSERVE: recorded only, no block/Authority change, honestly typed
    // unsupported (today's real Rule has no executable logic yet).
    expect(chatView).toContain("Evaluate & record only (no block)");
    expect(chatView).toContain("No block, no Authority change");
    expect(chatView).toContain("Typed unsupported");
    // ENFORCE: supported Actions only, no Authority expansion.
    expect(chatView).toContain("Supported Actions only, no Authority expansion");
  });

  test("renders Evaluation, Action Permission, and Violation Presentation per Mode (ja)", async () => {
    stubFetchByUrl();
    render(<ConstitutionPanel language="ja" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-preview")).not.toBeNull();
    });

    const chatView = document.querySelector("#constitution-preview-view-chat")?.textContent;
    expect(chatView).toContain("Constitution由来のActionなし");
    expect(chatView).toContain("評価して記録のみ（Blockしない）");
    expect(chatView).toContain("Blockなし・Authority変更なし");
    expect(chatView).toContain("未対応（Typed Unsupported）");
    expect(chatView).toContain("対応済みActionのみ・Authority拡張なし");
  });

  test("a failed Preview fetch never hides the already-working Runtime section", async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes("/preview")) {
        return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
      }
      if (url.includes("/runtime")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(runtimeV1) });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ConstitutionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#constitution-manifest-summary")).not.toBeNull();
    });
    expect(document.querySelector("#constitution-preview")).toBeNull();
  });
});
