"use strict";

import { renderSafeMarkdown } from "./safe_markdown.js";

const UI_LANGUAGE_KEY = "margpa.ui_language.v1";
const DEFAULT_UI_LANGUAGE = "ja";

const translations = {
  ja: {
    documentTitle: "Nazuna Research Governance LLM プレビュー",
    uiLanguageLabel: "表示言語",
    newChat: "新規Chat",
    previewLabel: "プレビュー利用上の注意",
    previewNote: "この画面はResearch Previewです。本番AccountまたはProduction Serviceではありません。",
    messagesLabel: "Chatメッセージ",
    emptyTitle: "一時的なChatを開始",
    emptyNote: "会話はこのBrowser TabのMemoryだけに保持され、Reloadで失われます。",
    resetEmptyTitle: "新しいChat",
    resetEmptyNote: "Browser Memoryを初期化しました。ModelはReloadされません。",
    composerLabel: "メッセージ入力",
    promptLabel: "メッセージ",
    promptPlaceholder: "メッセージを入力してください",
    idle: "待機中",
    stop: "停止",
    send: "送信",
    shortcutHint: "Cmd+Enter／Ctrl+Enterで送信",
    settingsLabel: "生成設定",
    settingsTitle: "設定",
    responseLanguageLabel: "回答言語",
    responseJa: "日本語（ja）",
    responseEn: "英語（en）",
    responseAuto: "自動（auto）",
    maxNewTokensLabel: "最大生成Token数",
    thinkingModeLabel: "推論生成",
    thinkingVisibilityLabel: "推論過程を表示",
    thinkingUnavailable: "このModelでは推論生成Controlを利用できません。",
    thinkingRegionLabel: "推論過程（保存・Copyされません）",
    summaryModeLabel: "要約モード",
    summaryOff: "OFF",
    summaryOn: "ON",
    summaryNote: "ONでは通常回答の完了後に同じModelで要約します。処理時間とToken使用量が増え、要約により詳細、前提、注意事項等が省略・変形される可能性があります。",
    documentationRagModeLabel: "プロジェクトDocs参照",
    documentationRagOff: "OFF",
    documentationRagOn: "ON",
    documentationRagNote: "ONではProject内の許可されたDocsを参照し、System由来の参照文書を回答と分離して表示します。",
    documentationRagUnavailable: "Project Docs参照はこのRuntimeでは利用できません。",
    retrievingDocumentation: "Project Docsを検索しています",
    citationsLabel: "参照文書",
    noCitations: "参照文書なし",
    copyPath: "Pathをコピー",
    docsMissing: "docsが設置されていないため参照出来ません。",
    documentationNoHit: "参照対象のDocsから対応する根拠を取得できませんでした。",
    documentationContextInsufficient: "根拠を取得しましたが、Context余力不足のため回答に使用できません。",
    documentationSubjectCoverageInsufficient: "質問対象の一部に必要なProject Docsの根拠が揃わないため、回答を停止しました。",
    documentationPromptMeasurementUnavailable: "ModelのChat Prompt Token数を安全に計測できないため、Project Docs参照を停止しました。",
    thinkingNote: "推論生成はLatency／Token使用量を増やす可能性があります。表示内容は正しさや真の内部思考を保証しません。Token上限により最終回答前に停止する場合があります。Raw Thinkingは永続保存しません。",
    copy: "コピー",
    copied: "コピーしました",
    copyFailed: "コピーできませんでした",
    markdownFallback: "Markdown表示に失敗したためPlain Textで表示しています。",
    streamProtocolError: "Streaming Responseの形式が正しくありません。",
    runtimeLoading: "Runtimeを確認しています…",
    runtimeLoadFailed: "Runtime情報を取得できませんでした。",
    connecting: "接続しています",
    generating: "回答を生成しています",
    summarizing: "回答を要約しています",
    completed: "完了 ({reason})",
    warning: "警告: {message}",
    stopped: "生成を停止しました",
    emptyMessage: "空のMessageは送信できません",
    invalidTokenLimit: "最大生成Token数は1〜2048の整数にしてください",
    streamUnavailable: "Streaming Responseを受信できませんでした。",
    requestFailed: "Requestに失敗しました。",
    stopRequestFailed: "停止Requestを送信できませんでした",
    genericError: "処理に失敗しました。",
    errorStatus: "Error: {code}",
    finalAnswerTokenLimit: "最終回答を生成する前にToken上限へ到達しました。",
    summaryFallbackOriginal: "要約を安全に完了できなかったため、元の回答を表示します。",
    invalidRequest: "Requestが正しくありません。",
    requestTooLarge: "Chat Requestが大きすぎます。",
    authenticationRequired: "Preview認証が必要です。",
    generationNotActive: "指定された生成は実行中ではありません。",
    modelBusy: "Modelは別のRequestを処理中です。",
    contextLimitExceeded: "入力がModelのContext上限を超えました。",
    generationFailed: "回答の生成に失敗しました。",
    unexpectedError: "予期しないErrorで処理に失敗しました。",
  },
  en: {
    documentTitle: "Nazuna Research Governance LLM Preview",
    uiLanguageLabel: "Interface language",
    newChat: "New Chat",
    previewLabel: "Preview access notice",
    previewNote: "This is a research preview, not a production account or service.",
    messagesLabel: "Chat messages",
    emptyTitle: "Start an ephemeral chat",
    emptyNote: "This conversation exists only in this browser tab's memory and is lost on reload.",
    resetEmptyTitle: "New Chat",
    resetEmptyNote: "Browser memory was cleared. The model was not reloaded.",
    composerLabel: "Message composer",
    promptLabel: "Message",
    promptPlaceholder: "Enter a message",
    idle: "Idle",
    stop: "Stop",
    send: "Send",
    shortcutHint: "Send with Cmd+Enter / Ctrl+Enter",
    settingsLabel: "Generation settings",
    settingsTitle: "Settings",
    responseLanguageLabel: "Response Language",
    responseJa: "Japanese (ja)",
    responseEn: "English (en)",
    responseAuto: "Auto (auto)",
    maxNewTokensLabel: "Max New Tokens",
    thinkingModeLabel: "Generate model reasoning",
    thinkingVisibilityLabel: "Show model reasoning output",
    thinkingUnavailable: "Reasoning generation control is unavailable for this model.",
    thinkingRegionLabel: "Model reasoning output (not stored or copied)",
    summaryModeLabel: "Summary Mode",
    summaryOff: "OFF",
    summaryOn: "ON",
    summaryNote: "When ON, the completed answer is summarized by the same model. This increases latency and token usage, and details, assumptions, or cautions may be omitted or altered by the summary.",
    documentationRagModeLabel: "Project Docs",
    documentationRagOff: "OFF",
    documentationRagOn: "ON",
    documentationRagNote: "When ON, the runtime searches allowed project documentation and shows system-derived citations separately from the answer.",
    documentationRagUnavailable: "Project Docs are unavailable in this runtime.",
    retrievingDocumentation: "Searching Project Docs",
    citationsLabel: "References",
    noCitations: "No reference documents",
    copyPath: "Copy path",
    docsMissing: "Project documentation is not installed and cannot be referenced.",
    documentationNoHit: "No supporting evidence was found in the available Project Docs.",
    documentationContextInsufficient: "Supporting documents were found, but the remaining context is insufficient to use them in an answer.",
    documentationSubjectCoverageInsufficient: "The answer was stopped because Project Docs evidence is missing for one or more requested subjects.",
    documentationPromptMeasurementUnavailable: "Project Docs were stopped because the model's chat prompt tokens could not be measured safely.",
    thinkingNote: "Reasoning generation may increase latency and token usage. Displayed reasoning does not guarantee correctness or reveal true internal thought. The token limit may be reached before a final answer. Raw thinking is never persisted.",
    copy: "Copy",
    copied: "Copied",
    copyFailed: "Could not copy",
    markdownFallback: "Markdown rendering failed, so the answer is shown as plain text.",
    streamProtocolError: "The streaming response has an invalid format.",
    runtimeLoading: "Checking runtime…",
    runtimeLoadFailed: "Could not load runtime information.",
    connecting: "Connecting",
    generating: "Generating answer",
    summarizing: "Summarizing answer",
    completed: "Completed ({reason})",
    warning: "Warning: {message}",
    stopped: "Generation stopped",
    emptyMessage: "A blank message cannot be sent",
    invalidTokenLimit: "Max New Tokens must be an integer from 1 to 2048",
    streamUnavailable: "The streaming response is unavailable.",
    requestFailed: "The request failed.",
    stopRequestFailed: "Could not send the stop request",
    genericError: "The operation failed.",
    errorStatus: "Error: {code}",
    finalAnswerTokenLimit: "The token limit was reached before a final answer was generated.",
    summaryFallbackOriginal: "The summary could not be completed safely, so the original answer is shown.",
    invalidRequest: "The request is invalid.",
    requestTooLarge: "The chat request is too large.",
    authenticationRequired: "Preview authentication is required.",
    generationNotActive: "The requested generation is not active.",
    modelBusy: "The model is processing another request.",
    contextLimitExceeded: "The input exceeds the model context limit.",
    generationFailed: "The answer could not be generated.",
    unexpectedError: "The operation failed unexpectedly.",
  },
};

