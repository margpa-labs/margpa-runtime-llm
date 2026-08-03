# 実装担当向け Phase 1-G Shutdown Cancel Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_shutdown_cancel_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md](designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md)
- 実装報告: [implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md](implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)
- 前回Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 最新Index: [documentation_index_20260721164248.md](../documentation_index_20260721164248.md)
- supersedes: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`

## 1. Current State

SSE Disconnect／Consumer CloseのCross-thread Cancelは解消した。残件はActive Generation中のRuntime ShutdownにおけるCross-thread `force_cancel()`と1件である。

```text
Resolved : SSE Event Loop → Native Generator force_cancel
Remaining: Shutdown Worker → Native Generator force_cancel
Impact   : ValueError、Model Close Callback未到達、Shutdown Failure抑制
```

Phase 1-GはChanges Requested、Phase 1-HはWaitingである。

## 2. Authorized Scope after User Approval

ユーザーが追加Follow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/app.py
tests/unit/conversation/
tests/unit/web/
tests/integration/web/test_web_app.py
docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_*
```

Backend Contractとllama.cpp Adapterの変更が不可避な場合、実装前に理由、Thread-safe保証、CLIへの影響、最小変更範囲を設計者役へ戻す。

## 3. Required Work

1. `ConversationGenerationService.shutdown()`のTimeout経路からThread-unsafeな`session.force_cancel()`を除去する。
2. `request_cancel()`とProducer Iteration Thread上のNative Cancel／Closeを正規Shutdown経路とする。
3. Timeout時は成功を偽装せず、`False`または明示例外とする。
4. SessionがまだActiveな場合、Model Close Callbackを先に呼ばない。
5. Session終了後、Model Close Callbackを正確に1回だけ呼ぶ。
6. FastAPI LifespanがShutdown Failureを無記録で抑制しない。外部へSecret／Path／Raw Exceptionを出さず、OperatorがFailureを認識できるようにする。
7. `force_cancel()`を残す場合、Thread-affine Streamへ安全に呼べないMethodとして汎用Lifecycleから到達不可能にする。
8. Backend保証のThread-safe Stop Signalを新設する場合は、無断にContractを拡張せず設計Reviewへ戻す。

## 4. Required Regression Test

Thread-affine Blocking Streamを用い、次をAssertする。

### 4.1 Timeout before Native Boundary

- ProducerがNative `next()`内でBlockingしている。
- 別Threadから短いTimeoutで`shutdown()`する。
- Shutdown ThreadからNative `cancel()`／`close()`が呼ばれない。
- Resultは成功ではない。
- Active Request解放を偽装しない。
- Model Close Callbackは呼ばれない。

### 4.2 Recovery after Native Boundary

- Native Boundary解放後、Producer Thread上でCancel／Closeされる。
- Session／Generation Gateが解放される。
- 再度のShutdownまたはRuntime Closeが成功する。
- Model Close Callbackは合計1回である。
- 未完了Producer Task／Threadが残らない。

### 4.3 Lifespan Failure Visibility

- Shutdown TimeoutまたはClose Failureを成功扱いしない。
- FailureをOperatorが認識できる。
- Client向けResponseへRaw Exception、Absolute Path、Secretを出さない。

## 5. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

Native Model Smokeは実装報告で2 passedだったが、設計者Review環境では`Failed to create llama_context`により2回失敗した。Follow-up完了時に再実行し、Host Resource条件と結果をStatusへ記録する。

Mac Manual Browserで、Stop、Post-cancel Generation、New Chat、Active Generation中のServer Shutdown／Restartを確認する。

## 6. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- Shutdown Cancelの修正方式とThread Boundary
- Timeout時のState
- Model Close Callbackの回数
- Lifespan Failure Visibility
- Regressionの再現条件と結果
- 全Verification CommandのExit Code／件数
- Native Model SmokeのHost Resource条件と結果
- Manual Shutdown／Restart結果
- Phase 1-H未着手の明記

## 7. Out of Scope

- 解消済みSSE Disconnect／Queue Backpressure／Token Warning／Public Namingの再変更
- Backend全体のThread-safe Stop Contract新設
- Phase 1-H Summary Mode
- Lightning Full Upload／Model Transfer
- React／本格UI／Conversation永続化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 8. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Shutdown Cancel Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 9. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。
