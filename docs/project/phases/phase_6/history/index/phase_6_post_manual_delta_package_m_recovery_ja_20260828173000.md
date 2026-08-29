# Phase 6 Post-Manual Delta — Package M Recovery（Provider Routing／Lifecycle／Main Switch）

```yaml
document_id: phase_6_post_manual_delta_package_m_recovery_20260828173000
package: P6-RR-M
completed_wu: M-WU-002 (Main Dropdown Transaction), M-WU-004 (Status Projection)
deferred_wu: M-WU-001 (Provider Execution Router — Package Oへ統合), M-WU-003 (Role Lifecycle — 既存実装で充足と判断)
status: PACKAGE_COMPLETE_WITH_DEFERRAL
created_at: 2026-08-28 17:30:00 JST
next_exact_work_unit: P6-RR-N-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## 結論

P6-CODEX-049（Main Dropdown未接続）とP6-CODEX-050（Model Status投影不整合）を解消した。P6-CODEX-047（Selected/Executed Judge不一致）・048（Qwen3Guard未接続）は、実Invocation経路の変更を要するため、Package Oへ意図的に委譲する（Scope縮小ではなく、正しいPackage境界への割当）。

## M-WU-002 Main Dropdown Transaction

`web/provider_selection_routes.py`へ`_apply_main_provider_selection()`を追加し、`PUT /api/v6/provider-selection/main`が既存`RuntimeModelController.switch_to_model_key()`（Architecture 3.2、無変更）を実際に呼ぶよう配線した。

- 成功時：`controller.replace_runtime_state(role=MAIN, configured_provider=X, active_provider=X, state=ACTIVE)`でConfigured／Active／Model Status／Sidebarを同一Revisionへ収束（P6-DELTA-001）。
- 失敗時（`RuntimeModelRevisionConflict`／`RuntimeModelBusyError`／`RuntimeModelContextLimitExceeded`／`RuntimeModelTargetNotRegistered`／`RuntimeModelLoadFailure`／`RuntimeModelRollbackFailure`）：`RuntimeModelController`自身のRollback後の実Snapshotを再読し、旧ActiveをそのままActiveとして維持しつつ、`failure_reason=f"main_switch_failed:{ExceptionType}"`付きで`ProviderSelectionError(ACTIVATION_FAILED)`をRaiseする（既存Judge／Guard Activation Failureと同一のHTTP Error Pattern、P6-DELTA-002）。
- 既に指定Providerがactive_providerと一致する場合はNo-op（不要なUnload／Reloadを回避）。
- `runtime_model_control`未Bindの場合も、Silent SuccessではなくActivation Failedとして正確に報告する。

## M-WU-004 Status Projection

`web/runtime_model_control_routes.py`の`_project_status()`を変更し、`provider_selection_control`が存在する場合、Judge／Guard Identityを**Provider Selection Controllerの実Snapshot**（Advanced Mode Provider Selection Panelと同一の正本）から投影するようにした。旧来のPhase 4 `RuntimeModelSnapshot.role_bindings`＋`main_self_available`Heuristic、および Guard固定`model_id=None`は、`provider_selection_control`が無い場合のFallbackとしてのみ残した。

- `JudgeIndependenceClass`へ`BUILT_IN`を追加（既存4値へのAdditive拡張。既存の分岐は全てException/Elseを持つため無影響、Regression 0で確認済み）。Built-inをMAIN_SELFやINDEPENDENT_ARTIFACTとして誤表示しない。
- Guard Identityは、Built-in選択時のみ（Digest不要のProvider Typeであるため）Active表示を許可し、実Model（Selene／Qwen3Guard等）がactive_provider≠Noneかつこの経路がDigestをまだ持たない場合はINVALID状態とする（既存`project_guard_model_identity`のINVALID-without-digest規約、P6-CODEX-014と同型）。本Cycleでは実Digestが常にNoneのため、この分岐は将来のPackage O配線後にActive表示を正しく解禁する設計となっている。

## Deferred Work Units

- **M-WU-001 Provider Execution Router**：Judge／Guard Hookが実際にSelected Providerを呼び出す経路変更は、Live Judge Integration（`judge_live_integration.py`）とGuardrail Governance Composition（`guardrail_governance.py`）双方の大規模な書き換えを要する。Package Oの本来のScope（Selene／Qwen3Guard Route、Explicit Main Model Judge、Guard Additive Route）と不可分のため、そちらへ統合する。
- **M-WU-003 Role Lifecycle**：既存`RoleProviderLifecycleManager`（Package 0〜Iで完成）は、Preflight→Load→Commit／Rollback、Active Turn Drain、Pending Unloadを既に正しく実装済みと確認した（Package K Recovery Index参照）。Addendum §5.1のM-WU-005（Atomic Mode／Provider Transition）は、より詳細な設計判断（Mode変更とProvider変更を同一Transactionに含めるか、Provider変更のみ別Transactionとし失敗時はMode自体をRollbackするか）を要するため、Package O内で対応する。

## Open Finding（Non-critical、記録のみ）

`/api/v4/runtime-model/switch`（Legacy Route、Phase 6-G-WU-001由来）は、`provider_selection_control`のConfigured／Activeを更新しない。本Packageで修正した経路は`/api/v6/provider-selection/main`のみである。両経路の完全同期（例：`RuntimeModelController.on_commit`へProvider Selection同期を追加）はP-WU-004（Bounded UI Delta item 1、重複Main Dropdown非表示）が実施されれば実質的にUser露出が無くなるため、本Delta Scopeでは追加対応しない。

## Focused／Regression Evidence

```text
Command: ./.venv/bin/ruff check src/ tests/
Result : All checks passed! (exit 0)

Command: ./.venv/bin/mypy src/
Result : Success: no issues found in 289 source files (exit 0)

Command: ./.venv/bin/pytest tests/integration/web/test_provider_selection_main_switch.py -v
Result : 4 passed（新規：成功／失敗／No-op／Runtime Model Control未Bind）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1660 passed, 7 deselected（Package J Baseline 1656 passed比、新規Test純増でRegression 0）
```

Backend Full Suiteを本Packageで実行し、既存Baselineとの差分がRegression 0であることを確認した（Validation LadderのPer Subphase基準を超える形で、より厳格なEvidenceを取得）。

## Claims Not Made

- Judge／Guard Hookの実Invocation経路（Selected Provider呼び出し）が接続されたと主張しない（Package O）。
- Legacy `/api/v4/runtime-model/switch`経路のProvider Selection同期を主張しない（Open Findingとして記録のみ）。
- Real Selene／Qwen3Guard Active状態を主張しない（Model Authority Receipt未成立のまま、Package L同様）。
