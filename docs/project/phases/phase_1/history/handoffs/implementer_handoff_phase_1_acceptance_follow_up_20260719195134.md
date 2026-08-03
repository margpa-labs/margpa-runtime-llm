# 実装担当向け Phase 1 ユーザー受入Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1_acceptance_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1_acceptance_follow_up_requirements_20260719195134.md](../requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md)
- Known Issues: [known_issues_and_observations_20260719195134.md](../operations/known_issues_and_observations_20260719195134.md)
- supersedes: なし（新規Follow-up Handoff系列）

## 1. Current State

Phase 1-A～1-Eの実装ReviewはAcceptedである。User Acceptance Testで、機能破損ではないが改善すべき2件が確認された。

- CLI HelpのMetavar説明不足
- Hidden ThinkingがToken上限へ到達した場合の空表示

Phase 1 User Acceptance／Backup GateはFollow-upのDisposition確定までWaitingである。

## 2. 実装Scope候補

```text
src/margpa_runtime_llm/entrypoints/cli/
src/margpa_runtime_llm/modules/presentation/    # 必要最小限
src/margpa_runtime_llm/orchestration/           # Stop Evidence伝達に必要な場合
tests/
docs/handoffs/implementer_status_*
```

`config/`変更が必要な場合は、理由と対象を実装前に設計者／ユーザーへ返す。

## 3. Required Work

1. Helpの大文字が仮引数名であることを明示する。
2. `--profile`の正しい配置例をHelpから理解できるようにする。
3. Hidden Thinking＋Final未生成＋Token上限到達時だけSafe Warningを表示する。
4. False Positiveを防ぐUnit Testを追加する。
5. Default TestとNative Model Smokeを実行する。
6. 新Timestampの`implementer_status_*`を作成しReviewを依頼する。

## 4. Out of Scope

- Final Answer先頭空行のTrim
- Reasoning Language強制／翻訳
- Linux／Windows一般自動Routing
- Lightning AI Studio Profile
- UI、Governance、Auditの実装

## 5. 実装開始条件

このHandoffは準備済みだが、まだ開始指示ではない。ユーザーが実装担当Taskへ明示的にFollow-up実装を許可した時点で開始する。
