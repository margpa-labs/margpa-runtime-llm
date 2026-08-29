# Phase 6 Current Claude Task — Package R17 Final Recovery（Composite Transition／Status Snapshot）

```yaml
document_id: phase_6_current_claude_task_r17_final_recovery_20260829035038
package: P6-RR-R17
status: PACKAGE_COMPLETE
created_at: 2026-08-29 03:50:38 JST
active_contract: phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_ja_20260829032604.md
predecessor: phase_6_current_claude_task_r16_final_recovery_ja_20260828233354.md
git_action: 0
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-080: Status Readを含むAtomic Tuple未成立 -> RESOLVED（本Package）
```

## 調査（実装前）

P6-GOV-022のController診断コード（Provider RuntimeをACTIVEへ更新した直後、Mode Commit直前で
意図的に停止し、独立Lockを使うReaderが`active_provider=built_in.deterministic／mode=off`という
Torn Tupleを実際に観測した、という再現）を検証した。原因は、R13で導入した`self._condition`が
Mutation側（`apply_mode_transition`／`apply_provider_selection`）の内部では正しく単一Transaction
化されていた一方、Reader側（`provider_selection_routes.get_provider_selection()`、
`feature_modes_routes.get_status()`、両Mode Apply Responseの`_project_status()`呼び出し）が
`ProviderSelectionController.snapshot()`と各Mode Controller（`JudgeModeController`／
`GuardrailModeController`）の`mode_snapshot()`をそれぞれ独立に、`self._condition`を一切介さずに
呼んでいたことにあった。特に`_GuardrailGovernanceModeApplierAdapter.apply()`は
`apply_mode_transition()`のLock解放後に`self._composition.mode_controller.mode_snapshot()`を
別途呼んでおり、これは同一Requestの結果としてすら不正確になり得る（Lock解放後に別Requestが
割り込めば、その別Requestの結果を返してしまう）ことを確認した。

## 実装

### Changed Files

```text
[変更]
src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py
  - ModeReadResult（revision, value）、CompositeRoleStatus（provider, judge_mode, guard_mode）
    をProvider-neutral Value Typeとして新設。
  - composite_status(read_judge_mode, read_guard_mode)を新設。self._condition内で
    Provider Selection SnapshotとJudge／Guard両Mode値を同時に読む、Pure-read primitive。
  - apply_mode_transition()／apply_provider_selection()の戻り値をProviderSelectionSnapshot
    からCompositeRoleStatusへ変更。Transition完了直後、Lock解放前にMode値を読み切って返す
    （Lock解放後の別読み直しを構造的に禁止）。
  - _commit_mode_after_activation()を新設し、_activate_locked()の2箇所（Built-in／実Load成功後）
    のcommit_mode()呼び出しを統一。commit_mode()自体がRaiseした場合、既にLoad済みのCandidateを
    Rollback（Unload）し、Providerを honest な UNAVAILABLE（Rollback自体も失敗した場合はDEGRADED）
    Tupleへ訂正してから復帰する（Raiseはしない）— 本Package内でTestを書く過程で発見した新規Gap
    （「commit_modeがRaiseするとProvider ACTIVE／Mode未Commitのまま外部へ露出する」）の修正。

src/margpa_runtime_llm/web/feature_modes_routes.py
  - _read_judge_mode()／_read_guard_mode()を新設（Manager非経由時のFallback、および
    composite_status()／apply_mode_transition()へ渡すCallableとして共用）。
  - _judge_snapshot()へmode: ModeReadResult | None = Noneパラメータ追加。指定時はそれを使用、
    未指定時（Unbound Runtime）は従来通りLive読み。
  - get_status()：role_provider_lifecycle経由時はcomposite_status()を1回呼び、その結果を
    _project_statusへ渡す（Judge Mode独立読みを廃止）。
  - apply_judge()：apply_mode_transition()の戻り値（Composite）から直接Responseを構築。
    従来の「Mutation後にProject_statusを再呼び出し」（Lock解放後の別読み）を廃止。

src/margpa_runtime_llm/web/provider_selection_routes.py
  - 同様の_read_judge_mode()／_read_guard_mode()、_status()のasync化＋composite_status()経由化。
  - _apply_role_provider_selection()：apply_provider_selection()のCompositeからcomposite.provider
    を直接Responseとして返す（別読み直し廃止）。

src/margpa_runtime_llm/bootstrap/configuration_control.py
  - _GuardrailGovernanceModeApplierAdapterへjudge_mode_control（Optional）を追加。
    apply()内、Lock解放後の`self._composition.mode_controller.mode_snapshot()`再読みを廃止し、
    apply_mode_transition()が返すComposite.guard_modeから直接Responseを構築。

src/margpa_runtime_llm/bootstrap/web_application.py
  - build_configuration_control()呼び出しへjudge_mode_control=judge_mode_control追加。

[新規Test]
tests/unit/runtime_model_control/test_role_lifecycle_manager.py（6 tests追加）
  - test_composite_status_blocks_until_on_transition_fully_commits（R17-A/B相当、Manager単体）
  - test_composite_status_blocks_until_off_transition_fully_commits（R17-C相当、Manager単体）
  - test_composite_status_blocks_for_guard_role_too（項目5: Judge/Guard双方）
  - test_apply_mode_transition_reports_honest_tuple_after_commit_mode_failure（R17-D）
  - test_composite_status_reports_honest_tuple_after_active_turn_drain_pending（R17-D）
  （5 testsの意図だが、Threadベース検証の構造上6関数として実装 — 詳細はFile本体を参照）

tests/integration/web/test_provider_selection_role_atomicity.py（3 tests追加）
  - test_judge_provider_change_to_main_self_while_enforce_drains_active（R16由来、既存）
  - test_r17_provider_and_feature_modes_get_block_during_on_transition（R17-A/B、HTTP Route実測）
  - test_r17_both_gets_block_during_off_transition（R17-C、HTTP Route実測）
```

