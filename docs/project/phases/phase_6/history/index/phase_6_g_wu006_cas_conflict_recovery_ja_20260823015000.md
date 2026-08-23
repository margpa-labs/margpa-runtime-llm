# Phase 6-G-WU-006 CAS Conflict自己解消（Browser Sync要件の一部）

```yaml
document_id: phase_6_g_wu006_cas_conflict_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu006_partial_cas_conflict_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 01:50:00 JST
```

## 発見した問題（Self-review、Local Bug、Governance「局所Bugは自己解消」範囲内）

```text
症状: RuntimeModelStatusPanelのContext／Max New Tokens Apply失敗時（Stale CAS等）、
      同じ古いRevision／Digestのまま再Applyすると常に失敗し続ける
      （別Tab等でSnapshotが変わった後、本Panel側が自動的にCurrent値へ追従しない）。
初回修正の副作用: 失敗時に単純にrunFetch()（Loading状態を経由する通常Refresh相当）を
      呼ぶと、その再Fetch自体が失敗した場合にPanel全体がstatus=nullへ戻り、
      直前の「Failed to apply.」Messageごと消えてしまうRegressionをTest実行で検出
      （test_a_failed_context_apply...が実際にFAILした）。
```

## 修正

```text
resyncAfterApplyFailure()という専用の「Silent Resync」関数を新設。
Apply失敗時にこれを呼び、成功すればstatusのみ静かに更新（次回ApplyのCAS Tokenを
最新化）、失敗しても何もしない（capability変更なし、status変更なし）ことで、
直前のApply失敗Messageと既存表示を保持する。
```

## Validation

```text
New Frontend Test: 2 passed（Stale CAS Conflict後の自動Resync確認、Resync自体が
                    失敗してもPanelが消えないことを確認）
Full Frontend    : 187 passed／22 files（既存185 + 新規2、回帰0）
Full Backend     : 1403 passed／3 deselected（Frontend専用変更のため影響なし確認）
Lint／Typecheck／Build: Clean
```

## Next Exact Route

Phase 6-G-WU-006残り（別Tab同期の実Browser確認、Keyboard／Focus、Responsive Layout）、
またはPhase 6-H（Comparative Experiment）へ進む。
