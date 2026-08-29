# Phase 6 Current Claude Task — Package R26 Recovery（Role Lease Admission／Unload Failure）

```yaml
document_id: phase_6_current_claude_task_r26_recovery_20260829104503
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 10:45:03 JST
active_contract: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_ja_20260829101215.md
resolves: P6-CODEX-089
package: P6-RR-R26
```

## 対象Finding

P6-CODEX-089（Major、新規）: `begin_role_turn()`はAdapter存在と`_shutting_down`だけを確認し、
Selectionが`ACTIVE`か、`active_provider`がAdapterと一致するか、Roleが`_pending_unload`かを
確認していなかった。Controller Probe Bは、既存Leaseを保持したままMode OFFへ遷移し
`DEGRADED/active_turn_drain_pending`となった状態でも、新しいLease取得が成功することを
再現した。さらにClaude自身がIR-R24-001として記録した`_unload_locked()`のException時
Pop非対称性も、単なるObservationではなくProduction Lifecycle Failureとして再Openされた。

## 実装

### 1. `begin_role_turn()`の追加検証（`role_lifecycle_manager.py`）

Adapter存在・Shutdown確認に加え、同一Lock内で以下を追加確認するよう修正：

- `selection.state is ProviderRuntimeState.ACTIVE`
- `selection.active_provider is not None`
- `selection.active_provider == adapter.provider_id`（Adapter Providerとの一致）
- `role not in self._pending_unload`

いずれか不成立ならLeaseを発行せず`None`を返す（built_in／none時の既存Silent-None契約と
同型——例外を投げるのはShutdown進行中のみ、という既存方針を維持）。OFF前に成立したLeaseは
`_active_turns`Counterで引き続き正しくDrainされる。

### 2. `_unload_locked()`のException時Pop対称化

Unload Exception時も成功時と同様に`self._active_adapters.pop(role, None)`を実行するよう
修正。`_transition_to_locked`の既存Failed-unload Discipline（Exception時Popし信頼しない）
と対称化した。これにより`begin_role_turn()`の第一Check（`adapter is None`）だけで
Unload失敗後のAdapterを即座に拒否できる。

### 3. `end_turn()`のDrain完了State修正（CONFIGURED偽装Bug）

`end_turn()`が`_unload_locked()`の戻り値を捨てて常に`CONFIGURED`を主張していたBugを修正。
`_deactivate_locked`の既存`unload_ok`駆動State／Failure Reason解決ロジックと同一の分岐
（`unload_ok`かつ`configured_provider != "none"` → CONFIGURED、`unload_ok`のみ → NONE、
それ以外 → DEGRADED＋`failure_reason="provider_unload_failed"`）をDrain完了経路にも適用。

## 決定論的Test（新規4件、`test_role_lifecycle_manager.py`）

```text
test_off_inserted_between_frozen_belief_and_lease_acquisition_is_refused ... PASS
  （実Thread2本＋Event: Mode Freeze直後とLease取得直前の間へOFFを挿入する
    Production Raceを再現。frozen belief（Turn自身の凍結済み判断）がstaleでも
    begin_role_turn()はLive Stateを見て正しく拒否）
test_begin_role_turn_refuses_a_second_lease_once_drain_has_begun ... PASS
  （Drain待ち中の第二Lease拒否——Adapter参照はまだ_active_adaptersに残ったまま
    なので、新規state/_pending_unload Checkが実際に機能することを直接証明）
test_begin_role_turn_refuses_after_an_immediate_unload_exception ... PASS
  （Lease未保持時の即時Unload失敗後、新規Lease拒否）
test_end_turn_drain_completion_with_unload_failure_settles_degraded_not_configured ... PASS
  （P6-CODEX-089の「CONFIGUREDへ偽装」Bugを直接再現・修正実証。Drain完了時の
    Unload失敗がDEGRADED/provider_unload_failedへ正しく収束し、
    その後の新規Lease取得も拒否されることを確認）
```

既存18件は全てPASSのまま維持（計22件）。

## Focused Evidence

```text
tests/unit/runtime_model_control/test_role_lifecycle_manager.py ... 22 passed
tests/unit/runtime_model_control + tests/integration/web + tests/unit/bootstrap +
  tests/unit/guardrail_governance + tests/unit/adapters ... 522 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 483 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 483 source files
pytest（Full Suite） ... 1792 passed, 7 deselected
```

## Judge／Guard Production Call Site Exactly-once Release（維持確認）

`judge_live_integration.py`／`qwen3guard_detector_adapter.py`は本Packageで変更していない。
`begin_role_turn()`が`None`を返すCaseが増えた（Drain中等）だけであり、両Call Siteの既存
「Adapter None → Typed Unavailable、Lease None → Release No-op」処理は変更なく正しく機能する
——Release側Logicには一切触れていないため、Exactly-once Release契約はそのまま維持される
（522件のFocused Evidence、既存R21 Threaded Testの継続PASSで確認済み）。

## P6-RR-ACC-016／017再導出（暫定、最終判定はR28）

`begin_role_turn()`のPost-OFF/Drain/Unload-Exception全経路での新規Lease拒否を実Thread Test
4件で証明した。最終PASS Dispositionと Evidence PointerはR28（66 ID正本再集計）でまとめて
確定する。

## Open（次Packageへ持ち越し）

```text
P6-CODEX-090（偽Manifest Verified扱い）: OPEN、R27で対応。
P6-CODEX-091（Guard Evidence Identity消失）: OPEN、R27で対応。
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

Exact next action: Package R27（Strict Manifest Binding／Guard Evidence Provenance、
P6-CODEX-090／091）へ継続。