const knownServerMessages = {
  final_answer_token_limit: "finalAnswerTokenLimit",
  summary_fallback_original: "summaryFallbackOriginal",
  invalid_request: "invalidRequest",
  request_too_large: "requestTooLarge",
  authentication_required: "authenticationRequired",
  generation_not_active: "generationNotActive",
  model_busy: "modelBusy",
  context_limit_exceeded: "contextLimitExceeded",
  generation_failed: "generationFailed",
  unsupported_capability: "thinkingUnavailable",
  documentation_docs_missing: "docsMissing",
  documentation_no_hit: "documentationNoHit",
  documentation_context_budget_insufficient: "documentationContextInsufficient",
  documentation_subject_coverage_insufficient: "documentationSubjectCoverageInsufficient",
  documentation_prompt_measurement_unavailable: "documentationPromptMeasurementUnavailable",
  documentation_corpus_empty: "documentationRagUnavailable",
  documentation_index_build_failed: "documentationRagUnavailable",
  unexpected_error: "unexpectedError",
};

const elements = {
  messages: document.querySelector("#messages"),
  emptyState: document.querySelector("#empty-state"),
  prompt: document.querySelector("#prompt"),
  send: document.querySelector("#send"),
  stop: document.querySelector("#stop"),
  newChat: document.querySelector("#new-chat"),
  generationStatus: document.querySelector("#generation-status"),
  runtimeStatus: document.querySelector("#runtime-status"),
  responseLanguage: document.querySelector("#response-language"),
  maxNewTokens: document.querySelector("#max-new-tokens"),
  thinkingMode: document.querySelector("#thinking-mode"),
  thinkingVisibility: document.querySelector("#thinking-visibility"),
  documentationRagControl: document.querySelector("#documentation-rag-control"),
  documentationRagNote: document.querySelector("#documentation-rag-note"),
  uiLanguageJa: document.querySelector("#ui-language-ja"),
  uiLanguageEn: document.querySelector("#ui-language-en"),
};

