# Phase 2-E-I 実装完了（I-2〜I-5）＋ Streaming Usage欠落の発見と修正

```yaml
document_id: claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_20260818181920
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（将来の参照用）
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-18 18:19:20 JST
language: ja
purpose: |
  設計確定済みだった2-E-I（Context Window使用状況の可視化・LLM自己認識
  ON/OFF機能）について、ユーザー指示「工程：I-1→I-2→I-3→I-4→I-5。一気に
  よろしく。終わったら、作業用indexと、Automationのエビデンスを書いて
  おいて。」に基づき、I-2〜I-5を実施した記録。設計自体は
  [claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md]
  （以下「設計書」）で確定済み。
  本Docはあわせて、実装過程で発見した独立の事実
  ——llama-cpp-python（本Runtimeが使用する既存Backend）のStreaming Chat
  Completion形式が、Streaming中は一度もToken使用量（usage）を報告しない
  という、既存Adapter側の潜在的欠落——の発見・修正も記録する。
created: Claude Code
```

## 0. 位置づけ

設計書の第7節Statusは「実装（I-2以降）はユーザーの明示的な一時停止指示（Manual Compaction実施待ち）により未着手」だった。本Compaction Cycle開始直後、ユーザーから工程I-2〜I-5を一括で実施する明示指示があり、本Docはその実施内容を記録する。

## 1. I-2：Backend実装（Context Usage露出）

### 1.1 設計判断の実装時解釈

設計書は「新規Response Contract」「新規Route」の2案を提示しつつ、Q1（低Cost・既存`_completed_event`と同じTimingで開始）の確定を根拠に、**既存の完了時SSE Event（COMPLETED）へ相乗りする方式**を選択した。新規GET Routeは追加していない——理由は、Q1が明示的に「既存_completed_eventと同じTiming」を選んだこと自体が、新規Pull Route（生成とは独立したTimingでの取得）ではなく、既存の完了通知に相乗りする経路を示唆していたため。この設計時点での未解決の曖昧さ（GET Route案）は、実装時判断（設計書第4節Q3の趣旨）として解消した。

### 1.2 実装内容

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  - ConversationGenerationSession／ConversationGenerationServiceへ
    text_token_counter（TextTokenCounter）とeffective_context_sizeを追加。
  - _completed_event()のdataへ"context_usage"Fieldを追加。中身は
    _context_usage()が算出：
      - prompt_tokens／completion_tokens／total_tokensは、summary_mode時に
        presented（要約Sub-request）ではなく、original（実際の会話Request）
        のusageを使う——presentedを使うと要約Sub-requestの小さいPrompt
        Sizeが誤って報告される。
      - breakdown（Q2の4分類）：
        system_prompt_tokens = System Role Message（RAG参照Message以外）の
          Token数合計。
        rag_context_tokens = name="documentation_reference"のMessageの
          Token数合計。
        conversation_history_tokens = max(0, prompt_tokens -
          system_prompt_tokens - rag_context_tokens)（残差方式。History
          側を個別に再TokenizeするとChat Template整形Overheadの二重計上に
          なるため、意図的に残差として算出）。
        free_tokens = max(0, effective_context_size - total_tokens)。
      - usage_ratio = min(1.0, total_tokens / effective_context_size)。

src/margpa_runtime_llm/bootstrap/web_application.py
  - text_token_counter=application.service.count_text_tokensを常時配線。

src/margpa_runtime_llm/web/persistent_streaming.py
  - project_persistent_event()のCOMPLETED分岐へ"context_usage"を追加
    （既存のcommon dictはWhitelist方式で個別Fieldを列挙する実装のため、
    ここへ明示追加しないとPersistent SSE経由では届かなかった）。
