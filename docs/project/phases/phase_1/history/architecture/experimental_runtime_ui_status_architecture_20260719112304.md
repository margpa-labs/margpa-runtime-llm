# Experimental Runtime・UI・Status Architecture

- 文書ID: `experimental_runtime_ui_status_architecture`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 2 Component Control／Experiment／Event／Status、Phase 4 UI／Config
- 正本言語: 日本語
- 上位要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規Architecture系列）

## 1. Architecture Goal

本Architectureは、次の4つを同じTyped Runtime Modelから駆動する。

1. ComponentとGovernance BindingのON／OFF／Mode
2. 実験Profileと再現可能なRun Record
3. Event-driven Runtime Status／Observability
4. 一般UIと開発・研究設定

UIが独自の設定意味を持たず、CLI、API、Experiment Runner、UIが同一のConfig ContractとEffective Configを使用する。

## 2. High-level Flow

```text
Tracked Defaults              Deployment Profile
config/application.toml       config/profiles/*.toml
          └───────────────┬───────────────┘
                         ↓
                  Typed Config Composer
                         ↑
          Local Runtime Override／Experiment Profile
                         ↓
                   Effective Runtime Config
                         ↓
       Component Registry／Dependency Validator
                         ↓
                   Runtime Execution Plan
                         ↓
        Components + Governance Bindings + Events
                         ↓
      Status Projection／Audit／Experiment Run Record
```

## 3. Component Registry

### 3.1 Component Descriptor

```text
component_id
component_kind
display_name
enabled_by_default
required_for_operations[]
required_capabilities[]
provided_capabilities[]
required_dependencies[]
optional_dependencies[]
conflicts[]
degraded_modes[]
side_effect_level
apply_mode
governance_point_ids[]
```

`component_kind`はUI Groupingに利用できるが、未知Componentを追加できるExtensible Valueとする。

### 3.2 Component Configuration

```toml
[components.main_model]
enabled = true

[components.main_model.governance]
mode = "off"

[components.guard]
enabled = false

[components.guard.governance]
mode = "off"

[components.judge]
enabled = false

[components.judge.governance]
mode = "off"

[components.repair]
enabled = false

[components.agent]
enabled = false

[components.agent.governance]
mode = "off"
```

Boolean `enabled`とGovernance `mode`は別の意味を持つ。Functional Componentを無効化しただけで、そのComponentの統治が別Componentへ横流しない。

### 3.3 Validation Result

```text
valid
valid_with_warnings
degraded
invalid
```

Validation Issueは次を持つ。

```text
issue_id
severity
component_id
binding_id
configuration_path
reason
required_action
apply_mode
```

### 3.4 Invalid Combination例

| 構成 | 判定 |
|---|---|
| Main Model OFFでChat実行 | Invalid／Execution Refusal |
| Agent OFF + Agent Governance Observe／Enforce | Invalid（Pointの対象がない） |
| Judge OFF + JudgeだけをTriggerにするRepair ON | Invalid |
| Judge OFF + Rule Audit Triggerを持つRepair ON | Valid／Configured Degraded可 |
| Tool Permission Resolver OFF + Tool ON | Invalid／Tool Refusal |
| Status Projection OFF | Valid／Lifecycleは維持、表示のみ無効 |
| Audit Sink OFF + High-assurance Experiment | Profile PolicyによりInvalid可 |

## 4. Runtime Apply Mode

Configフィールドごとに次を持つ。

| Apply Mode | 例 |
|---|---|
| `immediate` | Status verbosity、UI表示 |
| `next_request` | Temperature、Max New Tokens、Governance Mode |
| `model_reload` | Context Size、GPU Layers、Model Selection |
| `application_restart` | Provider Plugin、Adapter Plugin、一部Deployment Setting |

UIとCLIは変更の適用時期を事前に表示する。

## 5. Experiment Runtime

### 5.1 Experiment Profile

Experiment Profileは、再利用可能なConfig Overlayと記録Policyを持つ。

```toml
[experiment]
profile = "baseline_empty_governance"
record_inputs = true
record_outputs = true
record_events = true
fixed_seed = 42
```

### 5.2 初期Profile

| Profile | 意味 |
|---|---|
| `baseline_no_governance` | Governance Subsystem自体を使わないBaseline |
| `baseline_empty_governance` | Governance PortはあるがDefinition 0件 |
| `main_governance_observe` | Main Governance判定とLogのみ |
| `main_governance_enforce` | Main Governance介入あり |
| `guard_judge_repair` | 安全・評価・修復構成 |
| `all_implemented_layers` | その時点の全実装Componentを有効化 |

