import { useEffect, useRef, useState } from "react";
import {
  applyJudgeMode,
  applyRecordingMode,
  applyRepairMode,
  fetchFeatureModesStatus,
} from "../api/client";
import { translate } from "../i18n/translations";
import type {
  FeatureModesStatus,
  JudgeModeSnapshot,
  RecordingOutcome,
  UiLanguage,
} from "../types";

// Self-contained fetch/apply, same rationale as RuntimeModelStatusPanel:
// each toggle here is an independent CAS-free Mode change with no other
// panel depending on the result (Acceptance P6-ACC-025: Judge/Repair/
// Recording Modes are independent of each other and of Main/Guardrail
// Governance Mode).
type LoadCapability = "loading" | "ready" | "failed";

const JUDGE_MODES = ["off", "observe", "enforce"] as const;
const REPAIR_MODES = ["off", "observe", "enforce"] as const;
const RECORDING_MODES = ["off", "metadata", "full"] as const;

interface FeatureModesPanelProps {
  language: UiLanguage;
  visible: boolean;
}

function mergeCanonicalStatus(
  current: FeatureModesStatus | null,
  incoming: FeatureModesStatus,
): FeatureModesStatus {
  if (current === null) {
    return incoming;
  }
  const chooseIncoming = <T extends { revision: number | null }>(present: T, next: T): T =>
    (next.revision ?? -1) >= (present.revision ?? -1) ? next : present;
  return {
    judge: chooseIncoming(current.judge, incoming.judge),
    repair: chooseIncoming(current.repair, incoming.repair),
    recording: chooseIncoming(current.recording, incoming.recording),
  };
}

