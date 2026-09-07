import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import type { ExperimentComparison, ExperimentPresets, ExperimentVariantRunResult } from "../types";
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

describe("ExperimentPanel", () => {
  beforeEach(() => {
    vi.stubGlobal("crypto", { randomUUID: () => "00000000-0000-0000-0000-000000000000" });
  });

  afterEach(() => {
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
    fireEvent.click(screen.getByRole("button", { name: "Create plan" }));

    await waitFor(() => {
      expect(screen.getByText("Plan created. Run each variant below.")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Run: judge-observe/ }));

    await waitFor(() => {
      expect(screen.getByText("judge-observe")).toBeInTheDocument();
      expect(screen.getByText("completed")).toBeInTheDocument();
    });

    // The Comparison Report's own Evaluation column shows the real
    // Deterministic Observation outcome, not merely the Run State.
    await waitFor(() => {
      expect(screen.getByText("pass")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Detail evidence (by component)" }));

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
});
