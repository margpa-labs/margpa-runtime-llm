# Phase 6 Current Claude Task — Package R25 Recovery（Atomic Worker Admission／Shutdown）

```yaml
document_id: phase_6_current_claude_task_r25_recovery_20260829103844
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 10:38:44 JST
active_contract: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_ja_20260829101215.md
resolves: P6-CODEX-088
package: P6-RR-R25
```

## 対象Finding

P6-CODEX-088（Major、新規）: `run_tracked_stage()`は`registry.accepting_new_work()`／
`executor.submit(work)`／`registry.track(future)`を独立した3 Callで実行していた。
Controller Probe Aは、受付確認後かつSubmit前にShutdownを通すことで、`shutdown_clean=True`
かつ`worker_started_after_shutdown=True`かつ`registry_active_after_clean=1`という状態を
再現した——R22の「Shutdown後の新規受付0」契約が未成立だった。

## 実装

### `TrackedStageWorkerRegistry.submit()`（`track()`を置換）

受付確認・Thread Dispatch・Registry登録を単一Lock Acquisition内でAtomicに実行する
`submit(*, work) -> Future | None`を新設し、旧`track()`を廃止した。`shutdown()`は同一Lockを
取得して`_accepting`をFalseにしFuture Snapshotを取得するため、`submit()`の臨界区間と
`shutdown()`の臨界区間は絶対に交錯しない——`submit()`が先に完了すればそのWorkerは必ず
Snapshotに含まれ、`shutdown()`が先に完了すれば`_accepting`は既にFalseで`submit()`は
`work`を一切呼ばず`None`を返す。

`future.add_done_callback()`は意図的にLock解放**後**に登録する。`concurrent.futures.Future.
add_done_callback`はFutureが既に完了している場合、登録した瞬間に同一Thread上で同期的に
Callbackを呼び出す仕様であり、Lock保持中に登録すると`_untrack`自身の`with self._lock:`が
同一Threadから非Reentrant Lockを再取得しようとしてDeadlockする（Contract Item 5で明示警告
された経路）。Lock解放後の登録により、この経路でもDeadlockしない。

`run_tracked_stage()`は`registry`が渡された場合、Admissionを`registry.submit()`へ完全に
委譲する形へ変更した。

## Threaded Regression Test（実Thread、新規1件）

```text
test_atomic_submit_closes_the_admission_shutdown_toctou_probe_a ... PASS
  （150試行、Barrier同期でsubmit()とshutdown()を同一Registry Lockへ強制競合させ、
    Probe Aの正確な悪状態（Clean Shutdown後もWorkerがActiveに残る）が
    一度も再現しないことを実証。Rejected時はwork()が一度も呼ばれないこと、
    Admitted時はshutdown()完了までに必ず完了しActive Count 0になることを検証）
```

既存11件（Timeout／Zero-Budget／Late Publish 0／Worker Exception／Blocked Shutdown等）は
全てPASSのまま維持（計12件）。

## Focused Evidence

```text
tests/unit/bootstrap/test_tracked_stage_worker.py ... 12 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 483 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 483 source files
pytest（Full Suite） ... 1788 passed, 7 deselected
```

## Open（次Packageへ持ち越し）

```text
P6-CODEX-089（Mode OFF後もLease発行、Unload Exception後の再実行許容）: OPEN、R26で対応。
P6-CODEX-090（偽Manifest Verified扱い）: OPEN、R27で対応。
P6-CODEX-091（Guard Evidence Identity消失）: OPEN、R27で対応。
Real Selene/Qwen3Guard Artifact、Real Browser、User Manual Acceptance: 既知Gapのまま変更なし。
```

## Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0（本Task全体でNetwork Access禁止）
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package R26（Role Lease Admission／Unload Failure、P6-CODEX-089）へ継続。
