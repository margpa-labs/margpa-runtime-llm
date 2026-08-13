# Phase 2 Runtime Data Root／Recording Architecture

```yaml
document_id: phase_2_runtime_data_root_and_recording_architecture
status: accepted_design_direction_deferred_implementation
phase: phase_2
primary_target_subphase: phase_2_b
language: ja
created_at: 2026-08-14 00:46:46 JST
from_role: User／プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役／Phase 2実装者役
decision_authority: user
directory_created: false
runtime_data_write_enabled: false
recording_default: "off"
protected_research_capture_default: "off"
```

## 1. 目的

今後追加するConversation、RAG、Experiment、Evaluation、Evidence、Config Snapshotその他のRuntime Dataを、後から比較、検証、再現、移行およびBackupできる形で蓄積するため、Project内に一つの論理Data Rootを予約する。

現時点ではPC容量を優先し、Directory、Concrete Storage、実Data、Retention Jobまたは自動削除を作らない。Phase 2-B以降で必要なSchema、Port、HookおよびProfile Bindingを段階的に実装し、記録はDefault OFFとする。

## 2. Data Root Boundary

Project-local Default候補は次とする。

```text
margpa-runtime-llm/
└─ runtime_data/
```

`runtime_data/`は論理Defaultであり、CoreへAbsolute PathをHard-codeしない。Mac Local、Lightning、Home Server、Cloudまたは将来の外部Persistent Volumeで差替え可能なRoot Bindingを使う。

設定境界候補：

```text
MARGPA_RUNTIME_DATA_ROOT
```

名称はPhase 2-BのConfig Contractで最終確定する。Environment Variableを唯一の設定源へ固定せず、Profile／Config PortからEffective Rootを解決できる構造とする。

## 3. Logical Directory Layout

```text
runtime_data/
├─ persistent/
│  └─ <scope_id>/
│     ├─ conversations/
│     ├─ rag/
│     ├─ experiments/
│     ├─ evaluations/
│     ├─ evidence/
│     └─ config_snapshots/
├─ derived/
│  └─ <scope_id>/
│     ├─ indexes/
│     └─ cache/
├─ recovery/
│  ├─ checkpoints/
│  └─ migrations/
├─ exchange/
│  ├─ imports/
│  └─ exports/
└─ volatile/
   ├─ locks/
   ├─ logs/
   └─ temp/
```

本Layoutは論理分類である。全Directoryを先行作成せず、実装済み機能が必要とするものだけAdapterが作成する。単一巨大Directoryへ異なるLifecycle、秘密度および復元性のDataを混在させない。

## 4. Data Class Separation

### 4.1 Persistent

再起動後も維持し、Project機能または検証で正本となるDataを置く。

- Conversation／Session／Turn／Message
- Experiment RunとAccepted Result
- Evaluation Result
- Evidence Reference
- Config Snapshot
- 将来のRAG Source／Chunk Metadata

### 4.2 Derived

Persistent Sourceから再生成可能なDataを置く。

- Search Index
- Embedding Cache
- Projection Cache
- Presentation用派生Artifact

Derived DataをPrimary Recordまたは唯一のEvidenceにしない。

### 4.3 Recovery

Migration、Schema更新、RollbackまたはCrash Recoveryに必要なCheckpointとState Markerを置く。通常のRuntime Dataと混ぜず、作成、検証、Cutover、Retentionおよび削除を別Contractで扱う。

### 4.4 Exchange

明示的なImport／Exportだけに使用する。External送信Authorityを生成せず、Project内へFileを作ったことを公開、Uploadまたは共有許可と解釈しない。

### 4.5 Volatile

Lock、Temporary Stateおよび再生成可能なRuntime Logを置く。Process Crash後に残存し得るため、単にTemporaryという名称だけで安全な自動削除対象にしない。

## 5. Scope Isolation

全Persistence Operationは`scope_id`と対象Identityを組にして扱う。Conversation ID、Directory名、Browser Session、Basic Auth共通Credentialまたは推測困難なIDだけをAuthorization Boundaryにしない。

少なくとも次のSurfaceを黙って同一Scopeへ統合しない。

- Local Private Runtime
- Basic Preview
- Public Demo
- Research／Developer Environment
- Test／Fixture

安全な所有／Scope Contractが成立していないProfileは、Persistence Adapter未BindingかつZero WriteをDefaultとする。Public DemoとShared Basic Previewへ個人Conversation Listを先行接続しない。

## 6. Model Artifact Boundary

GGUF、SafeTensorsその他の巨大Model Artifact本体はRuntime Data Rootへ複製しない。Model Root／Registryを別境界として維持し、Runtime Data側には検証に必要な次のMetadataだけを参照保存できる。

- Model Key／Version
- Adapter／Backend
- Artifact Digest
- Effective Config Digest
- Load／Runtime Profile
- Provenance Reference

## 7. Feature ModeとRecording Modeの分離

Governance、Evaluation、Guard、Judgeその他の介入可能Componentでは、機能の実行状態とData記録状態を直交させる。

```text
feature_mode:
  off
  observe
  enforce

recording_mode:
  off
  metadata
  full
```

### 7.1 Feature Mode

- `off`：対象機能を実行しない。
- `observe`：評価または判定するが、Main Runtimeの結果へ介入しない。
- `enforce`：Accepted AuthorityとPolicyの範囲内で判定結果をRuntimeへ反映する。

全機能へ機械的に同じ3値を強制しない。意味上`off／observe／enforce`が成立するComponentに適用し、別State Machineが必要なComponentはCapability Contractで表現する。

### 7.2 Recording Mode

- `off`：永続記録を行わない。
- `metadata`：ID、Digest、Mode、Config、時刻、Token、Latency、Outcome、Source Reference等に限定する。
- `full`：許可されたCanonical Input／Output、判定結果、ReferenceおよびMetadataを保存する。

