// Typed fetch wrappers over the existing Backend API. This intentionally
// mirrors the request/response shapes already used by the vanilla-JS
// client (web/static/app.js) rather than introducing a new contract.
import type {
  ChatMessage,
  ConfigurationPreviewResult,
  ConfigurationSnapshot,
  ConstitutionModePreview,
  ConstitutionRuntime,
  DevAgentApprovalProfile,
  DevAgentCapability,
  DevAgentCapabilityId,
  DevAgentPlanStepRequest,
  DevAgentRun,
  DevAgentToolDescriptor,
  GenerationSettings,
  GovernanceStatus,
  GuardrailGovernanceStatus,
  DataControlPolicy,
  LocalCorpusDocument,
  LocalCorpusDocumentList,
  LocalCorpusDocumentSummary,
  PersistentConversationDetail,
  WebSearchActivation,
  WebSearchResult,
  PersistentConversationPage,
  PersistentMutationResponse,
  PersistentRuntimeResponse,
  FeatureModesStatus,
  ProviderRole,
  ProviderSelectionStatus,
  RuntimeGovernanceStatus,
  RuntimeInfo,
  RuntimeModelStatus,
} from "../types";

export interface ApiFailure {
  code: string | null;
  message: string;
}

export class ApiMutationError extends Error {
  readonly code: string | null;

  constructor(failure: ApiFailure) {
    super(failure.message);
    this.name = "ApiMutationError";
    this.code = failure.code;
  }
}

export async function safeError(response: Response, fallbackMessage: string): Promise<ApiFailure> {
  try {
    const payload = (await response.json()) as { code?: string; message?: string };
    return { code: payload.code ?? null, message: payload.message ?? fallbackMessage };
  } catch {
    return { code: null, message: fallbackMessage };
  }
}

export async function fetchRuntime(): Promise<RuntimeInfo> {
  const response = await fetch("/api/v1/runtime", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("runtime_load_failed");
  }
  return (await response.json()) as RuntimeInfo;
}

export function startChatStream(
  messages: ChatMessage[],
  settings: GenerationSettings,
  signal: AbortSignal,
): Promise<Response> {
  return fetch("/api/v1/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, settings }),
    signal,
    cache: "no-store",
  });
}

export async function stopChat(requestId: string): Promise<void> {
  await fetch("/api/v1/chat/stop", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: requestId }),
    cache: "no-store",
  });
}

export async function fetchPersistentRuntime(): Promise<PersistentRuntimeResponse> {
  const response = await fetch("/api/v2/conversations/runtime", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("persistent_capability_load_failed");
  }
  return (await response.json()) as PersistentRuntimeResponse;
}

// P8-MR3 (P8-MANUAL-003): explicit `state=active` — without it, the
// Backend's default returns both Active and Archived Conversations, so an
// Archived Chat kept reappearing in the ordinary Sidebar list alongside
// the Archived-only Data Controls panel below.
export async function fetchPersistentList(): Promise<PersistentConversationPage> {
  const response = await fetch("/api/v2/conversations?state=active&limit=50", {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error((await safeError(response, "request_failed")).message);
  }
  return (await response.json()) as PersistentConversationPage;
}

// P8-B (P8-REQ-010): the `state=archived` query param and cursor pagination
// already existed server-side (Phase 2-E) — this is purely a new Client-side
// call, not new Backend surface. "Lazy" (P8-REQ-010's own wording) means
// this is only ever called on demand from the Data Controls panel, never
// eagerly alongside the ordinary Sidebar list.
export async function fetchArchivedPersistentList(
  cursor: string | null = null,
): Promise<PersistentConversationPage> {
  const query = new URLSearchParams({ state: "archived", limit: "50" });
  if (cursor !== null) {
    query.set("cursor", cursor);
  }
  const response = await fetch(`/api/v2/conversations?${query.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error((await safeError(response, "request_failed")).message);
  }
  return (await response.json()) as PersistentConversationPage;
}

export async function fetchPersistentDetail(
  conversationId: string,
): Promise<PersistentConversationDetail> {
  const response = await fetch(`/api/v2/conversations/${encodeURIComponent(conversationId)}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error((await safeError(response, "request_failed")).message);
  }
  return (await response.json()) as PersistentConversationDetail;
}

export async function createPersistentConversation(
  operationId: string,
): Promise<PersistentMutationResponse> {
  const response = await fetch("/api/v2/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation_id: operationId, expected_revision: null }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("request_failed");
  }
  return (await response.json()) as PersistentMutationResponse;
}

export function startPersistentTurnStream(
  conversationId: string,
  content: string,
  settings: GenerationSettings,
  operationId: string,
  expectedRevision: number,
  signal: AbortSignal,
): Promise<Response> {
  return fetch(`/api/v2/conversations/${encodeURIComponent(conversationId)}/turns/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content,
      settings,
      operation_id: operationId,
      expected_revision: expectedRevision,
    }),
    signal,
    cache: "no-store",
  });
}

export function startPersistentDerivedStream(
  conversationId: string,
  turnId: string,
  kind: "retry" | "regenerate",
  settings: GenerationSettings,
  operationId: string,
  expectedRevision: number,
  signal: AbortSignal,
): Promise<Response> {
  return fetch(
    `/api/v2/conversations/${encodeURIComponent(conversationId)}/turns/${encodeURIComponent(turnId)}/${kind}/stream`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        settings,
        operation_id: operationId,
        expected_revision: expectedRevision,
      }),
      signal,
      cache: "no-store",
    },
  );
}

export async function stopPersistentGeneration(
  conversationId: string,
  requestId: string,
  expectedRevision: number,
): Promise<Response> {
  return fetch(
    `/api/v2/conversations/${encodeURIComponent(conversationId)}/generations/${encodeURIComponent(requestId)}/stop`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request_id: requestId, expected_revision: expectedRevision }),
      cache: "no-store",
    },
  );
}

export async function persistentMutation(
  path: string,
  operationId: string,
  expectedRevision: number,
): Promise<Response> {
  return fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ operation_id: operationId, expected_revision: expectedRevision }),
    cache: "no-store",
  });
}

export async function renamePersistentConversation(
  conversationId: string,
  title: string,
  operationId: string,
  expectedRevision: number,
): Promise<Response> {
  return fetch(`/api/v2/conversations/${encodeURIComponent(conversationId)}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title,
      operation_id: operationId,
      expected_revision: expectedRevision,
    }),
    cache: "no-store",
  });
}

