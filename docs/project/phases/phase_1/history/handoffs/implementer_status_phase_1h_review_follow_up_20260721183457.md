# Phase 1-H Review Follow-up 実装者Status

- 更新時点: 2026-07-21 18:34:57 JST
- 担当: 実装者役担当Task
- 対象: Phase 1-H Review Follow-up 4 Mandatory Finding
- 状態: 限定修正・自動検証・Mac Metal Smoke・Browser確認 完了、設計者再Review待ち
- 正本取扱い: Index／Review／Handoff／Requirements／Architecture／ADRは読み取り専用

## 1. 結論

Follow-up Handoffで指定された4 Findingを、許可Scope内だけで修正した。

```text
Finding 1 Successful Summary SSE Privacy : Fixed
Finding 2 Long Silent SSE Keepalive       : Fixed
Finding 3 Summary Risk Notice             : Fixed
Finding 4 Runtime Error Relocalization     : Fixed
```

Config Schema、Summary Prompt、Model Adapter、CLI、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 2. 変更File

- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/web/streaming.py`
- `src/margpa_runtime_llm/web/static/app.js`
- `src/margpa_runtime_llm/web/static/index.html`
- `tests/unit/conversation/test_conversation_generation.py`
- `tests/integration/web/test_web_app.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `docs/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md`

`app.css`の追加変更は不要だった。

## 3. Finding 1：Successful Summary SSE Data Minimization

### 3.1 修正内容

Summary成功時のPublic SSEから次を削除した。

```text
original_assistant_message
summary_assistant_message
presented_source
original_usage
summary_usage
```

Original canonical answerは`ConversationGenerationSession`内のLocal ArtifactとしてSummary生成とfallback判断にだけ使用する。Clientへ別Fieldで返さず、永続保存もしない。

### 3.2 Success Payload

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "usage": null,
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

回答本文は`assistant_message`のPresented Summaryだけである。`transformation`は本文を含まない状態Metadataである。

### 3.3 Fallback Payload

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Original answer"
  },
  "usage": null,
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": false,
    "fallback_used": true,
    "original_finish_reason": "stop",
    "summary_finish_reason": null
  }
}
```

FallbackではOriginalがPresented Answerなので`assistant_message`として返すが、別Fieldへ重複させない。不完全Summary本文は送らない。

### 3.4 Test Evidence

- Unit: Summary成功Event全体に`Long original answer`が存在しない。
- Web Integration: Raw SSE Response全体に`Original answer`、Original Thinking、Summary Thinkingが存在しない。
- Web Integration: `original_assistant_message`／`summary_assistant_message` Keyが存在しない。
- Web Integration: Summaryは`assistant_message`として存在し、`summary_applied=true`、`fallback_used=false`。
- Fallback Integration: Originalの`assistant_message` Payloadは1個、不完全Summaryは0、`fallback_used=true`。

## 4. Finding 2：SSE Keepalive

### 4.1 固定Contract

```text
Interval    : 15.0 seconds
Wire Format : : keepalive\n\n
SSE Type    : Comment
event/data  : None
```

`SSE_KEEPALIVE_INTERVAL_SECONDS = 15.0`と`SSE_KEEPALIVE_COMMENT = ": keepalive\n\n"`を`web/streaming.py`へ追加した。

### 4.2 Lifecycle

- Async Consumer側だけでIdle時間を計測する。
- Application Event送信時にIdle Timerをresetする。
- 15秒Application Eventがない場合だけCommentをyieldする。
- Normal Hidden Generation／Summary Buffered Generationの両段階で動作する。
- Conversation Event Queueへ積まない。
- Terminal item受信後はKeepaliveを送らない。
- Consumer終了時は既存`finally`でcooperative cancel、Queue drain、producer joinを行う。
- Heartbeat専用Task／Threadは作らないためCleanup対象を増やさない。
- CommentへRequest ID、Prompt、Exception等を含めない。

### 4.3 Regression Test

- Default Interval `15.0`とWire Formatを固定Test。
- Intervalだけ`0.01`へmonkeypatchし、実時間15秒を待たず確認。
- Blocking Normal Generation中にKeepaliveを確認。
- Buffered Summary Generation中にKeepaliveを確認。
- Keepalive後も通常Event／completedを受信。
- completed countは1回。
- Keepaliveに`event:`／`data:`がない。
- Keepalive後のconsumer closeでproducer-thread native cancel／closeを確認。
- Cleanup後に`margpa-sse-producer-*` Taskが残らない。
- Existing backpressure／disconnect／cleanup timeout／shutdown Testも継続合格。

## 5. Finding 3：Summary Risk Notice

### 5.1 日本語

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増え、要約により詳細、前提、注意事項等が省略・変形される可能性があります。
```

