import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import type {
  ExperimentComparison,
  ExperimentPresets,
  ExperimentVariantRun,
  ExperimentVariantRunResult,
} from "../types";
import ExperimentPanel from "./ExperimentPanel";

const presets: ExperimentPresets = {
  enabled: true,
  cases: [
    { case_id: "case-1", revision: "rev-1", input: "input text", requires_human_review: false },
  ],
  variants: [
    { variant_id: "baseline-all-off", label: "Baseline", components: [] },
    {
      variant_id: "judge-observe",
      label: "Judge OBSERVE",
      // R4-WU-01 (Handoff R4 SS4.1.1): a Preset's own declared
      // `selector_id` (Provider identity) must be visible to the User,
      // not only Mode.
      components: [
        { component_key: "judge", selector_id: "judge.gemma-4-e2b-it-q4-0", mode: "observe" },
      ],
    },
  ],
};

const runResult: ExperimentVariantRunResult = {
  run: {
    run_id: "run-1",
    experiment_id: "exp-1",
    variant_id: "judge-observe",
    request_id: "req-1",
    execution_mode: "fixture",
    state: "completed",
    generation: 1,
    started_at: "2026-01-01T00:00:00+00:00",
    completed_at: "2026-01-01T00:00:01+00:00",
    failure_reason: null,
    fixture_only: true,
    frozen_configuration_digest_sha512: null,
  },
  invocations: [
    {
      component_key: "judge",
      called: true,
      outcome: "completed",
      mutation_count: 1,
      evidence_count: 1,
      authority_exercised: true,
    },
    {
      component_key: "main",
      called: false,
      outcome: "off",
      mutation_count: 0,
      evidence_count: 0,
      authority_exercised: false,
    },
  ],
  production_request_id: null,
  assistant_content: null,
  final_disposition: null,
};

const comparison: ExperimentComparison = {
  experiment_id: "exp-1",
  case_id: "case-1",
  case_revision: "rev-1",
  rows: [
    {
      variant_id: "judge-observe",
      run_id: "run-1",
      execution_mode: "fixture",
      runtime_state: "completed",
      metric: {
        runtime_state: "completed",
        latency_ms: null,
        call_count: 1,
        unknown_component_count: 0,
        deviation_count: null,
        repair_adopted: null,
        false_positive: null,
        false_grounding: null,
        correction_acceptance: null,
      },
      observations: [
        {
          evaluator_kind: "deterministic",
          evaluator_identity: "metric.deterministic-v1",
          outcome: "pass",
          score: null,
          reason: null,
        },
      ],
      failure_reason: null,
      raw_evidence_pointer: "run-1",
      variant_components: [],
      frozen_configuration_digest_sha512: null,
    },
  ],
};

