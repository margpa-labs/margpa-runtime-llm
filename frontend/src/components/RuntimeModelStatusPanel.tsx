import { useEffect, useState } from "react";
import {
  applyRuntimeModelContext,
  applyRuntimeModelMaxNewTokens,
  applyRuntimeModelSwitch,
  fetchRuntimeModelStatus,
} from "../api/client";
import { translate } from "../i18n/translations";
import type { RuntimeModelStatus, UiLanguage } from "../types";

// Unlike RuntimeGovernancePanel/GuardrailGovernancePanel, this panel owns
// its own fetch: the Apply flows below are self-contained CAS round-trips
// against this panel's own `status`, with no other panel or App-level
// state depending on the result, so there is no shared-state reason to
// lift the fetch/apply lifecycle into App.tsx the way the Governance
// panels do.
type LoadCapability = "loading" | "ready" | "failed";

interface RuntimeModelStatusPanelProps {
  language: UiLanguage;
  visible: boolean;
}

export default function RuntimeModelStatusPanel({
  language,
  visible,
}: RuntimeModelStatusPanelProps) {
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [status, setStatus] = useState<RuntimeModelStatus | null>(null);
  const [contextInput, setContextInput] = useState("");
  const [maxTokensInput, setMaxTokensInput] = useState("");
  const [switchTarget, setSwitchTarget] = useState("");
  const [switchContextInput, setSwitchContextInput] = useState("");
  const [applyResultText, setApplyResultText] = useState("");
  const [applyingContext, setApplyingContext] = useState(false);
  const [applyingMaxTokens, setApplyingMaxTokens] = useState(false);
  const [applyingSwitch, setApplyingSwitch] = useState(false);

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
      setSwitchContextInput(String(status.loaded_context_size ?? ""));
    }
  }

  // Fetches without first synchronously setting "loading" — the initial
  // `useState("loading")` already covers the on-mount case, so an Effect
  // calling this needs no extra synchronous setState of its own (avoids
  // react-hooks/set-state-in-effect). The Refresh button's onClick, which
  // is an event handler rather than an Effect, explicitly resets to
  // "loading" itself before calling this.
  const runFetch = () => {
    fetchRuntimeModelStatus()
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

  // Used only after a failed Apply (most commonly a stale CAS token):
  // silently re-syncs `status` if the re-fetch succeeds, but never clears
  // an already-displayed Panel or touches `capability` on its own failure
  // — the user still needs to see the "Failed to apply." message from the
  // Apply call that triggered this, not have it replaced by an unrelated
  // secondary fetch's own error.
  const resyncAfterApplyFailure = () => {
    fetchRuntimeModelStatus()
      .then((next) => {
        setStatus(next);
      })
      .catch(() => {
        // Deliberately ignored — see comment above.
      });
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
        setStatus(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch(() => {
        setApplyResultText(translate(language, "runtimeModelApplyFailed"));
        // A failure (most commonly a stale CAS token: the Snapshot changed
        // elsewhere, e.g. another Tab) leaves this Panel's own status
        // un-refreshed, so retrying Apply would just repeat the same
        // conflict against the same stale revision/digest. Re-fetch so the
        // next Apply attempt uses the real Current CAS token.
        resyncAfterApplyFailure();
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
    const requested = Number.parseInt(switchContextInput, 10);
    if (!Number.isFinite(requested) || requested <= 0) {
      return;
    }
    setApplyingSwitch(true);
    applyRuntimeModelSwitch(status.revision, status.digest_sha512, switchTarget, requested)
      .then((next) => {
        setStatus(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch(() => {
        setApplyResultText(translate(language, "runtimeModelApplyFailed"));
        // Same reasoning as applyContext/applyMaxTokens above: a failed
        // Switch (stale CAS, unregistered target, or a genuine Load
        // failure the Controller already rolled back) leaves this Panel's
        // status un-refreshed, so re-fetch before the next attempt.
        resyncAfterApplyFailure();
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
        setStatus(next);
        setApplyResultText(translate(language, "runtimeModelApplySuccess"));
      })
      .catch(() => {
        setApplyResultText(translate(language, "runtimeModelApplyFailed"));
        resyncAfterApplyFailure();
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
          onClick={refresh}
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
            <dt>{translate(language, "runtimeModelMainModelLabel")}</dt>
            <dd>{status.main_model?.model_key ?? "—"}</dd>
            <dt>{translate(language, "runtimeModelStateLabel")}</dt>
            <dd>{status.main_model?.state ?? status.runtime_state ?? "—"}</dd>
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
              {status.model_native_context_limit ?? "—"}
              {")"}
            </label>
            <input
              id="runtime-model-context-input"
              type="number"
              min={1}
              max={status.model_native_context_limit ?? undefined}
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
          {status.available_models.length > 0 && (
            <div className="configuration-controls">
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
              <input
                id="runtime-model-switch-context-input"
                type="number"
                min={1}
                value={switchContextInput}
                onChange={(event) => {
                  setSwitchContextInput(event.target.value);
                }}
              />
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
