# Phase 3 Architecture Decision Record

```yaml
document_id: phase_3_adr
status: proposed_for_user_acceptance
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
```

## ADR-3-001：Phase 3とPhase 4を分離する

### Decision

Phase 3はDefinitionをCompiled Planまで変換するが、PlanをGovernance PointやAction AdapterへBindingしない。全Planを`unbound／non_executable`とする。

### Reason

Definitionの存在、ValidationまたはCompileをAuthority、Activation、Enforcementと混同すると、Phase 3だけで未承認介入が成立するため。

## ADR-3-002：Governance Runtime初期値を`off`とする

### Decision

初期既定値は`off`とする。`observe`は明示Applyで有効化する。Phase 3の`enforce`はUnavailableであり、要求時にFail-closedとする。

### Reason

既存RuntimeをBaselineとして維持し、追加Cost、Evidence、Definition処理および将来の介入効果を比較可能にするため。未実装`enforce`を`observe`として代替するとMode比較が破壊される。

## ADR-3-003：Audit ModeとGovernance Modeを同一概念にしない

### Decision

Governanceは`off／observe／enforce`、Evidence Recordingは別Capabilityとして扱う。Phase 3のGovernance `observe`はMetadata Evidenceを必要とするが、将来の一般Recording `off／metadata／full`を置換しない。

### Reason

全機能へ同じ三状態を機械的にHard-codeせず、機能本体、Governance BindingおよびRecording Capabilityを分離するため。

## ADR-3-004：Manifest-firstとする

### Decision

Filesystem Providerは明示Manifestだけを入口とし、Directory ScanやFilename Inferenceをしない。

### Reason

現在のDefinition Sourceは複数Schema、複数Logical Definition／一File、および異なるArchetypeを含む。File名やKeyだけではTrusted Interpretationを証明できない。

## ADR-3-005：Reference Bundle固有AdapterをCore外へ隔離する

### Decision

ARGD／DAGD Combined、CDOGDおよびCommon Domain Extension用Adapterを、Generic Core外のTrusted Adapter Pluginとして実装する。

### Reason

既知略称と現行件数をCoreへ埋め込まず、将来のUnknown／Custom DefinitionをCore変更なしで追加するため。

## ADR-3-006：Source JSONを原則Immutable Inputとして扱う

### Decision

現行DefinitionはManifestとDigestで包み、黙って整形・補完・正規化しない。必要な修正はVersionまたは明示Correctionとして扱う。

### Reason

ユーザーはSource編集を許可しているが、技術的に編集可能であることと、Provenanceを壊すSilent Rewriteは別である。既に公開済みのSourceとの差分検証可能性を維持する。

## ADR-3-007：EvidenceはMetadata Allowlistを初期実装とする

### Decision

Phase 3ではFull Prompt、Output、Thinking、System Prompt、SecretおよびHidden Artifactを保存しない。Event KindごとのTyped MetadataだけをAppendする。

### Reason

検証性を得ながらPrivacy／Security Riskを限定し、将来のProtected Captureを別設計として追加できるようにする。

## ADR-3-008：Local JSONLを初期Evidence Adapterとする

### Decision

Evidence Portの初期Adapterは、`runtime_data/`配下のLocal Append-only JSONLとする。Conversation SQLiteへ混在させない。

### Reason

Human-readable、Diff可能、Recovery試験可能な最小実装であり、将来のSQLite、Ledger、WORMまたはOCILNS Adapterへ交換できる。

## ADR-3-009：Observeは非介入Subscriberとする

### Decision

Observe Hookを既存GenerationのEvent Subscriberとして接続し、Model Input／Output、SSE Terminal、Conversation CommitまたはCancel Authorityを所有させない。

### Reason

Evidence FailureやDefinition Failureで既存Generationを壊さず、Phase 3にEnforcement責務を持ち込まないため。

## ADR-3-010：Enforce UIを隠蔽せずUnavailable表示する

### Decision

Settingsには三Modeを表示するが、Phase 3の`enforce`をUnavailable Reason付きで無効化する。API要求もUnsupportedとする。

### Reason

最終形を先に示しながら、未実装機能を動作済みと誤認させず、Silent Downgradeを防ぐため。

## ADR-3-011：Phase規模Claude実行を有界化する

### Decision

Claude CodeはPhase 3-0～3-GをMaterial Work Unit単位で連結できるが、Phase 3-H、Git、Backup、Root外、Provider Memoryおよび最終完了宣言を行わない。

### Reason

Phase規模Automation／Cross-provider／Compaction Recoveryを実験しつつ、人間専用Gateと不可逆境界を維持するため。

## ADR-3-012：Work Unitは細かくするがArtifactを固定増殖させない

### Decision

一Work Unitを一つの意味あるDesign／Implementation／Review境界にする。各Commandや微修正ごとにIndex／Handoff／Statusを作らない。Compaction Recoveryに必要なCurrent StateとEvidenceだけをMaterial Boundaryで作る。

### Reason

Claude Auto-Compactionからの復旧性と、File数、Storage、Context、Review Costの両方を最適化するため。

## ADR-3-013：Phase 3のRuntime対象はMac Localとする

### Decision

初期BindingはLocal／Loopback／Auth-disabled／Explicit opt-inに限定し、Public／Basic／LightningではGovernance Control、Definition LoadおよびEvidence WriteをBindingしない。

### Reason

Private EvidenceとDefinition Controlを共有認証または匿名環境へ持ち込まず、Lightning反映をPhase 3または4後の別Gateへ維持するため。

## Acceptance State

本ADRは提案状態である。ユーザーAcceptanceとPhase 3開始Gate成立前に、実装Authorityを生成しない。