```

Ephemeral（`/api/v1/chat/stream`）側は`web/streaming.py`のSSE Encodeが
`event.data`をそのままJSON化する実装であるため、上記の変更のみで
自動的に伝播する（追加配線不要）。

### 1.3 Test

`tests/unit/conversation/test_conversation_generation.py`へ6件追加
（Context Usage欠落時null、通常算出、RAG併用時の分類分離、Summary Mode時
にOriginal Requestを使うことの確認、text_token_counter未配線時の
Breakdown全0Fallback）。`tests/integration/web/test_persistent_web_app.py`
へ2件追加（Persistent SSE Wireへの伝播、未算出時のnull伝播）。

## 2. I-3：Configuration Control新規Toggle

### 2.1 設計判断の実装時解釈

設計書I-3見出しは「Configuration Controlへの新規Toggle追加」だが、
Q4の確定内容（「単純なSettings、SettingsPanel直結の即時反映Toggle。
Configuration ControlのPatch-Preview-Apply Flowは不採用」）を素直に
実装すると、既存の`thinking_mode`／`documentation_rag_mode`と同型の、
`conversation.contracts.ConversationSettings`直下のFieldとして実装する
のが正しい——`configuration_control`Module（Process全体のRuntime設定を
Preview-Apply Flowで制御するための別Module）を経由する必要は無い。

### 2.2 実装内容

```text
src/margpa_runtime_llm/modules/conversation/contracts.py
  - 新規StrEnum ContextUsagePromptInjectionMode（DISABLED／ENABLED）、
    既定DISABLED。
  - ConversationSettingsへcontext_usage_prompt_injection_mode Field追加。
    Ephemeral／Persistent両方のRequest Contract（ConversationSettingsを
    共有）に自動的に反映される。

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  - _build_request()にて、Mode=ENABLED かつ chat_prompt_token_counterが
    利用可能な場合、既に構築済みのMessages（History＋System Prompt＋RAG
    参照、すべて込み）のToken数を実測し、その場でSystem Role Messageと
    してNotice文を追加注入する（name="context_usage_notice"）。
  - Notice文はQ5の確定通り、**純粋にReactive**：「ユーザーから明示的に
    尋ねられた場合にのみ...回答してください。尋ねられていない場合は...
    自発的に言及しないでください」という指示を明記。
  - chat_prompt_token_counterは、従来documentation_rag利用時のみ配線
    されていたが（bootstrap/web_application.py）、本機能はRAG利用有無に
    関わらず必要なため、常時配線するよう変更。

Q3（丸IconのVisual仕様）：実装時確認に一任、第4節参照。
```

### 2.3 Test

`tests/unit/conversation/test_conversation_generation.py`へ3件追加
（既定OFF時は注入なし、ON時はReactive文言を含むSystem Message注入、
Counter未配線時は安全にSkip）。

## 3. I-4：Frontend実装

### 3.1 事前調査

Frontend構造（`frontend/src/`）は本Session内で未調査だったため、
並行してExplore Agentへ調査を依頼した（SSE Event型定義、Settings UI
構造、Composer配置、API Client、i18n、CSS Theme変数、App.tsx配線の
7観点）。報告により、**Backend側のcontext_usage FieldはSSE経由で既に
Frontendまで到達しており（Filter無し）、純粋にFrontend型定義・UI実装の
問題である**ことが確認できた。

### 3.2 実装内容

```text
frontend/src/types.ts
  - ContextUsage／ContextUsageBreakdown型追加。StreamEventDataへ
    context_usage Field追加。GenerationSettingsへ
    context_usage_prompt_injection_mode Field追加。

frontend/src/components/ContextUsageGauge.tsx（新規）
  - 丸Gauge Icon（Ring形式、使用率で塗り分け、85%/95%閾値で
    警告色・危険色に切替）。
  - Hover Tooltipは既存SidebarToggleButtonと全く同じPattern（Hoverで
    Tooltip、ClickでToggle）を転用。
  - Click時のみBreakdown Panel開閉（Q2の4分類：会話履歴／System
    Prompt／RAG Context／残り）。
  - Data未到達時（初回Turn完了前）はDisabled表示＋専用Tooltip文言。

frontend/src/components/Composer.tsx
  - .actions行内、Stop/Send直前へContextUsageGaugeを追加。

frontend/src/components/SettingsPanel.tsx
  - SettingsFormStateへinjectContextUsage: boolean追加。既存
    thinking-mode Switch-Rowと同型のCheckboxを追加。

frontend/src/App.tsx
  - contextUsage State追加。Ephemeral／Persistent両方のcompleted Event
    Handlerでcontext_usageを捕捉。会話切替・新規Chat時にNullへReset
    （古いConversationの数値が残るのを防止。Reload直後は次のTurn完了まで
    Unavailable表示——第6節に限定条件として明記）。
  - settingsPayload()へcontext_usage_prompt_injection_mode追加。

frontend/src/i18n/translations.ts
  - contextUsageToggleShow／Hide、contextUsageUnavailable、
    contextUsagePanelLabel、4分類Label、injectContextUsageLabel／Note
    をja／en両方に追加。

