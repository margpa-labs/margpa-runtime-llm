# Phase 9-1 Three Distinct Controller Independent Review Recovery

```yaml
document_id: phase_9_1_three_distinct_controller_independent_review_recovery_20260901004404
document_state: complete_recovery
language: ja
created_at: 2026-09-01T00:44:04+09:00
phase: phase_9
program: phase_9_1
controller_five_hour_remaining_at_entry: approximately_10_percent_user_report
default_review_policy_changed: false
exception_scope: phase_9_1_only
```

## 1. User Authority

Phase 9-1の高難度と週間Resourceの価値を踏まえ、既存Independent Reviewと全く異なる観点であと2回Reviewし、3回連続の完全別観点Independent Reviewとする。

DefaultのReview規定値は2回のまま変更しない。本3回目追加はPhase 9-1のような特に難しいScopeに限定する。

## 2. Review Separation

### Review 1 — Completed Before This Recovery

```text
Perspective:
  Requirement／Acceptance／Source／Test／Claim Conformance

Main outputs:
  P9-CODEX-001〜005
  Maximum Claim Correction
  Real Dedicated Activation Mandatory Correction
```

本RecoveryでReview 1を再実行しない。

### Review 2 — Operator Journey／Production Reachability

Requirements TableやAcceptance Countを起点にせず、Userが実際に次を行った時のProduction Dataflowを前から後ろへ追う。

```text
Startup CLI
-> Production Factory
-> Provider Registry / Selection
-> Mode Apply
-> Artifact Preflight
-> Candidate Load
-> Active Commit
-> Actual Inference
-> Strict Decode
-> Evidence / UI Projection
-> OFF / Stop / Unload
```

目的は「TypeまたはFixtureが存在する」ではなく、Real Selene／Qwen3GuardへProductionから到達可能かを判定することである。

### Review 3 — Temporal State／Concurrency／Lifecycle

Functional Requirementを起点にせず、時間軸上のState Transitionだけを攻撃的に追う。

```text
Provider switch during active turn
Concurrent mode apply / turn begin
Candidate load failure after prior active provider
Cancel / deadline / late completion
OFF while lease exists
Shutdown while worker exists
Unload exception / retry
Restart / persistence / historical-current separation
Evidence identity across state changes
```

目的はRace、TOCTOU、Stale State、False Active、Lease Leak、Late ResultおよびIdentity Driftを発見することである。

## 3. PoC／MVP Finding Line

Current ReworkまたはBlocker候補は次だけとする。

- Real Selene／Qwen3Guard成立を防ぐ。
- Main／Judge／Guard／RepairのCurrent Production Turnを誤って実行する。
- Data／Evidence／Provider Identityを破壊または虚偽表示する。
- OFF／Stop／Cancel／Unload後に新しいInferenceまたはLate ResultをCurrentとして追加する。
- User Mac Manualへ渡せない。

Minor／Polish／Enterprise Hardeningは即時Reworkしない。

## 4. Current State at Recovery Creation

```text
Review 1: complete
Review 2: complete — Critical 1／Major 1
Review 3: complete — Critical 2／Major 1
Real Selene PASS: not yet
Real Qwen3Guard PASS: not yet
Phase 9-1 Complete Candidate: not claimed
Phase 9-2: not started
Git / Network / Real Model / Browser action by this review: 0
```

## 5. Exact Resume Action

```text
1. Read this Recovery only.
2. Do not repeat Review 1.
3. Review 2は再実行しない。
4. Start Review 3 from Temporal State／Concurrency／Lifecycle.
5. Record exact Source path / symbol / reproduction for each material finding.
6. If the five-hour limit interrupts work, update this Recovery with the exact last symbol and next action.
```

## 5.1 Review 2 Result

Review 1とは別のOperator Journey／Production Reachability観点で、次を新規検出した。

- P9-CODEX-006: Selene公式Prompt未成立、公式TemplateとProject独自JSON DecoderのContract不一致、`active`表示と実評価可能性の分離。Critical／MVP Blocker。
- P9-CODEX-007: Dedicated Preflightが実際にはAuthority＋Registry＋静的Capability計算だけであり、Artifact／Digest／Manifest／Hardwareを検査するというClaimが虚偽。Major。