### 5.2 English

```text
When ON, the completed answer is summarized by the same model.
This increases latency and token usage, and details, assumptions, or cautions may be omitted or altered by the summary.
```

Initial HTMLとTranslation Dictionaryを同義内容へ更新した。品質／正確性保証は追加していない。既存Layout／CSS変更は不要だった。Static Testで日英のRisk表現を固定した。

## 6. Finding 4：Runtime Status Relocalization

### 6.1 State

Render済みError文字列を`runtimeText`へ保持する方式を廃止し、次のStable Stateへ変更した。

```text
loading:
  kind           = loading
  translationKey = runtimeLoading
  text           = null

metadata:
  kind           = metadata
  translationKey = null
  text           = opaque Model／Profile／Device Metadata

known_error:
  kind           = known_error
  translationKey = runtimeLoadFailed
  text           = null
```

`renderRuntimeStatus()`を追加し、`applyTranslations()`から常に呼ぶ。Metadata成功時だけOpaque Textをそのまま表示し、Loading／Known Failureは現在のUI Languageで毎回解決する。

### 6.2 Evidence

Source Contract Test:

- `runtimeText`が存在しない。
- `runtimeStatus.kind=loading`、`known_error`、`runtimeLoadFailed`を確認。
- `renderRuntimeStatus()`を確認。

Mac BrowserでRuntime APIを意図的に500へした確認:

```text
ja : Runtime情報を取得できませんでした。
en : Could not load runtime information.
ja : Runtime情報を取得できませんでした。
```

同じ切替でSummary Risk Noticeも日英へ再描画された。Response Language値は変更していない。

## 7. Verification

```text
./.venv/bin/ruff format --check src scripts tests
  Exit 0／93 files already formatted

./.venv/bin/ruff check src scripts tests
  Exit 0／All checks passed

./.venv/bin/mypy .
  Exit 0／93 source files、no issues

./.venv/bin/python -m compileall -q src scripts tests
  Exit 0

node --check src/margpa_runtime_llm/web/static/app.js
  Exit 0

./.venv/bin/pytest -q
  Exit 0／246 passed、3 deselected

./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
  Exit 0／51 passed

./.venv/bin/pytest -q -m model_smoke
  Exit 0／2 passed、1 skipped、246 deselected

uv lock --check --offline
  Exit 0／Resolved 122 packages

bash -n scripts/setup/setup_macos_arm64_metal.sh \
  scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  scripts/setup/preflight_lightning_ai_studio.sh
  Exit 0
```

Model SmokeのSkip 1件は`MARGPA_PHASE1F_PROFILE`未設定のPhase 1-F cross-environment Testであり、Phase 1-H Follow-up blockerではない。

## 8. Manual Browser／Raw SSE確認

- Runtime Failure後の`ja → en → ja`: Pass。
- Summary Risk Noticeの日英表示: Pass。
- UI LanguageとResponse LanguageのState分離: 維持。
- Summary SuccessのRaw SSE Original非送信: Deterministic ASGI Integration TestでResponse Bodyを直接検査しPass。
- Summary FallbackのOriginal表示Contract: Deterministic ASGI Integration TestでPass。
- Mac Metal Summary ON: model_smokeでPass。
- Stop／New Chat／Reload: 既存Browser／Integration Testが継続合格。

Browser DevToolsを用いた実Model SSE本文の再検査は行っていない。代わりに、Raw SSE Bodyの完全一致を可能にするASGI Integration TestとMac Metal実Model Pipeline Testを分離して実行した。

## 9. Optional Improvement

Summary StageのBroad `except Exception`へのOperator Log追加は実施していない。4 Mandatory Findingの修正Scopeを優先し、Client安全性／fallback動作は変更していない。

## 10. 非実施／境界

- Lightning Upload／Model Transfer／Cloud実行: 未実施
- Phase 1完了宣言／Backup: 未実施
- Phase 1-ex: 未着手
- Git初期化／Commit／Push／GitHub公開: 未実施
- Config Schema／Summary Prompt／Token値変更: 未実施
- Model Adapter／CLI／Dependency変更: 未実施
- Public Docs更新: 未実施

Phase 1-H Follow-upの受入判断は設計者再Reviewへ戻す。
