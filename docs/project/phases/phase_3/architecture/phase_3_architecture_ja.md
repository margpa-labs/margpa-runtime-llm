# Phase 3 Audit／Evidence／Generic Governance Definition Platform Architecture

```yaml
document_id: phase_3_architecture
status: design_candidate
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
```

## 1. Architecture Summary

```text
Explicit Runtime Configuration
  ├─ governance.mode = off | observe | enforce
  ├─ provider binding
  └─ evidence binding
          │
          ▼
Governance Definition Source
  → Provider
  → Package Manifest／Source Envelope
  → Package／Definition Repository State
  → Trusted Adapter Registry
  → Normalized Governance IR
  → Compiler
  → Unbound Compiled Plan
  → Phase 4 Governance Binding（Phase 3では未接続）

Existing Runtime Event
  → Non-intervening Observation Port
  → Safe Audit Event
  → Canonicalizer
  → Append-only Evidence Port
  → Local JSONL Adapter
  → Status Projection
```

Definition PipelineとEvidence Pipelineは疎結合であり、片方の失敗を他方の成功へ偽装しない。

## 2. Package Layout

実装時の推奨境界は次である。Coreへ既知Definition名を入れない。

```text
src/margpa_runtime_llm/
├─ modules/
│  ├─ audit_evidence/
│  │  ├─ contracts.py
│  │  ├─ identities.py
│  │  ├─ canonicalization.py
│  │  ├─ application.py
│  │  ├─ ports.py
│  │  └─ public.py
│  └─ governance_definitions/
│     ├─ contracts.py
│     ├─ repository.py
│     ├─ normalized_ir.py
│     ├─ compiler.py
│     ├─ application.py
│     ├─ ports.py
│     └─ public.py
├─ adapters/
│  ├─ audit_evidence/
│  │  └─ local_jsonl_store.py
│  └─ governance_definitions/
│     ├─ empty_provider.py
│     ├─ filesystem_provider.py
│     ├─ reference_bundle_adapters.py
│     └─ manifest_loader.py
├─ bootstrap/
│  ├─ audit_evidence.py
│  └─ governance_definitions.py
└─ web/
   └─ governance_routes.py

definitions/
├─ manifest.jsonまたはmanifests/<package>.json
├─ core_governance/
├─ orchestration/
└─ domain_extensions/

tests/
├─ unit/audit_evidence/
├─ unit/governance_definitions/
├─ integration/audit_evidence/
├─ integration/governance_definitions/
└─ integration/web/
```

実際のFile単位は、各Work Unit開始時に現行Sourceへ合わせてExact Mutation ManifestでFreezeする。上記は責務境界であり、全Fileを機械的に必須生成する固定Packageではない。

## 3. Identity Model

### 3.1 Independent Identity

```text
AuditRunId          : 一つのProcess／Runtime Observation期間
AuditEventId        : 一つのImmutable Event
GenerationRequestId : 既存Generation Attempt相関
ConversationId      : 永続Conversation
ConversationSessionId
TurnId
DefinitionPackageId
DefinitionId
DefinitionSourceId
NormalizedIrId
CompiledPlanId
EvidenceReceiptId
```

各IDはTyped Opaque Stringとし、別種ID間の暗黙変換を禁止する。Source DigestやPlan DigestをIDそのものとして再利用せず、IdentityとIntegrityを分離する。

### 3.2 Correlation

Audit Eventは、存在するIdentityへのOptional Referenceを持つ。関連対象が存在しない場合、別Identityから推測生成しない。

## 4. Evidence Architecture

### 4.1 Event Envelope

```text
AuditEventEnvelope
  schema_version
  canonicalization_version
  event_id
  run_id
  occurred_at_utc
  source_component
  event_kind
  correlation_refs
  subject_refs
  safe_payload
  provenance
  event_digest_sha512
```

`safe_payload`はEvent KindごとのTyped Allowlistである。任意DictへRaw Runtime ObjectをDumpしない。

### 4.2 Event Kind

Phase 3の最小Event Kindは次とする。

- `runtime_started／runtime_stopped`
- `generation_started／generation_terminal`
- `definition_provider_resolved`
- `definition_source_loaded`
- `definition_validated／definition_rejected`
- `definition_normalized`
- `governance_plan_compiled`
- `governance_mode_changed`
- `audit_write_degraded`

Phase 4以降の`governance_point_started`、Deviation、Action、Repairは予約し、Phase 3で実行済みEventを捏造しない。

### 4.3 Canonicalization

- UTF-8。
- JSON Object KeyをLexicographic Sort。
- Separatorは`,`と`:`。
- NaN／Infinityを拒否。
- TimestampはUTCで正規化。
- Enumは明示String。
- Digest Field自身をDigest Inputから除外。
- Schema VersionとCanonicalization Versionを独立管理。

### 4.4 Local JSONL Store

```text
runtime_data/
└─ audit_evidence/
   └─ <scope>/
      ├─ store_metadata.json
      ├─ segments/
      │  └─ <segment_id>.jsonl
      └─ receipts/
```

