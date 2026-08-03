# 実装担当向け Phase 1-G Cross-thread Cancel Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_review_follow_up_20260721122621.md](designer_review_phase_1g_review_follow_up_20260721122621.md)
- 実装報告: [implementer_status_phase_1g_review_follow_up_20260721121817.md](implementer_status_phase_1g_review_follow_up_20260721121817.md)
- 前回Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 最新Index: [documentation_index_20260721122621.md](../documentation_index_20260721122621.md)
- supersedes: `implementer_handoff_phase_1g_review_follow_up_20260721115330.md`

## 1. Current State

前回FindingのQueue Backpressure、Token Exhaustion UI、Public Namingは解消した。Static／Default／Web／Mac Native Gateも合格している。

残件は、Event Loop ThreadからProducer Thread上で実行中のNative Python Generatorへ即時`force_cancel()`するCross-thread競合1件だけである。

## 2. Authorized Scope after User Approval

ユーザーが追加Follow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/web/streaming.py
tests/integration/web/test_web_app.py
tests/unit/web/                         # 必要な場合だけ
docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_*
```

Backend Contract変更が不可避な場合は、実装前に理由、最小変更範囲、既存CLIへの影響を設計者役へ返す。まずWeb Boundary内のThread-affine Cooperative Cancelで解決する。

## 3. Required Work

1. Consumer終了時に`consumer_stopped`を設定する。
2. `session.request_cancel()`でCooperative Cancelを要求する。
3. Event Loop Threadから実行中Native Generatorへ即時`session.force_cancel()`しない。
4. Queue投入待ちはCurrent Pollingで解除し、Producer Thread自身がSession IteratorをCloseする。
5. Producer Threadが次Chunk境界でCancelを観測し、同一Thread上でNative StreamをCancel／Closeする。
6. Producer終了、Session `finally`、Generation Gate解放を待つ。
7. Timeout時は成功扱いせず、Thread-unsafeなGenerator Closeで結果を偽装しない。
8. Timeout EscalationにNative強制停止が必要なら、Backend保証のThread-safe Stop Signalを設計し、先に設計者役へEscalateする。

## 4. Required Regression Test

Fake StreamへThread Affinityを持たせる。

```text
Iteration Thread IDを記録
cancel／closeが別Threadなら例外
ProducerがNative next()中にConsumerをClose
```

Testは次をAssertする。

- Async Generator CloseがCross-thread `cancel／close`例外を出さない。
- Producer Thread上でCancel／Closeされる。
- Sessionが限定時間内に完了する。
- `active_request_id is None`になる。
- Producer Taskが残らない。
- 直後の次Generationが`completed`になる。
- Current Queue Capacity超過Regressionも引き続き合格する。

可能であれば、Production `LlamaCppGenerationStream`とBlocking Native Generatorを使ったUnit／Integration Testも追加し、`generator already executing`を再発防止する。

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

Mac Manual Browserで、Stop、Post-cancel Generation、New Chatを再確認する。大規模Lightning Uploadはまだ行わない。

## 6. Implementer Status Requirement

完了後、次を作成する。

```text
docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- Cross-thread競合の修正方式
- Cancel／Closeを実行するThread境界
- Timeout時の動作
- Regression Testの再現条件と結果
- 全Verification CommandのExit Code／件数
- Manual Stop／Post-cancel結果
- Phase 1-H未着手の明記

## 7. Out of Scope

- 解消済みToken Warning UIの再設計
- 解消済みPublic Namingの再変更
- Phase 1-H Summary Mode
- React／本格UI／Conversation永続化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 8. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Cross-thread Cancel Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 9. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。
