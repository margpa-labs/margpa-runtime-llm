# Phase 1 ユーザー受入Follow-up要件

- 文書ID: `phase_1_acceptance_follow_up_requirements`
- 状態: `proposed_waiting_implementation_authorization`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: CLI HelpとHidden Thinking Token上限診断
- 正本言語: 日本語
- User Test補足: [phase_1_user_acceptance_findings_20260719195134.md](../user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- Handoff: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- supersedes: なし（新規Follow-up系列）

## 1. Scope

実装候補は次の2件に限定する。

1. CLI Helpで大文字表記が仮引数名であることを説明する。
2. Hidden ThinkingがToken上限へ到達しFinal Answerを生成できなかった場合、Safe Warningを表示する。

Final先頭空行の正規化、Reasoning Language強制、一般Cross-platform完成は本Follow-upに含めない。

## 2. CLI Help要件

- Top-level、`generate`、`model-info`のHelpで、Usage中の大文字が実際の値へ置き換える仮引数名であると理解できること。
- `--profile`はSubcommand後へ置くことが分かること。
- `--profile PROFILE_PATH`のように意味のあるMetavarへ変更してよい。
- Optionの機能、値の例、Default／Sourceを過不足なく説明する。
- Help表示だけでModelをLoadしない。
- Helpの終了Codeは0を維持する。

## 3. Token上限Warning要件

- Thinking Executionが有効であること。
- Reasoningが非表示であること。
- Final Answerが生成されていないこと。
- Token上限到達を示す信頼できるStop Evidenceがあること。

上記を満たす場合だけ、Reasoning本文を含まないSafe Warningを表示する。

日本語の意味：

```text
最終回答を生成する前にToken上限へ到達しました。
```

要件：

- Raw Reasoningを表示しない。
- User Cancel、Model Error、正常な空回答をToken上限として誤分類しない。
- Streaming／Non-streamingの両方で意味が一致する。
- Warning出力先とExit CodeをTestで固定する。
- Model PortのCanonical OutputをPresentation都合で書き換えない。
- `--max-new-tokens`増加等の利用者向け対処をManualへ記載する。

## 4. Acceptance Criteria

- CLI Help Testが追加される。
- Correct／Incorrect `--profile`順序のBehaviorが維持される。
- Hidden Thinking＋Token上限でSafe Warningが出る。
- Hidden Thinking＋Final到達時はWarningが出ない。
- Visible Thinking、Thinking Disabled、Cancel、Errorで誤Warningが出ない。
- Default Test、Model Smoke、Ruff、MypyがPassする。
- 実装者Statusと設計者Reviewを新Timestampで作成する。

## 5. Authorization Boundary

本書とHandoffの作成だけでは実装開始を許可しない。ユーザーが実装担当へFollow-up開始を指示した後にSource／Testsを変更する。
