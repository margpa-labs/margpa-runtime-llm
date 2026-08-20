import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import App from "./App";
import type { RuntimeInfo } from "./types";

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
  chatStream?: Response;
  conversationDetail?: Record<string, { storage_revision: number; state: string }>;
  mutation?: (path: string, body: { expected_revision?: number }) => Response;
}

function detailPayload(conversationId: string, storageRevision: number, state: string): unknown {
  return {
    conversation_id: conversationId,
    state,
    storage_revision: storageRevision,
    head_turn_id: null,
    turns: [],
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
    if (path === "/api/v1/chat/stream" && method === "POST" && routes.chatStream !== undefined) {
      return Promise.resolve(routes.chatStream);
    }
    const detailMatch = /^\/api\/v2\/conversations\/([^/]+)$/u.exec(path);
    if (detailMatch !== null && method === "GET" && routes.conversationDetail !== undefined) {
      const conversationId = detailMatch[1] ?? "";
      const entry = routes.conversationDetail[conversationId];
      if (entry !== undefined) {
        return Promise.resolve(
          jsonResponse(detailPayload(conversationId, entry.storage_revision, entry.state)),
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
    // The app defaults to Japanese; pin English so assertions below can use
    // one fixed set of expected strings.
    window.localStorage.setItem("margpa.ui_language.v1", "en");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    document.head.querySelector("#configuration-bootstrap")?.remove();
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