Profile名は実効Configを代替しない。Runごとに必ずEffective Config Snapshot／Hashを保存する。

### 5.3 Run Identity

```text
experiment_id : 論理的な実験単位
run_id        : 1回の実行
request_id    : Inference Request
session_id    : Conversation Session
turn_id       : Conversation Turn
```

これらを同一IDに潰さず、一対多の関係を保持する。

### 5.4 Run Record

```text
identity
  experiment_id, run_id, request_id, session_id, turn_id

artifacts
  model_id, model_file, model_digest, quantization
  definition_refs, definition_digests, adjustment_digest
  compiler_version, plan_digest

configuration
  profile, effective_config, effective_config_digest
  source_map, enabled_components, governance_modes, seed

execution
  input, output, token_counts, latency, stop_reason
  event_refs, tool_calls, retrieval_refs

evaluation
  audit, score, deviations, severity
  judge_result, repair_count, retry_count

terminal
  status, warnings, errors, completed_at
```

## 6. Runtime Event Contract

### 6.1 Event Envelope

```text
event_id
event_schema_version
event_type
timestamp
sequence
experiment_id
run_id
request_id
session_id
turn_id
component_id
point_id
correlation_id
causation_id
payload
severity
```

### 6.2 Event Category

```text
runtime.request_received
runtime.preparing
component.started
component.completed
component.skipped
component.failed
governance.started
governance.observed
governance.enforced
governance.completed
model.loading
model.generating
model.cancelled
guard.completed
judge.completed
repair.started
repair.completed
agent.step
tool.requested
tool.completed
turn.completed
turn.failed
```

Event Typeも拡張可能にする。Unknown EventでProjection全体をCrashさせない。

## 7. Runtime Status Projection

### 7.1 責務

- Event Streamから現在のRuntime StatusをProjectionする。
- CLI、WebSocket／SSE、Web UI、Auditが別々のStatus Logicを持たないようにする。
- Projection FailureはInference Failureに伝播させない。
- 欠落EventやOut-of-orderをWarningとして扱える。

### 7.2 Projection Model

```text
overall_state
current_component
current_point
governance_state
progress_label
attempt
repair_count
warning_count
error_count
started_at
elapsed_ms
last_event_at
```

### 7.3 Lifecycleと表示の分離

Runtime CoreがCancel、Complete、Failureを正しく扱うためのLifecycle Stateは必須である。一方、Status UI、詳細Projection、永続化は任意Componentとする。

### 7.4 DAGD Statusとの区別

- Runtime Status: 全Pipelineの実行状態
- Governance Status: 特定Binding／Point／Definitionの統治状態
- DAGD Status Reporter: DAGD Definitionの意味上のStatus Reporting

三者の名前空間とSchemaを分ける。

## 8. Minimal Audit in Phase 2-C

Phase 2-Cは完全なGovernance Auditの前に、次をJSON／JSONL Append-Onlyで保存する。

- Run／Request Identity
- Effective Config Snapshot／Source／Digest
- Model Identity／Artifact Digest
- Component Switch／Governance Mode
- Runtime Event
- Input／Output
- Token／Latency／Stop／Error
- Canonicalization Version
- SHA-512 Integrity

完全なTurn Audit Schema、Hash Chain／HMAC／Signatureは後続Phaseで強化する。

## 9. Configuration Source Model

### 9.1 Source Layer

```text
Built-in Defaults
  < Tracked Application Config
  < Deployment Profile
  < Experiment Profile
  < Local Runtime Override
  < Environment
  < Explicit Request／CLI
```

ただし、すべてをGeneric Deep Mergeしない。Field Owner、Allowed Override Source、Apply ModeをTyped Schemaで決定する。

### 9.2 Source Map

Effective Fieldごとに次を返す。

```text
field_path
effective_value
source
source_location
apply_mode
validation_state
```

Secret、Credential、個人情報はSource MapにRaw Valueを記録しない。

## 10. Typed Config Service

### 10.1 Public Operations

```text
get_schema()
get_effective_config()
get_source_map()
validate_patch(patch)
preview_patch(patch)
save_local_override(patch, expected_revision)
reset_local_override(scope)
export_profile(scope)
import_profile(document)
```

