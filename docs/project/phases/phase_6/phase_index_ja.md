# MARGPA Runtime LLM Phase 6 Index

    document_id: phase_6_index
    status: special_minimal_closed_with_known_debt
    phase: phase_6
    active_subphase: none
    language: ja
    recorded_at: 2026-08-22 22:08:04 JST
    owner_role: プロジェクト責任者兼設計統括者役
    execution_provider_candidate: claude_code
    implementation_authorized: false_closed
    automation_control_state: OFF
    git_mutation_authorized: user_authorized_for_closure
    design_accepted: true
    design_frozen: true

## 1. Current Decision

Phase 5のTechnical ReviewとUser Mac AcceptanceはPASSした。Prompt Injection Markerに対し、OBSERVEはMatch 1／Action 0でModel生成を継続し、ENFORCEはMatch 1／Action 1でguardrail_reject_inputとしてModel Call前停止した。設定再OpenとServer再起動もPASSした。

Phase 6は多数のRework、Controller ReviewおよびUser Mac Manualを経た。Runtime Model Control、Conversation継続、Recording、Stopおよび周辺基盤は成立したが、Selene／Qwen3Guard実Activation、Semantic 109件、Built-in Judge評価およびRepair Golden Pathは未成立だった。

Userは未解決をStable Registryへ保持し、技術合格へ昇格しないまま、Resource／Portfolio／PoC MVP優先による特殊最小ClosureとPhase 7移行を明示決定した。

    Phase 5 Technical Review : PASS
    Phase 5 Mac Acceptance   : PASS
    Phase 5 Closure          : COMPLETE／ACCEPTED／CLOSED
    Phase 6 Design           : ACCEPTED／FROZEN
    Phase 6 State            : SPECIAL MINIMAL CLOSED／KNOWN DEBT DEFERRED
    Phase 6 Technical Core   : ADJUST／NOT FULLY ACCEPTED
    Phase 6 Implementation   : CLOSED
    Automation               : OFF
    Phase 7                  : DESIGN ACCEPTED／FROZEN／READY

## 2. Goal

Milestoneは Measurable Safety, Evaluation, and Repair Runtime。

- DeepSeek Q4 Local FeasibilityとQwen Default維持。
- Server再起動不要Model Switch。
- Dynamic Context Size／Max New Tokens。
- Deterministic Judge／LLM-as-a-Judge。
- Authority／Budget付きBounded Repair。
- Request-correlated Observability。
- Safe Guardrail Refusal。
- Feedback／Recording。
- Current Runtime Identity／UI整理。
- Phase 4〜6 Runtime Governance MVP v1のTechnical AcceptanceとMinimal Closure。Phase 3〜9の累積Full ClosureはPhase 9で実施する。

## 3. Subphase

    6-0 Entry／As-built／Exact Freeze
    6-A DeepSeek Local Artifact／Backend Feasibility
    6-B Runtime Model／Context／Token Control
    6-C Evaluation／Dataset／Deterministic Judge
    6-D LLM-as-a-Judge／Calibration
    6-E Bounded Repair
    6-F Status／Safe Refusal／Feedback／Recording
    6-G Advanced Settings／Sidebar／UI Naming
    6-H Comparative Experiment
    6-I Integrated Verification／COMPLETE_CANDIDATE
    6-J Codex／User Minimal Technical Closure

Claude担当候補は6-0〜6-I、Codex／User担当は6-J。

## 4. Design Package

- [Cross-phase Program](../../shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md)
- [Requirements](requirements/phase_6_requirements_ja.md)
- [Architecture](architecture/phase_6_architecture_ja.md)
- [ADR](adr/phase_6_adr_ja.md)
- [Claude Governance](governance/phase_6_claude_execution_governance_ja.md)
- [Execution Plan](operations/phase_6_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_6_acceptance_matrix_ja.md)
- [Claude Execution Handoff](handoffs/phase_6_claude_execution_handoff_ja.md)
- [Controller Design Review](history/operations/phase_6_controller_design_review_ja_20260822211308.md)
- [Exact Design Freeze](history/operations/phase_6_exact_design_freeze_ja_20260822211308.md)
- [READY_FOR_BACKUP Receipt](history/operations/phase_6_ready_for_backup_receipt_ja_20260822211308.md)
- [Phase 6〜9 Cumulative Full Closure Scope Correction](history/operations/phase_6_to_9_cumulative_full_closure_scope_correction_ja_20260822214404.md)
- [Dependency Acquisition Authority Receipt](history/operations/phase_6_dependency_acquisition_authority_receipt_ja_20260822220804.md)

主要予約Source：

- [DeepSeek／Dynamic Control Design](../../shared/history/planned_work/phase_6_0_deepseek_local_runtime_switch_design_ja_20260822105531.md)
- [DeepSeek Handoff Reservation](../../shared/history/planned_work/phase_6_0_deepseek_local_runtime_switch_handoff_ja_20260822105531.md)
- [Advanced Runtime Identity](../../shared/history/planned_work/phase_6_0_advanced_runtime_component_identity_projection_ja_20260822150342.md)
- [Mode／Constitution Separation](../../shared/history/planned_work/phase_6_8_component_identity_mode_and_constitution_separation_followup_ja_20260822151607.md)
- [Integrated Scope／Constitution Label](../../shared/history/planned_work/phase_6_integrated_scope_and_current_constitution_layer_label_followup_ja_20260822152513.md)
- [Phase 9 Context Compaction／Recovery／Governance Trace Observatory Reservation](../../shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md)
- [Runtime Data／Recording](../phase_2/architecture/phase_2_runtime_data_root_and_recording_architecture_ja.md)

## 5. User Decisions Incorporated

