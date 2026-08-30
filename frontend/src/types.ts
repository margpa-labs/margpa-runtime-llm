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
  source_class: string;
  project_relative_path: string;
  heading_breadcrumb: string | null;
  chunk_id: string;
  document_sha512: string;
  retrieval_score: number;
  selected_order: number;
  truncated: boolean;
  // P7-RW5-B/C: only ever populated for a Local Corpus Citation
  // (`source_class === "local_corpus"`) - `null` for Project Docs and for
  // any Citation persisted before these fields existed.
  document_title: string | null;
  storage_display_path: string | null;
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

// --- Governance Definitions (Phase 3-F) ---

export type GovernanceMode = "off" | "observe" | "enforce";

export interface GovernanceModeDescriptor {
  mode: GovernanceMode;
  availability: "available" | "unavailable";
  apply_disposition: string;
  unavailable_reason_code: string | null;
}

export interface GovernanceModeInfo {
  revision: number;
  digest_sha512: string;
  current_mode: GovernanceMode;
  descriptors: GovernanceModeDescriptor[];
}

export interface GovernanceObserveSummary {
  provider_state: string;
  package_found: boolean;
  package_state: string | null;
  definition_count: number;
  valid_definition_count: number;
  invalid_definition_count: number;
  unsupported_definition_count: number;
  compiled_plan_id: string | null;
}

export interface GovernanceStatus {
  mode: GovernanceModeInfo;
  observe_summary: GovernanceObserveSummary | null;
}

// --- Main Runtime Governance (Phase 4) ---

export type MainGovernanceMode = "off" | "observe" | "enforce";

export interface MainGovernanceModeDescriptor {
  mode: MainGovernanceMode;
  availability: "available" | "unavailable";
  unavailable_reason_code: string | null;
}

export interface RuntimeGovernancePointStatus {
  point_id: string;
  execution_state: string | null;
  selected_descriptor_count: number | null;
  severity: string | null;
  recommended_action_count: number | null;
  executed_action_count: number | null;
  unavailable_reason_code: string | null;
  degraded_reason_code: string | null;
  latency_ms: number | null;
  observation_count: number | null;
  pass_count: number | null;
  deviation_count: number | null;
  deferred_count: number | null;
}

export interface RuntimeGovernanceEvidenceStatus {
  degraded: boolean;
  degraded_reason_code: string | null;
  degraded_event_count: number;
}

export interface RuntimeGovernanceStatus {
  enabled: boolean;
  revision: number | null;
  current_mode: MainGovernanceMode | null;
  descriptors: MainGovernanceModeDescriptor[];
  points: RuntimeGovernancePointStatus[];
  evidence: RuntimeGovernanceEvidenceStatus | null;
}

// --- Runtime Model Control (Phase 6) ---

export interface RuntimeModelMainIdentity {
  model_key: string;
  artifact_digest: string;
  backend_identity: string;
  state: string;
}

export interface RuntimeModelJudgeIdentity {
  model_key: string | null;
  independence_class: string;
  state: string;
}

export interface RuntimeModelGuardIdentity {
  model_id: string | null;
  exact_revision: string | null;
  artifact_digest_sha512: string | null;
  state: string;
}

export interface RuntimeModelGovernanceLayerIdentity {
  package_id: string | null;
  manifest_digest_sha512: string | null;
  state: string;
}

export interface FeatureModeSnapshot {
  enabled: boolean;
  revision: number | null;
  current_mode: string | null;
}

export interface JudgeLastResult {
  request_id: string;
  judge_role: string;
  recommendation: string;
  confidence: number;
  execution_state: string;
  failure_reason: string | null;
  repair_eligibility: string | null;
  repair_outcome: string | null;
  repair_accepted: boolean | null;
  repair_new_turn_id: string | null;
  presentation_outcome?: string | null;
  candidate_withheld?: boolean;
  started_at?: string | null;
  completed_at?: string | null;
  frozen_main_mode?: string | null;
  frozen_guard_mode?: string | null;
  frozen_judge_mode?: string | null;
  frozen_repair_mode?: string | null;
  recording_mode?: string | null;
  configured_provider?: string | null;
  active_provider?: string | null;
  executed_provider?: string | null;
  budget_profile?: string | null;
  criteria_selected?: number;
  criteria_evaluated?: number;
  criteria_passed?: number;
  criteria_deviated?: number;
  criteria_unknown?: number;
  criteria_not_applicable?: number;
  criteria_deferred?: number;
  judge_outcome?: string | null;
  final_disposition?: string | null;
  failure_message?: string | null;
  failure_language?: string | null;
  repair_rejudge_provider?: string | null;
  repair_rejudge_role?: string | null;
}

