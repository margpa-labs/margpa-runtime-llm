# MARGPA Runtime LLM 基本設計書

```yaml
document_id: basic_design
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-08-04 06:11:04 JST
owner: Nazuna Research
active_phase: phase_2_ready_to_start
rag_default: true
```

## 1. Scope

本書はRequirementsを実装へ渡すためのModule、Interface、State、Config、ErrorおよびDirectory境界を定義する。個別Classや関数単位の詳細設計はSourceとPhase別設計へ委ねる。

## 2. Project Module

```text
src/margpa_runtime_llm/
├─ domain／contracts
├─ application／use_cases
├─ adapters
├─ modules
└─ entrypoints
   ├─ cli
   └─ web
```

依存方向はDomain／Contractを中心とし、EntrypointやAdapterからCoreへ接続する。

## 3. Model Runtime

### Input

- Message列
- Generation Config
- Cancellation Handle
- Model Selection
- Deployment Profile

### Output

- Streaming Delta
- Final Text
- Thinking／Final Channel
- Stop Reason
- Token Usage
- Runtime Metadata

### Invariant

- 同一Runtime Instanceの同時Generation上限は1。
- Busy時は安全に拒否し、先行Requestを壊さない。
- StopはCooperative Cancelを基本とする。
- Close／ShutdownはIdempotentにする。
- Model Artifact Hash検証失敗時はLoadしない。

## 4. Configuration

```text
config/application/
  → 共通Model選択、回答、Generation、Presentation

config/profiles/
  → OS、Architecture、Device、Backend、Acceleration

config/models/
  → Model ID、Artifact Relative Path、Hash、Capability
```

Environment／CLI／Web RequestはTyped Validation後にOverrideする。UIがTOMLを直接無検証で書き換える構造にしない。

## 5. CLI

```text
margpa-llm model-info
margpa-llm generate
```

- `model-info`はEffective Config、Model、Capability、Deploymentを表示する。
- `generate`はPromptまたはstdinを受け、Streaming／Non-streamingを選べる。
- Help内の大文字表記は仮引数名であり、Literal入力ではない。
- Token上限到達、Cancel、Config Errorを区別する。

## 6. Web

### Current Surface

- New Chat
- Message Input
- Stop／Send
- UI Language
- Response Language
- Max New Tokens
- Thinking Generation／Visibility
- Summary Mode
- User／Assistant Copy

### State

- Conversation：Browser Memoryのみ
- UI Language：Browser側で保持可能
- その他Option：Reload時にRuntime Defaultへ戻る。
- Server側永続履歴：未実装

### Access Profile

```text
basic_preview:
  Basic認証

public_demo:
  匿名Access
  Side-effect-free
  Server-side Hard Limit
```

Access Modeは起動時に固定する。非Loopback BindでModeまたはPolicyが不足する場合はFail Closedとする。

Public Demoは最大生成Token、入力、Message数、会話全体量、Rate、Generation BudgetおよびTimeoutをServer側で制限する。Tool／RAG／Agent／外部I/O／永続化はLoadしない。

### Streaming Presentation

- 生成中は安全なPlain Textとして表示する。
- Completion後にSanitize済みMarkdownへ変換する。
- ThinkingとFinalを別Channel／表示領域で扱う。
- Hidden ThinkingをClientへ送らない。
- Raw Thinkingを永続化しない。

## 7. Summary Mode

```text
Original Generation
  ↓ completed
Summary Generation by same Main Model
  ↓
Summary成功  : Summaryだけを返す
Summary失敗  : OriginalへFallback
```

Summaryは情報を省略、変形する可能性があり、正確性を保証しない。追加LatencyとTokenをUIで明示する。

## 8. Error Model

最低限区別する。

```text
configuration_error
model_artifact_error
capability_error
model_busy
generation_cancelled
token_limit_reached
backend_error
summary_failed_with_fallback
authentication_required
docs_unavailable
```

