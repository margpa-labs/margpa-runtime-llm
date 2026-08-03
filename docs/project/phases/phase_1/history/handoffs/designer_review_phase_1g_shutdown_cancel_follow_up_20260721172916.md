# Phase 1-G Shutdown Cancel Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_shutdown_cancel_follow_up`
- 状態: `accepted_with_non_blocking_environment_observation`
- 作成日時: `2026-07-21 17:29:16 JST`
- 更新日時: `2026-07-21 17:29:16 JST`
- Snapshot: `20260721172916`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Shutdown Cancel Follow-upとPhase 1-G最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md](implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md)
- 対象Handoff: [implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md](implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md)
- 前回Review: [designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md](designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 最新Index: [documentation_index_20260721172916.md](../documentation_index_20260721172916.md)
- supersedes: `designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`

## 1. Review結論

Phase 1-G Shutdown Cancel Follow-upは要求どおり実装され、前回のMandatory Findingは解消した。

```text
SSE Consumer Cross-thread Cancel : Resolved
Runtime Shutdown Cross-thread    : Resolved
Timeout State Falsification      : Resolved
Model Close Callback             : Pass／Exactly Once after Success
Lifespan Failure Visibility      : Pass／Sanitized and Propagated
Static／Default Regression       : Pass／215 passed、3 deselected
Web／Conversation Targeted       : Pass／32 passed
Implementer Native Model Smoke   : Pass／2 passed、1 skipped
Reviewer Native Model Smoke      : Environment Failure／2 failed、1 skipped
Final Decision                   : Phase 1-G Accepted
Next Phase                       : Phase 1-H Requirements／Design
```

Reviewer Native Model Smokeは`llama_context` creationで再度失敗したが、Phase 1-G変更経路に入る前のModel Loadである。実装担当の同一Snapshotでは2件合格し、実ModelのShutdown／Restart／後続Generationも成立している。このためSource Findingとせず、Phase 1全体の最終User Gateで再実行する非ブロッカー環境観察とする。

## 2. Mandatory Finding解消

### 2.1 Cooperative Shutdown

`ConversationGenerationService.shutdown()`は次のみを行う。

```text
session.request_cancel()
session.wait(timeout)
  ├─ Finished → True
  └─ Timeout  → False
```

Timeout後の`session.force_cancel()`は除去された。Native Streamの`cancel()`／`close()`はProducer Iteration Threadが次Chunk境界でCancel要求を観測した後に行う。

### 2.2 Timeout State

Native `next()`がTimeout内に復帰しない場合：

- `shutdown()`は`False`を返す。
- `WebRuntime.close()`は固定された安全な`RuntimeError`とする。
- Active Sessionと`active_request_id`を維持する。
- Model Close Callbackを呼ばない。
- Shutdown ThreadからNative Cancel／Closeを呼ばない。

Native Boundary解放後はProducer Thread上でCancel／Closeし、Session／Generation Gateを解放する。

### 2.3 Model Close Idempotency

`WebRuntime.close()`はLockと成功Stateを持つ。

```text
Active Session Timeout     : Callback 0
Session終了後の初回Close : Callback 1
2回目以降                  : Callback追加0
```

### 2.4 Lifespan Failure Visibility

Runtime Close Failureを無記録で抑制する経路は除去された。Operator Logと伝播例外は次の固定Messageだけを使う。

```text
The web runtime could not shut down cleanly.
```

Private Text、Absolute Path、Raw ExceptionをLog／伝播例外へ含めないRegressionが合格した。

## 3. Regression Coverage

`tests/integration/web/test_web_app.py`は次を直接確認する。

- Active Generation中の別Shutdown Thread
- Native `next()` Blocking中のTimeout
- Shutdown ThreadからのCancel／Close 0件
- Active RequestとModel Callbackの非偽装
- Native Boundary解放後のProducer Thread Cancel／Close
- Session／Gate解放と後続Generation
- Runtime Close 2回に対するCallback合計1回
- Lifespan FailureのSanitized Log／Exception

既存のSSE Thread-affine、Queue Backpressure、Cleanup Timeout Testも継続合格している。

## 4. Independent Verification

```text
ruff format --check src scripts tests     : Pass／88 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／88 source files
python -m compileall -q src scripts tests : Pass
pytest -q                                 : Pass／215 passed、3 deselected
Conversation／Web Targeted               : Pass／32 passed
uv lock --check --offline                 : Pass／122 packages
bash -n scripts/setup/*.sh                : Pass
```

### Native Model Evidence

```text
Implementer Automated : 2 passed、1 skipped
Implementer Manual    : Active Shutdown、Stop、Restart、RESTARTED. Generation Pass
Reviewer Automated    : 2 failed、1 skipped
Reviewer Failure      : Failed to create llama_context
Related Runtime       : 別MARGPA／Python／Uvicorn／llama常駐なし
```

Reviewer失敗時のUnified Memoryは圧縮Pageを多く保持していた。原因は未確定であり、SnapshotのSource不具合と断定しない。Phase 1完了に必要なUser Testで再確認する。

## 5. Non-blocking Observation

`ConversationGenerationSession.force_cancel()`のMethod定義自体は公開Session Surfaceに残るが、Current `src/margpa_runtime_llm/`からの呼出しは0件である。

現行LifecycleはすべてCooperative Cancelだが、将来のAgent／Backend／並行実行拡張前に次のいずれかを行う。

- `force_cancel()`を削除または非公開化する。
- Backendが保証するThread-safe Stop Signal Contractとして再設計する。

現在のPhase 1-G実行経路に危険なCallerがないため、これはAcceptance Blockerとしない。

## 6. Acceptance Status

| Area | Result |
|---|---|
| Minimal Web Surface | Accepted |
| Conversation Isolation | Accepted |
| Settings 3項目 | Accepted |
| SSE Streaming／Stop | Accepted |
| Disconnect／Backpressure Cleanup | Accepted |
| Shutdown／Restart | Accepted |
| Token Exhaustion Warning | Accepted |
| Preview Access Control | Accepted |
| Safe Shutdown Failure | Accepted |
| Phase 1-G Overall | Accepted |

## 7. Next Gate

Phase 1-Gは完了し、Phase 1-H Summary Modeの要件定義／設計へ進める。

ただしPhase 1-H実装、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開は本Reviewだけで自動許可しない。

## 8. Append-Only

既存Reviewを変更せず、新TimestampのAccepted Reviewとして追加した。
