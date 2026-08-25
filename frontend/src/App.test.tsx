import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import App from "./App";
import type { RuntimeInfo, RuntimeModelStatus } from "./types";

const RUNTIME_INFO: RuntimeInfo = {
  model_key: "main.qwen3-4b-q4-k-m",
  profile_key: "local.macos-arm64",
  device_kind: "gpu",
  acceleration_api: "metal",
  defaults: {
    response_language: "ja",
    max_new_tokens: 2048,
    thinking_mode: "disabled",
    thinking_visibility: "hidden",
    thinking_control_available: false,
    summary_mode: "off",
    documentation_rag_mode: "disabled",
  },
  documentation_rag: {
    effective_state: "unavailable",
    control_available: false,
    provider_display_name: null,
    default_mode: "disabled",
  },
};

const RUNTIME_MODEL_STATUS: RuntimeModelStatus = {
  enabled: true,
  configured_startup_model_key: "main.qwen3-4b-q4-k-m",
  revision: 7,
  digest_sha512: "d".repeat(128),
  runtime_state: "active",
  loaded_context_size: 8192,
  model_native_context_limit: 131072,
  backend_context_limit: 131072,
  deployment_verified_context_limit: 8192,
  hardware_verified_context_limit: 8192,
  effective_context_limit: 8192,
  minimum_context_size: 512,
  context_limit_reason_code: "deployment_hardware_verified_limit",
  max_output_token_limit: 8191,
  current_max_new_tokens: 1024,
  main_model: {
    model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
    artifact_digest: "a".repeat(128),
    backend_identity: "llama_cpp",
    state: "active",
  },
  judge_model: {
    model_key: "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
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

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

function setBootstrapTag(enabled: boolean): void {
  document.head.querySelector("#configuration-bootstrap")?.remove();
  const script = document.createElement("script");
  script.id = "configuration-bootstrap";
  script.type = "application/json";
  script.textContent = JSON.stringify({ enabled });
  document.head.appendChild(script);
}

function setGovernanceBootstrapTag(enabled: boolean): void {
  document.head.querySelector("#governance-bootstrap")?.remove();
  const script = document.createElement("script");
  script.id = "governance-bootstrap";
  script.type = "application/json";
  script.textContent = JSON.stringify({ enabled });
  document.head.appendChild(script);
}

function setRuntimeGovernanceBootstrapTag(enabled: boolean): void {
  document.head.querySelector("#runtime-governance-bootstrap")?.remove();
  const script = document.createElement("script");
  script.id = "runtime-governance-bootstrap";
  script.type = "application/json";
  script.textContent = JSON.stringify({ enabled });
  document.head.appendChild(script);
}

function setRuntimeModelControlBootstrapTag(enabled: boolean): void {
  document.head.querySelector("#runtime-model-control-bootstrap")?.remove();
  const script = document.createElement("script");
  script.id = "runtime-model-control-bootstrap";
  script.type = "application/json";
  script.textContent = JSON.stringify({ enabled });
  document.head.appendChild(script);
}

function pathOf(input: RequestInfo | URL): string {
  const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
  return url.split("?")[0] ?? url;
}

function sseStreamResponse(events: { type: string; data: unknown }[]): Response {
  const encoder = new TextEncoder();
  const body = events.map((event) => `event: ${event.type}\ndata: ${JSON.stringify(event.data)}\n\n`).join("");
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

interface FetchRoutes {
  persistentRuntime?: { enabled: boolean; source_of_truth: string };
  persistentList?: { items: { conversation_id: string; updated_at: string; state: string }[]; next_cursor: null };
  configurationRuntime?: { enabled: boolean; non_persistent: boolean };
  configurationEffective?: unknown;
  governanceRuntime?: unknown;
  runtimeGovernanceStatus?: unknown;
  featureModesStatus?: unknown;
  runtimeModelStatus?: RuntimeModelStatus | (() => RuntimeModelStatus);
  chatStream?: Response;
  persistentTurnStream?: Response;
  persistentDerivedStream?: Response;
  conversationDetail?: Record<
    string,
    { storage_revision: number; state: string; turns?: unknown[]; head_turn_id?: string | null }
  >;
  mutation?: (
    path: string,
    body: { expected_revision?: number },
  ) => Response | Promise<Response>;
}

function detailPayload(
  conversationId: string,
  storageRevision: number,
  state: string,
  turns: unknown[] = [],
  headTurnId: string | null = null,
): unknown {
  return {
    conversation_id: conversationId,
    state,
    storage_revision: storageRevision,
    head_turn_id: headTurnId,
    turns,
    sessions: [],
  };
}

function installFetchMock(routes: FetchRoutes): ReturnType<typeof vi.fn> {
  const mock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const path = pathOf(input);
    const method = init?.method ?? "GET";
    if (path === "/api/v1/runtime") {
      return Promise.resolve(jsonResponse(RUNTIME_INFO));
    }
    if (path === "/api/v5/feature-modes/status") {
      // P6-CODEX-024: App's own background Live Judge/Repair badge poll
      // hits this unconditionally once a Turn starts — a harmless "not
      // enabled" default here keeps every pre-existing test route-complete
      // without each one needing to know about this unrelated feature.
      return Promise.resolve(
        jsonResponse(
          routes.featureModesStatus ?? {
            judge: { enabled: false, revision: null, current_mode: null, state: null, current_request_id: null, last_result: null },
            repair: { enabled: false, revision: null, current_mode: null },
            recording: { enabled: false, revision: null, current_mode: null, last_outcome: null, judge_evidence_last_outcome: null },
          },
        ),
      );
    }
    if (path === "/api/v4/runtime-model/status") {
      const configured = routes.runtimeModelStatus ?? RUNTIME_MODEL_STATUS;
      const status = typeof configured === "function" ? configured() : configured;
      return Promise.resolve(jsonResponse(status));
    }
    if (path === "/api/v2/conversations/runtime") {
      return Promise.resolve(jsonResponse(routes.persistentRuntime ?? { enabled: false, source_of_truth: "server" }));
    }
    if (path === "/api/v2/conversations" && method === "GET") {
      return Promise.resolve(jsonResponse(routes.persistentList ?? { items: [], next_cursor: null }));
    }
    if (path === "/api/v2/configuration/runtime") {
      return Promise.resolve(
        jsonResponse(routes.configurationRuntime ?? { enabled: false, non_persistent: true }),
      );
    }
    if (path === "/api/v2/configuration/effective") {
      return Promise.resolve(jsonResponse(routes.configurationEffective ?? {}));
    }
    if (path === "/api/v3/governance/runtime") {
      return Promise.resolve(
        jsonResponse(
          routes.governanceRuntime ?? {
            mode: {
              revision: 1,
              digest_sha512: "gov123",
              current_mode: "off",
              descriptors: [
                { mode: "off", availability: "available", apply_disposition: "hot", unavailable_reason_code: null },
                {
                  mode: "observe",
                  availability: "available",
                  apply_disposition: "hot",
                  unavailable_reason_code: null,
                },
                {
                  mode: "enforce",
                  availability: "unavailable",
                  apply_disposition: "rejected",
                  unavailable_reason_code: "phase_3_enforce_unavailable",
                },
              ],
            },
            observe_summary: null,
          },
        ),
      );
    }
    if (path === "/api/v3/runtime-governance/status") {
      return Promise.resolve(
        jsonResponse(
          routes.runtimeGovernanceStatus ?? {
            enabled: true,
            revision: 1,
            current_mode: "off",
            descriptors: [
              { mode: "off", availability: "available", unavailable_reason_code: null },
              { mode: "observe", availability: "available", unavailable_reason_code: null },
              { mode: "enforce", availability: "unavailable", unavailable_reason_code: "no_definitions" },
            ],
            points: [],
            evidence: null,
          },
        ),
      );
    }
    if (path === "/api/v1/chat/stream" && method === "POST" && routes.chatStream !== undefined) {
      return Promise.resolve(routes.chatStream);
    }
    const turnStreamMatch = /^\/api\/v2\/conversations\/([^/]+)\/turns\/stream$/u.exec(path);
    if (turnStreamMatch !== null && method === "POST" && routes.persistentTurnStream !== undefined) {
      return Promise.resolve(routes.persistentTurnStream);
    }
    const derivedStreamMatch =
      /^\/api\/v2\/conversations\/([^/]+)\/turns\/([^/]+)\/(?:retry|regenerate)\/stream$/u.exec(path);
    if (derivedStreamMatch !== null && method === "POST" && routes.persistentDerivedStream !== undefined) {
      return Promise.resolve(routes.persistentDerivedStream);
    }
    const detailMatch = /^\/api\/v2\/conversations\/([^/]+)$/u.exec(path);
    if (detailMatch !== null && method === "GET" && routes.conversationDetail !== undefined) {
      const conversationId = detailMatch[1] ?? "";
      const entry = routes.conversationDetail[conversationId];
      if (entry !== undefined) {
        return Promise.resolve(
          jsonResponse(
            detailPayload(
              conversationId,
              entry.storage_revision,
              entry.state,
              entry.turns ?? [],
              entry.head_turn_id ?? null,
            ),
          ),
        );
      }
    }
    if (method === "POST" && routes.mutation !== undefined) {
      const body =
        typeof init?.body === "string"
          ? (JSON.parse(init.body) as { expected_revision?: number })
          : {};
      return Promise.resolve(routes.mutation(path, body));
    }
    throw new Error(`Unhandled fetch in test: ${method} ${path}`);
  });
  vi.stubGlobal("fetch", mock);
  return mock;
}

describe("App", () => {
  beforeEach(() => {
    setBootstrapTag(false);
    setGovernanceBootstrapTag(false);
    setRuntimeGovernanceBootstrapTag(false);
    setRuntimeModelControlBootstrapTag(false);
    // The app defaults to Japanese; pin English so assertions below can use
    // one fixed set of expected strings.
    window.localStorage.setItem("margpa.ui_language.v1", "en");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    document.head.querySelector("#configuration-bootstrap")?.remove();
    document.head.querySelector("#governance-bootstrap")?.remove();
    document.head.querySelector("#runtime-governance-bootstrap")?.remove();
    document.head.querySelector("#runtime-model-control-bootstrap")?.remove();
    window.localStorage.clear();
  });

  test("never silently falls back to ephemeral or persistent when capability negotiation reports an invalid runtime", async () => {
    installFetchMock({ persistentRuntime: { enabled: true, source_of_truth: "client" } });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("The conversation mode could not be determined safely.")).toBeInTheDocument();
    });
    expect(document.querySelectorAll(".chat-list-item")).toHaveLength(0);
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  test("persistent mode loads the conversation list and shows it in the sidebar when the server enables it", async () => {
    installFetchMock({
      persistentRuntime: { enabled: true, source_of_truth: "server" },
      persistentList: {
        items: [{ conversation_id: "conversation-abcdef", updated_at: "2024-01-01T00:00:00Z", state: "active" }],
        next_cursor: null,
      },
    });

    render(<App />);

    await waitFor(() => {
      expect(document.querySelectorAll(".chat-list-item")).toHaveLength(1);
    });
    expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
  });

  test("ephemeral mode is used, and the conversation list is never fetched, when persistent is server-disabled", async () => {
    const fetchMock = installFetchMock({ persistentRuntime: { enabled: false, source_of_truth: "server" } });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
    expect(document.querySelectorAll(".chat-list-item")).toHaveLength(0);
    expect(fetchMock.mock.calls.some((call) => pathOf(call[0] as RequestInfo) === "/api/v2/conversations")).toBe(
      false,
    );
  });

  test("configuration control stays out of the DOM and unfetched when the bootstrap tag reports disabled", async () => {
    const fetchMock = installFetchMock({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
    });
    expect(document.querySelector("#configuration-panel")).toBeNull();
    expect(
      fetchMock.mock.calls.some((call) => pathOf(call[0] as RequestInfo).startsWith("/api/v2/configuration")),
    ).toBe(false);
  });

  test("configuration control loads once the bootstrap tag reports enabled", async () => {
    setBootstrapTag(true);
    installFetchMock({
      configurationRuntime: { enabled: true, non_persistent: true },
      configurationEffective: {
        schema_version: "1",
        revision: 1,
        digest_sha512: "abc123",
        fields: [{ key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" }],
        feature_hooks: [],
        recording_hooks: [],
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    await waitFor(() => {
      expect(document.querySelector("#configuration-panel")).not.toBeNull();
    });
    expect(screen.getByText("Runtime configuration control")).toBeInTheDocument();
  });

  test("projects one canonical runtime-model snapshot into Sidebar and Advanced status", async () => {
    setRuntimeModelControlBootstrapTag(true);
    installFetchMock({ runtimeModelStatus: RUNTIME_MODEL_STATUS });

    render(<App />);

    await waitFor(() => {
      expect(document.querySelector("#runtime-status")?.textContent).toBe(
        "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
      );
    });
    expect(document.querySelector(".sidebar-title-block")?.textContent).toContain("Context 8192");

    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")).not.toBeNull();
    });
    const details = document.querySelector("#runtime-model-status-details");
    expect(details?.textContent).toContain("main.qwen3-4b-q4-k-m");
    expect(details?.textContent).toContain("main.deepseek-r1-0528-qwen3-8b-q4-k-m");
    expect(screen.getByText("Current LLM-as-a-Judge Model")).toBeInTheDocument();
    expect(document.querySelector("#runtime-model-context-input")).toHaveValue(8192);
  });

  test("a canonical refresh converges Sidebar and Advanced after another tab changes the model", async () => {
    setRuntimeModelControlBootstrapTag(true);
    const nextStatus: RuntimeModelStatus = {
      ...RUNTIME_MODEL_STATUS,
      revision: 8,
      digest_sha512: "e".repeat(128),
      loaded_context_size: 4096,
      main_model: {
        ...RUNTIME_MODEL_STATUS.main_model!,
        model_key: "main.qwen3-4b-q4-k-m",
      },
      judge_model: {
        ...RUNTIME_MODEL_STATUS.judge_model!,
        model_key: "main.qwen3-4b-q4-k-m",
      },
    };
    let statusReadCount = 0;
    installFetchMock({
      runtimeModelStatus: () => {
        statusReadCount += 1;
        return statusReadCount === 1 ? RUNTIME_MODEL_STATUS : nextStatus;
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-status")?.textContent).toContain("deepseek");
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    fireEvent.click(document.querySelector("#runtime-model-status-refresh") as Element);

    await waitFor(() => {
      expect(document.querySelector("#runtime-status")?.textContent).toBe("main.qwen3-4b-q4-k-m");
      expect(document.querySelector("#runtime-model-context-input")).toHaveValue(4096);
    });
    const judgeLabel = screen.getByText("Current LLM-as-a-Judge Model");
    expect(judgeLabel.nextElementSibling?.textContent).toBe("main.qwen3-4b-q4-k-m");
  });

  test("a stale runtime-model mutation response cannot roll back status or max-token settings", async () => {
    setRuntimeModelControlBootstrapTag(true);
    const newerStatus: RuntimeModelStatus = {
      ...RUNTIME_MODEL_STATUS,
      revision: 8,
      digest_sha512: "e".repeat(128),
      current_max_new_tokens: 1536,
    };
    const staleMutationStatus: RuntimeModelStatus = {
      ...RUNTIME_MODEL_STATUS,
      revision: 7,
      digest_sha512: "f".repeat(128),
      current_max_new_tokens: 512,
    };
    let statusReadCount = 0;
    let resolveMutation = (_response: Response): void => {
      throw new Error("runtime-model mutation was not started");
    };
    const staleMutationResponse = new Promise<Response>((resolve) => {
      resolveMutation = resolve;
    });
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      runtimeModelStatus: () => {
        statusReadCount += 1;
        return statusReadCount === 1 ? RUNTIME_MODEL_STATUS : newerStatus;
      },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-runtime-model-atomic" } },
        {
          type: "completed",
          data: { assistant_message: { content: "accepted" }, finish_reason: "stop" },
        },
      ]),
      mutation: (path) => {
        if (path === "/api/v4/runtime-model/max-new-tokens") {
          return staleMutationResponse;
        }
        throw new Error(`unexpected mutation: ${path}`);
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelector("#runtime-status")?.textContent).toContain("deepseek");
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    const maxTokensInput = document.querySelector(
      "#runtime-model-max-new-tokens-input",
    ) as HTMLInputElement;
    fireEvent.change(maxTokensInput, { target: { value: "512" } });
    fireEvent.click(document.querySelector("#runtime-model-max-new-tokens-apply") as Element);

    fireEvent.click(document.querySelector("#runtime-model-status-refresh") as Element);
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")?.textContent).toContain("8");
      expect(maxTokensInput).toHaveValue(1536);
    });

    resolveMutation(jsonResponse(staleMutationStatus));
    await waitFor(() => {
      expect(document.querySelector("#runtime-model-status-details")?.textContent).toContain("8");
      expect(maxTokensInput).toHaveValue(1536);
    });

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hello" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("accepted")).toBeInTheDocument();
    });
    const chatCall = fetchMock.mock.calls.find(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v1/chat/stream",
    );
    const body = JSON.parse((chatCall?.[1] as RequestInit).body as string) as {
      settings: { max_new_tokens: number };
    };
    expect(body.settings.max_new_tokens).toBe(1536);
  });

  test("governance status stays out of the DOM and unfetched when the bootstrap tag reports disabled", async () => {
    const fetchMock = installFetchMock({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
    });
    expect(document.querySelector("#governance-panel")).toBeNull();
    expect(
      fetchMock.mock.calls.some((call) => pathOf(call[0] as RequestInfo).startsWith("/api/v3/governance")),
    ).toBe(false);
  });

  test("governance status loads once the bootstrap tag reports enabled", async () => {
    setGovernanceBootstrapTag(true);
    installFetchMock({});

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    await waitFor(() => {
      expect(document.querySelector("#governance-panel")).not.toBeNull();
    });
    expect(screen.getByText("Governance Definitions")).toBeInTheDocument();
  });

  test("governance apply goes through Configuration Control's apply endpoint, never a dedicated governance mutation route", async () => {
    setBootstrapTag(true);
    setGovernanceBootstrapTag(true);
    const fetchMock = installFetchMock({
      configurationRuntime: { enabled: true, non_persistent: true },
      configurationEffective: {
        schema_version: "1",
        revision: 5,
        digest_sha512: "cfg-digest",
        fields: [{ key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" }],
        feature_hooks: [],
        recording_hooks: [],
        governance_hooks: [
          {
            component_key: "governance_mode",
            allowed_modes: ["off", "observe"],
            current_mode: "off",
            available: true,
            apply_disposition: "runtime_applicable",
          },
        ],
      },
      mutation: (path) => {
        if (path === "/api/v2/configuration/apply") {
          return jsonResponse({
            outcome: "applied",
            revision: 6,
            digest_sha512: "cfg-digest-2",
            redacted_changes: [],
            restart_fields: [],
          });
        }
        throw new Error(`unexpected mutation: ${path}`);
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    await waitFor(() => {
      expect(document.querySelector("#governance-panel")).not.toBeNull();
    });

    fireEvent.click(screen.getByRole("radio", { name: "Observe" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) => pathOf(call[0] as RequestInfo) === "/api/v2/configuration/apply",
        ),
      ).toBe(true);
    });
    expect(
      fetchMock.mock.calls.some(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/governance/mode",
      ),
    ).toBe(false);

    const applyCall = fetchMock.mock.calls.find(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v2/configuration/apply",
    );
    const requestInit = applyCall?.[1] as RequestInit;
    const body = JSON.parse(requestInit.body as string) as { patch: Record<string, unknown> };
    expect(body.patch).toEqual({ governance_mode: "observe" });
  });

  test("runtime governance status stays out of the DOM and unfetched when the bootstrap tag reports disabled", async () => {
    const fetchMock = installFetchMock({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
    });
    expect(document.querySelector("#runtime-governance-panel")).toBeNull();
    expect(
      fetchMock.mock.calls.some((call) =>
        pathOf(call[0] as RequestInfo).startsWith("/api/v3/runtime-governance"),
      ),
    ).toBe(false);
  });

  test("runtime governance status loads once the bootstrap tag reports enabled", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    installFetchMock({});

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    await waitFor(() => {
      expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    });
    expect(screen.getByText("Main Runtime Governance")).toBeInTheDocument();
  });

  test("runtime governance selection stays canonical until immediate mutation returns", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    installFetchMock({});

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    await waitFor(() => {
      expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    });

    const panel = document.querySelector("#runtime-governance-panel") as HTMLElement;
    expect(within(panel).getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(within(panel).getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");

    fireEvent.click(within(panel).getByRole("radio", { name: "Observe" }));

    expect(within(panel).getByRole("radio", { name: "OFF" })).toHaveAttribute("aria-checked", "true");
    expect(within(panel).getByRole("radio", { name: "Observe" })).toHaveAttribute("aria-checked", "false");
    expect(within(panel).queryByRole("button", { name: "Apply" })).toBeNull();
  });

  test("runtime governance apply goes through Configuration Control's apply endpoint, never a dedicated runtime governance mutation route, and resyncs Status after applying", async () => {
    setBootstrapTag(true);
    setRuntimeGovernanceBootstrapTag(true);
    let applyCount = 0;
    const fetchMock = installFetchMock({
      configurationRuntime: { enabled: true, non_persistent: true },
      configurationEffective: {
        schema_version: "1",
        revision: 5,
        digest_sha512: "cfg-digest",
        fields: [{ key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" }],
        feature_hooks: [],
        recording_hooks: [],
      },
      runtimeGovernanceStatus: {
        enabled: true,
        revision: 1,
        current_mode: "off",
        descriptors: [
          { mode: "off", availability: "available", unavailable_reason_code: null },
          { mode: "observe", availability: "available", unavailable_reason_code: null },
          { mode: "enforce", availability: "unavailable", unavailable_reason_code: "no_definitions" },
        ],
        points: [],
        evidence: null,
      },
      mutation: (path) => {
        if (path === "/api/v2/configuration/apply") {
          applyCount += 1;
          return jsonResponse({
            outcome: "applied",
            revision: 6,
            digest_sha512: "cfg-digest-2",
            redacted_changes: [],
            restart_fields: [],
          });
        }
        throw new Error(`unexpected mutation: ${path}`);
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    await waitFor(() => {
      expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    });

    const statusCallsBeforeApply = fetchMock.mock.calls.filter(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
    ).length;

    const panel = document.querySelector("#runtime-governance-panel") as HTMLElement;
    fireEvent.click(within(panel).getByRole("radio", { name: "Observe" }));

    await waitFor(() => {
      expect(applyCount).toBe(1);
    });
    expect(
      fetchMock.mock.calls.some(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/mode",
      ),
    ).toBe(false);

    const applyCall = fetchMock.mock.calls.find(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v2/configuration/apply",
    );
    const requestInit = applyCall?.[1] as RequestInit;
    const body = JSON.parse(requestInit.body as string) as { patch: Record<string, unknown> };
    expect(body.patch).toEqual({ main_governance_mode: "observe" });

    // P4-CODEX-012-D §5: Apply success re-reads Status from the Server —
    // never trusts the locally-selected Mode alone.
    await waitFor(() => {
      const statusCallsAfterApply = fetchMock.mock.calls.filter(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
      ).length;
      expect(statusCallsAfterApply).toBeGreaterThan(statusCallsBeforeApply);
    });
  });

  test("closing and reopening Settings keeps each Server Current Mode selected", async () => {
    // P4-CODEX-013: the Settings Modal fully unmounts its Panels on
    // close (`if (!open) return null`) and remounts them on reopen — a
    // remount must not silently reset the visible selection to OFF when
    // the Server's own Current Mode is already something else.
    setBootstrapTag(true);
    setGovernanceBootstrapTag(true);
    setRuntimeGovernanceBootstrapTag(true);
    installFetchMock({
      configurationRuntime: { enabled: true, non_persistent: true },
      configurationEffective: {
        schema_version: "1",
        revision: 5,
        digest_sha512: "cfg-digest",
        fields: [{ key: "research_developer_mode", value: "off", source: "default", apply_disposition: "hot" }],
        feature_hooks: [],
        recording_hooks: [],
      },
      governanceRuntime: {
        mode: {
          revision: 2,
          digest_sha512: "gov123",
          current_mode: "observe",
          descriptors: [
            { mode: "off", availability: "available", apply_disposition: "hot", unavailable_reason_code: null },
            {
              mode: "observe",
              availability: "available",
              apply_disposition: "hot",
              unavailable_reason_code: null,
            },
            {
              mode: "enforce",
              availability: "unavailable",
              apply_disposition: "rejected",
              unavailable_reason_code: "phase_3_enforce_unavailable",
            },
          ],
        },
        observe_summary: null,
      },
      runtimeGovernanceStatus: {
        enabled: true,
        revision: 2,
        current_mode: "enforce",
        descriptors: [
          { mode: "off", availability: "available", unavailable_reason_code: null },
          { mode: "observe", availability: "available", unavailable_reason_code: null },
          { mode: "enforce", availability: "available", unavailable_reason_code: null },
        ],
        points: [],
        evidence: null,
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));

    await waitFor(() => {
      expect(document.querySelector("#governance-panel")).not.toBeNull();
      expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    });
    expect(
      within(document.querySelector("#governance-panel") as HTMLElement).getByRole("radio", {
        name: "Observe",
      }),
    ).toHaveAttribute("aria-checked", "true");
    expect(
      within(document.querySelector("#runtime-governance-panel") as HTMLElement).getByRole("radio", {
        name: "Enforce",
      }),
    ).toHaveAttribute("aria-checked", "true");

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    fireEvent.click(screen.getByRole("button", { name: "Advanced Mode" }));
    await waitFor(() => {
      expect(document.querySelector("#governance-panel")).not.toBeNull();
      expect(document.querySelector("#runtime-governance-panel")).not.toBeNull();
    });

    expect(
      within(document.querySelector("#governance-panel") as HTMLElement).getByRole("radio", {
        name: "Observe",
      }),
    ).toHaveAttribute("aria-checked", "true");
    expect(
      within(document.querySelector("#runtime-governance-panel") as HTMLElement).getByRole("radio", {
        name: "Enforce",
      }),
    ).toHaveAttribute("aria-checked", "true");
  });

  test("runtime governance status refreshes exactly once after an ephemeral chat terminates", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-1" } },
        { type: "delta", data: { channel: "final", text: "hello there" } },
        { type: "completed", data: { assistant_message: { content: "hello there" }, finish_reason: "stop" } },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
    const statusCallsBeforeSend = fetchMock.mock.calls.filter(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
    ).length;

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("hello there")).toBeInTheDocument();
    });
    await waitFor(() => {
      const statusCallsAfterSend = fetchMock.mock.calls.filter(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
      ).length;
      expect(statusCallsAfterSend).toBe(statusCallsBeforeSend + 1);
    });
  });

  test("P6-CODEX-024: the completed assistant bubble carries the stream's own request_id for Live Judge/Repair correlation", async () => {
    installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-live-judge-1" } },
        { type: "delta", data: { channel: "final", text: "hello there" } },
        { type: "completed", data: { assistant_message: { content: "hello there" }, finish_reason: "stop" } },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("hello there")).toBeInTheDocument();
    });
    const bubble = screen.getByText("hello there").closest("[data-request-id]");
    expect(bubble?.getAttribute("data-request-id")).toBe("req-live-judge-1");
  });

  test("P6-CODEX-024: a live Judge badge appears once the background poll observes this Turn's own request_id running", async () => {
    installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-live-judge-2" } },
        { type: "delta", data: { channel: "final", text: "hello there" } },
        { type: "completed", data: { assistant_message: { content: "hello there" }, finish_reason: "stop" } },
      ]),
      featureModesStatus: {
        judge: {
          enabled: true,
          revision: 1,
          current_mode: "enforce",
          state: "judging",
          current_request_id: "req-live-judge-2",
          last_result: null,
        },
        repair: { enabled: true, revision: 1, current_mode: "enforce" },
        recording: {
          enabled: false,
          revision: null,
          current_mode: null,
          last_outcome: null,
          judge_evidence_last_outcome: null,
        },
      },
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("hello there")).toBeInTheDocument();
    });
    await waitFor(
      () => {
        expect(screen.getByText("Reviewing…")).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  test("a runtime governance status refresh failure never rewrites the completed chat result", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      runtimeGovernanceStatus: undefined,
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-1" } },
        { type: "completed", data: { assistant_message: { content: "final answer" }, finish_reason: "stop" } },
      ]),
    });
    // Force the post-Terminal Status refetch to fail, without touching
    // the Chat stream response above at all.
    const originalFetch = window.fetch.bind(window);
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        if (pathOf(input) === "/api/v3/runtime-governance/status") {
          return Promise.reject(new Error("simulated network failure"));
        }
        return originalFetch(input, init);
      }),
    );

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("final answer")).toBeInTheDocument();
    });
    expect(screen.queryByText(/^Error/u)).toBeNull();
  });

  test("no extra runtime governance status GET happens when the bootstrap tag reports disabled", async () => {
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-1" } },
        { type: "completed", data: { assistant_message: { content: "hello" }, finish_reason: "stop" } },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("hello")).toBeInTheDocument();
    });
    expect(
      fetchMock.mock.calls.some((call) =>
        pathOf(call[0] as RequestInfo).startsWith("/api/v3/runtime-governance"),
      ),
    ).toBe(false);
  });

  test("runtime governance status refreshes exactly once after a persistent turn terminates", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: true, source_of_truth: "server" },
      persistentList: {
        items: [{ conversation_id: "conversation-1", updated_at: "2024-01-01T00:00:00Z", state: "active" }],
        next_cursor: null,
      },
      conversationDetail: {
        "conversation-1": { storage_revision: 1, state: "active" },
      },
      persistentTurnStream: sseStreamResponse([
        {
          type: "start",
          data: { request_id: "req-1", turn_id: "turn-1", durable_revision: 2, state: "generating" },
        },
        {
          type: "completed",
          data: {
            durable_revision: 3,
            assistant_message: { content: "persistent answer" },
            finish_reason: "stop",
          },
        },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelectorAll(".chat-list-item")).toHaveLength(1);
    });
    fireEvent.click(within(document.querySelector(".chat-list") as HTMLElement).getByText(/conversati/));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    const statusCallsBeforeSend = fetchMock.mock.calls.filter(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
    ).length;

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      const statusCallsAfterSend = fetchMock.mock.calls.filter(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
      ).length;
      expect(statusCallsAfterSend).toBe(statusCallsBeforeSend + 1);
    });
  });

  test("runtime governance status refreshes exactly once after a derived (retry/regenerate) turn terminates", async () => {
    setRuntimeGovernanceBootstrapTag(true);
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: true, source_of_truth: "server" },
      persistentList: {
        items: [{ conversation_id: "conversation-1", updated_at: "2024-01-01T00:00:00Z", state: "active" }],
        next_cursor: null,
      },
      conversationDetail: {
        "conversation-1": {
          storage_revision: 1,
          state: "active",
          head_turn_id: "turn-1",
          turns: [
            {
              turn_id: "turn-1",
              state: "completed",
              messages: [
                { role: "user", content: "hi" },
                { role: "assistant", content: "first answer" },
              ],
            },
          ],
        },
      },
      persistentDerivedStream: sseStreamResponse([
        {
          type: "start",
          data: { request_id: "req-1", turn_id: "turn-1", durable_revision: 2, state: "generating" },
        },
        {
          type: "completed",
          data: {
            durable_revision: 3,
            assistant_message: { content: "regenerated answer" },
            finish_reason: "stop",
          },
        },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelectorAll(".chat-list-item")).toHaveLength(1);
    });
    fireEvent.click(within(document.querySelector(".chat-list") as HTMLElement).getByText(/conversati/));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument();
    });

    const statusCallsBeforeAction = fetchMock.mock.calls.filter(
      (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
    ).length;

    fireEvent.click(screen.getByRole("button", { name: "Regenerate" }));

    await waitFor(() => {
      const statusCallsAfterAction = fetchMock.mock.calls.filter(
        (call) => pathOf(call[0] as RequestInfo) === "/api/v3/runtime-governance/status",
      ).length;
      expect(statusCallsAfterAction).toBe(statusCallsBeforeAction + 1);
    });
  });

  test("browser storage only ever receives the two interface-preference keys, never conversation or configuration data", async () => {
    installFetchMock({ persistentRuntime: { enabled: false, source_of_truth: "server" } });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    fireEvent.click(screen.getByRole("button", { name: "Dark" }));
    fireEvent.click(screen.getByRole("button", { name: "English" }));

    expect(new Set(Object.keys(window.localStorage))).toEqual(
      new Set(["margpa.ui_theme.v1", "margpa.ui_language.v1"]),
    );
    expect(window.localStorage.getItem("margpa.ui_theme.v1")).toBe("dark");
    expect(window.localStorage.getItem("margpa.ui_language.v1")).toBe("en");
    expect(window.sessionStorage.length).toBe(0);
  });

  test("a token-limit warning that arrives before completed stays the terminal status, not overwritten by completed", async () => {
    installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "start", data: { request_id: "req-1" } },
        {
          type: "warning",
          data: { code: "final_answer_token_limit", message: "token limit reached" },
        },
        { type: "completed", data: { assistant_message: { content: "" }, finish_reason: "length" } },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hello" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(
        screen.getByText("Warning: The token limit was reached before a final answer was generated."),
      ).toBeInTheDocument();
    });
    expect(screen.queryByText(/^Completed/u)).toBeNull();
  });

  test("P6-CODEX-012: preparing/guarding STATUS events before start are handled without breaking the chat result", async () => {
    installFetchMock({
      persistentRuntime: { enabled: false, source_of_truth: "server" },
      chatStream: sseStreamResponse([
        { type: "status", data: { request_id: "req-1", state: "preparing" } },
        { type: "status", data: { request_id: "req-1", state: "guarding" } },
        { type: "start", data: { request_id: "req-1", state: "generating" } },
        { type: "delta", data: { channel: "final", text: "hello there" } },
        {
          type: "completed",
          data: { assistant_message: { content: "hello there" }, finish_reason: "stop" },
        },
      ]),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    fireEvent.change(screen.getByLabelText("Message"), { target: { value: "hi" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(screen.getByText("hello there")).toBeInTheDocument();
    });
    expect(screen.queryByText(/^Error/u)).toBeNull();
  });

  test("the sidebar Account entry opens the settings modal, showing basic settings by default", async () => {
    installFetchMock({ persistentRuntime: { enabled: false, source_of_truth: "server" } });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Account" })).toBeInTheDocument();
    });
    expect(screen.queryByRole("dialog")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Account" }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(document.querySelector("#response-language-label")).not.toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  test("the single sidebar toggle button hides the sidebar and shows it again", async () => {
    installFetchMock({ persistentRuntime: { enabled: false, source_of_truth: "server" } });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelector("#sidebar")).toHaveAttribute("data-visible", "true");
    });

    // The sidebar stays mounted (CSS handles the collapse/slide transition)
    // rather than unmounting, so visibility is asserted via data-visible,
    // not DOM presence.
    fireEvent.click(screen.getByRole("button", { name: "Hide menu" }));
    expect(document.querySelector("#sidebar")).toHaveAttribute("data-visible", "false");

    fireEvent.click(screen.getByRole("button", { name: "Show menu" }));
    expect(document.querySelector("#sidebar")).toHaveAttribute("data-visible", "true");
  });

  test("resuming a non-selected conversation from the sidebar fetches that conversation's own revision, not the open one's", async () => {
    const mutation = vi.fn((path: string, body: { expected_revision?: number }) => {
      expect(path).toBe("/api/v2/conversations/target-conversation/resume");
      expect(body.expected_revision).toBe(42);
      return jsonResponse({ detail: detailPayload("target-conversation", 43, "active") });
    });
    const fetchMock = installFetchMock({
      persistentRuntime: { enabled: true, source_of_truth: "server" },
      persistentList: {
        items: [
          { conversation_id: "open-conversation", updated_at: "2024-01-01T00:00:00Z", state: "active" },
          { conversation_id: "target-conversation", updated_at: "2024-01-02T00:00:00Z", state: "active" },
        ],
        next_cursor: null,
      },
      conversationDetail: {
        "open-conversation": { storage_revision: 1, state: "active" },
        "target-conversation": { storage_revision: 42, state: "active" },
      },
      mutation,
    });

    render(<App />);
    await waitFor(() => {
      expect(document.querySelectorAll(".chat-list-item")).toHaveLength(2);
    });

    // Open "open-conversation" first so persistentRevisionRef tracks *its*
    // revision (1) — the bug this test guards against is using that ref's
    // value when acting on a different, unopened conversation instead.
    fireEvent.click(screen.getByText(/open-conve/));
    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) => pathOf(call[0] as RequestInfo) === "/api/v2/conversations/open-conversation",
        ),
      ).toBe(true);
    });

    const targetItem = document.querySelectorAll<HTMLElement>(".chat-list-item")[1];
    if (targetItem === undefined) throw new Error("expected a second chat list item");
    fireEvent.click(within(targetItem).getByRole("button", { name: "Chat options" }));
    fireEvent.click(within(targetItem).getByRole("menuitem", { name: "Resume" }));

    await waitFor(() => {
      expect(mutation).toHaveBeenCalled();
    });
  });
});