RootとScopeはServer側が解決する。User入力から任意Pathを作らない。Evidence StoreはConversation SQLiteと別Adapter／別Schema／別Lifecycleとする。

一件のAppendは、Canonical Event作成、Digest計算、Exclusive Append、Flush／必要時fsync、Receipt返却の順とする。Crashで末尾にPartial Lineがある場合、そのSegmentを`degraded_tail`として扱い、自動切詰めしない。Valid PrefixのReadはPolicyで許可できるが、破損末尾をValid Eventとして返さない。

### 4.5 Failure Policy

Phase 3 Observeでは、Evidence Write FailureをModel出力停止へ変換しない。Runtime Statusを`degraded`にし、安全なError Codeを返す。Fail-closed Evidence Profileは将来予約であり、Phase 3のDefaultではない。

## 5. Definition Source Architecture

### 5.1 Provider Contract

```text
DefinitionProviderPort
  describe() -> ProviderDescriptor
  load_package(request) -> PackageSourceResult
```

ProviderはSource差だけを隠蔽し、Schema解釈、IR変換、CompileまたはActivationを行わない。

`EmptyDefinitionProvider`は`empty`を正常に返す。Filesystem Providerは明示Root／Manifestだけを読む。Remote ProviderはPhase 3 Non-scopeである。

### 5.2 Manifest Contract

```text
PackageManifest
  manifest_format_version
  package_id
  package_version
  publisher
  license
  source_entries[]
  definition_entries[]
  dependencies[]
  signatures[]
  manifest_digest_sha512

SourceEntry
  source_id
  relative_path
  media_type
  byte_length
  content_digest_sha512
  schema_id
  trusted_adapter_id
  logical_definition_ids[]

DefinitionEntry
  definition_id
  definition_version
  display_name
  domain
  source_id
  source_object_pointer
  extension_archetype
  capability_kinds[]
  role_kinds[]
  activation_patterns[]
  governed_object_types[]
  non_targets[]
  dependencies[]
  conflicts[]
```

ManifestはMappingの正本だが、Runtime Authorityではない。Source File名やDirectory位置から欠落Fieldを推測しない。

### 5.3 Repository State

Provider、Package、Source、Definition、IR、Planは別Stateを持つ。

```text
Provider : not_configured | unavailable | empty | ready | failed
Package  : discovered | loaded | validated | invalid | quarantined | disabled
Source   : loaded | digest_mismatch | size_mismatch | invalid | unsupported
Definition: validated | unsupported | invalid | disabled | normalized
Plan     : compiled_unbound | stale | invalid | unavailable
```

`active`はPhase 3のCompiled Plan Stateとして使用しない。Phase 4 Binding後にだけ定義する。

### 5.4 Security Boundary

- Manifest Entry以外のDirectory Scanをしない。
- File名からSchema／Domain／Adapterを推測しない。
- Pathは`resolve`前後でRoot Containmentを確認する。
- Symlink、Device、FIFO、SocketおよびDirectoryをSourceとして拒否する。
- Byte SizeをParse前に検査する。
- JSON Parse後にDepth、Object数、Array長、String長を検査する。
- Unknown Adapter IDは`unsupported`。
- Adapter IDをModule PathとしてImportしない。
- Definition TextをPrompt、Shell、TemplateまたはCodeとして実行しない。

## 6. Trusted Adapter Architecture

### 6.1 Registry

```text
TrustedAdapterRegistry
  register(adapter_descriptor, adapter_instance)
  resolve(adapter_id, schema_id, source_media_type)
```

Duplicate、Version Conflict、Schema不一致およびCapability不一致をFail-closedとする。

### 6.2 Reference Bundle Adapter Classes

Reference Bundle用AdapterはGeneric Coreの外へ置く。

1. Combined ARGD／DAGD Adapter：一Sourceから二Logical Definitionを明示Object Pointerで抽出する。
2. CDOGD Adapter：Orchestration Definitionを変換するが、RoutingやActivationを実行しない。
3. Common Domain Extension Adapter：共通構造を持つ15 Definitionを変換する。Pipeline順序やWatchdog条件はManifest／IRに保持し、実行しない。

Definition IDの一覧や18件という件数をCoreへ固定しない。Reference BundleのManifestとContract Testだけが期待集合を所有する。

### 6.3 Normalized IR

IRはSourceの意味を完全表現できない場合、Loss Reportを必須にする。

```text
NormalizedGovernanceDefinition
  ir_schema_version
  ir_id
  identity
  source_provenance
  domain
  activation
  scopes
  conditions
  rules
  evaluators
  actions
  state_model
  evidence_requirements
  dependencies
  conflicts
  non_targets
  normalization_warnings
  unsupported_source_pointers
  ir_digest_sha512
```

Raw SourceはIRへ埋め込まない。Source DigestとPointerで参照する。

## 7. Compiler Architecture

### 7.1 Phase 3 Compiler

Phase 3 CompilerはDefinition Readinessを検証するDeterministic Compilerであり、Runtime介入を行わない。

