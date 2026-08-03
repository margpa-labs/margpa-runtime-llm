# 実装担当向け Phase 1-H Summary Mode／UI Language Handoff

- 文書ID: `implementer_handoff_phase_1h_summary_mode_and_ui_language`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Roadmap: [implementation_roadmap_20260721174346.md](../architecture/implementation_roadmap_20260721174346.md)
- Latest Phase 1-G Review: [designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md](designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md)
- supersedes: なし（Phase 1-H実装開始用Handoffの初回）

## 1. Current State

Phase 1-GはAcceptedである。Minimal Web Surface、SSE、Browser-owned History、Stop／Disconnect／ShutdownのCooperative Cancel、Preview Basic Authが成立している。

Phase 1-Hの設計は完了したが、実装は未許可である。

```text
Phase 1-G : Accepted
Phase 1-H : Design Complete／Waiting User Authorization
Lightning Full Upload : Deferred until Phase 1-H Mac Acceptance
```

## 2. Start Condition

ユーザーが実装担当TaskへPhase 1-H開始を明示した時点で、本Handoffの限定範囲を実装できる。それ以前はSource／Config／Testを変更しない。

## 3. Authorized Scope after User Approval

```text
config/application.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/modules/summarization/       # 必要な場合
src/margpa_runtime_llm/orchestration/
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
tests/unit/conversation/
tests/unit/summarization/                            # 必要な場合
tests/unit/inference/test_config_and_registry.py
tests/integration/web/test_web_app.py
必要な既存Test Fixture
docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_*
```

`pyproject.toml／uv.lock`は新Dependency不要のため原則変更しない。不可避なDependency追加が必要なら、変更前に設計者役へ理由を戻す。

## 4. Work Package 1: Configuration／Contracts

1. Application Config Schemaを`2`から`3`へ更新する。
2. `[layers.summarization]`をTyped Configとして追加する。
3. `mode=off|post_generation`、`backend=main_model`、`max_new_tokens=1024`、`thinking_mode=disabled`、`preserve_original=true`、`failure_policy=fallback_original`を厳格Validationする。
4. Deployment Profile Schemaは変更しない。
5. `ConversationSettings`へ`summary_mode`を追加する。
6. `/api/v1/runtime`へDefault Summary Modeを追加する。
7. CLI Contractを変更しない。
8. Typo／未知値を黙って受理しない。

## 5. Work Package 2: Summarization Layer

1. SummarizationをConversation／Webから分離したTyped Application責務として実装する。
2. BrowserやFastAPI HandlerからInferenceを直接2回呼ばない。
3. NormalとSummaryを同じConversation Sessionが逐次所有する。
4. Normal StreamをCloseしてからSummary StreamをOpenする。
5. Model Loadは1回、同時Native Streamは最大1とする。
6. Summary RequestへOriginal Canonical Final Answerだけを渡す。
7. Normal Thinking、History、System Prompt、Runtime内部情報を渡さない。
8. Sourceを命令ではなくDataとして扱うSummary InstructionをServer側で構成する。
9. Response Language `ja／en／auto`を要約へ反映する。
10. Summary max 1024、Thinking disabledを強制する。
11. その他のGeneration ParametersはEffective Defaultを継承する。
12. Summary Raw OutputにもThinking Parserを適用し、ReasoningをClientへ漏らさない。

## 6. Work Package 3: Result／Fallback

Original、Summary、Presented Answerを別変数／Contractとして扱う。

次はWarning付きOriginal Fallback：

- Summary Inference Error
- Context Limit
- Empty／Whitespace Final
- Parser Failure
- Finish Reason Length
- Terminal不整合

Fallback時はOriginalを`completed.assistant_message`へ入れ、Browser HistoryもOriginalとする。

Summary中CancelはFallbackしない。`cancelled`で終了し、HistoryへAssistant Messageを追加しない。

OriginalのToken Limit WarningをSummary成功／Fallbackの両方で維持する。

## 7. Work Package 4: SSE／Cancellation

1. `status` Eventを追加し、`generating_answer／summarizing_answer`を送る。
2. Terminalは`completed／cancelled／error`の1回だけとする。
3. OFF時は既存Phase 1-G Event順序と表示を維持する。
4. ON時はNormal Delta／ThinkingをBrowserへ送らない。
5. Summaryは成功確定前に不完全Textを混在させない。推奨はBuffer後に表示する。
6. Normal／SummaryでCancel Flagを共有する。
7. Stage間でCancelを再確認し、Cancel後にSummaryを開始しない。
8. Stop API、Disconnect、Backpressure Cleanup、Shutdownを既存Cooperative Cancelへ合流させる。
9. 別ThreadからNative `cancel／close`を呼ばない。
10. Gate Release、Active Request、Model Close CallbackをPhase 1-Gから後退させない。

