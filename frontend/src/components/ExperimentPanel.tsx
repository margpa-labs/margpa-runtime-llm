import { useEffect, useRef, useState } from "react";
import {
  ApiMutationError,
  cancelExperimentRun,
  createExperimentPlan,
  fetchExperimentComparison,
  fetchExperimentPresets,
  fetchExperimentRun,
  fetchExperimentRunList,
  newActionId,
  startExperimentRun,
} from "../api/client";
import { translate } from "../i18n/translations";
import type {
  ExperimentActorInvocation,
  ExperimentComparison,
  ExperimentComponentSelection,
  ExperimentExecutionMode,
  ExperimentPlan,
  ExperimentPresets,
  ExperimentVariantRun,
  UiLanguage,
} from "../types";

interface ExperimentPanelProps {
  language: UiLanguage;
  open: boolean;
  onClose: () => void;
}

type LoadState = "idle" | "ready" | "failed";
// Phase 9-2 R2-WU-05 (Handoff R2 SS8): "Comparison取得失敗を無言で握りつぶし、
// 古いComparisonを最新に見せない" -- `"stale"` keeps the last-known
// Comparison ON SCREEN (never blanks it) but visibly flags it as no longer
// confirmed current; `"unavailable"` is the honest state when there has
// never been a successful fetch at all.
type ComparisonStatus = "idle" | "ok" | "stale" | "unavailable";

const TERMINAL_RUN_STATES = new Set(["completed", "failed", "cancelled"]);
const POLL_INTERVAL_MS = 250;
const POLL_TIMEOUT_MS = 120_000;

// Phase 9-2 R2-WU-05 / R3-WU-05 (IR-P9-2-R2-03 fix): a Preset Variant's
// own DECLARED Component/Mode pairs -- shown BEFORE the Plan is created
// so a Production choice's own requirements are visible up front. This
// is never labeled "Frozen Config": it is only the Preset's own
// declaration, not a captured Live Snapshot. The Plan's own "Desired
// Config Digest" (computed once Plan creation reads Live, per Variant --
// `plan.variant_configurations`) and a Run's own genuine "Frozen Config
// Digest" (captured fresh at that Run's own start) are separate, later
// values this Panel never conflates with this declaration string. An
// absent Component (WU-C C3's own 不在/OFF distinction) is simply not
// listed.
// Phase 9-2 R4-WU-01 (Handoff R4 SS4.1.1): a Component's own declared
// `selector_id` (its Provider identity, e.g. "judge.gemma-4-e2b-it-q4-0")
// is now shown alongside its Mode -- ModeだけでなくProvider Identityも
// 明示する applies to what the User sees, not only to what the backend
// enforces. Absent for a Component that leaves its Provider Don't-care.
function formatComponents(components: ExperimentComponentSelection[]): string {
  if (components.length === 0) {
    return "-";
  }
  return components
    .map((component) => {
      const mode = component.mode ?? "off";
      return component.selector_id === null
        ? `${component.component_key}=${mode}`
        : `${component.component_key}=${mode}(${component.selector_id})`;
    })
    .join(", ");
}

// Phase 9-2 R3-WU-05: a digest is never fully re-typed onto the screen --
// truncated to a short, still-comparable prefix so a reader can eyeball
// "these two rows are NOT the same value" without needing the full 128
// hex characters.
function shortDigest(digest: string | null | undefined): string {
  if (digest === null || digest === undefined) {
    return "-";
  }
  return `${digest.slice(0, 12)}…`;
}

// Phase 9-2 R3-WU-02 (IR-P9-2-R2-04 fix): a genuine three-state render --
// `called === null` (not_observed) must never be displayed as the
// confirmed-negative "false" a `called ? "true" : "false"` ternary would
// collapse it to.
function calledDisplay(language: UiLanguage, called: boolean | null): string {
  if (called === true) {
    return translate(language, "experimentCalledTrue");
  }
  if (called === false) {
    return translate(language, "experimentCalledFalse");
  }
  return translate(language, "experimentCalledUnknown");
}

