# ADR-0020: Phase 1-H Summary PipelineとUI Languageを分離する

- 文書ID: `adr_0020_phase_1h_summary_pipeline_and_ui_language_separation`
- 状態: `accepted`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- supersedes: なし

## Context

Phase 1-Gで、Main Modelを1回呼び出すMinimal Web Surface、Browser-owned Ephemeral Conversation、Response Language、Thinking Presentation、SSE、Cancel、Preview Access Controlが成立した。

ユーザーはPhase 1-Hとして次を要求した。

- 通常回答を同じMain Modelでもう一度要約してから表示するOption。
- 画面右上で日本語／英語を切り替えるUI。
- UI LanguageとModel Response Languageを独立させること。

要約をBrowser側の2回目API Callとして実装すると、Cancel、Generation Gate、Original／Summaryの関連、Audit Hookが分断される。UI LanguageをResponse Languageへ流用すると、「英語UI／日本語回答」等の有効な組合せを表現できない。

## Decision

### 1. Summary

- SummarizationをApplication側のOptional Response Transformation Layerとする。
- `off／post_generation` Modeを持つ。
- ON時はNormal GenerationとSummary Generationを1つのConversation Sessionが逐次所有する。
- Summary Backendは初期版で`main_model`を使う。
- Normal maxはRequest値／Default 2048、Summary maxは1024、Summary Thinkingはdisabledとする。
- Summary対象はOriginal Canonical Final Answerだけとする。
- Summary失敗、空、Context不足、Length時はWarning付きOriginalへFallbackする。
- Summary中CancelはFallbackせず`cancelled`とする。
- Original／Summary／Presented Answerを論理的に分離する。

### 2. UI Language

- UI LanguageはBrowser-only Presentation Preferenceとする。
- 値は`ja／en`、Defaultは`ja`とする。
- Response Languageの`ja／en／auto`から独立させる。
- UI LanguageだけをNamespaced `localStorage`へ保存する。
- Translation DictionaryをRepository内のVanilla JavaScriptで持つ。
- Model Output／Thinkingを翻訳しない。

### 3. Configuration

- Summary Layerは`config/application.toml`の`[layers.summarization]`へ追加する。
- Application Schemaを`2`から`3`へ更新する。
- Deployment ProfileへSummary設定を複製しない。
- UI LanguageはTOMLへ追加しない。

## Rationale

- 要約は追加Inferenceであり、単なるUI加工ではない。
- Session内に置くことで1 Model／1 Gate／1 Cancel Contractを維持できる。
- Modeにすることで将来の別方式やDedicated Modelへ拡張できる。
- 不完全SummaryよりOriginalを優先する方が情報欠落を隠しにくい。
- UI Languageは利用者の画面Preference、Response LanguageはModelへの出力Policyであり、責務が異なる。
- Current UI文字列数では外部i18n Dependencyを導入せずに成立する。

## Rejected Alternatives

### BrowserがMain APIを2回呼ぶ

却下。Cancel、Busy、Session、Audit Correlationが分断され、BrowserがSummary Promptを知ることになる。

### Normal回答を先にStreamingし、後からSummaryで置換する

却下。見えていた回答が突然変わり、Canonical Historyとユーザー認識が不安定になる。

### Summary失敗時にTurn全体をErrorとする

却下。既に有効なOriginal Answerがあるため、安全なWarning付きFallbackの方が可用性が高い。

### Summary Lengthでも不完全Summaryを採用する

却下。欠落を完成Summaryとして表示する危険がある。Phase 1-HではOriginalへFallbackする。

### Summary中Cancel後にOriginalを表示する

却下。停止したユーザー意思に反して回答を確定させるため。

### UI LanguageとResponse Languageを1つにする

却下。英語UI／日本語回答等の組合せを失う。

### UI LanguageをApplication TOMLへ保存する

却下。Server／Deployment設定ではなくBrowser利用者ごとのPreferenceである。

### i18n Framework／翻訳APIを導入する

却下。Phase 1-H規模ではDependencyとSecurity Surfaceが過大である。

## Consequences

- Summary ON時はLatencyとInference Costが増える。
- Current 4096 Contextでは長いOriginalがFallbackする可能性がある。
- Same Model Summaryの正確性は保証されない。
- Conversation SessionのState MachineとTest Matrixが増える。
- UI Language切替は軽量で、Response Language契約を壊さない。
- 将来のSummary Model、Audit Log、Judge、Governance接続点を確保できる。

## Implementation Gate

本ADRは設計判断をAcceptedとする。Source／Config／UI変更は、ユーザーが実装担当へPhase 1-H開始を明示した後に限る。
