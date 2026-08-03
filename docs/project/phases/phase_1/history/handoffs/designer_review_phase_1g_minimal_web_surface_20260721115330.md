# Phase 1-G Minimal Web Surface 設計Review

- 文書ID: `designer_review_phase_1g_minimal_web_surface`
- 状態: `changes_requested_before_phase_1h`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Repository実装、Web Surface、Security、Streaming、Manual Evidence
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_minimal_web_surface_20260721105005.md](implementer_status_phase_1g_minimal_web_surface_20260721105005.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- Follow-up Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 最新Index: [documentation_index_20260721115330.md](../documentation_index_20260721115330.md)
- supersedes: なし（Phase 1-G Review系列の初回）

## 1. Review結論

Phase 1-Gは、Framework境界、Browser所有のEphemeral Conversation、Request単位の3設定、Model Lifecycle、Basic Auth、Safe Rendering、SSE Contract、既存CLI非回帰の大部分で要件に沿っている。

Static／Default／Web／Mac Native Model Smokeはすべて合格した。実装報告の主要Evidenceも独立検証と一致している。

ただし、次のMandatory項目に未解消Findingがあるため、現時点ではPhase 1-Gを受け入れず、Phase 1-Hへ進めない。

```text
High Finding                 : 1
Medium Finding               : 2
Low Observation              : 2
Static／Default Gate          : Pass
Web Targeted Test            : Pass／26 passed
Mac Native Model Smoke       : Pass／2 passed、1 skipped
Manual Browser Smoke         : Broad Pass／Evidence補完1件
Final Decision               : Changes Requested
Phase 1-H                    : Waiting Follow-up Review
```

必須Follow-upは次の3系統である。

1. Bounded Queueが満杯の状態でも、Client Disconnect後にProducerとGeneration Gateを確実に解放する。
2. Final Answer前Token Exhaustion Warningを、`completed` Eventで上書きせず画面へ明示する。
3. User-visible UIを含むSource内の廃止済み第一者名義を`Nazuna Research`へ統一する。

## 2. Positive Findings

次は設計と実装の両方で成立している。

- FastAPI／UvicornはDelivery AdapterとEntrypointへ局所化され、Inference／Presentation Coreへ侵入していない。
- Browser TabがCanonical `user／assistant` Historyを所有し、Serverは会話を永続保存または利用者間共有しない。
- Client指定の`system／tool` Role、不正順序、空Message、不正SettingをTyped Contractで拒否する。
- UI設定は`response_language`、`max_new_tokens`、`thinking_visibility`の3項目だけである。
- Request OverrideはTracked TOMLを書き換えず、Thinking VisibilityとThinking Executionを分離している。
- ModelはLifespanで1回Load／1回Unloadされ、同時Generationは409でFail Fastする。
- Hidden ThinkingはSSE DeltaとCanonical Assistant Historyへ混入しない。
- Basic AuthはServer側、Environment-only、Constant-time Compareであり、Non-loopback＋Auth DisabledはFail Closedになる。
- `/healthz`以外のUI、Asset、APIが同一認証境界にあり、Interactive API Docsは無効である。
- Model Outputは`textContent`で描画し、External Script／CDN／Fontや`innerHTML`を使用していない。
- CSP、`no-store`、`nosniff`、`no-referrer`を設定している。
- Phase 1-H Summary Mode Controlを先行表示していない。
- Current CLI、Config、Model Port、llama.cpp Adapterの既存Contractを破壊していない。

## 3. Findings

### 3.1 High: Backpressure中のDisconnectでProducerとGeneration Gateが残留し得る

対象：

- `src/margpa_runtime_llm/web/streaming.py:29-57`
- `tests/integration/web/test_web_app.py:377-414`

同期Model IteratorからAsync SSEへ渡すQueueは`maxsize=32`である。Producer Threadは各Eventを次の処理でQueueへ投入し、完了まで同期的に待つ。

```text
run_coroutine_threadsafe(queue.put(event), loop).result()
```

Client側Consumerが終了し、Queueが満杯の場合、Producerは`queue.put`で停止する。Async Generatorの`finally`はCancel要求後にProducerを最大10秒待ち、Timeout時に`session.force_cancel()`を呼ぶが、QueueをDrainせずProducerを再度待たない。

このため、Native StreamへCancelを設定しても、ProducerはNative Iteratorへ戻れずQueue投入待ちのまま残り得る。`ConversationGenerationSession.events()`の`finally`へ到達しなければ、Active SessionとGeneration Gateも解放されない。

既存Disconnect Testは2 Chunkだけを生成し、Async Generatorを最後までDrainしているため、Queue Capacity超過とConsumer早期終了を再現していない。

これは次のMandatory要件に反する。

- LockはTerminal／Error／Disconnectの全経路でReleaseする。
- Browser Disconnect時にNative GenerationをCancelする。
- Cancel後のGenerationを成立させる。
- UI側の受信遅延でModel Generationを恒久Blockしない。

Required Follow-up：

- Consumer終了をProducerへ伝えるCancellation／Stop Signalを設ける。
- Disconnect後もProducerがQueue投入待ちから脱出し、Session IteratorをCloseできる構造にする。
- Cleanup完了前にGeneration Gate解放を成功扱いしない。
- Queue Capacityを超えるEvent列でConsumerを早期CloseするRegression Testを追加する。
- Testは限定時間内のProducer終了、`active_request_id is None`、次Generation成功、Orphan Task／Thread不在を確認する。

### 3.2 Medium: Token Exhaustion Warningが直後のCompleted表示で消える

対象：

- `src/margpa_runtime_llm/web/static/app.js:138-153`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:132-153`
- `tests/unit/conversation/test_conversation_generation.py:286-287`

Serverは`finish_reason=length`かつCanonical Finalが空の場合、次を正しく送信する。

```text
code    : final_answer_token_limit
message : 最終回答を生成する前にToken上限へ到達しました。
```

しかしBrowserは`warning` EventでStatusを設定した直後、後続`completed` EventでStatusを`完了 (length)`へ上書きする。Canonical Finalが空の場合はPending UserをRollbackするだけで、Assistant表示Nodeも空のまま残る。

したがって、Server Contractは成立しているが、User-visible Acceptanceでは「空Responseにならず明示される」が成立しない。現在の自動TestはServer Warning生成だけを確認し、Browser Event適用後の最終表示を検証していない。

Required Follow-up：

- `final_answer_token_limit`をRequest単位で保持し、後続`completed`で上書きしない。
- Canonical Finalが空でも、正本MessageをAssistant Historyへ混入させず、画面上には上記Safe Warningを明示する。
- 空Assistant Bubbleだけを残さない。
- Browser Event列`warning → completed`後の最終表示をRegression Testまたは同等の決定論的検証で固定する。

### 3.3 Medium: Source内に廃止済み第一者名義が2箇所残っている

対象：

- `src/margpa_runtime_llm/__init__.py:1`
- `src/margpa_runtime_llm/web/static/index.html:14`

前者はPackage Docstring、後者はWeb UIへ直接表示されるEyebrowである。Current Mandatory Ruleは、第一者の作者・研究・表示名を`Nazuna Research`へ統一し、現時点で例外を認めていない。

Required Follow-up：

- 両方を`Nazuna Research Governance LLM`へ統一する。
- `src／tests／scripts／config／Root Metadata`を再検索し、廃止済み第一者名義が0件であることをEvidence化する。
- Third-party Provenance、Model Author、Dependency Authorまで誤置換しない。

## 4. Low Observations

### 4.1 Request Byte Limitは`Content-Length`へ依存する

`MAX_CHAT_REQUEST_BYTES`の事前拒否は`Content-Length` Headerがある場合だけ行われる。Header省略／Chunked Bodyでは、PydanticのMessage／文字数上限により意味的には拒否されるが、ASGIがBodyを受理する前の厳密なByte上限にはならない。

少人数PreviewのPhase 1-G Acceptanceを単独で止めるFindingにはしない。Public Hardening時には、信頼できるReverse ProxyのRequest Size LimitまたはASGI側の実Body上限を明示する。

### 4.2 Browser Manual Evidenceに`auto`の明示結果がない

実装報告は日本語Defaultと`en`を記録しているが、Browser UIで`auto`を選択した結果を個別に記録していない。Contract上は`ja／en／auto`を受理し、既存Language Composerを再利用している。

Follow-up Manual Smokeで`auto`を1回実行し、受理、Streaming、最終回答までのEvidenceを補完する。

## 5. Independent Verification

### 5.1 Static／Default／Web Gate

```text
ruff format --check src scripts tests             : Pass／88 files
ruff check src scripts tests                      : Pass
mypy .                                            : Pass／88 source files
python -m compileall -q src scripts tests         : Pass
bash -n Mac／Lightning Setup／Preflight            : Pass
pytest -q                                         : Pass／209 passed、3 deselected
Conversation／Web Targeted Test                   : Pass／26 passed
uv lock --check --offline                         : Pass／122 packages
```

Sandbox内の`uv lock`は共有uv CacheへのAccess制限でExit 2となった。Repository／Lock Failureではないため、通常ホスト環境で同一Commandを再実行しExit 0を確認した。

### 5.2 Mac Native Model Smoke

```text
pytest -q -m model_smoke
Result : 2 passed、1 skipped、209 deselected
Skip   : Lightning Profile Environment未指定
```

Sandbox内ではMetal Contextを作成できず2件失敗した。通常Mac／Metal環境で同一Commandを再実行し2件合格したため、Product Runtime Failureとは扱わない。

### 5.3 Identity Search

```text
Search Scope : src／tests／scripts／config／pyproject.toml／uv.lock
Match        : 2
Location     : Package Docstring 1、Web UI 1
Result       : Follow-up Required
```

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Dependency／Lock | Pass | 122 packages |
| Static／Default Test | Pass | 209 passed、3 deselected |
| Mac Model Smoke | Pass | 2 passed、1 skipped |
| Web Architecture Boundary | Pass | Framework局所化 |
| Conversation Isolation | Pass | Browser-owned／Server non-persistent |
| Settings 3項目 | Pass | Request Overrideのみ |
| Preview Access Control | Pass | Non-loopback Fail Closed |
| Output Rendering | Pass | Plain Text／Local Assets |
| Normal Stop／Post-cancel | Pass | Current短いStream条件 |
| Backpressured Disconnect | Fail | Producer／Gate残留経路 |
| Token Exhaustion UI | Fail | WarningがCompletedで上書き |
| Public Naming | Fail | Source 2件 |
| Browser `auto` Evidence | Pending | Follow-up Manual Smoke |

## 7. Next Gate

```text
実装担当 Phase 1-G Follow-up
  ├─ Disconnect／Backpressure Cleanup
  ├─ Token Exhaustion UI Warning保持
  ├─ Source表示名2件統一
  ├─ Regression Test追加
  └─ Browser auto／Warning Manual Smoke
        ↓
設計者役 Phase 1-G Follow-up Review
        ↓
Phase 1-G Accepted判定
        ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本Review、Follow-up Handoff、Indexの作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーがFollow-up開始を明示的に指示した後、Follow-up Handoffの限定範囲を変更する。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
