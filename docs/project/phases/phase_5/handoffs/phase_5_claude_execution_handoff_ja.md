# Phase 5 Claude Execution Handoff

```yaml
document_id: phase_5_claude_execution_handoff
status: accepted_frozen_ready_for_backup_not_activated
phase: phase_5
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
recorded_at: 2026-08-22 09:57:48 JST
automation_control_state: OFF
implementation_authorized: false
completion_line: phase_5_g_complete_candidate
```

## 1. Current Instruction

本HandoffはAccepted／Frozenの`READY_FOR_BACKUP`であり、実行開始指示ではない。UserのPhase 5開始前Backup報告、Codex Activation Preflight／`ARMED`、その後のUser Startが全て成立した場合だけActivateする。

## 2. Mandatory Reading Order

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`
5. `docs/project/shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md`
6. `docs/project/phases/phase_4/history/operations/phase_4_minimal_final_closure_ja_20260822095748.md`
7. `docs/project/phases/phase_4/handoffs/phase_4_claude_state_observability_rework_complete_candidate_handoff_ja.md`
8. `docs/project/phases/phase_5/phase_index_ja.md`
9. Phase 5 Requirements／Architecture／ADR。
10. Phase 5 Governance／Execution Plan／Acceptance Matrix。
11. `docs/project/current/governance/runtime_governance_specification_ja.md`
12. Phase 4 As-built Source／Test／Frontendの必要範囲。
13. Phase 5開始時Activation Receipt（まだ存在しない。作られるまで開始不可）。

Provider Memory、Conversation Summary、Timestampの新しさまたは自己の記憶で正本を代替しない。

## 3. Execution Objective

Phase 5-0からPhase 5-Gまでを依存順に連結実行し、Qwen Current RouteでGuardrail／Security／Policy／AuthorityのOFF／OBSERVE／ENFORCEを成立させる。Subphase境界でRecoveryを残すが、状況報告だけを理由に停止しない。

## 4. Required Behavior

- WU開始前にFrozen ContractとAs-builtからExact Mutationを動的に決める。
- 必要なSource／Testだけを作り、固定Packageを機械的に量産しない。
- Local Bug、Test Failure、Frozen Scope内の設計具体化はSelf-review／局所Reworkして継続する。
- Deterministic Baselineを必須とし、Safety Model成功を捛造しない。
- Security／Authority／Streaming／Privacy／Concurrency境界をAdversarialに検証する。
- Completion時は実測Test数、Exact Mutation、Evidence Class、Open Major Finding、Compaction／Quota RecoveryおよびHuman Burdenを日本語で報告する。

## 5. Forbidden

- Project Root外、Provider Memory、User実`runtime_data/`、Git／GitHub、Network、Model Download／Load、AWS／Lightning、Secret／課金。
- Existing Stable Docs／Existing Historyの無断変更。
- Phase 5-H／Final Closure／Phase 5-EX／Phase 6の開始。
- Human Approval／Tool Permission／External Authorityの捛造。
- Unknown／Timeout／Unsupported／Low ConfidenceのSafe Allow化。
- Secret／PII実値のEvidence／Status／Log化。
- Definition名、Model名、Absolute Path／固定件数のCore Hard-code。

## 6. Completion Handoff

`docs/project/phases/phase_5/handoffs/phase_5_claude_complete_candidate_handoff_ja.md`を新規作成し、次を記録して停止する。

```text
Phase 5-G Recommendation
Technical／Security Blockers
Governance Incidents
Controller-owned Work
Deferred Evidence／Current Impact
Exact Mutation
Focused／Subphase／Full／Static／Frontend
OFF／OBSERVE／ENFORCE Matrix
Input／Context／Stream／Output Adversarial Evidence
Policy／Authority／Approval／Action Evidence
Secret／PII Non-disclosure Evidence
Compaction／Quota Recovery／Human Burden
Root／Git／User Data／External Evidence Class
Next Action: Codex Phase 5-H Independent Review only
```

## 7. Activation Gate

```text
Current State : ACCEPTED／FROZEN／READY_FOR_BACKUP／OFF
Needed        : User Backup → Codex Activation Preflight
                → Codex ARMED → User Start
```
