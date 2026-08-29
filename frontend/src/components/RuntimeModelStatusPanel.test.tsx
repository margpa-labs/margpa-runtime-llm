import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import RuntimeModelStatusPanel, { type RuntimeModelControlState } from "./RuntimeModelStatusPanel";
import type { RuntimeModelStatus } from "../types";

const enabledStatus: RuntimeModelStatus = {
  enabled: true,
  configured_startup_model_key: "main.qwen3-4b-q4-k-m",
  revision: 3,
  digest_sha512: "b".repeat(128),
  runtime_state: "active",
  loaded_context_size: 4096,
  model_native_context_limit: 8192,
  backend_context_limit: 8192,
  deployment_verified_context_limit: 8192,
  hardware_verified_context_limit: 8192,
  effective_context_limit: 8192,
  minimum_context_size: 512,
  context_limit_reason_code: "model_native_limit",
  max_output_token_limit: 8191,
  current_max_new_tokens: 1024,
  main_model: {
    model_key: "main.qwen3-4b-q4-k-m",
    artifact_digest: "a".repeat(128),
    backend_identity: "llama_cpp",
    state: "active",
  },
  judge_model: {
    model_key: "main.qwen3-4b-q4-k-m",
    independence_class: "main_self",
    state: "active",
  },
  guard_model: null,
  governance_layer: null,
  available_models: [
    {
      model_key: "main.qwen3-4b-q4-k-m",
      provider: "Qwen",
      native_context_limit: 32768,
      backend_context_limit: 32768,
      hardware_verified_context_limit: 8192,
      effective_context_limit: 8192,
      context_limit_reason_code: "deployment_hardware_verified_limit",
      max_output_token_limit: 8191,
    },
    {
      model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
      provider: "DeepSeek",
      native_context_limit: 131072,
      backend_context_limit: 131072,
      hardware_verified_context_limit: 8192,
      effective_context_limit: 8192,
      context_limit_reason_code: "deployment_hardware_verified_limit",
      max_output_token_limit: 8191,
    },
  ],
};

const disabledStatus: RuntimeModelStatus = {
  enabled: false,
  configured_startup_model_key: null,
  revision: null,
  digest_sha512: null,
  runtime_state: null,
  loaded_context_size: null,
  model_native_context_limit: null,
  backend_context_limit: null,
  deployment_verified_context_limit: null,
  hardware_verified_context_limit: null,
  effective_context_limit: null,
  minimum_context_size: null,
  context_limit_reason_code: null,
  max_output_token_limit: null,
  current_max_new_tokens: null,
  main_model: null,
  judge_model: null,
  guard_model: null,
  governance_layer: null,
  available_models: [],
};

function readyState(status: RuntimeModelStatus = enabledStatus): RuntimeModelControlState {
  return { capability: "ready", status };
}

function renderPanel(
  overrides: {
    visible?: boolean;
    state?: RuntimeModelControlState;
    onRefresh?: () => void;
    onStatusChange?: (status: RuntimeModelStatus) => void;
  } = {},
) {
  return render(
    <RuntimeModelStatusPanel
      language="en"
      visible={overrides.visible ?? true}
      state={overrides.state ?? readyState()}
      onRefresh={overrides.onRefresh ?? vi.fn()}
      onStatusChange={overrides.onStatusChange ?? vi.fn()}
    />,
  );
}

