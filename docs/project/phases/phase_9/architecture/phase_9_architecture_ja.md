# Phase 9 Architecture — Three-program Composable Research Runtime

```yaml
document_id: phase_9_architecture
document_state: accepted_frozen_ready_not_started
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
architecture_style: modular_monolith_ports_and_adapters_with_program_gates
```

## 1. Program Boundary

```text
Phase 9-1  Governance Semantic Debt Fast Closure
  ├─ Dedicated Judge／Guard Runtime
  ├─ Semantic Criterion Runtime
  ├─ Judge／Repair／Rejudge
  └─ Semantic ENFORCE／Identity／Recording
           │ Controller Review + User Checkpoint
           ▼
Phase 9-2  Experiment／Evaluation／Multi-Governance
  ├─ Experiment Run／Config Snapshot
  ├─ Evaluation Set／Metric／Rubric
  ├─ Multiple Governance／Conflict／Routing
  └─ Freshness／NO_HIT／Belief Revision／Progressive Presentation
           │ Controller Review + User Checkpoint
           ▼
Phase 9-3  Context Compaction／Recovery Technical Core
  ├─ Context Budget／Pressure
  ├─ Snapshot／Atomic Compaction／Rollback
  ├─ Recovery Index／Selective Rehydration
  └─ UI-independent Event／Projection Contract
```

後段Programは前段のSourceへ暗黙に混入しない。各CheckpointはReturn、Review、User判断を持つが、Phase Closureではない。

## 2. Reused As-built Baseline

Phase 9-1は次の既存Componentを再利用し、同等機能を新規Frameworkで作り直さない。

```text
modules/runtime_model_control
  Provider Selection／Role Lifecycle／Lease／Load／Unload／Budget

adapters/runtime_model_control
  Dedicated Role Adapter／llama.cpp Backend／Model Registry

modules/runtime_governance
  Binder／Semantic Runtime／Point Runtime／Mode／Action Resolver

modules/governance_definitions
  Manifest／Compiler／Normalized IR／Adapter Registry／Runtime

modules/evaluation
  Judge Role／Prompt／Decoder／Budget／Mode

modules/repair
  Eligibility／Plan／State Machine／Budget／Success Evaluator

modules/guardrail_governance
  Deterministic Guard／Qwen3Guard Contract／Mode／Point／Stream Guard

bootstrap + web
  Production Wiring／Route／Status／Evidence／Failure Presentation
```

Phase 7のRAG／Citation、Phase 8のManual URL Evidence／Constitution／Dev AgentはRegression対象であり、Phase 9-1の再設計対象ではない。

## 3. Phase 9-1 Dedicated Role Flow

```text
Configured Provider
  -> Mode Transition Request
  -> Artifact／Manifest／Authority／Hardware Preflight
  -> Candidate Load
  -> Strict Contract Probe
  -> Atomic Active Commit
  -> Frozen Role Lease
  -> Real Inference
  -> Typed Decode／Failure
  -> Evidence／Recording
  -> Lease End
  -> OFF／Shutdown Unload
```

### 3.1 Invariants

- Configured変更だけでActiveまたはExecutedを捏造しない。
- Candidate Load／Probe成功前にModeをActiveへCommitしない。
- Provider切替中の旧Leaseを途中で別Providerへ差し替えない。
- Deadline／Cancel後のLate ResultをCurrentへPublishしない。
- Model Load失敗を一般的な`unknown`だけへ潰さず、Stage／Reason／Artifact Identityを保持する。
- Startup OFFではDedicated Model Call 0および不要な常駐Memory 0を目標とする。

## 4. Phase 9-1 Semantic Evaluation Flow

```text
Verified Definition Source
  -> Compiler／Normalized IR
  -> Rule／Point／Capability Binding
  -> Semantic Criterion Adapter
  -> Applicability Resolution
       ├─ applicable -> Built-in or Model Evaluation
       ├─ not_applicable
       ├─ unsupported
       ├─ unknown
       └─ deferred
  -> Criterion Evidence
  -> Action Resolver
```

一律109件Deferredを解消することは、109件すべてをPASSさせることではない。Ruleごとに何が評価され、なぜ評価されないかを正確に分離する。

## 5. Phase 9-1 Judge／Repair／Rejudge Flow

```text
Main Candidate
  -> Frozen Evaluation Context
  -> Judge Dispatch
  -> Strict Judge Decode
  -> Disposition
       ├─ accept -> Final Candidate
       ├─ deviation -> Repair Eligibility
       │                 -> Repair Candidate
       │                 -> Rejudge
       │                 -> adopt／reject／fallback
       ├─ unsupported -> Typed Presentation
       ├─ timeout／cancel -> Safe Failure
       └─ malformed／unavailable -> Safe Failure
  -> Final Presentation
  -> Correlated Recording
```

### 5.1 Identity Chain

