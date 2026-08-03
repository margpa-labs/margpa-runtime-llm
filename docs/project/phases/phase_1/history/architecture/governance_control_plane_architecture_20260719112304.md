# Governance Control Plane Architecture

- 文書ID: `governance_control_plane_architecture`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 2～9のGovernance共通基盤
- 正本言語: 日本語
- 上位要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 関連ADR: [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規Architecture系列）

## 1. Decision Summary

Governanceを1つの巨大な直列Layerとして全機能を管理する構成は採用しない。また、Guard、Judge、Agent等の各所に完全なMARGPA一式を複製する構成も採用しない。

採用するのは、次のHybrid Architectureである。

> 共有Governance Control Plane／Kernel + 分散Governance Enforcement Point + 明示Governance Binding

## 2. Logical Architecture

```text
                    ┌── Governance Control Plane ──┐
                    │ Definition Providers／Registry   │
                    │ Descriptor／Adapter／Compiler  │
                    │ Activation／Rule Selection      │
                    │ State Namespace／Evidence       │
                    │ Evaluator Port／Budget          │
                    │ Conflict／Action Resolver       │
                    │ Status Event Publisher            │
                    └────────────────────────────────────┘
                         ↑ Binding／Plan／Result
                         ↓
Input → [Input Point]
      → RAG → [RAG Point]
      → Guard → [Guard Point]
      → Agent → [Agent Point]
      → Tool → [Tool Point]
      → Judge → [Judge Point]
      → Main Model → [Model Point]
      → Output → [Repair Point]
      → Response
```

Pointの実際の配置は常にComponent後とは限らない。`pre`、`post`、`around`、`stream`等のHook KindをDescriptorで表現し、Functional Componentの性質に応じて決める。

## 3. Component Responsibility

### 3.1 Governance Definition Provider

- Filesystem、Empty、将来のRemote／Database等のSource差を隠蔽する。
- Raw Definitionを読み込む前にMetadataとRepository Stateを提供する。
- Definition 0件を正式に表現する。

### 3.2 Governance Registry

- Provider、Package、Definition、Adapter、Compiler、Evaluator、Action Adapter、Point Typeの登録を管理する。
- Startup時はMetadata中心とし、Raw JSON全件を読み込まない。
- Canonical Reference、Version、Digest、Capabilityで解決する。
- GD略称を固定列挙にしない。

### 3.3 Adapter／Normalizer

- SourceごとのSchema差をNormalized Governance IRへ変換する。
- Sourceの意味を無断で補完しない。
- Unsupported、Ambiguous、Invalidを状態とEvidenceで返す。

### 3.4 Governance Compiler

- IR、Binding、Adjustment、Point Context、Runtime CapabilityからCompiled Planを生成する。
- 必要なRuleだけを選択する。
- Hard Constraint、Structural、Soft、Advisoryの区別を保持する。
- Compiler VersionをPlan Identityに含める。

### 3.5 Governance Kernel

- PointからのEvaluate Requestを受ける。
- Mode、Activation、Budget、Capability、Required Flagを検証する。
- Rule Engineと必要なSemantic Evaluatorを呼び分ける。
- Result、Evidence、Recommended Actionを生成する。

### 3.6 Conflict／Action Resolver

- 複数Rule、Definition、PointからのActionを一つの実行決定に整理する。
- System／Host／Tool Permission／Human Approval等の外部Authorityを越えない。
- 未知Actionは実行せずRecommendationとして記録する。
- `refuse > require_approval > stop > repair > regenerate > warn > allow`のような単純固定順位のみで全問題を解決せず、Action Category、Authority、Scope、Severity、Point、Conflict Policyを使う。

### 3.7 Evidence／Audit

- Input Fact、Rule Match、Evaluator Result、Recommended Action、Executed Actionを分離する。
- Source Definition、Package、Adjustment、Plan、Compiler、PointのDigestを関連づける。
- Append-Only EventとしてAudit Sinkへ渡す。

### 3.8 Status Publisher

- `governance_started`、`rule_evaluated`、`semantic_evaluation_requested`、`action_recommended`、`action_executed`、`governance_completed`等のEventを発行する。
- Status ProjectionとGovernance実行を相互依存させない。

## 4. Governance Point Contract

Point Requestの概念形：

```text
GovernancePointRequest
  request_id
  session_id
  turn_id
  point_id
  hook_kind
  component_id
  binding_ref
  input_scope
  shared_context_ref
  local_state_ref
  runtime_capabilities
  deadline
```

Point Resultの概念形：

```text
GovernancePointResult
  execution_state
  repository_state
  selected_definitions
  selected_rules
  observations
  deviations
  severity
  recommended_actions
  executed_actions
  warnings
  errors
  evidence_refs
  state_patch
  cost
```

PointはFunctional ComponentのBusiness Logicを内包しない。例えばGuard PointはGuard Modelの代わりではなく、Guard Componentへの入力と出力を統治する。

## 5. Governance Binding

### 5.1 Bindingの概念形

```toml
[governance.bindings.main_model_pre]
point_id = "main_model.pre"
mode = "observe"
required = false
profile = "foundational"
definition_refs = []
required_capabilities = ["premise_preservation"]
max_semantic_calls = 0
max_repair_attempts = 0
```

### 5.2 Selectionの優先順位

1. Explicit Definition Reference
2. Explicit Package／Profile Selection
3. Capability RequirementによるSelection
4. 設定済みDefault Binding
5. No Binding／Inactive

File名、Directory、略称、Catalog上の推奨はSelectionの根拠にしない。

## 6. Execution Mode

### 6.1 OFF

```text
Rule Selection          : Skip
Plan Load               : Skip
Semantic Model Call     : 0
Intervention            : 0
Minimal Status          : governance_disabled
```

### 6.2 OBSERVE

- 判定、Score、Deviation、Recommendation、Costを記録する。
- Functional ComponentのInput／Outputを変更しない。
- Refuse／Repair／Regenerateを実行しない。
- External Policyによる独立した強制拒否は別責務であり、Observeで無効にはならない。

### 6.3 ENFORCE

- Compile済みRuleと登録済みAction Adapterの範囲内で介入する。
- Definition、Capability、Dependency、Authorityが不足する場合は、Enforcement Successとは扱わない。
- Repair／RegenerationはBudget、Loop Limit、Success Criterionを必須とする。

## 7. State Architecture

### 7.1 Shared Turn／Session Context

次のような複数Pointで共有すべき参照情報を持つ。

- Interpreted Intent
- Fixed Premise
- User Decision
- Active Experiment
- Runtime Capabilities
- External Authority State Reference

### 7.2 Point-local Namespace

```text
governance_state.input.*
governance_state.guard.*
governance_state.agent.*
governance_state.judge.*
governance_state.main_model.*
governance_state.repair.*
```

Custom Point IDを許容するため、上記は例である。

### 7.3 Append-Only Evidence

Stateの現在値と、そこへ至ったEvidence Eventを分離する。ProjectionはEventから再構築可能にする。

## 8. Rule Evaluation Pipeline

```text
Point Request
  ↓ Binding Resolution
  ↓ Repository／Definition State Validation
  ↓ Activation Evaluation
  ↓ Compiled Plan Cache Lookup
  ↓ Deterministic Rule Evaluation
  ↓ Semantic Evaluation（必要な場合のみ）
  ↓ Score／Deviation／Severity
  ↓ Action Recommendation
  ↓ Conflict／Authority Resolution
  ↓ Mode Application
  ↓ Evidence／Event／State Patch
```

## 9. Performance Control

### 9.1 Lazy Strategy

- Registry Startup: Package／Definition Metadataのみ
- Activation時: Raw Definition Load／Validation
- Point実行時: Required RuleのCompileまたはCache Hit
- Semantic Evaluation: Deterministic Ruleで不足する場合のみ

### 9.2 Cache Key

```text
provider_id
package_digest
definition_digest_set
adapter_version_set
adjustment_digest
compiler_id_and_version
point_id
runtime_capability_digest
```

### 9.3 Budget

- Max Rules
- Max Prompt Tokens
- Max Semantic Calls
- Max Evaluator Tokens
- Max Latency
- Max Repair Attempts
- Max Total Turn Calls
- Max Meta-governance Depth

Budget超過は黙って無視せず、`budget_exhausted`とDegraded／Refusal Policyを返す。

## 10. Main Governanceの第一実装

Phase 3の第一実証はMain Modelに最も近いPointとする。

```text
User／Conversation Context
  ↓ Main Model Pre-governance Point
  ↓ Prompt／Context／Generation Configuration
  ↓ Model Adapter
  ↓ Main Model Post-governance Point
  ↓ Optional Repair
```

第一実装では、利用可能な場合にARGD／DAGDを使って汎用基盤を実証する。ただしDefinition 0件Baselineを必ず同時に成立させる。

実行Profile：

| Profile | 内容 |
|---|---|
| `core` | 必須Rule、決定論中心、追加Model Call最小 |
| `standard` | Core + 回答後Audit + 必要時の軽量Repair |
| `full` | 前後Audit、詳細Score、Severity、Repair Loop、Rebind／Enforce／Reinitialize |

Definition内容と実行負荷Profileを分離する。

## 11. Meta-governance Boundary

Governance Pointの出力を別のGovernance Pointが無制限に評価する構造を禁止する。

Phase 3～8：

- Meta-governanceは原則OFF
- 個別に必要なSelf Auditは同一Plan内でBoundedに行う
- Cross-GD Meta Reviewは手動または非同期

Phase 9以降：

- Orchestration Capabilityを持つDefinitionのみ使用
- Max Depth 1をDefault
- 元EvaluationとMeta ReviewのEvidenceを分離
- Meta Reviewが外部Authorityに化けない

## 12. Failure Policy

| Failure | Optional Binding | Required Binding |
|---|---|---|
| Definition Source Missing | Inactive + Warning | Error／Refuse |
| Invalid Optional Definition | Quarantine + Continue | Error if selected |
| Adapter Missing | Quarantine | Error if selected |
| Semantic Evaluator Unavailable | Rule-based Degraded | RefuseまたはConfigured Degraded |
| Status Sink Failure | Continue + Local Warning | Continue（Inferenceを壊さない） |
| Audit Sink Failure | Policyに従う | High-assurance ProfileではRefuse可 |
| Action Adapter Missing | Recommend only | Refuse if action required |

## 13. 実装順序

1. Phase 2-A: Component Registry、Point／Bindingのフック、Mode Contract
2. Phase 2-B: Experiment Profile、Run Identity、Snapshot
3. Phase 2-C: Runtime Event、Status Projection、Minimal Audit
4. Phase 3: Definition Provider、Registry、Adapter、IR、Compiler、Kernel
5. Phase 3: Main Model Pre／Post Point、Basic Repair
6. Phase 5～8: Functional ComponentごとにPoint／Bindingを追加
7. Phase 9: Multiple GD、Conflict、Dynamic Orchestration、Meta Review

## 14. 未決事項

- Normalized Governance IRの詳細Schema
- Action CategoryとConflict Matrix
- Semantic Evaluatorの第一Backend
- Score／Weight／Thresholdの正規化
- Repair Success Criterionの共通部とDomain固有部
- Audit Sink Failure時のProfile別Policy
- Local OverrideによるBinding保存Path
- Runtime中のBinding Reload範囲

## 15. Authorization Boundary

本ArchitectureはAcceptedであるが、Source／Config／Testの実装は未解禁である。
