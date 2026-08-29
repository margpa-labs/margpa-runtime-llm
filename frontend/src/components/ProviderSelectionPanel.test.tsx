import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import type { ProviderSelectionStatus } from "../types";
import ProviderSelectionPanel from "./ProviderSelectionPanel";
import { mergeProviderSelectionStatus } from "./providerSelectionState";

const statusV1: ProviderSelectionStatus = {
  enabled: true,
  revision: 1,
  digest_sha512: "a".repeat(128),
  selections: [
    {
      role: "main",
      configured_provider: "main.qwen",
      active_provider: "main.qwen",
      state: "active",
      independence: "self",
      failure_reason: null,
      failure_at: null,
      budget: null,
    },
    {
      role: "guard",
      configured_provider: "guard.qwen3guard",
      active_provider: null,
      state: "configured",
      independence: "independent_other_model",
      failure_reason: null,
      failure_at: null,
      budget: {
        profile_id: "guard-budget",
        verification_state: "configured_not_hardware_verified",
        load_budget_ms: 180000,
        prompt_build_budget_ms: 5000,
        inference_budget_ms: 120000,
        decode_budget_ms: 5000,
        repair_generation_budget_ms: 180000,
        rejudge_budget_ms: 120000,
        cancel_grace_ms: 10000,
      },
    },
    {
      role: "judge",
      configured_provider: "judge.selene",
      active_provider: null,
      state: "configured",
      independence: "independent_other_model",
      failure_reason: "artifact_unavailable",
      failure_at: "2026-08-28T20:16:00+00:00",
      budget: {
        profile_id: "judge-budget",
        verification_state: "configured_not_hardware_verified",
        load_budget_ms: 180000,
        prompt_build_budget_ms: 5000,
        inference_budget_ms: 120000,
        decode_budget_ms: 5000,
        repair_generation_budget_ms: 180000,
        rejudge_budget_ms: 120000,
        cancel_grace_ms: 10000,
      },
    },
  ],
  options: [
    {
      provider_id: "main.qwen",
      role: "main",
      kind: "model",
      display_name: "Qwen",
      enabled: true,
      model_key: "main.qwen",
    },
    {
      provider_id: "main.deepseek",
      role: "main",
      kind: "model",
      display_name: "DeepSeek",
      enabled: true,
      model_key: "main.deepseek",
    },
    {
      provider_id: "none",
      role: "guard",
      kind: "none",
      display_name: "None",
      enabled: true,
      model_key: null,
    },
    {
      provider_id: "built_in.rule_pattern",
      role: "guard",
      kind: "built_in",
      display_name: "Built-in Rule / Pattern",
      enabled: true,
      model_key: null,
    },
    {
      provider_id: "guard.qwen3guard",
      role: "guard",
      kind: "model",
      display_name: "Qwen3Guard",
      enabled: true,
      model_key: "guard.qwen3guard",
    },
    {
      provider_id: "none",
      role: "judge",
      kind: "none",
      display_name: "None",
      enabled: true,
      model_key: null,
    },
    {
      provider_id: "built_in.deterministic",
      role: "judge",
      kind: "built_in",
      display_name: "Built-in Deterministic",
      enabled: true,
      model_key: null,
    },
    {
      provider_id: "judge.selene",
      role: "judge",
      kind: "model",
      display_name: "Selene",
      enabled: true,
      model_key: "judge.selene",
    },
  ],
};

function withSelection(
  base: ProviderSelectionStatus,
  role: "main" | "guard" | "judge",
  configuredProvider: string,
  revision: number,
): ProviderSelectionStatus {
  return {
    ...base,
    revision,
    digest_sha512: String(revision).repeat(128).slice(0, 128),
    selections: base.selections.map((selection) =>
      selection.role === role
        ? {
            ...selection,
            configured_provider: configuredProvider,
            active_provider: null,
            state: configuredProvider === "none" ? "none" : "configured",
          }
        : selection,
    ),
  };
}

describe("ProviderSelectionPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders three role dropdowns and configured/active/state/independence/budget", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(statusV1) }),
    );
    render(<ProviderSelectionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#provider-selection-main-select")).not.toBeNull();
    });
    expect(document.querySelector("#provider-selection-guard-select")).not.toBeNull();
    expect(document.querySelector("#provider-selection-judge-select")).not.toBeNull();
    const judgeText = document.querySelector("#provider-selection-judge")?.textContent;
    expect(judgeText).toContain("judge.selene");
    expect(judgeText).toContain("none");
    expect(judgeText).toContain("configured");
    expect(judgeText).toContain("independent_other_model");
    expect(judgeText).toContain("configured_not_hardware_verified");
    expect(judgeText).toContain("artifact_unavailable");
    expect(judgeText).toContain("2026-08-28T20:16:00+00:00");
  });

  test("serializes two-tab-like rapid changes and uses the latest CAS revision", async () => {
    const statusV2 = withSelection(statusV1, "judge", "built_in.deterministic", 2);
    const statusV3 = withSelection(statusV2, "guard", "built_in.rule_pattern", 3);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(statusV1) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(statusV2) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(statusV3) });
    vi.stubGlobal("fetch", fetchMock);
    render(<ProviderSelectionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#provider-selection-judge-select")).not.toBeNull();
    });
    fireEvent.change(document.querySelector("#provider-selection-judge-select") as Element, {
      target: { value: "built_in.deterministic" },
    });
    fireEvent.change(document.querySelector("#provider-selection-guard-select") as Element, {
      target: { value: "built_in.rule_pattern" },
    });
    await waitFor(() => {
      expect(document.querySelector("#provider-selection-revision")?.textContent).toContain("3");
    });
    const firstCall = fetchMock.mock.calls[1];
    const secondCall = fetchMock.mock.calls[2];
    expect(firstCall).toBeDefined();
    expect(secondCall).toBeDefined();
    const firstPut = JSON.parse((firstCall?.[1] as RequestInit).body as string) as {
      expected_revision: number;
    };
    const secondPut = JSON.parse((secondCall?.[1] as RequestInit).body as string) as {
      expected_revision: number;
    };
    expect(firstPut.expected_revision).toBe(1);
    expect(secondPut.expected_revision).toBe(2);
  });

  test("stale response cannot roll back a newer canonical revision", () => {
    const statusV2 = withSelection(statusV1, "judge", "built_in.deterministic", 2);
    expect(mergeProviderSelectionStatus(statusV2, statusV1)).toBe(statusV2);
  });

  test("CAS conflict shows typed reason and reloads server canonical state", async () => {
    const canonical = withSelection(statusV1, "judge", "built_in.deterministic", 4);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(statusV1) })
      .mockResolvedValueOnce({
        ok: false,
        json: () =>
          Promise.resolve({
            code: "provider_selection_revision_conflict",
            message: "The provider selection changed; reload and retry.",
          }),
      })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(canonical) });
    vi.stubGlobal("fetch", fetchMock);
    render(<ProviderSelectionPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#provider-selection-judge-select")).not.toBeNull();
    });
    fireEvent.change(document.querySelector("#provider-selection-judge-select") as Element, {
      target: { value: "none" },
    });
    await waitFor(() => {
      expect(screen.getByText(/provider_selection_revision_conflict/)).toBeTruthy();
    });
    expect(document.querySelector("#provider-selection-revision")?.textContent).toContain("4");
    expect(document.querySelector("#provider-selection-judge-select")).toHaveValue(
      "built_in.deterministic",
    );
  });
});
