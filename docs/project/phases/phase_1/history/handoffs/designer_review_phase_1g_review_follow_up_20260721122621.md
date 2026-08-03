# Phase 1-G Review Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_review_follow_up`
- 状態: `changes_requested_cross_thread_cancel_follow_up`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Review Follow-up実装と最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_review_follow_up_20260721121817.md](implementer_status_phase_1g_review_follow_up_20260721121817.md)
- 前回Review: [designer_review_phase_1g_minimal_web_surface_20260721115330.md](designer_review_phase_1g_minimal_web_surface_20260721115330.md)
- 前回Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 追加Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 最新Index: [documentation_index_20260721122621.md](../documentation_index_20260721122621.md)
- supersedes: `designer_review_phase_1g_minimal_web_surface_20260721115330.md`

## 1. Review結論

前回ReviewのMandatory Finding 3系統は、要求どおりFollow-upされている。

- Bounded Queue満杯時にProducerがQueue投入待ちから脱出し、Session Gateを解放するTestが追加された。
- Final Answer前Token Exhaustion Warningは、`completed`後もStatusとAssistant Bubbleへ残る。
- Warning TextはCanonical Assistant Historyへ追加されない。
- 第一者表示名は`Nazuna Research`へ統一され、対象Scopeの廃止済み名義検索は0件である。
- Browser `auto`、Warning、Stop、Post-cancelのManual Evidenceも補完された。

Static／Default／Web／Mac Native Model Smokeはすべて合格した。

ただし、Web CleanupがEvent Loop ThreadからNative Streamへ即時`force_cancel()`するよう変更され、Native Python Generatorが別Threadで`next()`実行中の場合に`ValueError: generator already executing`となる競合を独立再現した。

Disconnect CleanupのMandatory条件を全Timingで満たさないため、Phase 1-Gは現時点でもAcceptedにせず、Cross-thread Cancelだけの局所Follow-upを要求する。

```text
前回High Finding解消       : 1／1／元のQueue詰まり経路
前回Medium Finding解消     : 2／2
前回Low Evidence補完       : 1／1
新規High Finding           : 1
Static／Default Gate        : Pass／211 passed、3 deselected
Web Targeted Test          : Pass／28 passed
Mac Native Model Smoke     : Pass／2 passed、1 skipped
Final Decision             : Changes Requested／One Local Follow-up
Phase 1-H                  : Waiting Phase 1-G Final Review
```

## 2. 前回Findingの解消確認

### 2.1 Queue Backpressure

`consumer_stopped`と50ms Pollingにより、Queue Capacityを超えた投入待ちはConsumer終了後に解除される。Producer側でSession Iteratorを`close()`し、Session `finally`とGeneration Gate解放へ到達する。

96 Chunk、最初の`start`だけConsumerが取得、Queue Capacity超過後にAsync GeneratorをCloseするRegression Testで、次を確認している。

- Native Fake Stream Cancel
- Session完了
- Active Request解除
- Producer Task終了
- 直後の次Generation完了

元の「Queue満杯のためProducerが永久に`queue.put`待ちになる」Findingは解消した。

### 2.2 Token Exhaustion UI

Browserは`final_answer_token_limit`をRequest単位で保持し、後続`completed`でWarning Statusを上書きしない。Canonical Finalが空の場合、Safe WarningをAssistant Bubbleへ表示し、Canonical Historyへ追加しない。

Mac Manual Browser Smokeでも、StatusとBubbleの両方へWarningが残り、空Bubbleが0件であることが確認されている。

前回Medium Findingは解消した。

### 2.3 Public Naming

Package DocstringとWeb UIは`Nazuna Research Governance LLM`へ統一された。

```text
Search Scope : src／tests／scripts／config／pyproject.toml／uv.lock
Match        : 0
Result       : Pass
```

前回Medium Findingは解消した。

### 2.4 Browser `auto` Evidence

実Model／Metal／Browserで`response_language=auto`のStreamingとCanonical Finalが成立した。前回Low Evidence Gapは補完された。

## 3. New Finding

### 3.1 High: Event Loop Threadから実行中Native GeneratorをCloseする競合

対象：

- `src/margpa_runtime_llm/web/streaming.py:87-107`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:81-84`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py:129-155`
- `tests/integration/web/test_web_app.py:461-521`

Consumer終了時、Web Cleanupは次の順序で処理する。

```text
consumer_stopped.set()
session.request_cancel()
session.force_cancel()
  → LlamaCppGenerationStream.cancel()
  → native_stream.close()
```