```text
request_id
  -> turn_id
  -> configured_provider_id
  -> active_provider_id
  -> executed_provider_id
  -> definition_revision／criterion_id
  -> judge_run_id
  -> repair_run_id
  -> rejudge_run_id
  -> final_disposition
  -> recording_id
```

CurrentとHistoricalはProjectionで分離し、Identity Recordを上書きしない。

## 6. Phase 9-1 ENFORCE／Progressive Boundary

Phase 9-1ではSemantic ENFORCEのRuntime正当性を優先する。大規模なProgressive UXはPhase 9-2へ送る。

```text
Phase 9-1:
  Strict Bufferまたは既存Presentationを使い、未検証CandidateをFinalと誤表示しない。
  Supported Actionだけを実行し、Repair／Fallbackを正直に示す。

Phase 9-2:
  StrictとProgressiveを比較する。
  Progressiveは短いBlock／Chunk単位で検査済み部分だけを表示する。
  既表示部分を回収できないRiskをEvidence化する。
```

## 7. Phase 9-2 Experiment Architecture Reservation

```text
Evaluation Case／Dataset Manifest
  -> Experiment Plan
  -> Frozen Effective Config Snapshot
  -> Variant Run A／B／...
  -> Raw Output／Evaluation／Action／Repair／Final
  -> Metric／Qualitative Observation
  -> Comparison Report
```

Canonical Contract候補：

- `ExperimentIdentity`
- `ExperimentPlan`
- `EffectiveConfigurationSnapshot`
- `VariantRun`
- `EvaluationCaseManifest`
- `MetricObservation`
- `QualitativeObservation`
- `GovernanceCompositionResult`
- `BeliefRevisionObservation`
- `ExecutionTraceProjection`

Model、Provider、GD、RAGまたはJudge固有SchemaをExperiment Coreへ直結せず、Adapterで正規化する。

## 8. Phase 9-2 Semantic Research Boundary

### 8.1 Freshness／Authority

```text
Historical Conversation Fact
Current Source Lifecycle
Current Retrieval Evidence
Source Authority／Provenance
User Correction
  -> Semantic Freshness Evaluation
  -> Judge／Repair／Rejudge
  -> Current Answer／Insufficient Evidence／Conflict Presentation
```

過去TurnのCitation／Revision／Digestは永久に固定し、新TurnだけCurrent Sourceを再評価する。

### 8.2 NO_HIT

次を比較可能にする。

1. `Model Callあり + NO_HIT Evidence + Semantic Governance`
2. `Strict NO_HIT + Model Call 0 + 設定言語固定回答`

品質、Latency、言語安定性、False GroundingおよびUser体験を比較し、Strict方式を既定化するかはEvidence後に決める。

## 9. Phase 9-3 Context Core Reservation

```text
Context Capacity／Usage
  -> Effective Budget Calculation
  -> Pressure State
  -> OFF／OBSERVE／ENFORCE／Manual Decision
  -> Pre-action Snapshot
  -> Structured Compaction Candidate
  -> Validation
  -> Atomic Swap or Rollback
  -> Recovery Index
  -> Selective Rehydration
```

Original Chat、Active Context、Structured Context、Snapshot、Recovery IndexおよびHandoffを別Artifactとして扱う。要約だけをLosslessと呼ばない。

## 10. UI／Observability Boundary

Phase 9で許可するUIはTechnical Acceptanceに必要な最小Projectionだけである。

- Provider Configured／Active／Executed。
- Model Call CountまたはCall 0を裏付けるStage Trace。
- Criterion Count／Outcome。
- Judge／Repair／Rejudge／Final Disposition。
- Current／Historical分離。
- Exact Failure Stage／Reason。

次はPhase 10後半へ送る。

- Right-side Governance Trace Observatory。
- Citation／Source詳細の右Panel統合。
- Advanced Settings全体再編。
- Context Action Button。
- Responsive／Mobileを含む大規模Visual Consolidation。

## 11. Data／Security Boundary

- Network Artifact取得、外部Upload、Git、BackupまたはDeployは個別Authorityなしに行わない。
- Local Artifact Load／Inference AuthorityとNetwork Download Authorityを分離する。
- Raw Secret、CredentialまたはProviderが露出しないInternal ReasoningをEvidenceへ保存しない。
- Full Raw Research Traceを将来扱う場合、Visibility、Persistence、Redaction、Retentionを分離する。
- Runtime DataとProject Sourceを混同せず、Test FixtureからUser DataへMutationしない。

## 12. Failure／Fallback Classes

```text
artifact_missing
artifact_digest_mismatch
manifest_unverified
hardware_profile_unverified
model_load_failed
model_inference_failed
model_output_malformed
criterion_not_applicable
criterion_unsupported
criterion_unknown
criterion_deferred
judge_unavailable
repair_ineligible
repair_failed
rejudge_failed
budget_exceeded
deadline_exceeded
cancelled
late_result_rejected
authority_denied
```

FallbackはFailureを消さない。User-facing安全表示とResearch Evidenceを同じ理由Identityへ相関する。
