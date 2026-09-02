# Phase 9 Documentation Index

```yaml
document_id: phase_9_documentation_index
document_state: P9_1_JUDGE_COMMON_SUBSTRATE_REWORK_REQUIRED
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
current_program: P9_1_JUDGE_COMMON_SUBSTRATE_REWORK_REQUIRED
implementation_started: true
phase_8_formal_closure_required_first: false
user_backup_complete: true
phase_9_1_preflight: go
```

## 1. Current State

```text
Phase 8 Implementation／User Manual: COMPLETE／ACCEPTED／CLOSED
Phase 8 Formal Closure: COMPLETE
Phase 9 Design／Work Breakdown: ACCEPTED／FROZEN
Phase 9 READY: TRUE
User Backup after Phase 8 Commit／Push: COMPLETE（User Report）
Phase 9-1 Preflight: GO／COMPLETE
Phase 9-1 Claude Exact Handoff: READY
Phase 9-1 Claude First Candidate: CONTROLLER REVIEWED／REWORK REQUIRED
Phase 9-1 Controller Bounded Rework Handoff: READY
Phase 9-1 Controller Bounded Rework P9-CODEX-001〜005: COMPLETE CANDIDATE
Phase 9-1 Codex Controller Source／Docs Finding Review: P9-CODEX-001〜005 ACCEPTED
Phase 9-1 User Closure Correction: REAL SELENE／QWEN3GUARD MANDATORY
Phase 9-1 Acceptance: PASS 35／MANDATORY REAL ARTIFACT NOT RUN 2／USER MANUAL GATE 1
Phase 9 Source Implementation: REAL DEDICATED ACTIVATION REQUIRED BEFORE COMPLETE CANDIDATE
Phase 9-1 Copilot P9-CODEX-006〜010 Return: CONTROLLER REVIEWED／REWORK REQUIRED
Phase 9-1 Copilot Terra Max P9-CODEX-011〜014 Continuation: QUOTA EXHAUSTED／PARTIAL／REWORK REQUIRED
Phase 9-1 2026-09-01 User Mac Manual: FAIL／ADJUST／REWORK REQUIRED
Phase 9-1 2026-09-02 Judge Recheck: MAIN-SHARED MALFORMED／BUILT-IN EVALUATED 0／ALL JUDGE OPERATIONALLY UNAVAILABLE
Phase 9-1 Root Cause: COMMON JUDGE SUBSTRATE FIRST HYPOTHESIS／NOT YET CONFIRMED
Phase 9-1 Next Entry: LIGHTWEIGHT INDEPENDENT JUDGE SELECTION AFTER QUOTA RECOVERY
Phase 9-1 Current Open Findings: P9-CODEX-011〜017／UF-P9-002〜004／UF-P9-007
Phase 9-1 Current Validation: 2214 PASS／2 FAIL／7 DESELECTED、Mypy 45 Errors、Ruff PASS
Phase 9-1 Closure: NOT CLAIMED
```

## 2. Three-program Decision

| Program | Purpose | Current Detail | Start Condition |
|---|---|---|---|
| Phase 9-1 | Phase 6 Governance Semantic Debt Fast Closure | Requirements／Architecture／23 WU／38 Acceptanceを詳細Freeze | User Backup、Preflight、Exact Handoff |
| Phase 9-2 | Experiment／Evaluation／Multi-Governance／Semantic Research | 6 Package／7 Acceptanceの境界予約 | P9-1 Controller Review＋User Checkpoint |
| Phase 9-3 | Context Compaction／Recovery Technical Core | 6 Conditional Package／5 Acceptanceの境界予約 | P9-2成立＋Resource／Priority再評価 |

## 3. Canonical Phase 9 Documents

