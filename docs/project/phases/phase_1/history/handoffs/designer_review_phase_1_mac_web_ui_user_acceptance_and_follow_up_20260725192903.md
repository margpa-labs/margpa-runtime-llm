# Phase 1 Mac Web UI User Acceptance Review and Follow-up

- 文書ID: `designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up`
- 状態: `reviewed_with_follow_up`
- 作成日時: `2026-07-25 19:29:03 JST`
- 作成担当: 設計者役担当Task
- 対象環境: Mac／Local Web Preview
- 対象Phase: Phase 1-G／1-HおよびPhase 1-F Follow-up
- 実装許可: 本文書単独では付与しない

## 1. Review Outcome

Mac Web Previewは、Phase 1の最小公開評価画面として想定した構成と動作を概ね満たしている。

```text
Visual Composition                    : PASS
Ephemeral Multi-turn                 : PASS
New Chat／Browser Memory Reset       : PASS
Model Reload Separation              : PASS
Send Button                          : PASS
Stop Button                          : PASS
Ctrl+Enter Send                      : PASS
Token Limit Behavior                 : PASS
UI Language Switch                   : PASS
Response Language Switch             : PASS
Summary Mode                         : PASS
Thinking Presentation               : EXPLAINED／UX FOLLOW-UP
Markdown Presentation                : NOT IMPLEMENTED／FOLLOW-UP
User／Assistant Copy                 : NOT IMPLEMENTED／FOLLOW-UP
```

Phase 1-G／1-Hの既存Repository Acceptanceを覆す重大Failureは確認されていない。一方、Thinking設定の意味が画面だけでは分かりにくいため、Top-level Phase 1の最終User Acceptance前に扱いを明示する必要がある。

## 2. Visual Evidence Reviewed

次のLocal Screenshotを視認した。

- `スクリーンショット 2026-07-25 19.12.25.png`
- `スクリーンショット 2026-07-25 19.12.35.png`

Absolute Local Pathは本公開候補文書へ記録しない。Screenshot自体は現在Repository Artifactではない。

確認できた画面要素：

- Nazuna Research Governance LLM Branding
- `MARGPA Runtime LLM` Title
- Model／Profile／Device／Acceleration表示
- UI日本語／英語切替
- New Chat
- Preview注意表示
- Message Timeline
- Composer
- Stop／Send
- Response Language
- Max New Tokens
- Thinking Visibility
- Summary Mode
- Thinking／Summary注意事項

Desktop Previewとして、Header、Message、Composer、Settingsの責務分離は明確であり、Phase 1 UIとして想定どおりである。

## 3. User Test Inputs

代表的な入力：

```text
キミの役割は？
you are task？
小型LLMを交換可能にする設計を考えてください。日本語で。
```

同一Promptの複数回実行、言語切替、複数Turn、長い構造化回答、Token上限による途中停止を含む。

Model Outputの内容品質は本UI Acceptanceと分離する。回答が一般的でProject固有情報を持たない点は、Model RuntimeのFailureではなく、将来のProject Documentation Explainer／RAGが価値を持つObservationである。

## 4. Confirmed Behavior

### 4.1 Ephemeral Multi-turn

同一Browser Tab内でUser／Assistant Messageが交互にRequestへ含まれ、複数Turnが成立した。

Persistent Historyではない。Reload時に失われるPhase 1のBrowser Memoryであり、Phase 2の永続Conversationとは区別する。

### 4.2 New Chat

「新しいChat」によりBrowser Memoryが初期化された。

```text
Browser Memoryを初期化しました。ModelはReloadされません。
```

表示と実際のContractが一致している。Model LifecycleとConversation Lifecycleの分離も確認できた。

### 4.3 Send／Stop

- Send Buttonが動作した。
- Stop Buttonが動作した。
- `Ctrl+Enter`で送信できた。
- Current Web実装は`Cmd+Enter`にも対応する。

利用者がShortcutを発見できる表示がないため、Composer周辺に「`Cmd+Enter`／`Ctrl+Enter`で送信」等のHintを追加する候補とする。

### 4.4 Token Limit

User指定の254 Tokenで出力が切れることを確認した。Current Web Contractは1～2048を受け付ける。

Token上限到達と通常完了を区別し、最終回答前に上限へ到達した場合のWarningを維持する。

### 4.5 Language Separation

- UI Languageの日本語／英語切替が動作した。
- Response Languageの`ja／en／auto`切替が動作した。
- UI LanguageとResponse Languageは独立していた。

### 4.6 Summary Mode

Summary Mode `OFF／ON`が動作した。Summaryは同じMain ModelをSequentialに再利用するため、LatencyとToken Usageが増える注意事項を維持する。

## 5. Finding — Thinking Visibility

### 5.1 Observation

「推論過程を表示」をONにしても、推論過程が画面へ現れなかった。

### 5.2 Root Cause

Current Config：

```toml
[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
```

Web UIがRequestごとに送信するのは`thinking_visibility`であり、`thinking_mode`ではない。

Conversation ServiceはWeb Requestから`max_new_tokens`とPresentation Visibilityを変更するが、Thinking GenerationはApplication Defaultの`disabled`を維持する。

したがって、

