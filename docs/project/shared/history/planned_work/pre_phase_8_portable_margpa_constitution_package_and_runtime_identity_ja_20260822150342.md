# Pre-Phase 8 Portable MARGPA Constitution Package／Runtime Identity 予約

```yaml
document_id: pre_phase_8_portable_margpa_constitution_package_and_runtime_identity_20260822150342
status: planned_not_started_not_authorized
document_type: append_only_planned_work
target_phase: pre_phase_8_constitution_gate
recorded_at: 2026-08-22 15:03:42 JST
implementation_authorized: false
```

## 1. Purpose

Phase 8でAgent／Toolを本格導入する前に、Phase 1-ex以降に蓄積した絶対禁止、Authority、Docs、Mutation、Handoff、Review、Recovery、Backup、Git、Cost、停止条件、Incident、Near Miss、AutomationおよびCross-provider EvidenceをLosslessに再編成し、Portableな統合憲法／制度Packageへ昇格する。

既存Roadmapの`docs/project/shared/constitution/`案を維持しつつ、Runtime、Agent、Toolおよび他Projectから参照する正本Packageは、場合によってProject Root直下の独立Folderへ配置することを検討する。

## 2. DocsとRuntime Packageの分離

既存Docsを一括MoveしてHistory／Link／Evidenceを破壊しない。

推奨責務：

```text
docs/project/shared/constitution/
  設計、説明、編纂Evidence、History、Review、Migration記録

<project-root>/<constitution-package>/
  Accepted Normative Core
  Canonical Manifest
  Rule Schema／Rule ID
  Role View Schema
  Provider Adapter Contract
  Machine-readable Enforcement Input
```

Exact Root Folder名はPhase 8 Gateで決定する。候補は`margpa_constitution/`、`governance_constitution/`等とし、特定Project名、Provider、Absolute Path、PhaseまたはTaskをNormative CoreへHard-codeしない。

「DocsからRootへ移動」は、単純なFile Moveではなく、Approved RevisionをPortable PackageへPromote／Compileし、旧Docs HistoryとTraceabilityを保持するMigrationとして扱う。

## 3. MARGPA-like Runtime Component

統合憲法を単なる注意書きではなく、MARGPA Governance Definitionsと同様にIdentity、Revision、Digest、ModeおよびBinding Stateを持つRuntime Component候補として扱う。

```text
component_role      : development_governance_constitution
safe_display_name   : MARGPA Constitution <revision>
revision            : accepted revision
manifest_digest     : canonical SHA-512
mode                : off／observe／enforce candidate
binding_state       : none／active／unavailable／invalid／degraded
provider_view       : Codex／Claude／future provider adapter
```

正式な名称、Version体系およびMode名はPhase 8でFreezeする。`MARGPA Constitution v0.x`等は候補であり、現時点の固定名称ではない。

## 4. Advanced Settings Reservation

Phase 8以降、Advanced SettingsのAI Components／Governance情報へ次を表示する候補とする。

```text
Current Development Governance Constitution
Constitution Revision
Constitution Mode
Role／Provider View
Binding／Validation State
```

表示例：

```text
MARGPA Constitution v0.x · Observe
None
Unavailable
Invalid revision／digest
```

- Package不存在は`None`。
- Required Package欠落、Stale Revision、Digest不一致またはRule Conflictは`Unavailable／Invalid`としてFail-closedする。
- Packageの存在またはUI表示だけでAgent／Tool Authorityを生成しない。
- Constitution Mode OFFを`allow all`と解釈しない。
- Agent／Tool個別Mode、Platform Sandbox、Permission、Human ApprovalおよびExternal Authorityを独立維持する。

## 5. Portability Requirements

- Root PackageとProject Manifestを別Projectへ配置し、Project固有値だけをManifest／Adapterで与えられる。
- Codex Desktop、Claude Codeおよび将来Providerの差をProvider Adapterへ隔離する。
- Normative CoreへTool名、UI名、Absolute Path、CommandまたはProvider MemoryをHard-codeしない。
- Role／Phase／Task別Constitution Viewは同じAccepted Revisionから導出する。
- ViewはAuthorityを追加できず、Source Revision／DigestへTrace可能とする。
- Humanだけが最上位規則群の追加、削除、編集または正式Exceptionを承認できる。
- Agent／Toolは違反、Conflict、Missing RuleまたはStale StateをEvidence化し、許可を自己生成しない。

## 6. Pre-Phase 8 Work

1. Existing Rule／Evidence CorpusをLossless Inventory化する。
2. 重複、Conflict、古い規則、Normative／Descriptive／Historicalを分類する。
3. Human-only Top-level Rulesと下位運用規則を分離する。
4. Canonical Index、章別Rule、Rule ID、Schema、Manifest、Role View、Provider Adapterを設計する。
5. `docs/project/shared/constitution/`とRoot Runtime Packageの責務をFreezeする。
6. Migration／Promotion／Rollback／Digest／Stale Detectionを定義する。
7. Advanced SettingsのIdentity／Mode／State Projectionを設計する。
8. Constitution OFF／OBSERVE／ENFORCE候補の比較Testを作成する。
9. Agent／Tool開始Gateを満たした後だけPhase 8本実装へ進む。

## 7. Non-Authorization

本書は予約であり、既存Rule／DocsのMove、Constitution Folder／Runtime Package作成、Agent／Tool開始、Authority変更、Source／Frontend変更、Git／GitHubまたは外部操作を許可しない。

