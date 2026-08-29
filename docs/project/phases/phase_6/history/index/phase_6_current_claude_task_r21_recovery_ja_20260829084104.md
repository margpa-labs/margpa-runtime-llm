# Phase 6 Current Claude Task — Package R21 Recovery（Production Dedicated Role Execution Lease）

```yaml
document_id: phase_6_current_claude_task_r21_recovery_20260829084104
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 08:41:04 JST
active_contract: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md
resolves: P6-CODEX-086
package: P6-RR-R21
```

## 対象Finding

`P6-GOV-023`（`phase_6_gov023_claude_r17_to_r20_controller_independent_review_ja_20260829062910.md`）
の P6-CODEX-086: `RoleProviderLifecycleManager.begin_turn()`／`end_turn()`
自体は実装済みだが、Current Production Source全体でこの2 APIを呼ぶ箇所が0件（Test内のみ）。
Judge／Qwen3Guard Detectorは`active_adapter()`でRaw Adapterを取得した後、Leaseを持たずに実行し
ていたため、実Judge／Guard Call中でも`_active_turns`は0のままで、Provider切替・Mode OFF・
Shutdownが実行中Adapterと競合できた。P6-RR-ACC-016／017のPASS Claimはこの配線欠落により不成立
と指摘された。

## 実装

### 1. Atomic Lease-Acquire API（`role_lifecycle_manager.py`）

`RoleTurnHandle(lease, adapter)` を新設し、`begin_role_turn(*, role) -> RoleTurnHandle | None`
を追加。Adapter解決（`_active_adapters.get(role)`）とLease取得（`_active_turns`Increment＋
`RoleTurnLease`生成）を`self._condition`一Lock内でAtomicに行う——旧`active_adapter()`→別call
`begin_turn()`のTOCTOU設計を廃止。`none`／`built_in`（Adapter未登録）はNoneを返しLeaseを作らな
い（暗黙Fallbackなし）。Shutdown進行中に実Adapterが残っている場合のみ`ProviderSelectionError`を
raiseし新規Leaseを拒否する。既存`begin_turn()`／`end_turn()`／`active_adapter()`は変更せず低レ
ベルPrimitiveとして維持（`end_turn()`がRelease APIを兼ねる）。

### 2. Judge Production配線（`judge_live_integration.py`）

`active_judge_adapter_resolver`を`begin_judge_role_turn`／`end_judge_role_turn`の対へ置換。
`hook()`内でLease取得を**Judge OFF早期returnの後**へ移動（OFF Turnで無駄にLeaseを取得して
リークする経路を排除）。`_run_judge()`に`role_turn_lease`引数を追加し、`_run_judge_and_repair()`
呼び出しを囲む`try/except/finally`の`finally`でExactly-once Release——成功／Typed Failure／
Exceptionの全Pathを一箇所で網羅。ENFORCE同期待ちPathとOBSERVE Background Path双方の
`model_access_coordinator.start_background()`が`False`を返す（Coordinator Slot拒否）Branchにも
明示Release呼び出しを追加——ここは`_run_judge()`自体が実行されないため`finally`だけでは
Releaseされない、新たに発見したLeak経路。Hook入口〜Dispatch分岐間のRun-Correlation構築部にも
Exception Safety Net（`try/except`でRelease後`mark_skipped`して`return None`）を追加。

### 3. Guard Production配線（3 Point共通）

- `qwen3guard_detector_adapter.py`: `Qwen3GuardRoleTurn(adapter, lease)`を新設。
  `Qwen3GuardDetectorAdapter.__init__`を`begin_role_turn`／`end_role_turn`対へ置換。
  `detect()`で`classify_point()`呼び出しを`try/finally`で囲みExactly-once Release
  （UNAVAILABLE Pathは元よりLease未取得のためRelease不要）。
- `guardrail_governance.py`: `GuardrailGovernanceComposition`の
  `qwen3guard_active_adapter_resolver`を`qwen3guard_begin_role_turn`／`qwen3guard_end_role_turn`
  へ置換。INPUT／OUTPUT_CANDIDATE／CONTEXT_SOURCEの3 Point全てが同一Lease対を共有。
