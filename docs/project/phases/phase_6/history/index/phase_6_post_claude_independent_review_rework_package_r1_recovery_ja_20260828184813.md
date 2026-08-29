# Phase 6 Post-Claude Independent Review Rework — Package R1 Recovery（Atomic Provider／Mode／Lifecycle Transaction）

```yaml
document_id: phase_6_post_claude_independent_review_rework_package_r1_recovery_20260828184813
package: P6-RR-R1
completed_wu: R1-WU-001, R1-WU-002, R1-WU-003, R1-WU-004, R1-WU-005, R1-WU-006, R1-WU-007
status: PACKAGE_COMPLETE
created_at: 2026-08-28 18:48:13 JST
predecessor: phase_6_post_claude_independent_review_rework_package_r1_entry_ja_20260828184524.md
task_owned_temp: .venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
git_action: 0
network_action: 0
root_outside_action: 0
```

## 対象Finding

```text
P6-CODEX-062: Provider Selection／Mode／Lifecycleが非Atomic -> RESOLVED（本Package）
```

## R1-WU-001〜R1-WU-006 — 実装

### 設計（詳細はPackage R1 Entry §2参照）

Mode-Apply経路（`feature_modes_routes.py`のJudge、`configuration_control.py`の
`_GuardrailGovernanceModeApplierAdapter`のGuard）は、既にActivation-before-Mode-Commitを
正しく実装済みであることを確認し、変更しなかった（Redo禁止原則の遵守）。

実際のGapは`provider_selection_routes.py`のJUDGE／GUARD Provider Selection経路にのみ存在した。
`ProviderSelectionController.select()`自体が「Selectionは暗黙のLoadを行わない」設計であるため、
Selection経路でActivationを試みるのではなく、Configured実変更時にその場でMode를OFFへ強制
Rollbackし、旧Adapterを無条件Drainする方式を採用した（Addendum M-WU-005の
「旧Activeを維持するかMode OFFへRollback」のうちRollback側）。

### Changed Files

```text
[変更]
src/margpa_runtime_llm/web/provider_selection_routes.py
  新規関数 _apply_role_provider_selection() 追加。JUDGE／GUARD Roleの
  PUT /api/v6/provider-selection/{role} を、Configured実変更時のみ次のAtomic
  Transactionへ変更：
    1. controller.select() でConfigured変更（既存動作維持）。
    2. revision不変（no-op再選択）なら即Return——Mode強制OFFを一切行わない。
    3. role_provider_lifecycle.deactivate(role) を無条件実行——旧Adapterを
       常にDrain／Unload（R1-WU-005）。
    4. Judge: judge_mode_control.mode_snapshot().current_mode ≠ OFFなら
       apply_mode(OFF)。
       Guard: guardrail_governance_composition.mode_controller.current_mode_value()
       ≠ "off"なら apply_mode(GovernanceMode.OFF)。
       （JudgeとGuardへ同一Contractを適用——R1-WU-006）
  MAIN Roleの既存 _apply_main_provider_selection() は無変更。

[新規Test]
tests/integration/web/test_provider_selection_role_atomicity.py（5 tests）
  - test_judge_provider_change_while_enforce_forces_mode_off_and_drains_active
    （P6-GOV-018 Scenario B Judge版の再現と修正確認）
  - test_guard_provider_change_while_enforce_forces_mode_off_and_drains_active
    （同上Guard版、R1-WU-006の同一Contract確認）
  - test_judge_provider_change_while_mode_off_leaves_mode_untouched
    （既存安全経路への非破壊確認）
  - test_judge_reselecting_current_provider_is_noop_and_never_forces_mode_off
    （No-op再選択がModeを誤ってOFF化しないことの確認）
  - test_judge_provider_change_drains_stale_adapter_even_without_lifecycle_race
    （Turn Lease経由でのDrain確認、既存deactivate()のPending-unload契約を再利用）
```

## R1-WU-007 — Package R1 Recovery Index作成

本File自体がFinal Recovery Indexを兼ねる。

## Focused Evidence

```text
Command: ./.venv/bin/mypy src/margpa_runtime_llm/web/provider_selection_routes.py
         tests/integration/web/test_provider_selection_role_atomicity.py
Result : Success: no issues found in 2 source files

Command: ./.venv/bin/ruff check <上記2File>
Result : All checks passed!

Command: ./.venv/bin/ruff format --check <上記2File>
Result : 2 files already formatted

Command: ./.venv/bin/pytest
         tests/integration/web/test_provider_selection_main_switch.py
         tests/integration/web/test_provider_selection_role_atomicity.py
         tests/unit/adapters/runtime_model_control/
         tests/unit/bootstrap/test_judge_live_integration.py
         tests/unit/guardrail_governance/
         tests/unit/adapters/guardrail_governance/
Result : 206 passed（新規5件含む、既存201件Regression 0）

Command: ./.venv/bin/pytest tests/ -k "provider_selection or role_lifecycle or feature_modes"
Result : 34 passed, 1661 deselected（Regression 0、広範Keyword一致確認）
```

## Acceptance再確認（P6-DELTA-021/022/023、R8で最終Acceptance再導出時に反映）

```text
P6-DELTA-021（Dedicated Configured／Active noneの状態でOBSERVE／ENFORCEを正常Commitしない）:
  R1修正により、Judge／Guard Provider Selection経由での`Mode ON / Active none`Commitパスが
  解消された。既存のMode-Apply経路（Activation-before-Commit）と合わせ、両経路とも
  `Mode ON / Active none`を生成し得ない。Controllerの以前の判定「PARTIAL／Scenario B FAIL」の
  うちScenario B部分をR1で解消したとみなす——最終Dispositionの確定はR7 Fixture Regression
  （P6-GOV-018 Scenario A〜C、P6-GOV-019 Reproduction）実行後にR8で行う。

P6-DELTA-022（Built-in→Dedicated変更のProvider／Mode TransitionがAtomicで、false ENFORCEを
  残さない）: 同上、R1で解消。

P6-DELTA-023（Configured／Active／Executedが別々に記録され、ExecutedをConfiguredから推測しない）:
  R1はConfigured／Active分離の一部（Selection経路でのActive誤放置防止）を解消したが、
  Executed Identity自体の分離・推測排除（judge_live_integration.py:582等）はP6-CODEX-063として
  R2で対応する。R1単独ではP6-DELTA-023をFull PASSへ昇格しない。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-062はRESOLVED。P6-CODEX-063〜067は引き続きOpen、R2〜R6で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま、本Package内で新規Git Actionなし）
Git Mutation      : 0
Network Action     : 0
Provider Memory    : 0
User runtime_data  : 0
Root外Persistent Write: 0 known
```

## Task-owned Temporary／Active Process／Loaded Model

```text
Task-owned Temp: .venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
Active Process : 0
Loaded Model   : 0（本Package内でReal Model Loadは未実施、全てFixture／Fake Backend）
```

## Exact Next Action

```text
next_exact_work_unit: P6-RR-R2-WU-001
```
