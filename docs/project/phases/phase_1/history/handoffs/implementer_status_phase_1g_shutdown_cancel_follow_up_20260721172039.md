# Phase 1-G Shutdown Cancel Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_shutdown_cancel_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 17:20:39 JST`
- Snapshot: `20260721172039`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`
- 対象Handoff: `implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md`

## 1. 結果

Phase 1-G Shutdown Cancel Follow-upを限定Scope内で完了した。

`ConversationGenerationService.shutdown()`のTimeout経路からCross-thread `force_cancel()`を除去した。Shutdown、SSE Consumer Closeともに`request_cancel()`を第一段とし、Native Cancel／CloseはProducer Iteration Thread上で実行する。

Runtime CloseはActive Sessionの終了を確認するまでModel Close Callbackを呼ばず、成功後は複数回CloseされてもCallbackを合計1回だけ呼ぶ。Lifespan Shutdown Failureは安全な固定Messageで記録し、抑制せず呼出元へ伝播する。

Phase 1-Hには着手していない。

## 2. 変更File

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py` | Shutdown Timeout後の`session.force_cancel()`を除去し、Cooperative Cancel待ちの結果を返す |
| `src/margpa_runtime_llm/web/contracts.py` | Runtime CloseへTimeout引数、排他制御、成功後のIdempotencyを追加 |
| `src/margpa_runtime_llm/web/app.py` | Lifespan Shutdown Failureを安全な固定MessageでLogし、`RuntimeError`として再送出 |
| `tests/integration/web/test_web_app.py` | Active Generation Shutdown、Thread Affinity、Callback回数、Lifespan Failure VisibilityのRegression Testを追加 |
| `docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md` | 本実装報告 |

Backend Contract、llama.cpp Adapter、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 3. Shutdown CancelとThread Boundary

```text
Shutdown Worker Thread
  conversation.shutdown(timeout)
    session.request_cancel()
    session.wait(timeout)
    ├─ Finished → True
    └─ Timeout  → False

Producer Iteration Thread
  Native next()の次Chunk境界
  Cancel要求を観測
  Native Stream cancel／close
  Session finally
  Generation Gate解放
```

`force_cancel()`のMethod定義自体は既存Sessionに残しているが、`src/margpa_runtime_llm/`内の汎用Lifecycleからの呼出しは0件である。

## 4. Timeout時のState

Active GenerationがTimeout内に終了しない場合：

- `ConversationGenerationService.shutdown()`は`False`を返す。
- `WebRuntime.close()`は`RuntimeError("The active generation did not stop during shutdown.")`を送出する。
- Active Sessionと`active_request_id`を解放済みと偽装しない。
- Model Close Callbackは呼ばない。
- Shutdown ThreadからNative `cancel()`／`close()`を呼ばない。

Native Boundary解放後はProducer ThreadがCancel／Closeを行い、SessionとGeneration Gateを解放する。その後のRuntime Closeは成功する。

## 5. Model Close Callback

`WebRuntime.close()`へLockと成功状態を追加した。

- Active Session Shutdown成功前：Callback 0回
- Session終了後の最初のRuntime Close：Callback 1回
- 2回目以降のRuntime Close：追加Callback 0回
- Regression Test最終合計：1回

## 6. Lifespan Failure Visibility

Shutdown TimeoutまたはModel Close Failureを無記録で抑制しない。

```text
The web runtime could not shut down cleanly.
```

Lifespanは上記固定MessageをOperator Logへ記録し、同じMessageの`RuntimeError`を例外連鎖なしで送出する。元のRaw Exception、Secret、Absolute PathはLogにも伝播例外にも含めない。

Regression Testでは、Close CallbackへPrivate TextとProject Absolute Pathを含む例外を注入し、次を確認した。

- Safe Logが1件記録される。
- Lifespan Exitが失敗として認識される。
- Raw Private TextはLogへ出ない。
- Project Absolute PathはLogへ出ない。

## 7. Regression Test

Thread-affine Blocking StreamをProducer Threadで消費中に、別Shutdown Threadから50ms Timeoutで`runtime.close()`を実行した。

### Timeout before Native Boundary

- Shutdown Resultは成功ではなく安全な`RuntimeError`
- Shutdown ThreadからNative `cancel()`呼出し0件
- Shutdown ThreadからNative `close()`呼出し0件
- Active Requestは維持
- Model Close Callback 0回

### Recovery after Native Boundary

- Native Boundary解放後のCancel Thread ID = Producer Iteration Thread ID
- Close Thread ID = Producer Iteration Thread ID
- Producer Threadは2秒以内に終了
- `active_request_id is None`
- 次Generationは`completed`
- Runtime Closeを2回実行してCallback合計1回

既存SSE Thread-affine／Backpressure／Cleanup Timeout Regressionも引き続き合格した。

## 8. Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 215 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 32 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、215 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 9. Native Model Smoke Host Resource

```text
Architecture      : arm64
Physical Memory   : 17179869184 bytes／16 GiB
VM Page Size      : 16384 bytes
Pages Free        : 4023
Pages Inactive    : 390661
Pages Speculative : 2602
Compressor Pages  : 96436 occupied
```

Smoke前に別MARGPA／llama／Uvicorn常駐は確認されなかった。設計者Reviewで発生した`Failed to create llama_context`は今回は再現せず、8.32秒で合格した。先行失敗の原因は未確定である。

## 10. Mac Manual Shutdown／Restart

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. `max_new_tokens=2048`の長文Generationを開始し、Streaming中であることを確認した。
2. Active Generation中にServerへShutdownを要求した。
3. Uvicornは`Waiting for connections to close`となり、失敗を成功扱いせずConnection終了を待った。
4. Client Stop後、UIは`生成を停止しました`、ServerはApplication Shutdown完了まで到達した。
5. Shutdown Logに`ValueError: generator already executing`、Raw Exception、Model Close Failureはなかった。
6. 同一PortでServerを再起動し、Model Context作成とApplication Startupが成功した。
7. New Chat後、Message 0件／Status`待機中`を確認した。
8. Restart後の実Model Generationは`RESTARTED.`、Status`完了 (stop)`となった。
9. Browser Console Errorは0件だった。
10. 再起動ServerもApplication Shutdown完了を確認して終了した。

## 11. 未実行・Out of Scope

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Backend全体のThread-safe Stop Contractは新設していない。
- Phase 1完了宣言／Backup、Phase 1-ex、Git／GitHub公開は未着手。