- `web_application.py`: `_qwen3guard_begin_role_turn()`／`_qwen3guard_end_role_turn()`Closureを
  新設（`role_provider_lifecycle.begin_role_turn(role=GUARD)`→`Qwen3GuardRoleAdapter`への
  Unwrap失敗時はLease即時Release）。Judge側も同型の`begin_judge_role_turn`／
  `end_judge_role_turn`Closureへ置換。

## Threaded Regression Test（実Thread、`test_role_lifecycle_manager.py`新規5件）

```text
test_begin_role_turn_pairs_adapter_and_lease_from_one_lock_acquisition ... PASS
test_begin_role_turn_returns_none_for_a_none_provider_no_lease_acquired ... PASS
test_begin_role_turn_blocks_shutdown_from_unloading_until_release ... PASS
  （実Thread2本＋Event同期: 実Call実行中のShutdownはFalseに収束しUnload 0件、
    Release後の明示Shutdownで初めてUnload 1件——実Callが真にUnloadをBlockすることを証明）
test_lease_released_via_finally_after_a_real_call_exception_leaves_zero_leak ... PASS
  （Exception後もfinally経由でRelease——Leak 0をShutdown成功で証明）
test_multiple_concurrent_role_turns_each_track_their_own_lease_generation ... PASS
  （3並行Lease、各generation一意、最後の1件until全ReleaseまでUnload 0）
```

`test_judge_live_integration_dispatch_router.py::test_selene_initial_judge_repair_and_frozen_
selene_rejudge_single_turn_e2e`（S9既存E2E）にRelease Trackerを追加し、Initial Judge→Repair→
Rejudgeの一連Runを通じてLeaseが最終的に1回だけReleaseされることをE2Eでも確認（PASS）。

`test_qwen3guard_detector_adapter.py`を新API（`begin_role_turn`／`end_role_turn`）へ全面改稿し、
成功／ERROR／UNAVAILABLE／Release自体がraiseする防御Path各々でRelease回数を明示Assertion（新規
1件追加、計6件、全PASS）。

## Focused Evidence

```text
tests/unit/runtime_model_control/test_role_lifecycle_manager.py ... 18 passed
tests/unit/bootstrap/test_judge_live_integration.py ... (既存分included)
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py ... (既存分included)
tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py ... 6 passed
tests/unit/guardrail_governance/test_bootstrap_hooks.py ... (既存分included)
上記5 File計 ... 96 passed
tests/unit/web/test_web_cli.py（Bootstrap Wiring含む） ... 33 passed
tests/unit/bootstrap + tests/unit/runtime_model_control + tests/unit/guardrail_governance +
  tests/unit/adapters + tests/integration/web + tests/unit/web ... 574 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 481 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 481 source files
pytest（Full Suite） ... 1759 passed, 7 deselected
```

## P6-RR-ACC-016／017 再導出（暫定、最終集計はR24）

Judge／Guard双方でProduction Call SiteがReal Model Callの間Lease（`begin_role_turn`/
`end_turn`）を保持することを実Thread Testで実証した——P6-CODEX-086がOpenとした
「Production配線0件」自体は解消。Acceptance IDとしての最終PASS/PARTIAL Dispositionと
Evidence Pointerの確定はR24（66 ID正本再集計）でまとめて行う（Handoff §3 R24-2の指示通り）。

## Open（次Packageへ持ち越し）

```text
P6-CODEX-081（Tracked Stage Worker実完了追跡／Shutdown False-clean）: OPEN、R22で対応。
P6-CODEX-087（Qwen3Guard公式Contract Manifest／Decoder契約不一致）: OPEN、R23で対応。
P6-CODEX-084（66 ID集計不正確）: OPEN、R24で対応。
Real Selene/Qwen3Guard Artifact、Real Browser、User Manual Acceptance: 既知Gapのまま変更なし。
```

## Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package R22（Tracked Stage Worker Registry／Shutdown、P6-CODEX-081）へ継続。