内部ExceptionやPathをPublic Responseへそのまま露出しない。

## 9. Security

- Non-loopback BindはAccess Controlなしで許可しない。
- `/healthz`は最小Statusだけを返す。
- CredentialをDocs、Config、ScreenshotまたはGitへ保存しない。
- Raw HTML、Script、Event Handlerおよび危険URL Schemeを拒否する。
- Tool／RAG／外部操作は明示的に有効化されるまで実行しない。
- Public DemoではTool／RAG／外部操作をConfig Overrideでも有効化できない。

## 10. Documentation／RAG

簡易Documentation RAGの既定Source：

```text
docs/project/current/
docs/project/phases/<active_phase>/phase_index_ja.md
docs/project/phases/<completed_phase>/*_ja.md
docs/public/
```

`history/`は通常検索から除外する。`docs/`が存在しない場合は、推測で回答せず「docsが設置されていないため参照できません」と明示する。

実装はMac限定でも、次を交換可能なPortとして分離する。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
```

Lightning、Home ServerまたはCloudではAdapterを追加する。Public DemoではRAG PortをBindingしない。

## 11. Future Component Contract

各追加Componentは最低限次を持つ。

```text
component_id
enabled
mode
required_dependencies
optional_dependencies
capabilities
input_contract
output_contract
timeout
budget
failure_policy
status_events
audit_fields
```

Component本体と専用Governance Pointを別に有効化する。

AgentおよびToolは、Component本体、通常Governance BindingおよびConstitution適用を別状態として扱う。

```text
component.enabled = true／false
constitution.enabled = true／false
governance.mode = off／observe／enforce
constitution_revision
constitution_view_id
constitution_view_digest
constitution_failure_policy
```

Agentと各ToolのConstitution状態は独立する。Agent Constitution ONは、Tool Constitution ON、Tool Permission、Side Effect ApprovalまたはHuman Approvalを生成しない。Constitution OFFは憲法固有処理の比較Baselineであり、Platform Security、Sandbox、Access Controlまたは既存Authorityを解除しない。

Constitution ONでRevision、View、Digestまたは必要Capabilityを解決できない場合はFail-closedとし、OFFへ暗黙Fallbackしない。Component本体OFFとConstitution ON等の矛盾はInvalid Combinationとして扱う。

## 12. Traceability

- [Requirements](../requirements/requirements_specification_ja.md)
- [System Architecture](system_architecture_ja.md)
- [Runtime Governance](../governance/runtime_governance_specification_ja.md)
- [Phase 1 Architecture Compilation](../../phases/phase_1/architecture/phase_1_architecture_ja.md)

## 13. Current Source Boundary

Current実装のLogical Moduleは次のとおりである。

```text
src/margpa_runtime_llm/
├─ adapters/
│  ├─ model_backends/
│  │  └─ llama_cpp/
│  └─ output_protocols/
├─ bootstrap/
├─ entrypoints/
│  ├─ cli/
│  └─ web/
├─ modules/
│  ├─ conversation/
│  ├─ inference/
│  │  ├─ application/
│  │  ├─ contracts/
│  │  ├─ domain/
│  │  └─ ports/
│  ├─ presentation/
│  └─ summarization/
├─ orchestration/
├─ shared/
└─ web/
   └─ static/
```

`__pycache__`等の生成物はSource構成に含めず、公開前Sanitationで除外する。

## 14. Bootstrap／Composition

Bootstrapは次を解決してApplication Runtimeを構成する。

```text
CLI／Web Arguments
  ↓
Project Path Resolution
  ↓
Application Config Load
  ↓
Platform Registry／Deployment Profile Resolution
  ↓
Model Registry Load
  ↓
Model Artifact Resolution／Hash Verification
  ↓
Backend Adapter Construction
  ↓
Inference Service
  ↓