- [Requirements](requirements/phase_9_requirements_ja.md)
- [Architecture](architecture/phase_9_architecture_ja.md)
- [Execution Plan](operations/phase_9_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_9_acceptance_matrix_ja.md)
- [Pre-Phase-8-Closure Design Freeze](history/operations/phase_9_pre_phase_8_closure_three_program_design_and_execution_freeze_ja_20260831210244.md)
- [Phase 9 READY Receipt](history/operations/phase_9_ready_receipt_ja_20260831213232.md)
- [Phase 9-1 Preflight](history/operations/phase_9_1_governance_semantic_debt_preflight_ja_20260831221231.md)
- [Phase 9-1 Claude Four-percent Resource-bounded Long-run Exact Handoff](handoffs/phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_handoff_ja_20260831221823.md)
- [Phase 9-1 Claude First Exact Return](handoffs/phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_return_handoff_ja_20260901033000.md)
- [Phase 9-1 Codex Controller Independent Review／Finding Ledger](history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md)
- [Phase 9-1 Claude One-percent Controller Bounded Rework Handoff](handoffs/phase_9_claude_p9_1_one_percent_controller_bounded_rework_exact_handoff_ja_20260831231243.md)
- [Phase 9-1 Post-Claude Quota Codex Exact Continuation](handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_continuation_exact_handoff_ja_20260831234357.md)
- [Phase 9-1 Acceptance Disposition Addendum](history/operations/phase_9_1_post_claude_quota_acceptance_disposition_addendum_ja_20260831234930.md)
- [Phase 9-1 Corrected User Manual／Recheck Sheet](history/operations/phase_9_1_corrected_user_manual_recheck_sheet_ja_20260831234930.md)
- [Phase 9-1 Post-Claude Quota Continuation Recovery](history/index/phase_9_1_post_claude_quota_continuation_recovery_ja_20260831234930.md)
- [Phase 9-1 Post-Claude Quota Exact Return](handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_exact_return_handoff_ja_20260831234930.md)
- [Phase 9-1 Maximum Claim Correction Addendum](history/operations/phase_9_1_maximum_claim_correction_addendum_ja_20260901000630.md)
- [Phase 9-1 P9-CODEX-005 Micro Recovery](history/index/phase_9_1_p9_codex_005_maximum_claim_micro_recovery_ja_20260901000630.md)
- [Phase 9-1 Maximum Claim Corrected Exact Return](handoffs/phase_9_codex_designer_implementer_p9_1_maximum_claim_corrected_exact_return_handoff_ja_20260901000630.md)
- [Phase 9-1 Codex Controller Final Re-review Acceptance Receipt](history/operations/phase_9_1_codex_controller_final_re_review_acceptance_receipt_ja_20260901001158.md)
- [Phase 9-1 Real Selene／Qwen3Guard Mandatory Closure Correction](history/operations/phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_ja_20260901001700.md)
- [Phase 9-1 Post-Copilot Real Dedicated Independent Review](history/operations/phase_9_1_codex_controller_post_copilot_real_dedicated_independent_review_finding_ledger_ja_20260901112423.md)
- [Phase 9-1 Terra Max Fresh Rework Exact Handoff](handoffs/phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_ja_20260901113052.md)
- [Phase 9-1 Terra Max Quota Exhaustion Partial State Review](history/operations/phase_9_1_codex_controller_terra_max_quota_exhaustion_partial_state_review_ja_20260901122823.md)
- [Phase 9-1 User Mac Full Manual Result／Unresolved／Reservation Evidence](history/operations/phase_9_1_user_mac_full_manual_result_unresolved_and_reservation_evidence_ja_20260901184023.md)
- [Phase 9-1 All-Judge Operational Failure／Common-substrate Hypothesis／Rework Order](history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md)
- [Phase 8 Closure／Phase 9 READY Canonical Verification](../phase_8/history/operations/phase_8_closure_phase_9_ready_canonical_verification_receipt_ja_20260831213232.md)

## 4. Primary Inputs

- `docs/public/roadmap_ja.md` Phase 9 Current Plan。
- `docs/public/roadmap_summary_ja.md` Phase 9 Summary。
- `docs/project/phases/phase_6/history/operations/phase_6_special_minimal_closure_with_known_debt_ja_20260829171422.md`。
- `docs/project/phases/phase_6/history/operations/phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_ja_20260829164049.md`。
- `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`。
- `docs/project/shared/history/planned_work/phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md`。
- `docs/project/shared/history/planned_work/phase_9_stale_conversation_fact_semantic_governance_and_progressive_presentation_reservation_ja_20260830190930.md`。
- `docs/project/shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md`。
- `docs/project/shared/history/planned_work/phase_8_post_mr8_manual_deferred_phase_9_10_11_routing_reservation_ja_20260831181553.md`。

## 5. Source Priority Correction

過去Historyにある「Phase 6中心Debtを新Phase 10へ移管」および「Phase 9 FinalでPhase 3〜9全Docs統合」は、後続User Decisionで再編された過去Snapshotである。Current境界は次とする。

```text
Phase 9 : Governance Semantic Debt + Experiment／Multi-Governance + Context Core
Phase 10: All-Docs Integration + Shared Constitution + PADG + Full Runtime Constitution + UI Consolidation
```

Phase 8 Formal ClosureでCurrent RoadmapおよびCurrent未解決Registryへこの優先順位を反映した。History Snapshotは改変しない。

## 6. Next Authorized Sequence

```text
1. AI利用可能量回復後、Local Mac向け軽量独立Judge候補を選定／取得する
2. Built-in／Main-shared Qwen／Selene／軽量Judgeの同一条件比較Matrixを作る
3. Criteria／Semantic Snapshot／Prompt／Inference／Decode／Projection／Lifecycleを含む共通Judge基盤を先に診断／修復する
4. 残るProvider固有差分を修復し、各JudgeのOBSERVE／ENFORCEを成立させる
5. Judge→Repair→RejudgeおよびSemantic 109のBudget内実評価を成立させる
6. Judge問題解決後、ARGD／DAGDを含むMain Runtime Governance ENFORCE Golden Pathを成立させる
7. Real Qwen3Guardの成立済み基本Baselineを短く再確認する
8. User Mac Manual Gateを実施する
9. 上記成立までPhase 9-1 Complete Candidate／Closure／Phase 9-2を主張しない
```

本Indexは上記Actionの実行Authorityを生成しない。
