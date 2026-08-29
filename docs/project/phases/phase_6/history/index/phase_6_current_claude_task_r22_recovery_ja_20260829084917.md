# Phase 6 Current Claude Task — Package R22 Recovery（Tracked Stage Worker Registry／Shutdown）

```yaml
document_id: phase_6_current_claude_task_r22_recovery_20260829084917
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 08:49:17 JST
active_contract: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md
resolves: P6-CODEX-081
package: P6-RR-R22
```

## 対象Finding

P6-CODEX-081（Open、再Open）: R18の`run_tracked_stage()`はCallerをBudget内へBoundし、Late
ResultをCallerへ返さない点では改善済みだったが、Timeout時に返される`Future`はPrompt Build／
Decodeの両Production Call Siteで参照を破棄されていた。`tracked_stage_worker.py`自身にActive
Future Registry、Shutdown、JoinまたはCompletion CallbackによるOwner管理がなく、
`ModelAccessCoordinator`は外側のJudge Workerだけを追跡し内側のPrompt／Decode Workerを追跡し
ない。Cancellationを無視して走り続けるPrompt／Decode Workerが存在してもWebRuntime／
CoordinatorはClean Shutdownを主張できた。

## 実装

### 1. `TrackedStageWorkerRegistry`（`tracked_stage_worker.py`新設）

- `track(future)`: 提出直後にDictへ登録し、`future.add_done_callback()`でExactly-once除去を
  仕込む。正常完了／Exception／Timeout後のLate Completeの全Pathで同一Callbackが発火するため、
  除去漏れが起きない。
- `accepting_new_work()`: `shutdown()`呼出し後は`False`——新規Stage提出はここで止める
  （Call Site側で新規Threadを一切立てない）。
- `shutdown(*, timeout_seconds)`: 新規受付を止めた上で、その時点のTracked Future全件を
  合計`timeout_seconds`以内でBounded-Join（1件ごとにFull Budgetを消費させない）。Bound超過で
  なお実行中のFutureが残る場合は`False`を返す——Cleanの偽装をしない。Exceptionで終了した
  FutureはDone扱いでClean判定に影響しない。
- `active_count()`: Test／診断用の現在Track数。

### 2. `run_tracked_stage()`拡張

`registry: TrackedStageWorkerRegistry | None = None`引数を追加。Thread提出直後に
`registry.track(future)`。Shutdown進行中（`accepting_new_work() is False`）の呼出しは新規
Threadを一切立てず、即座に`timed_out=True, result=None`のTyped Outcomeを返す
（`budget_ms<=0`のInline Pathは元よりThreadを持たないため対象外）。

### 3. Production配線

- `judge_live_integration.py`: `build_judge_completion_hook()`に`tracked_stage_registry`引数を
  追加し、Prompt Build／Decodeの両`run_tracked_stage(...)`呼出しへ`registry=tracked_stage_
  registry`を配線。
- `web_application.py`: `feature_modes_enabled`時に`TrackedStageWorkerRegistry()`を1個構築
  （`request_correlation_registry`と同一のRuntime寿命／共有モデル）。
  `build_judge_completion_hook(...)`と`WebRuntime(...)`双方へ渡す。
- `web/contracts.py`: `WebRuntime`に`tracked_stage_registry`Field追加（TYPE_CHECKING経由）。
  `close()`で`self.conversation.shutdown(timeout)`の直後・`role_provider_lifecycle.shutdown()`
  および`close_callback()`（Main Model Unload）より前に`tracked_stage_registry.shutdown(
  timeout_seconds=timeout)`を確認し、False-clean時は`RuntimeError`でUnloadへ進まない——既存の
  `model_access_coordinator.shutdown()`ゲート（`_close()`内、Main Unload直前）と同型の
  Fail-safe Patternを踏襲。

## Threaded Regression Test（実Thread、`test_tracked_stage_worker.py`新規6件）

```text
test_registry_shutdown_returns_false_while_a_worker_is_still_blocked ... PASS
  （実Thread＋Event: Blocked Worker中のshutdown()がFalseに収束、2秒未満でBound）
test_registry_shutdown_retried_after_release_reports_true ... PASS
  （Release後の再shutdown()呼出しでTrueへ収束）
test_registry_untracks_a_worker_that_raises_zero_leak ... PASS
test_registry_untracks_a_late_completing_worker_that_raises_zero_leak ... PASS
  （Timeout後のLate Complete＋Exceptionの複合Pathでも0 Leak）
test_registry_tracks_several_concurrent_workers_independently ... PASS
  （3並行Worker、2件Release後もshutdown() False、全件Release後にTrue）
test_registry_refuses_new_work_once_shutdown_has_begun_zero_late_publish ... PASS
  （Shutdown開始後は新規Threadを一切立てない——最強形のLate Publish 0）
```

既存5件（Timeout／Zero-Budget／Late Publish 0／Worker Exception等）と合わせ計11件、全PASS。

## Focused Evidence

```text
tests/unit/bootstrap/test_tracked_stage_worker.py ... 11 passed
tests/unit/bootstrap + tests/unit/web + tests/integration/web ... 352 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 481 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 481 source files
pytest（Full Suite） ... 1765 passed, 7 deselected
```

## Late Publish 0（既存性質の保持、確認）

Prompt／Decode Resultの「Timeoutを超えたLate ResultがJudge Result、Evidence、Presented
Final、Last Resultへ一切Publishされない」という既存契約（R18由来）はRegistry追加による変更
なし——Registryは純粋にLifecycle追跡のみを担い、`run_tracked_stage()`の戻り値経路
（Timeout時は`result=None`固定）には一切関与しない。新規Testで「Shutdown後は新規Thread自体を
立てない」という、より強い形のLate Publish 0も追加で実証した。

## Open（次Packageへ持ち越し）

```text
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

Exact next action: Package R23（Qwen3Guard Official Contract Manifest／Strict Decoder、
P6-CODEX-087）へ継続。