const state = {
  messages: [],
  controller: null,
  requestId: null,
  active: false,
  terminalWarning: null,
  thinkingControlAvailable: false,
  documentationRagControlAvailable: false,
  documentationRagEffectiveState: "unavailable",
  uiLanguage: readStoredUiLanguage(),
  status: { key: "idle", values: {} },
  runtimeStatus: { kind: "loading", translationKey: "runtimeLoading", text: null },
};

function readStoredUiLanguage() {
  try {
    const stored = localStorage.getItem(UI_LANGUAGE_KEY);
    return stored === "ja" || stored === "en" ? stored : DEFAULT_UI_LANGUAGE;
  } catch {
    return DEFAULT_UI_LANGUAGE;
  }
}

function t(key, values = {}) {
  let value = translations[state.uiLanguage][key] ?? translations[DEFAULT_UI_LANGUAGE][key] ?? key;
  for (const [name, replacement] of Object.entries(values)) {
    value = value.replaceAll(`{${name}}`, String(replacement));
  }
  return value;
}

function setText(selector, key) {
  const node = document.querySelector(selector);
  if (node !== null) {
    node.textContent = t(key);
  }
}

function renderStatus() {
  if (state.status.serverWarning !== undefined) {
    const message = translatedServerMessage(
      state.status.serverWarning.code,
      state.status.serverWarning.fallback,
    );
    elements.generationStatus.textContent = t("warning", { message });
    return;
  }
  elements.generationStatus.textContent = t(state.status.key, state.status.values);
}

