import { useCallback, useEffect, useRef, useState } from "react";
import { translate, type TranslationKey } from "./i18n/translations";
import { usePreference } from "./hooks/usePreference";
import { readConfigurationBootstrap } from "./lib/configurationBootstrap";
import { readGovernanceBootstrap } from "./lib/governanceBootstrap";
import { readRuntimeGovernanceBootstrap } from "./lib/runtimeGovernanceBootstrap";
import { readGuardrailGovernanceBootstrap } from "./lib/guardrailGovernanceBootstrap";
import { readRuntimeModelControlBootstrap } from "./lib/runtimeModelControlBootstrap";
import { readLocalCorpusBootstrap } from "./lib/localCorpusBootstrap";
import { readWebSearchBootstrap } from "./lib/webSearchBootstrap";
import { readDataControlsBootstrap } from "./lib/dataControlsBootstrap";
import { readEventStream } from "./lib/eventStream";
import {
  detailToMessages,
  emptyMessage,
  knownMessageText,
  translatedServerMessage,
} from "./lib/persistentDetailProjection";
import * as api from "./api/client";
import type {
  ChatMessage,
  CitationEvidence,
  ContextUsage,
  ConversationMode,
  DisplayMessage,
  GenerationSettings,
  GovernanceMode,
  GuardrailGovernanceMode,
  LiveJudgeBadge,
  MainGovernanceMode,
  PersistentConversationDetail,
  RuntimeModelStatus,
  StreamEvent,
  UiLanguage,
  UiTheme,
} from "./types";
import TopBar from "./components/TopBar";
import SidebarToggleButton from "./components/SidebarToggleButton";
import Sidebar from "./components/Sidebar/Sidebar";
import type { ChatListAction } from "./components/Sidebar/ChatListItem";
import SettingsModal from "./components/SettingsModal/SettingsModal";
import type { ConfigurationControlState } from "./components/ConfigurationControlPanel";
import type { GovernanceControlState } from "./components/GovernancePanel";
import type { RuntimeGovernanceControlState } from "./components/RuntimeGovernancePanel";
import type { GuardrailGovernanceControlState } from "./components/GuardrailGovernancePanel";
import type { RuntimeModelControlState } from "./components/RuntimeModelStatusPanel";
import type { LocalCorpusState } from "./components/LocalCorpusPanel";
import type { WebSearchPanelState } from "./components/WebSearchPanel";
import type {
  ArchivedChatsState,
  DataControlConsentState,
  DataControlsState,
} from "./components/DataControlsPanel";
import MessageList from "./components/MessageList";
import Composer from "./components/Composer";
import type { SettingsFormState } from "./components/SettingsPanel";

const UI_LANGUAGE_KEY = "margpa.ui_language.v1";
const UI_THEME_KEY = "margpa.ui_theme.v1";
// P8-B (P8-REQ-009): a Presentation-only preference — never sent to the
// Server, never gates the Branch API/data itself (see `MessageBubble`'s
// own `branchUiVisible` prop doc).
const BRANCH_UI_VISIBILITY_KEY = "margpa.branch_ui_visible.v1";

type Status =
  | { kind: "key"; key: TranslationKey; values?: Record<string, string | number> }
  | { kind: "serverWarning"; code: string; fallback: string };