```text
Compiler Input
  normalized_ir_refs
  profile
  binding_candidate
  runtime_capability_snapshot
  authority_snapshot

Compiler Output
  compiled_plan_id
  compiler_id／version
  source_definition_digests
  ir_digests
  selected_rule_refs
  selected_evaluator_refs
  selected_action_refs
  unresolved_dependencies
  conflicts
  warnings
  binding_state = unbound
  executable = false
  plan_digest_sha512
```

Action ReferenceがSourceに存在しても、Phase 3では実行AdapterをBindingしない。`executable=false`をPlan Digest対象へ含める。

### 7.2 Cache

CacheはProcess-local In-memoryを初期実装とする。永続Cacheは必須ではない。Cache HitでもPlan Digestを再検証し、Definition／IR／Compiler／Profile／Capability／Authority Snapshotが異なるEntryを使わない。

## 8. Mode Architecture

### 8.1 State

```text
GovernanceMode       : off | observe | enforce
ModeAvailability     : available | unavailable | denied
ModeApplyDisposition : runtime_applicable | restart_required | unsupported
```

Phase 3 Local Profile：

| Mode | Availability | Apply | Meaning |
|---|---|---|---|
| `off` | available | runtime_applicable | Governance固有処理なし |
| `observe` | available | runtime_applicable | 非介入のLoad／Validate／Compile／Evidence |
| `enforce` | unavailable | unsupported | Phase 4 Binding待ち |

### 8.2 Transition

```text
off → observe
  explicit apply
  provider resolution
  validation／compile
  state commit only after complete success or explicit degraded result

observe → off
  stop new governance observations
  clear process-local registry／plan cache
  retain existing append-only evidence

* → enforce
  Phase 3: reject unsupported／state unchanged
```

Observe開始時に一部DefinitionがInvalidでも、Package PolicyがPartial Acceptanceを許し、Valid EntryとInvalid Entryを区別できる場合はDegraded Observeを許可する。Manifest自体、Root BoundaryまたはTrusted Adapter RegistryがInvalidな場合はPackage全体をQuarantineする。

### 8.3 Configuration Integration

既存Configuration Controlへ`governance_mode`のTyped FieldとMode Descriptorを追加する。Config Revision／Digest／CAS／Preview／Applyを維持する。Tracked TOML、EnvironmentまたはCLIへUIから書き戻さない。

## 9. Runtime／Web Integration

### 9.1 Bootstrap

Local／Loopback／Auth-disabledかつExplicit Phase 3 Flag／ProfileでのみGovernance Controlを構築する。Public／BasicではServiceを構築せず、Route CallもDefinition ReadもEvidence Writeも0とする。

### 9.2 API

推奨Surface：

```text
GET  /api/v3/governance/runtime
GET  /api/v3/governance/definitions
GET  /api/v3/governance/plans
GET  /api/v3/governance/evidence/status
```

Mode Mutationは既存Configuration ControlのPreview／Applyへ統合する。API Responseは相対Source ID、Safe State、Count、DigestおよびSafe Reasonだけを返し、絶対Path、Source本文またはRaw Exceptionを返さない。

### 9.3 UI

Advanced SettingsへGovernance Sectionを追加する。

- Three-state Controlを表示。
- 初期`OFF`。
- `OBSERVE`選択可能。
- `ENFORCE`は表示するがDisabled、理由を明示。
- Current Mode、Provider／Package／Definition／Plan Count、Degraded／Invalid Count、Last Evidence Stateを表示。
- Apply前Preview、Revision／Digest CASおよびFailure時State不変を維持。

## 10. Existing Runtime Compatibility

- v1 Ephemeral API、v2 Persistent API、SSE Event名／順序を変更しない。
- Conversation DBとAudit Evidence Storeを分ける。
- Existing Citation EvidenceをAudit本文へ複写しない。Reference ID／Count等のAllowlistだけを記録可能にする。
- Model Adapter、Prompt、Thinking、Summary、RAG、ConversationのFunctional Outputを`off`で変更しない。
- `observe`でもModel Input／Outputを変更しない。
- Runtime CompositionへGovernance Definition PlatformをComponent Descriptorとして登録できるが、登録はAuthorityやActivationではない。

## 11. Reference Definition Bundle

現行`definitions/`は17 JSON Source、18 Logical Definitionである。既存Sourceは原則Immutable Inputとして扱い、Phase 3-A開始時にManifestとDigestで固定する。

Source修正が必要な場合は、次を満たす。

1. 修正前Digestと意味差分をEvidence化。
2. 同一VersionのSilent Rewriteを避け、新Versionまたは明示Correctionを使用。
3. Manifest、Size、Digest、Adapter ContractおよびTest Fixtureを同一Work Unitで更新。
4. Userが許可した`definitions/`以外へ原本を移動・複製しない。
5. `.DS_Store`等の非Manifest FileをProvider Sourceとして扱わず、無断削除しない。

## 12. Phase 4 Seam

Phase 3のOutputは、Phase 4が次を接続できる状態にする。

```text
Unbound Compiled Plan
  + Governance Point Binding
  + Runtime Capability
  + Policy／Authority State
  + Registered Action Adapter
  = Executable Governance Plan Candidate
```

Phase 3では右辺を成立させない。これがPhase 3とPhase 4の非交渉境界である。