### 10.2 Preview Result

```text
validity
issues[]
before_digest
after_digest
diff[]
source_changes[]
apply_modes[]
required_actions[]
```

### 10.3 Save

- UIはTracked Defaultを書き換えない。
- Local OverrideはGit Ignore対象とする。
- Temporary File + `fsync`相当 + Atomic Replace等の安全な保存を使う。
- Revision／DigestでLost Updateを防止する。
- Invalid Configを現在のEffective Runtimeへ適用しない。

## 11. UI Information Architecture

### 11.1 Basic UI

```text
Chat
  ├─ New Chat
  ├─ History／Resume
  ├─ Main Model
  ├─ Response Language
  ├─ Input／Generate／Stop／Regenerate
  └─ Simple Runtime Status
```

一般利用者にGovernance Definition Hash、Top-p、Point Binding、Action Resolverを常時表示しない。

### 11.2 開発・研究設定

```text
開発・研究設定
  ├─ Generation
  ├─ Model Runtime
  ├─ Component Structure
  ├─ Governance
  │    ├─ Repository State
  │    ├─ Definition／Package／Digest
  │    ├─ Point／Binding／Mode
  │    └─ Adjustment／Budget
  ├─ Evaluation／Repair
  ├─ Agent／Tool
  ├─ Experiment
  ├─ Status／Audit
  └─ Deployment
```

### 11.3 Governance Editor Boundary

- Immutable Definition SourceをUIから変更しない。
- Package／DefinitionのActive State、Binding、Mode、Adjustment Profileを操作対象にする。
- Unsupported／Invalid／Quarantinedの理由を表示する。
- Definition 0件を「読み込み失敗」と表示しない。

## 12. API Boundary

Phase 4のWeb UIは次のApplication APIのみに依存する。

```text
Conversation Service
Generation Service
Model Catalog Service
Typed Config Service
Component Registry Service
Experiment Service
Runtime Status Service
Audit Query／Export Service
```

UIからFilesystem、Model Adapter、Definition Providerを直接呼ばない。

## 13. Streaming

- Generation Token StreamとRuntime Event Streamは別Channelまたは識別可能なEnvelopeにする。
- Thinking PresentationのRaw／Display分離を崩さない。
- Guard／GovernanceによるStream StopはTerminal EventとStop Reasonを残す。
- Status表示の遅延でToken GenerationをBlockしない。

## 14. Phase Allocation

### Phase 2-A

- Component Registry
- Descriptor／Capability／Dependency
- Governance Mode Contract
- Point／Binding Hook
- Effective Switch Validation

### Phase 2-B

- Experiment Profile
- Experiment／Run Identity
- Effective Config Snapshot／Digest
- Baseline Profiles

### Phase 2-C

- Event Envelope
- Lifecycle Events
- Runtime Status Projection
- Minimal JSON／JSONL Audit
- SHA-512

### Phase 4

- API
- Conversation／History
- Web UI
- Typed Config Service
- Local Override
- 開発・研究設定
- Status／Experiment UI

## 15. Test Strategy

### 15.1 Registry

- Required／Optional Dependency
- Conflict
- Degraded
- Unknown Component
- Custom Component ID
- Apply Mode
- Invalid Combination

### 15.2 Experiment

- Profile名とEffective Configの分離
- Same Input／Seed／Model／ConfigのRecord一致
- Digest変更検出
- Incomplete／Cancelled／Failed Run

### 15.3 Event／Status

- Ordered／Out-of-order／Duplicate Event
- Unknown Event Type
- Projector FailureでInference継続
- Cancel／Repair／Retry
- Multiple Session

### 15.4 Config／UI

- Schema Validation
- Previewと実適用の同値性
- Atomic Save
- Revision Conflict
- Secret Redaction
- Apply Mode表示
- Basic UIからAdvanced Fieldがノイズにならない

## 16. 未決事項

- UI Framework（FastAPI + Vanilla JS／React等）
- Runtime Event Transport（In-process Bus／SSE／WebSocket）
- Local Overrideの正式Path
- Override FileのEncryption必要性
- Experiment RecordとTurn AuditのPhysical Storage分離
- Status Historyの保持期間
- Hot Reload可能なFieldの最終一覧

## 17. Authorization Boundary

本ArchitectureはAcceptedであるが、Phase 2／4のSource、Config、UI、Storageの実装は未解禁である。
