# Phase 1 ユーザー受入テスト補足

- 文書ID: `phase_1_user_acceptance_findings`
- 状態: `current_supplement`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: Phase 1 macOSユーザー受入テストで判明した操作上の補足
- 正本言語: 日本語
- 基本文書: [phase_1_macos_user_manual_20260719171836.md](phase_1_macos_user_manual_20260719171836.md)
- Known Issues: [known_issues_and_observations_20260719195134.md](../operations/known_issues_and_observations_20260719195134.md)
- supersedes: なし（基本Manualを置き換えない補足文書）

## 1. CLI Helpの大文字表記

Helpに表示される次のような大文字は、文字列をそのまま入力する指定ではない。

```text
--profile PROFILE
--model-root MODEL_ROOT
--max-new-tokens MAX_NEW_TOKENS
```

`PROFILE`、`MODEL_ROOT`、`MAX_NEW_TOKENS`等は、利用者が実際の値へ置き換える仮引数名である。

また、`--profile`等の共通OptionはTop-level Commandの前ではなく、`generate`または`model-info`の後ろに指定する。

正しい例：

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/local_macos_arm64.toml
```

```bash
./.venv/bin/margpa-llm generate \
  --profile config/profiles/local_macos_arm64.toml \
  --prompt "こんにちは"
```

誤った例：

```bash
./.venv/bin/margpa-llm --profile PROFILE
```

CLI Help自体にも、この仮引数規則と各Optionの説明を追加するFollow-upを行う。

## 2. Thinkingの意味とDefault

`--thinking`は、Modelに`<think>...</think>`形式の内部Reasoning出力を生成させる指定である。

`<高度推論>...</高度推論>`は、そのReasoningを利用者へ表示する場合のPresentation Labelであり、別の推論処理ではない。

通常利用では次をDefaultとする現在の設計が妥当である。

```text
Thinking Execution : disabled
Thinking Visibility: hidden
Persistence        : disabled
```

## 3. Hidden ThinkingとToken上限

Thinkingを有効にして非表示にした場合、ModelがReasoningだけでToken上限へ到達し、Final Answerを生成できないことがある。

```text
Thinking生成
  → Token上限到達
  → Closing／Final未生成
  → ReasoningはHidden
  → CLI表示が空になる
```

`--max-new-tokens 1024`へ増やすとFinal Answerまで生成できることをユーザー環境で確認した。

これはReasoning漏洩やParser故障ではない。ただし空出力だけでは原因が分からないため、次の意味のSafe Warningを追加する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

## 4. Final Answer先頭の空行

`</think>`直後にModelが生成した改行をCurrent Parserが保持するため、Hidden ThinkingのFinal Answer先頭に空行が残る場合がある。

Raw Output保持方針による現象であり、Phase 1の重大問題ではない。UI／Presentation層における表示正規化候補として後続対応へ延期する。

## 5. 表示したReasoningの言語

`--response-language ja`はFinal Answerを日本語へ誘導するが、表示対象のRaw Reasoningまで日本語へ強制しない。Qwen3は日本語PromptでもReasoningを英語で生成する場合がある。

Phase 1-EではStrict Language EnforcementをScope外としている。後続で次を比較検討する。

- Model固有のReasoning Language Instruction
- `reasoning_language`設定
- Model交換
- 表示用翻訳

小型ModelではPrompt指定だけによる完全保証を主張しない。

## 6. Cross-platformの現在地

Current RuntimeはOS／Architectureを自動検出し、登録済みDefault Profileを選択する。未登録PlatformをMac Profileへ黙ってFallbackせず、安全に停止する。

一方、Linux／Windowsで実際に自動実行するProfile、Native Build、実機検証は未完了である。一般的なLinux／Windows自動対応は、後続Phaseへ延期する。

これはApplication Coreの後続機能をBlockしない。既存のDeployment Profile、Registry、Model Port、Capability境界を維持し、環境追加時に主としてProfile、Registry、Setup Recipe、Platform Testへ差分を閉じ込める。

ただし、同じLinux x86_64でもCPU、NVIDIA CUDA、AMD ROCm等が存在するため、全Hardwareを自動選択する完成形はConfig Fileの追加だけではない。Hardware／Acceleration検出と選択方針が必要になる。

## 7. User Acceptanceへの影響

- CLI仮引数説明とToken上限WarningはPhase 1 Acceptance Follow-up候補とする。
- Final先頭空行、Reasoning言語、一般Cross-platform完成はAccepted Deferredとする。
- Follow-up実装を行った場合、変更箇所とUser Manual該当項目を再検証してからPhase 1完了判定を行う。