frontend/src/styles/app.css
  - --gauge-warn／--gauge-danger（Light／Dark両Theme）追加。
  - .context-usage-*一式（Sidebar Toggle Buttonの規約を踏襲）。
```

### 3.3 Test

`frontend/src/components/ContextUsageGauge.test.tsx`（新規、3件）：
未到達時のDisabled表示、Click Toggleと Breakdown内容、日本語Label確認。
既存`SettingsModal.test.tsx`のFixtureへinjectContextUsage Field追加。

## 4. 実装中に発見したBackend Adapterの潜在的欠落（Streaming Usage）

### 4.1 発見の経緯

I-2完了後、実Browser・実Local Model（Mac、Qwen3-4B）でLive確認したところ、
実際のTurn完了後もContext Usage Gaugeが「未取得」のまま変化しないことに
気づいた。生SSE出力を`curl`で直接確認したところ、`"context_usage":null`
——Backend側のcontext_usage算出Logic自体は正しく動作しているが、その
入力である`original.usage`（TokenUsage）が常にNoneだった。

### 4.2 根本原因

インストール済みllama-cpp-python（`.venv/lib/python3.13/site-packages/
llama_cpp/`）のSource Codeを直接確認した結果、次の事実を確認した。

```text
llama.py: Llama._create_completion()
  - Non-streaming分岐（Line 1788-1806）：戻り値へ"usage"Keyを含む。
  - Streaming分岐（Line 1589-1706）：最終Chunk（finish_reason付き）を
    含め、いずれのYield Objectにも"usage"Keyを一切含まない。

llama_chat_format.py: _convert_text_completion_chunks_to_chat()
  - Streaming用のChat Completion Chunk変換Generator。全Chunkについて
    "usage"を含めない（Non-streaming用の
    _convert_text_completion_to_chatのみ"usage": completion["usage"]
    を含む）。

  include_usage／stream_optionsに相当するKwargも、このVersionには
  存在しない（grep 0件）。
```

すなわち、**Streaming生成時、llama-cpp-pythonはToken使用量を一度も
報告しない**——これはMARGPA側のBugではなく、使用しているBackend
Library自体の仕様（少なくとも本Version）である。

この欠落は、本Sub-phaseで新設したcontext_usage Fieldだけでなく、
**既存の`usage`Field（`_completed_event`のdata、Phase 1-Gから存在）にも
同様に影響していた**——Streaming経由の生成では、`usage`は常にNoneで
あり、この事実はこれまで可視化する消費者が存在しなかったため、
気づかれていなかった。

### 4.3 修正内容

```text
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
  - _validate_context()の戻り値をNoneからint（Prompt Token数）へ変更
    （既存呼び出し元4箇所のUsageに影響なし、直接Unit Testも戻り値を
    検証していないことを確認済み）。
  - stream()にて、_validate_context()の戻り値をfallback_prompt_tokens
    として、chat_template.count_text_tokensをcompletion_text_token_
    counterとして、LlamaCppGenerationStreamへ渡すよう変更。

src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
  - LlamaCppGenerationStreamへfallback_prompt_tokens／
    completion_text_token_counterを追加。Streaming中のText Deltaを
    累積保持。
  - 最終Chunk確定時：`parse_token_usage(payload) or self._fallback_usage()`
    ——Backend Native値が存在すればそれを信頼し（将来Versionで
    Streaming Usageに対応した場合に備える）、存在しなければ
    Fallback Usage（Prompt Token数は元々Fail-closed Context Checkで
    算出済みの値を再利用、Completion Token数は累積Textを都度
    Tokenizeして算出）を用いる。