## 8. Work Package 5: Minimal UI

### 8.1 Summary Mode

- Settingsへ横スライド型`要約モード OFF／ON`を追加する。
- DefaultはRuntime Config由来のOFFとする。
- Requestでは`off／post_generation`へMappingする。
- ON時に追加生成、遅延、情報欠落の可能性がある旨を短く注記する。
- StatusをNormal生成／Summary生成で区別する。

### 8.2 UI Language

- Topbar右上へ`日本語 | English` Switchを追加する。
- New Chat Buttonと衝突しないResponsive Layoutにする。
- UI LanguageはResponse Language Pull-downと別Stateとする。
- Repository内のTranslation DictionaryとStable Keyを使用する。
- Title、`html lang`、Button、Label、Placeholder、Status、Known Warning／Error、ARIAを切り替える。
- Response Language OptionはLabelだけ翻訳し、Valueを維持する。
- Model Output／Thinkingを翻訳しない。
- `margpa.ui_language.v1`等へUI LanguageだけをBest-effort保存する。
- Invalid Value／Storage不可は日本語へ安全にFallbackする。
- New ChatでUI Languageを消さない。
- Chat、Prompt、Credential、OutputをLocal Storageへ保存しない。

## 9. Required Automated Tests

### 9.1 Config／Contract

- Schema 3のValid／Invalid Matrix
- Unknown Summary Mode／Backend／Policy Reject
- Deployment Profileへの混入Rejectまたは非採用
- UI Request `summary_mode` Validation
- Runtime Default Response

### 9.2 Summary Pipeline

- OFFはInference Call 1回
- ONはInference Call 2回、順序Normal→Summary
- Native Stream同時Open数1
- Summary Request Content Boundary
- Thinking disabled／max 1024
- ja／en／auto Policy
- Original／Summary／Presented分離
- Error／Empty／Context／Length Fallback
- Original Token Warning維持
- Summary Success Canonical History
- Fallback Original Canonical History

### 9.3 Cancellation／Lifecycle

- Normal中Cancel
- Stage間Cancel
- Summary中Cancel
- Disconnect／Backpressure両Stage
- Cancel後の後続Generation
- Busy状態が両Stageで継続
- Shutdown Timeout／Native Boundary Recovery
- Model Close Callback Exactly Once
- Producer Thread上のNative Cancel／Close

### 9.4 UI Language

- ja／enのStatic／Dynamic Text
- UI LanguageとResponse Languageの独立性
- Runtime中Statusの即時再描画
- New Chat後維持
- Reload相当のStorage復元
- Invalid／Unavailable Storage Fallback
- Model Content非翻訳
- Safe Text描画／`innerHTML`不使用
- Known／Unknown Error表示

## 10. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

`tests/unit/summarization`を作らない場合は、同等Testの配置先をStatusへ記録する。

Manual Mac Gate：

- Summary OFF／ON
- Summary Status遷移
- UI日本語／English
- UIとResponse Languageの交差組合せ
- Normal中Stop／Summary中Stop
- Fallbackの安全表示
- New Chat後のUI Language維持
- Server Shutdown／Restart

## 11. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_YYYYMMDDHHMMSS.md
```

Statusへ次を必ず記録する。

- 変更File一覧
- Final Directory／Contract
- Config Schema Migration
- Summary Prompt Boundary
- Model Call回数／逐次性Evidence
- Fallback Matrix
- SSE Event順序
- Cancel／Shutdown Thread Boundary
- UI Translation Key／Storage Boundary
- 全Verification Command、Exit Code、件数
- Native Model Smoke／Manual UI結果
- 未解決事項／非ブロッカー
- Lightning Full Upload未実施の明記
- Phase 1完了／Backup／Phase 1-ex未着手の明記

## 12. Out of Scope

- Dedicated Summary Model／Model Download
- Guard Model／Judge Model
- Governance／Repair／RAG／Agent
- Summary Quality Judge
- Pre-generation／History Summary
- Original Answer表示UI
- Conversation Persistence／Delete
- React／Next.js／Node
- Machine Translation API
- 本格Account／OAuth／TLS終端
- Lightning Full Upload／Dependency Install／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 13. Stop／Return Conditions

次の場合、独自判断で範囲を広げず設計者役へ戻す。

- Backend Contract変更が必要
- Dedicated Modelが必要
- Contextを収めるためOriginal切捨てが必要
- Summary PromptへHistory／System Promptを渡す必要が生じた
- Thread-safe Native Stop Contractの新設が必要
- 新Dependency追加が必要
- Existing CLI Contract変更が必要
- Summary FailureでOriginalを復元できない
- Public Access／Credential境界変更が必要

## 14. Append-Only

本書はPhase 1-H初回実装Handoffとして新規追加した。実装報告、Review、Follow-upは別Timestampの新文書とする。