function setStatus(key, values = {}) {
  state.status = { key, values };
  renderStatus();
}

function setWarningStatus(code, fallback) {
  state.status = { serverWarning: { code, fallback } };
  renderStatus();
}

function renderRuntimeStatus() {
  if (state.runtimeStatus.kind === "metadata") {
    elements.runtimeStatus.textContent = state.runtimeStatus.text;
    return;
  }
  elements.runtimeStatus.textContent = t(state.runtimeStatus.translationKey);
}

function applyTranslations() {
  document.documentElement.lang = state.uiLanguage;
  document.title = t("documentTitle");
  document.querySelector("#ui-language-switcher").setAttribute("aria-label", t("uiLanguageLabel"));
  document.querySelector("#preview-note").setAttribute("aria-label", t("previewLabel"));
  elements.messages.setAttribute("aria-label", t("messagesLabel"));
  document.querySelector("#composer").setAttribute("aria-label", t("composerLabel"));
  document.querySelector("#settings").setAttribute("aria-label", t("settingsLabel"));
  elements.prompt.setAttribute("placeholder", t("promptPlaceholder"));
  elements.uiLanguageJa.setAttribute("aria-pressed", String(state.uiLanguage === "ja"));
  elements.uiLanguageEn.setAttribute("aria-pressed", String(state.uiLanguage === "en"));

  const bindings = {
    "#new-chat": "newChat",
    "#preview-note": "previewNote",
    "#empty-title": "emptyTitle",
    "#empty-note": "emptyNote",
    "#prompt-label": "promptLabel",
    "#shortcut-hint": "shortcutHint",
    "#stop": "stop",
    "#send": "send",
    "#settings-title": "settingsTitle",
    "#response-language-label": "responseLanguageLabel",
    "#response-language-ja": "responseJa",
    "#response-language-en": "responseEn",
    "#response-language-auto": "responseAuto",
    "#max-new-tokens-label": "maxNewTokensLabel",
    "#thinking-mode-label": "thinkingModeLabel",
    "#thinking-visibility-label": "thinkingVisibilityLabel",
    "#summary-mode-label": "summaryModeLabel",
    "#summary-mode-off": "summaryOff",
    "#summary-mode-on": "summaryOn",
    "#summary-note": "summaryNote",
    "#documentation-rag-mode-label": "documentationRagModeLabel",
    "#documentation-rag-mode-off": "documentationRagOff",
    "#documentation-rag-mode-on": "documentationRagOn",
    "#thinking-note": "thinkingNote",
  };
  for (const [selector, key] of Object.entries(bindings)) {
    setText(selector, key);
  }
  document.querySelectorAll("[data-i18n-message]").forEach((node) => {
    node.textContent = t(node.dataset.i18nMessage);
  });
  elements.thinkingMode.title = state.thinkingControlAvailable ? "" : t("thinkingUnavailable");
  elements.documentationRagControl.title = state.documentationRagControlAvailable
    ? ""
    : t("documentationRagUnavailable");
  syncDocumentationRagControls();
  renderRuntimeStatus();
  renderStatus();
}

function setUiLanguage(language) {
  state.uiLanguage = language === "en" ? "en" : DEFAULT_UI_LANGUAGE;
  try {
    localStorage.setItem(UI_LANGUAGE_KEY, state.uiLanguage);
  } catch {
    // Browser storage may be disabled; the in-memory language still works.
  }
  applyTranslations();
}

