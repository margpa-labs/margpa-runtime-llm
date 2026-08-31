import { useEffect, useState } from "react";
import {
  advanceDevAgentRun,
  cancelDevAgentRun,
  fetchDevAgentCapabilities,
  fetchDevAgentTools,
  startDevAgentRun,
  submitDevAgentApproval,
  submitDevAgentCompletionApproval,
} from "../api/client";
import { usePreference } from "../hooks/usePreference";
import { translate } from "../i18n/translations";
import type {
  DevAgentCapabilityId,
  DevAgentImportantGateReason,
  DevAgentPlanStepRequest,
  DevAgentRun,
  DevAgentToolDescriptor,
  UiLanguage,
} from "../types";

// P8-D/P8-F: Stable Capability ID + Chat/Dev Agent UI switch, plus a
// minimal but real interactive Run surface (P8-ACC-040: a User must be able
// to confirm Gate/Stop behavior from the actual screen, not only via REST).
// The Demo Run always uses the same 3-Tool Plan the backend Golden Path
// Tests already cover — this Panel is a thin, honest window onto the exact
// Run Service exercised by those Tests, not a separate code path.
interface DevAgentPanelProps {
  language: UiLanguage;
  visible: boolean;
}

type LoadCapability = "loading" | "ready" | "failed";

const CAPABILITY_VALUES: readonly DevAgentCapabilityId[] = ["chat", "dev_agent"];
const DEV_AGENT_CAPABILITY_KEY = "margpa.dev_agent_capability.v1";

const DEMO_PLAN_STEPS: DevAgentPlanStepRequest[] = [
  { step_id: "list", tool_id: "list_files", input: {} },
  { step_id: "read", tool_id: "read_file", input: { path: "notes/readme.md" } },
  {
    step_id: "write",
    tool_id: "write_note",
    input: { path: "notes/new.md", content: "Hello from the Dev Agent Demo Run." },
  },
];

const TERMINAL_RUN_STATES = new Set(["completed", "failed", "cancelled"]);

// P8-MR9-1 (P8-CODEX-011/UF-P8-003): the Completion Gate's Gate Reason is
// always `completion` by Runtime Contract (`CompletionApprovalEvidence
// .gate_reason: Literal[ImportantGateReason.COMPLETION]`) — it must never
// read `run.envelope.gate_reasons`, which still holds the last Tool Gate's
// reason (e.g. `external_write`) left over from the frozen Step Envelope.
const COMPLETION_GATE_REASON: DevAgentImportantGateReason = "completion";

// P8-MR5 (P8-MANUAL-005): a small, generic key:value formatter for a Step's
// real `input`/`output` dict — never a Tool-specific hand-written renderer,
// so this Panel always shows exactly what the Server actually carries
// (Target Path/Write Content for `write_note`, Digest/Overwrite/Written At
// once it succeeds), never a Frontend-only guess that could silently
// diverge from the real Plan/Result.
function formatRecord(record: Record<string, unknown>): string {
  const entries = Object.entries(record);
  if (entries.length === 0) return "—";
  return entries.map(([key, value]) => `${key}: ${String(value)}`).join(", ");
}

