// Shared API response / domain types. These mirror the Backend Pydantic
// contracts (src/margpa_runtime_llm/web/contracts.py,
// persistent_contracts.py, and the configuration_control module) but are
// intentionally hand-written rather than generated, matching the existing
// vanilla-JS client's approach of trusting the JSON shape at the boundary.

export type UiLanguage = "ja" | "en";
export type UiTheme = "white" | "dark";

export interface RuntimeDefaults {
  response_language: string;
  max_new_tokens: number;
  thinking_mode: "enabled" | "disabled";
  thinking_visibility: "visible" | "hidden";
  thinking_control_available: boolean;
  summary_mode: string;
  documentation_rag_mode: string;
}

export interface DocumentationRagRuntime {
  effective_state: "enabled" | "disabled" | "unavailable" | "denied";
  control_available: boolean;
  provider_display_name: string | null;
  default_mode: string;
}

export interface RuntimeInfo {
  model_key: string;
  profile_key: string;
  device_kind: string;
  acceleration_api: string;
  defaults: RuntimeDefaults;
  documentation_rag: DocumentationRagRuntime;
}

export interface ServerWarning {
  code: string;
  message: string;
}

export interface Citation {
  project_relative_path: string;
  heading_breadcrumb: string | null;
}

export interface CitationEvidence {
  citations: Citation[];
  warnings: ServerWarning[];
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface GenerationSettings {
  response_language: string;
  max_new_tokens: number;
  thinking_mode: "enabled" | "disabled";
  thinking_visibility: "visible" | "hidden";
  summary_mode: string;
  documentation_rag_mode: string;
  context_usage_prompt_injection_mode: "enabled" | "disabled";
  expressive_mode: "enabled" | "disabled";
}

// --- Context Window usage (Phase 2-E-I) ---

export interface ContextUsageBreakdown {
  conversation_history_tokens: number;
  system_prompt_tokens: number;
  rag_context_tokens: number;
  free_tokens: number;
}

export interface ContextUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  loaded_context_size: number;
  usage_ratio: number;
  breakdown: ContextUsageBreakdown;
}

// --- Configuration Control ---

export interface ConfigurationField {
  key: string;
  value: string | number | boolean;
  source: string;
  apply_disposition: string;
}

export interface ConfigurationSnapshot {
  schema_version: string;
  revision: number;
  digest_sha512: string;
  fields: ConfigurationField[];
  feature_hooks: unknown[];
  recording_hooks: unknown[];
}

export interface ConfigurationPreviewResult {
  outcome: "restart_required" | "applied";
  redacted_changes: unknown;
}

// --- Persistent conversations (v2) ---

export interface PersistentConversationSummary {
  conversation_id: string;
  updated_at: string;
  state: string;
  title: string | null;
  has_active_session: boolean;
}

export interface PersistentConversationPage {
  items: PersistentConversationSummary[];
  next_cursor: string | null;
}

export interface PersistentTurnMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PersistentTurnCitations {
  available: boolean;
  citations: Citation[];
}

export interface PersistentTurn {
  turn_id: string;
  state: "pending" | "completed" | "failed" | "cancelled" | "interrupted";
  messages: PersistentTurnMessage[];
  citations?: PersistentTurnCitations;
}

export interface PersistentSession {
  state: string;
}

export interface PersistentConversationDetail {
  conversation_id: string;
  state: "active" | "archived" | "deleted";
  title: string | null;
  storage_revision: number;
  head_turn_id: string | null;
  turns: PersistentTurn[];
  sessions: PersistentSession[];
}

export interface PersistentMutationResponse {
  detail: PersistentConversationDetail;
}

export interface PersistentRuntimeResponse {
  enabled: boolean;
  source_of_truth: string;
}

export type ConversationMode =
  | "capability_pending"
  | "capability_failed"
  | "persistent"
  | "ephemeral";

// --- SSE stream events ---
//
// A single flat, fully-optional shape rather than an intersection of
// "required field" interfaces: which fields are actually present depends on
// `type`, and JSON off the wire is never as trustworthy as a compile-time
// type suggests. Keeping every field optional here means the `??`/optional
// chaining used at every call site is genuinely load-bearing, not just
// noise the type checker would otherwise flag as redundant.
export interface StreamEventData {
  request_id?: string;
  state?: string;
  durable_revision?: number;
  turn_id?: string;
  channel?: string;
  text?: string;
  assistant_message?: { content: string };
  finish_reason?: string;
  code?: string;
  message?: string;
  citations?: Citation[];
  warnings?: ServerWarning[];
  context_usage?: ContextUsage | null;
}

export interface StreamEvent {
  type: "start" | "retrieval" | "status" | "delta" | "warning" | "completed" | "cancelled" | "error";
  data: StreamEventData;
}

// --- UI-side unified message model (used for both ephemeral and
// persistent rendering, so MessageList/MessageBubble stay mode-agnostic) ---

export interface TurnActionSpec {
  kind: "retry" | "regenerate" | "selectBranch";
  turnId: string;
}

export interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isFinal: boolean;
  isError: boolean;
  isIncomplete: boolean;
  errorCode: string | null;
  errorMessage: string | null;
  thinkingText: string;
  thinkingVisible: boolean;
  citations: CitationEvidence | null;
  turnActions: TurnActionSpec[];
}
