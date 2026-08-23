# MARGPA Runtime LLM Phase 5 Index

```yaml
document_id: phase_5_index
status: complete_accepted_closed
phase: phase_5
active_subphase: phase_5_h_closed
language: ja
recorded_at: 2026-08-22 21:01:19 JST
owner_role: プロジェクト責任者兼設計統括者役
execution_provider_candidate: claude_code
implementation_authorized: false
automation_control_state: OFF
git_mutation_authorized: false
design_accepted: true
design_frozen: true
```

## 1. Current Decision

Phase 4はMain Runtime Governance、ARGD／DAGD Reference Binding、OFF／OBSERVE／ENFORCE、Evidence／Status／UIおよびQwen Mac Manual Acceptanceを完了した。意味Rule 109件が`Deferred`として正確に可視化され、Phase 6 Semantic Evaluator／Judge／Repairとの境界も実測した。

Phase 5はClaudeによる5-0～5-G連結実行、Codex独立Review、Exact Rework、User Mac Manual AcceptanceおよびMinimal Closureを完了した。Prompt Injection Markerに対し、OBSERVEは`Match 1／Action 0`で非介入、ENFORCEは`Match 1／Action 1`でModel Call前停止した。通常Chat、RAG／Citation Smoke、Mode再OpenおよびServer再起動もPASSした。

意味的Hallucination／知ったかぶり／根拠なき断定のJudge／RepairはPhase 6、RAG再構成後の最終品質評価はPhase 7へ正式延期した。いずれもPhase 5 Completion Blockerではない。

```text
Phase 4                    : COMPLETE／ACCEPTED／CLOSED
Phase 5 Program Design     : ACCEPTED／FROZEN
Phase 5 Implementation     : COMPLETE／ACCEPTED
Phase 5 Mac Acceptance     : PASS
Phase 5 Final State        : COMPLETE／ACCEPTED／CLOSED
Phase 6 Design             : CONTROLLER CANDIDATE PREPARED
Automation                 : OFF
Phase 6 Implementation     : NOT AUTHORIZED
Safety Model／AWS／Lightning: NOT AUTHORIZED
```

## 2. Goal

Milestoneは`Security and Authority-aware Runtime`。

- Guardrail ResultをMain Governance Resultから分離する。
- Deterministic Input／Context／Output／Streaming Guardを成立させる。
- Detection、Policy、Authority／Approval、Recommendation、Executed Actionを分離する。
- OFF／OBSERVE／ENFORCEをGuardrail独立Modeとして比較できるようにする。
- Secret／PII実値、未検査Streamおよび捛造Approvalを露出／実行しない。
- Phase 6 Judge／RepairがSafety／Authority Denyを上書きできない境界を固定する。

## 3. Subphase

```text
5-0 Entry／As-built Reconciliation／Threat Model／Freeze
5-A Contracts／Taxonomy／Ports
5-B Deterministic Input／Context Guard
5-C Output／Streaming Guard／Terminal Atomicity
5-D Policy／Authority／Approval／Conflict
5-E Optional Safety Model Seam／Calibration
5-F Runtime／Evidence／Configuration／Web／UI
5-G Integrated Adversarial COMPLETE_CANDIDATE
5-H Codex／User Minimal Closure
```

Claude担当は5-0～5-G、Codex／User担当は5-H。

## 4. Design Package

- [Cross-phase Program](../../shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md)
- [Requirements](requirements/phase_5_requirements_ja.md)
- [Architecture](architecture/phase_5_architecture_ja.md)
- [ADR](adr/phase_5_adr_ja.md)
- [Claude Governance](governance/phase_5_claude_execution_governance_ja.md)
- [Execution Plan](operations/phase_5_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_5_acceptance_matrix_ja.md)
- [Claude Handoff](handoffs/phase_5_claude_execution_handoff_ja.md)
- [Phase 5 As-built Reconciliation](history/operations/phase_5_as_built_reconciliation_ja_20260822095748.md)
- [Phase 5 Exact Design Freeze](history/operations/phase_5_exact_design_freeze_ja_20260822095748.md)
- [Phase 5 READY_FOR_BACKUP Receipt](history/operations/phase_5_ready_for_backup_receipt_ja_20260822095748.md)
- [Phase 5 Final Independent Review](handoffs/phase_5_codex_final_independent_review_acceptance_ja_20260822195345.md)
- [Phase 5 Mac Manual Acceptance](history/operations/phase_5_mac_manual_acceptance_ja_20260822210119.md)
- [Phase 5 Minimal Final Closure](history/operations/phase_5_minimal_final_closure_ja_20260822210119.md)

## 5. Included／Excluded

### Included

- Deterministic Guardrail／Taxonomy／Result／Point。
- Input／RAG Context／Output／Streaming Boundary。
- Policy／Authority／Approval Contract。
- Registered Security Actions。
- Guardrail OFF／OBSERVE／ENFORCE。
- Safe Evidence／Status／Local UI。
- Safety Model Port／Unavailable Baseline。

### Excluded

- Phase 6 Semantic Judge／Repair／LLM-as-a-Judge。
- Production Safety Model Download／Load／Promotion。
- Tool／Agent本体／External Side Effect／Human Approval UI完成。
- Phase 5-EX AWS、Lightning反映、URL公開／Secret／課金。
- DeepSeek Current Promotion、本格RAG GovernanceおよびProtected Full Capture。

## 6. Entry Gates

1. Phase 4 Technical Finding Closed：PASS。
2. Phase 4 User Mac Acceptance：PASS。
3. Phase 4 Minimal Closure：PASS。
4. Phase 5 As-built Reconciliation／Exact Freeze：PASS。
5. User Phase 5開始前Backup：PASS／USER REPORTED。
6. Codex Activation Preflight／`ARMED`：PASS。
7. User Start：PASS／EXECUTED。
8. Claude 5-0～5-G COMPLETE_CANDIDATE：PASS。
9. Codex Independent Review／Rework：PASS／OPEN MAJOR 0。
10. User Mac Acceptance：PASS。
11. Phase 5 Minimal Closure：PASS。

## 7. Next Safe Action

Phase 5を再Openしない。次はPhase 6 Design CandidateのController Review／Acceptance／Freezeである。Phase 6実装、Model Conversion／Load、Gitまたは外部操作は別Gate成立まで開始しない。

## 8. Recovery Entry

- [Phase 4 Minimal Final Closure](../phase_4/history/operations/phase_4_minimal_final_closure_ja_20260822095748.md)
- [Phase 4／5 Recovery Index](history/index/phase_4_closure_and_phase_5_ready_recovery_ja_20260822095748.md)
- [Phase 5 Exact Freeze](history/operations/phase_5_exact_design_freeze_ja_20260822095748.md)
- [Phase 5 READY Receipt](history/operations/phase_5_ready_for_backup_receipt_ja_20260822095748.md)
- [Phase 5 Activation Preflight／ARMED Receipt](history/operations/phase_5_activation_preflight_and_armed_receipt_ja_20260822101913.md)
- [Phase 5 Final Independent Review](handoffs/phase_5_codex_final_independent_review_acceptance_ja_20260822195345.md)
- [Phase 5 Mac Manual Acceptance](history/operations/phase_5_mac_manual_acceptance_ja_20260822210119.md)
- [Phase 5 Minimal Final Closure](history/operations/phase_5_minimal_final_closure_ja_20260822210119.md)
- [Phase 5／6 Recovery Index](history/index/phase_5_final_closure_and_phase_6_design_recovery_ja_20260822210119.md)
- [Phase 6 Index](../phase_6/phase_index_ja.md)
