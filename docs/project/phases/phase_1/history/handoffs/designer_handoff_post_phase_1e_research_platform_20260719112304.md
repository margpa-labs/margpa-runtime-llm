# Phase 1-E後 AI実験・Governance Platform 実装担当Handoff

- 文書ID: `designer_handoff_post_phase_1e_research_platform`
- 状態: `planning_handoff_implementation_not_authorized`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- 最新Roadmap: [implementation_roadmap_20260719112304.md](../architecture/implementation_roadmap_20260719112304.md)
- supersedes: なし（Phase 1-E後新規Handoff系列）

## 1. 最重要な状態

本Handoffは、Phase 1-E完了後の実装担当へ向けた計画・境界の共有文書である。

```text
Requirements／Architecture／ADR : Accepted
Source／Config／Test Implementation: Not Authorized
Dependency Install                    : Not Authorized
Model Download                        : Not Authorized
Lightning External Operation          : Not Authorized
ARGD／DAGD Project Import             : Not Authorized
```

ユーザーが対象Phaseの実装開始を明示的に許可するまで、本Handoffを根拠にSource／Config／Test／Directory／Dependency／External Serviceを変更しないこと。

## 2. 実装前に読む正本

### 2.1 共通

1. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719112304.md](../architecture/implementation_roadmap_20260719112304.md)

### 2.2 今回の追加要件