```text
Thinking Generation   : disabled
Thinking Visibility   : visible
Generated Think Block : none
Visible Think Block   : none
```

となる。表示対象そのものが生成されていないため、CheckboxをONにしても何も出ない。

### 5.3 Assessment

Core Contract上は想定可能な状態であり、Parser／Presentation Failureとは断定しない。ただし、UI Labelだけを見ると「ONにすればThinkingが出る」と解釈しやすい。

### 5.4 Follow-up Requirement

- Thinking GenerationとThinking Visibilityを別設定として保持する。
- Generation OFFの場合、Visibility ControlをDisableするか「現在は生成されません」と表示する。
- 研究・開発者向け設定にThinking Generation `OFF／ON`を配置する候補とする。
- 一般利用者向けDefaultはGeneration OFF／Visibility Hidden候補とする。
- Raw Thinking非保存を維持する。
- Thinking内容を真の内部思考、正解または説明責任の完全な証拠として扱わない。

## 6. Finding — Markdown Presentation

### 6.1 Observation

Assistant OutputのMarkdown記号が、そのままPlain Textとして表示された。

### 6.2 Root Cause

Phase 1 Web UIは、XSSを避けるため`innerHTML`を使用せず、Messageを`textContent`で表示する。

既存Integration Testも次を要求している。

```text
innerHTML : absent
textContent : present
```

したがって、現状は意図した安全側のPhase 1実装である。

### 6.3 Follow-up Requirement

Assistant Outputを主要LLM Productに近いMarkdown表示へ発展させる。

- Rendering対象はAssistantのCanonical Contentとする。
- User InputはDefault Plain Textとする。
- Raw HTMLはDefault Disabledとする。
- Sanitizerまたは同等Allowlistを必須にする。
- Script、Event Handler、危険なURL Schemeを拒否する。
- Streaming中の不完全Markdownを安全に扱う。
- 初期候補はStreaming中をPlain Text、Completion後にMarkdown Renderingとする。
- Canonical ContentとRendered DOMを分離する。

SecurityとStreaming設計が必要なため、Default配置はPhase 4候補とする。

## 7. Follow-up — Message Copy

User MessageとAssistant MessageへCopy Buttonを追加する候補とする。

- UserはCanonical Input TextをCopyする。
- AssistantはCanonical Assistant ContentをCopyする。
- Rendered HTMLを無条件にCopyしない。
- Hidden Thinking、Metadata、非表示Original Summaryを混入させない。
- Copy成功／失敗Feedbackを表示する。
- 日本語／英語UI、Keyboard、Touchへ対応する。
- Clipboard内容のReadは行わない。

比較的小さい機能であり、Phase 1 Completionを遅延させない場合は前倒し可能である。

## 8. Lightning Linux x86_64 Pure CPU Follow-up

### 8.1 Existing State

既存File：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

既存Profileは次の状態である。

```text
compute_kind_key  : cpu
gpu_layers        : 0
build_variant_key : cuda
```

これはPure CPU Buildではなく、CUDA BuildのBackendをCPU実行するProfileである。

既存Setup ScriptもCUDA Buildの存在を検証し、未構築時はCUDA Toolkit／`nvcc`を必要とする可能性がある。

### 8.2 Requirement

Freshな最小CPU Studioでも再構築できるよう、Pure CPU RuntimeをCUDA Runtimeから分離する。

- GPU不要
- NVIDIA Driver不要
- CUDA Toolkit不要
- `nvcc`不要
- `gpu_layers = 0`
- CPU BuildであることをRuntime Observationへ記録
- Python 3.12系のSupport
- CPU専用Setup／Preflight／Acceptance
- Fresh Environment再構築
- Model Digest検証
- Bounded Smoke
- Latency／Memory／Token／Error記録

### 8.3 Candidate Artifacts

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

最終名称は既存CUDA CPU Execution ProfileとのMigrationを含めて決定する。

### 8.4 Acceptance Candidates

- NVIDIA DeviceがなくてもPreflightが通る。
- `nvcc`がなくてもSetupが完了する。
- BackendがCUDA Supportを必須にしない。
- DeviceがCPUとして観測される。
- `gpu_layers = 0`がEffective Configへ反映される。
- Qwen3-4B Q4_K_Mの短いGenerationが完了する。
- Cancel／Token Limit／LanguageがCPU環境でもContractどおり動作する。
- CPUの遅さをFailureと誤認せず、TimeoutとBounded Smokeを分離する。

## 9. Priority Proposal

```text
P0:
  Thinking Generation／Visibility状態の説明またはUI整合

P1:
  Shortcut Hint
  Message Copy
  Lightning Pure CPU Profile

P2:
  Sanitized Markdown Presentation
```

Markdown PresentationをPhase 1へ前倒しする場合も、SanitizerとStreaming Completion境界を省略しない。

## 10. Authorization Boundary

本文書はReview、要件整理および将来Handoff候補である。

次を自動許可しない。

- Web UI変更
- Markdown Library追加
- Copy Button実装
- Thinking Control変更
- Pure CPU Profile／Script実装
- Dependency Installation
- Model Download
- 外部環境操作
- Git／GitHub操作

実装開始時は、対象範囲、Phase GateおよびAcceptanceを確定した実装担当向けHandoffを別途作成する。
