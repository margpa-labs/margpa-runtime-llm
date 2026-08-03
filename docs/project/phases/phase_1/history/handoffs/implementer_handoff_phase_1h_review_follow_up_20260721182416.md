# 実装担当向け Phase 1-H Review Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1h_review_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 18:24:16 JST`
- 更新日時: `2026-07-21 18:24:16 JST`
- Snapshot: `20260721182416`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md](designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md)
- 実装報告: [implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md](implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- 前回Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- Latest Index: [documentation_index_20260721182416.md](../documentation_index_20260721182416.md)
- supersedes: `implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md`

## 1. Current State

Phase 1-Hの中核機能、Static／Unit／Integration、Mac Metal実Modelは成立している。ただし設計Reviewで4件のMandatory Findingが確認されたため、Phase 1-Hは`changes_requested`である。

```text
Core Summary Pipeline        : Pass
Config／Cancel／Fallback      : Pass
UI Language Main Path        : Pass
Successful Summary SSE       : Original全文を含むためFail
Long Silent SSE              : Keepaliveなし
Summary UI Risk Notice       : 不足
Runtime Error Relocalization : 不足
```

本Follow-upは4件だけを修正する。Phase 1-H全体を再設計しない。

## 2. Start Condition

ユーザーが実装担当Taskへ本Follow-up開始を明示した時点で、Section 3の限定範囲を変更できる。それ以前はSource／Config／Testを変更しない。

## 3. Authorized Scope after User Approval

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
tests/unit/conversation/test_conversation_generation.py
tests/integration/web/test_web_app.py
必要な既存Web／Conversation Test Fixture
docs/handoffs/implementer_status_phase_1h_review_follow_up_*
```

`app.css`の変更は、文言追加による最小Layout調整が必要な場合だけ許可する。

Config Schema、Summary Prompt、Model Adapter、CLI、Dependency、`pyproject.toml`、`uv.lock`は変更しない。

## 4. Work Package 1：Successful Summary SSEのData Minimization

### 4.1 Required Public Contract

Summary成功時、Public SSEへ返す回答本文はPresented Answerだけとする。

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "usage": {},
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

禁止：

```text
original_assistant_message
summary_assistant_message
Original全文を含む任意の別Field
Summary本文の重複Field
```

Originalは`ConversationGenerationSession`内のServer-side Artifactとして保持する。Phase 1-HではClientへ返さず、永続保存もしない。将来Audit Logは別責務で接続する。

### 4.2 Fallback Contract

Fallback時はOriginalがPresented Answerになるため、次を許可する。

```json
{
  "assistant_message": {
    "role": "assistant",
    "content": "Original answer"
  },
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": false,
    "fallback_used": true,
    "original_finish_reason": "stop",
    "summary_finish_reason": null
  }
}
```

FallbackでもOriginalを別Fieldへ重複させない。

### 4.3 Usage Metadata

Current Presented `usage`は維持する。Original／Summaryの段階別Usageを残す場合、回答本文を含まない`stage_usage`等のMetadataへ整理してよい。

既存Clientが未知Fieldを無視できることを維持する。

### 4.4 Required Test

Success SSE Testへ最低限次を追加する。

```text
Original Canonical FinalはResponse全体に存在しない
Summaryはassistant_messageとして存在する
Summary Thinkingは存在しない
Original Thinkingは存在しない
original_assistant_message Keyは存在しない
summary_assistant_message Keyは存在しない
summary_applied=true
fallback_used=false
```

Fallback Testでは、Originalが`assistant_message`として1回だけ存在し、`fallback_used=true`であることを確認する。

## 5. Work Package 2：SSE Keepalive

### 5.1 Interval

Phase 1-H Follow-upの固定値：

```text
SSE Keepalive Interval : 15.0 seconds
Wire Format            : : keepalive\n\n
Semantic Event         : No
Conversation History   : No
Audit Event            : No
```

KeepaliveはSSE Commentであり、`event:`／`data:`を付けない。BrowserのCurrent ParserはData LineのないBlockを無視できる。

### 5.2 Required Behavior

- Application Eventが15秒間来ない場合だけKeepalive Commentを送る。
- Eventが送信された場合はIdle TimerをResetする。
- Normal Hidden GenerationとSummary Buffered Generationの両方で動作する。
- Consumer Disconnect後に送らない。
- Terminal後に送らない。
- Heartbeat専用Background Taskを残さない。
- Generation QueueへConversation Eventとして積まない。
- Queue Capacity、Backpressure、Terminal Countを変えない。
- `Cache-Control: no-store`、`X-Accel-Buffering: no`を維持する。
- Raw Exception、Request ID、Prompt等をCommentへ含めない。

実装は`stream_session_as_sse()`のAsync Consumer側で行う。Native Model／Producer ThreadへTimer処理を入れない。

### 5.3 Required Test

Testでは実時間15秒を待たない。IntervalをMonkeypatch可能なModule Constant等として定義し、短いTest値を使う。

確認項目：

- Blocking／Silent Producer中にKeepaliveが1回以上出る。
- Keepaliveは`ConversationEvent`としてCountされない。
- Keepalive後に通常Eventを受信できる。
- Completed後にKeepaliveが出ない。
- DisconnectでProducerへCooperative Cancelが伝わる。
- Cleanup後にTask／Threadが残らない。
- Existing Cross-thread Cancel Testが継続合格する。

## 6. Work Package 3：Summary Risk Notice

日本語Default文言：

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増え、要約により詳細、前提、注意事項等が省略・変形される可能性があります。
```

