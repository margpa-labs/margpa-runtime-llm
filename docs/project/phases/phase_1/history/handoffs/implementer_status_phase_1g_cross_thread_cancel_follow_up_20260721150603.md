# Phase 1-G Cross-thread Cancel Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_cross_thread_cancel_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 15:06:03 JST`
- Snapshot: `20260721150603`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_review_follow_up_20260721122621.md`
- 対象Handoff: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`

## 1. 結果

Phase 1-G Cross-thread Cancel Follow-upを限定Scope内で完了した。

Event Loop Threadから実行中Native Generatorへ`force_cancel()`／`close()`する経路を除去し、Producer Thread上でCancel／CloseするCooperative Cancelへ統一した。Thread-affine Regression、既存Queue Capacity超過Regression、Static／Default／Mac Native Model／Manual Browser Gateはすべて合格した。

Phase 1-Hには着手していない。

## 2. 変更File

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/web/streaming.py` | Event Loop側の即時／Timeout時`force_cancel()`を除去し、`request_cancel()`＋Producer終了待ちへ変更 |
| `tests/integration/web/test_web_app.py` | Thread-affine Blocking Stream、正常Cleanup、Timeout Safe FailureのRegression Testを追加 |
| `docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md` | 本実装報告 |

Backend Contract、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 3. Cross-thread競合の修正方式

Consumerが終了した場合は次の順序で処理する。

```text
Event Loop Thread
  consumer_stopped.set()
  session.request_cancel()
  Queue Drain
  Producer Taskを最大10秒Await

Producer Thread
  Queue投入待ちPollingから脱出、またはNative next()の次Chunk境界へ到達
  SessionがCancel要求を観測
  Native Stream cancel()
  Session Iterator close()
  Session finally
  Generation Gate解放
```

`consumer_stopped`により、Bounded Queueが満杯でもProducerの`queue.put()`待ちは解除される。Native `next()`中の場合は、そのThreadが次のChunk境界へ到達するまでEvent Loop側からGeneratorを閉じない。

Cancel／CloseはProducerのIteration Thread上だけで実行される。

## 4. Timeout時の動作

Production Cleanup Timeoutは10秒である。

10秒以内にProducerが終了しない場合、Thread-unsafeなNative Generator CloseへEscalateしない。`RuntimeError("The SSE producer did not stop during cleanup.")`を送出し、成功扱いしない。

Backend保証のThread-safe Stop Signalは今回追加していない。Native `next()`が長時間復帰しない場合は、明示的Cleanup失敗となる。

## 5. Regression Test

### 5.1 Thread-affine正常Cleanup

Fake Streamは次を実装する。

- Native Iteration Thread IDを記録する。
- `next()`内部でTest制御SignalまでBlockingする。
- `cancel()`／`close()`がIteration Thread以外から呼ばれた場合、`ValueError("generator already executing")`を送出する。

ProducerがNative `next()`中にConsumer Async GeneratorをCloseし、その後Native Boundaryを解放した。

結果：

- Async Generator CloseでCross-thread例外なし
- `cancel()` Thread ID = Producer Iteration Thread ID
- `close()` Thread ID = Producer Iteration Thread ID
- Sessionが2秒以内に終了
- `active_request_id is None`
- 未完了Producer Task 0件
- 直後の次Generationが`completed`

### 5.2 Timeout Safe Failure

Test内だけCleanup Timeoutを50msに短縮し、Native `next()`をBlockingした。

結果：

- Async Generator Closeは期待どおり`RuntimeError`
- Timeout時点のNative `cancel()`呼出し0件
- Timeout時点のNative `close()`呼出し0件
- Active Requestを解放済みと偽装しない
- Native Boundary解放後はProducer Thread上でCancel／Close
- Session／Gate解放後、次Generationが`completed`

既存のQueue Capacity `32`、96 Chunk、Consumer早期Close Regressionも引き続き合格した。

## 6. Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 213 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 30 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、213 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 7. Mac Manual Browser

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. 長文Generation開始後にStop Buttonが有効になることを確認した。
2. Stop後、Statusは`生成を停止しました`、Sendは再有効、Stopは無効となった。
3. New Chat後、Messageは0件、Statusは`待機中`となった。
4. Stop／New Chat直後のGenerationが`完了 (stop)`まで到達した。
5. Browser Console Errorは0件だった。
6. Test ServerはApplication Shutdown完了を確認して終了した。

## 8. 未実行・Out of Scope

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Backend Contract／Thread-safe Native Stop Signalは変更していない。
- Phase 1完了宣言／Backup、Phase 1-ex、Git／GitHub公開は未着手。