function setActive(active) {
  state.active = active;
  elements.send.disabled = active;
  elements.stop.disabled = !active;
  elements.prompt.disabled = active;
  syncThinkingControls();
  syncDocumentationRagControls();
}

function syncDocumentationRagControls() {
  const denied = state.documentationRagEffectiveState === "denied";
  elements.documentationRagControl.hidden = denied;
  elements.documentationRagNote.hidden = denied;
  const inputs = elements.documentationRagControl.querySelectorAll("input");
  for (const input of inputs) {
    input.disabled = state.active || !state.documentationRagControlAvailable;
  }
  if (!state.documentationRagControlAvailable) {
    const off = elements.documentationRagControl.querySelector('input[value="disabled"]');
    if (off !== null) {
      off.checked = true;
    }
    elements.documentationRagNote.textContent = t("documentationRagUnavailable");
  } else {
    elements.documentationRagNote.textContent = t("documentationRagNote");
  }
}

function syncThinkingControls() {
  const generationAvailable = state.thinkingControlAvailable && !state.active;
  elements.thinkingMode.disabled = !generationAvailable;
  if (!generationAvailable && !state.thinkingControlAvailable) {
    elements.thinkingMode.checked = false;
  }
  const generationEnabled = state.thinkingControlAvailable && elements.thinkingMode.checked;
  elements.thinkingVisibility.disabled = state.active || !generationEnabled;
  if (!generationEnabled) {
    elements.thinkingVisibility.checked = false;
  }
}

function createMessageContainer(role, extraClass = "") {
  if (elements.emptyState !== null) {
    elements.emptyState.remove();
    elements.emptyState = null;
  }
  const node = document.createElement("div");
  node.className = `message message-${role}${extraClass ? ` ${extraClass}` : ""}`;
  elements.messages.append(node);
  return node;
}

function createCopyButton(canonicalText, translationKey = "copy") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "message-copy secondary";
  button.dataset.i18nMessage = translationKey;
  button.textContent = t(translationKey);
  button.addEventListener("click", async () => {
    let feedback = "copyFailed";
    try {
      if (navigator.clipboard === undefined) {
        throw new Error("clipboard_unavailable");
      }
      await navigator.clipboard.writeText(canonicalText);
      feedback = "copied";
    } catch {
      feedback = "copyFailed";
    }
    button.dataset.i18nMessage = feedback;
    button.textContent = t(feedback);
    window.setTimeout(() => {
      button.dataset.i18nMessage = translationKey;
      button.textContent = t(translationKey);
    }, 1600);
  });
  return button;
}

function appendUserMessage(text) {
  const container = createMessageContainer("user");
  const content = document.createElement("div");
  content.className = "message-content";
  content.textContent = text;
  const actions = document.createElement("div");
  actions.className = "message-actions";
  actions.append(createCopyButton(text));
  container.append(content, actions);
  scrollMessages();
  return container;
}

function appendAssistantMessage() {
  const container = createMessageContainer("assistant");
  const thinking = document.createElement("section");
  thinking.className = "message-thinking";
  thinking.hidden = true;
  const thinkingLabel = document.createElement("div");
  thinkingLabel.className = "message-thinking-label";
  thinkingLabel.dataset.i18nMessage = "thinkingRegionLabel";
  thinkingLabel.textContent = t("thinkingRegionLabel");
  const thinkingContent = document.createElement("div");
  thinkingContent.className = "message-thinking-content";
  thinking.append(thinkingLabel, thinkingContent);

  const finalContent = document.createElement("div");
  finalContent.className = "message-content message-final";
  const actions = document.createElement("div");
  actions.className = "message-actions";
  const citations = document.createElement("section");
  citations.className = "message-citations";
  citations.hidden = true;
  const citationsLabel = document.createElement("div");
  citationsLabel.className = "message-citations-label";
  citationsLabel.dataset.i18nMessage = "citationsLabel";
  citationsLabel.textContent = t("citationsLabel");
  const citationsList = document.createElement("div");
  citationsList.className = "message-citations-list";
  citations.append(citationsLabel, citationsList);
  container.append(thinking, finalContent, citations, actions);
  scrollMessages();
  return {
    container,
    thinking,
    thinkingContent,
    finalContent,
    citations,
    citationsList,
    actions,
  };
}