1. Startup DefaultはQwen。
2. DeepSeek-R1-0528-Qwen3-8BはQ4_K_M Local Candidate。
3. 起動中にQwen／DeepSeekを切替可能にする。
4. Context SizeとMax New Tokensを実Capability上限内で動的変更する。
5. Current Main／Guardrail／Judge ModelとGovernance LayerをAdvanced Settingsへ表示する。
6. Guardrail Rejectを生Errorではなく安全な会話表示へする。
7. Current Requestで未実行のPointへ前Request結果を混ぜない。
8. 利用者向け機能名へPhase番号Suffixを付けない。
9. Phase 3専用設定UIを整理し、内部Definition基盤は残す。
10. Judge／Repair／Recordingを含む対応機能はDefault OFF。
11. RecordingはOFF／METADATA／FULL、Protected Captureは別CapabilityでDeferred。
12. RAG回答品質の最終定性評価はFull RAG実装後のPhase 7で行う。
13. Current Constitution LayerはPhase 8で追加し、Current Governance Layerと分離する。
14. Phase 6〜8はMinimal Technical Closureとし、Phase 3〜9の累積Docs統合／Full ClosureはPhase 9で実施する。
15. Phase 9後半に、利用可能量とAs-builtが許す範囲で、Native Context Compaction／Recovery、
    Handoff／Manual Compaction ButtonおよびFull Raw Governance Trace Observatoryを優先候補とする。
    本予約はPhase 6のImplementation／Closure Scopeを変更しない。

## 6. Included／Excluded

### Included

- Local Qwen／DeepSeek Model-neutral Runtime。
- Evaluation／Judge／Repair／Observability。
- Safe Presentation／Feedback／Recording。
- Advanced Settings／Sidebar／Naming Cleanup。
- Qwen／DeepSeek比較。

### Excluded

- Phase 7 Full RAGと最終RAG品質評価。
- Phase 8 Agent／Tool／MARGPA Constitution。
- AWS／Lightning／Desktop／一般公開。
- DeepSeek V4 Local、Cloud常時運用。
- Dedicated Guard／Judge Model Download。
- Protected Research Capture。

## 7. Entry Gates

1. Phase 5 Technical Review：PASS。
2. Phase 5 User Mac Acceptance：PASS。
3. Phase 5 Full／Minimal Closure：PASS。
4. Phase 6 Design Review／Acceptance／Freeze：PASS。
5. User Phase 6開始前Backup：PASS／USER REPORTED COMPLETE。
6. Model Artifact／Disk／Memory Authority：PASS／EXACT RECEIPT FIXED。
7. models Symlink Resolved Target／DeepSeek Subtree Authority：PASS／EXACT RECEIPT FIXED。
8. Codex Activation Preflight／ARMED：PASS。
9. User Start：PASS／DECLARED。
10. Scoped Phase 6 Dependency Acquisition Authority：PASS。

## 8. Next Safe Action

Phase 7 READY Sequenceに従い、Closure Commit／Push、Backup、Preflightを完了してから、Phase 7 Exact HandoffのP7-0へ進む。Phase 6既知DebtをPhase 7 Executorが無断修正しない。

## 9. Predecessor Closure

- [Phase 5 Final Independent Review](../phase_5/handoffs/phase_5_codex_final_independent_review_acceptance_ja_20260822195345.md)
- [Phase 5 Mac Manual Acceptance](../phase_5/history/operations/phase_5_mac_manual_acceptance_ja_20260822210119.md)
- [Phase 5 Minimal Final Closure](../phase_5/history/operations/phase_5_minimal_final_closure_ja_20260822210119.md)
- [Phase 5／6 Recovery Index](../phase_5/history/index/phase_5_final_closure_and_phase_6_design_recovery_ja_20260822210119.md)

## 10. Phase 6 Freeze／Backup Gate

- [Controller Design Review](history/operations/phase_6_controller_design_review_ja_20260822211308.md)
- [Exact Design Freeze](history/operations/phase_6_exact_design_freeze_ja_20260822211308.md)
- [READY_FOR_BACKUP Receipt](history/operations/phase_6_ready_for_backup_receipt_ja_20260822211308.md)
- [Exact Model Authority Receipt](history/operations/phase_6_exact_model_authority_receipt_ja_20260822212732.md)
- [Activation Preflight／ARMED Receipt](history/operations/phase_6_activation_preflight_and_armed_receipt_ja_20260822212732.md)
- [Phase 6〜9 Cumulative Full Closure Scope Correction](history/operations/phase_6_to_9_cumulative_full_closure_scope_correction_ja_20260822214404.md)
- [Dependency Acquisition Authority Receipt](history/operations/phase_6_dependency_acquisition_authority_receipt_ja_20260822220804.md)
- [Phase 6-0 Entry Recovery](history/index/phase_6_0_entry_reconciliation_and_freeze_recovery_ja_20260822214550.md)
- [Phase 6-A Toolchain Authority Wait](history/index/phase_6_a_wu001_toolchain_blocked_deferral_ja_20260822215600.md)

## 11. Final Special Minimal Closure

- [User Mac Core Failure／Claim Correction](history/operations/phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_ja_20260829164049.md)
- [User Override／Phase 7 Progression](history/operations/phase_6_gov027_user_override_ui_only_and_phase_7_progression_ja_20260829164947.md)
- [Special Minimal Closure](history/operations/phase_6_special_minimal_closure_with_known_debt_ja_20260829171422.md)
- [Closure／Phase 7 READY Recovery](history/index/phase_6_special_minimal_closure_and_phase_7_ready_recovery_ja_20260829171422.md)
- [Current Unresolved Registry](../../shared/未解決/current_unresolved_findings_registry_ja.md)
- [Phase 7 Index](../phase_7/phase_index_ja.md)