Conversation／Presentation／Summary Service
```

Composition RootだけがConcrete Adapterを知る。Use CaseおよびDomain ContractはConcrete BackendをImportしない。

## 15. Configuration Contract

### 15.1 Application Config

```text
application_schema_version
application_key
selected_model
load
generation
response
presentation
future component switches
```

Current主なField：

```text
load.context_size
load.batch_size
load.micro_batch_size
load.threads
load.threads_batch
load.gpu_layers
load.use_mmap
load.use_mlock
load.verify_artifact_hash

generation.max_new_tokens
generation.temperature
generation.top_p
generation.top_k
generation.min_p
generation.presence_penalty
generation.frequency_penalty
generation.repeat_penalty
generation.seed
generation.stop_sequences
generation.thinking_mode

response.language

presentation.thinking.visibility
presentation.thinking.display_label
presentation.thinking.persistence
```

### 15.2 Deployment Profile

```text
host:
  operating_system_key
  architecture_key
  execution_environment_key
  distribution_key

compute:
  compute_kind_key
  vendor_key
  acceleration_api_key
  memory_topology_key
  device_selector
  offload_policy_key

backend_runtime:
  backend_key
  required_version
  build_variant_key
  execution_mode_key

runtime_requirements:
  required_capabilities
  required_device_kind
  required_acceleration_api
  fallback_policy
```

Profile Resolutionは明示指定、Environment Hint、Platform Defaultの順で行う。対象PlatformにDefaultがなければErrorとし、macOS Profileへ暗黙Fallbackしない。

### 15.3 Model Registry

```text
model_key
role
distribution_repository
upstream_model
revision
artifact_relative_path
artifact_sha512
format
quantization
architecture
native_context_limit
declared_capabilities
output_protocol
```

File名は識別表示に使えるが、RoleやCapabilityの正本にしない。

## 16. Model Lifecycle

### 16.1 State

概念上のState：

```text
unloaded
loading
ready
generating
closing
closed
failed
```

### 16.2 Load

1. Model DefinitionをValidateする。
2. Model Root＋Relative PathからArtifactを解決する。
3. File存在、Sizeおよび必要時SHA-512を確認する。
4. Deployment RequirementとBackend Capabilityを照合する。
5. BackendへLoad Configを渡す。
6. Observed Metadata／Capabilityを取得する。
7. Declared／Observed／Requiredを照合する。
8. Runtime Infoを確定する。

途中失敗時にReady扱いしない。

### 16.3 Generate

1. RuntimeがReadyか確認する。
2. Concurrent Generation Lockを取得する。
3. Message、Generation Config、CapabilityをValidateする。
4. Model Output Protocolを選択する。
5. Streaming Sessionを開始する。
6. Cancellation Requestを監視する。
7. DeltaをReasoning／Final Channelへ分離する。
8. Stop Reason、Token Usage、Warningを確定する。
9. Lockを必ず解放する。

### 16.4 Cancel／Shutdown

- Stopは対象`request_id`だけをCancelする。
- New ChatはActive Generation／Summaryを停止してBrowser Stateを初期化する。
- Cross-thread Cancel後も次Requestを受理できる。
- ShutdownはActive SessionへCancelを要求し、Bounded Wait後にBackendをCloseする。
- CloseとShutdownは複数回呼ばれても安全にする。

## 17. Conversation Contract

### 17.1 Message

```text
role: system／user／assistant
content: non-empty text
```

Phase 1のHistoryはBrowserがRequestごとに送信する。Serverは永続Sessionを保持しない。

### 17.2 Generation Input

```text
request_id
messages
response_language
max_new_tokens
thinking_mode
thinking_visibility
summary_mode
optional generation overrides
```

Client生成`request_id`は空白を拒否し、Stop対象のCorrelationに使用する。

### 17.3 Conversation Event

最低限：

```text
started
delta
warning
completed
cancelled
error
```

Delta Channel：

```text
reasoning
final
```

Summaryを使用する場合、Original GenerationとSummary GenerationのStageをEvent Stateで区別する。

## 18. Web API Contract

### 18.1 Endpoints

```text
GET  /healthz
GET  /
GET  /api/v1/runtime
POST /api/v1/chat/stream
POST /api/v1/chat/stop
```

### 18.2 `/healthz`

- 認証外
- HTTP 200
- `{"status":"ok"}`相当の最小情報
- Model Path、Credential、Config、Internal Stateを返さない。

### 18.3 `/api/v1/runtime`

UI初期値とCapabilityを返す。

- Model／Profile表示
- Response Language Default
- Max New Tokens Default
- Thinking Control Availability
- Thinking Mode／Visibility／Label
- Summary Mode

Secret、Local Absolute Pathおよび不要な内部Metadataを返さない。

### 18.4 `/api/v1/chat/stream`

- SSE
- Content Type `text/event-stream`
- Bounded Queue
- Keepalive Comment
- Disconnect時Cancel
- Cleanup Timeout
- Concurrent Request拒否

Client Disconnect、Stop、New ChatまたはShutdownでProducerが残存しないことをTestする。

### 18.5 `/api/v1/chat/stop`

- `request_id`を受ける。
- Active Request一致時にCancellationを要求する。
- Cancellation完了を即時保証せず、受理状態を返す。
- 別Requestを誤停止しない。

## 19. Web Client State

```text
messages[]
ui_language
response_language
max_new_tokens
thinking_mode
thinking_visibility
summary_mode
active_request_id
active_abort_controller
runtime_defaults
```

### 19.1 New Chat

1. Active RequestがあればStop／Abortする。
2. User／Assistant Messageを消去する。
3. Runtime ModelはReloadしない。
4. 入力可能状態へ戻す。

### 19.2 Reload

- Conversation消去
- Response Language等はRuntime Defaultへ戻る。
- UI LanguageのみBrowser側保持を許容する。
- Server ModelはProcess継続中ならReloadしない。

### 19.3 Busy

別Tab等から同時Generationが来た場合：

- 先行Requestを継続する。
- 後続Requestを安全に拒否する。
- User向け`Modelは別のRequestを処理中`相当を表示する。
- 先行完了後は再送信可能にする。

## 20. Thinking Presentation Design

### 20.1 Control

```text
Generation OFF:
  Visibility Control disabled
  Reasoning Channelなし