function renderCitations(assistantView, data) {
  const citations = Array.isArray(data.citations) ? data.citations : [];
  assistantView.citations.hidden = false;
  assistantView.citationsList.replaceChildren();
  if (citations.length === 0) {
    const empty = document.createElement("div");
    empty.className = "message-citation-empty";
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    const reason = warnings.find((warning) => knownServerMessages[warning.code] !== undefined);
    if (reason === undefined) {
      empty.dataset.i18nMessage = "noCitations";
      empty.textContent = t("noCitations");
    } else {
      setKnownNodeMessage(empty, reason.code, reason.message);
    }
    assistantView.citationsList.append(empty);
    return;
  }
  for (const citation of citations) {
    const item = document.createElement("div");
    item.className = "message-citation";
    const path = document.createElement("code");
    path.textContent = citation.project_relative_path;
    const heading = document.createElement("span");
    heading.textContent = citation.heading_breadcrumb || "";
    const copy = createCopyButton(citation.project_relative_path, "copyPath");
    item.append(path, heading, copy);
    assistantView.citationsList.append(item);
  }
}

function scrollMessages() {
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function renderCompletedMarkdown(node, canonical) {
  try {
    const rendered = renderSafeMarkdown(canonical);
    node.replaceChildren(rendered);
    node.classList.add("message-markdown");
    return true;
  } catch {
    node.textContent = canonical;
    node.classList.remove("message-markdown");
    return false;
  }
}

function setKnownNodeMessage(node, code, fallback) {
  const key = knownServerMessages[code];
  if (key !== undefined) {
    node.dataset.i18nMessage = key;
    node.textContent = t(key);
    return t(key);
  }
  delete node.dataset.i18nMessage;
  node.textContent = fallback || t("genericError");
  return node.textContent;
}

function translatedServerMessage(code, fallback) {
  const key = knownServerMessages[code];
  return key === undefined ? fallback || t("genericError") : t(key);
}

function rollbackPendingUser() {
  const last = state.messages.at(-1);
  if (last?.role === "user") {
    state.messages.pop();
  }
}

function settingsPayload() {
  const summaryMode = document.querySelector('input[name="summary-mode"]:checked');
  const documentationRagMode = document.querySelector(
    'input[name="documentation-rag-mode"]:checked',
  );
  return {
    response_language: elements.responseLanguage.value,
    max_new_tokens: Number(elements.maxNewTokens.value),
    thinking_mode: elements.thinkingMode.checked ? "enabled" : "disabled",
    thinking_visibility: elements.thinkingVisibility.checked ? "visible" : "hidden",
    summary_mode: summaryMode?.value ?? "off",
    documentation_rag_mode: documentationRagMode?.value ?? "disabled",
  };
}

async function loadRuntime() {
  try {
    const response = await fetch("/api/v1/runtime", { cache: "no-store" });
    if (!response.ok) {
      throw new Error("runtime_load_failed");
    }
    const runtime = await response.json();
    state.runtimeStatus = {
      kind: "metadata",
      translationKey: null,
      text: [
        runtime.model_key,
        runtime.profile_key,
        runtime.device_kind,
        runtime.acceleration_api,
      ].join(" · "),
    };
    renderRuntimeStatus();
    elements.responseLanguage.value = runtime.defaults.response_language;
    elements.maxNewTokens.value = String(runtime.defaults.max_new_tokens);
    state.thinkingControlAvailable = runtime.defaults.thinking_control_available === true;
    elements.thinkingMode.checked = (
      state.thinkingControlAvailable && runtime.defaults.thinking_mode === "enabled"
    );
    elements.thinkingVisibility.checked = runtime.defaults.thinking_visibility === "visible";
    syncThinkingControls();
    const summaryMode = document.querySelector(
      `input[name="summary-mode"][value="${runtime.defaults.summary_mode}"]`,
    );
    if (summaryMode !== null) {
      summaryMode.checked = true;
    }
    const documentationRuntime = runtime.documentation_rag ?? {};
    state.documentationRagEffectiveState =
      documentationRuntime.effective_state ?? "unavailable";
    state.documentationRagControlAvailable =
      documentationRuntime.control_available === true;
    const documentationMode = document.querySelector(
      `input[name="documentation-rag-mode"][value="${
        documentationRuntime.default_mode ?? "disabled"
      }"]`,
    );
    if (documentationMode !== null) {
      documentationMode.checked = true;
    }
    syncDocumentationRagControls();
  } catch {
    state.thinkingControlAvailable = false;
    syncThinkingControls();
    state.documentationRagControlAvailable = false;
    state.documentationRagEffectiveState = "unavailable";
    syncDocumentationRagControls();
    state.runtimeStatus = {
      kind: "known_error",
      translationKey: "runtimeLoadFailed",
      text: null,
    };
    renderRuntimeStatus();
  }
}

function parseEventBlock(block) {
  let eventType = "message";
  const dataLines = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      eventType = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trimStart());
    }
  }
  if (dataLines.length === 0) {
    return null;
  }
  return { type: eventType, data: JSON.parse(dataLines.join("\n")) };
}