export interface JudgeModeSnapshot extends FeatureModeSnapshot {
  // `idle`/`queued_or_skipped` mean no Judge Run is in flight right now
  // (P6-CODEX-020, Third Rework: `queued_or_skipped` covers both Judge OFF
  // and a busy-Model skip, always correlated with `current_request_id`),
  // so `last_result` (if present) is necessarily from a *previous* Turn,
  // not this one — a reader must compare `last_result.request_id` against
  // `current_request_id`, never assume freshness from `state` alone.
  // P6-CODEX-031 (Fourth Rework): "judging"/"repairing"/"rejudging" are
  // three distinct in-flight sub-states (never a single generic
  // "running") — the exact P6-OBS-004 Runtime State vocabulary for this
  // portion of the pipeline.
  state:
    | "idle"
    | "queued_or_skipped"
    | "judging"
    | "repairing"
    | "rejudging"
    | "completed"
    | "failed"
    | "cancelled"
    | "degraded"
    | null;
  current_request_id: string | null;
  last_result: JudgeLastResult | null;
  historical_last_result?: JudgeLastResult | null;
}

export interface RecordingOutcome {
  request_id: string;
  ok: boolean;
  degraded_reason: string | null;
}

// P6-RR-R19-WU-001..004 (Post-Claude Independent Review Rework, resolves
// P6-CODEX-082): the Server-side single Join of Turn Metadata (from the
// shared Request Correlation Registry, valid from the instant a Turn
// starts, not only once it completes), Judge Result, and both Recording
// Outcomes for the Current Request.
export interface RequestCorrelationSummary {
  request_id: string;
  status: "pending" | "completed" | "cancelled" | "failed";
  started_at: string;
  completed_at: string | null;
  judge_result: JudgeLastResult | null;
  turn_recording: RecordingOutcome | null;
  judge_evidence_recording: RecordingOutcome | null;
}

export interface RecordingModeSnapshot extends FeatureModeSnapshot {
  last_outcome: RecordingOutcome | null;
  judge_evidence_last_outcome: RecordingOutcome | null;
  correlation?: {
    request_id: string | null;
    current: RequestCorrelationSummary | null;
    current_turn: RecordingOutcome | null;
    current_judge_evidence: RecordingOutcome | null;
    historical_or_unmatched: RecordingOutcome[];
  } | null;
}

export interface FeatureModesStatus {
  judge: JudgeModeSnapshot;
  repair: FeatureModeSnapshot;
  recording: RecordingModeSnapshot;
}

export type ProviderRole = "main" | "guard" | "judge";

export interface ProviderStageBudget {
  profile_id: string;
  verification_state: string;
  load_budget_ms: number;
  prompt_build_budget_ms: number;
  inference_budget_ms: number;
  decode_budget_ms: number;
  repair_generation_budget_ms: number;
  rejudge_budget_ms: number;
  cancel_grace_ms: number;
}

export interface ProviderOption {
  provider_id: string;
  role: ProviderRole;
  kind: "none" | "built_in" | "model";
  display_name: string;
  enabled: boolean;
  model_key: string | null;
}

export interface RoleProviderSelection {
  role: ProviderRole;
  configured_provider: string;
  active_provider: string | null;
  state: string;
  independence: string;
  failure_reason: string | null;
  failure_at: string | null;
  budget: ProviderStageBudget | null;
}

export interface ProviderSelectionStatus {
  enabled: boolean;
  revision: number | null;
  digest_sha512: string | null;
  selections: RoleProviderSelection[];
  options: ProviderOption[];
}

export interface RuntimeModelAvailableModel {
  model_key: string;
  provider: string;
  native_context_limit: number;
  backend_context_limit: number;
  hardware_verified_context_limit: number;
  effective_context_limit: number;
  context_limit_reason_code: string;
  max_output_token_limit: number;
}

export interface RuntimeModelStatus {
  enabled: boolean;
  configured_startup_model_key: string | null;
  revision: number | null;
  digest_sha512: string | null;
  runtime_state: string | null;
  loaded_context_size: number | null;
  model_native_context_limit: number | null;
  backend_context_limit: number | null;
  deployment_verified_context_limit: number | null;
  hardware_verified_context_limit: number | null;
  effective_context_limit: number | null;
  minimum_context_size: number | null;
  context_limit_reason_code: string | null;
  max_output_token_limit: number | null;
  current_max_new_tokens: number | null;
  main_model: RuntimeModelMainIdentity | null;
  judge_model: RuntimeModelJudgeIdentity | null;
  guard_model: RuntimeModelGuardIdentity | null;
  governance_layer: RuntimeModelGovernanceLayerIdentity | null;
  available_models: RuntimeModelAvailableModel[];
}

// --- Guardrail Governance (Phase 5) ---

export type GuardrailGovernanceMode = "off" | "observe" | "enforce";

export interface GuardrailModeDescriptor {
  mode: GuardrailGovernanceMode;
  availability: "available" | "unavailable";
  unavailable_reason_code: string | null;
}