Generation ON／Visibility Hidden:
  ModelはThinkingを生成可能
  ClientへReasoning Textを送らない
  Finalだけ表示

Generation ON／Visibility Visible:
  ReasoningとFinalを別領域に表示
```

### 20.2 Label

表示Labelの初期値は`高度推論`から変更候補があり、最終的には一般利用者が内部処理表示であると理解できるLabelを再評価する。Label変更はModel Delimiter変更ではない。

### 20.3 Token Limit

ReasoningだけでToken Budgetを消費し、Finalが空になる場合は専用Warningを返す。空Finalを正常回答と誤認しない。

## 21. Markdown／Copy Design

### 21.1 Rendering

```text
Streaming Delta
  → textContent

Completed Final
  → Markdown Parse
  → Sanitize
  → Safe DOM

Parse／Sanitize Failure
  → Plain Text
```

### 21.2 Copy

- User Copy：User Message本文
- Assistant Copy：Final Answer本文
- Reasoning：Copy対象外
- Hidden Original Answer：Copy対象外
- UI Label／Internal Error／Metadata：Copy対象外

将来Code Block単位Copyを追加する場合も、Final Answer全体Copyと別Buttonにする。

## 22. Summary Design

Summary Mode：

```text
off
post_generation
```

Current Summary Backend：

```text
same_main_model
```

Failure Policy：

```text
fallback_original
```

Summary Resultは空文字、Reasoningのみ、ErrorまたはCancelの場合に成功扱いしない。Summary中のStop／New Chat／ShutdownをOriginal Generationと同じCancellation契約で扱う。

## 23. Lightning Environment Design

### 23.1 Paths

```text
Workspace Root:
  /teamspace/studios/this_studio