async function readEventStream(response, assistantNode) {
  if (response.body === null) {
    throw new Error(t("streamUnavailable"));
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done }).replaceAll("\r\n", "\n");
    let boundary = buffer.indexOf("\n\n");
    while (boundary >= 0) {
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const event = parseEventBlock(block);
      if (event !== null) {
        handleEvent(event, assistantNode);
      }
      boundary = buffer.indexOf("\n\n");
    }
    if (done) {
      return;
    }
  }
}

function handleEvent(event, assistantView) {
  const data = event.data;
  if (event.type === "start") {
    state.requestId = data.request_id;
    state.terminalWarning = null;
    setStatus(
      data.state === "retrieving_documentation" ? "retrievingDocumentation" : "generating",
    );
    return;
  }
  if (event.type === "retrieval") {
    renderCitations(assistantView, data);
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    if (warnings.length > 0) {
      const warning = warnings.at(-1);
      state.terminalWarning = { code: warning.code, fallback: warning.message };
      setWarningStatus(warning.code, warning.message);
    } else {
      setStatus("generating");
    }
    return;
  }
  if (event.type === "status" && data.state === "summarizing_answer") {
    setStatus("summarizing");
    return;
  }
  if (event.type === "delta") {
    if (data.channel === "reasoning") {
      assistantView.thinking.hidden = false;
      assistantView.thinkingContent.textContent += data.text;
    } else if (data.channel === "final") {
      assistantView.finalContent.textContent += data.text;
    } else {
      const error = new Error(t("streamProtocolError"));
      error.code = "invalid_stream_channel";
      throw error;
    }
    scrollMessages();
    return;
  }
  if (event.type === "warning") {
    state.terminalWarning = { code: data.code, fallback: data.message };
    if (data.code === "final_answer_token_limit") {
      assistantView.container.classList.add("message-error");
      setKnownNodeMessage(assistantView.finalContent, data.code, data.message);
    }
    setWarningStatus(data.code, data.message);
    return;
  }
  if (event.type === "completed") {
    const canonical = data.assistant_message?.content ?? "";
    let markdownRendered = true;
    if (canonical.trim()) {
      state.messages.push({ role: "assistant", content: canonical });
      assistantView.finalContent.textContent = canonical;
      markdownRendered = renderCompletedMarkdown(assistantView.finalContent, canonical);
      assistantView.actions.replaceChildren(createCopyButton(canonical));
    } else {
      rollbackPendingUser();
      if (state.terminalWarning === null) {
        assistantView.container.remove();
      }
    }
    if (state.terminalWarning !== null) {
      setWarningStatus(state.terminalWarning.code, state.terminalWarning.fallback);
    } else if (!markdownRendered) {
      setStatus("markdownFallback");
    } else {
      setStatus("completed", { reason: data.finish_reason });
    }
    return;
  }
  if (event.type === "cancelled") {
    rollbackPendingUser();
    assistantView.container.classList.add("message-incomplete");
    setStatus("stopped");
    return;
  }
  if (event.type === "error") {
    rollbackPendingUser();
    assistantView.container.classList.add("message-error");
    setKnownNodeMessage(assistantView.finalContent, data.code, data.message);
    setStatus("errorStatus", { code: data.code });
  }
}

