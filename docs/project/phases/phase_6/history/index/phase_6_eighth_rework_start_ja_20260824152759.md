# Phase 6 Eighth Rework Start Recovery

Timestamp: 2026-08-24 15:27:59 JST
Role: 設計者兼実装者役
State: EIGHTH_REWORK_IN_PROGRESS
Authority: `phase_6_codex_controller_eighth_rework_exact_handoff_ja_20260824152512.md`

## 1. Authority Verification

- GOV-012 SHA-512:
  `79c55e6c7df63ce69518740074616369ca55dc22ea673a5cd890bd991f9b69eb57a30d9241257f24455bd124260812c2aa7d05036a213ef8807e1d9d4819ccc7`
- Exact Handoff SHA-512:
  `acf10bbcd298437bc7dc390643a241397b58a006c3cec86cfa4f318c6769425d73d155da1bf0cbd00be133448e059c0f635dc0c25594997707188e01337dc9cf`
- Mandatory Reading 4文書を全文読了。

## 2. Exact Scope

Seventh Rework Package A〜Gはやり直さず、次の3 Findingだけを差分修正する。

1. `P6-RW7-CODEX-001`: ENFORCE Judge／Repair中のActive Request早期解放。
2. `P6-RW7-CODEX-002`: 同期ENFORCEの無期限WaitとLate Worker Ownership。
3. `P6-RW7-CODEX-003`: Stale Runtime Status棄却時のMax New Tokens派生値巻き戻し。

## 3. Required Contract

- Model Main LeaseだけをJudge前に解放し、Service Active CorrelationはTerminal確定まで保持。
- Stop／ShutdownをCurrent Judge／Repair Cancellationへ接続し、Cancelが勝った場合は
  `cancelled` exactly once／`completed` 0。
- Judge Wall-clock Deadlineを実行中に強制し、有界Grace後はRaw Candidate 0のSafe
  FallbackまたはCancelled Terminalへ収束。
- Late WorkerはPresented Final／Persistence／Terminal／Last-result Projectionを上書き不可。
- Runtime Status Revisionの採用時だけ、Statusと`settingsForm.maxNewTokens`をAtomic更新。

## 4. Boundary

```text
Package A-G Redo                    : 0
Current Eighth Cycle Root外Action   : 0
Cumulative Root-outside Attempt     : 1 (P6-RW7-INC-001)
Provider Memory Internal Access     : 0
User runtime_data Access            : 0
Git / Network / Model Mutation      : 0
Phase 6 Closure / Phase 7 / Roadmap : 0
```

## 5. Resume Point

Current Source／TestのRead-only Inventoryを行い、RW8-A〜Cの最小変更とRequired Regressionを
連結実行する。通常Failureは権限内で修正し、Focused→Canonical Full→Append-only
Recovery／Returnまで停止せず進む。
