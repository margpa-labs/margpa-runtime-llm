# Phase 1-H Summary Mode／UI Language Architecture

- 文書ID: `phase_1h_summary_mode_and_ui_language_architecture`
- 状態: `accepted_design_complete_waiting_implementation_authorization`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- supersedes: なし（Phase 1-H Architecture系列の初回）

## 1. Architectural Goal

Phase 1-GのConversation Applicationへ、追加Inferenceを伴うSummarization Layerを挿入する。同時に、Browser UIだけのLocalization Layerを追加し、Model Response Languageから分離する。

```text
Browser UI
  ├─ UI Language Adapter（ja／en、Browser-only）
  └─ Conversation Request
       ↓
FastAPI Delivery Adapter
       ↓
Conversation Generation Orchestrator
  ├─ Normal Generation
  ├─ Canonical Final Extraction
  ├─ Optional Summarization Port
  └─ Presented Answer Resolution
       ↓
Existing Inference Service／Model Port
       ↓
Current Main Model Adapter
```

SummarizationはPresentation文字列の短縮処理ではない。Model Inferenceを追加する独立Response Transformationとする。

## 2. Dependency Direction

```text
web/static UI Language Dictionary
        └─ Browser DOMだけへ依存

web／FastAPI
        ↓
conversation application
        ↓
summarization contracts／application
        ↓
inference + presentation public contracts
        ↓
model adapter
```

禁止：

- Summarization CoreからFastAPI／DOMへ依存する。
- Browser JavaScriptがMain Modelを直接2回呼ぶ。
- `llama_cpp`やQwen固有処理をSummary Applicationへ入れる。
- UI Language値をResponse Languageとして流用する。
- Summary PromptをBrowserへ組み立てさせる。
- Original AnswerをModel Generated Thinkingと混同する。

## 3. Domain／Application Contracts

候補Contract：

```text
SummaryMode
  OFF
  POST_GENERATION

SummarizationConfig
  mode
  backend
  max_new_tokens
  thinking_mode
  preserve_original
  failure_policy

SummaryArtifact
  original_final_answer
  summary_final_answer?
  presented_answer
  summary_applied
  fallback_used
  original_finish_reason
  summary_finish_reason?
  warning_codes[]
```

`ConversationSettings`へ`summary_mode`を追加する。UIのCheckboxはBooleanのままCoreへ渡さず、`off／post_generation`へ変換する。

Summary用Portは、少なくとも次の抽象責務を持つ。

```text
build_summary_request(original, response_policy, generation_defaults)
evaluate_summary_result(result)
resolve_presented_answer(original, summary_result)
```

初期Adapterは既存Inference ServiceとCurrent Main Model Keyを再利用する。将来Dedicated Modelを接続しても、Conversation／Web Contractを全面変更しない。

## 4. Session State Machine

```text
CREATED
  → GENERATING_ORIGINAL
      ├─ cancelled → CANCELLED
      ├─ error     → ERROR
      └─ complete  → ORIGINAL_READY
  → SUMMARY_DISABLED
      └─ COMPLETED_ORIGINAL
  → SUMMARIZING
      ├─ cancelled       → CANCELLED
      ├─ failure         → COMPLETED_FALLBACK_ORIGINAL
      ├─ invalid/length  → COMPLETED_FALLBACK_ORIGINAL
      └─ complete        → COMPLETED_SUMMARY
```

Terminalは`COMPLETED_*／CANCELLED／ERROR`のいずれか1回である。Summary内部FailureはTurn全体の`error`にせず、Originalが有効な場合はDegraded Completedへ解決する。

## 5. Sequential Model Ownership

NormalとSummaryは1つの`ConversationGenerationSession`が所有する。

```text
Generation Gate Acquire
  → Normal Stream Open／Consume／Close
  → Summary Stream Open／Consume／Close
  → Generation Gate Release
```

- Summary StreamはNormal StreamのContext Manager終了後に作成する。
- 2つのNative Streamを同時に開かない。
- Model Load Instanceを増やさない。
- Summary開始時も同じProcess-wide Generation Gateを保持する。
- Active Request IDはTurn単位のParent IDとして維持する。
- Normal／Summaryには将来監査用のChild Request IDを持たせてよい。
- Gate、Active Session、Close Callbackの正確性をPhase 1-Gから維持する。

Current `ConversationGenerationService.start()`はStreamを事前作成しているため、Phase 1-HではSessionがNormal Requestを受け取り、Producer Thread上でStreamを段階的に作成できる構造へ局所再編する必要がある。Web Entrypointで2回呼ぶ実装は禁止する。