describe("RuntimeModelStatusPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders nothing when not visible and owns no independent fetch", () => {
    vi.stubGlobal("fetch", vi.fn());
    renderPanel({ visible: false });
    expect(document.querySelector("#runtime-model-status-panel")).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });

  test("renders startup default, current main, and main_self Judge from one snapshot", () => {
    renderPanel();
    const details = document.querySelector("#runtime-model-status-details");
    expect(details?.textContent).toContain("Configured Startup Default");
    expect(details?.textContent).toContain("main.qwen3-4b-q4-k-m");
    const judgeLabel = screen.getByText("Current LLM-as-a-Judge Model");
    expect(judgeLabel.nextElementSibling?.textContent).toBe("main.qwen3-4b-q4-k-m");
    expect(screen.getByText("Model Native Context Maximum").nextElementSibling?.textContent).toBe(
      "8192",
    );
    expect(screen.getByText("Effective Context Maximum").nextElementSibling?.textContent).toBe(
      "8192",
    );
    expect(screen.getByText("Current Guardrail Model").nextElementSibling?.textContent).toBe(
      "Not configured",
    );
    expect(document.querySelector("#runtime-model-context-input")).toHaveAttribute("min", "512");
    expect(document.querySelector("#runtime-model-context-input")).toHaveAttribute("max", "8192");
  });

  test("shows only the status line when the feature is disabled server-side", () => {
    renderPanel({ state: readyState(disabledStatus) });
    expect(document.querySelector("#runtime-model-status-details")).toBeNull();
  });

  test("keeps the last verified snapshot visible while a refresh reports failed", () => {
    renderPanel({ state: { capability: "failed", status: enabledStatus } });
    expect(screen.getByText("Model status could not be retrieved safely.")).toBeTruthy();
    expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
  });

  test("context apply posts the current CAS token and returns the canonical snapshot upward", async () => {
    const next = { ...enabledStatus, revision: 4, loaded_context_size: 8192 };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(next) });
    vi.stubGlobal("fetch", fetchMock);
    const onStatusChange = vi.fn();
    renderPanel({ onStatusChange });

    const input = document.querySelector<HTMLInputElement>("#runtime-model-context-input");
    fireEvent.change(input as HTMLInputElement, { target: { value: "8192" } });
    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(onStatusChange).toHaveBeenCalledWith(next);
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, { body: string }];
    expect(url).toBe("/api/v4/runtime-model/context");
    expect(JSON.parse(init.body)).toEqual({
      expected_revision: 3,
      expected_digest: "b".repeat(128),
      requested_context_size: 8192,
    });
  });

  test("failed mutation preserves canonical display and requests a shared-state refresh", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, json: () => Promise.resolve({ code: "conflict" }) }),
    );
    const onRefresh = vi.fn();
    renderPanel({ onRefresh });
    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);
    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalledOnce();
    });
    expect(screen.getByText("Failed to apply.")).toBeTruthy();
    expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
  });

  test("typed limit failure shows the safe server reason and rolls back the input", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: () =>
          Promise.resolve({
            code: "runtime_model_limit_exceeded",
            message:
              "requested context size 8193 is outside the effective range 512..8192 (deployment_hardware_verified_limit)",
          }),
      }),
    );
    const onRefresh = vi.fn();
    renderPanel({ onRefresh });
    const input = document.querySelector<HTMLInputElement>("#runtime-model-context-input");
    fireEvent.change(input as HTMLInputElement, { target: { value: "8193" } });
    fireEvent.click(document.querySelector("#runtime-model-context-apply") as Element);

    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalledOnce();
      expect(input).toHaveValue(4096);
    });
    expect(document.querySelector("#runtime-model-apply-result")?.textContent).toContain(
      "effective range 512..8192",
    );
  });

  test("model switch has no duplicate context input and reuses current context safely", async () => {
    const switched = {
      ...enabledStatus,
      revision: 4,
      main_model: {
        ...enabledStatus.main_model!,
        model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
      },
    };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(switched) });
    vi.stubGlobal("fetch", fetchMock);
    renderPanel();
    const select = document.querySelector<HTMLSelectElement>("#runtime-model-switch-select");
    fireEvent.change(select as HTMLSelectElement, {
      target: { value: "main.deepseek-r1-0528-qwen3-8b-q4-k-m" },
    });
    fireEvent.click(document.querySelector("#runtime-model-switch-apply") as Element);
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledOnce();
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, { body: string }];
    expect(url).toBe("/api/v4/runtime-model/switch");
    expect(JSON.parse(init.body)).toMatchObject({ requested_context_size: 4096 });
    expect(document.querySelector("#runtime-model-switch-context-input")).toBeNull();
  });

  test("model switch uses the target effective limit rather than its native metadata maximum", async () => {
    const limitedTargetStatus: RuntimeModelStatus = {
      ...enabledStatus,
      available_models: enabledStatus.available_models.map((model) =>
        model.model_key.includes("deepseek")
          ? { ...model, effective_context_limit: 2048, hardware_verified_context_limit: 2048 }
          : model,
      ),
    };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(enabledStatus) });
    vi.stubGlobal("fetch", fetchMock);
    renderPanel({ state: readyState(limitedTargetStatus) });
    const select = document.querySelector<HTMLSelectElement>("#runtime-model-switch-select");
    fireEvent.change(select as HTMLSelectElement, {
      target: { value: "main.deepseek-r1-0528-qwen3-8b-q4-k-m" },
    });
    fireEvent.click(document.querySelector("#runtime-model-switch-apply") as Element);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledOnce();
    });
    const [, init] = fetchMock.mock.calls[0] as [string, { body: string }];
    expect(JSON.parse(init.body)).toMatchObject({ requested_context_size: 2048 });
  });

  test("failed model switch rolls the selector back to the canonical model before refresh", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, json: () => Promise.resolve({ code: "load_failed" }) }),
    );
    const onRefresh = vi.fn();
    renderPanel({ onRefresh });
    const select = document.querySelector<HTMLSelectElement>("#runtime-model-switch-select");
    fireEvent.change(select as HTMLSelectElement, {
      target: { value: "main.deepseek-r1-0528-qwen3-8b-q4-k-m" },
    });
    fireEvent.click(document.querySelector("#runtime-model-switch-apply") as Element);

    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalledOnce();
      expect(select).toHaveValue("main.qwen3-4b-q4-k-m");
    });
  });

  test("max new tokens apply is explicit and reports the canonical result upward", async () => {
    const next = { ...enabledStatus, revision: 4, current_max_new_tokens: 2048 };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(next) });
    vi.stubGlobal("fetch", fetchMock);
    const onStatusChange = vi.fn();
    renderPanel({ onStatusChange });
    const input = document.querySelector<HTMLInputElement>("#runtime-model-max-new-tokens-input");
    fireEvent.change(input as HTMLInputElement, { target: { value: "2048" } });
    fireEvent.click(document.querySelector("#runtime-model-max-new-tokens-apply") as Element);
    await waitFor(() => {
      expect(onStatusChange).toHaveBeenCalledWith(next);
    });
  });
});