export async function fetchConfigurationRuntime(): Promise<{
  enabled: boolean;
  non_persistent: boolean;
}> {
  const response = await fetch("/api/v2/configuration/runtime", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("configuration_runtime_unavailable");
  }
  return (await response.json()) as { enabled: boolean; non_persistent: boolean };
}

export async function fetchConfigurationEffective(): Promise<ConfigurationSnapshot> {
  const response = await fetch("/api/v2/configuration/effective", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("configuration_effective_unavailable");
  }
  return (await response.json()) as ConfigurationSnapshot;
}

export async function previewConfigurationPatch(
  patch: Record<string, unknown>,
): Promise<ConfigurationPreviewResult> {
  const response = await fetch("/api/v2/configuration/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patch }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("configuration_preview_failed");
  }
  return (await response.json()) as ConfigurationPreviewResult;
}

export async function applyConfigurationPatch(
  operationId: string,
  expectedRevision: number,
  expectedDigest: string,
  patch: Record<string, unknown>,
): Promise<Response> {
  return fetch("/api/v2/configuration/apply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      operation_id: operationId,
      expected_revision: expectedRevision,
      expected_digest: expectedDigest,
      patch,
    }),
    cache: "no-store",
  });
}

export async function fetchGovernanceStatus(): Promise<GovernanceStatus> {
  const response = await fetch("/api/v3/governance/runtime", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("governance_runtime_unavailable");
  }
  return (await response.json()) as GovernanceStatus;
}

export async function fetchRuntimeGovernanceStatus(): Promise<RuntimeGovernanceStatus> {
  const response = await fetch("/api/v3/runtime-governance/status", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("runtime_governance_status_unavailable");
  }
  return (await response.json()) as RuntimeGovernanceStatus;
}

export async function fetchRuntimeModelStatus(): Promise<RuntimeModelStatus> {
  const response = await fetch("/api/v4/runtime-model/status", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("runtime_model_status_unavailable");
  }
  return (await response.json()) as RuntimeModelStatus;
}