async function safeError(response) {
  try {
    const payload = await response.json();
    return { code: payload.code, message: payload.message ?? t("requestFailed") };
  } catch {
    return { code: null, message: t("requestFailed") };
  }
}

async function sendMessage() {
  if (state.active) {
    return;
  }
  const content = elements.prompt.value;
  if (!content.trim()) {
    setStatus("emptyMessage");
    return;
  }
  const maxNewTokens = Number(elements.maxNewTokens.value);
  if (!Number.isInteger(maxNewTokens) || maxNewTokens < 1 || maxNewTokens > 2048) {
    setStatus("invalidTokenLimit");
    return;
  }

  state.messages.push({ role: "user", content });
  appendUserMessage(content);
  const assistantView = appendAssistantMessage();
  elements.prompt.value = "";
  state.controller = new AbortController();
  state.requestId = null;
  state.terminalWarning = null;
  setActive(true);
  setStatus("connecting");

  try {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: state.messages, settings: settingsPayload() }),
      signal: state.controller.signal,
      cache: "no-store",
    });
    if (!response.ok) {
      const failure = await safeError(response);
      const error = new Error(failure.message);
      error.code = failure.code;
      throw error;
    }
    await readEventStream(response, assistantView);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      rollbackPendingUser();
      setStatus("stopped");
    } else {
      rollbackPendingUser();
      assistantView.container.classList.add("message-error");
      const code = error instanceof Error ? error.code : null;
      const message = error instanceof Error ? error.message : t("requestFailed");
      setKnownNodeMessage(assistantView.finalContent, code, message);
      setStatus("requestFailed");
    }
  } finally {
    state.controller = null;
    state.requestId = null;
    state.terminalWarning = null;
    setActive(false);
    elements.prompt.focus();
  }
}

async function stopGeneration() {
  if (!state.active) {
    return;
  }
  if (state.requestId !== null) {
    try {
      await fetch("/api/v1/chat/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: state.requestId }),
        cache: "no-store",
      });
    } catch {
      setStatus("stopRequestFailed");
    }
  }
  state.controller?.abort();
}

function renderNewChatEmptyState() {
  elements.messages.replaceChildren();
  const empty = document.createElement("div");
  empty.id = "empty-state";
  empty.className = "empty-state";
  const title = document.createElement("h2");
  title.dataset.i18nMessage = "resetEmptyTitle";
  title.textContent = t("resetEmptyTitle");
  const note = document.createElement("p");
  note.dataset.i18nMessage = "resetEmptyNote";
  note.textContent = t("resetEmptyNote");
  empty.append(title, note);
  elements.messages.append(empty);
  elements.emptyState = empty;
}

async function newChat() {
  await stopGeneration();
  state.messages = [];
  state.terminalWarning = null;
  renderNewChatEmptyState();
  setStatus("idle");
}

elements.send.addEventListener("click", sendMessage);
elements.stop.addEventListener("click", stopGeneration);
elements.newChat.addEventListener("click", newChat);
elements.uiLanguageJa.addEventListener("click", () => setUiLanguage("ja"));
elements.uiLanguageEn.addEventListener("click", () => setUiLanguage("en"));
elements.thinkingMode.addEventListener("change", syncThinkingControls);
elements.prompt.addEventListener("keydown", (event) => {
  if (!event.isComposing && (event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

applyTranslations();
syncThinkingControls();
syncDocumentationRagControls();
loadRuntime();
