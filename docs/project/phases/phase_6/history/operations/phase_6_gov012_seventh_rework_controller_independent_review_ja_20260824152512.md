# Phase 6 GOV-012 — Seventh Rework Controller Independent Review

```yaml
document_id: phase_6_gov012_seventh_rework_controller_independent_review_20260824152512
status: adjust_required
phase: phase_6
reviewer_role: プロジェクト責任者兼設計統括者役
review_target: phase_6_codex_designer_implementer_seventh_rework_complete_candidate_handoff_ja_20260824151646.md
created_at: 2026-08-24 15:25:12 JST
closure_recommendation: do_not_close_yet
```

## 1. 判定

Seventh Rework Package A〜Gの大半は成立している。UI即時適用、Current Runtime Identity、
Capability分離、意味評価／RepairのPresented Final拘束、反復検出、全自動検証は保持する。

ただし、Controller Independent ReviewでCurrent Transitionに直接影響するMajor 3件を確認した。
いずれもController-owned Reworkであり、User判断へ返さず差分修正する。

```text
Result                    : ADJUST
Open Technical Critical   : 0
Open Technical Major      : 3
Phase 6 Closure           : NOT ALLOWED YET
Package A-G redo          : PROHIBITED
```

## 2. P6-RW7-CODEX-001 — ENFORCE中のActive Request早期解放

`ConversationGenerationSession._completed_event()`はMain Model生成後、同期Judge／Repairの前に
`self._release()`を呼ぶ。このCallbackはModel Access Main Leaseだけでなく、
`ConversationGenerationService._active`も同時に`None`へする。

その結果、ENFORCEのJudge／Repairがまだ動作中で、SessionもTerminalへ到達していないのに、
次が成立する。

- `active_request_id`が`None`になる。
- `/api/v1/chat/stop`およびPersistent Stopが`generation_not_active`へ誤収束する。
- `ConversationGenerationService.shutdown()`がActive Sessionなしと誤認し得る。
- Userの停止操作がJudge／Repairへ伝播しない。

Controller再現結果:

```text
active_request_id None
cancel_result False
finished_during_judge False
```

生成Backend Lease解放と、Request Lifecycle／Stop Correlation解放を分離しなければならない。
SessionのActive Correlationは`completed|cancelled|error` Terminal確定まで保持する。

## 3. P6-RW7-CODEX-002 — 同期Judge／Repairの無期限Wait

`build_judge_completion_hook()`のENFORCE経路は`completed.wait()`をTimeoutなしで呼ぶ。
`EvaluationBudget.max_wall_time_ms=30000`はModel Call完了後の結果をBudget超過へ分類するだけで、
実行中Callを30秒で停止しない。Backend／Threadが応答しない場合、SSE TerminalとSession
Lifecycleが無期限に停止する。

必要Contract:

- Wall-clock Deadlineを実行中に強制する。
- Deadline／User Cancel／Shutdownで同一Cancellation TokenをCancelする。
- 有界Grace後もWorkerが終了しない場合もCallerはSafe FallbackまたはCancelled Terminalへ収束する。
- Late WorkerはCanonical Presented Final／Turn Persistenceを書き換えない。
- User Cancelが勝った場合はSafe Fallback CompletionではなくCancelled Terminalとする。

## 4. P6-RW7-CODEX-003 — Stale Runtime StatusによるMax New Tokens欄巻戻し

`App.acceptRuntimeModelStatus()`はRevision比較でStale `RuntimeModelStatus`をStateから棄却する一方、
`settingsForm.maxNewTokens`はRevision判定外で無条件に更新する。Polling／Mutation Responseが逆順に
到着すると、Current Model Statusは新Revisionのまま、入力欄だけ古い値へ戻り得る。

Runtime Model Statusと派生UI値は、同じAcceptance判定の中でAtomicに採用する。

## 5. 保持する成立範囲

次は再実装・Rollbackしない。

- Package BのImmediate Apply／Sequence Guard。
- Package CのCurrent Runtime Snapshot投影。
- Package DのNative／Backend／Hardware／Effective Context分離。
- Package EのOFF／OBSERVE／ENFORCE意味境界とStrict Decoder。
- Package FのEOS正規化／病的反復Circuit Breaker。
- Package GのValidation Infrastructure。
- P6-RW7-INC-001 Historical Nonconformance。

## 6. Closure条件

3件を修正し、少なくとも次を新規Regressionで証明する。

1. ENFORCE Judge待機中もActive Request Correlationが残る。
2. 同期間のStopが成功し、Cancelled Terminal exactly onceへ収束する。
3. ShutdownがJudge／RepairをCancel／Joinし、偽Cleanを返さない。
4. Judge Timeoutは有界で、Raw Candidateを公開せずSafe Finalへ収束する。
5. Timeout後のLate WorkerがCanonical結果を変更しない。
6. Stale Runtime StatusはStatusとMax New Tokensの両方でAtomicに棄却される。