```

この修正により、既存の`usage`FieldもStreaming経由で正しく算出される
ようになった——2-E-Iのための変更でありながら、Phase 1-G以来の既存
Telemetry Gapも同時に解消した。

### 4.4 Test

`tests/unit/inference/test_llama_cpp_boundary.py`へ2件追加（Backend
Native Usage欠落時のFallback算出値確認、Backend Native Usage存在時は
そちらを優先することの確認）。既存6箇所の`LlamaCppGenerationStream`直接
構築Test（Constructor引数が増えたことによる型不整合）を修正。

## 5. I-5：Validation・実Browser確認

### 5.1 自動Validation

```text
Backend: pytest -q               694 passed, 3 deselected
Backend: ruff check（変更File）   All checks passed
Backend: mypy（変更File）         Success: no issues found
Frontend: npm run lint            Clean
Frontend: npm run typecheck       Clean
Frontend: npm test（Vitest）      13 Files, 72 Tests, All passed
Frontend: npm run build           Clean（app.js 251.51kB, app.css 17.36kB）
```

### 5.2 実Browser・実Local Model確認

`.claude/launch.json`へ新規Entry`margpa-web-i-verify`を追加（Port 8001、
`--conversation-persistence`、専用Runtime Data Root・Scope-ID）。実際に
Qwen3-4B（Mac、Metal）でTurnを実行し、次を確認した。

```text
- 初回Load時：Gauge Iconは無効表示（"コンテキスト使用状況は未取得です"）。
- Turn完了後：Iconが実際の使用率（Ring Fill）を表示、Hover Tooltipが
  「コンテキスト状況を表示」に変化。
- Click：Breakdown Panelが開閉。値の例（あるTurn）：使用率1%、
  会話履歴27、System Prompt 30、RAG Context 0、残り8,125、
  67 / 8,192 tokens——Context Sizeは2-E-C（Mac専用Default）で設定した
  8192と一致。
- Settings Modal内「LLMへContext使用率を伝える」Checkboxが表示・操作
  可能。ONにした状態で「今、コンテキストは何パーセントぐらい
  使っていますか？」とユーザーが尋ねたところ、実Modelが「1%」と正しく
  回答した——Q5（純粋にReactive、尋ねられた時のみ回答）の意図通りの
  End-to-End動作を、実Modelの応答として直接確認した。
- Dark Theme：Gauge・Panelとも正しい配色で表示（既存Theme変数を再利用）。
```

## 6. 限定条件・既知の制約

```text
- Context Usageは、会話をServer側から再読込しただけ（新規Turn未実行）の
  状態では表示されない——SSE経由のみでClient State（Ephemeral）を更新
  する設計であり、専用GET Routeも永続化も追加していないため（第1.1節の
  設計判断）。次のTurn完了まで「未取得」表示が続く。低Cost開始という
  設計意図（設計書Q1）を優先した、意図的なV1の制約。
- Context Usageの内訳（第4分類）は、Prompt全体のExact Token数から
  System Prompt・RAG参照分を差し引いた残差として会話履歴を算出する
  近似であり、Chat Template自体の整形Overhead（Role区切り等）は
  会話履歴側に含まれる。
- Summary Mode有効時、実際に保存されるAssistant Messageは要約後の
  短い文章だが、Context Usageの算出にはOriginal（要約前）のPrompt・
  Completion Token数を用いる——将来のContext占有量をやや保守的に
  （実際より高めに）見積もる。安全側の近似として意図的に採用。
- 第4節のStreaming Usage Fallbackは、Backend Native値が存在しない場合の
  近似算出であり、llama-cpp-pythonの内部Tokenization処理と、MARGPA側の
  Chat Template Tokenize処理が完全に同一Algorithmであることを保証する
  ものではない（別経路のTokenize呼び出しであるため、僅かな差異が
  生じうる）。
```

## 7. Status

```text
Current Point            : Phase 2-E-I、I-1〜I-5すべて完了。実装・Test・
                            静的解析・実Browser確認、いずれも完了。
                            実装過程で発見したStreaming Usage欠落
                            （第4節）も、Adapter層で修正・Test済み。
Files Created／Modified  : Backend 7File（conversation_generation.py、
                            conversation/contracts.py、conversation/
                            public.py、web_application.py、
                            persistent_streaming.py、llama_cpp/
                            adapter.py、llama_cpp/stream.py）＋Test 4File。
                            Frontend 8File（新規ContextUsageGauge.tsx／
                            .test.tsx含む）。.claude/launch.json
                            （新規Entry追加）。
Validation                : 第5.1節（自動）・第5.2節（実Browser・実Model）
                            のとおり、いずれもClean。
Open Current Blocker      : NONE。
Controller-owned Next Work: 予約Task（Phase Index参照）のTrigger成立を
                            待つのみ。future_scope_proposal 2件
                            （Context Observatory・LLM Self-awareness）は、
                            既存History Fileの無許可上書き禁止
                            （運用メモ第2.1節）に該当するため、本Docでは
                            直接編集せず、前倒し完了した部分の反映は
                            後続のPhase Index側（Current Operational
                            State層）で行う。
Exact Next Route          : ユーザーの次の判断待ち。
```
