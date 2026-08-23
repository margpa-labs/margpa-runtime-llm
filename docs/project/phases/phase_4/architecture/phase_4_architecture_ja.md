# Phase 4 MARGPA Main Runtime Governance Architecture

```yaml
document_id: phase_4_architecture
status: accepted_frozen_ready_for_backup
phase: phase_4
language: ja
recorded_at: 2026-08-21 22:04:22 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Architecture Summary

```text
Phase 3 Package／IR／Unbound Plan
  + Runtime Capability Snapshot
  + Authority／Policy Snapshot
  + Action Registry Snapshot
  + Profile／Budget
        ↓
Governance Binder
        ↓
Bound Governance Plan（immutable／digest）
        ↓
main_model.pre Governance Point
  → deterministic evaluation
  → recommendation
  → mode／authority／budget aware action resolution
        ↓
Existing Model Adapter／Generation
        ↓
main_model.post Governance Point
  → deterministic evaluation
  → recommendation／bounded action
        ↓
Canonical Assistant Result

全境界 → Standard Governance Result → Evidence／Status Subscriber
```

Phase 4は既存Generation Serviceを置換しない。Governance OrchestratorがPointを前後へ合成し、`off`では既存経路そのものへShort-circuitする。

## 2. Module Boundary Candidate

```text
modules/runtime_governance/
  domain/{identities,results,binding,evaluation,actions,mode,errors}.py
  ports.py
  application/{binder,point_runtime,action_resolver}.py
  public.py

adapters/runtime_governance/
  deterministic_evaluator.py
  reference_definition_adapter.py
  registered_actions.py

bootstrap/runtime_governance.py
web/governance_routes.py（既存Phase 3 Surfaceを互換拡張）
```

実FileはPhase 4開始時のAs-built Sourceへ合わせてFreezeする。固定Package一式を機械的に作る契約ではない。

## 3. Core Contracts

### 3.1 Bound Plan

```text
BoundGovernancePlan
  binding_id
  binding_version
  point_id／stages
  source_plan_id／digest
  selected_rule_refs／digests
  evaluator_bindings
  action_bindings
  capability_snapshot_digest
  authority_snapshot_digest
  policy_snapshot_digest
  action_registry_digest
  profile_digest
  budget_digest
  unresolved／conflicts／warnings
  executable
  binding_digest_sha512
```

`executable=true`は全Planが安全という意味ではない。各InvocationでMode、Current Authority、CapabilityおよびBudgetを再確認する。

### 3.2 Invocation Context

```text
GovernanceInvocation
  invocation_id
  point_id
  stage
  turn／request refs
  input_snapshot_ref
  bound_plan_ref
  capability／authority／policy snapshot refs
  budget
  mode
```

SnapshotはTyped Allowlistであり、任意Runtime Object Dumpではない。

### 3.3 Standard Result

```text
StandardGovernanceResult
  execution_state
  selected_definitions／rules
  observations
  deviations
  scores／critical_flags
  severity
  recommended_actions
  executed_actions
  warnings／errors
  evidence_refs
  state_patch
  cost／latency／call_count
```

Phase 4の`state_patch`はPoint-local Governance Stateだけを対象とし、Conversation DBやTool Permissionを直接変更しない。

## 4. Mode Routing

### OFF

OrchestratorはBinder／Evaluator／Actionを呼ばず、既存Generation Inputをそのまま既存Serviceへ渡す。Statusは最小Mode Snapshotのみ。

### OBSERVE

Pointを実行してResult／Recommendation／Evidenceを生成するが、Model Input、Generation Config、Terminal Output、StopまたはConversation Persistenceを変更しない。

### ENFORCE

Bound PlanとAction Registryが利用可能な場合だけ、Action Resolverを通す。Action実行順は次で固定する。

```text
recommendations
  → conflict resolution
  → mode check
  → authority／policy check
  → capability check
  → budget check
  → registered adapter validation
  → execute or explicit not_executed reason
