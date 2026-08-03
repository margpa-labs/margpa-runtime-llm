# Phase 1-H Summary Mode／UI Language 設計Review

- 文書ID: `designer_review_phase_1h_summary_mode_and_ui_language`
- 状態: `changes_requested`
- 作成日時: `2026-07-21 18:20:38 JST`
- 更新日時: `2026-07-21 18:20:38 JST`
- Snapshot: `20260721182038`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-H Summary Mode／UI Language実装
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md](implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- Latest Index: [documentation_index_20260721182038.md](../documentation_index_20260721182038.md)
- supersedes: なし（Phase 1-H Review系列の初回）

## 1. Review結論

Phase 1-Hの中核実装は成立している。Static、Type、Unit、Web Integration、Mac Metal実Modelは合格した。

ただし、正本Architecture／公開Preview境界に対してMandatory Findingが4件あるため、Phase 1-HをAcceptedにはしない。

```text
Summary Call Count／Sequentiality : Pass
Summary Prompt Boundary           : Pass
Summary Thinking／Token Policy    : Pass
Fallback Matrix                   : Pass
Cancel／Shutdown Thread Boundary  : Pass
Application Schema 3              : Pass
UI／Response Language Separation  : Mostly Pass
Successful Summary SSE Privacy    : Fail
Long Silent SSE Reliability       : Fail／Pre-Lightning Blocker
Summary Risk Notice               : Incomplete
Runtime Error Relocalization      : Incomplete
Final Decision                    : Changes Requested
```

「テストが落ちている実装」ではない。既存Testが受入Contractとの差を捕捉していない状態である。

## 2. Mandatory Finding 1：Summary成功時にもOriginal全文をClientへ送信している

- Priority: High
- Acceptance Impact: Blocker
- 対象: `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:348-395`
- Test Gap: `tests/integration/web/test_web_app.py:340-373`

Summary成功時の`completed` Eventへ次を含めている。

```json
{
  "assistant_message": {"content": "Short summary"},
  "original_assistant_message": {"content": "Original answer"},
  "summary_assistant_message": {"content": "Short summary"}
}
```

このため、UIにOriginalが描画されなくても、SSE Response BodyにはOriginal全文が出力される。

独立再現結果：

```json
{
  "event": "completed",
  "data": {
    "assistant_message": {"content": "Short summary"},
    "presented_source": "summary",
    "original_assistant_message": {"content": "Original answer"},
    "summary_assistant_message": {"content": "Short summary"}
  }
}
```

正本では、Summary成功時にBrowser Historyへ採用するのはSummaryであり、OriginalはPipeline内の独立Artifact／将来Audit Hookとして扱う。ArchitectureのCompleted例も、回答本文ではなく非機密Transformation Metadataだけを返す。

Current Integration Test名は`hides_original_then_presents_only_valid_summary`だが、`Original answer`がResponseへ存在しないことをAssertしていない。このため実装とTestが同じContract Driftを固定している。

Required Correction：

1. Summary成功時のPublic SSEから`original_assistant_message`と重複する`summary_assistant_message`を除く。
2. OriginalはServer-side Session Artifactとして保持し、Phase 1-HではClientへ送らない。
3. `assistant_message`はPresented Answerだけとする。
4. Completedへ必要なら次の非本文Metadataだけを返す。

```json
{
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

5. Fallback時はOriginalがPresented Answerであるため、`assistant_message`として返してよい。
6. Success Integration Testへ、Original Canonical FinalがSSE Response全体に存在しないAssertを追加する。

## 3. Mandatory Finding 2：Hidden／Buffered 2段生成中のSSE Keepaliveがない

- Priority: High
- Acceptance Impact: Pre-Lightning Blocker
- 対象: `src/margpa_runtime_llm/web/streaming.py:68-85`
- 関連: `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:164-214`

Summary Mode ONでは、Normal Generation DeltaをClientへ送らず、Summaryも成功確定までBufferする。

```text
start
  → Normal 0..2048 tokens／Client outputなし
status
  → Summary 0..1024 tokens／Client outputなし
delta＋completed
```

Current SSE BridgeはQueueが空の場合、0.1秒ごとにDisconnectだけを確認し、ClientへComment／Heartbeatを送らない。

この構造では、低速Mac、Lightning CPU Profile、混雑時、長い2048／1024 Generationにより、Reverse ProxyのIdle Timeoutで接続が切れる可能性がある。Phase 1-HはOriginal／Summaryを意図的に非Streaming化したため、Phase 1-GよりIdle区間が大幅に長くなっている。

Required Correction：

1. SSE Bridgeへ意味を持たないPeriodic Keepalive Commentを追加する。
2. 例：15秒程度のBounded Intervalで`: keepalive\n\n`を送る。
3. KeepaliveをConversation Event／History／Audit Resultとして扱わない。
4. Consumer Stop／Disconnect後にHeartbeat Taskが残らないようLifecycleを同じ`finally`で閉じる。
5. Blocking Fake Streamを使い、Application Eventが長時間ない間にもKeepaliveが出るTestを追加する。
6. KeepaliveがTerminal Count、Queue Capacity、Cancel Thread Boundaryを壊さないことを確認する。

Intervalの最終値はFollow-up Handoffで固定する。LightningへUploadする前に解消する。

## 4. Mandatory Finding 3：要約による情報欠落可能性のUI注記がない

- Priority: Medium
- Acceptance Impact: Blocker／Small Fix
- 対象: `src/margpa_runtime_llm/web/static/app.js:35,91`
- 対象: `src/margpa_runtime_llm/web/static/index.html`のSummary Note
- 正本: Handoff Section 8.1

Current Noteは追加LatencyとToken使用量だけを説明している。

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増えます。
```

正本Handoffは、追加生成、遅延に加えて、要約による情報欠落の可能性を短く明示するよう要求している。

Required Correction：

- 日本語Noteへ「要約により詳細、前提、注意事項等が省略・変形される可能性があります」相当を追加する。
- English Noteへ同義の注意を追加する。
- Translation DictionaryとInitial HTMLを一致させる。
- Static Testで欠落RiskのKey／Textを確認する。

## 5. Mandatory Finding 4：Runtime取得失敗後のUI Language再切替がError表示へ反映されない

- Priority: Medium
- Acceptance Impact: Blocker／Small Fix
- 対象: `src/margpa_runtime_llm/web/static/app.js:207-249,316-342`

`loadRuntime()`失敗時、現在言語でRender済みのError Textを`state.runtimeText`へ保存する。その後`applyTranslations()`は`runtimeText === null`の場合しかRuntime Statusを再描画しない。

再現する論理経路：

```text
UI ja
  → Runtime API Failure
  → 「Runtime情報を取得できませんでした。」をstate.runtimeTextへ保存
  → UIをEnglishへ変更
  → state.runtimeTextはnon-null
  → Error表示は日本語のまま
```

Known Error／StatusをUI Language切替対象とする正本要件に適合しない。

Required Correction：

1. Runtime StatusもRender済み文字列ではなく、`kind／translation_key／values`等のStable Stateで保持する。
2. Runtime Metadata成功時だけOpaque Textとして保持する。
3. Runtime Loading／Known Failureは`applyTranslations()`で再描画する。
4. Runtime Failure後の`ja → en → ja`を動作Testする。

## 6. Non-blocking Observation

### 6.1 Summary StageのBroad Exception Fallback

`_events_with_summary()`はSummary Stage全体の`Exception`を無記録でOriginal Fallbackへ変換する。

End UserへRaw Exceptionを出さない点は正しい。一方、実装Bugまで静かにFallbackするとOperatorが異常を識別できない。Phase 1-H Follow-upでは、少なくとも固定された安全なOperator Logまたは内部Reason Codeを残し、Raw Exception／Prompt／PathをClientへ出さない構成を検討する。

Current Fallback結果自体は安全であるため、本Observation単独ではBlockerとしない。

### 6.2 Legacy `force_cancel()`

Public Session SurfaceにThread-affine Streamへ別Threadから到達し得る`force_cancel()`定義が残る。Current Runtime Callerは0件であり、実経路はCooperative Cancelだけなので、Phase 1-Gから継続する非ブロッカーとする。

## 7. Accepted Areas

次は正本どおり成立している。

- `off／post_generation`の厳格なTyped Contract
- Application Config Schema `3`
- Deployment Profile Schema非変更
- Default OFF
- OFF時Main Model Call 1回
- ON時Normal／Summary Call各1回
- Same Model Key／Sequential Stream
- Normal Stream Close後のSummary Stream Open
- Summary max 1024／Thinking disabled
- Canonical FinalだけをJSON Data Boundaryで要約
- User Prompt／History／Thinking／System Prompt非混入
- `ja／en／auto` Summary Language Policy
- Summary OutputのThinking Parser適用
- Error／Context／Empty／Parser／Length／No Terminal Fallback
- Summary Delta Buffering
- Cancel時No Fallback／No History
- Normal／Summary両段階のProducer-thread Cancel／Close
- Gate Release／後続Generation
- UI LanguageとResponse LanguageのState分離
- UI LanguageだけをNamespaced Local Storageへ保存
- Plain Text DOM更新／No External i18n Dependency
- New Chat／Reload後のUI Language維持
- New Dependencyなし／CLI Contract非変更

## 8. Independent Verification

### 8.1 Static／Type／Unit／Integration

```text
ruff format --check src scripts tests     : Pass／93 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／93 source files
python -m compileall -q src scripts tests : Pass
node --check app.js                       : Pass
pytest -q                                 : Pass／242 passed、3 deselected
Conversation／Summary／Web Targeted       : Pass／47 passed
uv lock --check --offline                 : Pass／122 packages
bash -n Setup Scripts                     : Pass
```

`uv lock`はSandbox内でUser Cache Permissionにより失敗したため、既存CacheへAccess可能なReview実行で再確認し合格した。Source Failureではない。

### 8.2 Mac Metal実Model

```text
Sandbox Run : 2 failed、1 skipped／llama_context creation failure
Direct Run  : 2 passed、1 skipped、242 deselected
Skip        : Phase 1-F Profile未指定
```

Direct Mac Metalで合格したため、Sandbox FailureはPhase 1-H Source Findingとしない。

## 9. Follow-up Acceptance Conditions

Phase 1-H Acceptedには次をすべて満たす必要がある。

1. Summary成功時のSSEからOriginal全文を除く。
2. Transformation Metadataを非本文・非機密にする。
3. Success SSEでOriginal不在をTestする。
4. Hidden Normal／Buffered Summary中のSSE Keepaliveを追加する。
5. Keepalive Lifecycle／Disconnect／Cancel Regressionを追加する。
6. Summary Noteへ情報欠落／変形可能性を日英で追加する。
7. Runtime Known ErrorをUI Language切替後に再描画する。
8. Static／Default／Targeted／Model Smokeを再実行する。
9. Lightning Full UploadはFollow-up Accepted後まで行わない。

## 10. Next Gate

```text
Phase 1-H Changes Requested
  → Designer Follow-up Handoff
  → User authorizes Follow-up
  → Implementer Correction／Status
  → Designer Re-review＋New Index
  → User Mac Acceptance
  → Batch Lightning Upload／Validation
```

本ReviewはSource修正、Lightning操作、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を許可しない。

## 11. Append-Only

実装報告、Requirements、Architecture、ADRを変更せず、新TimestampのReviewとして追加した。
