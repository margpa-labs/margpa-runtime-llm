import { useCallback, useEffect, useRef, useState } from "react";
import { translate, knownServerMessages, type TranslationKey } from "./i18n/translations";
import { usePreference } from "./hooks/usePreference";
import { readConfigurationBootstrap } from "./lib/configurationBootstrap";
import { readEventStream } from "./lib/eventStream";
import * as api from "./api/client";
import type {
  ChatMessage,
  CitationEvidence,
  ContextUsage,
  ConversationMode,
  DisplayMessage,
  GenerationSettings,
  PersistentConversationDetail,
  PersistentTurn,
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
import MessageList from "./components/MessageList";
import Composer from "./components/Composer";
import type { SettingsFormState } from "./components/SettingsPanel";

const UI_LANGUAGE_KEY = "margpa.ui_language.v1";
const UI_THEME_KEY = "margpa.ui_theme.v1";

type Status =
  | { kind: "key"; key: TranslationKey; values?: Record<string, string | number> }
  | { kind: "serverWarning"; code: string; fallback: string };

function translatedServerMessage(language: UiLanguage, code: string, fallback: string): string {
  const key = knownServerMessages[code];
  return key === undefined ? fallback || translate(language, "genericError") : translate(language, key);
}

function knownMessageText(language: UiLanguage, code: string | null, fallback: string): string {
  if (code !== null) {
    const key = knownServerMessages[code];
    if (key !== undefined) {
      return translate(language, key);
    }
  }
  return fallback || translate(language, "genericError");
}

function emptyMessage(role: "user" | "assistant", content: string, id: string): DisplayMessage {
  return {
    id,
    role,
    content,
    isFinal: role === "user",
    isError: false,
    isIncomplete: false,
    errorCode: null,
    errorMessage: null,
    thinkingText: "",
    thinkingVisible: false,
    citations: null,
    turnActions: [],
  };
}

function detailToMessages(detail: PersistentConversationDetail): DisplayMessage[] {
  const out: DisplayMessage[] = [];
  for (const turn of detail.turns) {
    const user = turn.messages.find((message) => message.role === "user");
    const assistant = turn.messages.find((message) => message.role === "assistant");
    if (user !== undefined) {
      out.push(emptyMessage("user", user.content, `${turn.turn_id}-user`));
    }
    if (assistant !== undefined) {
      const turnActions = buildTurnActions(turn, detail);
      out.push({
        ...emptyMessage("assistant", assistant.content, `${turn.turn_id}-assistant`),
        isFinal: true,
        citations:
          turn.citations?.available === true
            ? { citations: turn.citations.citations, warnings: [] }
            : null,
        turnActions,
      });
    } else {
      // A turn without a completed assistant message (failed/cancelled/interrupted
      // before any content) still needs somewhere to host retry/regenerate actions.
      const turnActions = buildTurnActions(turn, detail);
      if (turnActions.length > 0) {
        const last = out.at(-1);
        if (last !== undefined) {
          last.turnActions = turnActions;
        }
      }
    }
  }
  return out;
}

function buildTurnActions(
  turn: PersistentTurn,
  detail: PersistentConversationDetail,
): DisplayMessage["turnActions"] {
  // Order matches the display row's left-to-right layout (right-aligned,
  // Copy always last/rightmost): branch-select, then regenerate.
  const actions: DisplayMessage["turnActions"] = [];
  if (["failed", "cancelled", "interrupted"].includes(turn.state)) {
    actions.push({ kind: "retry", turnId: turn.turn_id });
  }
  if (turn.state === "completed") {
    if (turn.turn_id !== detail.head_turn_id) {
      actions.push({ kind: "selectBranch", turnId: turn.turn_id });
    }
    actions.push({ kind: "regenerate", turnId: turn.turn_id });
  }
  return actions;
}

export default function App() {
  const [uiLanguage, setUiLanguage] = usePreference<UiLanguage>(UI_LANGUAGE_KEY, ["ja", "en"], "ja");
  const [uiTheme, setUiTheme] = usePreference<UiTheme>(UI_THEME_KEY, ["white", "dark"], "white");
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

  const [prompt, setPrompt] = useState("");
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

  // Non-rendering imperative bookkeeping (mirrors the plain-object mutation
  // semantics of the original vanilla state object for fields that never
  // drive rendering on their own).
  const controllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef<string | null>(null);
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

  function settingsPayload(): GenerationSettings {
    return {
      response_language: settingsForm.responseLanguage,
      max_new_tokens: Number(settingsForm.maxNewTokens),
      thinking_mode: settingsForm.thinkingMode ? "enabled" : "disabled",
      thinking_visibility: settingsForm.thinkingVisibility ? "visible" : "hidden",
      summary_mode: settingsForm.summaryMode,
      documentation_rag_mode: settingsForm.documentationRagMode,
      context_usage_prompt_injection_mode: settingsForm.injectContextUsage ? "enabled" : "disabled",
      expressive_mode: settingsForm.expressiveMode ? "enabled" : "disabled",
    };
  }

  function updateMessageById(id: string, updater: (message: DisplayMessage) => DisplayMessage): void {
    setMessages((previous) => previous.map((message) => (message.id === id ? updater(message) : message)));
  }

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
          text: [runtime.model_key, runtime.profile_key, runtime.device_kind, runtime.acceleration_api].join(
            " · ",
          ),
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

  // --- Configuration Control ---
  const loadConfigurationControl = useCallback(async (): Promise<void> => {
    if (!configurationBootstrapEnabled) {
      return;
    }
    setConfigurationState((previous) => ({ ...previous, capability: "loading" }));
    try {
      const runtime = await api.fetchConfigurationRuntime();
      if (!runtime.enabled || !runtime.non_persistent) {
        throw new Error("configuration_runtime_invalid");
      }
      const snapshot = await api.fetchConfigurationEffective();
      setConfigurationState({ capability: "ready", snapshot, resultText: "" });
    } catch {
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

  async function handleConfigurationPreview(patch: Record<string, unknown>): Promise<void> {
    if (configurationState.capability !== "ready") {
      return;
    }
    try {
      const preview = await api.previewConfigurationPatch(patch);
      const message =
        preview.outcome === "restart_required" ? t("configurationRestartRequired") : t("configurationPreviewReady");
      setConfigurationState((previous) => ({
        ...previous,
        resultText: `${message}\n${JSON.stringify(preview.redacted_changes, null, 2)}`,
      }));
    } catch {
      setConfigurationState((previous) => ({ ...previous, resultText: t("configurationFailed") }));
    }
  }

  async function handleConfigurationApply(researchDeveloperMode: string): Promise<void> {
    const snapshot = configurationState.snapshot;
    if (configurationState.capability !== "ready" || snapshot === null) {
      return;
    }
    try {
      const response = await api.applyConfigurationPatch(
        api.newActionId(),
        snapshot.revision,
        snapshot.digest_sha512,
        { research_developer_mode: researchDeveloperMode },
      );
      if (response.status === 409) {
        setConfigurationState((previous) => ({ ...previous, resultText: t("configurationConflict") }));
        await loadConfigurationControl();
        return;
      }
      if (!response.ok) {
        throw new Error("configuration_apply_failed");
      }
      await loadConfigurationControl();
      setConfigurationState((previous) => ({ ...previous, resultText: t("configurationApplied") }));
    } catch {
      setConfigurationState((previous) => ({ ...previous, resultText: t("configurationFailed") }));
    }
  }

  // --- Ephemeral (v1) streaming ---
  function handleEphemeralEvent(event: StreamEvent, assistantId: string): boolean {
    const data = event.data;
    if (event.type === "start") {
      requestIdRef.current = data.request_id ?? null;
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
    if (event.type === "status" && data.state === "summarizing_answer") {
      setStatusKey("summarizing");
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
    if (event.type === "error") {
      rollbackPendingUserIfLast();
      updateMessageById(assistantId, (message) => ({
        ...message,
        isError: true,
        isFinal: true,
        content: knownMessageText(uiLanguage, data.code ?? null, data.message ?? ""),
      }));
      setStatusKey("errorStatus", { code: data.code ?? "unknown" });
      return false;
    }
    return false;
  }

  async function sendEphemeralMessage(): Promise<void> {
    const content = prompt;
    if (!content.trim()) {
      setStatusKey("emptyMessage");
      return;
    }
    const maxNewTokens = Number(settingsForm.maxNewTokens);
    if (!Number.isInteger(maxNewTokens) || maxNewTokens < 1 || maxNewTokens > 2048) {
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
    controllerRef.current = new AbortController();
    requestIdRef.current = null;
    terminalWarningRef.current = null;
    setActive(true);
    setStatusKey("connecting");

    try {
      const response = await api.startChatStream(history, settingsPayload(), controllerRef.current.signal);
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
    setMessages(detailToMessages(detail));
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
      setMessages(detailToMessages(result.detail));
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
        setStatusKey("errorStatus", { code: event.data.code ?? "generation_failed" });
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
    if (!Number.isInteger(maxNewTokens) || maxNewTokens < 1 || maxNewTokens > 2048) {
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
        settingsPayload(),
        operationId,
        persistentRevisionRef.current,
        controllerRef.current.signal,
      );
      if (!response.ok) {
        await handlePersistentFailure(response);
        return;
      }
      setPrompt("");
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
    setMessages(detailToMessages(result.detail));
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
          setMessages(detailToMessages(result.detail));
        }
      }
      await loadPersistentList();
    } catch {
      setStatusKey("requestFailed");
    }
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
        runtimeStatus={runtimeStatus}
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
        />
      </main>

      <SettingsModal
        language={uiLanguage}
        open={settingsModalOpen}
        onClose={() => {
          setSettingsModalOpen(false);
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
        onConfigurationPreview={(patch) => void handleConfigurationPreview(patch)}
        onConfigurationApply={(mode) => void handleConfigurationApply(mode)}
      />
    </div>
  );
}
