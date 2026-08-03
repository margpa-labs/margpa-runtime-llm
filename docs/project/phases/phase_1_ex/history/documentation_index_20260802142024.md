# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260802142024
state_at: 2026-08-02 14:20:24 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260802073901.md
  - operations/git_existing_repository_continuity_and_public_account_transition_decision_20260802142024.md
  - ../../../shared/operations/git_publication_sanitation_policy_ja.md
supersedes: documentation_index_20260802073901.md
source: user_existing_repository_history_preservation_and_public_account_transition_decision
personal_information_recording: excluded
```

本Snapshotは[2026-08-02 07:39:01版](documentation_index_20260802073901.md)までの全状態を継承し、Repository再作成案の撤回、Existing Remote History継承、公開用GitHub Account `nazuna-research`への今後の更新主体移行および後続Git運用設計順序をAppend-onlyで記録する。

本Snapshotおよび今回の新規決定記録には、個人名、個人Email、旧個人Account Handle、個人連絡先その他の個人識別情報を記録していない。

## 1. Decision Transition

```text
Previous Candidate:
  Contributor Attributionを単一化するためRepositoryを削除・再作成
  Clean Root Commitから開始

Current Accepted Direction:
  Existing Repositoryを削除・再作成しない
  Existing Remote Historyを継承する
  Contributor整理を目的としたHistory Rewrite／Force Pushを行わない
  Future GitHub Accountはnazuna-research
  過去のContributor AttributionはHistoryとして受容
```

Repository再作成案は過去の検討記録としてHistoryに残すが、現在の実施方針としては失効した。

## 2. Publication Time Boundary

Existing Repositoryは少なくとも2026-07-27 JST時点で公開されていたものとして扱う。ただし、正確な初回公開日時は未確定であり、2026-07-27を厳密な初回公開日時とは断定しない。

公開Historyと開発連続性を保持することを、Contributor表示の単一化より優先する。

## 3. Repository Scope

```text
Existing Repository:
  研究開発Historyを継承
  Public継続／将来Private化は未確定

Separate Public Distribution:
  独自要素を選択的に除外した対外公開用Repository
  Existing RepositoryとはHistory／Scope／責務を分離
```

既存RepositoryをPrivateへ変更する場合は、Visibility変更前に公開状態のEvidenceを保存する。候補はRepository URL、公開確認日時、基準Commit SHA、Source Archive、SHA-512 Manifestおよび必要な画面Evidenceである。

## 4. Existing History継承手順の方向

Local ProjectにGit Metadataがない状態で、現在Project Rootを即時初期化してRemoteへ上書きする方式は採用しない。

```text
User Backup
  → CLI認証方式決定
  → nazuna-research認証確認
  → ユーザー指定の別作業場所へExisting RepositoryをClone
  → Remote History／HEAD確認
  → Repository-local Identity設定
  → Current Projectの公開対象差分をAllowlist反映
  → Review／Test／Sanitation
  → Local Commit Metadata／Parent History確認
  → Backup／Tag／Push規則に従い通常Push
  → Remote再検証
```

作業場所作成、Clone、Copy、同期、Commit、Tag、RemoteおよびPushは未実行であり、ユーザーの個別承認を必要とする。

## 5. Next Design Sequence

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

各項目は、実行場所、Commandの意味、期待出力および失敗時の停止条件を含め、順番に確定する。

## 6. Canonical／History

- [Accepted Decision Record](operations/git_existing_repository_continuity_and_public_account_transition_decision_20260802142024.md)
- [GitHub Publication Sanitation Policy](../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [GitHub Publication Sanitation Policy Before](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_before_repository_continuity_decision_ja_20260802142024.md)
- [GitHub Publication Sanitation Policy After](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_after_repository_continuity_decision_ja_20260802142024.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_repository_continuity_decision_ja_20260802142024.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_repository_continuity_decision_ja_20260802142024.md)

## 7. Integrity

```text
Previous Documentation Index:
  138439c137f0693dd35499f8709c3945fa87ce7325d1ca497225f6c90c340e5d17a1015375680734d758c25ee38b7edefbc458cd8d2219601069d6ce83eb4045

GitHub Publication Sanitation Policy Before:
  ea3d60904a971cf8f343636734cdccc7a85a0045b7622ebf02d5d01ff4793bdf3df42a5fee9a92901c6b290da30752f4bbf975c23751c143fafc4a7d95ff5fc7

GitHub Publication Sanitation Policy Stable／After:
  20397252dea53ef74a644391b4f15ff292afa459fc88b118224dbac7c11bea721d0026a706f5702341b69f1a0a2568fec1d742f3daea8c3de1cb277f9205a6dc

Accepted Decision Record:
  f78c886656806e3b52f7dbc338da75889d3a591addc307d4a8fcb17b97c866ba3cbd9753ec96867cfb514440a652f38f138b6eb4e6276d91ba775956e71ceba0

Phase Index Before:
  3104eae9d551e2d88c62499b7480adddcdc86f86938da650c2013bd7191e6c475f61aae6946526e08db42606159d24eb03de060566b3766099b45adcdc2b8890

Phase Index Stable／After:
  15adea35b8bcc38c54f2a2c8c13f8fcde087500e761aa0140b192e7a37b4b74c044c5129413a023367a81fbe09d121ed6e72f87caf7ce4b687de4ccd52f23561

.gitignore unchanged:
  4d104e1264c06923c7f3f3732ea4808681c9e90d5fa2d568377dd9bec59d0e8b7fd58d15353388568e89fbfb5987c3d8dc5ab34ac7e51bc3c63fd346b476f6c3
```

Stable文書と対応After SnapshotのSHA-512一致を確認する。

## 8. Mutation Boundary

```text
Git／GitHub Operation              : NONE
Repository Delete／Recreate       : CANCELLED／NONE
Visibility Change                 : NONE
Clone／Copy／Sync                  : NONE
Commit／Tag／Remote／Push          : NONE
History Rewrite／Force Push       : NONE
Source／Config／Script／Test Change: NONE
Docs Change                       : Policy／Decision／Phase Index／Snapshot only
```
