import { useState } from "react";
import {
  ApiMutationError,
  applyRuntimeModelContext,
  applyRuntimeModelMaxNewTokens,
  applyRuntimeModelSwitch,
} from "../api/client";
import { translate } from "../i18n/translations";
import type { RuntimeModelStatus, UiLanguage } from "../types";

// App owns the canonical status fetch and polling lifecycle so Sidebar,
// Advanced settings, mutation responses, and cross-tab refreshes all project
// one accepted Runtime Model Snapshot. This panel only performs explicit CAS
// mutations and returns their canonical response upward.
type LoadCapability = "loading" | "ready" | "failed" | "disabled";

export interface RuntimeModelControlState {
  capability: LoadCapability;
  status: RuntimeModelStatus | null;
}

interface RuntimeModelStatusPanelProps {
  language: UiLanguage;
  visible: boolean;
  state: RuntimeModelControlState;
  onRefresh: () => void;
  onStatusChange: (status: RuntimeModelStatus) => void;
}

export default function RuntimeModelStatusPanel({
  language,
  visible,
  state,
  onRefresh,
  onStatusChange,
}: RuntimeModelStatusPanelProps) {
  const { capability, status } = state;
  const [contextInput, setContextInput] = useState(() => String(status?.loaded_context_size ?? ""));
  const [maxTokensInput, setMaxTokensInput] = useState(() =>
    String(status?.current_max_new_tokens ?? ""),
  );
  const [switchTarget, setSwitchTarget] = useState(() => status?.main_model?.model_key ?? "");
  const [applyResultText, setApplyResultText] = useState("");
  const [applyingContext, setApplyingContext] = useState(false);
  const [applyingMaxTokens, setApplyingMaxTokens] = useState(false);
  const [applyingSwitch, setApplyingSwitch] = useState(false);

  const restoreInputsFromCanonical = (): void => {
    setContextInput(String(status?.loaded_context_size ?? ""));
    setMaxTokensInput(String(status?.current_max_new_tokens ?? ""));
    setSwitchTarget(status?.main_model?.model_key ?? "");
  };

  const mutationFailureText = (error: unknown): string => {
    if (error instanceof ApiMutationError) {
      if (error.code === "runtime_model_limit_exceeded") {
        return error.message;
      }
      if (error.code === "runtime_model_revision_conflict") {
        return translate(language, "runtimeModelConflict");
      }
      if (error.code === "runtime_model_busy") {
        return translate(language, "runtimeModelBusy");
      }
    }
    return translate(language, "runtimeModelApplyFailed");
  };

  // Re-sync the two input fields whenever a *new* status arrives (same
  // "adjust during render" pattern as RuntimeGovernancePanel's
  // syncedRevision), so a successful Apply's own response updates the
  // displayed input to the new Current value without clobbering
  // in-progress typing on every unrelated re-render.
  const [syncedDigest, setSyncedDigest] = useState(status?.digest_sha512);
  if (status?.digest_sha512 !== syncedDigest) {
    setSyncedDigest(status?.digest_sha512);
    if (status !== null && status.enabled) {
      setContextInput(String(status.loaded_context_size ?? ""));
      setMaxTokensInput(String(status.current_max_new_tokens ?? ""));
      setSwitchTarget(status.main_model?.model_key ?? "");
    }
  }

  if (!visible) {
    return null;
  }

  const statusKey =
    capability === "loading"
      ? "runtimeModelLoading"
      : capability === "ready"
        ? "runtimeModelReady"
        : "runtimeModelFailed";

  const applyContext = () => {
    if (status === null || status.revision === null || status.digest_sha512 === null) {
      return;
    }
    const requested = Number.parseInt(contextInput, 10);
    if (!Number.isFinite(requested) || requested <= 0) {
      return;
    }
    setApplyingContext(true);
    applyRuntimeModelContext(status.revision, status.digest_sha512, requested)
      .then((next) => {
        onStatusChange(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch((error: unknown) => {
        setApplyResultText(mutationFailureText(error));
        restoreInputsFromCanonical();
        // A failure (most commonly a stale CAS token: the Snapshot changed
        // elsewhere, e.g. another Tab) leaves this Panel's own status
        // un-refreshed, so retrying Apply would just repeat the same
        // conflict against the same stale revision/digest. Re-fetch so the
        // next Apply attempt uses the real Current CAS token.
        onRefresh();
      })
      .finally(() => {
        setApplyingContext(false);
      });
  };

  const applySwitch = () => {
    if (status === null || status.revision === null || status.digest_sha512 === null) {
      return;
    }
    if (!switchTarget) {
      return;
    }
    const target = status.available_models.find((model) => model.model_key === switchTarget);
    const currentContext = status.loaded_context_size;
    if (target === undefined || currentContext === null || currentContext <= 0) {
      return;
    }
    const requested = Math.min(currentContext, target.effective_context_limit);
    setApplyingSwitch(true);
    applyRuntimeModelSwitch(status.revision, status.digest_sha512, switchTarget, requested)
      .then((next) => {
        onStatusChange(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch((error: unknown) => {
        setApplyResultText(mutationFailureText(error));
        restoreInputsFromCanonical();
        // Same reasoning as applyContext/applyMaxTokens above: a failed
        // Switch (stale CAS, unregistered target, or a genuine Load
        // failure the Controller already rolled back) leaves this Panel's
        // status un-refreshed, so re-fetch before the next attempt.
        onRefresh();
      })
      .finally(() => {
        setApplyingSwitch(false);
      });
  };

  const applyMaxTokens = () => {
    if (status === null || status.revision === null || status.digest_sha512 === null) {
      return;
    }
    const requested = Number.parseInt(maxTokensInput, 10);
    if (!Number.isFinite(requested) || requested <= 0) {
      return;
    }
    setApplyingMaxTokens(true);
    applyRuntimeModelMaxNewTokens(status.revision, status.digest_sha512, requested)
      .then((next) => {
        onStatusChange(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch((error: unknown) => {
        setApplyResultText(mutationFailureText(error));
        restoreInputsFromCanonical();
        onRefresh();
      })
      .finally(() => {
        setApplyingMaxTokens(false);
      });
  };

  return (
    <section
      id="runtime-model-status-panel"
      className="configuration-panel"
      aria-label={translate(language, "runtimeModelTitle")}
    >
      <div className="configuration-panel-header">
        <div>
          <h2 id="runtime-model-status-title">{translate(language, "runtimeModelTitle")}</h2>
          <p id="runtime-model-status-note">{translate(language, "runtimeModelNote")}</p>
        </div>
        <button
          id="runtime-model-status-refresh"
          className="secondary"
          type="button"
          disabled={capability === "loading"}
          onClick={onRefresh}
        >
          {translate(language, "runtimeModelRefresh")}
        </button>
      </div>
      <p id="runtime-model-status-line">{translate(language, statusKey)}</p>
      {status === null || !status.enabled ? null : (
        <>
          <dl className="configuration-meta" id="runtime-model-status-details">
            <dt>{translate(language, "runtimeModelRevision")}</dt>
            <dd>{status.revision}</dd>
            <dt>{translate(language, "runtimeModelStartupDefaultLabel")}</dt>
            <dd>{status.configured_startup_model_key ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelMainModelLabel")}</dt>
            <dd>{status.main_model?.model_key ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelStateLabel")}</dt>
            <dd>{status.main_model?.state ?? status.runtime_state ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelNativeContextLabel")}</dt>
            <dd>{status.model_native_context_limit ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelBackendContextLabel")}</dt>
            <dd>{status.backend_context_limit ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelHardwareContextLabel")}</dt>
            <dd>{status.hardware_verified_context_limit ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelEffectiveContextLabel")}</dt>
            <dd>{status.effective_context_limit ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelContextReasonLabel")}</dt>
            <dd>{status.context_limit_reason_code ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelJudgeModelLabel")}</dt>
            <dd>{status.judge_model?.model_key ?? translate(language, "runtimeModelJudgeNone")}</dd>
            <dt>{translate(language, "runtimeModelGuardModelLabel")}</dt>
            <dd>{status.guard_model?.model_id ?? translate(language, "runtimeModelGuardNone")}</dd>
            <dt>{translate(language, "runtimeModelGovernanceLayerLabel")}</dt>
            <dd>
              {status.governance_layer?.package_id ??
                translate(language, "runtimeModelGovernanceLayerNone")}
            </dd>
          </dl>
          <div className="configuration-controls">
            <label htmlFor="runtime-model-context-input">
              {translate(language, "runtimeModelContextLabel")}
              {" ("}
              {status.loaded_context_size ?? "—"}
              {" / "}
              {status.effective_context_limit ?? "—"}
              {")"}
            </label>
            <input
              id="runtime-model-context-input"
              type="number"
              min={status.minimum_context_size ?? 1}
              max={status.effective_context_limit ?? undefined}
              value={contextInput}
              onChange={(event) => {
                setContextInput(event.target.value);
              }}
            />
            <button
              id="runtime-model-context-apply"
              className="primary"
              type="button"
              disabled={applyingContext}
              onClick={applyContext}
            >
              {translate(language, "runtimeModelApply")}
            </button>
          </div>
          <div className="configuration-controls">
            <label htmlFor="runtime-model-max-new-tokens-input">
              {translate(language, "runtimeModelMaxNewTokensLabel")}
              {" ("}
              {status.current_max_new_tokens ?? "—"}
              {" / "}
              {status.max_output_token_limit ?? "—"}
              {")"}
            </label>
            <input
              id="runtime-model-max-new-tokens-input"
              type="number"
              min={1}
              max={status.max_output_token_limit ?? undefined}
              value={maxTokensInput}
              onChange={(event) => {
                setMaxTokensInput(event.target.value);
              }}
            />
            <button
              id="runtime-model-max-new-tokens-apply"
              className="primary"
              type="button"
              disabled={applyingMaxTokens}
              onClick={applyMaxTokens}
            >
              {translate(language, "runtimeModelApply")}
            </button>
          </div>
          {/* P6-RR-P-WU-004 (Production Wiring Delta item 1): this Legacy
              `/api/v4/runtime-model/switch` Dropdown duplicates the Main
              Provider Selection Panel's own switch (which drives the real
              CAS Transaction via `/api/v6/provider-selection/main` and
              stays in sync with Configured/Active there) — kept, not
              deleted, and its own Apply Contract still works if
              re-enabled, but hidden from the normal Advanced Mode surface
              to avoid two divergent "switch Main" controls. */}
          {status.available_models.length > 0 && (
            <div className="configuration-controls" hidden>
              <label htmlFor="runtime-model-switch-select">
                {translate(language, "runtimeModelSwitchLabel")}
              </label>
              <select
                id="runtime-model-switch-select"
                value={switchTarget}
                onChange={(event) => {
                  setSwitchTarget(event.target.value);
                }}
              >
                {status.available_models.map((model) => (
                  <option key={model.model_key} value={model.model_key}>
                    {model.model_key}
                  </option>
                ))}
              </select>
              <button
                id="runtime-model-switch-apply"
                className="primary"
                type="button"
                disabled={
                  applyingSwitch ||
                  switchTarget === "" ||
                  switchTarget === status.main_model?.model_key
                }
                onClick={applySwitch}
              >
                {translate(language, "runtimeModelSwitchApply")}
              </button>
            </div>
          )}
          <pre id="runtime-model-apply-result" className="configuration-result" aria-live="polite">
            {applyResultText}
          </pre>
        </>
      )}
    </section>
  );
}
