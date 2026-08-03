# Phase 1-ex 運用再整備 要件プレースホルダー

- 文書ID: `phase_1_ex_operations_reorganization_requirements`
- 状態: `requirements_pending`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- supersedes: なし

## 1. 確定事項

Phase 1と初回GitHub公開の間に、次を追加する。

```text
Phase ID : Phase 1-ex
Name     : 運用再整備
State    : Added／Requirements Pending
```

Phase 1-ex完了後に初回GitHub公開を行う。Phase 1-ex前の状態は初回公開しない。

## 2. 現時点の目的

- Phase単位BackupとGitHub履歴の対応を整える
- 公開前Sanitationを再現可能にする
- 公開Identity、Path、Secret、Archive境界を固定する
- Git／GitHub運用、Release単位、証跡を整える
- 今後の各Phaseで同じ運用を反復可能にする

## 3. 未定義事項

次は後続の要件定義で決める。

- Git初期化、Branch、Commit、Tag、Release方式
- Repository Visibilityと公開範囲
- Backup生成／Sanitation Scriptの要否
- Manifest／Receipt Schema
- GitHubへ含めるDocs／Public Docs境界
- README、License、Copyright
- CI、Release Check、Secret Scanの範囲
- Phase 1-exのUser Manualと受入条件
- 担当Task間の実行順序

## 4. 完了条件

現時点では未定義である。詳細要件確定前にPhase 1-ex完了を宣言しない。

少なくとも、運用文書、公開対象Inventory、Privacy Gate、Backup／GitHub対応、復元・検証手順がAcceptedであることを将来の候補条件とする。

## 5. Authorization Boundary

本書はPhase 1-exの存在と配置を確定するだけであり、実装、File変更、Backup生成、Git初期化、Commit、Remote作成、Push、GitHub公開を許可しない。