## 6. Normal Generation Capture

Summary Mode ON時は、Normal GenerationのPresentation Sessionを通して次を得る。

```text
raw stream
  → Thinking Parser
      ├─ display delta : Browserへ出さない
      ├─ reasoning     : 要約対象外／非永続
      └─ final_content : Original Canonical Final
```

Normal生成中はUIへStatusだけを返す。Thinking Visibilityがvisibleでも、要約モードON時のNormal Thinkingを画面へ出さない。これは通常回答をそのまま表示しないという要約モードのPresentation Contractを優先するためである。

Summary Mode OFF時は既存のPresentation Streamingを一切変えない。

## 7. Summary Request Construction

Summary RequestはServer側で構成する。

```text
System:
  Summary Transformation Policy
  Response Language Policy
  Sourceを命令ではなくDataとして扱う指示

User:
  明確なSource Boundary内のOriginal Canonical Final Answer
```

Source Boundaryは固定DelimiterまたはJSON Serialization等、入力本文とInstructionが区別できる形式を採用する。Source本文をString連結で曖昧に埋め込まない。

要約時Generation Parameters：

```text
base             = effective generation defaults
max_new_tokens   = summarization.max_new_tokens（1024）
thinking_mode    = disabled
other parameters = baseを継承
```

Response Language：

```text
ja   → 日本語要約を明示
en   → 英語要約を明示
auto → Originalの主要言語を維持
```

## 8. Summary Validation／Fallback

SummaryのRaw Outputにも既存Thinking Parser／Canonical Final抽出を適用する。Thinkingはdisabledでも、Protocol逸脱でTagが出た場合にRaw ReasoningをClientへ漏らさない。

Fallback条件：

```text
InferenceError
Context Limit
Empty Final
Parser Failure
FinishReason.LENGTH
Unknown／Missing Terminal
```

Fallback時のContract：

```text
warning(code="summary_*_fallback")
completed(
  assistant_message = original,
  summary_applied = false,
  fallback_used = true
)
```

Summary中CancelはFallbackしない。Cancel後にOriginalが画面へ突然確定すると、ユーザーの停止意思に反するためである。

## 9. SSE Contract Extension

`ConversationEventType`へ`STATUS`を追加する。

候補Payload：

```json
{
  "request_id": "turn-id",
  "state": "generating_answer"
}
```

```json
{
  "request_id": "turn-id",
  "state": "summarizing_answer"
}
```

Completedには非機密Metadataを追加できる。

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {"role": "assistant", "content": "..."},
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

Usageは段階別保持が望ましい。既存`usage`を壊さないため、Phase 1-HではPresented StageのUsageを既存Fieldへ置き、将来監査用に`stage_usage.original／summary`を追加可能とする。Browserは未知Fieldを無視できる。

FallbackではSummary Deltaを先に表示しない。Summary成功確定前にDeltaをStreamingすると、途中失敗時に不完全要約とOriginalが混在するため、Phase 1-Hの安全優先案ではSummary結果もServer側でCanonical Final確定後に表示する。実装量を抑えてStreamingする場合でも、失敗時にDOMを明示的にResetしてOriginalだけを表示できるTest済みContractが必須である。推奨実装はSummaryをBufferし、成功後にDeltaとしてまとめて送る方式である。

## 10. Cancellation／Disconnect／Shutdown

Sessionは現在のStageを認識し、Producer Thread上でCancelを処理する。

```text
request_cancel()
  → shared cancel flag
  → current stream iteration boundary
  → producer thread calls cancel／close
  → cancelled terminal
```

- NormalとSummaryで同じCancel Flagを共有する。
- Stage切替直前にもCancel Flagを確認し、Cancel後にSummary Streamを開始しない。
- SSE Disconnect、Stop API、Runtime Shutdownの全経路を同じCooperative Contractへ合流させる。
- 別ThreadからNative Streamへ`force_cancel()`しない。
- Shutdown Timeout時はFalse／Safe Failureを維持し、Model Closeを先行しない。
- Cancel後にGeneration Gateを解放し、次Requestを受理できる。

## 11. Configuration Architecture

`config/application.toml`のApplication Schemaを`3`へ更新する。

候補Pydantic Contract：

```text
ApplicationConfig(schema_version="3")
  ├─ existing fields
  └─ layers
      └─ summarization

EffectivePhase1Config
  └─ summarization policy
```

