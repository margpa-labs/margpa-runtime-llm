# Phase 1-G Cross-thread Cancel Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_cross_thread_cancel_follow_up`
- 状態: `changes_requested_shutdown_cancel_follow_up`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Cross-thread Cancel Follow-upとPhase 1-G最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md](implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)
- 対象Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 前回Review: [designer_review_phase_1g_review_follow_up_20260721122621.md](designer_review_phase_1g_review_follow_up_20260721122621.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 追加Handoff: [implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md](implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md)
- 最新Index: [documentation_index_20260721164248.md](../documentation_index_20260721164248.md)
- supersedes: `designer_review_phase_1g_review_follow_up_20260721122621.md`

## 1. Review結論

SSE Consumer終了時のEvent Loop ThreadからProducer Thread上のNative Generatorを即時Closeする競合は解消した。

- Web Streaming Cleanupから`session.force_cancel()`が除去された。
- `request_cancel()`と`consumer_stopped`によるCooperative Cancelへ統一された。
- Native Streamの`cancel()`と`close()`はProducer Iteration Thread上で行われる。
- Timeout時にCross-thread Closeで成功を偽装せず、明示的Cleanup Failureとする。
- Thread-affine正常Cleanup、Timeout Safe Failure、Queue BackpressureのRegression Testが合格した。

ただし、`ConversationGenerationService.shutdown()`のTimeout EscalationにCross-thread `force_cancel()`が残っている。Active Generation中のWeb Runtime Shutdownで前回と同じ`ValueError: generator already executing`を独立再現した。

この例外により`WebRuntime.close()`のModel Close Callbackまで到達せず、FastAPI Lifespanは現在その例外を記録せずに抑制する。Phase 1-GのShutdown／Unload受入条件と整合しない。

したがってPhase 1-GはまだAcceptedとせず、Shutdown Cancelだけの追加局所Follow-upを要求する。

```text
SSE Disconnect Cross-thread Finding : Resolved
Queue Backpressure                   : Pass
Timeout Safe Failure                 : Pass
Targeted Web／Conversation Test     : Pass／30 passed
Default Regression                   : Pass／213 passed、3 deselected
Shutdown Cross-thread Cancel         : Fail／1 Mandatory Finding
Reviewer Native Model Smoke          : Inconclusive／2 failed、1 skipped
Final Decision                       : Changes Requested
Phase 1-H                            : Waiting Phase 1-G Acceptance
```

## 2. 解消確認

`src/margpa_runtime_llm/web/streaming.py`は次の順序になった。

```text
Event Loop Thread
  consumer_stopped.set()
  session.request_cancel()
  Queue Drain
  Producer TaskをAwait

Producer Thread
  Queue投入待ち解除、またはNative next()の次Chunk境界
  Cancel要求を観測
  Native Stream cancel／close
  Session finally
  Generation Gate解放
```

Thread-affine Blocking Streamにより、別Threadからの`cancel()`／`close()`を失敗させ、Producer Thread上のCancel／Close、Session／Gate解放、後続Generation、Timeout中のNative Call 0件を確認している。直接対象として適切なRegressionである。

## 3. Mandatory Finding

### 3.1 High: Runtime ShutdownにCross-thread `force_cancel()`が残存

対象：

- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:246-255`
- `src/margpa_runtime_llm/web/contracts.py:46-49`
- `src/margpa_runtime_llm/web/app.py:46-50`

Current Shutdownは次である。

```text
Web Lifespan Shutdown Worker Thread
  runtime.close()
  conversation.shutdown()
    request_cancel()
    session.wait(10 seconds)
    session.force_cancel()
      stream.cancel()
      native generator.close()
```

SSE Producer ThreadがNative Generatorの`next()`内にいる場合、Shutdown Worker Threadの`force_cancel()`はThread Affinityを破る。

Repositoryを変更しない一時診断結果：

```text
Iteration Thread ID       : 6106624000
Shutdown Thread ID        : 8525073536
shutdown result           : None
shutdown error            : ValueError: generator already executing
Cancel Thread at timeout  : Shutdown Thread

Native Boundary解放後
  Producer                : Finished
  Session                 : Finished
  Active Request          : None
```

Required Correction：

1. `shutdown()`からThread-unsafeな`session.force_cancel()`を呼ばない。
2. Shutdownも`request_cancel()`とProducer Thread上のCancel／Closeを正規経路とする。
3. Timeout時は`False`または明示例外とし、Session解放やModel Unload成功を偽装しない。
4. Backend保証のThread-safe Stop Signalが必要なら、Generator `close()`と分離したContractを先に設計Reviewへ戻す。
5. Runtime Shutdown FailureをLifespanが無記録で抑制しない。
6. Active Generation中ShutdownのThread-affine Regression Testを追加する。
7. Cleanup成功時はModel Close Callbackが正確に1回だけ呼ばれることをTestする。

## 4. Independent Verification

```text
ruff format --check src scripts tests     : Pass／88 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／88 source files
python -m compileall -q src scripts tests : Pass
pytest -q                                 : Pass／213 passed、3 deselected
Conversation／Web Targeted               : Pass／30 passed
uv lock --check --offline                 : Pass／122 packages
bash -n scripts/setup/*.sh                : Pass
```

`uv`はSandboxからUser Cacheを使えなかったため、書込可能な一時Cacheを指定してLock整合性を確認した。

### 4.1 Native Model Smoke

```text
Implementer Evidence : Pass／2 passed、1 skipped
Reviewer Run 1       : Fail／2 failed、1 skipped
Reviewer Run 2       : Fail／2 failed、1 skipped
Failure Point        : Model Load／llama_context creation
Error                : ValueError: Failed to create llama_context
```

Reviewer実行時、別のMARGPA／Python／Uvicorn／llama関連Processは確認されなかった。失敗はPhase 1-G Web差分の実行前に発生し、Current Follow-upのSource差分による失敗とは現時点で断定しない。Reviewer Native Gateは合格していないため、Shutdown Follow-up後の再Reviewで必ず再実行する。

## 5. Acceptance Matrix

| Area | Result | Notes |
|---|---|---|
| SSE Disconnect Cooperative Cancel | Pass | Cross-thread Close除去 |
| Queue Backpressure | Pass | Consumer終了後にProducer解放 |
| Cleanup Timeout | Pass | Unsafe Escalationなし |
| Thread-affine Regression | Pass | Cancel／CloseはProducer Thread |
| Static／Default Regression | Pass | 213 passed |
| Web Targeted | Pass | 30 passed |
| Active Generation Shutdown | Fail | Cross-thread `force_cancel()`再現 |
| Model Close Callback | Fail path present | Shutdown例外時に未到達 |
| Lifespan Failure Visibility | Fail | Shutdown例外を抑制 |
| Reviewer Native Model Smoke | Inconclusive | `llama_context` creation failure |

## 6. Next Gate

```text
実装担当 Phase 1-G Shutdown Cancel局所Follow-up
  ↓
設計者役 Phase 1-G Final Review
  ├─ Static／Default／Targeted
  ├─ Shutdown Diagnostic
  └─ Mac Native Model Smoke再実行
  ↓
Phase 1-G Accepted判定
  ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 7. Authorization Boundary

本Review、追加Handoff、Index作成はSource／Testsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

## 8. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
