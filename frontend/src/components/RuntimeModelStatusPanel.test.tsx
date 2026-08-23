import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import RuntimeModelStatusPanel from "./RuntimeModelStatusPanel";
import type { RuntimeModelStatus } from "../types";

const enabledStatus: RuntimeModelStatus = {
  enabled: true,
  revision: 3,
  digest_sha512: "b".repeat(128),
  runtime_state: "active",
  loaded_context_size: 4096,
  model_native_context_limit: 8192,
  backend_context_limit: 8192,
  deployment_verified_context_limit: 8192,
  max_output_token_limit: 2048,
  current_max_new_tokens: 1024,
  main_model: {
    model_key: "main.qwen3-4b-q4-k-m",
    artifact_digest: "a".repeat(128),
    backend_identity: "llama_cpp",
    state: "active",
  },
  judge_model: null,
  guard_model: null,
  governance_layer: null,
  available_models: [
    { model_key: "main.qwen3-4b-q4-k-m", provider: "Qwen", native_context_limit: 32768 },
    {
      model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
      provider: "DeepSeek",
      native_context_limit: 131072,
    },
  ],
};

const disabledStatus: RuntimeModelStatus = {
  enabled: false,
  revision: null,
  digest_sha512: null,
  runtime_state: null,
  loaded_context_size: null,
  model_native_context_limit: null,
  backend_context_limit: null,
  deployment_verified_context_limit: null,
  max_output_token_limit: null,
  current_max_new_tokens: null,
  main_model: null,
  judge_model: null,
  guard_model: null,
  governance_layer: null,
  available_models: [],
};

function mockFetchOnce(body: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      json: () => Promise.resolve(body),
    }),
  );
}

describe("RuntimeModelStatusPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders nothing when not visible, and issues no fetch", () => {
    mockFetchOnce(enabledStatus);
    render(<RuntimeModelStatusPanel language="en" visible={false} />);
    expect(document.querySelector("#runtime-model-status-panel")).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });

  test("renders the bound snapshot once loaded", async () => {
    mockFetchOnce(enabledStatus);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });
    // The Switch selector also lists "main.qwen3-4b-q4-k-m" as an <option>,
    // so this must be scoped to the status details list specifically.
    const details = document.querySelector("#runtime-model-status-details");
    expect(details).not.toBeNull();
    expect(details?.textContent).toContain("main.qwen3-4b-q4-k-m");
    // Judge Model and Governance Layer share the same "Not configured"
    // fallback text when both are None; assert count rather than uniqueness.
    expect(screen.getAllByText("Not configured")).toHaveLength(2);
  });

  test("P6-CODEX-005: renders all four Component Identity rows, Guard/Governance honestly None", async () => {
    mockFetchOnce(enabledStatus);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });
    expect(screen.getByText("Current Guardrail Model")).toBeTruthy();
    expect(screen.getByText("Not configured (Rule/Pattern-based detection)")).toBeTruthy();
    expect(screen.getByText("Current Governance Layer")).toBeTruthy();
  });

  test("shows only the status line when the feature is disabled server-side", async () => {
    mockFetchOnce(disabledStatus);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-line")).not.toBeNull();
    });
    expect(document.querySelector("#runtime-model-status-details")).toBeNull();
  });

  test("degrades to a failed status line on a network error, without throwing", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(screen.getByText("Model status could not be retrieved safely.")).toBeTruthy();
    });
  });

  test("applying a new context size posts the current CAS token and updates the display", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enabledStatus) })
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({ ...enabledStatus, revision: 4, loaded_context_size: 8192 }),
      });
    vi.stubGlobal("fetch", fetchMock);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    const input = document.querySelector<HTMLInputElement>("#runtime-model-context-input");
    expect(input?.value).toBe("4096");
    fireEvent.change(input as HTMLInputElement, { target: { value: "8192" } });
    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(screen.getByText("Applied.")).toBeTruthy();
    });
    const secondCall = fetchMock.mock.calls[1];
    expect(secondCall).toBeDefined();
    const [url, init] = secondCall as [string, { body: string }];
    expect(url).toBe("/api/v4/runtime-model/context");
    const body = JSON.parse(init.body) as Record<string, unknown>;
    expect(body).toEqual({
      expected_revision: 3,
      expected_digest: "b".repeat(128),
      requested_context_size: 8192,
    });
  });

  test("a failed context apply shows the failure text without crashing", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enabledStatus) })
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ code: "runtime_model_revision_conflict" }),
      });
    vi.stubGlobal("fetch", fetchMock);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(screen.getByText("Failed to apply.")).toBeTruthy();
    });
  });

  test("a stale CAS conflict re-syncs the digest so a retry can succeed, without losing the failure message", async () => {
    const conflictedStatus: RuntimeModelStatus = {
      ...enabledStatus,
      revision: 4,
      digest_sha512: "c".repeat(128),
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enabledStatus) })
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ code: "runtime_model_revision_conflict" }),
      })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(conflictedStatus) });
    vi.stubGlobal("fetch", fetchMock);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(screen.getByText("Failed to apply.")).toBeTruthy();
    });
    // The failed-apply message must still be visible after the silent
    // resync, and the Panel must not have been wiped back to a bare
    // "loading"/"failed" state by the secondary fetch.
    expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  test("switching the model posts the target key and the current CAS token", async () => {
    const switchedStatus: RuntimeModelStatus = {
      ...enabledStatus,
      revision: 4,
      main_model: {
        model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        artifact_digest: "d".repeat(128),
        backend_identity: "llama_cpp",
        state: "active",
      },
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enabledStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(switchedStatus) });
    vi.stubGlobal("fetch", fetchMock);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    const select = document.querySelector<HTMLSelectElement>("#runtime-model-switch-select");
    fireEvent.change(select as HTMLSelectElement, {
      target: { value: "main.deepseek-r1-0528-qwen3-8b-q4-k-m" },
    });
    fireEvent.click(document.querySelector("#runtime-model-switch-apply") as Element);

    await waitFor(() => {
      expect(screen.getByText("Applied.")).toBeTruthy();
    });
    const secondCall = fetchMock.mock.calls[1];
    const [url, init] = secondCall as [string, { body: string }];
    expect(url).toBe("/api/v4/runtime-model/switch");
    const body = JSON.parse(init.body) as Record<string, unknown>;
    expect(body).toEqual({
      expected_revision: 3,
      expected_digest: "b".repeat(128),
      target_model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
      requested_context_size: 4096,
    });
  });

  test("the switch button is disabled while the selected target is already the active model", async () => {
    mockFetchOnce(enabledStatus);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    const button = document.querySelector<HTMLButtonElement>("#runtime-model-switch-apply");
    expect(button?.disabled).toBe(true);
  });

  test("a failed resync after Apply does not clear the already-shown Panel or failure text", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enabledStatus) })
      .mockResolvedValueOnce({ ok: false, json: () => Promise.resolve({ code: "conflict" }) })
      .mockRejectedValueOnce(new Error("network down"));
    vi.stubGlobal("fetch", fetchMock);
    render(<RuntimeModelStatusPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(screen.getByText("Failed to apply.")).toBeTruthy();
    });
    expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
  });
});
