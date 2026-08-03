# Git Existing Repository Continuity／Public Account Transition Decision

```yaml
document_id: git_existing_repository_continuity_and_public_account_transition_decision
phase: phase_1_ex
status: accepted_user_decision_recorded
created_at: 2026-08-02 14:20:24 JST
owner: 設計統括者役
decision_authority: user
personal_information_recording: excluded
```

## 1. 目的

本書は、Git未経験者が既存GitHub Repositoryの公開Historyを維持しながら、今後の更新主体を公開用GitHub Account `nazuna-research`へ移行するために、2026-08-02までに行った検討、方針変更、確定事項および後続設計項目を記録する。

本書には、個人名、個人Email、旧個人Account Handle、個人連絡先その他の個人識別情報を記載しない。

## 2. 検討の流れ

### 2.1 Git運用設計の開始

Phase 1-exのGit工程は、利用者がGit操作に不慣れであることを前提に、一つずつ説明・確認してから進める方針で開始した。

対象項目として、次を予約した。

- CLI認証方式：SSH／HTTPS
- Branch運用
- Commit Message規則
- Phase Tag規則
- BackupとCommit／Tag／Pushの順序
- Branch Protection
- Commit署名
- Existing Remote Historyの継承方法
- Rollback／Remote検証

### 2.2 Repository再作成案の検討

Contributor Attributionを公開用Identityだけへ整理する目的で、既存Repositoryを削除し、Sanitation済みのClean Root Commitから作り直す案を一時採用候補とした。

公開用GitHub Account `nazuna-research`を今後のCommit／Push主体として使用できる状態を整え、Repository-local Git IdentityとCommand Line Commitを使用する方向を確認した。一時RepositoryによるAttribution試験も候補としたが、必須工程にはしなかった。

### 2.3 Publication Sanitationの時点変更

Identity、Privacy、意図しないAffiliationおよび`.DS_Store`等の公開不要Artifactを目的とした全Project Scan／Cleanupは、通常開発のたびには実施せず、GitHubへ公開する単位のPreparation Gateで実施する方針へ変更した。

SanitationはWorking Treeだけでなく、Git Index、Commit／Tag Metadataおよび全Outgoing Commit Treeを対象とする。検出だけでは元Projectの変更・削除Authorityは成立せず、修正、削除、History操作およびPushはユーザーの明示承認を必要とする。

### 2.4 Existing Repository継承への最終変更

Repository削除・再作成案は撤回した。

理由は、既存Repositoryが少なくとも2026-07-27 JST時点で公開されており、その公開Historyと開発連続性を消すことが、Contributor表示の整理より大きな損失になるためである。正確な初回公開日時は未確定であるため、2026-07-27を厳密な初回公開日時としては断定しない。

既存Historyに過去のContributor Attributionが残ることを受容し、今後のCommit／Pushだけを`nazuna-research`へ統一する。

## 3. 確定方針

```text
Existing Repository:
  削除しない
  再作成しない
  既存公開Historyを継承する
  Contributor整理を目的としたHistory Rewriteを行わない
  Force PushでRoot Historyを置換しない

Future Updates:
  GitHub Accountはnazuna-researchを使用する
  Author／Committer／Taggerの公開Identityを統一する
  具体的な個人情報またはEmail値は本書へ記録しない

Visibility:
  当面未確定
  Public継続または将来Private化のどちらも候補
  Visibility変更は別途ユーザー承認が必要

Public Distribution:
  独自要素を選択的に除外した対外公開用Repositoryを別運用する
  既存RepositoryとHistory／Scope／責務を混同しない
```

## 4. Existing Historyを壊さず更新する準備

現在のLocal ProjectにGit Metadataが存在しない場合、次を禁止する。

- Remote History未確認のまま現在Project Rootを初期化して上書きPushする
- `--force`で既存RemoteのRoot Historyを置換する
- Existing Repositoryを削除して同名Repositoryを作り直す
- Contributor表示だけを目的にHistoryを書き換える

推奨する準備順序は次である。これは設計上の順序であり、本書作成時点では未実行である。

```text
1. User Backup完了を確認
2. CLI認証方式を決定
3. nazuna-researchで認証できることを確認
4. ユーザーが明示指定した別作業場所へExisting RepositoryをClone
5. Remote URL、Default Branch、HEAD、HistoryをRead-only確認
6. Repository-local Author／Committer Identityを設定
7. 現Projectの公開対象をAllowlistで選定
8. Clone側へ反映する差分を作成
9. Source／Docs／Test／Legal／SanitationをReview
10. Local Commit前にAuthor／Committer予定値を確認
11. Commit後にTree、Metadata、Parent Historyを確認
12. Backup／Tag／Push順序に従い、ユーザー承認後に通常Push
13. Remote History、Contributor、公開内容を再検証
```

Clone先の作成、Copy／同期、Git設定、CommitおよびPushは、ユーザーの個別承認なしに実行しない。

## 5. 将来Private化する場合

Existing RepositoryをPrivateへ変更すると、第三者が過去の公開状態を直接検証しにくくなる可能性がある。Private化を選択する場合は、実施直前に少なくとも次を保存候補とする。

- Repository URL
- 公開確認日時
- 基準Commit SHA
- 公開時点のSource Archive
- Artifact／ManifestのSHA-512
- 必要な公開画面Evidence
- Tag／Releaseを使用する場合はその識別子

これらは公開先行を絶対的に証明する単独手段とは扱わず、複数Evidenceの組合せとして保持する。

## 6. 次に順番に確定する項目

次工程は実操作ではなく、次のGit運用設計である。

1. CLI認証方式：SSH／HTTPS
2. Branch運用
3. Commit Message規則
4. Phase Tag規則
5. BackupとCommit／Tag／Pushの順序
6. Branch Protection
7. Commit署名：初期は任意
8. Existing Repository Clone／差分反映手順
9. Publication Sanitation／Push Gate
10. Rollback／Remote検証

各項目は、利用者が実行場所、Commandの意味、期待出力および失敗時の停止条件を理解できる粒度で順番に提示する。

## 7. Supersession

次の過去判断はHistoryとして保持するが、現在のRepository方針としては置き換える。

- Clean Root Commitから同名Repositoryを作り直す
- Existing Web Upload Historyを移行しない
- Contributor Attributionを単一化するためRepositoryを再作成する

次は継続する。

- Publication SanitationをGitHub公開単位で実施する
- Secret／CredentialをFail-closedで扱う
- `.gitignore`でLocal／Model／Cache／Secret候補を追跡対象外にする
- Author／Committer／Tagger／Push Accountを公開用Identityへ統一する
- Git／GitHub Mutationはユーザー最終Authorityとする

## 8. Current Mutation Boundary

```text
git init／clone／commit／tag／remote／push : NOT EXECUTED
Repository delete／recreate              : CANCELLED／NOT EXECUTED
Visibility change                        : NOT DECIDED／NOT EXECUTED
History rewrite／force push              : PROHIBITED／NOT EXECUTED
Docs update                              : THIS DECISION ONLY
```