export interface GuardrailPointStatus {
  point_id: string;
  execution_state: string | null;
  severity: string | null;
  recommended_action_count: number | null;
  executed_action_count: number | null;
  unavailable_reason_code: string | null;
  degraded_reason_code: string | null;
  latency_ms: number | null;
  detection_count: number | null;
  match_count: number | null;
}

export interface GuardrailGovernanceStatus {
  enabled: boolean;
  revision: number | null;
  current_mode: GuardrailGovernanceMode | null;
  descriptors: GuardrailModeDescriptor[];
  points: GuardrailPointStatus[];
}

// --- Local Corpus (Phase 7-B) ---

export type LocalCorpusDocumentState = "active" | "deleted";

export interface LocalCorpusDocumentSummary {
  document_id: string;
  state: LocalCorpusDocumentState;
  title: string;
  content_sha512: string;
  character_count: number;
  current_revision: number;
  created_at: string;
  updated_at: string;
}

export interface LocalCorpusDocument extends LocalCorpusDocumentSummary {
  content: string;
}

export interface LocalCorpusDocumentList {
  documents: LocalCorpusDocumentSummary[];
}

// --- Web Search (Phase 7-E/F) ---

export type WebSearchActivation = "disabled" | "manual" | "automatic";
export type WebEvidenceGovernanceMode = "off" | "observe" | "enforce";

export interface WebEvidenceItem {
  evidence_id: string;
  canonical_url: string;
  title: string;
  provider_key: string;
  source_authority: string;
  snippet: string;
  fetched: boolean;
  fetched_content: string | null;
  withheld_by_governance: boolean;
  fetched_at: string | null;
  content_type: string | null;
  prompt_injection_detected: boolean;
  rejected: boolean;
  rejection_reason: string | null;
}

export interface WebCitationItem {
  citation_id: string;
  canonical_url: string;
  title: string;
  provider_key: string;
  source_authority: string;
  fetched_at: string | null;
  selected_order: number;
}

export interface WebSearchResult {
  request_id: string;
  activation: WebSearchActivation;
  governance_mode: WebEvidenceGovernanceMode;
  evidence: WebEvidenceItem[];
  citations: WebCitationItem[];
  should_generate_with_evidence: boolean;
  failure_reason: string | null;
  network_calls_made: number;
}

export interface WebSearchRuntimeResponse {
  enabled: boolean;
  governance_mode: WebEvidenceGovernanceMode;
}

// --- Data Controls (Phase 7-G) ---

export interface DataControlConsent {
  external_query_transmission_consent: boolean;
  feedback_research_use: boolean;
  synthetic_data_use: boolean;
  future_training_export: boolean;
  updated_at: string;
}

export interface DataControlRetentionFact {
  source_class: string;
  retained: boolean;
  description: string;
}

export interface DataControlPolicy {
  consent: DataControlConsent;
  retention_facts: DataControlRetentionFact[];
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
  // P7-RW5-A: reuses `PersistedTurnCitationEvidence.warning_codes` - lets a
  // Persistent Detail reload reconstruct a NO_HIT "no current grounds"
  // display even though `citations` itself stays empty for that Grounding
  // State.
  warning_codes: string[];
}

export interface PersistentTurn {
  turn_id: string;
  state: "pending" | "completed" | "failed" | "cancelled" | "interrupted";
  messages: PersistentTurnMessage[];
  citations?: PersistentTurnCitations;
  failure_reason_code?: string | null;
  // P6-CODEX-024 (Third Rework): already present on the backend's
  // `PersistentTurnResponse` (`turn.request_id`, set at `start_generation`)
  // but not previously consumed here — the correlation key a Live Judge/
  // Repair badge needs, durable across a full conversation-detail reload
  // (unlike a purely in-memory, streaming-only `requestId`, which a detail
  // reload after completion would otherwise silently wipe back to null).
  request_id?: string | null;
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
  // P6-CODEX-024 (Third Rework): the backend request_id this specific
  // assistant Turn's Generation Attempt ran under — the correlation key a
  // Live Judge/Repair badge on the Chat surface is matched against (see
  // `LiveJudgeBadge` below), never a fabricated identity when unknown
  // (e.g. a reconstructed historical Turn from before this field existed).
  requestId: string | null;
}

/** P6-CODEX-024 (Third Rework): a Current-Request-correlated Live Judge/
 * Repair projection for the Chat surface — distinct from
 * `FeatureModesStatus.judge`'s own richer, Feature-Modes-Panel-only view.
 * `requestId` is always the specific Turn's request_id this badge is
 * currently for; a `MessageBubble` only ever renders it when its own
 * `message.requestId` equals this `requestId` — never presented as
 * "current" for any other Turn. */
export interface LiveJudgeBadge {
  requestId: string;
  state: string;
  repairAccepted: boolean | null;
}