function stubFetch(enabled = true): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.includes("/presets")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(enabled ? presets : { enabled: false, cases: [], variants: [] }),
      });
    }
    if (url.includes("/plans")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            experiment_id: "exp-1",
            case_id: "case-1",
            case_revision: "rev-1",
            variant_ids: ["judge-observe"],
            plan_digest_sha512: "a".repeat(128),
            variant_configurations: [
              {
                variant_id: "judge-observe",
                desired_configuration_digest_sha512: "b".repeat(128),
                desired_components: [],
              },
            ],
          }),
      });
    }
    if (url.includes("/comparison")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(comparison) });
    }
    if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(runResult.run) });
    }
    if (url.match(/\/runs\/[^/]+$/) !== null) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(runResult) });
    }
    if (url.includes("/experiments/") && url.includes("/runs")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ experiment_id: "exp-1", runs: [runResult.run] }),
      });
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function installLongRunFetch(
  statusState: () => ExperimentVariantRun["state"],
  listState: (listReadCount: number) => ExperimentVariantRun["state"],
): { fetchMock: ReturnType<typeof vi.fn>; trace: { posts: number; statusGets: number; listGets: number } } {
  const trace = { posts: 0, statusGets: 0, listGets: 0 };
  let runId = "run-pending";
  const asRun = (state: ExperimentVariantRun["state"]): ExperimentVariantRun => ({
    ...runResult.run,
    run_id: runId,
    state,
    completed_at: state === "completed" ? "2026-01-01T00:00:01+00:00" : null,
  });
  const fetchMock = vi.fn((url: string, init?: RequestInit) => {
    if (url.includes("/presets")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
    }
    if (url.includes("/plans")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            experiment_id: "exp-1",
            case_id: "case-1",
            case_revision: "rev-1",
            variant_ids: ["judge-observe"],
            plan_digest_sha512: "a".repeat(128),
            execution_mode: "fixture",
            variant_configurations: [],
          }),
      });
    }
    if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
      trace.posts += 1;
      if (typeof init.body === "string") {
        const body = JSON.parse(init.body) as { run_id: string };
        runId = body.run_id;
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve(asRun("running")) });
    }
    if (/\/runs\/[^/]+$/u.test(url)) {
      trace.statusGets += 1;
      const run = asRun(statusState());
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ ...runResult, run }),
      });
    }
    if (url.includes("/experiments/") && url.includes("/runs")) {
      trace.listGets += 1;
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({ experiment_id: "exp-1", runs: [asRun(listState(trace.listGets))] }),
      });
    }
    if (url.includes("/comparison")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ ...comparison, rows: [] }),
      });
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, trace };
}

interface Deferred<T> {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (reason?: unknown) => void;
}

function deferred<T>(): Deferred<T> {
  let resolvePromise: (value: T) => void = () => {};
  let rejectPromise: (reason?: unknown) => void = () => {};
  const promise = new Promise<T>((resolve, reject) => {
    resolvePromise = resolve;
    rejectPromise = reject;
  });
  return { promise, resolve: resolvePromise, reject: rejectPromise };
}