export default function FeatureModesPanel({ language, visible }: FeatureModesPanelProps) {
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [status, setStatus] = useState<FeatureModesStatus | null>(null);
  const [resultText, setResultText] = useState("");
  const mutationQueueRef = useRef<Promise<void>>(Promise.resolve());

  const runFetch = () => {
    fetchFeatureModesStatus()
      .then((next) => {
        setStatus((current) => mergeCanonicalStatus(current, next));
        setCapability("ready");
      })
      .catch(() => {
        setStatus(null);
        setCapability("failed");
      });
  };

  const refresh = () => {
    setCapability("loading");
    runFetch();
  };

  useEffect(() => {
    if (!visible) return;
    runFetch();
    const intervalId = window.setInterval(runFetch, 2_000);
    return () => {
      window.clearInterval(intervalId);
    };
  }, [visible]);

  if (!visible) {
    return null;
  }

  const statusKey =
    capability === "loading"
      ? "featureModesLoading"
      : capability === "ready"
        ? "featureModesReady"
        : "featureModesFailed";

  const applyOne = (
    apply: (mode: string) => Promise<FeatureModesStatus>,
    requestedMode: string,
  ) => {
    const run = async (): Promise<void> => {
      try {
        const next = await apply(requestedMode);
        setStatus((current) => mergeCanonicalStatus(current, next));
        setResultText(translate(language, "featureModesApplySuccess"));
      } catch {
        setResultText(translate(language, "featureModesApplyFailed"));
        try {
          const canonical = await fetchFeatureModesStatus();
          setStatus((current) => mergeCanonicalStatus(current, canonical));
        } catch {
          // Keep the last verified snapshot and the original apply failure.
        }
      }
    };
    mutationQueueRef.current = mutationQueueRef.current.then(run, run);
  };

  const renderModeGroup = (
    idPrefix: string,
    labelKey: Parameters<typeof translate>[1],
    modes: readonly string[],
    current: string | null,
    apply: (mode: string) => Promise<FeatureModesStatus>,
  ) => (
    <div className="configuration-controls">
      <div className="configuration-toggle" role="radiogroup" aria-label={translate(language, labelKey)}>
        <span id={`${idPrefix}-label`}>{translate(language, labelKey)}</span>
        {modes.map((mode) => (
          <button
            key={mode}
            id={`${idPrefix}-${mode}`}
            className="secondary"
            type="button"
            role="radio"
            aria-checked={current === mode}
            onClick={() => {
              applyOne(apply, mode);
            }}
          >
            {mode}
          </button>
        ))}
      </div>
    </div>
  );

  const judgeStateKey = (state: JudgeModeSnapshot["state"]): Parameters<typeof translate>[1] => {
    switch (state) {
      // P6-CODEX-031 (Fourth Rework): three distinct in-flight sub-states
      // (never a single generic "running") — the exact P6-OBS-004 Runtime
      // State vocabulary, genuinely observable here rather than collapsed
      // back down to one label at this display layer.
      case "judging":
        return "featureModesJudgeStateJudging";
      case "repairing":
        return "featureModesJudgeStateRepairing";
      case "rejudging":
        return "featureModesJudgeStateRejudging";
      case "completed":
        return "featureModesJudgeStateCompleted";
      case "queued_or_skipped":
        return "featureModesJudgeStateSkipped";
      case "failed":
        return "featureModesJudgeStateFailed";
      case "cancelled":
        return "featureModesJudgeStateCancelled";
      case "degraded":
        return "featureModesJudgeStateDegraded";
      default:
        return "featureModesJudgeStateIdle";
    }
  };

  const renderJudgeStatus = (judge: JudgeModeSnapshot) => {
    const historical = judge.last_result === null && judge.historical_last_result != null;
    const lastResult = judge.last_result ?? judge.historical_last_result ?? null;
    return (
      <div id="feature-modes-judge-status" className="configuration-result">
      <p id="feature-modes-judge-state">
        {translate(language, "featureModesJudgeStateLabel")}:{" "}
        {translate(language, judgeStateKey(judge.state))}
      </p>
      {lastResult === null ? null : (
        <div id="feature-modes-judge-last-result">
          <p>
            {translate(language, "featureModesJudgeResultLabel")}
            {historical || judge.current_request_id !== lastResult.request_id
              ? ` ${translate(language, "featureModesJudgeResultStale")}`
              : ""}
          </p>
          <ul>
            <li>Request ID: {lastResult.request_id}</li>
            <li>
              {translate(language, "featureModesJudgeRecommendation")}: {lastResult.recommendation}
            </li>
            <li>
              {translate(language, "featureModesJudgeConfidence")}:{" "}
              {lastResult.confidence.toFixed(2)}
            </li>
            <li>
              {translate(language, "featureModesJudgeExecutionState")}: {lastResult.execution_state}
            </li>
            {lastResult.started_at == null ? null : <li>Started: {lastResult.started_at}</li>}
            {lastResult.completed_at == null ? null : <li>Completed: {lastResult.completed_at}</li>}
            <li>Configured Provider: {lastResult.configured_provider ?? "none"}</li>
            <li>Active Provider: {lastResult.active_provider ?? "none"}</li>
            <li>Executed Provider: {lastResult.executed_provider ?? "none"}</li>
            {lastResult.budget_profile == null ? null : (
              <li>Budget: {lastResult.budget_profile}</li>
            )}
            {lastResult.frozen_judge_mode == null ? null : (
              <li>
                Frozen Modes: main={lastResult.frozen_main_mode ?? "unknown"}, guard=
                {lastResult.frozen_guard_mode ?? "unknown"}, judge={lastResult.frozen_judge_mode},
                repair={lastResult.frozen_repair_mode ?? "off"}, recording=
                {lastResult.recording_mode ?? "off"}
              </li>
            )}
            {lastResult.criteria_selected === undefined ? null : (
              <li>
                Criteria: selected={lastResult.criteria_selected}, evaluated=
                {lastResult.criteria_evaluated ?? 0}, passed={lastResult.criteria_passed ?? 0},
                deviated={lastResult.criteria_deviated ?? 0}, unknown=
                {lastResult.criteria_unknown ?? 0}, not_applicable=
                {lastResult.criteria_not_applicable ?? 0}, deferred=
                {lastResult.criteria_deferred ?? 0}
              </li>
            )}
            {lastResult.failure_reason === null ? null : (
              <li>
                {translate(language, "featureModesJudgeFailureReason")}: {lastResult.failure_reason}
              </li>
            )}
            {lastResult.failure_message == null ? null : <li>{lastResult.failure_message}</li>}
            {lastResult.repair_eligibility === null ? null : (
              <li>
                {translate(language, "featureModesRepairEligibility")}: {lastResult.repair_eligibility}
              </li>
            )}
            {lastResult.repair_outcome === null ? null : (
              <li>
                {translate(language, "featureModesRepairOutcome")}: {lastResult.repair_outcome}
              </li>
            )}
            {lastResult.repair_accepted === null ? null : (
              <li>
                {translate(language, "featureModesRepairAccepted")}:{" "}
                {String(lastResult.repair_accepted)}
              </li>
            )}
            {lastResult.repair_new_turn_id === null ? null : (
              <li>
                {translate(language, "featureModesRepairNewTurn")}: {lastResult.repair_new_turn_id}
              </li>
            )}
            {lastResult.presentation_outcome === undefined ||
            lastResult.presentation_outcome === null ? null : (
              <li>
                {translate(language, "featureModesPresentationOutcome")}: {lastResult.presentation_outcome}
              </li>
            )}
            {lastResult.candidate_withheld ? (
              <li>{translate(language, "featureModesCandidateWithheld")}</li>
            ) : null}
          </ul>
        </div>
      )}
      </div>
    );
  };

  const renderRecordingOutcome = (
    idPrefix: string,
    labelKey: Parameters<typeof translate>[1],
    outcome: RecordingOutcome | null,
  ) => (
    <p id={idPrefix}>
      {translate(language, labelKey)}:{" "}
      {outcome === null
        ? translate(language, "featureModesRecordingOutcomeNone")
        : outcome.ok
          ? translate(language, "featureModesRecordingOutcomeOk")
          : `${translate(language, "featureModesRecordingOutcomeDegraded")} (${outcome.degraded_reason ?? ""})`}
      {outcome === null ? "" : ` [${outcome.request_id}]`}
    </p>
  );

  const renderRecordingCorrelation = () => {
    if (status === null) return null;
    const judge = status.judge;
    const result = judge.last_result;
    const derivedRequestId =
      result !== null && judge.current_request_id === result.request_id ? result.request_id : null;
    const correlation = status.recording.correlation;
    const requestId = correlation?.request_id ?? derivedRequestId;
    const turnOutcome = status.recording.last_outcome;
    const evidenceOutcome = status.recording.judge_evidence_last_outcome;
    const turnCurrent = correlation?.current_turn ?? (
      turnOutcome !== null && turnOutcome.request_id === requestId ? turnOutcome : null
    );
    const evidenceCurrent = correlation?.current_judge_evidence ?? (
      evidenceOutcome !== null && evidenceOutcome.request_id === requestId ? evidenceOutcome : null
    );
    const unmatched = [
      turnOutcome !== null && turnOutcome.request_id !== requestId
        ? { kind: "turn" as const, outcome: turnOutcome }
        : null,
      evidenceOutcome !== null && evidenceOutcome.request_id !== requestId
        ? { kind: "judge_evidence" as const, outcome: evidenceOutcome }
        : null,
    ].filter(
      (
        item,
      ): item is {
        kind: "turn" | "judge_evidence";
        outcome: RecordingOutcome;
      } => item !== null,
    );
    const current = correlation?.current ?? null;
    return (
      <div id="feature-modes-recording-correlation-summary" className="configuration-result">
        <p id="feature-modes-recording-correlation-request">
          Request ID: {requestId ?? "none"}
        </p>
        {current === null ? null : (
          <p id="feature-modes-recording-correlation-status">
            Status: {current.status}
            {current.started_at ? ` (started ${current.started_at})` : ""}
            {current.completed_at ? ` (completed ${current.completed_at})` : ""}
          </p>
        )}
        {renderRecordingOutcome(
          "feature-modes-recording-turn-outcome",
          "featureModesRecordingLastOutcomeLabel",
          turnCurrent,
        )}
        {renderRecordingOutcome(
          "feature-modes-recording-judge-evidence-outcome",
          "featureModesJudgeEvidenceOutcomeLabel",
          evidenceCurrent,
        )}
        {unmatched.length === 0 ? null : (
          <ul id="feature-modes-recording-unmatched">
            {unmatched.map(({ kind, outcome }) => (
              <li key={`${kind}:${outcome.request_id}:${outcome.degraded_reason ?? "ok"}`}>
                {translate(
                  language,
                  kind === "turn"
                    ? "featureModesHistoricalTurnRecording"
                    : "featureModesHistoricalJudgeEvidenceRecording",
                )}
                : {outcome.request_id}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  };

  return (
    <section
      id="feature-modes-panel"
      className="configuration-panel"
      aria-label={translate(language, "featureModesTitle")}
    >
      <div className="configuration-panel-header">
        <div>
          <h2 id="feature-modes-title">{translate(language, "featureModesTitle")}</h2>
          <p id="feature-modes-note">{translate(language, "featureModesNote")}</p>
        </div>
        <button
          id="feature-modes-refresh"
          className="secondary"
          type="button"
          disabled={capability === "loading"}
          onClick={refresh}
        >
          {translate(language, "featureModesRefresh")}
        </button>
      </div>
      <p id="feature-modes-status-line">{translate(language, statusKey)}</p>
      {status === null ? null : (
        <>
          {renderModeGroup(
            "feature-modes-judge",
            "featureModesJudgeLabel",
            JUDGE_MODES,
            status.judge.current_mode,
            applyJudgeMode,
          )}
          {renderJudgeStatus(status.judge)}
          {renderModeGroup(
            "feature-modes-repair",
            "featureModesRepairLabel",
            REPAIR_MODES,
            status.repair.current_mode,
            applyRepairMode,
          )}
          {renderModeGroup(
            "feature-modes-recording",
            "featureModesRecordingLabel",
            RECORDING_MODES,
            status.recording.current_mode,
            applyRecordingMode,
          )}
          {renderRecordingCorrelation()}
          <pre id="feature-modes-result" className="configuration-result" aria-live="polite">
            {resultText}
          </pre>
        </>
      )}
    </section>
  );
}
