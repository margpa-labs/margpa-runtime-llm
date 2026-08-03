# ADR 0003 日本語Docsと担当別引き継ぎ

- 文書ID: `adr_0003_japanese_documentation_and_handoffs`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連ルール: [documentation_rules_20260718174637.md](../requirements/documentation_rules_20260718174637.md)

## Context

ユーザーは現時点で英語文書を読むことを前提にできない。

また、Projectでは次の担当タスクを分離する構想がある。

- 設計者役
- 実装者役
- 対外向けDocs作成者役
- その他の専門担当

タスクごとに長大な会話を再度貼り付ける負担を減らし、Docsを共通の引き継ぎ基盤として利用する必要がある。

## Decision

- Docsの正本言語を日本語とする
- 技術識別子や正式名称だけ英語を保持する
- `docs/`を要件・設計・判断・引き継ぎの正本とする
- `requirements`、`architecture`、`governance`、`adr`、`handoffs`へ分割する
- 各担当タスクは共通引き継ぎと担当領域文書を読む
- File名は英語Lower Snake CaseとTimestampを使用する
- 文書索引で現在の正本を指定する

## File Name

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

TimezoneはJSTとする。

同一Snapshotとして一括作成する文書は、同じ作成時刻を共有してよい。

## Consequence

Positive：

- ユーザーがDocsを直接確認できる
- 別タスクへの引き継ぎが容易になる
- DesignとImplementationの責務を分けられる
- 判断理由をADRとして保持できる
- GitHub公開用Docsの原稿として再利用できる

Negative／Risk：

- 英語利用者向けDocsは後から翻訳が必要
- 同じ主題のDocumentが増えると正本判定が難しくなる
- 古いHandoffが残ると矛盾する可能性がある

## Mitigation

- `documentation_index`でCurrent文書を指定する
- 状態を`current`、`superseded`等で明示する
- 実質的変更は新Timestamp Fileとして作る
- Handoffは正本へのLinkを持つ
- 英語版は日本語正本から派生させる
