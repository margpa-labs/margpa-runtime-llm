# Phase 6 UI-only Override／Phase 7 Progression Decision（P6-GOV-027）

```yaml
document_id: phase_6_gov027_user_override_ui_only_and_phase_7_progression_20260829164947
governance_id: P6-GOV-027
document_type: user_override_and_scope_stop
document_state: frozen
language: ja
created_at: 2026-08-29 16:49:47 JST
authority_owner: Nazuna Research
decision: stop_phase_6_core_rework_fix_ui_only_proceed_phase_7
```

## Decision

UserはP6-GOV-026で確定した中心機能FAILの影響を承知した上で、Phase 6の追加Reworkを停止し、指定UIだけを修正してPhase 7へ進むことを決定した。

この決定は、Selene、Qwen3Guard、Semantic 109件またはJudge／RepairがPASSしたことを意味しない。既知技術Debtとして未解決Registryへ保持する。

P6-GOV-026後に作成した次のHandoffは未実行のままsupersedeする。

`docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_final_p0_core_activation_semantic_repair_exact_handoff_ja_20260829164049.md`

## UI-only Result

- Sidebarを`<model> active`と`<profile> • <device> • <acceleration>`の2行へ修正し、Context表示を除去。
- Active Guardなしの表示を`未設定`へ修正。
- Governance Mode適用Failureの安全なCode／Messageを保持し、Status Refreshで消去しない。
- Historical RecordingをTurn／Judge Evidence別Labelへ修正。

```text
Frontend Typecheck: PASS
Frontend Lint: PASS
Focused Test: 3 files / 54 tests PASS
Frontend Build: PASS / 50 modules transformed
Backend semantic mutation: 0
```

## Phase Boundary

```text
Phase 6 Core Technical Acceptance: FAIL / known debt
Additional Phase 6 Core Rework: STOPPED BY USER
Phase 7 Progression: AUTHORIZED
False PASS Claim: prohibited
```