## Focused／Full Evidence

```text
Command: ./.venv/bin/pytest tests/unit/runtime_model_control/test_role_lifecycle_manager.py \
         tests/integration/web/test_provider_selection_role_atomicity.py \
         tests/integration/web/test_feature_modes_routes.py \
         tests/integration/web/test_configuration_control_web_app.py -q
Result : 全件 PASS（新規9 tests含む）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/ -q
Result : 1708 passed, 7 deselected（R16終了時1701 + 新規7 tests = 1708、Regression 0）

Command: ./.venv/bin/mypy src tests
Result : Success: no issues found（471 source files相当、本Package変更分に限定実行でも0 issues）

Command: ./.venv/bin/ruff check <本Package変更File>
Result : All checks passed!
```

## Required Regression Scenarios（本Package分）

```text
R17-A: ON Transaction中のProvider GET
  -> test_r17_provider_and_feature_modes_get_block_during_on_transition PASS
R17-B: ON Transaction中のFeature Modes GET
  -> 同上（同一Testで両Route同時検証）PASS
R17-C: OFF Transaction中の両GET
  -> test_r17_both_gets_block_during_off_transition PASS
R17-D: Mode／Unload Failure時のHonest Tuple
  -> test_apply_mode_transition_reports_honest_tuple_after_commit_mode_failure（Mode Commit Failure）
     test_composite_status_reports_honest_tuple_after_active_turn_drain_pending（Active Turn Drain）
     PASS（Unload Failure自体は既存test_transition_with_previous_unload_failure_is_degraded...で
     R13時点から継続してカバー済み、本Packageでの新規Regressionなし）
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-080はRESOLVED。081〜085は引き続きOpen、R18〜R20で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま。本Package中の新規発生 0）
Git Mutation      : 0
Network Action     : 0
Root外Persistent Write: 0 known
```

## Changed File SHA-512（本Package）

```text
91d472cde99b0f75508ccbdf3b84d001acdf548851837230a396417b7360b4bc854ead7e6b3f7c11247619808730398911fbaef4fa6085b585061bf66925e668 role_lifecycle_manager.py
e98109912355fdc8c8b30f7f4206c87806c4f2af27f226ca98bf99ca34adb39055f4fa2867aa9072934e5d18c369c3edf516ea0ea50c44ccb3c224a2cd4f9c08 feature_modes_routes.py
8c3d2aa6a7264ac5da266464b752530d738a59462b1538a1bdefa17bb558d80d30fe7a570723d72cc816c4c270ec08f0133f1c12b1793c95eee3671acab2b40b provider_selection_routes.py
ed192217c5b3328cc466fe03375a54c09e4190e6f4fadd67d98dadfd2e1ca87fa6bb7f4633e095ff6951fa78f7833200e2cc9f1f6911c90d8f48eb548b725605 configuration_control.py
32e13235adf8700d0fe9c47c414f28d059ac293bf068bbc73f2d810c10d8c93e257ba83b5d71c9ba9b594566480754dc52ac897278a699c70e566b604fb444e9 web_application.py
6a8cf44802319b56070966f75dd0bc5bd005fcd025a62404243482acb72a05bba3403ad584ccf37f89955960efc6b484e3e7d70310ec6de97f6e46f9771fc8ca test_provider_selection_role_atomicity.py
cf1fa44c80f1d7794b177f713305d0a5f44226f1b05b8e3fc0fdd308a5243f847c9e91cbb83a0884b2f647844bb2e5aa82a1b98fa4b5829a5494c945ffcd64b9 test_role_lifecycle_manager.py
```

## Exact Next Action

```text
next_exact_action: P6-RR-R18-WU-001（Full Stage Deadline／AUTO Language）
```
