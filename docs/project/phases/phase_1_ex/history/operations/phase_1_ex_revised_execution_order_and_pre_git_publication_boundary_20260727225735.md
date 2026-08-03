# Phase 1-ex 実行順変更／Git未使用掲載境界 Record

```yaml
document_id: phase_1_ex_revised_execution_order_and_pre_git_publication_boundary
status: accepted_not_executed
language: ja
created_at: 2026-07-27 22:57:35 JST
owner: 設計統括者役
phase: phase_1_ex
git_operation_performed: false
external_publication_performed: false
```

## 1. 目的

ユーザー決定に基づき、Phase 1-exの残工程順を変更する。

本Recordは順序と境界を記録するものであり、Git初期化、Commit、Remote設定、Push、GitHubへのFile投入、Public Demo匿名公開または外部Service変更を許可・実行するものではない。

## 2. 正規化した実行順

ユーザー原文では番号`4`が二度使われている。内容と前後関係は変更せず、参照時の曖昧さを避けるため、Docs上では次の10段階へ正規化する。

### Stage 1 — Git未使用のGitHub掲載準備／一時掲載

- GitHubへ掲載するための準備を行う。
- 今回はGitを使用しない。
- 詳細手順と掲載対象は、これからユーザーが指示する。
- 準備完了後、一度この時点の成果をGitHubへ掲載する。
- 本Record作成時点では、準備・掲載とも未実施である。

### Stage 2 — Public Demo

1. Basic認証Previewとは分離したPublic Demo基盤を実装する。
2. この時点では匿名公開を有効化しない。
3. Public Demoの最終確認を行う。
4. 合格後、ユーザーの明示判断により匿名公開を有効化する。

Public Demoの最低境界：

- 認証なし
- Rate Limit
- 生成Token上限
- Cost／Resource保護
- Tool無効
- RAG無効
- 外部操作無効
- Basic認証Previewとの設定・Lifecycle・Access Profile分離

追加保護は要件・工数・現行Runtimeとの整合を確認して決める。上記だけで安全性や可用性を保証したと扱わない。

### Stage 3 — Mac限定簡易Documentation RAG

- Mac実機を対象に簡易Documentation RAGを実装する。
- 将来のLightning、Home Server、Cloud等へ接続できるExternal Hookを維持する。
- Public DemoではRAGを無効とする。

### Stage 4 — Git運用設計

- Branch規則
- Tag規則
- Commit規則
- Author／Email
- Remote／公開Repository
- Phase BackupとCommit／Tag／公開Snapshotの対応

### Stage 5 — Git初期化／公開Sanitation

- `.gitignore`
- `.gitattributes`
- Model／Secret／Cache等の除外
- Privacy／Secret／Identity Scan
- LICENSE方針の再確認
- 初回Commit直前までの準備
- ユーザー原文上、このStage末尾に含まれるGitHub公開

このStageでは、初回Commitをまだ作成しない。

### Stage 6 — Docs必要箇所の再整理

- 新しい実装・検証・運用決定を反映する。
- 必要な文書・箇所だけを再整理または新規作成する。
- Phase 1-ex Final Lossless Compilationと設計統括者役Recovery情報を、初回Commit前に最新化する。
- Stable更新前後の完全SnapshotとAppend-only Indexを保持する。

### Stage 7 — 全体Review／Test／Privacy Scan

- Source／Config／Test／Docs／Link／Hashの全体Review
- Runtime Test
- Public Allowlist確認
- Privacy／Secret／Identity Scan
- Model Weight、Credential、Cache、Log、Backup等の除外確認
- 初回Commit可否判定

### Stage 8 — 初回Commit

Stage 1～7の必要Gateに合格し、ユーザーが明示的に許可した後に初回Commitを作成する。

### Stage 9 — Phase 1-ex Backup

Phase 1-ex完了条件、ユーザーAcceptance、設計統括者役Recovery更新および復元検証を満たした後、Phase Backupを取得する。

### Stage 10 — Phase 2

Phase 1-exの完了宣言とPhase 2着手可能宣言後にPhase 2へ進む。

## 3. GitHub掲載とGit履歴の境界

本順序には、Stage 1の「Gitを使わない一時掲載」、Stage 5の「Git初期化／GitHub公開との対応」およびStage 8の「初回Commit」が併存する。

これらを設計統括者役の判断で統合、削除、前後入替または実施しない。少なくとも次をStage 4のGit運用設計で明示する。

- Stage 1掲載物の位置付け
- Stage 1掲載物と後続Git Repositoryの履歴関係
- Stage 5の「GitHub公開」が準備、差替えまたは正式公開のどれを意味するか
- 初回CommitとRemote公開の正確な順序
- Stage 1掲載物を残すか、後続Snapshotへ置換するか
- Rollback、Backup、Commit、Tagおよび公開時点の対応

不明なまま外部変更を行わない。

## 4. 現在の次工程

次工程はStage 1である。

ただし、掲載対象、除外対象、操作方法、GitHub側の配置および完了条件は、今後のユーザー指示を待つ。現時点のDocs更新だけをもって、GitHub掲載準備完了または公開済みとは扱わない。

## 5. 保持する既存Gate

順序変更によって、次を削除しない。

- Public DemoとBasic Previewの分離
- Public Demo匿名公開前の最終確認
- Mac限定RAGのExternal Hook
- Public DemoでのRAG／Tool／外部操作無効
- Phase 1-ex Final Lossless Compilation
- Design Governance Recovery Manifest
- 全体Review／User Acceptance
- Phase Backup
- Git／外部公開に対するユーザーの明示許可
