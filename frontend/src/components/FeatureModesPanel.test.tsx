import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import FeatureModesPanel from "./FeatureModesPanel";
import type { FeatureModesStatus } from "../types";

const allOffStatus: FeatureModesStatus = {
  judge: {
    enabled: true,
    revision: 1,
    current_mode: "off",
    state: "idle",
    current_request_id: null,
    last_result: null,
  },
  repair: { enabled: true, revision: 1, current_mode: "off" },
  recording: {
    enabled: true,
    revision: 1,
    current_mode: "off",
    last_outcome: null,
    judge_evidence_last_outcome: null,
  },
};

function mockFetchOnce(body: unknown, ok = true) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok, json: () => Promise.resolve(body) }),
  );
}

describe("FeatureModesPanel", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  test("renders nothing when not visible, and issues no fetch", () => {
    mockFetchOnce(allOffStatus);
    render(<FeatureModesPanel language="en" visible={false} />);
    expect(document.querySelector("#feature-modes-panel")).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });

  test("shows all three modes as off by default", async () => {
    mockFetchOnce(allOffStatus);
    render(<FeatureModesPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-off")).not.toBeNull();
    });

    expect(document.querySelector("#feature-modes-judge-off")?.getAttribute("aria-checked")).toBe(
      "true",
    );
    expect(
      document.querySelector("#feature-modes-repair-off")?.getAttribute("aria-checked"),
    ).toBe("true");
    expect(
      document.querySelector("#feature-modes-recording-off")?.getAttribute("aria-checked"),
    ).toBe("true");
  });

  test("clicking Judge Enforce applies only the Judge mode and shows success", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(allOffStatus) })
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            ...allOffStatus,
            judge: { ...allOffStatus.judge, revision: 2, current_mode: "enforce" },
          }),
      });
    vi.stubGlobal("fetch", fetchMock);
    render(<FeatureModesPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-enforce")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#feature-modes-judge-enforce") as Element);

    await waitFor(() => {
      expect(screen.getByText("Applied.")).toBeTruthy();
    });
    const secondCall = fetchMock.mock.calls[1];
    expect(secondCall).toBeDefined();
    const [url, init] = secondCall as [string, { body: string }];
    expect(url).toBe("/api/v5/feature-modes/judge");
    expect(JSON.parse(init.body)).toEqual({ requested_mode: "enforce" });
    expect(document.querySelector("#feature-modes-judge-apply")).toBeNull();
  });

  test("rapid clicks are serialized and converge to the last server-canonical mode", async () => {
    const observeStatus = {
      ...allOffStatus,
      judge: { ...allOffStatus.judge, revision: 2, current_mode: "observe" },
    };
    const enforceStatus = {
      ...allOffStatus,
      judge: { ...allOffStatus.judge, revision: 3, current_mode: "enforce" },
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(allOffStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(observeStatus) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(enforceStatus) });
    vi.stubGlobal("fetch", fetchMock);
    render(<FeatureModesPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-observe")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#feature-modes-judge-observe") as Element);
    fireEvent.click(document.querySelector("#feature-modes-judge-enforce") as Element);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-enforce")).toHaveAttribute(
        "aria-checked",
        "true",
      );
    });
    const postedModes = fetchMock.mock.calls.slice(1).map((call) => {
      const init = call[1] as RequestInit;
      return (JSON.parse(init.body as string) as { requested_mode: string }).requested_mode;
    });
    expect(postedModes).toEqual(["observe", "enforce"]);
  });

  test("P6-CODEX-012: displays the current Judge Run state, last result, and Repair outcome", async () => {
    const statusWithJudgeResult: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        enabled: true,
        revision: 3,
        current_mode: "enforce",
        state: "completed",
        current_request_id: "req-42",
        last_result: {
          request_id: "req-42",
          judge_role: "main_self",
          recommendation: "needs_repair",
          confidence: 0.4,
          execution_state: "completed",
          failure_reason: null,
          repair_eligibility: "eligible",
          repair_outcome: "improved",
          repair_accepted: true,
          repair_new_turn_id: "turn-repaired-1",
          presentation_outcome: "repair_accepted",
          candidate_withheld: true,
          started_at: "2026-08-26T01:00:00+00:00",
          completed_at: "2026-08-26T01:00:02+00:00",
          frozen_main_mode: "observe",
          frozen_guard_mode: "enforce",
          frozen_judge_mode: "enforce",
          frozen_repair_mode: "enforce",
          recording_mode: "metadata",
          configured_provider: "judge.selene",
          active_provider: "judge.selene",
          budget_profile: "local_macos_selene_judge_v1",
          criteria_selected: 4,
          criteria_evaluated: 4,
          criteria_passed: 3,
          criteria_deviated: 1,
          criteria_unknown: 0,
        },
      },
    };
    mockFetchOnce(statusWithJudgeResult);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-state")).not.toBeNull();
    });

    expect(document.querySelector("#feature-modes-judge-state")?.textContent).toContain(
      "Completed",
    );
    const lastResult = document.querySelector("#feature-modes-judge-last-result");
    expect(lastResult?.textContent).toContain("needs_repair");
    expect(lastResult?.textContent).toContain("0.40");
    expect(lastResult?.textContent).toContain("eligible");
    expect(lastResult?.textContent).toContain("improved");
    expect(lastResult?.textContent).toContain("true");
    expect(lastResult?.textContent).toContain("turn-repaired-1");
    expect(lastResult?.textContent).toContain("repair_accepted");
    expect(lastResult?.textContent).toContain("failed original candidate was withheld");
    expect(lastResult?.textContent).toContain("req-42");
    expect(lastResult?.textContent).toContain("judge.selene");
    expect(lastResult?.textContent).toContain("local_macos_selene_judge_v1");
    expect(lastResult?.textContent).toContain("selected=4");
  });

  test("P6-CODEX-012: a stale last result while a Run is in flight is labeled as such", async () => {
    const statusWithRunningJudge: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        enabled: true,
        revision: 4,
        current_mode: "observe",
        state: "judging",
        current_request_id: "req-99",
        last_result: null,
        historical_last_result: {
          request_id: "req-98",
          judge_role: "main_self",
          recommendation: "accept",
          confidence: 0.9,
          execution_state: "completed",
          failure_reason: null,
          repair_eligibility: null,
          repair_outcome: null,
          repair_accepted: null,
          repair_new_turn_id: null,
        },
      },
    };
    mockFetchOnce(statusWithRunningJudge);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-state")).not.toBeNull();
    });

    expect(document.querySelector("#feature-modes-judge-state")?.textContent).toContain(
      "Judging",
    );
    expect(document.querySelector("#feature-modes-judge-last-result")?.textContent).toContain(
      "from a previous Turn",
    );
  });

  test("polls only while visible and cleans up when hidden", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: () => Promise.resolve(allOffStatus) });
    vi.stubGlobal("fetch", fetchMock);
    const { rerender } = render(<FeatureModesPanel language="en" visible={true} />);

    vi.runAllTicks();
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await vi.advanceTimersByTimeAsync(2_000);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    rerender(<FeatureModesPanel language="en" visible={false} />);
    await vi.advanceTimersByTimeAsync(4_000);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  test("P6-CODEX-031: judging/repairing/rejudging each render distinct text, never collapsed to one label", async () => {
    for (const [state, expectedText] of [
      ["judging", "Judging"],
      ["repairing", "Repairing"],
      ["rejudging", "Rejudging"],
    ] as const) {
      const statusWithStage: FeatureModesStatus = {
        ...allOffStatus,
        judge: {
          enabled: true,
          revision: 4,
          current_mode: "enforce",
          state,
          current_request_id: "req-stage-1",
          last_result: null,
        },
      };
      mockFetchOnce(statusWithStage);
      const { unmount } = render(<FeatureModesPanel language="en" visible={true} />);

      await waitFor(() => {
        expect(document.querySelector("#feature-modes-judge-state")).not.toBeNull();
      });
      expect(document.querySelector("#feature-modes-judge-state")?.textContent).toContain(
        expectedText,
      );

      unmount();
      vi.unstubAllGlobals();
    }
  });

  test("P6-CODEX-012: displays Recording last-outcome and a Degraded reason for Judge Evidence", async () => {
    const statusWithRecordingOutcomes: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        ...allOffStatus.judge,
        current_request_id: "req-1",
        last_result: {
          request_id: "req-1",
          judge_role: "main_self",
          recommendation: "accept",
          confidence: 1,
          execution_state: "completed",
          failure_reason: null,
          repair_eligibility: null,
          repair_outcome: null,
          repair_accepted: null,
          repair_new_turn_id: null,
        },
      },
      recording: {
        enabled: true,
        revision: 2,
        current_mode: "full",
        last_outcome: { request_id: "req-1", ok: true, degraded_reason: null },
        judge_evidence_last_outcome: {
          request_id: "req-1",
          ok: false,
          degraded_reason: "RecordingQuotaExceeded: over limit",
        },
      },
    };
    mockFetchOnce(statusWithRecordingOutcomes);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-recording-turn-outcome")).not.toBeNull();
    });

    expect(
      document.querySelector("#feature-modes-recording-turn-outcome")?.textContent,
    ).toContain("Recorded successfully");
    const evidenceOutcome = document.querySelector(
      "#feature-modes-recording-judge-evidence-outcome",
    );
    expect(evidenceOutcome?.textContent).toContain("Could not be recorded");
    expect(evidenceOutcome?.textContent).toContain("RecordingQuotaExceeded: over limit");
    expect(document.querySelector("#feature-modes-recording-correlation-summary")).not.toBeNull();
  });

  test("renders unavailable providers explicitly as none", async () => {
    const statusWithNoProviders: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        ...allOffStatus.judge,
        current_request_id: "req-none",
        last_result: {
          request_id: "req-none",
          judge_role: "unavailable",
          recommendation: "unknown",
          confidence: 0,
          execution_state: "failed",
          failure_reason: "judge_provider_unavailable",
          repair_eligibility: null,
          repair_outcome: null,
          repair_accepted: null,
          repair_new_turn_id: null,
          configured_provider: null,
          active_provider: null,
          executed_provider: null,
        },
      },
    };
    mockFetchOnce(statusWithNoProviders);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-judge-last-result")).not.toBeNull();
    });
    const lastResult = document.querySelector("#feature-modes-judge-last-result");
    expect(lastResult?.textContent).toContain("Configured Provider: none");
    expect(lastResult?.textContent).toContain("Active Provider: none");
    expect(lastResult?.textContent).toContain("Executed Provider: none");
  });

  test("keeps a different recording request out of the current correlation", async () => {
    const statusWithUnmatchedRecording: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        ...allOffStatus.judge,
        current_mode: "observe",
        state: "completed",
        current_request_id: "req-current",
        last_result: {
          request_id: "req-current",
          judge_role: "main_self",
          recommendation: "accept",
          confidence: 1,
          execution_state: "completed",
          failure_reason: null,
          repair_eligibility: null,
          repair_outcome: null,
          repair_accepted: null,
          repair_new_turn_id: null,
        },
      },
      recording: {
        ...allOffStatus.recording,
        last_outcome: { request_id: "req-old", ok: true, degraded_reason: null },
        judge_evidence_last_outcome: null,
      },
    };
    mockFetchOnce(statusWithUnmatchedRecording);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-recording-unmatched")).not.toBeNull();
    });
    expect(document.querySelector("#feature-modes-recording-turn-outcome")?.textContent).toContain(
      "No record yet",
    );
    expect(document.querySelector("#feature-modes-recording-unmatched")?.textContent).toContain(
      "req-old",
    );
    expect(document.querySelector("#feature-modes-recording-unmatched")?.textContent).toContain(
      "Historical / unmatched Turn recording",
    );
  });

  test("labels historical Turn and Judge Evidence separately even when request ids match", async () => {
    const statusWithTwoHistoricalRecords: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        ...allOffStatus.judge,
        current_request_id: "req-current",
      },
      recording: {
        ...allOffStatus.recording,
        last_outcome: { request_id: "req-old", ok: true, degraded_reason: null },
        judge_evidence_last_outcome: {
          request_id: "req-old",
          ok: true,
          degraded_reason: null,
        },
      },
    };
    mockFetchOnce(statusWithTwoHistoricalRecords);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-recording-unmatched")).not.toBeNull();
    });
    const historical = document.querySelector("#feature-modes-recording-unmatched")?.textContent;
    expect(historical).toContain("Historical / unmatched Turn recording: req-old");
    expect(historical).toContain("Historical / unmatched Judge Evidence recording: req-old");
  });

  test("P6-CODEX-077: uses the server-computed correlation as the current Turn even when Judge never ran", async () => {
    const statusWithServerCorrelation: FeatureModesStatus = {
      ...allOffStatus,
      judge: {
        ...allOffStatus.judge,
        current_mode: "off",
        current_request_id: null,
      },
      recording: {
        ...allOffStatus.recording,
        current_mode: "full",
        last_outcome: { request_id: "req-77", ok: true, degraded_reason: null },
        judge_evidence_last_outcome: null,
        correlation: {
          request_id: "req-77",
          current: {
            request_id: "req-77",
            status: "completed",
            started_at: "t0",
            completed_at: "t1",
            judge_result: null,
            turn_recording: { request_id: "req-77", ok: true, degraded_reason: null },
            judge_evidence_recording: null,
          },
          current_turn: { request_id: "req-77", ok: true, degraded_reason: null },
          current_judge_evidence: null,
          historical_or_unmatched: [],
        },
      },
    };
    mockFetchOnce(statusWithServerCorrelation);
    render(<FeatureModesPanel language="en" visible={true} />);

    await waitFor(() => {
      expect(document.querySelector("#feature-modes-recording-correlation-request")).not.toBeNull();
    });
    expect(
      document.querySelector("#feature-modes-recording-correlation-request")?.textContent,
    ).toContain("req-77");
    expect(document.querySelector("#feature-modes-recording-turn-outcome")?.textContent).not.toContain(
      "No record yet",
    );
    expect(document.querySelector("#feature-modes-recording-unmatched")).toBeNull();
    expect(
      document.querySelector("#feature-modes-recording-correlation-status")?.textContent,
    ).toContain("completed");
  });

  test("a failed apply re-fetches canonical state and never leaves an optimistic selection", async () => {
    const canonical = {
      ...allOffStatus,
      recording: { ...allOffStatus.recording, revision: 2, current_mode: "metadata" },
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(allOffStatus) })
      .mockResolvedValueOnce({ ok: false, json: () => Promise.resolve({ code: "boom" }) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(canonical) });
    vi.stubGlobal("fetch", fetchMock);
    render(<FeatureModesPanel language="en" visible={true} />);
    await waitFor(() => {
      expect(document.querySelector("#feature-modes-recording-full")).not.toBeNull();
    });

    fireEvent.click(document.querySelector("#feature-modes-recording-full") as Element);

    await waitFor(() => {
      expect(screen.getByText("Failed to apply.")).toBeTruthy();
    });
    expect(document.querySelector("#feature-modes-recording-full")).toHaveAttribute(
      "aria-checked",
      "false",
    );
    expect(document.querySelector("#feature-modes-recording-metadata")).toHaveAttribute(
      "aria-checked",
      "true",
    );
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
});
