# Post-generation Summary Mode 要件予約

- 文書ID: `post_generation_summary_mode_requirements_reservation`
- 状態: `accepted_deferred_to_phase_1g_follow_up`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Phase 1-G最小UI成立後の小規模Follow-up
- 正本言語: 日本語
- 最新Index: [documentation_index_20260721090725.md](../documentation_index_20260721090725.md)
- supersedes: なし（Post-generation Summary Mode要件系列の初回）

## 1. Decision

ユーザー向けOptionへ次を追加する。

```text
要約モード  OFF／ON
```

初期値はOFFとする。ONの場合、Main Modelが生成した最終回答をそのまま表示せず、同じMain Modelによる2回目の要約生成を通してから表示する。

本機能はPhase 1-Fへ混在させない。Phase 1-Gの最小UIを先に成立させ、その直後の小規模Follow-upで実装する。

## 2. Initial Runtime Values

```text
通常生成 max_new_tokens : 2048
要約生成 max_new_tokens : 1024
要約時Thinking          : disabled
要約Backend              : Main Model
実行方式                 : Sequential／同時常駐なし
```

要約生成を2048にしない主な理由は、Current `context_size = 4096`の中に元回答、System／要約指示、要約出力を収める必要があるためである。

要約時はThinkingを無効化し、Reasoning Token消費によって最終要約が出ない危険を抑える。

## 3. Processing Flow

```text
User Request
  → Normal Generation／max 2048
  → Canonical Final Answer抽出
  → Summary Request構築
  → Same Main Model／Thinking disabled／max 1024
  → Summary Result Validation
  → User Presentation
```

要約対象は、通常生成のCanonical Final Answerだけとする。

次は要約対象にしない。

- Model Generated Thinking／Reasoning Segment
- 生のChain of Thought
- Runtime内部状態
- System Prompt
- Governance内部Evidence

## 4. UI Requirement

一般UIへ、通常設定として次を追加する。

```text
要約モード  [ OFF | ON ]
```

- 一般利用者には単純な横スライド型ON／OFF Switchとして表示する。
- OFFがDefaultである。
- ONは内部の`post_generation` Modeへ変換する。
- 要約生成中は、通常生成と区別できるStatusを表示する。

表示例：

```text
回答を生成しています
  → 回答を要約しています
  → 完了
```

将来の研究開発者向け設定では、Backend、Token上限、失敗時Policy等を表示可能にする。

## 5. Configuration Candidate

初期候補：

```toml
[layers.summarization]
mode = "off" # off | post_generation
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
```

一般UIのBooleanはConfigへ直接Booleanとして固定せず、内部Modeへ変換する。将来、別の要約方式や専用Modelを追加可能にするためである。

## 6. Architecture Boundary

SummarizationはPresentation上の文字列短縮ではなく、追加Inferenceを伴うResponse Transformation Layerとして扱う。

```text
Application／Generation Pipeline
  → Summarization Port
      └─ Initial Adapter: Main Model再利用
      └─ Future Adapter : Dedicated Summary Model
  → Presentation
```

- Main Model固有処理をApplication Coreへ入れない。
- 要約Modelを将来交換可能にする。
- Main Modelと別Modelを同時常駐させることを初期要件にしない。
- ConfigでLayer単位にOFF／ON相当を切り替え可能にする。

## 7. Original Answer Preservation

要約前のCanonical Final Answerは破棄しない。

- 将来のAudit Logへ元回答と要約回答を別Artifact／Eventとして記録できる。
- UIでは将来「元の回答を表示」を追加可能にする。
- 要約による欠落、歪み、過剰短縮を比較可能にする。
- 元回答をユーザーへ常時表示することは初期必須ではない。
- Model Generated ThinkingはOriginal Answer Preservationの対象外とする。

## 8. Failure／Token Handling

- Summary Callが失敗した場合、元回答を警告付きで表示する。
- Summary Outputが空の場合、元回答へFallbackする。
- `finish_reason=length`を検出し、要約が上限へ到達した事実を隠さない。
- 元回答自体がToken上限へ到達している場合、そのWarningを要約後も維持する。
- Context残量が不足する場合、設定値を黙って超過させない。
- Effective Summary Token上限は、将来Prompt TokenとSafety Marginから動的に縮小可能にする。
- Cancellationは通常生成中と要約生成中の両方で成立させる。

## 9. Streaming

初期版では、要約モードON時に元回答をStreaming表示しない。

```text
通常生成中 : Statusのみ表示
要約生成中 : 要約結果をStreaming表示可能
```

元回答を先に表示してから要約回答へ置換すると、表示内容が突然変化し、保存対象も曖昧になるため初期版では採用しない。

## 10. Out of Scope

次は本機能と分離する。

- ユーザー入力の生成前要約
- 会話履歴の自動圧縮
- RAG Contextの要約
- ARGD／DAGDによる要約許可判定
- Dedicated Summary Modelの初期同時常駐
- 要約品質のLLM-as-a-Judge評価

入力や会話履歴の生成前要約は、前提・決定事項・入力構造を失う危険があるため、将来のContext Managementとして別途設計する。

## 11. Acceptance Direction

将来実装時は最低限次を確認する。

- OFF時は追加Inferenceが発生しない。
- ON時は通常生成と要約生成が各1回だけ発生する。
- 要約時Thinkingが無効である。
- 要約上限が1024である。
- 元回答と要約回答が混同されない。
- 要約失敗時に元回答へ安全にFallbackする。
- Cancelが両段階で成立する。
- Model Adapter交換性を壊さない。

## 12. Authorization Boundary

本書は要件予約であり、Phase 1-F Source／Config／UIの変更を許可しない。実装はPhase 1-G最小UI Accepted後の別Handoffにより開始する。
