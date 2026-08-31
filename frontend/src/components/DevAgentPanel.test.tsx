import { fireEvent, render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import type { DevAgentCapability, DevAgentRun, DevAgentToolDescriptor } from "../types";
import DevAgentPanel from "./DevAgentPanel";

const capabilities: DevAgentCapability[] = [
  { capability_id: "chat" },
  { capability_id: "dev_agent" },
];

const tools: DevAgentToolDescriptor[] = [
  {
    tool_id: "list_files",
    name: "List Files",
    description: "Lists files.",
    important_gate_reason: null,
  },
  {
    tool_id: "write_note",
    name: "Write Note",
    description: "Writes a note.",
    important_gate_reason: "external_write",
  },
];

function stubFetch(): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn((url: string) => {
    if (url.includes("/capabilities")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(capabilities) });
    }
    if (url.includes("/tools")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(tools) });
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function baseRun(overrides: Partial<DevAgentRun>): DevAgentRun {
  return {
    run_id: "run-1",
    capability_id: "dev_agent",
    approval_profile: "important_gate_only",
    max_steps: 5,
    state: "running",
    steps: [
      { step_id: "list", tool_id: "list_files", state: "pending", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
      { step_id: "read", tool_id: "read_file", state: "pending", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
      { step_id: "write", tool_id: "write_note", state: "pending", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
    ],
    created_at: "2026-08-30T00:00:00+00:00",
    deadline_at: null,
    completion: null,
    constitution_mode: null,
    constitution_rule_ids: null,
    envelope: null,
    ...overrides,
  };
}

function stubFetchWithRunFlow(runResponses: DevAgentRun[]): ReturnType<typeof vi.fn> {
  let mutationCallIndex = 0;
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.includes("/capabilities")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(capabilities) });
    }
    if (url.includes("/tools")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(tools) });
    }
    if (init?.method === "POST" && url.includes("/dev-agent/runs")) {
      const response = runResponses[mutationCallIndex];
      mutationCallIndex += 1;
      return Promise.resolve({ ok: true, json: () => Promise.resolve(response) });
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function selectDevAgent(): Promise<void> {
  await waitFor(() => {
    expect(document.querySelector("#dev-agent-panel")).not.toBeNull();
  });
  const radios = document.querySelectorAll('input[name="dev-agent-capability"]');
  fireEvent.click(radios[1] as Element);
  await waitFor(() => {
    expect(document.querySelector("#dev-agent-tools")).not.toBeNull();
  });
}

describe("DevAgentPanel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders nothing when not visible, even without a fetch", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<DevAgentPanel language="en" visible={false} />);
    expect(document.querySelector("#dev-agent-panel")).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("defaults to Chat and does not fetch Tools until Dev Agent is selected", async () => {
    const fetchMock = stubFetch();
    render(<DevAgentPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-panel")).not.toBeNull();
    });
    expect(document.querySelector("#dev-agent-tools")).toBeNull();
    expect(fetchMock.mock.calls.some((call) => String(call[0]).includes("/tools"))).toBe(false);
  });

  test("selecting Dev Agent reveals the registered Tools, important flagged", async () => {
    stubFetch();
    render(<DevAgentPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-panel")).not.toBeNull();
    });
    const radios = document.querySelectorAll('input[name="dev-agent-capability"]');
    fireEvent.click(radios[1] as Element);

    await waitFor(() => {
      expect(document.querySelector("#dev-agent-tools")).not.toBeNull();
    });
    const listText = document.querySelector("#dev-agent-tools")?.textContent;
    expect(listText).toContain("List Files");
    expect(listText).toContain("Write Note");
    expect(listText).toContain("Requires approval");
  });

  test("a failed capabilities fetch degrades to silently absent", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }));
    const { container } = render(<DevAgentPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(container.textContent).toBe("");
    });
    expect(document.querySelector("#dev-agent-panel")).toBeNull();
  });

  test("starting a Demo Run shows its state and Steps", async () => {
    stubFetchWithRunFlow([baseRun({})]);
    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);

    await waitFor(() => {
      expect(document.querySelector("#dev-agent-run-detail")).not.toBeNull();
    });
    const stepsText = document.querySelector("#dev-agent-run-steps")?.textContent;
    expect(stepsText).toContain("list");
    expect(stepsText).toContain("read");
    expect(stepsText).toContain("write");
    expect(document.querySelector("#dev-agent-approval-gate")).toBeNull();
  });

  test("the full Gate -> Approve -> Complete flow works end to end from the screen", async () => {
    // P8-RW6-C (P8-CODEX-007): `important_gate_only` now also Gates the
    // Run's own Completion (a Run-level Important Gate, distinct from any
    // Step Gate) — the mocked sequence below mirrors the real backend's
    // actual Step -> Step-Approve -> Step-Execute -> Completion-Gate ->
    // Completion-Approve -> Complete shape, not a collapsed shortcut.
    const gated = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "read", tool_id: "read_file", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "write", tool_id: "write_note", state: "awaiting_approval", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
      ],
      state: "awaiting_approval",
    });
    const approved = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "read", tool_id: "read_file", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "write", tool_id: "write_note", state: "pending", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: true },
      ],
      state: "running",
    });
    const stepDone = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "read", tool_id: "read_file", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "write", tool_id: "write_note", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: true },
      ],
      state: "running",
    });
    const awaitingCompletion = baseRun({
      steps: stepDone.steps,
      state: "awaiting_completion_approval",
      // P8-MR9-1 (P8-CODEX-011/UF-P8-003): the frozen Step Envelope from the
      // earlier `write_note` Tool Gate is still attached to the Run — this
      // reproduces the real observed bug where the UI read this leftover
      // `external_write` instead of the Completion Gate's own `completion`
      // reason.
      envelope: {
        run_id: "run-1",
        allowed_step_ids: ["list", "read", "write"],
        allowed_tool_ids: ["list_files", "read_file", "write_note"],
        resource_scope: "fixture_only",
        max_steps: 5,
        max_attempts: 1,
        expires_at: null,
        gate_reasons: ["external_write"],
        issued_at: "t",
      },
    });
    const completionApproved = baseRun({ steps: stepDone.steps, state: "running" });
    const completed = baseRun({
      steps: stepDone.steps,
      state: "completed",
      completion: { outcome: "completed", reason: "All Plan Steps completed successfully." },
    });

    stubFetchWithRunFlow([gated, approved, stepDone, awaitingCompletion, completionApproved, completed]);
    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-approval-gate")).not.toBeNull();
    });
    expect(document.querySelector("#dev-agent-approval-gate")?.textContent).toContain("write");

    fireEvent.click(document.querySelector("#dev-agent-approve") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-approval-gate")).toBeNull();
    });

    fireEvent.click(document.querySelector("#dev-agent-advance") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-run-state")?.textContent).toContain("running");
    });

    fireEvent.click(document.querySelector("#dev-agent-advance") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-completion-gate")).not.toBeNull();
    });
    // P8-MR9-1 (P8-CODEX-011/UF-P8-003): the Completion Gate must show its
    // own Contract-true `completion` reason, never the stale Tool Gate's
    // `external_write` still attached to the frozen Envelope.
    const completionGate = document.querySelector("#dev-agent-completion-gate");
    expect(completionGate?.textContent).toContain("completion");
    expect(completionGate?.textContent).not.toContain("external_write");

    fireEvent.click(document.querySelector("#dev-agent-completion-approve") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-completion-gate")).toBeNull();
    });

    fireEvent.click(document.querySelector("#dev-agent-advance") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-run-completion")).not.toBeNull();
    });
    expect(document.querySelector("#dev-agent-run-completion")?.textContent).toContain(
      "completed",
    );
    // P8-MR9-3 (P8-CODEX-011/UF-UI-013): the same Style as the initial
    // "Start Run" Action, never a lesser/secondary-looking Button just
    // because the Run happens to be Completed/Cancelled.
    expect(document.querySelector("#dev-agent-reset")).toHaveClass("primary");
  });

  test("Cancel finalizes the Run from the screen", async () => {
    const started = baseRun({});
    const cancelled = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "cancelled", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
        { step_id: "read", tool_id: "read_file", state: "cancelled", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
        { step_id: "write", tool_id: "write_note", state: "cancelled", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
      ],
      state: "cancelled",
      completion: { outcome: "cancelled", reason: "Run was cancelled." },
    });
    stubFetchWithRunFlow([started, cancelled]);
    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-cancel")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#dev-agent-cancel") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-run-completion")?.textContent).toContain(
        "cancelled",
      );
    });
    // P8-MR9-3 (P8-CODEX-011/UF-UI-013): the same Style as the initial
    // "Start Run" Action, never a lesser/secondary-looking Button just
    // because the Run happens to be Completed/Cancelled.
    expect(document.querySelector("#dev-agent-reset")).toHaveClass("primary");
  });

  test("a failed Run start shows an error message, not a crash", async () => {
    stubFetch();
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/capabilities")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(capabilities) });
      }
      if (url.includes("/tools")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(tools) });
      }
      if (init?.method === "POST") {
        return Promise.resolve({
          ok: false,
          json: () =>
            Promise.resolve({ code: "dev_agent_unavailable", message: "unavailable right now" }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-run-error")).not.toBeNull();
    });
    expect(document.querySelector("#dev-agent-run-error")?.textContent).toContain(
      "unavailable right now",
    );
  });

  // -- P8-MR5 (P8-MANUAL-005): Informed Approval ----------------------------

  test("shows the real Target Path/Content before Approval, and Digest/Result after", async () => {
    const gated = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "succeeded", attempt_count: 1, input: {}, output: { paths: ["notes/readme.md", "notes/todo.md"] }, error: null, completed_at: "t", approved: false },
        { step_id: "read", tool_id: "read_file", state: "succeeded", attempt_count: 1, input: { path: "notes/readme.md" }, output: { path: "notes/readme.md", content: "hi" }, error: null, completed_at: "t", approved: false },
        {
          step_id: "write",
          tool_id: "write_note",
          state: "awaiting_approval",
          attempt_count: 0,
          input: { path: "notes/new.md", content: "Hello from the Dev Agent Demo Run." },
          output: null,
          error: null,
          completed_at: null,
          approved: false,
        },
      ],
      state: "awaiting_approval",
      envelope: {
        run_id: "run-1",
        allowed_step_ids: ["list", "read", "write"],
        allowed_tool_ids: ["list_files", "read_file", "write_note"],
        resource_scope: "fixture_only",
        max_steps: 5,
        max_attempts: 1,
        expires_at: null,
        gate_reasons: ["external_write"],
        issued_at: "t",
      },
    });
    const succeeded = baseRun({
      steps: [
        ...gated.steps.slice(0, 2),
        {
          step_id: "write",
          tool_id: "write_note",
          state: "succeeded",
          attempt_count: 1,
          input: { path: "notes/new.md", content: "Hello from the Dev Agent Demo Run." },
          output: {
            path: "notes/new.md",
            written: true,
            content_sha512: "a".repeat(128),
            overwrite: false,
          },
          error: null,
          completed_at: "t",
          approved: true,
        },
      ],
      state: "running",
    });

    stubFetchWithRunFlow([gated, succeeded]);
    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-approval-gate")).not.toBeNull();
    });

    // Informed Approval: the real Target Path/Content are visible BEFORE
    // the User ever clicks Approve.
    const gate = document.querySelector("#dev-agent-approval-gate");
    expect(gate?.textContent).toContain("notes/new.md");
    expect(gate?.textContent).toContain("Hello from the Dev Agent Demo Run.");
    expect(gate?.textContent).toContain("fixture_only");
    expect(gate?.textContent).toContain("external_write");
    expect(gate?.textContent).toContain("fixture_workspace");

    fireEvent.click(document.querySelector("#dev-agent-approve") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-approval-gate")).toBeNull();
    });

    // The real Result (Digest/Overwrite) is visible after Approval too.
    const stepsText = document.querySelector("#dev-agent-run-steps")?.textContent;
    expect(stepsText).toContain("written: true");
    expect(stepsText).toContain("a".repeat(128));
    expect(stepsText).toContain("overwrite: false");
  });

  // -- P8-MR6 (P8-MANUAL-006): Button Contrast ------------------------------

  test("Approve/Advance use the Primary style and Deny/Cancel use the Danger style", async () => {
    const gated = baseRun({
      steps: [
        { step_id: "list", tool_id: "list_files", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "read", tool_id: "read_file", state: "succeeded", attempt_count: 1, input: {}, output: {}, error: null, completed_at: "t", approved: false },
        { step_id: "write", tool_id: "write_note", state: "awaiting_approval", attempt_count: 0, input: {}, output: null, error: null, completed_at: null, approved: false },
      ],
      state: "awaiting_approval",
    });
    stubFetchWithRunFlow([gated]);
    render(<DevAgentPanel language="en" visible={true} />);
    await selectDevAgent();

    fireEvent.click(document.querySelector("#dev-agent-start-run") as Element);
    await waitFor(() => {
      expect(document.querySelector("#dev-agent-approval-gate")).not.toBeNull();
    });

    expect(document.querySelector("#dev-agent-approve")).toHaveClass("primary");
    expect(document.querySelector("#dev-agent-deny")).toHaveClass("danger");
    // Neither Button is left with no explicit style class at all — the
    // exact pre-Rework bug (near-white-on-white text) came from relying on
    // an unclassed `button`'s Browser-default Background.
    expect(document.querySelector("#dev-agent-approve")?.className).not.toBe("");
    expect(document.querySelector("#dev-agent-deny")?.className).not.toBe("");
  });
});