1. [post_phase_1e_research_platform_requirements_20260719112304.md](../requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
2. [generic_governance_definition_platform_requirements_20260719112304.md](../requirements/generic_governance_definition_platform_requirements_20260719112304.md)
3. [governance_definition_catalog_20260719112304.md](../governance/governance_definition_catalog_20260719112304.md)

### 2.3 Architecture

1. [governance_control_plane_architecture_20260719112304.md](../architecture/governance_control_plane_architecture_20260719112304.md)
2. [governance_definition_platform_architecture_20260719112304.md](../architecture/governance_definition_platform_architecture_20260719112304.md)
3. [experimental_runtime_ui_status_architecture_20260719112304.md](../architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
4. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)

### 2.4 Accepted ADR

1. [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
2. [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
3. [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
4. [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)

## 3. 現在のPhase状態

```text
1-A : Complete／Accepted
1-B : Complete／Accepted
1-C : Complete／Accepted
1-D : Implementation Complete／Review Requested／Not Yet Accepted
1-E : Planned／Not Designed／Not Authorized
2+  : Planning Only／Not Authorized
```

Phase 1-Dの最新Status：

- [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)

このStatusは最新Indexに取り込むが、設計者Reviewは未実施である。Acceptedと読み替えないこと。

## 4. 実装開始順序

現在の予定順序：

```text
Phase 1-D Review
  ↓
Phase 1-E Requirements／Architecture／ADR／Handoff
  ↓
Phase 1-E Implementation／Review
  ↓
Portable Runtime MVP Gate
  ↓
Phase 2-A Component Registry／Switchboard
  ↓
Phase 2-B Experiment Runtime
  ↓
Phase 2-C Event／Status／Minimal Audit
  ↓
Phase 2-D Lightning AI Studio
  ↓
Phase 3 Generic GD Platform／MARGPA Main Governance
```

Phase 2以降を一括実装しない。各Sub-phaseごとに詳細Handoff、ユーザー許可、Status、Reviewを通す。

## 5. Phase 2-Aの境界

### 5.1 作るもの

- Component Descriptor／Registry
- Component `enabled`
- Governance Mode `off／observe／enforce`
- Required／Optional Dependency
- Conflict／Invalid Combination
- Capability／Degraded Mode
- Apply Mode
- Governance Point／Binding HookのContract
- Effective Switch Validation

### 5.2 作らないもの

- Guard Model本体
- LLM-as-a-Judge本体
- Agent／Tool本体
- RAG本体
- ARGD／DAGD Compiler本体
- CDOGD Routing
- Web UI

### 5.3 非交渉条件

- Component IDを固定Closed Enumのみにしない。
- `enabled=false`とGovernance `mode=off`を同一視しない。
- Invalid Combinationを黙って自動修正しない。
- Tool Permission OFFをAllow Allにしない。
- System／Host／External AuthorityはApplication Switchで無効化できない。

## 6. Phase 2-Bの境界

### 6.1 作るもの

- Experiment Profile
- Experiment ID／Run ID／Request IDの分離
- Effective Config Snapshot／Hash／Source
- Model／Artifact Digest
- Definition／Adjustment／Plan Digestの将来Hook
- Seed／Input／Output／Latency／Token／Stop
- Baseline Profile

### 6.2 必須Baseline

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
```

Phase 3前の`main_governance_*`はProfile Schema／Validationの予約として存在できるが、未実装のGovernanceを実行済みと記録しない。

## 7. Phase 2-Cの境界

- Runtime Event Envelope
- Component／Governance Lifecycle Event
- Status Projection
- JSON／JSONL Append-Only
- Canonicalization Version／SHA-512
- Projection／Sink FailureでInferenceを壊さない

Runtime Lifecycle StateとDAGDのGovernance Status Reporterを同一Schemaにしない。

## 8. Phase 2-Dの境界

- Lightning AI Studioで同一Repositoryを使う。
- Linux x86_64／NVIDIA CUDA／llama.cppをDeployment Adapterで追加する。
- Application Coreに`if lightning`、`if cuda`を直書きしない。
- Macと同じLogical Model ID、Model Port、Test Contractを使う。
- GGUF、Secret、実LogをGitにCommitしない。
- ZeroGPUはこのPhaseのScopeに入れない。

## 9. Phase 3の最重要境界

### 9.1 Zero Definitionを先に成立させる

ARGD／DAGDを読み込む前に、次をPassさせる。

```text
definition_sources = []
definitions = 0
governance.mode = off
model load／generate／stream／cancel = pass
governance model calls／tokens／repairs = 0
```

`EmptyDefinitionProvider`をProduction Codeとして用意する。

### 9.2 特定GDのハードコード禁止

次をCoreに実装しない。

```text
if definition_id == "argd"
if filename contains "aisgd"
if cdogd exists
known_gd_count = 16
```

代わりにProvider／Manifest／Descriptor／Adapter／IR／Compiler／Bindingを使う。

### 9.3 Source JSONはData

- JSONからCode、Shell、Import、URL Downloadを実行しない。
- Custom SchemaはTrusted Adapter Pluginを別途登録する。
- Path Traversal、Size／Depth／Rule／Prompt上限、Digestを検証する。

### 9.4 ARGD／DAGD

- 現行の複合Source JSONはByte-for-byte不変でSnapshotする。
- Legacy Adapterが`argd`と`dagd`を個別Descriptor／IRに展開する。
- 利便性のためにSourceを独自分割しない。
- SourceがなくてもRuntimeを動作させる。

### 9.5 CDOGD

- 必須ではない。
- Phase 3でDynamic Routingを実装しない。
- 名前だけでOrchestrator Capabilityを付与しない。
- Custom Orchestrator-capability Definitionと交換可能にする。

## 10. Governance Source／Adjustment／Binding

```text
Immutable Definition Source
  + Manifest
  + Adjustment Profile
  + Binding
  + Compiler Version
  + Runtime Capability
  ↓
Compiled Plan
```

原始GD JSONに動作調整値を書き込まない。UIからもSource JSONではなくAdjustment／Bindingを編集する。

## 11. Governance Control Planeの非交渉条件

- Shared Control Plane + Distributed Point + Explicit Binding
- 各Pointへ完全なMARGPA一式を複製しない
- 全GDを毎ターン・全Pointで読み込まない
- Lazy Load／Rule Selection／Plan Cache／Budget
- Deterministic Rule First
- Semantic Evaluator Only When Needed
- Shared Context／Point-local State／Evidenceの分離
- Central Action Conflict Resolution
- Unknown ActionはRecord-only
- Governance-on-governanceの無限再帰禁止

## 12. UI実装時の境界

### Basic UI

- Main Model
- Response Language
- New Chat／History
- Generate／Stop／Regenerate
- Simple Status

### 開発・研究設定

- Generation
- Model Runtime
- Component Structure
- Governance
- Evaluation／Repair
- Agent／Tool
- Experiment
- Status／Audit
- Deployment

UIは`config/application.toml`を直接上書きしない。Typed Config Serviceを通じ、Preview、Validation、Diff、Source、Apply Modeを表示した後にGit対象外のLocal OverrideへAtomic Saveする。

## 13. 実装報告に必ず含めるもの

個別PhaseのImplementer Statusは少なくとも次を記載する。

- 実装ScopeとScope外
- 変更File一覧
- Contract／Schema／Migration
- Dependency変更の有無
- Unit／Integration／Native Test
- Mac／Lightning等の実行環境
- Effective Config／Source
- Artifact／Definition／Config Digest
- Performance／Token／Latency
- Degraded／Invalid／Failure Test
- 未解決項目
- Acceptance Criteriaの対応表

## 14. Docs運用

- 実装担当が読むその他のDocsは原則読み取り専用である。
- 実装Statusは`docs/handoffs/implementer_status_*_YYYYMMDDHHMMSS.md`として毎回新規作成する。
- 既存Docsを上書きしない。
- Review依頼後、設計者がReviewと新Indexを同時に作成する。

## 15. 将来GD Catalogの扱い

[governance_definition_catalog_20260719112304.md](../governance/governance_definition_catalog_20260719112304.md)に記載されたARGD、DAGD、CDOGD、SPPGD、DAAGD、SDAGD、SDMRGD、DSGD、ACRGD、AAGD、AISGD、MPGD、DCAGD、PMOGD、AIRGD、AIAGD、SEGD、OMRGDは、実装必須一覧ではない。

実装担当は次を守る。

- Catalogの名称をCore Enumにしない。
- Author提案PathをRuntime Contractにしない。
- GD名からCapabilityを推測しない。
- AAGDが実行許可を生成すると実装しない。
- DAAGDが存在しない権限を生成すると実装しない。
- MPGDが存在しないPolicyを生成すると実装しない。
- SDAGD／SDMRGDが外部の最終承認を代替すると実装しない。

## 16. 実装解禁時に設計者へ戻すべき条件

次のいずれかが発生した場合は、無断でScopeを拡大せず設計者／ユーザーへ戻す。

- 汎用Contractでは扱えないARGD／DAGD Schemaが見つかった
- Source JSONを書き換えないと実装できない
- 安全なIR／Action Contractに落とせない
- Required／Optional／Fail Open／Fail Closedの判断が方針を変える
- Lightningの課金／GPU／Model Upload操作が必要
- External Policy／Authority／Licenseの新しい条件がある
- UI FrameworkまたはStorageの最終選定が必要

## 17. Handoff結論

今回の設計で、Projectの次の中核が固定された。

```text
疎結合なFunctional Component
  + 個別Switch
  + 共有Governance Control Plane
  + 分散Governance Point
  + 全GD任意／0件Baseline
  + 実験再現性
  + Event-driven Status
  + Mac／Lightning Cross-environment
  + Basic UI／開発・研究設定の分離
```

実装担当は、後続Phaseを「特定のGDやServiceを埋め込む作業」ではなく、「0件から任意のComponent／Definitionを明示的に組み立てられるPlatformを段階的に実証する作業」として扱うこと。
