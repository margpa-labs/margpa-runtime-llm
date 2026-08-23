# Phase 4 Claude Execution Handoff

```yaml
document_id: phase_4_claude_execution_handoff
status: accepted_frozen_ready_for_backup_not_activated
phase: phase_4
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
recorded_at: 2026-08-21 22:04:22 JST
automation_control_state: OFF
implementation_authorized: false
completion_line: phase_4_g_complete_candidate
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Current Instruction

本HandoffはAccepted／Frozenされ、Phase 4は`READY_FOR_BACKUP`である。ただし現時点では実行開始指示ではない。ユーザーがBackup完了を報告し、Codexが開始直前Preflightと`ARMED`を宣言し、その後ユーザーが開始を明示した場合だけ有効化する。

## 2. Mandatory Reading Order

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md`
5. `docs/project/phases/phase_4/phase_index_ja.md`
6. Phase 4 Requirements／Architecture／ADR。
7. Phase 4 Governance／Execution Plan／Acceptance Matrix。
8. `docs/project/current/governance/runtime_governance_specification_ja.md`
9. Phase 3 Final Closure／As-built Recovery／最新Codex Review。
10. `definitions/manifest.json`とPhase 3 Definition Inventory。
11. `docs/project/phases/phase_4/history/operations/phase_4_as_built_reconciliation_ja_20260821232056.md`。
12. `docs/project/phases/phase_4/history/operations/phase_4_exact_design_freeze_ja_20260821232056.md`。
13. Phase 4開始時Activation Receipt。

Provider Memory、会話SummaryまたはTimestampの新しさだけで正本を決めない。

## 3. Execution Objective

Phase 4-0からPhase 4-Gまでを依存順に実行し、Qwen Current RouteでMain Model Governance OFF／OBSERVE／ENFORCE MVPを成立させる。Subphase境界ではRecoveryを残すが、報告だけを理由に停止せずPhase 4-Gまで継続する。

## 4. Required Behavior

- Work Unit開始前にExact MutationをFrozen要件とAs-built Sourceから動的決定する。
- 必要なSource／Testだけを作り、固定Packageを機械的に量産しない。
- Local Bug、Test Failure、Frozen範囲内の設計不整合は自己Review／局所Reworkする。
- Major Security／Authority／Recovery境界をAdversarialに再検証する。
- Completion時、実測Test数、Exact Mutation、Evidence ClassおよびOpen Findingを日本語で報告する。

## 5. Forbidden

- Project Root外、Provider Memory、User実`runtime_data/`、Git、Network、AWS、Secret、Model Download／Load。
- Stable Existing Docs／Existing Historyの無断変更。
- DeepSeek Current Promotion。
- Phase 5／6実装、Phase 4-H、Final Closure。
- Repair／Regenerateの自動反復。
- Definition名、Model名またはAbsolute PathのCore Hard-code。

## 6. Completion Handoff

新規`docs/project/phases/phase_4/handoffs/phase_4_claude_complete_candidate_handoff_ja.md`へ次を記録して停止する。

```text
Phase 4-G Recommendation
Technical Blockers
Governance Incidents
Controller-owned Work
Deferred Evidence／Current Impact
Exact Mutation
Focused／Subphase／Full／Static／Frontend
OFF／OBSERVE／ENFORCE Matrix
Qwen Manual／Automated Evidence
Compaction Recovery／Human Burden
Root／Git／User Data／External Evidence Class
Next Action: Codex Phase 4-H Independent Review only
```

## 7. Activation Gate

```text
Current State : ACCEPTED／FROZEN／READY_FOR_BACKUP／OFF
Needed        : User Backup → Activation Preflight
                → Codex ARMED → User Start
```