English Default文言：

```text
When ON, the completed answer is summarized by the same model.
This increases latency and token usage, and details, assumptions, or cautions may be omitted or altered by the summary.
```

- Translation DictionaryとInitial HTMLを一致させる。
- Model品質保証、正確性保証を主張しない。
- 既存Layoutを崩さない。
- Static Testで日英双方のRisk表現を確認する。

## 7. Work Package 4：Runtime Status Relocalization

Render済みRuntime Error Textを恒久Stateとして保持しない。

候補State：

```text
runtimeStatus.kind = loading | metadata | known_error
runtimeStatus.translationKey = runtimeLoading | runtimeLoadFailed
runtimeStatus.text = Model／Profile／Device等のOpaque Metadata成功時だけ
```

`renderRuntimeStatus()`等の単一責務を追加し、`applyTranslations()`から必ず呼ぶ。

期待動作：

```text
Loading中 ja → en : Checking runtime…へ更新
Failure後 ja → en : Could not load runtime information.へ更新
Failure後 en → ja : Runtime情報を取得できませんでした。へ更新
Success後 ja ↔ en : Model／Profile／Device Identifierは不変
```

未知のServer自由TextをClient側で機械翻訳しない既存方針は維持する。

新Dependencyを追加せず、可能な範囲でAutomated Testを追加する。Browser DOM Harnessを新規Dependencyなしで安全に作れない場合、Source-level Contract TestとManual Browser Evidenceを組み合わせ、Statusへ制約を明記する。

## 8. Optional Non-blocking Improvement

Summary StageのBroad `except Exception`でFallbackする場合、固定された安全なOperator Logまたは内部Reason Codeを残してよい。

条件：

- ClientへRaw Exception、Prompt、Pathを返さない。
- Original Fallbackを壊さない。
- LogへConversation本文を出さない。
- 本改善のためにScopeを広げない。

実施しなくても4 Mandatory Findingが解消されればFollow-up受入対象となる。

## 9. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
node --check src/margpa_runtime_llm/web/static/app.js
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

Manual Mac Browser：

- Summary ON成功で要約だけが表示される。
- Browser DevTools／SSE ResponseにOriginal全文が存在しない。
- Summary FallbackではOriginalが表示される。
- Summary Noteが日英でRiskを説明する。
- Runtime API Failure後にUI `ja → en → ja`が切り替わる。
- UI LanguageとResponse Languageは独立する。
- Stop／New Chat／Reloadが後退しない。

## 10. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1h_review_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を必ず記録する。

- 4 Findingごとの変更内容
- Final SSE Success／Fallback Payload Schema
- Original非送信のTest Evidence
- Keepalive Interval／Wire Format／Lifecycle
- Keepalive Regression Test
- Summary Risk Noticeの日英文言
- Runtime Status State／Relocalization Evidence
- 変更File一覧
- 全Verification Command、Exit Code、件数
- Mac Metal Smoke結果
- Manual Browser／DevTools確認結果
- Optional Improvement実施有無
- Lightning Upload未実施
- Phase 1完了／Backup／Phase 1-ex／Git未着手

## 11. Out of Scope

- Summary Prompt／Summary Model／Token値の再設計
- Dedicated Summary Model
- Config Schema追加変更
- Model Adapter／Backend Contract変更
- CLI変更
- New Dependency
- UI Framework移行
- Conversation永続化
- Audit Log本体
- Guardrail／Judge／Governance／Repair／RAG／Agent
- Lightning Upload／Model Transfer／Cloud実行
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 12. Stop／Return Conditions

次の場合、独自に範囲を広げず設計者役へ戻す。

- OriginalをClientへ返さないと現行UIが成立しない。
- KeepaliveのためNative Model Threadを変更する必要がある。
- SSE Protocol／FastAPI Dependency変更が必要になる。
- New Libraryが必要になる。
- Existing Cancel／Shutdown Contractが後退する。
- Public Access／Credential境界の変更が必要になる。
- Summary Prompt／Config Schemaの変更が必要になる。

## 13. Authorization Boundary

本Handoffは実装範囲を定義するが、実装開始指示ではない。ユーザーが実装担当TaskへFollow-up開始を明示した後に限り、Section 3の変更を行える。

## 14. Append-Only

前回Handoff、実装報告、Reviewを変更せず、新TimestampのFollow-up Handoffとして追加した。