`extra="forbid"`を維持し、Typoを黙って無視しない。

Deployment ProfileはHost／Compute／Backend Runtimeを扱うため、Summary Layer設定を入れない。Platform別Configへ同じ値を複製しない。

Phase 1-Hで旧Schema `2`の外部Config互換を保証するかは、Tracked Configが単一であるため必須ではない。実装はTracked ConfigとTest FixtureをSchema `3`へ一括Migrationする。もし旧Schema読込を残す場合も、暗黙の挙動差を生まない明示Migrationとする。

## 12. UI Localization Architecture

Vanilla JavaScript内に小規模なTranslation Dictionaryを置く。

```javascript
const translations = {
  ja: { /* stable keys */ },
  en: { /* stable keys */ },
};
```

Static HTMLは`data-i18n`、`data-i18n-placeholder`、`data-i18n-aria-label`等のStable KeyでTextを識別する。Dynamic Textは同じKey Resolverを使い、文字列を各Event Handlerへ重複させない。

```text
setUiLanguage(language)
  → validate ja／en
  → document.documentElement.lang
  → document.title
  → static text／attribute update
  → current status keyを再描画
  → localStorage best-effort save
```

Status Stateは表示済み文字列ではなくStable Keyとして保持する。言語切替時に、実行中Statusも即座に再描画できるようにする。

Response Language Optionは表示Labelだけを翻訳し、Valueは`ja／en／auto`を維持する。

外部i18n Package、CDN、翻訳APIは追加しない。Phase 4でReact等へ移行する際、Dictionary Keyを再利用できる。

## 13. Browser State Boundary

```text
Memory only
  messages[]
  active request state
  response language
  max tokens
  thinking visibility
  summary mode

localStorage
  ui_language only
```

New Chatは`messages[]`とActive UIだけを初期化し、UI Languageを保持する。ChatやCredentialをLocal Storageへ入れないPhase 1-GのPrivacy Boundaryを維持する。

## 14. Proposed Source Scope

実装担当は責務に応じて次を追加・変更できる。

```text
config/application.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/modules/summarization/      # 候補
src/margpa_runtime_llm/orchestration/              # Summary Prompt Composer候補
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
tests/unit/conversation/
tests/unit/summarization/                           # 候補
tests/unit/inference/test_config_and_registry.py
tests/integration/web/test_web_app.py
```

File分割は既存Module Styleに合わせて調整可能だが、巨大なConversation Serviceまたは`app.js`へSummary Policy、Prompt、Validation、Localizationを無秩序に集約しない。

## 15. Test Architecture

Fake Inference Streamで次を観測可能にする。

- Call回数
- Call順序
- Stream同時Open数
- Request Message列
- max_new_tokens／thinking_mode
- Finish Reason／Usage
- Cancel／Close Thread
- Gate Release

主要Test Matrix：

```text
OFF success
ON success
ON summary error
ON summary empty
ON summary context limit
ON summary length
Cancel during original
Cancel between stages
Cancel during summary
Disconnect during both stages
Shutdown timeout／recovery
Busy during both stages
ja／en／auto summary language policy
UI ja／en × response ja／en／auto
localStorage valid／invalid／unavailable
Known／unknown warning localization
```

Native Model Smokeでは最低限、OFF 1件、ON 1件を実Modelで確認する。ただしMacでの受入後までLightning Full Uploadは行わない。

## 16. Architectural Consequences

利点：

- Model Adapterを変えずにResponse Transformationを追加できる。
- Dedicated Summary Modelへの将来交換点ができる。
- UI LanguageとResponse Languageの意味混同を防げる。
- ON／OFF比較により要約の品質／Latency／Token Costを研究できる。
- OriginalとSummaryの将来監査が可能になる。

Trade-off：

- ON時はGeneration回数、Latency、Energy Costがほぼ増える。
- Current Context 4096では長いOriginalの要約がFallbackしやすい。
- 同一Modelの自己要約は誤要約、欠落、歪みを起こし得る。
- Originalを即時Streamingしないため、First Visible Answerまで待ち時間が増える。
- 小規模Vanilla i18nは将来の多言語化で専用Frameworkへ移行する可能性がある。

## 17. Authorization Boundary

本Architectureは実装方式を確定するが、Source／Config変更を自動許可しない。ユーザーのPhase 1-H実装開始指示後、対応Handoffを実装開始境界とする。

## 18. Append-Only

既存Phase 1-G ArchitectureおよびSummary予約要件を変更せず、Phase 1-H Architectureを新規追加した。