```

## 5. Phase 4 Action Ceiling

初期ActionはSide Effectを局所化する。

- `pass`。
- `recommend_only`。
- Safe Warning／Status。
- Generation開始前の明示Stop／Reject。
- Canonical Outputの明示Reject。
- Allowlist済みGeneration Config Constraint。

自動Repair、反復Regenerate、Secret Redaction、Tool Action、External Side EffectおよびHuman Approval代行はPhase 4で実行しない。

## 6. ARGD／DAGD Connection

Phase 3のGeneric Adapter／Structural IRを残し、Phase 4でTyped Execution Extensionを追加する。

```text
Generic Normalized IR
  + Trusted Definition-specific semantic mapping
  → typed rule／condition／evaluator／recommended action descriptors
  → Generic Binder
```

固有AdapterはPlugin境界に置き、Core Binder／Point RuntimeはDefinition IDを知らない。Sourceに存在しないRule、Priority、ActionまたはAuthorityを補完しない。

## 7. Main Model Integration

既存API／SSE Shapeは維持する。

- `pre` ObserveはModelへ渡す前のSnapshotを評価するが変更しない。
- `pre` EnforceのStopはModel Call前にTyped Terminalへ収束する。
- Generation Config Constraintは既存Validatorを通るAllowlist Fieldだけ。
- `post` ObserveはCanonical Final Assistant Contentを評価するが変更しない。
- `post` Enforce RejectはAssistant Contentを別内容へ自動書換えせず、明示状態として扱う。
- Summary／RAG／Persistent CompletionのCanonical順序を壊さない。

Persistent経路のTerminal順序は次で固定する。

```text
Model／Summary Canonical Candidate
  → main_model.post Governance Terminal Decision
  → Authorized passのみAssistant MessageをAtomic Commit
  → Commit成功後だけcompleted SSE
```

`reject_output`、Stop、Governance FailureまたはCommit Failureでは、未承認CandidateをConversation Message／Headへ保存せず、`completed`を送らない。通信断でCommit結果が不明な場合は既存Operation Receipt／Detail再読へ収束し、再生成や二重Commitで推測修復しない。Ephemeral経路も既存SSE Shapeの明示Terminalへ収束し、Reject済みCandidateをCompletionとして扱わない。

Repair／RegenerateはPhase 6までRecommendationに留める。

## 8. Evidence／Status

EvidenceはPhase 3 Portを拡張し、次をMetadataで記録する。

- Point／Stage／Invocation ID。
- Binding／Plan／Rule／Evaluator／Action Digest。
- Mode／Profile／Authority／Budget Digest。
- Evaluation State／Severity／Critical Flag。
- Recommended／Executed／Not-executed reason。
- Latency／Call／Token／Warning／Error。

Status Subscriber失敗をResult成功へ偽装しない。Default ObserveではGenerationを壊さずDegradedを可視化する。

## 9. Cache／Concurrency

- Binding Cache KeyはPlan、Point、Profile、Capability、Authority、Policy、BudgetおよびAction Registry Digestを含む。
- Cache Hit時にEmbedded Digestを再検証する。
- Mode OFF、Registry変更、Authority Revision変更またはDefinition Revision変更でStale Bindingを再利用しない。
- Invocation StateはRequest-local、共有StateはNamespaced CASとする。
- Multi-tab／Concurrent RequestでResultまたはActionを別Turnへ混同しない。

## 10. Failure Policy

- Provider／Adapter／Binding Failure：OFFでは無関係、Observe／EnforceではTyped Degraded／Unavailable。
- Deterministic Evaluation Failure：Raw Exceptionを露出せず、Enforceで安全側Actionまたは明示StopをProfileに従って選ぶ。
- Action Failure：Action成功を記録せず、Canonical Runtime Stateを不明瞭にしない。
- Evidence Failure：ProfileどおりDegradedまたはFail-closed。Default Observeは非介入。
- Authority不明：実行0。

## 11. Phase 5／6 Seams

- `guardrail.pre／post` Point Registry。
- Policy／Authority Provider Port。
- Semantic Judge Port。
- Repair Orchestrator Port。
- User Feedback／Evaluation Dataset Port。
- Status State Machine Extension。

Seamの存在を実装済みと表記しない。
