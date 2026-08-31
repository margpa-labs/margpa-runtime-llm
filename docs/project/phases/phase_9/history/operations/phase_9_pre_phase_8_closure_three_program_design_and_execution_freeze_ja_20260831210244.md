# Phase 9 Pre-Phase-8-Closure Three-program Design／Execution Freeze

```yaml
document_id: phase_9_pre_phase_8_closure_three_program_design_and_execution_freeze_20260831210244
document_type: design_decision_and_execution_freeze
document_state: frozen_not_ready_not_started
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
decision_authority: user
authority_owner: Nazuna Research
source_mutation: phase_9_docs_only
phase_8_closure: not_executed
phase_9_ready: false
phase_9_implementation: not_started
```

## 1. Decision

Userは、Formal Phase Closureへ入る前に次Phaseの現時点設計・工程分解を先に行う現行運用ルールに従い、Phase 8 Formal Closureより先にPhase 9を設計するよう指示した。

Phase 9は次の三つへ分離する。

```text
Phase 9-1:
  Phase 6 Governance Semantic Debt Fast Closure
  -> 最優先。詳細設計・工程分解を先に完了する。

Phase 9-2:
  Experiment／Evaluation／Multi-Governance／Semantic Research
  -> 9-1完了後。現時点はPackage境界と入口条件だけを固定する。

Phase 9-3:
  Context Compaction／Recovery Technical Core
  -> 9-2後、利用可能量とAs-builtを再評価する条件付きProgram。
```

## 2. Why This Split

Phase 9全Scopeを一つのLong-runへ詰め込むと、Phase 6の中心Debt解消がExperiment Platform、Semantic研究、Progressive UIおよびContext技術Coreに埋もれ、Userが最優先とした「まず1を早く終わらせる」が達成できない。

三分割により、次を可能にする。

- 9-1だけを独立Handoff、Independent Review、User Manualへ渡せる。
- 9-1のAs-builtを9-2の正確なBaselineにできる。
- 9-3をResource不足時に切り離しても、9-1／9-2のTechnical Claimを汚染しない。
- Phase 10の全Docs／Constitution／PADG／UI Integrationを先取りしない。

## 3. Frozen Phase 9-1 Scope

Phase 9-1は次の七つを中心Debtとして扱う。

1. Selene Dedicated Judgeの実Artifact Load／Inference／Prompt／Strict Output Contract。
2. Qwen3Guard Dedicated Guardの実Artifact Load／Inference／Target別Output Contract。
3. ARGD／DAGDその他GD Semantic RuleのLive Criterion評価。
4. Built-in Evaluatorの適用可能Criterionと`not_applicable／deferred／unknown`境界。
5. Independent JudgeによるJudge／Repair／Rejudge Golden Path。
6. Main Governance Semantic ENFORCE、Conflict／Priority／Budget。
7. Configured／Active／Executed／Evidence Identityの一致。

Phase 9-1は23 Work Unit、5 Packageへ分解した。

| Package | WU | Purpose |
|---|---:|---|
| P9-1-0 | 3 | Entry／As-built／Authority Freeze |
| P9-1-A | 5 | Dedicated Selene／Qwen3Guard Runtime |
| P9-1-B | 5 | Semantic 109／Built-in Evaluation |
| P9-1-C | 6 | Judge／Repair／Rejudge／Semantic ENFORCE |
| P9-1-D | 4 | Integration／Two-cycle Internal Review／User Manual Candidate |

## 4. Fast Closure Guardrails

- Existing Phase 6 Infrastructureを再実装しない。
- Phase 9-2 Experiment Frameworkを先に作らない。
- Phase 9-3 Context Coreを混ぜない。
- Phase 10 UI／All-Docs／Constitution／PADGを混ぜない。
- UIはModel Call、Provider Identity、Criterion、Judge／Repair、FailureおよびCurrent／Historicalを確認する最小Projectionだけにする。
- Dedicated ArtifactがMacで成立しない場合はPASSへ捏造せず、Stage別`RESOURCE_GATED`と正直なBaselineを返す。
- Product品質、未解決0件または一発完全合格を目標にしない。

## 5. Review／Return Model

```text
Executor:
  Implement + Test + Perspective-changed Internal Review 2 Cycles
  -> P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW

Codex Controller:
  Bounded Independent Review
  -> Critical／Major／MVP BlockerだけRework

User:
  Real Mac／Artifact／UI Manual Gate
  -> P9-1 Disposition

Then:
  Phase 9-2 detailed design update and Start decision
```

## 6. Current Source Priority

2026-08-29 History SnapshotはPhase 6 Debtを新Phase 10へ移送していた。その後の2026-08-30 User Decisionは、Phase 9へ有界Reworkを戻し、Phase 10をProject-wide Integrationへ再構成した。

従って本Freezeは次をCurrentとして扱う。

```text
Current:
  Phase 9-1 = Phase 6中心Debt Rework
  Phase 10  = All-Docs／Shared Constitution／PADG／Full Runtime Constitution／UI

Historical only:
  Phase 6 Debt -> New Phase 10
  Phase 9 Final -> Phase 3〜9 Full Docs Closure
```

Current未解決Registryに古い移管先記述が残るため、Phase 8 Formal Closure／Roadmap更新時にCorrectionする。

## 7. Produced Documents

- `docs/project/phases/phase_9/requirements/phase_9_requirements_ja.md`
- `docs/project/phases/phase_9/architecture/phase_9_architecture_ja.md`
- `docs/project/phases/phase_9/operations/phase_9_execution_plan_ja.md`
- `docs/project/phases/phase_9/operations/phase_9_acceptance_matrix_ja.md`
- `docs/project/phases/phase_9/phase_index_ja.md`

## 8. Authority／Stop

本Freezeで許可されたMutationはPhase 9設計文書だけである。Phase 8 Closure、Roadmap、Source実装、Model Load、Network、Git、Backup、Phase 9 READY、PreflightまたはExecutor Handoffには進まない。
