import { useEffect, useState } from "react";
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

export default function FeatureModesPanel({ language, visible }: FeatureModesPanelProps) {
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [status, setStatus] = useState<FeatureModesStatus | null>(null);
  const [resultText, setResultText] = useState("");

  const runFetch = () => {
    fetchFeatureModesStatus()
      .then((next) => {
        setStatus(next);
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
    if (visible) {
      runFetch();
    }
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
    apply(requestedMode)
      .then((next) => {
        setStatus(next);
        setResultText(translate(language, "featureModesApplySuccess"));
      })
      .catch(() => {
        setResultText(translate(language, "featureModesApplyFailed"));
      });
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

  const renderJudgeStatus = (judge: JudgeModeSnapshot) => (
    <div id="feature-modes-judge-status" className="configuration-result">
      <p id="feature-modes-judge-state">
        {translate(language, "featureModesJudgeStateLabel")}:{" "}
        {translate(language, judgeStateKey(judge.state))}
      </p>
      {judge.last_result === null ? null : (
        <div id="feature-modes-judge-last-result">
          <p>
            {translate(language, "featureModesJudgeResultLabel")}
            {/* P6-CODEX-020 (Third Rework): staleness is judged by comparing
                Request Identity, not by `state === "running"` alone —
                `queued_or_skipped` can just as validly leave `last_result`
                referring to an earlier, different Turn. */}
            {judge.current_request_id !== judge.last_result.request_id
              ? ` ${translate(language, "featureModesJudgeResultStale")}`
              : ""}
          </p>
          <ul>
            <li>
              {translate(language, "featureModesJudgeRecommendation")}: {judge.last_result.recommendation}
            </li>
            <li>
              {translate(language, "featureModesJudgeConfidence")}:{" "}
              {judge.last_result.confidence.toFixed(2)}
            </li>
            <li>
              {translate(language, "featureModesJudgeExecutionState")}: {judge.last_result.execution_state}
            </li>
            {judge.last_result.failure_reason === null ? null : (
              <li>
                {translate(language, "featureModesJudgeFailureReason")}: {judge.last_result.failure_reason}
              </li>
            )}
            {judge.last_result.repair_eligibility === null ? null : (
              <li>
                {translate(language, "featureModesRepairEligibility")}: {judge.last_result.repair_eligibility}
              </li>
            )}
            {judge.last_result.repair_outcome === null ? null : (
              <li>
                {translate(language, "featureModesRepairOutcome")}: {judge.last_result.repair_outcome}
              </li>
            )}
            {judge.last_result.repair_accepted === null ? null : (
              <li>
                {translate(language, "featureModesRepairAccepted")}:{" "}
                {String(judge.last_result.repair_accepted)}
              </li>
            )}
            {judge.last_result.repair_new_turn_id === null ? null : (
              <li>
                {translate(language, "featureModesRepairNewTurn")}: {judge.last_result.repair_new_turn_id}
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );

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
    </p>
  );

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
          {renderRecordingOutcome(
            "feature-modes-recording-turn-outcome",
            "featureModesRecordingLastOutcomeLabel",
            status.recording.last_outcome,
          )}
          {renderRecordingOutcome(
            "feature-modes-recording-judge-evidence-outcome",
            "featureModesJudgeEvidenceOutcomeLabel",
            status.recording.judge_evidence_last_outcome,
          )}
          <pre id="feature-modes-result" className="configuration-result" aria-live="polite">
            {resultText}
          </pre>
        </>
      )}
    </section>
  );
}