export default function DevAgentPanel({ language, visible }: DevAgentPanelProps) {
  const [capabilityId, setCapabilityId] = usePreference<DevAgentCapabilityId>(
    DEV_AGENT_CAPABILITY_KEY,
    CAPABILITY_VALUES,
    "chat",
  );
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [tools, setTools] = useState<DevAgentToolDescriptor[]>([]);
  const [run, setRun] = useState<DevAgentRun | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible) return;
    fetchDevAgentCapabilities()
      .then(() => {
        setCapability("ready");
      })
      .catch(() => {
        setCapability("failed");
      });
  }, [visible]);

  useEffect(() => {
    if (!visible || capability !== "ready" || capabilityId !== "dev_agent") return;
    fetchDevAgentTools()
      .then(setTools)
      .catch(() => {
        setTools([]);
      });
  }, [visible, capability, capabilityId]);

  if (!visible || capability === "failed") {
    return null;
  }

  const handleStartRun = (): void => {
    setRunError(null);
    startDevAgentRun("dev_agent", DEMO_PLAN_STEPS, "important_gate_only")
      .then(setRun)
      .catch((error: unknown) => {
        setRunError(error instanceof Error ? error.message : "dev_agent_run_start_failed");
      });
  };

  const handleAdvance = (): void => {
    if (run === null) return;
    setRunError(null);
    advanceDevAgentRun(run.run_id)
      .then(setRun)
      .catch((error: unknown) => {
        setRunError(error instanceof Error ? error.message : "dev_agent_run_advance_failed");
      });
  };

  const handleDecision = (stepId: string, decision: "approved" | "denied"): void => {
    if (run === null) return;
    setRunError(null);
    submitDevAgentApproval(run.run_id, stepId, decision)
      .then(setRun)
      .catch((error: unknown) => {
        setRunError(error instanceof Error ? error.message : "dev_agent_run_approval_failed");
      });
  };

  const handleCompletionDecision = (decision: "approved" | "denied"): void => {
    if (run === null) return;
    setRunError(null);
    submitDevAgentCompletionApproval(run.run_id, decision)
      .then(setRun)
      .catch((error: unknown) => {
        setRunError(
          error instanceof Error ? error.message : "dev_agent_run_completion_approval_failed",
        );
      });
  };

  const handleCancel = (): void => {
    if (run === null) return;
    setRunError(null);
    cancelDevAgentRun(run.run_id)
      .then(setRun)
      .catch((error: unknown) => {
        setRunError(error instanceof Error ? error.message : "dev_agent_run_cancel_failed");
      });
  };

  const handleReset = (): void => {
    setRun(null);
    setRunError(null);
  };

  const awaitingStep =
    run !== null ? run.steps.find((step) => step.state === "awaiting_approval") : undefined;
  const awaitingCompletion = run !== null && run.state === "awaiting_completion_approval";
  const isTerminal = run !== null && TERMINAL_RUN_STATES.has(run.state);

  return (
    <section
      id="dev-agent-panel"
      className="dev-agent-panel"
      aria-label={translate(language, "devAgentTitle")}
    >
      <h3 id="dev-agent-title">{translate(language, "devAgentTitle")}</h3>
      <p id="dev-agent-note">{translate(language, "devAgentNote")}</p>
      {capability === "loading" ? (
        <p id="dev-agent-status">{translate(language, "devAgentLoading")}</p>
      ) : (
        <>
          <div
            className="switch-row dev-agent-capability-switch"
            role="radiogroup"
            aria-label={translate(language, "devAgentSwitchLabel")}
          >
            <label>
              <input
                type="radio"
                name="dev-agent-capability"
                checked={capabilityId === "chat"}
                onChange={() => {
                  setCapabilityId("chat");
                }}
              />
              {translate(language, "devAgentCapabilityChat")}
            </label>
            <label>
              <input
                type="radio"
                name="dev-agent-capability"
                checked={capabilityId === "dev_agent"}
                onChange={() => {
                  setCapabilityId("dev_agent");
                }}
              />
              {translate(language, "devAgentCapabilityDevAgent")}
            </label>
          </div>
          {capabilityId === "dev_agent" ? (
            <>
              <ul id="dev-agent-tools" role="list">
                {tools.map((tool) => (
                  <li role="listitem" key={tool.tool_id} className="dev-agent-tool-row">
                    <span className="dev-agent-tool-name">{tool.name}</span>
                    <span className="dev-agent-tool-description">{tool.description}</span>
                    {tool.important_gate_reason !== null ? (
                      <span className="dev-agent-tool-important">
                        {translate(language, "devAgentToolImportant")} (
                        {tool.important_gate_reason})
                      </span>
                    ) : null}
                  </li>
                ))}
              </ul>

              <div id="dev-agent-demo-run" className="dev-agent-demo-run">
                <h4>{translate(language, "devAgentDemoRunTitle")}</h4>
                {run === null ? (
                  <button
                    id="dev-agent-start-run"
                    type="button"
                    className="primary"
                    onClick={handleStartRun}
                  >
                    {translate(language, "devAgentStartRun")}
                  </button>
                ) : (
                  <div id="dev-agent-run-detail">
                    <p id="dev-agent-run-state">
                      {translate(language, "devAgentRunStateLabel")}{" "}
                      <strong>{run.state}</strong>
                    </p>
                    <ul id="dev-agent-run-steps" role="list">
                      {run.steps.map((step) => (
                        <li
                          role="listitem"
                          key={step.step_id}
                          className="dev-agent-run-step-row"
                        >
                          <div className="dev-agent-run-step-header">
                            <span className="dev-agent-run-step-id">{step.step_id}</span>
                            <span className="dev-agent-run-step-tool">{step.tool_id}</span>
                            <span className="dev-agent-run-step-state">{step.state}</span>
                          </div>
                          {/* P8-MR5 (P8-MANUAL-005): the real Server Plan
                              Input — Target Path/Write Content for
                              `write_note` — visible before this Step is
                              ever Approved, not only after it succeeds. */}
                          <div className="dev-agent-run-step-detail dev-agent-run-step-input">
                            {translate(language, "devAgentStepInputLabel")}{" "}
                            {formatRecord(step.input)}
                          </div>
                          {step.output !== null ? (
                            <div className="dev-agent-run-step-detail dev-agent-run-step-output">
                              {translate(language, "devAgentStepOutputLabel")}{" "}
                              {formatRecord(step.output)}
                            </div>
                          ) : null}
                          {step.error !== null ? (
                            <span className="dev-agent-run-step-error">{step.error}</span>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                    {run.completion !== null ? (
                      <p id="dev-agent-run-completion">
                        {translate(language, "devAgentCompletionLabel")}{" "}
                        {run.completion.outcome} — {run.completion.reason}
                      </p>
                    ) : null}
                    {awaitingStep !== undefined ? (
                      <div id="dev-agent-approval-gate" className="dev-agent-approval-gate">
                        <p>
                          {translate(language, "devAgentApprovalGateLabel")} "
                          {awaitingStep.step_id}"
                        </p>
                        {/* P8-MR5 (P8-MANUAL-005): Exact Action visible
                            before Approval — the same Input row already
                            rendered above, plus Resource Scope/Gate Reason
                            from the real Frozen Envelope. */}
                        <p className="dev-agent-run-step-detail">
                          {translate(language, "devAgentStepInputLabel")}{" "}
                          {formatRecord(awaitingStep.input)}
                        </p>
                        {run.envelope !== null ? (
                          <>
                            <p className="dev-agent-run-step-detail">
                              {translate(language, "devAgentResourceScopeLabel")}{" "}
                              {run.envelope.resource_scope}
                            </p>
                            {run.envelope.gate_reasons.length > 0 ? (
                              <p className="dev-agent-run-step-detail">
                                {translate(language, "devAgentGateReasonLabel")}{" "}
                                {run.envelope.gate_reasons.join(", ")}
                              </p>
                            ) : null}
                          </>
                        ) : null}
                        <p className="dev-agent-fixture-workspace-disclaimer">
                          {translate(language, "devAgentFixtureWorkspaceDisclaimer")}
                        </p>
                        <button
                          id="dev-agent-approve"
                          type="button"
                          className="primary"
                          onClick={() => {
                            handleDecision(awaitingStep.step_id, "approved");
                          }}
                        >
                          {translate(language, "devAgentApprove")}
                        </button>
                        <button
                          id="dev-agent-deny"
                          type="button"
                          className="danger"
                          onClick={() => {
                            handleDecision(awaitingStep.step_id, "denied");
                          }}
                        >
                          {translate(language, "devAgentDeny")}
                        </button>
                      </div>
                    ) : null}
                    {awaitingCompletion ? (
                      <div
                        id="dev-agent-completion-gate"
                        className="dev-agent-approval-gate dev-agent-completion-gate"
                      >
                        <p>{translate(language, "devAgentCompletionGateLabel")}</p>
                        <p className="dev-agent-run-step-detail">
                          {translate(language, "devAgentGateReasonLabel")}{" "}
                          {COMPLETION_GATE_REASON}
                        </p>
                        <button
                          id="dev-agent-completion-approve"
                          type="button"
                          className="primary"
                          onClick={() => {
                            handleCompletionDecision("approved");
                          }}
                        >
                          {translate(language, "devAgentApprove")}
                        </button>
                        <button
                          id="dev-agent-completion-deny"
                          type="button"
                          className="danger"
                          onClick={() => {
                            handleCompletionDecision("denied");
                          }}
                        >
                          {translate(language, "devAgentDeny")}
                        </button>
                      </div>
                    ) : null}
                    {!isTerminal ? (
                      <>
                        <button
                          id="dev-agent-advance"
                          type="button"
                          className="primary"
                          onClick={handleAdvance}
                        >
                          {translate(language, "devAgentAdvance")}
                        </button>
                        <button
                          id="dev-agent-cancel"
                          type="button"
                          className="danger"
                          onClick={handleCancel}
                        >
                          {translate(language, "devAgentCancel")}
                        </button>
                      </>
                    ) : (
                      <button
                        id="dev-agent-reset"
                        // P8-MR9-3 (P8-CODEX-011/UF-UI-013): the same action
                        // as the initial "Start Run" Button
                        // (`#dev-agent-start-run`, also `.primary`) — it
                        // must not read as a lesser/secondary Action just
                        // because the Run happens to be Completed.
                        type="button"
                        className="primary"
                        onClick={handleReset}
                      >
                        {translate(language, "devAgentStartNewRun")}
                      </button>
                    )}
                  </div>
                )}
                {runError !== null ? (
                  <p id="dev-agent-run-error" className="dev-agent-run-error">
                    {runError}
                  </p>
                ) : null}
              </div>
            </>
          ) : null}
        </>
      )}
    </section>
  );
}
