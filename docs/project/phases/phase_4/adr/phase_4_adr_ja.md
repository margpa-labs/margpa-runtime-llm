# Phase 4 ADR — Main Runtime Governance MVP

```yaml
document_id: phase_4_adr
status: accepted_frozen_ready_for_backup
phase: phase_4
language: ja
recorded_at: 2026-08-21 22:04:22 JST
implementation_authorized: false
frozen_at: 2026-08-21 23:20:56 JST
```

## ADR-4-001：Phase 4はMain Model Pointだけを最初にBindingする

Guardrail／Judge／RAG／Agent／Tool Pointを同時実装しない。最初の実証対象を`main_model.pre／post`へ限定し、分散PointはPhase 5以降へ段階追加する。

## ADR-4-002：QwenをPhase 4の必須Baselineとする

DeepSeekは将来Candidateであり、Phase 4完了条件にしない。低資源QwenでGovernance OFF／OBSERVE／ENFORCEの差を測ること自体を研究価値とする。

## ADR-4-003：PlanとBindingを分離する

Phase 3のUnbound Planを上書きしない。Point、Capability、Authority、Policy、BudgetおよびAction Registryを含む別ArtifactとしてBindingする。

## ADR-4-004：Deterministic First

Phase 4は追加Model CallなしのDeterministic Evaluatorを正式Baselineとする。Semantic EvaluatorはPortを予約しても、Phase 6前に必須化しない。

## ADR-4-005：Phase 4 Enforceは有界Actionだけ

登録済み・局所的・明示的にAuthorityを持つActionだけを実行する。自動Repair／反復RegenerateはPhase 6へ延期する。

## ADR-4-006：ARGD／DAGDはReference AdapterでありCoreではない

Typed Semantic MappingはTrusted Adapterへ置く。CoreのEnum、BranchまたはPathへ固有略称を埋め込まない。

## ADR-4-007：Observeは絶対に非介入

Observe時のResult、ScoreまたはRecommendationを、Model Input／Output／Stop／Persistenceへ反映しない。比較実験のControlを守る。

## ADR-4-008：RejectとRepairを混同しない

Phase 4 post-Enforceで不適合OutputをRejectできても、別回答へ書き換えたり自動再生成しない。修復はPhase 6の独立Loopとする。

## ADR-4-009：各Phase境界で重大Reviewを行う

Phase 4の欠陥を抱えたままPhase 5／6へ進まない。Claude COMPLETE_CANDIDATE後、Codexは重大Findingだけを独立Reviewする。

## ADR-4-010：Phase 4／5 Closureは軽量、Phase 6でProgramを統合Reviewする

利用可能量とEvidence乱造を抑える。ただしRecovery Index、Exact Mutation、Test結果、Open Major FindingおよびUser Gateは省略しない。
