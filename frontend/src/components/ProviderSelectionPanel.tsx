import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiMutationError,
  applyProviderSelection,
  fetchProviderSelectionStatus,
} from "../api/client";
import { translate } from "../i18n/translations";
import type {
  ProviderRole,
  ProviderSelectionStatus,
  RoleProviderSelection,
  UiLanguage,
} from "../types";
import { mergeProviderSelectionStatus } from "./providerSelectionState";

type LoadCapability = "loading" | "ready" | "failed";

interface ProviderSelectionPanelProps {
  language: UiLanguage;
  visible: boolean;
}

const ROLES: readonly ProviderRole[] = ["main", "guard", "judge"];

export default function ProviderSelectionPanel({
  language,
  visible,
}: ProviderSelectionPanelProps) {
  const [capability, setCapability] = useState<LoadCapability>("loading");
  const [status, setStatus] = useState<ProviderSelectionStatus | null>(null);
  const [resultText, setResultText] = useState("");
  const statusRef = useRef<ProviderSelectionStatus | null>(null);
  const mutationQueueRef = useRef<Promise<void>>(Promise.resolve());

  const commitCanonical = useCallback((incoming: ProviderSelectionStatus) => {
    const canonical = mergeProviderSelectionStatus(statusRef.current, incoming);
    statusRef.current = canonical;
    setStatus((current) => mergeProviderSelectionStatus(current, canonical));
  }, []);

  const runFetch = useCallback(() => {
    fetchProviderSelectionStatus()
      .then((incoming) => {
        commitCanonical(incoming);
        setCapability("ready");
      })
      .catch(() => {
        setCapability("failed");
      });
  }, [commitCanonical]);

  useEffect(() => {
    if (visible) {
      runFetch();
    }
  }, [runFetch, visible]);

  if (!visible) {
    return null;
  }

  const applyOne = (role: ProviderRole, providerId: string) => {
    const run = async (): Promise<void> => {
      const current = statusRef.current;
      if (
        current === null ||
        current.revision === null ||
        current.digest_sha512 === null
      ) {
        return;
      }
      try {
        const incoming = await applyProviderSelection(
          role,
          providerId,
          current.revision,
          current.digest_sha512,
        );
        commitCanonical(incoming);
        setResultText(translate(language, "providerSelectionApplySuccess"));
      } catch (error) {
        setResultText(
          error instanceof ApiMutationError
            ? `${error.code ?? "provider_selection_error"}: ${error.message}`
            : translate(language, "providerSelectionApplyFailed"),
        );
        try {
          commitCanonical(await fetchProviderSelectionStatus());
        } catch {
          // Preserve the last server-verified snapshot and original reason.
        }
      }
    };
    mutationQueueRef.current = mutationQueueRef.current.then(run, run);
  };

  const selectionFor = (role: ProviderRole): RoleProviderSelection | null =>
    status?.selections.find((item) => item.role === role) ?? null;

  const renderRole = (role: ProviderRole) => {
    const selection = selectionFor(role);
    const options = status?.options.filter((item) => item.role === role && item.enabled) ?? [];
    const labelKey =
      role === "main"
        ? "providerSelectionMain"
        : role === "guard"
          ? "providerSelectionGuard"
          : "providerSelectionJudge";
    return (
      <div className="provider-selection-role" id={`provider-selection-${role}`} key={role}>
        <label htmlFor={`provider-selection-${role}-select`}>
          {translate(language, labelKey)}
        </label>
        <select
          id={`provider-selection-${role}-select`}
          value={selection?.configured_provider ?? ""}
          disabled={selection === null || options.length === 0}
          onChange={(event) => {
            applyOne(role, event.target.value);
          }}
        >
          {options.map((option) => (
            <option value={option.provider_id} key={`${role}:${option.provider_id}`}>
              {option.display_name}
            </option>
          ))}
        </select>
        {selection === null ? null : (
          <dl className="configuration-meta">
            <dt>{translate(language, "providerSelectionConfigured")}</dt>
            <dd>{selection.configured_provider}</dd>
            <dt>{translate(language, "providerSelectionActive")}</dt>
            <dd>{selection.active_provider ?? "none"}</dd>
            <dt>{translate(language, "providerSelectionState")}</dt>
            <dd>{selection.state}</dd>
            <dt>{translate(language, "providerSelectionIndependence")}</dt>
            <dd>{selection.independence}</dd>
            <dt>{translate(language, "providerSelectionBudget")}</dt>
            <dd>
              {selection.budget === null
                ? "none"
                : `${selection.budget.profile_id} / ${selection.budget.verification_state}`}
            </dd>
            {selection.failure_reason === null ? null : (
              <>
                <dt>{translate(language, "providerSelectionFailure")}</dt>
                <dd>{selection.failure_reason}</dd>
                {selection.failure_at === null ? null : (
                  <>
                    <dt>Failure timestamp</dt>
                    <dd>{selection.failure_at}</dd>
                  </>
                )}
              </>
            )}
          </dl>
        )}
      </div>
    );
  };

  const statusKey =
    capability === "loading"
      ? "providerSelectionLoading"
      : capability === "ready"
        ? "providerSelectionReady"
        : "providerSelectionFailed";

  return (
    <section
      id="provider-selection-panel"
      className="configuration-panel"
      aria-label={translate(language, "providerSelectionTitle")}
    >
      <div className="configuration-panel-header">
        <div>
          <h2>{translate(language, "providerSelectionTitle")}</h2>
          <p>{translate(language, "providerSelectionNote")}</p>
        </div>
        <button
          id="provider-selection-refresh"
          className="secondary"
          type="button"
          disabled={capability === "loading"}
          onClick={() => {
            setCapability("loading");
            runFetch();
          }}
        >
          {translate(language, "featureModesRefresh")}
        </button>
      </div>
      <p id="provider-selection-status-line">{translate(language, statusKey)}</p>
      {status === null || !status.enabled ? null : (
        <>
          <p id="provider-selection-revision">
            {translate(language, "providerSelectionRevision")}: {status.revision}
          </p>
          {ROLES.map(renderRole)}
        </>
      )}
      <pre id="provider-selection-result" className="configuration-result" aria-live="polite">
        {resultText}
      </pre>
    </section>
  );
}