`feature_mode=enforce`であることは`recording_mode=full`を意味せず、`recording_mode=full`も実行Authorityまたは介入Authorityを生成しない。

## 8. Initial Implementation Policy

当面は次を標準とする。

```text
Schema／Port／Adapter Hook : implement incrementally
Physical Data Directory    : create only when required
feature_mode               : component-specific safe default
recording_mode             : off
protected research capture : off
automatic deletion         : disabled
```

最初から全機能の実Dataを保存しない。容量、出力内容、安全性および検証価値を観測した後、機能単位、Profile単位およびScope単位で`metadata`または`full`を明示的に有効化する。

## 9. Verification Metadata

後から同じ条件を比較または再現できるよう、記録を有効化したRunでは必要に応じて次を保持する。

- `experiment_id`／`run_id`
- Conversation／Session／Turn／Request Identity
- Feature Mode／Recording Mode
- Model／Artifact／Adapter Digest
- Effective Config／Source／Digest
- Component／Definition／Compiled Plan Digest
- Input／Canonical Output Digest
- Start／Finish Timestamp
- Token／Latency／Outcome／Failure Class
- Source／Citation／Evidence Reference
- Schema／Storage Format Version
- Parent／Baseline／Retry／Regenerate関係

Metadata Fieldを一つの巨大汎用Blobへ固定せず、共通EnvelopeとComponent固有Extensionを分離する。

## 10. Capacity／Retention／Failure Boundary

容量上限へ到達した場合、既存Dataを無通知で古い順に削除しない。Quota、警告、記録停止、Runtime継続可否、Retention、Archiveおよび明示削除は別Policyとして設計する。

記録失敗時のRuntime動作は機能とModeごとに分離する。

- 観測用記録の失敗を、常にModel生成失敗へ昇格させない。
- Evidence必須の`enforce`処理を、記録失敗後も成功扱いしない。
- 記録停止、Degraded ModeまたはFail-closedを、Component Contractで明示する。
- Partial WriteをComplete Recordとして扱わない。

BackupはSource Code BackupとRuntime Data Backupを分離できるようにする。GitへRuntime Data本体を含めず、Code、Schema、ManifestおよびTestだけを管理対象とする方針をPhase 2-Bで確定する。

## 11. Sensitive／Internal Data Boundary

通常の`recording_mode=full`でも、次は既定のConversation Messageまたは一般Evidenceへ保存しない。

- Raw Thinking
- Secret／Credential／Token
- Internal System Prompt
- Tool内部情報
- RAG Injected Internal Context
- Hidden Original
- 未確定Partial Output

これは将来の検証可能性を永久に禁止する決定ではない。通常Recordと分離した高Risk研究用Captureを、後続Phaseで再検討する。

## 12. Protected Research Capture Reservation

将来候補：

```text
protected_research_capture:
  off
  metadata_only
  restricted_full
```

現時点ではHookだけを予約し、Default OFF、実データ保存なしとする。`restricted_full`を有効化する前に、少なくとも次を別のSecurity／Governance Gateで確定する。

- 明示的なHuman Activationと対象Scope
- Local-only／External禁止境界
- Encryption at Rest／Key管理
- Role／Task／User Access Control
- Secret Detection／Redaction
- Data Minimization
- Retention／容量上限／停止条件
- Audit／Export／Delete／Recovery
- Consent、第三者Dataおよび法的条件
- 通常Conversation／Evidenceからの物理・論理分離

`restricted_full`は通常の`full`の上位値ではなく、別Capabilityと別Authorityを持つ。Feature Mode、Recording ModeまたはResearch／Developer ModeをONにしただけでは有効化しない。

## 13. Phase Allocation

```text
Phase 2-B:
  Data Root Binding
  Conversation Persistence Adapter
  Storage Envelope／Schema／Migration／Recovery
  Recording Port／Default OFF Hook

Phase 2-C:
  Persistent Conversation API／UI
  User-visible Storage／Resume／Error State

Phase 2-D:
  Recording Mode Control Surface
  Effective Config／Apply／Restart Boundary

Phase 2-E:
  Component Mode／Dependency／Conflict Switchboard
  RAG Follow-up Recording Boundary

Later Research／Governance Phases:
  Experiment／Evaluation／Evidence expansion
  Protected Research Capture reconsideration
  Retention／Audit／Export policy hardening
```

## 14. Accepted／Deferred／Not Authorized

### Accepted Design Direction

- Project内に論理`runtime_data/` Rootを設け、用途とLifecycleで細分化する。
- Physical Rootは差替え可能とし、Absolute PathをCoreへHard-codeしない。
- Feature ModeとRecording Modeを分離する。
- 当面のRecording DefaultはOFFとし、Port／Schema／Hookを先に用意する。
- Runtime Data、Derived Data、Recovery、ExchangeおよびVolatile Dataを分離する。
- 通常`full`とProtected Research Captureを分離する。

### Deferred

- Concrete Storage製品／形式
- Exact Config Key／Profile Binding
- Retention／Quota／Archive／Delete Policy
- Basic Preview／Public DemoのPersistent Scope
- Protected Research Captureの実装とActivation
- Raw Thinkingその他の高Risk Data保存

### Not Authorized by This Document

- `runtime_data/` Directoryの作成
- Runtime Dataの書込み開始
- `.gitignore`変更
- Existing Runtime／Web／Lightning Binding変更
- Secret／Raw Thinking／Internal Promptの保存
- External Storage／Cloud／Upload／Export
- 自動削除、MigrationまたはPermission変更

本書はPhase 2-B以降の設計入力であり、それ自体はSource、Filesystem、Git、External ServiceまたはRuntimeへのMutation Authorityを生成しない。