Producerは`asyncio.to_thread()`上でNative Iteratorを消費する。Client Disconnectが、Producer ThreadでNative Generatorの`next()`実行中に発生した場合、Event Loop Threadから同じGeneratorへ`close()`することになる。

Python Generatorは実行中に別Threadから`close()`できない。Production `LlamaCppGenerationStream`と、Token生成中を模したBlocking Native Generatorで独立診断した結果は次である。

```text
Cross-thread cancel : ValueError: generator already executing
Terminal callback   : force_cancel時点では未実行
```

`stream_session_as_sse()`の`finally`では、最初の`session.force_cancel()`がProducer待機を囲む`try`より前にある。この例外によりQueue DrainとProducer Awaitを開始せずCleanupから離脱する。

既存Regression Testの`FakeStream.cancel()`はBooleanを変更するだけで、Python GeneratorのThread Affinityを再現しない。そのため28件のWeb Testは合格しても、この競合を検出できない。

実ModelのManual Stopが一度成功していても、Disconnect Timing依存のためFindingは解消しない。

Required Follow-up：

1. Event Loop Threadから、実行中Native Python Generatorを直接`close()`しない。
2. Normal Disconnectは`session.request_cancel()`を第一段とし、Producer Threadが次Chunk境界でCancel／Closeする。
3. `consumer_stopped`によりQueue待ちは解除済みであるため、Producer Thread自身の`events.close()`をCleanupの正規経路にする。
4. Timeout Escalationでも、Thread-unsafeな`native_stream.close()`を成功前提にしない。
5. Native Cancelを別Threadから安全に行う必要がある場合は、Generator `close()`ではなくBackendが保証するThread-safe Stop Signal／Stopping Criteria境界を使用する。
6. `cancel()`がIteration Thread以外から呼ばれた場合に失敗するThread-affine Fake StreamまたはProduction Wrapperを使い、早期Close後のGate解放と次GenerationをTestする。
7. Cleanup中の例外を黙って成功扱いせず、Producer終了とGate解放を確認する。

最小修正候補は、Web Cleanupの即時`force_cancel()`を除去し、Cooperative CancelとProducer Thread上のCloseを正規経路にすることである。実装方式の最終判断は実装担当へ委ねるが、Cross-thread Generator Closeを残してはならない。

## 4. Independent Verification

### 4.1 Static／Default／Web Gate

```text
ruff format --check src scripts tests             : Pass／88 files
ruff check src scripts tests                      : Pass
mypy .                                            : Pass／88 source files
python -m compileall -q src scripts tests         : Pass
bash -n Setup Scripts                             : Pass
pytest -q                                         : Pass／211 passed、3 deselected
Conversation／Web Targeted Test                   : Pass／28 passed
uv lock --check --offline                         : Pass／122 packages
Public Naming Search                              : Pass／0 match
```

### 4.2 Mac Native Model Smoke

```text
pytest -q -m model_smoke
Result : 2 passed、1 skipped、211 deselected
Skip   : Lightning Profile Environment未指定
```

通常Mac／Metal環境で実行し、合格した。

### 4.3 Cross-thread Cancel Diagnostic

Repository Fileを変更せず、一時診断ScriptでProduction `LlamaCppGenerationStream`を使用した。

```text
Producer Thread : native generatorのnext()実行中
Main Thread     : stream.cancel()
Result          : ValueError: generator already executing
```

これはTest-only Fakeの挙動ではなく、Current Production Wrapperの挙動である。

## 5. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| 前回Queue Backpressure | Pass | 元のQueue投入待ちは解消 |
| Token Exhaustion UI | Pass | Warning保持／History非追加 |
| Public Naming | Pass | 対象Scope 0 match |
| Browser `auto` Evidence | Pass | Manual Smoke補完 |
| Static／Default Test | Pass | 211 passed、3 deselected |
| Web Targeted Test | Pass | 28 passed |
| Mac Native Model Smoke | Pass | 2 passed、1 skipped |
| Cross-thread Native Cancel | Fail | 実行中Generator CloseでValueError |
| Disconnect Cleanup全Timing | Fail | Producer Await前に例外離脱可能 |

## 6. Next Gate

```text
実装担当 Cross-thread Cancel局所Follow-up
  ├─ Thread-affine Cooperative Cancel
  ├─ Producer Thread上のClose
  ├─ Timeout時のSafe Failure
  └─ Thread-affine Regression Test
        ↓
設計者役 Phase 1-G Final Review
        ↓
Phase 1-G Accepted判定
        ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 7. Authorization Boundary

本Review、追加Handoff、Index作成は、Source／Testsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーが追加Follow-up開始を明示した後、追加Handoffの限定範囲を変更する。

## 8. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
