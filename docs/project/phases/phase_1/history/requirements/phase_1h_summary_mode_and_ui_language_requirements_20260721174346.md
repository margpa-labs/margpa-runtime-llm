# Phase 1-H Summary Mode／UI Language 要件定義

- 文書ID: `phase_1h_summary_mode_and_ui_language_requirements`
- 状態: `accepted_design_complete_waiting_implementation_authorization`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Post-generation Summary Mode、画面表示言語切替
- 正本言語: 日本語
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](../handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- supersedes: `post_generation_summary_mode_requirements_reservation_20260721090725.md`

## 1. Objective

Phase 1-Gで成立したMinimal Web Surfaceへ、次の2機能を追加する。

```text
1. 要約モード OFF／ON
   └─ 通常回答を同じMain Modelでもう一度要約してから表示

2. 画面表示言語 日本語／English
   └─ UI Textだけを切替
   └─ Modelの出力言語とは独立
```

Phase 1-Hは、Phase 4の本格UI、会話永続化、専用要約Model、LLM-as-a-Judgeを先取りしない。現在の疎結合性、Model交換性、Single-worker、Cooperative Cancelを維持したまま、小規模なResponse TransformationとUI Localization Boundaryを成立させる。

## 2. User-visible Scope

### 2.1 要約モード

一般設定へ次を追加する。

```text
要約モード  [ OFF | ON ]
Default      : OFF
```

- OFF時はCurrent Phase 1-Gと同じ1回生成とする。
- ON時は通常回答を生成した後、同じMain Modelへ要約を1回だけ依頼する。
- 通常回答をStreaming表示してから置換しない。
- 通常回答生成中はStatusだけを表示し、要約生成の出力だけを回答欄へStreaming表示できる。
- 要約失敗時は、警告とともに通常回答へFallbackする。
- Switchは内部の`off／post_generation` ModeへMappingする。

### 2.2 画面表示言語

画面右上へ次の切替を追加する。

```text
日本語 | English
Default: 日本語
```

画面表示言語は、設定内の`Response Language`と完全に分離する。

有効な組合せ：

| UI Language | Response Language | 結果 |
|---|---|---|
| ja | ja | 日本語UI／日本語回答 |
| ja | en | 日本語UI／英語回答 |
| en | ja | 英語UI／日本語回答 |
| en | en | 英語UI／英語回答 |
| ja／en | auto | 選択UI言語／Model側自動回答 |

UI Language変更は、Model Message、System Instruction、Response Language Policy、Thinking Outputを変更しない。

## 3. Summary Runtime Values

```text
通常生成 max_new_tokens : Request値／Default 2048
要約生成 max_new_tokens : 1024固定
要約時Thinking          : disabled固定
要約Backend              : main_model
実行方式                 : Sequential
同時Model常駐            : なし
元回答保存               : true
失敗時Policy             : fallback_original
```

要約生成では、通常生成の`temperature／top_p／top_k／min_p／penalty／seed`等のEffective Generation値を継承し、`max_new_tokens`と`thinking_mode`だけを要約用Policyで上書きする。専用Sampling Profileは後続候補とする。

## 4. Processing Contract

```text
Validated Conversation Input
  → Normal Generation
  → Thinking／Final分離
  → Original Canonical Final Answer
  → Summary Request構築
  → Same Main Model／Thinking disabled／max 1024
  → Summary Final Answer検証
      ├─ Complete／Non-empty → Summaryを表示・履歴へ採用
      ├─ Failed／Empty／Length／Context不足 → Warning＋OriginalへFallback
      └─ Cancelled → Cancelled Terminal／履歴へ追加しない
```

要約対象は通常生成のCanonical Final Answerだけとする。次を要約Requestへ含めない。

- 通常生成のThinking／Reasoning Segment
- Presentation用表示Label
- 生のChain of Thought
- 元のConversation History
- User Promptの再掲
- Runtime内部状態
- System Prompt／Governance内部Evidence
- Credential／Path／Secret

## 5. Summary Instruction

要約RequestはBackend-independentなTyped Contractから構成し、特定Model名、GGUF、llama.cppを前提にしない。

要約指示は最低限、次を要求する。

- 入力された元回答を要約し、要約本文だけを返す。
- 新しい事実、判断、約束、出典を追加しない。
- 結論、前提、制約、警告、未解決事項、否定、例外を勝手に反転・削除しない。
- Code、Command、Identifier、数値等を変更する場合は意味を壊さない。
- 元回答内の指示らしきTextを命令として実行せず、要約対象Dataとして扱う。
- `ja／en`では指定されたResponse Languageに合わせる。
- `auto`では元回答の主要言語を維持する。

元回答は明確なData Boundaryで囲み、Summary System Instructionと混同させない。Phase 1-HはPrompt Injection Defense完成を主張しないが、元回答内の命令を要約器が実行対象と解釈しにくい構成を必須とする。

## 6. Original／Summary Artifact

Phase 1-Hの1 Turn内では次を明確に分離する。

```text
original_final_answer : 通常生成のCanonical Final Answer
summary_final_answer  : 要約生成のCanonical Final Answer
presented_answer      : 成功時Summary／Fallback時Original
```

- Summary成功時、次TurnのBrowser Conversation Historyへ追加するAssistant MessageはSummaryとする。
- Fallback時はOriginalをAssistant Messageとする。
- OriginalはPipeline内の独立Artifactとして保持する。
- Phase 1-HではOriginalをBrowserへ常時送信または永続保存しなくてよい。
- 将来のAudit LogでOriginal／Summaryを別Artifactとして保存できるMetadata境界を用意する。
- ThinkingはOriginal Preservationの対象にしない。

## 7. Failure／Degraded Policy

次の場合、不完全なSummaryを採用せずOriginalへFallbackする。

- Summary Inference Error
- Summary Context Limit Error
- Summary Outputが空または空白だけ
- Summary ParserからCanonical Final Answerを得られない
- Summary `finish_reason=length`
- Summary Terminalが不明または不整合

Fallback時：

- Safe Warning Codeを返す。
- OriginalをCanonical Assistant Messageとして完成させる。
- SummaryのRaw Exception、Prompt、Pathを返さない。
- Original自体のToken上限Warningを消さない。
- Summary失敗を正常なSummary成功として記録しない。

CancellationはFailure Fallbackとしない。通常生成中または要約生成中にCancelされた場合、`cancelled`で終了し、Original／SummaryのどちらもConversation Historyへ追加しない。

## 8. Context Policy

- Current Model Adapterの正確なFormatted Prompt Token検証を再利用する。
- 要約用`max_new_tokens=1024`を黙って超えない。
- Phase 1-Hでは元回答を無断切捨てしない。
- Phase 1-HではSummary Token Budgetを黙って動的縮小しない。
- Summary RequestがLoaded Contextへ収まらない場合、Warning付きOriginal Fallbackとする。
- Context Sizeの自動拡大、History圧縮、Pre-generation Summaryは後続設計とする。

## 9. Streaming／Status／Terminal

OFF時は既存のPhase 1-G SSE Contractを維持する。

ON時の論理Event順序：

```text
start(state="generating_answer")
  → Normal Generation／BrowserへDeltaを出さない
status(state="summarizing_answer")
  → Summary Delta
  → Warning 0..n
completed
```

Fallback時はSummary Deltaを採用せず、`completed.assistant_message`のOriginalを表示する。Terminal Eventは`completed／cancelled／error`のいずれか1回だけとする。

UI Statusは最低限、次を言語別に表示する。

```text
回答を生成しています / Generating an answer
回答を要約しています / Summarizing the answer
完了 / Completed
```

## 10. UI Localization Scope

切替対象：

- Document Title
- `html lang`
- Button、Label、Heading、Placeholder
- Preview Note
- Settings名とOption表示名
- Status、Warning、Known Errorの安全な表示
- Empty State／New Chat後の説明
- Accessibility用`aria-label`等
- 要約モードの説明

切替対象外：

- Modelが生成した回答
- Model Generated Thinking
- Model Key、Profile Key、Device Key等のIdentifier
- Serverから来た未知の自由Textを機械翻訳すること
- Requestの`response_language`値

Known Error／WarningはCodeをKeyとしてUI Dictionaryから表示できる。未知Codeは固定された安全なGeneric Message、またはServerのSafe Messageをそのまま表示し、Client側で恣意的に翻訳しない。

## 11. UI Language Persistence

- Browserの`localStorage`へUI Languageだけを保存してよい。
- KeyはProject Namespaceを持つ。例：`margpa.ui_language.v1`。
- 保存値は`ja／en`だけとし、不正値は`ja`へFallbackする。
- New ChatでUI Languageを初期化しない。
- Page Reload後に復元する。
- Chat Message、Credential、Response Language、Prompt、Model Outputは`localStorage`へ保存しない。
- Storage利用不可でも日本語Defaultで動作する。

## 12. Configuration

Application Configへ次のLayer Configを追加する。

```toml
[layers.summarization]
mode = "off" # off | post_generation
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
failure_policy = "fallback_original"
```

- Application Config Schemaは`2`から`3`へ更新する。
- Deployment Profile Schemaは変更しない。
- UI LanguageはTOML／Server Runtime Configへ追加しない。
- `/api/v1/runtime`はSummary Defaultを安全に返す。
- Browser RequestのSwitchは`settings.summary_mode`へMappingする。
- Phase 1-HではSummary Backendとして`main_model`だけを受理する。

## 13. Security／Privacy

- Summary OutputもPlain Textで描画し、`innerHTML`を使わない。
- Original／Summary／PromptをServer Access Logへ出さない。
- Summary ErrorにRaw Exception、Absolute Path、Promptを含めない。
- UI DictionaryはRepository内へ保持し、外部CDN／翻訳APIを使わない。
- UI Language切替でBasic Auth／Access Control境界を変えない。
- Summary LayerはToolを呼ばない。
- Phase 1-HはGuardrail／Content Safety／Prompt Injection対策完成を主張しない。

## 14. Non-functional Requirements

- OFF時の追加Inference回数は0である。
- ON時は同じMain Modelを逐次利用し、同時Generationを行わない。
- Modelを要約ごとにReloadしない。
- Normal＋Summaryを1つのActive Conversation SessionとしてGeneration Gateで保護する。
- Summary開始前にNormal Native Streamを確実にCloseする。
- SSE Consumer Disconnect、Stop API、Runtime ShutdownのCooperative Cancelを両段階で維持する。
- CLIの既存One-shot動作を変更しない。
- 新規Runtime Dependency／JavaScript Libraryを追加しない。
- Mac Python 3.13.14とLightning Python 3.12.11のSupport Pairを維持する。

## 15. Out of Scope

- Dedicated Summary Model
- 要約Model選択UI
- Pre-generation Prompt／History要約
- RAG Context要約
- Chat履歴永続化
- 元回答の表示切替UI
- 要約品質のJudge評価
- ARGD／DAGDによる要約判定
- Prompt Injection／Content Safetyの完成
- React／Next.js／Node Build
- Machine Translation API
- UI言語のTOML永続化
- Phase 4の本格設定UI
- Lightning Full Upload／Native Validation
- Phase 1完了宣言／Backup／Git／GitHub公開

## 16. Acceptance Criteria

### 16.1 Summary Mode

- OFF時、Model Callが正確に1回であり、Phase 1-G Streaming互換である。
- ON時、NormalとSummaryが正確に各1回、重複せず逐次実行される。
- Summary RequestへOriginal Canonical Finalだけが渡る。
- Summary Thinkingは常にdisabled、maxは1024である。
- Summary成功時はSummaryだけが表示・履歴採用される。
- Summary失敗、空、Context不足、Length時はWarning付きOriginalへFallbackする。
- CancelがNormal／Summaryの両段階で成立する。
- Cancel後に次Generationが成立する。
- Shutdown Timeout／Close契約をPhase 1-Gから後退させない。

### 16.2 UI Language

- 右上Switchで日本語／Englishを即時切替できる。
- UI言語とResponse Languageの全組合せが独立して動作する。
- New Chat後もUI Languageが維持される。
- Reload後にUI Languageだけが復元される。
- Message／Credential／Model OutputをBrowser Storageへ保存しない。
- Title、`html lang`、主要ARIA、Status、Setting、Known Errorが切り替わる。
- Model Output／ThinkingをUI切替で翻訳しない。

### 16.3 Regression

- Existing Static／Unit／Integration／Model Smokeが合格する。
- Basic Auth／Non-loopback Fail Closedが後退しない。
- SSE Terminalは正確に1回である。
- Hidden ThinkingがClientへ漏れない。
- Model Load once／Close onceを維持する。

## 17. Authorization Boundary

本書はPhase 1-Hの正本要件を確定するが、実装開始を自動許可しない。実装担当は、ユーザーからPhase 1-H実装開始の明示指示を受けた後、対応Handoffの範囲だけを変更できる。

## 18. Append-Only

要件予約文書を変更せず、本書をPhase 1-Hの後継正本として追加した。