describe("ExperimentPanel", () => {
  beforeEach(() => {
    vi.stubGlobal("crypto", { randomUUID: () => "00000000-0000-0000-0000-000000000000" });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  test("renders nothing when closed", () => {
    stubFetch();
    const { container } = render(
      <ExperimentPanel language="en" open={false} onClose={() => {}} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  test("shows the disabled note when the backend has no experiment_service", async () => {
    stubFetch(false);
    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(
        screen.getByText("The Experiment feature is not available in this deployment."),
      ).toBeInTheDocument();
    });
  });

  test("full lifecycle: presets -> plan -> run -> comparison -> details", async () => {
    stubFetch();
    render(<ExperimentPanel language="en" open onClose={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });

    // R4-WU-01 (Handoff R4 SS4.1.1): the Preset's own declared Provider
    // identity (`selector_id`) is visible alongside its Mode, not only
    // enforced silently on the backend.
    expect(screen.getByText("(judge=observe(judge.gemma-4-e2b-it-q4-0))")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    const createPlanButton = screen.getByRole("button", { name: "Create plan" });
    expect(createPlanButton).toHaveClass("primary");
    fireEvent.click(createPlanButton);

    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    const runButton = screen.getByRole("button", { name: /Run: judge-observe/ });
    expect(runButton).toHaveClass("primary");
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("judge-observe")).toBeInTheDocument();
      expect(screen.getByText("completed")).toBeInTheDocument();
    });

    // The Comparison Report's own Evaluation column shows the real
    // Deterministic Observation outcome, not merely the Run State.
    await waitFor(() => {
      expect(screen.getByText("pass")).toBeInTheDocument();
    });

    const detailButton = screen.getByRole("button", {
      name: "Detail evidence (by component)",
    });
    expect(detailButton).toHaveClass("secondary");
    fireEvent.click(detailButton);

    await waitFor(() => {
      expect(screen.getByText("judge")).toBeInTheDocument();
      expect(screen.getByText("main")).toBeInTheDocument();
    });

    expect(
      screen.getByText(
        "This result comes from Fixture Actors only. No real Main, Judge, Guard, or Repair call was ever made.",
      ),
    ).toBeInTheDocument();
  });

  test("a Production run's detail view shows the real-result disclaimer, never the Fixture one", async () => {
    const productionRunResult: ExperimentVariantRunResult = {
      ...runResult,
      run: { ...runResult.run, execution_mode: "production", fixture_only: false },
      production_request_id: "real-req-1",
      assistant_content: "Paris.",
    };
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-1",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["judge-observe"],
              plan_digest_sha512: "a".repeat(128),
              variant_configurations: [
                {
                  variant_id: "judge-observe",
                  desired_configuration_digest_sha512: "b".repeat(128),
                  desired_components: [],
                },
              ],
            }),
        });
      }
      if (url.includes("/comparison")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(comparison) });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(productionRunResult.run) });
      }
      if (url.match(/\/runs\/[^/]+$/) !== null) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(productionRunResult) });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ experiment_id: "exp-1", runs: [productionRunResult.run] }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await waitFor(() => {
      expect(screen.getByText("completed")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: "Detail evidence (by component)" }));
    await waitFor(() => {
      expect(
        screen.getByText(
          "This result comes from a real Production Turn. Real Main/Judge/Guard calls may have happened.",
        ),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByText(
        "This result comes from Fixture Actors only. No real Main, Judge, Guard, or Repair call was ever made.",
      ),
    ).not.toBeInTheDocument();
  });

  test("a transient status-read failure retries instead of stranding the first running row", async () => {
    const runningRun = {
      ...runResult.run,
      state: "running" as const,
      completed_at: null,
    };
    let statusReadCount = 0;
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-1",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["judge-observe"],
              plan_digest_sha512: "a".repeat(128),
              execution_mode: "fixture",
              variant_configurations: [],
            }),
        });
      }
      if (url.includes("/comparison")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(comparison) });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(runningRun) });
      }
      if (url.match(/\/runs\/[^/]+$/) !== null) {
        statusReadCount += 1;
        if (statusReadCount === 1) {
          return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve(runResult) });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-1",
              runs: [statusReadCount >= 2 ? runResult.run : runningRun],
            }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    // Merely having created a Plan is not a Comparison fetch failure.
    expect(screen.queryByText("The comparison table has not loaded yet.")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await waitFor(() => {
      expect(screen.getByText("completed")).toBeInTheDocument();
    });

    expect(statusReadCount).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText("The run failed.")).not.toBeInTheDocument();
  });

  test("the Fixture checklist can run both selected variants into a two-row comparison", async () => {
    const generatedIds = [
      "11111111-0000-0000-0000-000000000000",
      "aaaaaaaa-0000-0000-0000-000000000000",
      "bbbbbbbb-0000-0000-0000-000000000000",
    ];
    vi.stubGlobal("crypto", {
      randomUUID: () => generatedIds.shift() ?? "cccccccc-0000-0000-0000-000000000000",
    });
    let storedRuns: ExperimentVariantRun[] = [];
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-11111111",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["baseline-all-off", "judge-observe"],
              plan_digest_sha512: "a".repeat(128),
              execution_mode: "fixture",
              variant_configurations: [],
            }),
        });
      }
      if (url.includes("/comparison")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ...comparison,
              experiment_id: "exp-11111111",
              rows: storedRuns.map((run) => ({
                ...comparison.rows[0],
                variant_id: run.variant_id,
                run_id: run.run_id,
                runtime_state: run.state,
              })),
            }),
        });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        if (typeof init.body !== "string") {
          throw new Error("expected a JSON string request body");
        }
        const body = JSON.parse(init.body) as {
          experiment_id: string;
          variant_id: string;
          run_id: string;
        };
        const running: ExperimentVariantRun = {
          ...runResult.run,
          run_id: body.run_id,
          experiment_id: body.experiment_id,
          variant_id: body.variant_id,
          state: "running",
          completed_at: null,
        };
        storedRuns.push(running);
        return Promise.resolve({ ok: true, json: () => Promise.resolve(running) });
      }
      const statusMatch = /\/runs\/(run-[^/]+)$/u.exec(url);
      if (statusMatch !== null) {
        const runId = statusMatch[1] ?? "";
        const existing = storedRuns.find((run) => run.run_id === runId);
        if (existing === undefined) {
          return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
        }
        const completed: ExperimentVariantRun = {
          ...existing,
          state: "completed",
          completed_at: "2026-01-01T00:00:01+00:00",
        };
        storedRuns = storedRuns.map((run) => (run.run_id === runId ? completed : run));
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...runResult, run: completed }),
        });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ experiment_id: "exp-11111111", runs: storedRuns }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Baseline"));
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Run: baseline-all-off/ }));
    await waitFor(() => {
      expect(storedRuns[0]?.state).toBe("completed");
    });
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await waitFor(() => {
      expect(document.querySelectorAll(".experiment-comparison-table tbody tr")).toHaveLength(2);
    });

    expect(storedRuns.map((run) => run.variant_id)).toEqual([
      "baseline-all-off",
      "judge-observe",
    ]);
    expect(screen.queryByText("The run failed.")).not.toBeInTheDocument();
  });

  test("a wrong Production live configuration surfaces the typed rejection and creates no row", async () => {
    const productionPresets: ExperimentPresets = {
      ...presets,
      variants: [
        {
          variant_id: "production-judge-repair-baseline",
          label: "Production: Main + Judge/Repair ENFORCE",
          components: [
            { component_key: "main", selector_id: "main.qwen3-4b-q4-k-m", mode: "active" },
            {
              component_key: "judge",
              selector_id: "judge.gemma-4-e2b-it-q4-0",
              mode: "enforce",
            },
            { component_key: "repair", selector_id: null, mode: "enforce" },
          ],
        },
      ],
    };
    const rejectionMessage =
      "variant_id 'production-judge-repair-baseline' declares a Configuration Live cannot currently satisfy for slot(s): judge";
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(productionPresets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-1",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["production-judge-repair-baseline"],
              plan_digest_sha512: "a".repeat(128),
              execution_mode: "production",
              variant_configurations: [],
            }),
        });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        return Promise.resolve({
          ok: false,
          json: () =>
            Promise.resolve({ code: "live_config_mismatch", message: rejectionMessage }),
        });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ experiment_id: "exp-1", runs: [] }),
        });
      }
      if (url.includes("/comparison")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...comparison, rows: [] }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Production: Main + Judge/Repair ENFORCE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Production: Main + Judge/Repair ENFORCE"));
    fireEvent.change(screen.getByLabelText("Execution mode"), { target: { value: "production" } });
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });
    fireEvent.click(
      screen.getByRole("button", { name: /Run: production-judge-repair-baseline/ }),
    );

    await waitFor(() => {
      expect(screen.getByText(rejectionMessage)).toBeInTheDocument();
    });
    expect(document.querySelectorAll(".experiment-comparison-table tbody tr")).toHaveLength(0);
    expect(screen.queryByText("The run failed.")).not.toBeInTheDocument();
  });

  test("after auto-tracking expires, GET-only recheck reaches Terminal and clears the tracking error", async () => {
    let backendState: ExperimentVariantRun["state"] = "running";
    const { trace } = installLongRunFetch(
      () => backendState,
      // Deliberately stale forever: even after the direct Run GET observes
      // Terminal, this slower list Response must not roll it back to running.
      () => "running",
    );
    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    vi.useFakeTimers();
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
      await vi.advanceTimersByTimeAsync(120_000);
      await Promise.resolve();
    });

    expect(screen.getByText("The run status could not be confirmed before the tracking deadline. Recheck the Backend result.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Recheck the same run" })).toBeInTheDocument();
    expect(trace.posts).toBe(1);

    backendState = "completed";
    fireEvent.click(screen.getByRole("button", { name: "Recheck the same run" }));
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.queryByText("The run status could not be confirmed before the tracking deadline. Recheck the Backend result.")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Recheck the same run" })).not.toBeInTheDocument();
    expect(trace.posts).toBe(1);
  });

  test("the timeout-boundary final list refresh clears tracking error when it already sees Terminal", async () => {
    const { trace } = installLongRunFetch(
      () => "running",
      (listReadCount) => (listReadCount >= 2 ? "completed" : "running"),
    );
    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    vi.useFakeTimers();
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
      await vi.advanceTimersByTimeAsync(120_000);
      await Promise.resolve();
    });

    expect(trace.listGets).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.queryByText("The run status could not be confirmed before the tracking deadline. Recheck the Backend result.")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Recheck the same run" })).not.toBeInTheDocument();
    expect(trace.posts).toBe(1);
  });

  test("a late older refresh cannot replace a newer Terminal comparison", async () => {
    const olderComparisonResponse = deferred<{
      ok: boolean;
      json: () => Promise<ExperimentComparison>;
    }>();
    const terminalRun = { ...runResult.run, state: "completed" as const };
    const runningRun = {
      ...runResult.run,
      state: "running" as const,
      completed_at: null,
    };
    let comparisonReads = 0;
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-1",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["judge-observe"],
              plan_digest_sha512: "a".repeat(128),
              execution_mode: "fixture",
              variant_configurations: [],
            }),
        });
      }
      if (url.includes("/comparison")) {
        comparisonReads += 1;
        if (comparisonReads === 1) {
          return olderComparisonResponse.promise;
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve(comparison) });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(runningRun) });
      }
      if (/\/runs\/[^/]+$/u.test(url)) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...runResult, run: terminalRun }),
        });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ experiment_id: "exp-1", runs: [terminalRun] }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));

    await waitFor(() => {
      expect(comparisonReads).toBe(2);
      expect(screen.getByText("pass")).toBeInTheDocument();
    });
    olderComparisonResponse.resolve({
      ok: true,
      json: () => Promise.resolve({ ...comparison, rows: [] }),
    });
    await act(async () => {
      await olderComparisonResponse.promise;
      await Promise.resolve();
    });

    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.getByText("pass")).toBeInTheDocument();
  });

  test("a late detail response for run A cannot overwrite selected run B evidence", async () => {
    const generatedIds = [
      "11111111-0000-0000-0000-000000000000",
      "aaaaaaaa-0000-0000-0000-000000000000",
      "bbbbbbbb-0000-0000-0000-000000000000",
    ];
    vi.stubGlobal("crypto", {
      randomUUID: () => generatedIds.shift() ?? "cccccccc-0000-0000-0000-000000000000",
    });
    const delayedADetail = deferred<{
      ok: boolean;
      json: () => Promise<ExperimentVariantRunResult>;
    }>();
    let storedRuns: ExperimentVariantRun[] = [];
    const statusReads = new Map<string, number>();

    const detailResult = (
      run: ExperimentVariantRun,
      componentKey: "judge" | "guard",
    ): ExperimentVariantRunResult => ({
      ...runResult,
      run,
      invocations: [
        {
          component_key: componentKey,
          called: true,
          outcome: "completed",
          mutation_count: 1,
          evidence_count: 1,
          authority_exercised: true,
        },
      ],
    });

    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.includes("/presets")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(presets) });
      }
      if (url.includes("/plans")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              experiment_id: "exp-11111111",
              case_id: "case-1",
              case_revision: "rev-1",
              variant_ids: ["baseline-all-off", "judge-observe"],
              plan_digest_sha512: "a".repeat(128),
              execution_mode: "fixture",
              variant_configurations: [],
            }),
        });
      }
      if (url.includes("/comparison")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ...comparison,
              experiment_id: "exp-11111111",
              rows: storedRuns.map((run) => ({
                ...comparison.rows[0],
                run_id: run.run_id,
                variant_id: run.variant_id,
                execution_mode: run.execution_mode,
                raw_evidence_pointer: run.run_id,
              })),
            }),
        });
      }
      if (url.includes("/runs") && init?.method === "POST" && !url.includes("/cancel")) {
        if (typeof init.body !== "string") {
          throw new Error("expected a JSON string request body");
        }
        const body = JSON.parse(init.body) as {
          experiment_id: string;
          variant_id: string;
          run_id: string;
        };
        const running: ExperimentVariantRun = {
          ...runResult.run,
          experiment_id: body.experiment_id,
          variant_id: body.variant_id,
          run_id: body.run_id,
          execution_mode: body.variant_id === "baseline-all-off" ? "fixture" : "production",
          state: "running",
          completed_at: null,
        };
        storedRuns.push(running);
        return Promise.resolve({ ok: true, json: () => Promise.resolve(running) });
      }
      const statusMatch = /\/runs\/(run-[^/]+)$/u.exec(url);
      if (statusMatch !== null) {
        const runId = statusMatch[1] ?? "";
        const readCount = (statusReads.get(runId) ?? 0) + 1;
        statusReads.set(runId, readCount);
        const existing = storedRuns.find((run) => run.run_id === runId);
        if (existing === undefined) {
          return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
        }
        if (readCount === 1) {
          const completed = {
            ...existing,
            state: "completed" as const,
            completed_at: "2026-01-01T00:00:01+00:00",
          };
          storedRuns = storedRuns.map((run) => (run.run_id === runId ? completed : run));
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve(
                detailResult(
                  completed,
                  completed.variant_id === "baseline-all-off" ? "judge" : "guard",
                ),
              ),
          });
        }
        if (existing.variant_id === "baseline-all-off") {
          return delayedADetail.promise;
        }
        if (readCount >= 3) {
          return Promise.reject(new Error("detail read failed"));
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(detailResult(existing, "guard")),
        });
      }
      if (url.includes("/experiments/") && url.includes("/runs")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ experiment_id: "exp-11111111", runs: storedRuns }),
        });
      }
      return Promise.resolve({ ok: false, json: () => Promise.resolve({}) });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ExperimentPanel language="en" open onClose={() => {}} />);
    await waitFor(() => {
      expect(screen.getByText("Judge OBSERVE")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByLabelText("Baseline"));
    fireEvent.click(screen.getByLabelText("Judge OBSERVE"));
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));
    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Run: baseline-all-off/ }));
    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Detail evidence (by component)" })).toHaveLength(1);
    });
    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));
    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Detail evidence (by component)" })).toHaveLength(2);
    });

    const detailButtons = screen.getAllByRole("button", {
      name: "Detail evidence (by component)",
    });
    fireEvent.click(detailButtons[0]!);
    fireEvent.click(detailButtons[1]!);
    await waitFor(() => {
      expect(screen.getByText("guard")).toBeInTheDocument();
      expect(
        screen.getByText(
          "This result comes from a real Production Turn. Real Main/Judge/Guard calls may have happened.",
        ),
      ).toBeInTheDocument();
    });

    const runA = storedRuns.find((run) => run.variant_id === "baseline-all-off");
    expect(runA).toBeDefined();
    delayedADetail.resolve({
      ok: true,
      json: () => Promise.resolve(detailResult(runA!, "judge")),
    });
    await act(async () => {
      await delayedADetail.promise;
      await Promise.resolve();
    });

    expect(screen.getByText("guard")).toBeInTheDocument();
    expect(
      screen.getByText(
        "This result comes from a real Production Turn. Real Main/Judge/Guard calls may have happened.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(
        "This result comes from Fixture Actors only. No real Main, Judge, Guard, or Repair call was ever made.",
      ),
    ).not.toBeInTheDocument();

    // A later failure for the currently selected B is handled and clears
    // the previously displayed A detail instead of leaving it mislabeled.
    fireEvent.click(detailButtons[0]!);
    await waitFor(() => {
      expect(
        screen.getByText(
          "This result comes from Fixture Actors only. No real Main, Judge, Guard, or Repair call was ever made.",
        ),
      ).toBeInTheDocument();
    });
    fireEvent.click(detailButtons[1]!);
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(
      screen.queryByText(
        "This result comes from Fixture Actors only. No real Main, Judge, Guard, or Repair call was ever made.",
      ),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(
        "This result comes from a real Production Turn. Real Main/Judge/Guard calls may have happened.",
      ),
    ).not.toBeInTheDocument();
  });
});
