# Phase 6 Current Claude Task — Package R13 Final Recovery（Unified Role Transition Transaction）

```yaml
document_id: phase_6_current_claude_task_r13_final_recovery_20260828223716
package: P6-RR-R13
status: PACKAGE_COMPLETE
created_at: 2026-08-28 22:37:16 JST
active_contract: phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_ja_20260828221510.md
active_contract_sha512: c7d731d1d0033b7ba884293e3784f21d547bee4b2230434bb087e8de542678a76f3c42417e78aeab786f3672dbc9d26b97deee4a60466e35ceed8623f5055256
preserved_baseline: current_working_tree_after_claude_and_copilot_r0_to_r12（無変更部分は再実装せず）
git_action: 0（既知Incident1件、後述）
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-074: Role Provider／Modeの真のAtomicity未成立（reopens 069, 062） -> RESOLVED（本Package）
```

## 設計

Current Source再読により、Copilot R9〜R12は既に`RoleProviderLifecycleManager.transition_to()`（Candidate
Preflight／Loadを先に行い、成功後にOld Unload・Selection Commitへ進む、失敗時は旧Tuple保持のRollback）
を実装済みであることを確認した。一方、実際のGapはCodexのFinding記載どおり、`provider_selection_routes.
_apply_role_provider_selection()`がModeをLock外で読み、その後に別Lockを持つ`transition_to()`または
`ProviderSelectionController.select()`へ進む点、および`feature_modes_routes.apply_judge()`／
`configuration_control._GuardrailGovernanceModeApplierAdapter.apply()`がActivate（Lifecycle Lock内）
を実行した後、Lock外でMode Commitを行う点にあった。

修正方針：`RoleProviderLifecycleManager`自身の`self._condition`を、Role単位のUnified Transaction
Lock Boundaryとする。Mode Commitを行うCallable（`commit_mode`）と、Mode現在値を読むCallable
（`mode_is_on`）を、このLockを握ったまま呼び出す新規Public Method（`apply_mode_transition`、
`apply_provider_selection`）を追加し、既存の`activate()`／`deactivate()`／`transition_to()`は
内部Private Helper（`_activate_locked`／`_deactivate_locked`／`_transition_to_locked`）へ委譲する
形で保持した（直接呼び出すTest／Callerとの後方互換性を維持）。

## Changed Files

```text
[変更]
src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py
  - activate()/deactivate()/transition_to()の本体を_activate_locked/_deactivate_locked/
    _transition_to_locked（Lock取得済み前提のPrivate Helper）へ分離。
  - 新規Public Method追加：
      apply_mode_transition(role, target_mode_is_off, commit_mode: Callable[[], None])
      apply_provider_selection(role, provider_id, expected_revision, expected_digest,
                                mode_is_on: Callable[[], bool])
    いずれも単一のself._conditionを握ったまま、Mode Read／Commitと
    Provider Activate／Transition／Selectを同一Criticalセクションで実行する。
  - _transition_to_locked内、previous_adapter.unload()が例外を送出した場合の挙動を修正：
    従来はController状態を無変更のままRaiseするだけだった（旧Active Tupleが「保全」されたと
    誤認され得た）。修正後はreplace_runtime_state(..., state=DEGRADED,
    failure_reason="previous_provider_unload_failed:<ExceptionType>")を呼び、
    信頼できないAdapterを_active_adaptersから除去してからRaiseする
    （P6-CODEX-074「それを完全Rollbackと主張してはならない」に対応）。

src/margpa_runtime_llm/web/feature_modes_routes.py
  apply_judge(): activate()単独呼び出し+Lock外Mode Commitを、
  role_provider_lifecycle.apply_mode_transition(commit_mode=...)への単一呼び出しへ置換。

src/margpa_runtime_llm/bootstrap/configuration_control.py
  _GuardrailGovernanceModeApplierAdapter.apply(): 同様にapply_mode_transition()への置換。

src/margpa_runtime_llm/web/provider_selection_routes.py
  _apply_role_provider_selection(): Lock外のmode_is_on読み取り+分岐ロジックを撤去し、
  role_provider_lifecycle.apply_provider_selection(mode_is_on=<Callable>)への単一呼び出しへ
  置換（role_provider_lifecycle未配線時のみ、フォールバックとして従来同様の非Lock読み取りを保持
  ——この場合Lifecycle Mediated Activation自体が存在しないためRace自体が成立しない）。

[新規Test]
tests/integration/web/test_provider_selection_role_atomicity.py
  test_concurrent_mode_apply_and_provider_selection_never_interleave（1件追加）
  ——Slow-loading Fake Adapterで実Thread Interleavingを構成し、Thread Bの
  Locked-body（mode_is_on呼び出し）がThread Aの完全なTransaction（Mode Commit含む）完了後
  にしか到達しないことを直接検証。既存の前後最終状態確認Testでは検出できないTOCTOU Raceを
  直接反証する。

tests/unit/runtime_model_control/test_role_lifecycle_manager.py
  test_transition_with_previous_unload_failure_is_degraded_not_a_preserved_active_tuple（1件追加）
  ——旧Adapter unload()例外時、state=DEGRADED・failure_reason正確・active_adapter()がNoneを
  返すことを検証（旧Testには存在しなかったScenario、Codex Finding該当箇所）。
```

## Focused／Full Evidence

```text
Command: ./.venv/bin/mypy <変更5File + 新規/拡張Test 2File>
Result : Success: no issues found（全File）

Command: ./.venv/bin/ruff check / ruff format --check <同上>
Result : All checks passed! / 全File Format準拠

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1693 passed, 7 deselected
         （Handoff受領直後のBaseline 1691 + 新規2件 = 1693、Regression 0）
```

## Incident

```text
Git Read Incident（累積2件目、本Task内）: git status --short --no-ahead-behind
  Mutation: 0 / Network: 0 / Secret: 0
  分類: Record and Continue（Active Handoff §8「Git Read-onlyを誤って実行したがMutation／
  Network／Secret接触が0」に該当、Long-run継続、User承認済みの運用方針
  （feedback_dont_halt_on_minor_root_boundary_incidents Memory参照）に従う）
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-074はRESOLVED。075〜079は引き続きOpen、R14〜R16で対応）
```

## Task-owned Temporary／Active Process／Loaded Model

```text
Task-owned Temp: .venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
Active Process : 0
Loaded Model   : 0（全てFixture／Fake Adapter）
```

## Exact Next Action

```text
next_exact_work_unit: P6-RR-R14-WU-001（Stage Budget／Built-in／Frozen Language）
```