Project Root:
  <workspace>/margpa-runtime-llm

Model Root:
  <workspace>/models

Environment:
  <project>/.venv

Pinned uv:
  <workspace>/.runtime-tools/uv/0.11.29/bin
```

絶対PathはLightning手順上のEnvironment例であり、Application CoreへHard-codeしない。

### 23.2 Setup／Verification

```text
scripts/setup/preflight_lightning_ai_studio.sh
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
scripts/setup/verify_phase1_environment.py
scripts/models/phase1f_cross_environment_acceptance.py
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

### 23.3 Basic Preview Lifecycle

```text
scripts/runtime/lightning/
├─ auto_start_preflight.sh
├─ basic_preview_common.sh
└─ basic_preview_service.sh
```

Action：

```text
preflight
run
start
status
restart
stop
```

Credential Source：

```text
MARGPA_WEB_AUTH_MODE=basic
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Credential値を出力せず、AvailabilityとSourceだけをRedacted表示する。

### 23.4 Runtime State

Project外のRuntime State DirectoryへPID、Logその他のLifecycle Evidenceを置く。Environment Overrideが空文字または不正Pathの場合に`/`や広いDirectoryへFallbackしない。

Stale PIDはProcess Identityを確認してCleanupする。PID再利用や無関係ProcessをStopしない。Cleanup失敗時はEvidenceを保持し、安全なForced Recovery手順へ戻す。

## 24. Documentation Lifecycle Design

### 24.1 Stable

Stable FileはTimestampなし。

```text
requirements_specification_ja.md
system_architecture_ja.md
technology_selection_ja.md
basic_design_ja.md
runtime_governance_specification_ja.md
project_continuity_master_ja.md
roadmap_ja.md
```

### 24.2 History

変更前後の完全原文を次形式で保持する。

```text
<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

同Phase内の複数更新に対応するためTimestampを必須とする。

### 24.3 Lossless

Phase Lossless Compilationは、Source本文をDelimiter付きで収録し、Path、Size、SHA-512を保持する。再抽出してHash一致できなければ失敗とする。

Phase 1-ex進行中のCompilationはInterimとして作成し、Phase完了後に正式版を再構築する。

## 25. Future Governance Component Design

### 25.1 Component Manifest

```text
component_id
component_type
version
enabled
mode
provider
capabilities
required_dependencies
optional_dependencies
conflicts
input_scope
output_scope
timeout
budget
failure_policy
audit_schema
```

### 25.2 Governance Definition Manifest

```text
package_id
definition_id
definition_version
domain
schema_id
source_uri
source_digest
adapter_id
compiler_id
activation_condition
required_capabilities
dependencies
conflicts
priority
bindings
```

ARGD／DAGDを含め、特定略称を必須FieldやEnumにしない。

## 26. External R&D Hook Design

```text
External Provider Manifest
  ↓
Generic Provider Port
  ↓
Capability／Version／Digest Validation
  ↓
Explicit Binding
  ↓
Optional Component／Governance Point
```

EASA、DLAGSAおよびOCILNSはPhase 10以降のProvider候補である。各Providerごとに独立Switchを持ち、OFF時にModule Import、Network Call、Storage WriteまたはAudit Side Effectを発生させない。

## 27. Current Deferred Design Items

- Persistent Conversation Storage
- Chat List／Resume／Regenerate／Branch
- Markdown Streaming Renderer
- Table Rendering
- Code Fence UI／Code-only Copy
- Folder Upload／Drag-and-drop
- Responsive／Mobile UI
- Component Switchboard UI
- Governance Platform
- Audit Writer
- Judge／Repair
- Documentation RAG
- General RAG
- Agent／Tool
- Anonymous Public Demo Policy
- Traffic-aware Wake実機成立
- Git Workflow
- EASA／DLAGSA／OCILNS Integration