export async function applyRuntimeModelContext(
  expectedRevision: number,
  expectedDigest: string,
  requestedContextSize: number,
): Promise<RuntimeModelStatus> {
  const response = await fetch("/api/v4/runtime-model/context", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      expected_revision: expectedRevision,
      expected_digest: expectedDigest,
      requested_context_size: requestedContextSize,
    }),
  });
  if (!response.ok) {
    const failure = await safeError(response, "runtime_model_context_change_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as RuntimeModelStatus;
}

export async function applyRuntimeModelMaxNewTokens(
  expectedRevision: number,
  expectedDigest: string,
  requestedMaxNewTokens: number,
): Promise<RuntimeModelStatus> {
  const response = await fetch("/api/v4/runtime-model/max-new-tokens", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      expected_revision: expectedRevision,
      expected_digest: expectedDigest,
      requested_max_new_tokens: requestedMaxNewTokens,
    }),
  });
  if (!response.ok) {
    const failure = await safeError(response, "runtime_model_max_new_tokens_change_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as RuntimeModelStatus;
}

export async function applyRuntimeModelSwitch(
  expectedRevision: number,
  expectedDigest: string,
  targetModelKey: string,
  requestedContextSize: number,
): Promise<RuntimeModelStatus> {
  const response = await fetch("/api/v4/runtime-model/switch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      expected_revision: expectedRevision,
      expected_digest: expectedDigest,
      target_model_key: targetModelKey,
      requested_context_size: requestedContextSize,
    }),
  });
  if (!response.ok) {
    const failure = await safeError(response, "runtime_model_switch_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as RuntimeModelStatus;
}

export async function fetchConstitutionRuntime(): Promise<ConstitutionRuntime> {
  const response = await fetch("/api/v2/constitution/runtime", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("constitution_unavailable");
  }
  return (await response.json()) as ConstitutionRuntime;
}

export async function fetchConstitutionModePreview(): Promise<ConstitutionModePreview> {
  const response = await fetch("/api/v2/constitution/preview", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("constitution_unavailable");
  }
  return (await response.json()) as ConstitutionModePreview;
}

export async function fetchDevAgentCapabilities(): Promise<DevAgentCapability[]> {
  const response = await fetch("/api/v2/dev-agent/capabilities", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("dev_agent_unavailable");
  }
  return (await response.json()) as DevAgentCapability[];
}

export async function fetchDevAgentTools(): Promise<DevAgentToolDescriptor[]> {
  const response = await fetch("/api/v2/dev-agent/tools", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("dev_agent_unavailable");
  }
  return (await response.json()) as DevAgentToolDescriptor[];
}

export async function startDevAgentRun(
  capabilityId: DevAgentCapabilityId,
  steps: DevAgentPlanStepRequest[],
  approvalProfile: DevAgentApprovalProfile,
): Promise<DevAgentRun> {
  const response = await fetch("/api/v2/dev-agent/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      capability_id: capabilityId,
      steps,
      approval_profile: approvalProfile,
    }),
  });
  if (!response.ok) {
    const failure = await safeError(response, "dev_agent_run_start_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as DevAgentRun;
}

export async function advanceDevAgentRun(runId: string): Promise<DevAgentRun> {
  const response = await fetch(`/api/v2/dev-agent/runs/${encodeURIComponent(runId)}/advance`, {
    method: "POST",
  });
  if (!response.ok) {
    const failure = await safeError(response, "dev_agent_run_advance_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as DevAgentRun;
}

export async function submitDevAgentApproval(
  runId: string,
  stepId: string,
  decision: "approved" | "denied",
): Promise<DevAgentRun> {
  const response = await fetch(`/api/v2/dev-agent/runs/${encodeURIComponent(runId)}/approvals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ step_id: stepId, decision }),
  });
  if (!response.ok) {
    const failure = await safeError(response, "dev_agent_run_approval_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as DevAgentRun;
}

export async function submitDevAgentCompletionApproval(
  runId: string,
  decision: "approved" | "denied",
): Promise<DevAgentRun> {
  const response = await fetch(
    `/api/v2/dev-agent/runs/${encodeURIComponent(runId)}/completion-approval`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    },
  );
  if (!response.ok) {
    const failure = await safeError(response, "dev_agent_run_completion_approval_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as DevAgentRun;
}

export async function cancelDevAgentRun(runId: string): Promise<DevAgentRun> {
  const response = await fetch(`/api/v2/dev-agent/runs/${encodeURIComponent(runId)}/cancel`, {
    method: "POST",
  });
  if (!response.ok) {
    const failure = await safeError(response, "dev_agent_run_cancel_failed");
    throw new ApiMutationError(failure);
  }
  return (await response.json()) as DevAgentRun;
}

export async function fetchFeatureModesStatus(): Promise<FeatureModesStatus> {
  const response = await fetch("/api/v5/feature-modes/status", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("feature_modes_status_unavailable");
  }
  return (await response.json()) as FeatureModesStatus;
}

async function applyFeatureMode(
  path: "judge" | "repair" | "recording",
  requestedMode: string,
): Promise<FeatureModesStatus> {
  const response = await fetch(`/api/v5/feature-modes/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requested_mode: requestedMode }),
  });
  if (!response.ok) {
    const failure = await safeError(response, `feature_modes_${path}_apply_failed`);
    throw new Error(failure.code ?? failure.message);
  }
  return (await response.json()) as FeatureModesStatus;
}