Evidence:
`docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_2_operator_journey_production_reachability_ja_20260901032224.md`

## 5.2 Review 3 Result

Review 1／2とは別のTemporal State／Concurrency／Lifecycle観点で、次を新規検出した。

- P9-CODEX-008: Candidate部分Load失敗後にResourceがLoad済みのまま追跡不能になる。Critical／MVP Blocker。
- P9-CODEX-009: Lease Identityを消費しないため、Duplicate／Stale Releaseが別の実行中Turnを減算し、早期Unloadできる。Critical／Concurrency Blocker。
- P9-CODEX-010: Qwen3Guard実InferenceにDeadline／Cancellationがなく、User Stop／Mode OFF／Shutdownが実CallをPreemptできない。Major／MVP Liveness Blocker。

Evidence:
`docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_3_temporal_state_concurrency_lifecycle_ja_20260901033408.md`

## 5.3 Exact Next Action

```text
1. 3 Reviewの相互非重複性と追加検出価値をEvidence化する。
2. P9-CODEX-006〜010を一つのCopilot Rework Contractへ統合する。
3. Copilot Exact HandoffとUser貼付用指示文を作る。
4. Phase 9-2／Git／Real Model実行へは進まない。
```

## 6. Final Required Outputs

- Review 2 Result／Finding Ledger。
- Review 3 Result／Finding Ledger。
- 発見したCritical／Major／MVP Blockerの修正またはExact Rework Handoff。
- 三連続完全別観点Independent Reviewの有効性／非有効性Evidence。
- 修正箇所、発見Review、既存Reviewで見逃した理由の完全な対応。

## 7. Completion Receipt

```text
Review 1: complete
Review 2: complete — Critical 1／Major 1
Review 3: complete — Critical 2／Major 1
Additional Material Findings after Review 1: 5
Real Selene PASS: false
Real Qwen3Guard PASS: false
Phase 9-1 Complete Candidate: false
Copilot Rework Handoff: ready
Phase 9-2 / Git / Real Model action by this Review continuation: 0
```

### 7.1 Effectiveness Evidence

`docs/project/shared/history/automation/phase_9_1_three_fully_distinct_controller_independent_review_empirical_evidence_ja_20260901033839.md`

SHA-512:
`230e7cbf6683e5c35cdae53ad28fed9e9c0bda1c0fca996adac0627cee9ffb210a7bedadaec38a763ec5defc42da6193f91d293a3c1e9ee82cb113ded08592f0`

### 7.2 Copilot Exact Handoff

`docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_three_review_real_dedicated_completion_exact_handoff_ja_20260901034115.md`

SHA-512:
`82ee1b9d8330f6ade9b8650f3a3a43d52829dfa65e65066c7e1dc748966f5b3a74cfdd6e8059d52076116bbb21ec2d2b394ab6ca96a371bc1921e2d67254e757`

旧SHA-512 `a944ff1e...` は、Copilot Stale Task Incident後のMandatory Task Identity Reset追加によりSuperseded。

### 7.2.1 Copilot Stale Task Incident Evidence

`docs/project/shared/history/automation/copilot_stale_task_unauthorized_resume_after_wait_incident_evidence_ja_20260901104830.md`

SHA-512:
`04003e5b2cf59ec2808d2a803f21166bdf8059c3088cc783c2fd4d8c0f672f9395139611e071db942c7d82ce07f02662b29d4d98860fca0eb8779157449055c9`

### 7.2.2 Copilot Model Attribution Addendum

`docs/project/shared/history/automation/copilot_model_attribution_august_terra_high_and_september_codex_medium_addendum_ja_20260901110141.md`

SHA-512:
`93f8426e9d3e2353d5f6fbaea126792e94d22004e1a066d08291a191c8ae1c7b6ecaf2480f62a1953d2a47ad0c60dc928fd081f2cbc2a2ed0c04e8fff8e12b9b`

### 7.3 Exact Next Action

Copilot Taskへ上記Exact Handoffと統合指示文を渡し、P9-1-RW-Aから開始する。本Controller TaskはCopilot完了報告までSource実装を並行実行しない。
