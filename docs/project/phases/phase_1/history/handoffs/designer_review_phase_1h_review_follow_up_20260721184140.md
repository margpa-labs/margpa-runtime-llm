# Phase 1-H Review Follow-up 設計Review

- 文書ID: `designer_review_phase_1h_review_follow_up`
- 状態: `accepted_with_non_blocking_observations`
- 作成日時: `2026-07-21 18:41:40 JST`
- 更新日時: `2026-07-21 18:41:40 JST`
- Snapshot: `20260721184140`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-H Review Follow-upおよびPhase 1-H最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1h_review_follow_up_20260721183457.md](implementer_status_phase_1h_review_follow_up_20260721183457.md)
- Follow-up Handoff: [implementer_handoff_phase_1h_review_follow_up_20260721182416.md](implementer_handoff_phase_1h_review_follow_up_20260721182416.md)
- 前回Review: [designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md](designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Latest Index: [documentation_index_20260721184140.md](../documentation_index_20260721184140.md)
- supersedes: `designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md`

## 1. Review結論

前回の4 Mandatory Findingはすべて解消した。追加RegressionとMac Metal実Modelを含む独立検証も合格したため、Phase 1-H Summary Mode／UI LanguageをAcceptedとする。

```text
Finding 1 Successful Summary SSE Privacy : Resolved
Finding 2 Long Silent SSE Keepalive       : Resolved
Finding 3 Summary Risk Notice             : Resolved
Finding 4 Runtime Error Relocalization     : Resolved
Default Regression                        : 246 passed、3 deselected
Targeted Regression                       : 51 passed
Mac Metal Model Smoke                     : 2 passed、1 skipped
Final Decision                            : Phase 1-H Accepted
```

Phase 1-HがAcceptedになったことは、Phase 1全体完了、User Acceptance、Lightning Validation、Backup、Phase 1-ex開始を意味しない。

## 2. Finding 1 Resolution：Successful Summary SSE Data Minimization

Summary成功時のPublic Eventから次が除去された。

```text
original_assistant_message
summary_assistant_message
presented_source
original_usage
summary_usage
```

Current Success Completed：

```json
{
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

独立再現では、Normal Originalを`Original answer`、Summaryを`Short summary`としてEvent列を生成し、次を確認した。

```text
ORIGINAL_PRESENT = False
Presented Delta  = Short summary
Assistant Message = Short summary
Transformation   = Non-content Metadata only
```

Fallback時はOriginalがPresented Answerであるため`assistant_message`として返るが、別Fieldへ重複しない。不完全Summaryは送信されない。

追加Testは、Raw SSE全体からOriginal、Original Thinking、Summary Thinking、削除済みKeyが不在であることを直接Assertする。前回のTest Gapは解消した。

## 3. Finding 2 Resolution：SSE Keepalive

次の固定Contractが追加された。

```text
Interval    : 15.0 seconds
Wire Format : : keepalive\n\n
SSE Type    : Comment
Semantic Event／History／Audit : No
```

実装はAsync SSE Consumer側だけでIdle時間を計測する。

- Application Event送信でTimerをResetする。
- Normal Hidden Generation中に動作する。
- Summary Buffered Generation中に動作する。
- Conversation Event Queueへ積まない。
- Terminal後に送らない。
- Consumer Close／Disconnectで既存Cooperative Cancelへ合流する。
- 専用Task／Threadを作らない。
- Request ID、Prompt、ExceptionをCommentへ含めない。

短縮Intervalを用いたRegressionで、Keepalive後の通常Event／Completed、Producer-thread Native Cancel／Close、後続Generation、Task Cleanupが合格した。

KeepaliveはPhase 1-Hで新たに生じた長時間Silent Intervalを緩和する。実Lightning Reverse Proxy上の確認は、予定されているBatch Lightning Gateで行う。

## 4. Finding 3 Resolution：Summary Risk Notice

日本語とEnglishの両方へ、Latency／Token Costだけでなく、要約による情報欠落・変形可能性が追加された。

```text
日本語:
要約により詳細、前提、注意事項等が省略・変形される可能性があります。

English:
details, assumptions, or cautions may be omitted or altered by the summary.
```

Initial HTMLとTranslation Dictionaryは同義内容であり、品質保証を追加していない。Static Testも追加されている。

## 5. Finding 4 Resolution：Runtime Status Relocalization

Render済みError文字列を保持する`runtimeText`は削除され、次のStable Stateへ変更された。

```text
loading
metadata
known_error
```

`renderRuntimeStatus()`を`applyTranslations()`から毎回呼ぶため、Loading／Known Errorは現在のUI Languageで再解決される。Metadata成功時のModel／Profile／Device IdentifierだけはOpaque Textとして維持する。

実装報告のManual Browser Evidence：

```text
ja : Runtime情報を取得できませんでした。
en : Could not load runtime information.
ja : Runtime情報を取得できませんでした。
```

UI Language変更はResponse Language値を変更しない。

## 6. Phase 1-H Core Acceptance

Follow-up前に合格していた次の領域もRegressionを通過した。

- Summary Mode `off／post_generation`
- Default OFF
- OFF時Main Model Call 1回
- ON時Normal／Summary各1回
- Same Main Model Sequential Reuse
- Normal Stream Close後のSummary Stream Open
- Summary max 1024／Thinking disabled
- Canonical FinalだけのJSON Summary Source
- User Prompt／History／Thinking／System Prompt非混入
- Response Language `ja／en／auto`
- Summary Parser／Hidden Reasoning
- Error／Context／Empty／Parser／Length／No Terminal Fallback
- Cancel時No Fallback／No Assistant History
- Producer-thread Native Cancel／Close
- Disconnect／Backpressure／Shutdown
- Gate Release／後続Generation
- Application Config Schema 3
- Deployment Profile非変更
- UI Language／Response Language分離
- UI LanguageだけのNamespaced Local Storage
- Plain Text Rendering／No External Dependency
- CLI Contract非変更

## 7. Independent Verification

### 7.1 Static／Type／Unit／Integration

```text
ruff format --check src scripts tests     : Pass／93 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／93 source files
python -m compileall -q src scripts tests : Pass
node --check app.js                       : Pass
pytest -q                                 : Pass／246 passed、3 deselected
Conversation／Summary／Web Targeted       : Pass／51 passed
uv lock --check --offline                 : Pass／122 packages
bash -n Setup Scripts                     : Pass
```

### 7.2 Mac Metal実Model

```text
pytest -q -m model_smoke : 2 passed、1 skipped、246 deselected
Skip                     : Phase 1-F Profile未指定
```

Reviewでは最初からMac Metalへ直接Access可能な実行で確認し、`llama_context` Environment Failureは発生しなかった。

## 8. Non-blocking Observations

### 8.1 Summary Stage Broad Exception

Summary StageのBroad `except Exception`は、UserへRaw Errorを出さずOriginalへFallbackする。Operator Logはまだ追加されていない。

Current User Safety／Fallbackは成立しているためBlockerとしない。Audit／Observability導入時に、本文・Prompt・Pathを出さないSafe Internal Reason／Operator Logへ接続する。

### 8.2 Legacy `force_cancel()`

Public Session SurfaceにLegacy `force_cancel()`定義が残るが、Runtime Callerは0件であり、Current LifecycleはCooperative Cancelだけを使用する。Phase 1-Gから継続する非ブロッカーとする。

### 8.3 Lightning Native／Proxy

15秒KeepaliveのDeterministic Testは合格したが、Lightning上の実Reverse Proxy／CUDA／CPU実行は未実施である。これはPhase 1-H Source Findingではなく、予定どおりBatch Lightning Gateで確認する。

## 9. Acceptance Status

| Area | Result |
|---|---|
| Summary Core | Accepted |
| Summary Failure／Fallback | Accepted |
| Summary SSE Data Minimization | Accepted |
| SSE Keepalive | Accepted for Mac／Pending Lightning Native Gate |
| UI Language／Response Language Separation | Accepted |
| Runtime Error Relocalization | Accepted |
| Cancel／Disconnect／Shutdown | Accepted |
| Config Schema／Adapter Boundary | Accepted |
| Phase 1-H Overall | Accepted |

## 10. Next Gate

```text
Phase 1-H Accepted
  → User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion／Next Phase Ready Declaration
  → User Final Acceptance
  → Backup
  → Phase 1-ex
```

本ReviewはLightning Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

前回Review、Follow-up Handoff、実装報告を変更せず、新TimestampのAccepted Reviewとして追加した。