export function applyJudgeMode(requestedMode: string): Promise<FeatureModesStatus> {
  return applyFeatureMode("judge", requestedMode);
}

export function applyRepairMode(requestedMode: string): Promise<FeatureModesStatus> {
  return applyFeatureMode("repair", requestedMode);
}

export function applyRecordingMode(requestedMode: string): Promise<FeatureModesStatus> {
  return applyFeatureMode("recording", requestedMode);
}

export async function fetchProviderSelectionStatus(): Promise<ProviderSelectionStatus> {
  const response = await fetch("/api/v6/provider-selection", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("provider_selection_status_unavailable");
  }
  return (await response.json()) as ProviderSelectionStatus;
}

export async function applyProviderSelection(
  role: ProviderRole,
  providerId: string,
  expectedRevision: number,
  expectedDigest: string,
): Promise<ProviderSelectionStatus> {
  const response = await fetch(`/api/v6/provider-selection/${role}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      provider_id: providerId,
      expected_revision: expectedRevision,
      expected_digest: expectedDigest,
    }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "provider_selection_apply_failed"));
  }
  return (await response.json()) as ProviderSelectionStatus;
}

export async function fetchGuardrailGovernanceStatus(): Promise<GuardrailGovernanceStatus> {
  const response = await fetch("/api/v3/guardrail-governance/status", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("guardrail_governance_status_unavailable");
  }
  return (await response.json()) as GuardrailGovernanceStatus;
}

export async function fetchLocalCorpusDocuments(): Promise<LocalCorpusDocumentList> {
  const response = await fetch("/api/v2/local-corpus/documents", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("local_corpus_unavailable");
  }
  return (await response.json()) as LocalCorpusDocumentList;
}

export async function fetchLocalCorpusDocument(documentId: string): Promise<LocalCorpusDocument> {
  const response = await fetch(`/api/v2/local-corpus/documents/${encodeURIComponent(documentId)}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("local_corpus_document_unavailable");
  }
  return (await response.json()) as LocalCorpusDocument;
}

export async function registerLocalCorpusDocument(
  title: string,
  content: string,
): Promise<LocalCorpusDocument> {
  const response = await fetch("/api/v2/local-corpus/documents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "local_corpus_register_failed"));
  }
  return (await response.json()) as LocalCorpusDocument;
}

export async function updateLocalCorpusDocument(
  documentId: string,
  title: string,
  content: string,
): Promise<LocalCorpusDocument> {
  const response = await fetch(`/api/v2/local-corpus/documents/${encodeURIComponent(documentId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "local_corpus_update_failed"));
  }
  return (await response.json()) as LocalCorpusDocument;
}

export async function deleteLocalCorpusDocument(
  documentId: string,
): Promise<LocalCorpusDocumentSummary> {
  const response = await fetch(`/api/v2/local-corpus/documents/${encodeURIComponent(documentId)}`, {
    method: "DELETE",
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "local_corpus_delete_failed"));
  }
  return (await response.json()) as LocalCorpusDocumentSummary;
}

export async function searchWeb(
  query: string,
  activation: WebSearchActivation,
): Promise<WebSearchResult> {
  const response = await fetch("/api/v2/web-search/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, activation }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "web_search_failed"));
  }
  return (await response.json()) as WebSearchResult;
}

export async function fetchDirectUrl(
  url: string,
  activation: WebSearchActivation,
): Promise<WebSearchResult> {
  const response = await fetch("/api/v2/web-search/direct", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, activation }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "web_search_direct_fetch_failed"));
  }
  return (await response.json()) as WebSearchResult;
}

export async function fetchDataControlPolicy(): Promise<DataControlPolicy> {
  const response = await fetch("/api/v2/data-controls/policy", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("data_controls_unavailable");
  }
  return (await response.json()) as DataControlPolicy;
}

export async function updateDataControlConsent(
  patch: Partial<DataControlPolicy["consent"]>,
): Promise<DataControlPolicy> {
  const response = await fetch("/api/v2/data-controls/consent", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "data_controls_update_failed"));
  }
  return (await response.json()) as DataControlPolicy;
}

export async function resetDataControlConsent(): Promise<DataControlPolicy> {
  const response = await fetch("/api/v2/data-controls/reset", {
    method: "POST",
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiMutationError(await safeError(response, "data_controls_reset_failed"));
  }
  return (await response.json()) as DataControlPolicy;
}

export function newActionId(): string {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
}