// Phase 9-2 R2-WU-05: `repair_called` (a Repair Attempt ran) and
// `repair_adopted` (its output was actually Presented) are never
// rendered as the same fact -- a Called-but-rejected Repair must never
// look identical to an Adopted one.
function repairDisplay(language: UiLanguage, repairAdopted: boolean | null | undefined): string {
  if (repairAdopted === true) {
    return translate(language, "experimentRepairAdopted");
  }
  if (repairAdopted === false) {
    return translate(language, "experimentRepairCalledNotAdopted");
  }
  return "-";
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function pollUntilTerminal(
  runId: string,
  onUpdate: (result: ExperimentVariantRun) => void,
  onTransientFailure: () => void,
): Promise<void> {
  const deadline = Date.now() + POLL_TIMEOUT_MS;
  while (Date.now() < deadline) {
    try {
      const result = await fetchExperimentRun(runId);
      onUpdate(result.run);
      if (TERMINAL_RUN_STATES.has(result.run.state)) {
        return;
      }
    } catch {
      // A single transient status-read failure must not strand the UI at
      // the first `running` row while the Backend Worker continues. Keep
      // polling until the bounded deadline and disclose the retry state.
      onTransientFailure();
    }
    await wait(POLL_INTERVAL_MS);
  }
  throw new Error("experiment_run_poll_timeout");
}

function upsertRun(
  current: ExperimentVariantRun[],
  incoming: ExperimentVariantRun,
): ExperimentVariantRun[] {
  const index = current.findIndex((run) => run.run_id === incoming.run_id);
  if (index < 0) {
    return [...current, incoming];
  }
  return current.map((run, runIndex) => {
    if (runIndex !== index) {
      return run;
    }
    // VariantRun is a one-way state machine. A slower list/poll Response
    // that still says `planned`/`running` must never overwrite a Terminal
    // state already observed for this same generation.
    if (
      run.generation > incoming.generation ||
      (run.generation === incoming.generation &&
        TERMINAL_RUN_STATES.has(run.state) &&
        !TERMINAL_RUN_STATES.has(incoming.state))
    ) {
      return run;
    }
    return incoming;
  });
}

function mergeRuns(
  current: ExperimentVariantRun[],
  incoming: ExperimentVariantRun[],
): ExperimentVariantRun[] {
  return incoming.reduce(upsertRun, current);
}

// Phase 9-2 WU-E E4 (R1-WU-03/04/05): the Minimal Experiment screen.
// `startExperimentRun` returns immediately (`state="running"`) -- this
// Panel polls `fetchExperimentRun` for the real, eventual outcome rather
// than assuming synchronous completion. Execution mode defaults to
// Fixture (never a real Model call); choosing Production runs one real
// Turn through the Backend's own Production Adapter, when available.
export default function ExperimentPanel({ language, open, onClose }: ExperimentPanelProps) {
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [presets, setPresets] = useState<ExperimentPresets | null>(null);
  const [experimentId, setExperimentId] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [selectedVariantIds, setSelectedVariantIds] = useState<Set<string>>(new Set());
  const [executionMode, setExecutionMode] = useState<ExperimentExecutionMode>("fixture");
  const [planReady, setPlanReady] = useState(false);
  const [plan, setPlan] = useState<ExperimentPlan | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  const [runs, setRuns] = useState<ExperimentVariantRun[]>([]);
  const [comparison, setComparison] = useState<ExperimentComparison | null>(null);
  const [comparisonStatus, setComparisonStatus] = useState<ComparisonStatus>("idle");
  const [runningVariantId, setRunningVariantId] = useState<string | null>(null);
  const [recheckRunId, setRecheckRunId] = useState<string | null>(null);
  const [rechecking, setRechecking] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [runStatusNotice, setRunStatusNotice] = useState<string | null>(null);
  const [selectedRunInvocations, setSelectedRunInvocations] = useState<
    ExperimentActorInvocation[] | null
  >(null);
  const [selectedRunExecutionMode, setSelectedRunExecutionMode] =
    useState<ExperimentExecutionMode>("fixture");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const activeExperimentIdRef = useRef(experimentId);
  const refreshGenerationRef = useRef(0);
  const detailGenerationRef = useRef(0);
  const planGenerationRef = useRef(0);

  useEffect(() => {
    if (!open || loadState !== "idle") {
      return;
    }
    void fetchExperimentPresets()
      .then((data) => {
        setPresets(data);
        const generatedExperimentId = `exp-${newActionId().slice(0, 8)}`;
        activeExperimentIdRef.current = generatedExperimentId;
        setExperimentId(generatedExperimentId);
        const firstCase = data.cases[0];
        if (firstCase !== undefined) {
          setSelectedCaseId(firstCase.case_id);
        }
        setLoadState("ready");
      })
      .catch(() => {
        setLoadState("failed");
      });
  }, [open, loadState]);

  if (!open) {
    return null;
  }

  const toggleVariant = (variantId: string) => {
    setSelectedVariantIds((previous) => {
      const next = new Set(previous);
      if (next.has(variantId)) {
        next.delete(variantId);
      } else {
        next.add(variantId);
      }
      return next;
    });
  };

  const handleCreatePlan = () => {
    const requestedExperimentId = experimentId;
    const planGeneration = ++planGenerationRef.current;
    setPlanError(null);
    void createExperimentPlan(
      requestedExperimentId,
      selectedCaseId,
      Array.from(selectedVariantIds),
      executionMode,
    )
      .then((data) => {
        if (
          planGenerationRef.current !== planGeneration ||
          activeExperimentIdRef.current !== requestedExperimentId
        ) {
          return;
        }
        // A newly committed Plan is a new identity boundary even if no
        // refresh/detail Response has arrived yet. Invalidate every older
        // async reader before exposing its state.
        refreshGenerationRef.current += 1;
        detailGenerationRef.current += 1;
        setPlan(data);
        setPlanReady(true);
        setRuns([]);
        setComparison(null);
        setComparisonStatus("idle");
        setSelectedRunId(null);
        setSelectedRunInvocations(null);
      })
      .catch(() => {
        if (
          planGenerationRef.current === planGeneration &&
          activeExperimentIdRef.current === requestedExperimentId
        ) {
          setPlanError(translate(language, "experimentPlanFailed"));
        }
      });
  };

  const refreshRunList = async (id: string): Promise<ExperimentVariantRun[] | null> => {
    const refreshGeneration = ++refreshGenerationRef.current;
    const [runListResult, comparisonResult] = await Promise.allSettled([
      fetchExperimentRunList(id),
      fetchExperimentComparison(id),
    ]);
    const isLatestCurrentExperiment =
      refreshGenerationRef.current === refreshGeneration && activeExperimentIdRef.current === id;
    if (!isLatestCurrentExperiment) {
      return null;
    }
    if (runListResult.status === "fulfilled") {
      setRuns((previous) => mergeRuns(previous, runListResult.value.runs));
    }
    if (comparisonResult.status === "fulfilled") {
      const data = comparisonResult.value;
      setComparison(data);
      setComparisonStatus("ok");
    } else {
      // R2-WU-05 (Handoff R2 SS8): a transient failure here must never
      // silently keep showing the last Comparison as if it were still
      // current -- `"stale"` once something was already on screen,
      // `"unavailable"` while nothing has ever loaded successfully;
      // never a silent no-op that leaves `comparisonStatus` at `"ok"`.
      setComparisonStatus((previous) =>
        previous === "ok" || previous === "stale" ? "stale" : "unavailable",
      );
    }
    return runListResult.status === "fulfilled" ? runListResult.value.runs : null;
  };

  const handleRun = (variantId: string) => {
    setRunError(null);
    setRunStatusNotice(null);
    setRecheckRunId(null);
    setRunningVariantId(variantId);
    const runId = `run-${newActionId().slice(0, 8)}`;
    void (async () => {
      try {
        const startedRun = await startExperimentRun(experimentId, variantId, runId);
        setRuns((previous) => upsertRun(previous, startedRun));
        void refreshRunList(experimentId);
        await pollUntilTerminal(
          runId,
          (updatedRun) => {
            setRuns((previous) => upsertRun(previous, updatedRun));
            setRunStatusNotice(null);
          },
          () => {
            setRunStatusNotice(translate(language, "experimentRunStatusRetrying"));
          },
        );
        await refreshRunList(experimentId);
      } catch (error: unknown) {
        // R2-WU-05: a Production Run rejected at Call 0 (e.g. Live
        // Configuration drifted or cannot satisfy this Variant,
        // `live_config_mismatch`/`live_config_unavailable`) surfaces its
        // real Backend reason -- never only a generic "it failed".
        const message = error instanceof ApiMutationError ? error.message : null;
        if (error instanceof Error && error.message === "experiment_run_poll_timeout") {
          // A normal Production Run may legitimately outlive the bounded
          // auto-tracking window. Make one final GET-only refresh first:
          // if it already reached Terminal, clear the tracking error. If
          // not, preserve this same run_id for an explicit GET-only Recheck.
          const refreshedRuns = await refreshRunList(experimentId);
          const refreshedRun = refreshedRuns?.find((run) => run.run_id === runId);
          if (refreshedRun !== undefined && TERMINAL_RUN_STATES.has(refreshedRun.state)) {
            setRuns((previous) => upsertRun(previous, refreshedRun));
            setRunError(null);
            setRecheckRunId(null);
          } else {
            setRunError(translate(language, "experimentRunStatusUnavailable"));
            setRecheckRunId(runId);
          }
        } else {
          setRunError(message ?? translate(language, "experimentRunFailed"));
          await refreshRunList(experimentId);
        }
      } finally {
        setRunStatusNotice(null);
        setRunningVariantId(null);
      }
    })();
  };

  const handleRecheck = () => {
    if (recheckRunId === null || rechecking) {
      return;
    }
    const runId = recheckRunId;
    setRechecking(true);
    setRunStatusNotice(translate(language, "experimentRunStatusRechecking"));
    void fetchExperimentRun(runId)
      .then(async (result) => {
        setRuns((previous) => upsertRun(previous, result.run));
        if (TERMINAL_RUN_STATES.has(result.run.state)) {
          setRunError(null);
          setRecheckRunId(null);
          await refreshRunList(experimentId);
        } else {
          setRunError(translate(language, "experimentRunStillRunning"));
        }
      })
      .catch(() => {
        setRunError(translate(language, "experimentRunStatusUnavailable"));
      })
      .finally(() => {
        setRunStatusNotice(null);
        setRechecking(false);
      });
  };

  const handleCancel = (runId: string) => {
    void cancelExperimentRun(runId).then(() => {
      void refreshRunList(experimentId);
    });
  };

  const handleShowDetails = (run: ExperimentVariantRun) => {
    const detailGeneration = ++detailGenerationRef.current;
    const requestedExperimentId = experimentId;
    const requestedRunId = run.run_id;
    setSelectedRunId(run.run_id);
    setSelectedRunInvocations(null);
    setSelectedRunExecutionMode(run.execution_mode);
    void fetchExperimentRun(run.run_id).then((result) => {
      if (
        detailGenerationRef.current !== detailGeneration ||
        activeExperimentIdRef.current !== requestedExperimentId ||
        result.run.run_id !== requestedRunId
      ) {
        return;
      }
      setSelectedRunInvocations(result.invocations);
      setSelectedRunExecutionMode(result.run.execution_mode);
    }).catch(() => {
      if (
        detailGenerationRef.current === detailGeneration &&
        activeExperimentIdRef.current === requestedExperimentId
      ) {
        // The selected row remains selected, but no older row's Evidence
        // or disclaimer is allowed to survive a failed current read.
        setSelectedRunInvocations(null);
      }
    });
  };

  return (
    <div className="settings-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="settings-modal experiment-panel"
        role="dialog"
        aria-modal="true"
        onClick={(event) => { event.stopPropagation(); }}
      >
        <div className="settings-modal-header">
          <h2>{translate(language, "experimentPanelTitle")}</h2>
          <button
            type="button"
            className="settings-modal-close secondary"
            onClick={onClose}
            aria-label="close"
          >
            ×
          </button>
        </div>
        <div className="experiment-panel-body">
          <p className="experiment-panel-note">{translate(language, "experimentPanelNote")}</p>
          {loadState === "idle" && <p>{translate(language, "experimentLoading")}</p>}
          {loadState === "failed" && <p>{translate(language, "experimentFailed")}</p>}
          {loadState === "ready" && presets !== null && !presets.enabled && (
            <p>{translate(language, "experimentDisabledNote")}</p>
          )}
          {loadState === "ready" && presets !== null && presets.enabled && (
            <>
              <label className="experiment-field">
                {translate(language, "experimentExperimentIdLabel")}
                <input
                  type="text"
                  value={experimentId}
                  onChange={(event) => {
                    const nextExperimentId = event.target.value;
                    activeExperimentIdRef.current = nextExperimentId;
                    refreshGenerationRef.current += 1;
                    detailGenerationRef.current += 1;
                    planGenerationRef.current += 1;
                    setExperimentId(nextExperimentId);
                  }}
                  disabled={planReady}
                />
              </label>
              <label className="experiment-field">
                {translate(language, "experimentCaseLabel")}
                <select
                  value={selectedCaseId}
                  onChange={(event) => { setSelectedCaseId(event.target.value); }}
                  disabled={planReady}
                >
                  {presets.cases.map((item) => (
                    <option key={item.case_id} value={item.case_id}>
                      {item.case_id}
                      {item.requires_human_review ? " *" : ""}
                    </option>
                  ))}
                </select>
              </label>
              <fieldset className="experiment-field" disabled={planReady}>
                <legend>{translate(language, "experimentVariantsLabel")}</legend>
                {presets.variants.map((variant) => (
                  <div key={variant.variant_id} className="experiment-variant-row">
                    <label className="experiment-variant-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedVariantIds.has(variant.variant_id)}
                        onChange={() => { toggleVariant(variant.variant_id); }}
                      />
                      {variant.label}
                    </label>
                    {/* R2-WU-05 (Handoff R2 SS8): the Frozen Config a
                        Production choice of this Variant would need Live
                        to already satisfy, visible before Plan creation. */}
                    <span className="experiment-variant-config">
                      ({formatComponents(variant.components)})
                    </span>
                  </div>
                ))}
              </fieldset>
              <label className="experiment-field">
                {translate(language, "experimentExecutionModeLabel")}
                <select
                  value={executionMode}
                  onChange={(event) => {
                    setExecutionMode(event.target.value as ExperimentExecutionMode);
                  }}
                  disabled={planReady}
                >
                  <option value="fixture">
                    {translate(language, "experimentExecutionModeFixture")}
                  </option>
                  <option value="production">
                    {translate(language, "experimentExecutionModeProduction")}
                  </option>
                </select>
              </label>
              {!planReady && (
                <button
                  type="button"
                  className="primary"
                  onClick={handleCreatePlan}
                  disabled={selectedCaseId === "" || selectedVariantIds.size === 0}
                >
                  {translate(language, "experimentCreatePlan")}
                </button>
              )}
              {planError !== null && <p className="experiment-error">{planError}</p>}
              {planReady && (
                <>
                  <p>{translate(language, "experimentPlanCreated")}</p>
                  <div className="experiment-run-buttons">
                    {Array.from(selectedVariantIds).map((variantId) => {
                      const desired = plan?.variant_configurations.find(
                        (item) => item.variant_id === variantId,
                      );
                      const variantRuns = runs.filter((run) => run.variant_id === variantId);
                      const latestRun = variantRuns[variantRuns.length - 1];
                      // Phase 9-2 R3-WU-05 (Handoff R3 SS4.3 "各Variantの
                      // Ready／Mismatch／Running／Terminalを区別する"): a
                      // Variant with no Run yet is Ready; otherwise its
                      // latest Run's own real `state` is shown verbatim
                      // (never collapsed into a single generic label).
                      const statusLabel =
                        latestRun === undefined ? "ready" : latestRun.state;
                      return (
                        <div key={variantId} className="experiment-run-row">
                          <button
                            type="button"
                            className="primary"
                            onClick={() => { handleRun(variantId); }}
                            disabled={runningVariantId !== null || recheckRunId !== null}
                            aria-busy={runningVariantId === variantId}
                          >
                            {translate(language, "experimentRun")}: {variantId}
                          </button>
                          <span className="experiment-variant-status">[{statusLabel}]</span>
                          {desired !== undefined && (
                            <span className="experiment-variant-config">
                              {translate(language, "experimentColumnDesiredConfigDigest")}:{" "}
                              {shortDigest(desired.desired_configuration_digest_sha512)}
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  {runningVariantId !== null && (
                    <p role="status">{translate(language, "experimentRunning")}</p>
                  )}
                  {runStatusNotice !== null && <p role="status">{runStatusNotice}</p>}
                  {runError !== null && <p className="experiment-error">{runError}</p>}
                  {recheckRunId !== null && (
                    <button
                      type="button"
                      className="secondary"
                      onClick={handleRecheck}
                      disabled={rechecking}
                      aria-busy={rechecking}
                    >
                      {translate(language, "experimentRecheckRunStatus")}
                    </button>
                  )}
                  <h3>{translate(language, "experimentComparisonTitle")}</h3>
                  {comparisonStatus === "stale" && (
                    <p className="experiment-error">
                      {translate(language, "experimentComparisonStale")}
                    </p>
                  )}
                  {comparisonStatus === "unavailable" && (
                    <p className="experiment-error">
                      {translate(language, "experimentComparisonUnavailable")}
                    </p>
                  )}
                  <table className="experiment-comparison-table">
                    <thead>
                      <tr>
                        <th>{translate(language, "experimentColumnVariant")}</th>
                        <th>{translate(language, "experimentColumnConfig")}</th>
                        <th>{translate(language, "experimentColumnExecutionMode")}</th>
                        <th>{translate(language, "experimentColumnState")}</th>
                        <th>{translate(language, "experimentColumnFrozenConfigDigest")}</th>
                        <th>{translate(language, "experimentColumnMetric")}</th>
                        <th>{translate(language, "experimentColumnEvaluation")}</th>
                        <th>{translate(language, "experimentColumnFailure")}</th>
                        <th>{translate(language, "experimentColumnRawEvidence")}</th>
                        <th>{translate(language, "experimentColumnActions")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {runs.map((run) => {
                        const row = comparison?.rows.find((item) => item.run_id === run.run_id);
                        return (
                          <tr key={run.run_id}>
                            <td>{run.variant_id}</td>
                            <td>
                              {row === undefined ? "-" : formatComponents(row.variant_components)}
                            </td>
                            <td>{row?.execution_mode ?? run.execution_mode}</td>
                            <td>{run.state}</td>
                            <td>
                              {shortDigest(
                                row?.frozen_configuration_digest_sha512 ??
                                  run.frozen_configuration_digest_sha512,
                              )}
                            </td>
                            <td>
                              {row?.metric?.call_count ?? "-"}
                              {row?.metric?.unknown_component_count
                                ? ` (${translate(language, "experimentUnknownComponentCount")}: ${String(
                                    row.metric.unknown_component_count,
                                  )})`
                                : ""}
                              {" / "}
                              {repairDisplay(language, row?.metric?.repair_adopted)}
                            </td>
                            <td>
                              {row === undefined || row.observations.length === 0
                                ? "-"
                                : row.observations
                                    .map((observation) =>
                                      observation.outcome === "not_run"
                                        ? translate(language, "experimentHumanReviewPending")
                                        : observation.outcome,
                                    )
                                    .join(", ")}
                            </td>
                            <td>{run.failure_reason ?? "-"}</td>
                            <td>{row?.raw_evidence_pointer ?? "-"}</td>
                            <td>
                              <button
                                type="button"
                                className="secondary"
                                onClick={() => { handleShowDetails(run); }}
                              >
                                {translate(language, "experimentDetailsTitle")}
                              </button>
                              {!TERMINAL_RUN_STATES.has(run.state) && (
                                <button
                                  type="button"
                                  className="danger"
                                  onClick={() => { handleCancel(run.run_id); }}
                                >
                                  {translate(language, "experimentCancel")}
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                  {selectedRunId !== null && selectedRunInvocations !== null && (
                    <>
                      <h3>{translate(language, "experimentDetailsTitle")}</h3>
                      <p className="experiment-fixture-disclaimer">
                        {translate(
                          language,
                          selectedRunExecutionMode === "production"
                            ? "experimentRealResultDisclaimer"
                            : "experimentFixtureOnlyDisclaimer",
                        )}
                      </p>
                      <table className="experiment-comparison-table">
                        <thead>
                          <tr>
                            <th>{translate(language, "experimentColumnComponent")}</th>
                            <th>{translate(language, "experimentColumnCalled")}</th>
                            <th>{translate(language, "experimentColumnOutcome")}</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedRunInvocations.map((invocation) => (
                            <tr key={invocation.component_key}>
                              <td>{invocation.component_key}</td>
                              <td>{calledDisplay(language, invocation.called)}</td>
                              <td>{invocation.outcome}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