export default function App() {
  const [uiLanguage, setUiLanguage] = usePreference<UiLanguage>(UI_LANGUAGE_KEY, ["ja", "en"], "ja");
  const [uiTheme, setUiTheme] = usePreference<UiTheme>(UI_THEME_KEY, ["white", "dark"], "white");
  // P8-B (P8-REQ-009): no Settings UI is built to flip this in this
  // Package (a deliberately Bounded scope choice — see the P8-B Recovery)
  // — the stored preference key still exists as a genuine Feature Flag a
  // Researcher can set directly (e.g. via DevTools `localStorage.setItem
  // ("margpa.branch_ui_visible.v1", "shown")`), which is what P8-REQ-009
  // itself asks for ("既定非表示"), not a User-facing toggle control.
  const [branchUiVisibility] = usePreference<"shown" | "hidden">(
    BRANCH_UI_VISIBILITY_KEY,
    ["shown", "hidden"],
    "hidden",
  );
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);

  useEffect(() => {
    document.documentElement.lang = uiLanguage;
    document.title = translate(uiLanguage, "documentTitle");
  }, [uiLanguage]);

  useEffect(() => {
    document.documentElement.dataset.theme = uiTheme;
  }, [uiTheme]);

  const [configurationBootstrapEnabled] = useState(() => readConfigurationBootstrap());
  const [governanceBootstrapEnabled] = useState(() => readGovernanceBootstrap());
  const [runtimeGovernanceBootstrapEnabled] = useState(() => readRuntimeGovernanceBootstrap());
  const [guardrailGovernanceBootstrapEnabled] = useState(() => readGuardrailGovernanceBootstrap());
  const [runtimeModelControlBootstrapEnabled] = useState(() => readRuntimeModelControlBootstrap());
  const [localCorpusBootstrapEnabled] = useState(() => readLocalCorpusBootstrap());
  const [webSearchBootstrapEnabled] = useState(() => readWebSearchBootstrap());
  const [dataControlsBootstrapEnabled] = useState(() => readDataControlsBootstrap());

  const [prompt, setPrompt] = useState("");
  const [manualWebEvidenceUrl, setManualWebEvidenceUrl] = useState("");
  const [active, setActive] = useState(false);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [status, setStatus] = useState<Status>({ kind: "key", key: "persistentCapabilityPending" });
  const [runtimeStatus, setRuntimeStatus] = useState<{ kind: "loading" | "metadata" | "known_error"; text: string | null }>(
    { kind: "loading", text: null },
  );
  const [thinkingControlAvailable, setThinkingControlAvailable] = useState(false);
  const [documentationRagControlAvailable, setDocumentationRagControlAvailable] = useState(false);
  const [documentationRagEffectiveState, setDocumentationRagEffectiveState] = useState("unavailable");
  const [persistentEnabled, setPersistentEnabled] = useState(false);
  const [conversationMode, setConversationMode] = useState<ConversationMode>("capability_pending");
  const [persistentConversations, setPersistentConversations] = useState<
    {
      conversation_id: string;
      updated_at: string;
      state: string;
      title: string | null;
      has_active_session: boolean;
    }[]
  >([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [contextUsage, setContextUsage] = useState<ContextUsage | null>(null);
  // Non-null exactly for the turn currently being sent (set in
  // sendPersistentMessage/sendEphemeralMessage, cleared on conversation
  // load/switch/reset and before retry/regenerate) — see MessageList's
  // pinnedMessageId for why this changes the scroll target during a send.
  const [pinnedMessageId, setPinnedMessageId] = useState<string | null>(null);

  const [settingsForm, setSettingsForm] = useState<SettingsFormState>({
    responseLanguage: "ja",
    maxNewTokens: "2048",
    thinkingMode: false,
    thinkingVisibility: false,
    webSearchMode: "disabled",
    summaryMode: "off",
    documentationRagMode: "disabled",
    injectContextUsage: false,
    showContextUsage: false,
    expressiveMode: false,
  });

  const [configurationState, setConfigurationState] = useState<ConfigurationControlState>({
    capability: configurationBootstrapEnabled ? "loading" : "disabled",
    snapshot: null,
    resultText: "",
  });

  const [governanceState, setGovernanceState] = useState<GovernanceControlState>({
    capability: governanceBootstrapEnabled ? "loading" : "disabled",
    status: null,
    resultText: "",
  });

  const [runtimeGovernanceState, setRuntimeGovernanceState] =
    useState<RuntimeGovernanceControlState>({
      capability: runtimeGovernanceBootstrapEnabled ? "loading" : "disabled",
      status: null,
      resultText: "",
    });

  const [guardrailGovernanceState, setGuardrailGovernanceState] =
    useState<GuardrailGovernanceControlState>({
      capability: guardrailGovernanceBootstrapEnabled ? "loading" : "disabled",
      status: null,
      resultText: "",
    });

  const [runtimeModelControlState, setRuntimeModelControlState] =
    useState<RuntimeModelControlState>({
      capability: runtimeModelControlBootstrapEnabled ? "loading" : "disabled",
      status: null,
    });

  const [localCorpusState, setLocalCorpusState] = useState<LocalCorpusState>({
    capability: localCorpusBootstrapEnabled ? "loading" : "disabled",
    documents: [],
    resultText: "",
  });

  const [webSearchState, setWebSearchState] = useState<WebSearchPanelState>({
    capability: "idle",
    result: null,
    resultText: "",
    directUrl: { capability: "idle", result: null, resultText: "" },
  });

  const [dataControlsState, setDataControlsState] = useState<DataControlsState>({
    capability: dataControlsBootstrapEnabled ? "loading" : "disabled",
    consent: null,
    retentionFacts: [],
    resultText: "",
  });

  const [archivedChatsState, setArchivedChatsState] = useState<ArchivedChatsState>({
    capability: "idle",
    items: [],
    resultText: "",
  });

  const configurationLoadSequenceRef = useRef(0);
  const governanceLoadSequenceRef = useRef(0);
  const runtimeGovernanceLoadSequenceRef = useRef(0);
  const guardrailGovernanceLoadSequenceRef = useRef(0);
  const configurationMutationQueueRef = useRef<Promise<void>>(Promise.resolve());
  const localCorpusLoadSequenceRef = useRef(0);
  const localCorpusMutationQueueRef = useRef<Promise<void>>(Promise.resolve());
  const dataControlsLoadSequenceRef = useRef(0);
  const dataControlsMutationQueueRef = useRef<Promise<void>>(Promise.resolve());
  const runtimeModelStatusSequenceRef = useRef(0);
  const acceptedRuntimeModelRevisionRef = useRef(-1);

  // Non-rendering imperative bookkeeping (mirrors the plain-object mutation
  // semantics of the original vanilla state object for fields that never
  // drive rendering on their own).
  const controllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef<string | null>(null);
  // P6-CODEX-024 (Third Rework): the request_id a background poll is
  // actively waiting to see the Judge Run reach a terminal state for —
  // distinct from `requestIdRef` (which also drives Stop/cancel wiring and
  // is cleared on completion) because this one must survive past the Turn
  // itself completing (OBSERVE may continue in background; ENFORCE reaches
  // a terminal Judge/Repair result before the canonical completed event).
  const liveJudgePollRequestIdRef = useRef<string | null>(null);
  const liveJudgePollStartedAtRef = useRef<number | null>(null);
  const [liveJudgeBadge, setLiveJudgeBadge] = useState<LiveJudgeBadge | null>(null);
  const terminalWarningRef = useRef<{ code: string; fallback: string } | null>(null);
  const persistentRevisionRef = useRef<number | null>(null);
  const activePersistentTurnIdRef = useRef<string | null>(null);
  // Canonical ephemeral (v1) conversation history sent as request context.
  // Deliberately separate from the `messages` *display* list: a failed,
  // cancelled, or empty-completion turn stays visible in the transcript but
  // must NOT be resent to the model, mirroring the original's
  // state.messages.push/.pop bookkeeping.
  const chatHistoryRef = useRef<ChatMessage[]>([]);
  const messageIdCounter = useRef(0);
  const nextMessageId = (): string => {
    messageIdCounter.current += 1;
    return `msg-${String(messageIdCounter.current)}`;
  };

  const t = (key: TranslationKey, values: Record<string, string | number> = {}): string =>
    translate(uiLanguage, key, values);

  const statusText: string =
    status.kind === "serverWarning"
      ? t("warning", { message: translatedServerMessage(uiLanguage, status.code, status.fallback) })
      : t(status.key, status.values);

  function setStatusKey(key: TranslationKey, values: Record<string, string | number> = {}): void {
    setStatus({ kind: "key", key, values });
  }

  function setWarningStatus(code: string, fallback: string): void {
    setStatus({ kind: "serverWarning", code, fallback });
  }

  function settingsPayload(attachManualWebEvidence = false): GenerationSettings {
    const trimmedWebEvidenceUrl = manualWebEvidenceUrl.trim();
    return {
      response_language: settingsForm.responseLanguage,
      max_new_tokens: Number(settingsForm.maxNewTokens),
      thinking_mode: settingsForm.thinkingMode ? "enabled" : "disabled",
      thinking_visibility: settingsForm.thinkingVisibility ? "visible" : "hidden",
      summary_mode: settingsForm.summaryMode,
      documentation_rag_mode: settingsForm.documentationRagMode,
      context_usage_prompt_injection_mode: settingsForm.injectContextUsage ? "enabled" : "disabled",
      expressive_mode: settingsForm.expressiveMode ? "enabled" : "disabled",
      // P8-A: a one-shot Field, included only for the primary "send a new
      // message" call sites and only when the User actually typed a URL —
      // Retry/Regenerate never pass `attachManualWebEvidence`, so they never
      // re-trigger a fresh Fetch for an unrelated historical Turn.
      ...(attachManualWebEvidence && trimmedWebEvidenceUrl
        ? { manual_web_evidence_url: trimmedWebEvidenceUrl }
        : {}),
    };
  }

  function updateMessageById(id: string, updater: (message: DisplayMessage) => DisplayMessage): void {
    setMessages((previous) => previous.map((message) => (message.id === id ? updater(message) : message)));
  }

  // P6-CODEX-024 (Third Rework): called from every "start" event handler —
  // Judge/Repair start after raw generation. OBSERVE may outlive the
  // canonical Turn; ENFORCE completes before its Presented Final is sent.
  function beginLiveJudgePolling(requestId: string | null): void {
    liveJudgePollRequestIdRef.current = requestId;
    liveJudgePollStartedAtRef.current = requestId === null ? null : Date.now();
  }

  // P6-CODEX-024 (Third Rework): a single long-lived interval (not
  // recreated per Turn) that only ever does network work while
  // `liveJudgePollRequestIdRef` names a Turn actually being waited on —
  // idle between Turns costs nothing beyond the interval tick itself.
  useEffect(() => {
    const POLL_INTERVAL_MS = 1500;
    const MAX_POLL_MS = 45_000;
    const cancelledRef = { current: false };

    const tick = async () => {
      const targetRequestId = liveJudgePollRequestIdRef.current;
      if (targetRequestId === null) {
        return;
      }
      try {
        const status = await api.fetchFeatureModesStatus();
        if (cancelledRef.current || liveJudgePollRequestIdRef.current !== targetRequestId) {
          return;
        }
        if (status.judge.current_request_id === targetRequestId) {
          const state = status.judge.state ?? "idle";
          setLiveJudgeBadge({
            requestId: targetRequestId,
            state,
            repairAccepted: status.judge.last_result?.repair_accepted ?? null,
          });
          if (["completed", "failed", "cancelled", "degraded"].includes(state)) {
            liveJudgePollRequestIdRef.current = null;
          }
        } else {
          const startedAt = liveJudgePollStartedAtRef.current;
          if (startedAt !== null && Date.now() - startedAt > MAX_POLL_MS) {
            // Never became "current" within a generous bound (e.g. Judge
            // is OFF) — stop polling rather than forever.
            liveJudgePollRequestIdRef.current = null;
          }
        }
      } catch {
        // Best-effort status projection only. ENFORCE safety is owned by
        // the server-side Presented Final boundary, never by this poll.
      }
    };

    const interval = window.setInterval(() => {
      void tick();
    }, POLL_INTERVAL_MS);
    return () => {
      cancelledRef.current = true;
      window.clearInterval(interval);
    };
  }, []);

  // Mirrors the original rollbackPendingUser(): pops the optimistically
  // pushed user turn from the *request history* only. The display transcript
  // is never modified here — a failed/cancelled/empty turn stays visible so
  // the user can see what happened, it just won't be resent to the model.
  function rollbackPendingUserIfLast(): void {
    const history = chatHistoryRef.current;
    const last = history.at(-1);
    if (last?.role === "user") {
      chatHistoryRef.current = history.slice(0, -1);
    }
  }

  // --- Runtime (v1) bootstrap ---
  useEffect(() => {
    const cancelledRef = { current: false };
    api
      .fetchRuntime()
      .then((runtime) => {
        if (cancelledRef.current) return;
        setRuntimeStatus({
          kind: "metadata",
          text: [
            `${runtime.model_key} active`,
            [runtime.profile_key, runtime.device_kind, runtime.acceleration_api].join(" • "),
          ].join(" · "),
        });
        setSettingsForm((previous) => ({
          ...previous,
          responseLanguage: runtime.defaults.response_language,
          maxNewTokens: String(runtime.defaults.max_new_tokens),
          thinkingMode: runtime.defaults.thinking_control_available && runtime.defaults.thinking_mode === "enabled",
          thinkingVisibility: runtime.defaults.thinking_visibility === "visible",
          summaryMode: runtime.defaults.summary_mode,
          documentationRagMode: runtime.documentation_rag.default_mode,
        }));
        setThinkingControlAvailable(runtime.defaults.thinking_control_available);
        setDocumentationRagEffectiveState(runtime.documentation_rag.effective_state);
        setDocumentationRagControlAvailable(runtime.documentation_rag.control_available);
      })
      .catch(() => {
        if (cancelledRef.current) return;
        setThinkingControlAvailable(false);
        setDocumentationRagControlAvailable(false);
        setDocumentationRagEffectiveState("unavailable");
        setRuntimeStatus({ kind: "known_error", text: null });
      });
    return () => {
      cancelledRef.current = true;
    };
    // Runs once on mount, matching the original's single loadRuntime() call.
  }, []);

  const acceptRuntimeModelStatus = useCallback((next: RuntimeModelStatus): void => {
    const nextRevision = next.revision ?? -1;
    if (nextRevision < acceptedRuntimeModelRevisionRef.current) {
      return;
    }
    acceptedRuntimeModelRevisionRef.current = nextRevision;
    setRuntimeModelControlState({ capability: "ready", status: next });
    if (next.current_max_new_tokens !== null) {
      setSettingsForm((current) => ({
        ...current,
        maxNewTokens: String(next.current_max_new_tokens),
      }));
    }
  }, []);

  const loadRuntimeModelStatus = useCallback(
    async (showLoading: boolean): Promise<void> => {
      if (!runtimeModelControlBootstrapEnabled) {
        return;
      }
      const sequence = ++runtimeModelStatusSequenceRef.current;
      if (showLoading) {
        setRuntimeModelControlState((current) => ({ ...current, capability: "loading" }));
      }
      try {
        const next = await api.fetchRuntimeModelStatus();
        if (sequence === runtimeModelStatusSequenceRef.current) {
          acceptRuntimeModelStatus(next);
        }
      } catch {
        if (sequence === runtimeModelStatusSequenceRef.current) {
          setRuntimeModelControlState((current) => ({ ...current, capability: "failed" }));
        }
      }
    },
    [acceptRuntimeModelStatus, runtimeModelControlBootstrapEnabled],
  );

  useEffect(() => {
    if (!runtimeModelControlBootstrapEnabled) {
      return;
    }
    // Subscribe first and schedule initial synchronization as an external
    // timer callback; initial React state already projects "loading".
    const initialLoad = window.setTimeout(() => {
      void loadRuntimeModelStatus(false);
    }, 0);
    const interval = window.setInterval(() => {
      void loadRuntimeModelStatus(false);
    }, 1500);
    return () => {
      window.clearTimeout(initialLoad);
      window.clearInterval(interval);
    };
  }, [loadRuntimeModelStatus, runtimeModelControlBootstrapEnabled]);

  // --- Configuration Control ---
  const loadConfigurationControl = useCallback(async (): Promise<void> => {
    if (!configurationBootstrapEnabled) {
      return;
    }
    const sequence = ++configurationLoadSequenceRef.current;
    setConfigurationState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const runtime = await api.fetchConfigurationRuntime();
      if (!runtime.enabled || !runtime.non_persistent) {
        throw new Error("configuration_runtime_invalid");
      }
      const snapshot = await api.fetchConfigurationEffective();
      if (sequence !== configurationLoadSequenceRef.current) {
        return;
      }
      setConfigurationState({ capability: "ready", snapshot, resultText: "" });
    } catch {
      if (sequence !== configurationLoadSequenceRef.current) {
        return;
      }
      setConfigurationState({ capability: "failed", snapshot: null, resultText: "" });
    }
    // configurationBootstrapEnabled is set once (lazy useState init) and
    // never updated again, so this callback is effectively stable.
  }, [configurationBootstrapEnabled]);

  useEffect(() => {
    // loadConfigurationControl()'s first statement synchronously sets
    // capability to "loading" — already the initial state on first mount,
    // and intentional (not deferred) so a later manual refresh shows the
    // loading indicator immediately rather than after the fetch settles.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadConfigurationControl();
  }, [loadConfigurationControl]);

  function enqueueConfigurationModeMutation(
    patch: Record<string, unknown>,
    setResult: (message: string) => void,
    successKey: TranslationKey,
    failureKey: TranslationKey,
    refreshRelated?: () => Promise<void>,
  ): void {
    const run = async (): Promise<void> => {
      try {
        // Every queued click resolves a fresh CAS token at execution time.
        // This serializes rapid clicks across all Configuration-backed Mode
        // panels without presenting an optimistic value as Canonical.
        const snapshot = await api.fetchConfigurationEffective();
        const response = await api.applyConfigurationPatch(
          api.newActionId(),
          snapshot.revision,
          snapshot.digest_sha512,
          patch,
        );
        if (response.status === 409) {
          setResult(t("configurationConflict"));
          await loadConfigurationControl();
          if (refreshRelated !== undefined) {
            await refreshRelated();
          }
          return;
        }
        if (!response.ok) {
          throw new api.ApiMutationError(
            await api.safeError(response, "configuration_mode_apply_failed"),
          );
        }
        await loadConfigurationControl();
        if (refreshRelated !== undefined) {
          await refreshRelated();
        }
        setResult(t(successKey));
      } catch (error) {
        setResult(
          error instanceof api.ApiMutationError
            ? `${t(failureKey)} [${error.code ?? "configuration_mode_apply_failed"}] ${error.message}`
            : t(failureKey),
        );
        await loadConfigurationControl();
        if (refreshRelated !== undefined) {
          await refreshRelated();
        }
      }
    };
    configurationMutationQueueRef.current = configurationMutationQueueRef.current.then(run, run);
  }

  const loadLocalCorpus = useCallback(async (): Promise<void> => {
    if (!localCorpusBootstrapEnabled) {
      return;
    }
    const sequence = ++localCorpusLoadSequenceRef.current;
    setLocalCorpusState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const list = await api.fetchLocalCorpusDocuments();
      if (sequence !== localCorpusLoadSequenceRef.current) {
        return;
      }
      setLocalCorpusState({ capability: "ready", documents: list.documents, resultText: "" });
    } catch {
      if (sequence !== localCorpusLoadSequenceRef.current) {
        return;
      }
      setLocalCorpusState({ capability: "failed", documents: [], resultText: "" });
    }
    // localCorpusBootstrapEnabled is set once (lazy useState init) and never
    // updated again, so this callback is effectively stable.
  }, [localCorpusBootstrapEnabled]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadLocalCorpus();
  }, [loadLocalCorpus]);

  function enqueueLocalCorpusMutation(
    operation: () => Promise<unknown>,
    successKey: TranslationKey,
    failureKey: TranslationKey,
  ): void {
    const run = async (): Promise<void> => {
      let resultText: string;
      try {
        await operation();
        resultText = t(successKey);
      } catch (error) {
        resultText =
          error instanceof api.ApiMutationError
            ? `${t(failureKey)} [${error.code ?? "local_corpus_mutation_failed"}] ${error.message}`
            : t(failureKey);
      }
      await loadLocalCorpus();
      setLocalCorpusState((previous) => ({ ...previous, resultText }));
    };
    localCorpusMutationQueueRef.current = localCorpusMutationQueueRef.current.then(run, run);
  }

  function handleLocalCorpusRegister(title: string, content: string): void {
    enqueueLocalCorpusMutation(
      () => api.registerLocalCorpusDocument(title, content),
      "localCorpusRegisterSuccess",
      "localCorpusRegisterFailed",
    );
  }

  function handleLocalCorpusUpdate(documentId: string, title: string, content: string): void {
    enqueueLocalCorpusMutation(
      () => api.updateLocalCorpusDocument(documentId, title, content),
      "localCorpusUpdateSuccess",
      "localCorpusUpdateFailed",
    );
  }

  function handleLocalCorpusDelete(documentId: string): void {
    enqueueLocalCorpusMutation(
      () => api.deleteLocalCorpusDocument(documentId),
      "localCorpusDeleteSuccess",
      "localCorpusDeleteFailed",
    );
  }

  async function handleLocalCorpusEditRequest(
    documentId: string,
  ): Promise<{ title: string; content: string } | null> {
    try {
      const document = await api.fetchLocalCorpusDocument(documentId);
      return { title: document.title, content: document.content };
    } catch {
      return null;
    }
  }

  const loadDataControls = useCallback(async (): Promise<void> => {
    if (!dataControlsBootstrapEnabled) {
      return;
    }
    const sequence = ++dataControlsLoadSequenceRef.current;
    setDataControlsState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const policy = await api.fetchDataControlPolicy();
      if (sequence !== dataControlsLoadSequenceRef.current) {
        return;
      }
      setDataControlsState({
        capability: "ready",
        consent: policy.consent,
        retentionFacts: policy.retention_facts,
        resultText: "",
      });
    } catch {
      if (sequence !== dataControlsLoadSequenceRef.current) {
        return;
      }
      setDataControlsState({
        capability: "failed",
        consent: null,
        retentionFacts: [],
        resultText: "",
      });
    }
  }, [dataControlsBootstrapEnabled]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadDataControls();
  }, [loadDataControls]);

  function enqueueDataControlsMutation(operation: () => Promise<unknown>): void {
    const run = async (): Promise<void> => {
      try {
        await operation();
      } catch {
        // Fall through to loadDataControls() below either way — a fresh
        // GET after a failed mutation shows the true server-side state
        // rather than an unconfirmed optimistic value.
      }
      await loadDataControls();
    };
    dataControlsMutationQueueRef.current = dataControlsMutationQueueRef.current.then(run, run);
  }

  function handleDataControlsToggle(key: keyof DataControlConsentState, value: boolean): void {
    enqueueDataControlsMutation(() => api.updateDataControlConsent({ [key]: value }));
  }

  function handleDataControlsReset(): void {
    enqueueDataControlsMutation(() => api.resetDataControlConsent());
  }

  function handleWebSearch(query: string): void {
    setWebSearchState((previous) => ({ ...previous, capability: "loading" }));
    api
      .searchWeb(query, "manual")
      .then((result) => {
        setWebSearchState({
          capability: "ready",
          result,
          resultText: t("webSearchPanelSearchSuccess"),
        });
      })
      .catch((error: unknown) => {
        setWebSearchState({
          capability: "failed",
          result: null,
          resultText:
            error instanceof api.ApiMutationError
              ? `${t("webSearchPanelSearchFailed")} [${error.code ?? "web_search_failed"}] ${error.message}`
              : t("webSearchPanelSearchFailed"),
        });
      });
  }

  function handleFetchDirectUrl(url: string): void {
    setWebSearchState((previous) => ({
      ...previous,
      directUrl: { capability: "loading", result: previous.directUrl?.result ?? null, resultText: "" },
    }));
    api
      .fetchDirectUrl(url, "manual")
      .then((result) => {
        setWebSearchState((previous) => ({
          ...previous,
          directUrl: {
            capability: "ready",
            result,
            resultText: t("webSearchPanelSearchSuccess"),
          },
        }));
      })
      .catch((error: unknown) => {
        setWebSearchState((previous) => ({
          ...previous,
          directUrl: {
            capability: "failed",
            result: null,
            resultText:
              error instanceof api.ApiMutationError
                ? `${t("webSearchPanelDirectUrlFailed")} [${error.code ?? "web_search_direct_fetch_failed"}] ${error.message}`
                : t("webSearchPanelDirectUrlFailed"),
          },
        }));
      });
  }

  function handleConfigurationApply(researchDeveloperMode: string): void {
    enqueueConfigurationModeMutation(
      { research_developer_mode: researchDeveloperMode },
      (message) => {
        setConfigurationState((previous) => ({ ...previous, resultText: message }));
      },
      "configurationApplied",
      "configurationFailed",
    );
  }

  // --- Governance Definitions (Phase 3-F) ---
  const loadGovernanceStatus = useCallback(async (): Promise<void> => {
    if (!governanceBootstrapEnabled) {
      return;
    }
    const sequence = ++governanceLoadSequenceRef.current;
    setGovernanceState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const status = await api.fetchGovernanceStatus();
      if (sequence !== governanceLoadSequenceRef.current) {
        return;
      }
      setGovernanceState({ capability: "ready", status, resultText: "" });
    } catch {
      if (sequence !== governanceLoadSequenceRef.current) {
        return;
      }
      setGovernanceState({ capability: "failed", status: null, resultText: "" });
    }
    // governanceBootstrapEnabled is set once (lazy useState init) and never
    // updated again, so this callback is effectively stable.
  }, [governanceBootstrapEnabled]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadGovernanceStatus();
  }, [loadGovernanceStatus]);

  // Mode Mutation is a Typed Field on Configuration Control's shared
  // Preview/Apply state machine (Revision/Digest/CAS, Operation
  // Idempotency) — not a Governance-only endpoint. See
  // src/margpa_runtime_llm/web/governance_routes.py's module docstring.
  function handleGovernanceApply(requestedMode: GovernanceMode): void {
    enqueueConfigurationModeMutation(
      { governance_mode: requestedMode },
      (message) => {
        setGovernanceState((previous) => ({ ...previous, resultText: message }));
      },
      "governanceApplied",
      "governanceApplyFailed",
      loadGovernanceStatus,
    );
  }

  // --- Main Runtime Governance (Phase 4) ---
  const loadRuntimeGovernanceStatus = useCallback(async (): Promise<void> => {
    if (!runtimeGovernanceBootstrapEnabled) {
      return;
    }
    const sequence = ++runtimeGovernanceLoadSequenceRef.current;
    setRuntimeGovernanceState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const status = await api.fetchRuntimeGovernanceStatus();
      if (sequence !== runtimeGovernanceLoadSequenceRef.current) {
        return;
      }
      setRuntimeGovernanceState({ capability: "ready", status, resultText: "" });
    } catch {
      if (sequence !== runtimeGovernanceLoadSequenceRef.current) {
        return;
      }
      setRuntimeGovernanceState({ capability: "failed", status: null, resultText: "" });
    }
    // runtimeGovernanceBootstrapEnabled is set once (lazy useState init)
    // and never updated again, so this callback is effectively stable.
  }, [runtimeGovernanceBootstrapEnabled]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadRuntimeGovernanceStatus();
  }, [loadRuntimeGovernanceStatus]);

  // Mode Mutation is a Typed Field on Configuration Control's shared
  // Preview/Apply state machine (P4-CODEX-002 Rework) — the same pattern
  // as Phase 3's own governance_mode, not a separate direct-Apply route.
  // See src/margpa_runtime_llm/web/runtime_governance_routes.py's module
  // docstring.
  function handleRuntimeGovernanceApply(requestedMode: MainGovernanceMode): void {
    enqueueConfigurationModeMutation(
      { main_governance_mode: requestedMode },
      (message) => {
        setRuntimeGovernanceState((previous) => ({ ...previous, resultText: message }));
      },
      "runtimeGovernanceApplied",
      "runtimeGovernanceApplyFailed",
      loadRuntimeGovernanceStatus,
    );
  }

  // --- Guardrail Governance (Phase 5) ---
  const loadGuardrailGovernanceStatus = useCallback(async (): Promise<void> => {
    if (!guardrailGovernanceBootstrapEnabled) {
      return;
    }
    const sequence = ++guardrailGovernanceLoadSequenceRef.current;
    setGuardrailGovernanceState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const status = await api.fetchGuardrailGovernanceStatus();
      if (sequence !== guardrailGovernanceLoadSequenceRef.current) {
        return;
      }
      setGuardrailGovernanceState((previous) => ({
        capability: "ready",
        status,
        resultText: previous.resultText,
      }));
    } catch {
      if (sequence !== guardrailGovernanceLoadSequenceRef.current) {
        return;
      }
      setGuardrailGovernanceState((previous) => ({
        capability: "failed",
        status: null,
        resultText: previous.resultText,
      }));
    }
    // guardrailGovernanceBootstrapEnabled is set once (lazy useState init)
    // and never updated again, so this callback is effectively stable.
  }, [guardrailGovernanceBootstrapEnabled]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadGuardrailGovernanceStatus();
  }, [loadGuardrailGovernanceStatus]);

  // Mode Mutation is a Typed Field on Configuration Control's shared
  // Preview/Apply state machine (P5-F-WU-002, mirrors P4-CODEX-002
  // Rework) — the same pattern as Phase 3/4's own Governance Modes, not
  // a separate direct-Apply route. See
  // src/margpa_runtime_llm/web/guardrail_governance_routes.py's module
  // docstring.
  function handleGuardrailGovernanceApply(requestedMode: GuardrailGovernanceMode): void {
    enqueueConfigurationModeMutation(
      { guardrail_governance_mode: requestedMode },
      (message) => {
        setGuardrailGovernanceState((previous) => ({ ...previous, resultText: message }));
      },
      "guardrailGovernanceApplied",
      "guardrailGovernanceApplyFailed",
      loadGuardrailGovernanceStatus,
    );
  }

  // --- Ephemeral (v1) streaming ---
  function handleEphemeralEvent(event: StreamEvent, assistantId: string): boolean {
    const data = event.data;
    if (event.type === "start") {
      requestIdRef.current = data.request_id ?? null;
      beginLiveJudgePolling(data.request_id ?? null);
      updateMessageById(assistantId, (message) => ({ ...message, requestId: data.request_id ?? null }));
      terminalWarningRef.current = null;
      setStatusKey(data.state === "retrieving_documentation" ? "retrievingDocumentation" : "generating");
      return false;
    }
    if (event.type === "retrieval") {
      const citations: CitationEvidence = {
        citations: Array.isArray(data.citations) ? data.citations : [],
        warnings: Array.isArray(data.warnings) ? data.warnings : [],
      };
      updateMessageById(assistantId, (message) => ({ ...message, citations }));
      const warning = citations.warnings.at(-1);
      if (warning !== undefined) {
        terminalWarningRef.current = { code: warning.code, fallback: warning.message };
        setWarningStatus(warning.code, warning.message);
      } else {
        setStatusKey("generating");
      }
      return false;
    }
    if (event.type === "status") {
      // P6-CODEX-012 (Second Rework, P6-OBS-004's Current Request State
      // Machine): "preparing"/"guarding" precede the Turn's own `start`
      // event; any other `status` state (including ones this build does
      // not yet recognize) is intentionally left as a silent no-op rather
      // than showing a raw code.
      if (data.state === "preparing") {
        setStatusKey("preparingTurn");
      } else if (data.state === "guarding") {
        setStatusKey("guardingTurn");
      } else if (data.state === "summarizing_answer") {
        setStatusKey("summarizing");
      }
      return false;
    }
    if (event.type === "delta") {
      const deltaText = data.text ?? "";
      if (data.channel === "reasoning") {
        updateMessageById(assistantId, (message) => ({
          ...message,
          thinkingVisible: true,
          thinkingText: message.thinkingText + deltaText,
        }));
      } else if (data.channel === "final") {
        updateMessageById(assistantId, (message) => ({ ...message, content: message.content + deltaText }));
      } else {
        throw new Error(t("streamProtocolError"));
      }
      return false;
    }
    if (event.type === "warning") {
      const warningCode = data.code ?? "unexpected_error";
      const warningMessage = data.message ?? "";
      terminalWarningRef.current = { code: warningCode, fallback: warningMessage };
      if (warningCode === "final_answer_token_limit") {
        updateMessageById(assistantId, (message) => ({
          ...message,
          isError: true,
          content: knownMessageText(uiLanguage, warningCode, warningMessage),
        }));
      }
      setWarningStatus(warningCode, warningMessage);
      return false;
    }
    if (event.type === "completed") {
      const canonical = data.assistant_message?.content ?? "";
      setContextUsage(data.context_usage ?? null);
      if (canonical.trim()) {
        updateMessageById(assistantId, (message) => ({ ...message, content: canonical, isFinal: true }));
        chatHistoryRef.current = [...chatHistoryRef.current, { role: "assistant", content: canonical }];
      } else {
        rollbackPendingUserIfLast();
        if (terminalWarningRef.current === null) {
          setMessages((previous) => previous.filter((message) => message.id !== assistantId));
        }
      }
      if (terminalWarningRef.current !== null) {
        setWarningStatus(terminalWarningRef.current.code, terminalWarningRef.current.fallback);
      } else {
        setStatusKey("completed", { reason: data.finish_reason ?? "unknown" });
      }
      return canonical.trim().length > 0;
    }
    if (event.type === "cancelled") {
      rollbackPendingUserIfLast();
      updateMessageById(assistantId, (message) => ({ ...message, isIncomplete: true, isFinal: true }));
      setStatusKey("stopped");
      return false;
    }
    // Every other StreamEvent variant returned above, so `event.type` here
    // can only be "error".
    rollbackPendingUserIfLast();
    updateMessageById(assistantId, (message) => ({
      ...message,
      isError: true,
      isFinal: true,
      content: knownMessageText(uiLanguage, data.code ?? null, data.message ?? ""),
    }));
    setWarningStatus(data.code ?? "unknown", data.message ?? "");
    return false;
  }

  async function sendEphemeralMessage(): Promise<void> {
    const content = prompt;
    if (!content.trim()) {
      setStatusKey("emptyMessage");
      return;
    }
    const maxNewTokens = Number(settingsForm.maxNewTokens);
    const currentRuntimeMaxNewTokens =
      runtimeModelControlState.status?.current_max_new_tokens ?? 2048;
    if (
      !Number.isInteger(maxNewTokens) ||
      maxNewTokens < 1 ||
      maxNewTokens > currentRuntimeMaxNewTokens
    ) {
      setStatusKey("invalidTokenLimit");
      return;
    }
    chatHistoryRef.current = [...chatHistoryRef.current, { role: "user", content }];
    const history: ChatMessage[] = chatHistoryRef.current;
    const userId = nextMessageId();
    const assistantId = nextMessageId();
    setMessages((previous) => [...previous, emptyMessage("user", content, userId), emptyMessage("assistant", "", assistantId)]);
    setPinnedMessageId(userId);
    setPrompt("");
    setManualWebEvidenceUrl("");
    controllerRef.current = new AbortController();
    requestIdRef.current = null;
    terminalWarningRef.current = null;
    setActive(true);
    setStatusKey("connecting");

    try {
      const response = await api.startChatStream(
        history,
        settingsPayload(true),
        controllerRef.current.signal,
      );
      if (!response.ok) {
        const failure = await api.safeError(response, t("requestFailed"));
        throw Object.assign(new Error(failure.message), { code: failure.code });
      }
      await readEventStream(
        response,
        (event) => {
          handleEphemeralEvent(event, assistantId);
        },
        t("streamUnavailable"),
      );
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        // Matches the original: the assistant bubble is left as-is (whatever
        // partial content streamed in before the abort), not removed or
        // marked incomplete here — only the request-history bookkeeping
        // rolls back.
        rollbackPendingUserIfLast();
        setStatusKey("stopped");
      } else {
        rollbackPendingUserIfLast();
        const code = error instanceof Error ? ((error as Error & { code?: string }).code ?? null) : null;
        const message = error instanceof Error ? error.message : t("requestFailed");
        updateMessageById(assistantId, (existing) => ({
          ...existing,
          isError: true,
          isFinal: true,
          content: knownMessageText(uiLanguage, code, message),
        }));
        setStatusKey("requestFailed");
      }
    } finally {
      controllerRef.current = null;
      requestIdRef.current = null;
      terminalWarningRef.current = null;
      setActive(false);
      // P4-CODEX-014: Best-effort Observability refresh only — never
      // awaited into this function's own error handling, and
      // loadRuntimeGovernanceStatus never throws (it catches its own
      // fetch failure into `capability: "failed"`), so a Status read
      // failure here can never rewrite the Chat Result set above. A
      // no-op when the Bootstrap tag reports disabled (checked inside
      // loadRuntimeGovernanceStatus itself) — Call 0 stays Call 0.
      void loadRuntimeGovernanceStatus();
      void loadGuardrailGovernanceStatus();
    }
  }

  // --- Persistent (v2) ---
  async function loadPersistentList(): Promise<void> {
    const page = await api.fetchPersistentList();
    setPersistentConversations(page.items);
  }

  async function loadPersistentDetail(conversationId: string): Promise<void> {
    const detail = await api.fetchPersistentDetail(conversationId);
    persistentRevisionRef.current = detail.storage_revision;
    setMessages(detailToMessages(detail, uiLanguage));
  }

  useEffect(() => {
    const cancelledRef = { current: false };
    void (async () => {
      try {
        const runtime = await api.fetchPersistentRuntime();
        if (cancelledRef.current) return;
        if (runtime.source_of_truth !== "server" || typeof runtime.enabled !== "boolean") {
          throw new Error("persistent_capability_invalid");
        }
        if (runtime.enabled) {
          setConversationMode("persistent");
          setPersistentEnabled(true);
          await loadPersistentList();
        } else {
          setConversationMode("ephemeral");
          setPersistentEnabled(false);
        }
        setStatusKey("idle");
      } catch {
        if (cancelledRef.current) return;
        setConversationMode("capability_failed");
        setPersistentEnabled(false);
        setStatusKey("persistentCapabilityFailed");
      }
    })();
    return () => {
      cancelledRef.current = true;
    };
  }, []);

  async function selectPersistentConversation(conversationId: string): Promise<void> {
    if (active) return;
    setSelectedConversationId(conversationId);
    setContextUsage(null);
    setPinnedMessageId(null);
    // P8-MR9-2 (P8-CODEX-011/UF-UI-011): a past Turn's Failure warning
    // belongs to the Current Live Attempt only — switching Chat must never
    // leave a different Conversation's stale warning sitting in the
    // Composer. The Historical Failure bubble itself is untouched: it
    // lives in `messages`/`turns`, reloaded fresh by loadPersistentDetail
    // below, not in this Application-wide `status`.
    terminalWarningRef.current = null;
    setStatusKey("idle");
    await loadPersistentDetail(conversationId);
  }

  // Returns the newly created conversation's id so a caller that needs it
  // immediately (sendPersistentMessage) doesn't have to read
  // selectedConversationId back out of state right after setting it — that
  // state update isn't visible in this same closure until the next render,
  // so re-reading it here would just see the pre-update (still null) value.
  async function createPersistentConversationAndSelect(): Promise<string | null> {
    try {
      const result = await api.createPersistentConversation(api.newActionId());
      setSelectedConversationId(result.detail.conversation_id);
      persistentRevisionRef.current = result.detail.storage_revision;
      setMessages(detailToMessages(result.detail, uiLanguage));
      setContextUsage(null);
      setPinnedMessageId(null);
      await loadPersistentList();
      setStatusKey("idle");
      return result.detail.conversation_id;
    } catch {
      setStatusKey("requestFailed");
      return null;
    }
  }

  async function handlePersistentFailure(response: Response): Promise<void> {
    const failure = await api.safeError(response, t("requestFailed"));
    if (failure.code === "revision_conflict" || failure.code === "operation_already_applied") {
      setStatusKey("persistentConflict");
      if (selectedConversationId !== null) {
        await loadPersistentDetail(selectedConversationId);
      }
      return;
    }
    setStatusKey("requestFailed");
  }

  function handlePersistentEvent(event: StreamEvent, assistantId: string): boolean {
    if (event.type === "start") {
      requestIdRef.current = event.data.request_id ?? null;
      beginLiveJudgePolling(event.data.request_id ?? null);
      updateMessageById(assistantId, (message) => ({
        ...message,
        requestId: event.data.request_id ?? null,
      }));
      if (typeof event.data.durable_revision === "number") {
        persistentRevisionRef.current = event.data.durable_revision;
      }
      activePersistentTurnIdRef.current = event.data.turn_id ?? null;
      setStatusKey("generating");
      return false;
    }
    if (["retrieval", "status", "delta", "warning"].includes(event.type)) {
      handleEphemeralEvent(event, assistantId);
      return false;
    }
    if (["completed", "cancelled", "error"].includes(event.type)) {
      const durable = event.data.durable_revision;
      if (Number.isInteger(durable)) {
        persistentRevisionRef.current = durable as number;
      }
      if (event.type === "completed") {
        setStatusKey("completed", { reason: event.data.finish_reason ?? "unknown" });
        const canonical = event.data.assistant_message?.content ?? "";
        setContextUsage(event.data.context_usage ?? null);
        updateMessageById(assistantId, (message) => ({ ...message, content: canonical, isFinal: true }));
      } else if (event.type === "cancelled") {
        setStatusKey("stopped");
        updateMessageById(assistantId, (message) => ({ ...message, isIncomplete: true, isFinal: true }));
      } else {
        setWarningStatus(event.data.code ?? "generation_failed", event.data.message ?? "");
        updateMessageById(assistantId, (message) => ({
          ...message,
          isError: true,
          isFinal: true,
          content: knownMessageText(uiLanguage, event.data.code ?? null, event.data.message ?? ""),
        }));
      }
      activePersistentTurnIdRef.current = null;
      return Number.isInteger(durable);
    }
    return false;
  }

  async function sendPersistentMessage(): Promise<void> {
    const content = prompt;
    if (!content.trim()) {
      setStatusKey("emptyMessage");
      return;
    }
    let conversationId = selectedConversationId;
    if (conversationId === null) {
      conversationId = await createPersistentConversationAndSelect();
    }
    if (conversationId === null || persistentRevisionRef.current === null) {
      return;
    }
    const maxNewTokens = Number(settingsForm.maxNewTokens);
    const currentRuntimeMaxNewTokens =
      runtimeModelControlState.status?.current_max_new_tokens ?? 2048;
    if (
      !Number.isInteger(maxNewTokens) ||
      maxNewTokens < 1 ||
      maxNewTokens > currentRuntimeMaxNewTokens
    ) {
      setStatusKey("invalidTokenLimit");
      return;
    }
    const userId = nextMessageId();
    const assistantId = nextMessageId();
    setMessages((previous) => [...previous, emptyMessage("user", content, userId), emptyMessage("assistant", "", assistantId)]);
    setPinnedMessageId(userId);
    controllerRef.current = new AbortController();
    requestIdRef.current = null;
    setActive(true);
    setStatusKey("connecting");
    const operationId = api.newActionId();
    try {
      const response = await api.startPersistentTurnStream(
        conversationId,
        content,
        settingsPayload(true),
        operationId,
        persistentRevisionRef.current,
        controllerRef.current.signal,
      );
      if (!response.ok) {
        await handlePersistentFailure(response);
        return;
      }
      setPrompt("");
      setManualWebEvidenceUrl("");
      const durableTerminalObserved = { current: false };
      await readEventStream(
        response,
        (event) => {
          durableTerminalObserved.current =
            handlePersistentEvent(event, assistantId) || durableTerminalObserved.current;
        },
        t("streamUnavailable"),
      );
      if (!durableTerminalObserved.current) {
        updateMessageById(assistantId, (message) => ({
          ...message,
          isError: true,
          isFinal: true,
          content: knownMessageText(uiLanguage, "unexpected_error", t("requestFailed")),
        }));
        setStatusKey("requestFailed");
      }
    } catch (error) {
      if (!(error instanceof DOMException && error.name === "AbortError")) {
        setStatusKey("requestFailed");
      }
    } finally {
      controllerRef.current = null;
      requestIdRef.current = null;
      setActive(false);
      // conversationId is narrowed non-null by the early return above and
      // never reassigned again, so it is guaranteed to still be a string here.
      await loadPersistentDetail(conversationId);
      await loadPersistentList();
      // P4-CODEX-014: Best-effort Observability refresh — never awaited
      // into this function's own control flow, so a Status read failure
      // can never rewrite the Conversation Commit/canonical messages
      // reloaded just above. No-op when the Bootstrap tag is disabled.
      void loadRuntimeGovernanceStatus();
      void loadGuardrailGovernanceStatus();
      // Deliberately NOT clearing pinnedMessageId here: the reload above
      // swaps in canonical turn-id-based message ids, so the pinned
      // (locally-generated) id from the live send no longer matches
      // anything in the new DOM. MessageList's scrollIntoView call for it
      // becomes a silent no-op, which is exactly what keeps the view resting
      // at its last (pinned-near-top) position after the turn completes
      // instead of jumping to the bottom. The stale id is harmless afterward
      // — it only gets read again on the next messages update, by which
      // point a new send/selection has already overwritten or cleared it.
    }
  }

  async function persistentDerivedAction(turnId: string, kind: "retry" | "regenerate"): Promise<void> {
    if (active || selectedConversationId === null || persistentRevisionRef.current === null) {
      return;
    }
    // A derived turn reuses an earlier user message rather than sending a new
    // one, so there is no fresh id to pin — fall back to the default
    // scroll-to-bottom behavior instead of re-pinning a stale one.
    setPinnedMessageId(null);
    const assistantId = nextMessageId();
    setMessages((previous) => [...previous, emptyMessage("assistant", "", assistantId)]);
    controllerRef.current = new AbortController();
    setActive(true);
    try {
      const response = await api.startPersistentDerivedStream(
        selectedConversationId,
        turnId,
        kind,
        settingsPayload(),
        api.newActionId(),
        persistentRevisionRef.current,
        controllerRef.current.signal,
      );
      if (!response.ok) {
        await handlePersistentFailure(response);
        return;
      }
      await readEventStream(
        response,
        (event) => {
          handlePersistentEvent(event, assistantId);
        },
        t("streamUnavailable"),
      );
    } finally {
      controllerRef.current = null;
      requestIdRef.current = null;
      setActive(false);
      // selectedConversationId is narrowed non-null by the early return
      // above; this closure's snapshot of it cannot change mid-function.
      await loadPersistentDetail(selectedConversationId);
      await loadPersistentList();
      // P4-CODEX-014: Best-effort Observability refresh for Derived Turn
      // (retry/regenerate) Terminal too — see sendEphemeralMessage's own
      // comment on why this can never affect the Conversation Result.
      void loadRuntimeGovernanceStatus();
      void loadGuardrailGovernanceStatus();
    }
  }

  async function persistentMutationAction(path: string): Promise<void> {
    if (selectedConversationId === null || persistentRevisionRef.current === null) {
      return;
    }
    const response = await api.persistentMutation(path, api.newActionId(), persistentRevisionRef.current);
    if (!response.ok) {
      await handlePersistentFailure(response);
      return;
    }
    const result = (await response.json()) as { detail: PersistentConversationDetail };
    persistentRevisionRef.current = result.detail.storage_revision;
    setMessages(detailToMessages(result.detail, uiLanguage));
    await loadPersistentList();
  }

  // Sidebar list items act on whichever conversation the user clicked, which
  // is usually NOT the currently-selected one. persistentRevisionRef only
  // tracks the selected conversation's revision, so a non-selected target's
  // real revision has to be fetched first — each conversation has its own
  // independent revision counter, and mutating with the wrong one would
  // fail as a revision conflict every time.
  async function chatListItemAction(conversationId: string, action: ChatListAction): Promise<void> {
    try {
      const revision =
        conversationId === selectedConversationId && persistentRevisionRef.current !== null
          ? persistentRevisionRef.current
          : (await api.fetchPersistentDetail(conversationId)).storage_revision;
      const path = `/api/v2/conversations/${encodeURIComponent(conversationId)}/${action}`;
      const response = await api.persistentMutation(path, api.newActionId(), revision);
      if (!response.ok) {
        await handlePersistentFailure(response);
        return;
      }
      const result = (await response.json()) as { detail: PersistentConversationDetail };
      if (conversationId === selectedConversationId) {
        if (action === "delete") {
          // The conversation just vanished from the sidebar list — showing its
          // stale messages as if still selected would be misleading, and any
          // further mutation against it would fail as an invalid lifecycle.
          setSelectedConversationId(null);
          persistentRevisionRef.current = null;
          setMessages([]);
        } else {
          persistentRevisionRef.current = result.detail.storage_revision;
          setMessages(detailToMessages(result.detail, uiLanguage));
        }
      }
      await loadPersistentList();
    } catch {
      setStatusKey("requestFailed");
    }
  }

  // --- P8-B: Archived Chats (Data Controls) ---

  async function loadArchivedChats(): Promise<void> {
    setArchivedChatsState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const page = await api.fetchArchivedPersistentList();
      setArchivedChatsState({ capability: "ready", items: page.items, resultText: "" });
    } catch {
      setArchivedChatsState({ capability: "failed", items: [], resultText: "" });
    }
  }

  // P8-MR3 (P8-MANUAL-003): resets back to the Lazy "idle" default rather
  // than merely hiding the list — the next "Show" (whether from this
  // Button or after a Settings Reopen, see the `onClose` wiring below)
  // always issues a fresh `fetchArchivedPersistentList()` call, so a
  // Chat archived/unarchived elsewhere can never be seen as stale data.
  function closeArchivedChats(): void {
    setArchivedChatsState({ capability: "idle", items: [], resultText: "" });
  }

  async function openArchivedChat(conversationId: string): Promise<void> {
    setSettingsModalOpen(false);
    closeArchivedChats();
    await selectPersistentConversation(conversationId);
  }

  async function unarchiveArchivedChat(conversationId: string): Promise<void> {
    await chatListItemAction(conversationId, "unarchive");
    // The item just left the Archived set — drop it from this list's own
    // State directly rather than re-fetching, the same optimistic-update
    // shape `chatListItemAction` itself already applies to the Sidebar list.
    setArchivedChatsState((previous) => ({
      ...previous,
      items: previous.items.filter((item) => item.conversation_id !== conversationId),
    }));
  }

  async function chatListItemRename(conversationId: string, title: string): Promise<void> {
    try {
      const revision =
        conversationId === selectedConversationId && persistentRevisionRef.current !== null
          ? persistentRevisionRef.current
          : (await api.fetchPersistentDetail(conversationId)).storage_revision;
      const response = await api.renamePersistentConversation(
        conversationId,
        title,
        api.newActionId(),
        revision,
      );
      if (!response.ok) {
        await handlePersistentFailure(response);
        return;
      }
      const result = (await response.json()) as { detail: PersistentConversationDetail };
      if (conversationId === selectedConversationId) {
        persistentRevisionRef.current = result.detail.storage_revision;
      }
      await loadPersistentList();
    } catch {
      setStatusKey("requestFailed");
    }
  }

  function handleTurnAction(turnId: string, kind: "retry" | "regenerate" | "selectBranch"): void {
    if (kind === "selectBranch") {
      if (selectedConversationId === null) return;
      void persistentMutationAction(
        `/api/v2/conversations/${encodeURIComponent(selectedConversationId)}/branches/${encodeURIComponent(turnId)}/select`,
      );
      return;
    }
    void persistentDerivedAction(turnId, kind);
  }

  async function stopGeneration(): Promise<void> {
    if (!active) return;
    if (persistentEnabled) {
      if (requestIdRef.current === null || selectedConversationId === null || persistentRevisionRef.current === null) {
        controllerRef.current?.abort();
        return;
      }
      try {
        const response = await api.stopPersistentGeneration(
          selectedConversationId,
          requestIdRef.current,
          persistentRevisionRef.current,
        );
        if (!response.ok) {
          await handlePersistentFailure(response);
        }
      } catch {
        setStatusKey("stopRequestFailed");
      }
      return;
    }
    if (requestIdRef.current !== null) {
      try {
        await api.stopChat(requestIdRef.current);
      } catch {
        setStatusKey("stopRequestFailed");
      }
    }
    controllerRef.current?.abort();
  }

  async function newChat(): Promise<void> {
    await stopGeneration();
    if (conversationMode === "persistent") {
      await createPersistentConversationAndSelect();
      return;
    }
    if (conversationMode !== "ephemeral") {
      setStatusKey(conversationMode === "capability_pending" ? "persistentCapabilityPending" : "persistentCapabilityFailed");
      return;
    }
    setMessages([]);
    chatHistoryRef.current = [];
    terminalWarningRef.current = null;
    setContextUsage(null);
    setPinnedMessageId(null);
    setStatusKey("idle");
  }

  function sendMessage(): void {
    if (active) return;
    if (conversationMode === "persistent") {
      void sendPersistentMessage();
      return;
    }
    if (conversationMode !== "ephemeral") {
      setStatusKey(conversationMode === "capability_pending" ? "persistentCapabilityPending" : "persistentCapabilityFailed");
      return;
    }
    void sendEphemeralMessage();
  }

  const conversationReady = ["persistent", "ephemeral"].includes(conversationMode);
  const emptyTitleKey: TranslationKey =
    conversationMode === "persistent"
      ? "persistentEmptyTitle"
      : conversationMode === "ephemeral"
        ? "resetEmptyTitle"
        : "capabilityEmptyTitle";
  const emptyNoteKey: TranslationKey =
    conversationMode === "persistent"
      ? "persistentEmptyNote"
      : conversationMode === "ephemeral"
        ? "resetEmptyNote"
        : "capabilityEmptyNote";

  const documentationRagDenied = documentationRagEffectiveState === "denied";
  const documentationRagNoteText = documentationRagControlAvailable
    ? t("documentationRagNote")
    : t("documentationRagUnavailable");
  const currentRuntimeModel = runtimeModelControlState.status;
  // The live Current Model/Active pair below must not drop
  // the static Profile/Device/Acceleration info the Bootstrap Runtime
  // Snapshot already carries in `runtimeStatus.text` (its own first
  // segment there is the Bootstrap-time model_key, superseded here by the
  // Live one, so only the trailing segments are reused).
  const bootstrapEnvironment =
    runtimeStatus.kind === "metadata" && runtimeStatus.text !== null
      ? runtimeStatus.text.split(" · ").slice(1)
      : [];
  const sidebarRuntimeStatus =
    currentRuntimeModel?.enabled === true && currentRuntimeModel.main_model !== null
      ? {
          kind: "metadata" as const,
          text: [
            `${currentRuntimeModel.main_model.model_key} ${currentRuntimeModel.main_model.state}`,
            ...bootstrapEnvironment,
          ].join(" · "),
        }
      : runtimeStatus;

  return (
    <div className="app-shell" data-sidebar-visible={sidebarVisible}>
      <SidebarToggleButton
        language={uiLanguage}
        visible={sidebarVisible}
        onToggle={() => {
          setSidebarVisible((previous) => !previous);
        }}
      />
      <Sidebar
        language={uiLanguage}
        visible={sidebarVisible}
        runtimeStatus={sidebarRuntimeStatus}
        conversations={persistentEnabled ? persistentConversations : []}
        selectedConversationId={selectedConversationId}
        onSelectConversation={(id) => void selectPersistentConversation(id)}
        onConversationAction={(id, action) => void chatListItemAction(id, action)}
        onConversationRename={(id, title) => void chatListItemRename(id, title)}
        onNewChat={() => void newChat()}
        newChatDisabled={active || !conversationReady}
        onOpenSettings={() => {
          setSettingsModalOpen(true);
        }}
      />
      <main className="main-content">
        <TopBar
          language={uiLanguage}
          theme={uiTheme}
          onLanguageChange={setUiLanguage}
          onThemeChange={setUiTheme}
        />

        <MessageList
          language={uiLanguage}
          messages={messages}
          emptyTitleKey={emptyTitleKey}
          emptyNoteKey={emptyNoteKey}
          onTurnAction={handleTurnAction}
          pinnedMessageId={pinnedMessageId}
          active={active}
          liveJudgeBadge={liveJudgeBadge}
          branchUiVisible={branchUiVisibility === "shown"}
        />

        <Composer
          language={uiLanguage}
          value={prompt}
          onChange={setPrompt}
          onSend={sendMessage}
          onStop={() => void stopGeneration()}
          sendDisabled={active || !conversationReady}
          stopDisabled={!active}
          statusText={statusText}
          contextUsage={contextUsage}
          showContextUsage={settingsForm.showContextUsage}
          webEvidenceEnabled={webSearchBootstrapEnabled && settingsForm.webSearchMode === "manual"}
          webEvidenceUrl={manualWebEvidenceUrl}
          onWebEvidenceUrlChange={setManualWebEvidenceUrl}
        />
      </main>

      <SettingsModal
        language={uiLanguage}
        open={settingsModalOpen}
        onClose={() => {
          setSettingsModalOpen(false);
          // P8-MR3 (P8-MANUAL-003): Settings Close must never leave a
          // stale `ready` Archived Chats list behind — the next Reopen
          // always starts from the Lazy "idle" default again.
          closeArchivedChats();
        }}
        settingsForm={settingsForm}
        onSettingsChange={setSettingsForm}
        thinkingControlAvailable={thinkingControlAvailable}
        active={active}
        documentationRagControlAvailable={documentationRagControlAvailable}
        documentationRagDenied={documentationRagDenied}
        documentationRagNoteText={documentationRagNoteText}
        configurationBootstrapEnabled={configurationBootstrapEnabled}
        configurationState={configurationState}
        onConfigurationRefresh={() => void loadConfigurationControl()}
        onConfigurationApply={handleConfigurationApply}
        governanceBootstrapEnabled={governanceBootstrapEnabled}
        governanceState={governanceState}
        onGovernanceRefresh={() => void loadGovernanceStatus()}
        onGovernanceApply={handleGovernanceApply}
        runtimeGovernanceBootstrapEnabled={runtimeGovernanceBootstrapEnabled}
        runtimeGovernanceState={runtimeGovernanceState}
        onRuntimeGovernanceRefresh={() => void loadRuntimeGovernanceStatus()}
        onRuntimeGovernanceApply={handleRuntimeGovernanceApply}
        guardrailGovernanceBootstrapEnabled={guardrailGovernanceBootstrapEnabled}
        guardrailGovernanceState={guardrailGovernanceState}
        onGuardrailGovernanceRefresh={() => void loadGuardrailGovernanceStatus()}
        onGuardrailGovernanceApply={handleGuardrailGovernanceApply}
        runtimeModelControlBootstrapEnabled={runtimeModelControlBootstrapEnabled}
        runtimeModelControlState={runtimeModelControlState}
        onRuntimeModelRefresh={() => void loadRuntimeModelStatus(true)}
        onRuntimeModelStatusChange={acceptRuntimeModelStatus}
        localCorpusBootstrapEnabled={localCorpusBootstrapEnabled}
        localCorpusState={localCorpusState}
        onLocalCorpusRefresh={() => void loadLocalCorpus()}
        onLocalCorpusRegister={handleLocalCorpusRegister}
        onLocalCorpusUpdate={handleLocalCorpusUpdate}
        onLocalCorpusDelete={handleLocalCorpusDelete}
        onLocalCorpusEditRequest={handleLocalCorpusEditRequest}
        webSearchBootstrapEnabled={webSearchBootstrapEnabled}
        webSearchToggleEnabled={settingsForm.webSearchMode === "manual"}
        webSearchState={webSearchState}
        onWebSearch={handleWebSearch}
        onWebSearchDirectUrl={handleFetchDirectUrl}
        dataControlsBootstrapEnabled={dataControlsBootstrapEnabled}
        dataControlsState={dataControlsState}
        onDataControlsRefresh={() => void loadDataControls()}
        onDataControlsToggle={handleDataControlsToggle}
        onDataControlsReset={handleDataControlsReset}
        archivedChatsAvailable={conversationMode === "persistent"}
        archivedChatsState={archivedChatsState}
        onArchivedChatsLoad={() => void loadArchivedChats()}
        onArchivedChatsClose={closeArchivedChats}
        onArchivedChatsOpen={(id) => void openArchivedChat(id)}
        onArchivedChatsUnarchive={(id) => void unarchiveArchivedChat(id)}
      />
    </div>
  );
}
