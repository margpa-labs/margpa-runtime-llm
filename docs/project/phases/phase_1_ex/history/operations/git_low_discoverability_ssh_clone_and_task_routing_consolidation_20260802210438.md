# Git Low-discoverability／SSH／Clone／Task Routing Consolidation

```yaml
document_id: git_low_discoverability_ssh_clone_and_task_routing_consolidation
phase: phase_1_ex
state_at: 2026-08-02 21:04:38 JST
status: accepted_current_state
language: ja
owner: 設計統括者役
source: user_confirmed_manual_github_ssh_and_clone_evidence
contains_personal_data: false
```

## 1. 目的

本Recordは、Root公開面の低発見性調整、Existing Repository継続、Git用認証経路、既存History Clone、Working Tree Clean復旧および作業実行面のRouting方針を、個人情報・Credential・個人Pathを含めず一つに整理する。

## 2. Root公開面の低発見性調整

先行公開性とExisting Historyは維持しつつ、Repository Landing Pageおよび一般検索からの偶発的発見性を抑える運用を採用した。

実施済み境界：

```text
Topics            : none
About Description : empty
Website           : empty
Social Preview    : none
GitHub Pages      : unused
External Links    : intentionally absent
```

RootではREADME、LICENSE、NOTICEおよびTERMS_OF_USEを低発見性版へ更新し、`CITATION.cff`をDefault BranchおよびLocal Currentから削除した。削除前の`CITATION.cff`とRoot 4文書はHistory／ユーザーBackupに保持され、OSS化または再公開時に再評価・復元できる。

`CITATION.cff`削除はMachine-readable Citation UIと発見導線を減らすが、Existing Commit History、Repository作成・公開時点、Archive、Hash、Screenshotその他のEvidenceを消さないため、先行公開性への影響は限定的である。厳密な法的証明を単独で保証するものではない。

## 3. 変更範囲

Root公開面の対象は次の5 Artifactに限定した。

```text
README.md
LICENSE
NOTICE.md
TERMS_OF_USE.md
CITATION.cff  # removed from Current／Default Branch
```

同時期に追加・更新されたPhase 1-ex配下の文書は、Runtime／Source変更ではなく、公開面調整、Git方針、History SnapshotおよびAppend-only Indexの監査Evidenceである。

## 4. Existing Repository Continuity

Repository削除・再作成、Contributor表示の単一化を目的としたHistory RewriteおよびForce Pushは行わない。既存Historyと先行公開状態を保持し、今後の更新は公開研究Identityへ統一する。

Historical Contributor Attributionが残ることは受容し、それを除去するためにRoot Commitを置換しない。Public継続／将来Private化は未決定である。Private化する場合は、変更前に公開URL、確認日時、基準Commit、Archive、SHA-512 Manifestおよび必要な画面Evidenceを保存する。

独自要素を選択的に除外した別の対外Distributionは、Existing Repositoryと履歴・Scope・責務を混同しない。

## 5. Git認証経路

GitHub用の専用SSH IdentityとHost Aliasをユーザー管理領域へ作成し、次を確認した。

```text
Git Client               : available
OpenSSH                  : available
Dedicated Identity       : configured
Private Key Permission   : restricted
SSH Config Permission    : restricted
GitHub Authentication    : pass
Remote Read-only Query   : pass
Private Key／Passphrase  : not displayed／not recorded
Personal Email           : not recorded
```

GitHubのSSH TestがShell Access非提供を示す非0 Exitを返しても、Authentication成功Messageが成立していれば異常とは扱わない。Remote Read-only Queryの成功を別に確認する。

## 6. Existing Repository Clone

Original ProjectにはGit Metadataを追加せず、ユーザーが明示指定した別のGit Staging CloneへExisting RepositoryをCloneした。

確認結果：

```text
Original Git Metadata : absent
Clone Branch          : main
Clone HEAD            : 55e0ab854db07212dce987d1a7d7c4e43e2b63c6
Expected HEAD Match   : yes
Remote HEAD           : resolved
Git fsck              : pass
Remote URL            : approved SSH alias route
Original Files Copied : none
Git Config Changed    : none
Commit／Tag／Push      : none
```

Clone直下でmacOS由来の可能性がある未追跡`.DS_Store`を1件検出した。生成経路は断定せず、ユーザー承認済みのExact PathだけをRecoverableにTrashへ移動した。移動後、Clone Working TreeはClean、HEAD一致、Remaining Issueなしを確認した。

`.gitignore`はこのCleanupのために変更していない。Original ProjectのCurrent `.gitignore`は、後続のSource→Target Integration Manifestで他の公開対象差分とともにReviewする。

## 7. 現在の停止点

```text
SSH Setup                    : PASS
Existing Repository Clone    : PASS
Clone Integrity              : PASS
Clone Working Tree           : CLEAN
Original→Clone Copy          : NOT STARTED
Read-only Delta Inventory    : NEXT
Source→Target Integration    : NOT AUTHORIZED
Commit／Tag／Push             : NONE
```

次はCloneのGit MetadataとOriginal ProjectをRead-only Work Treeとして組み合わせ、Tracked Modified、Clone-only Tracked、Original-only Git Candidate、Ignored Local-only ArtifactおよびSymbolic Linkを分類する。Recursiveな単純Diffで`.venv`やModelを走査しない。

## 8. Task Routing決定

Codex利用可能量、Cloud Credit、ユーザー操作時間および再説明Costを抑えるため、次を共通運用とする。

```text
設計統括者役:
  方針、Contract、Authority、Handoff、Review、例外判断

Codex実装者役:
  Source／Test／Script／Configの実装、複数File変更、Repository整合

通常GPT＋ユーザー手動:
  確定Command、Read-only調査、External UI、配置／Permission／Hash確認

Script:
  繰り返す定型作業、Preflight、Lifecycle、Evidence収集
```

通常GPTへ渡す作業は、Exact Target、許可Action、禁止Action、期待結果、停止条件およびEvidence Handoffを設計統括者役が先に固定する。失敗時に通常GPTが推測修復せず、結果を返して設計統括者役へ戻す。

## 9. Privacy Boundary

本Recordには、個人名、個人Account Handle、個人Email、Private Key、Passphrase、Credential、個人Home Directoryおよびローカル絶対Pathを記録しない。公開運用に必要なProject Identity、Logical Role、Repository継続方針およびCommit SHAだけを保持する。

## 10. Acceptance

```text
Low-discoverability Root Surface : ACCEPTED／MANUALLY APPLIED
CITATION Current Removal          : CONFIRMED
Existing History Preservation     : ACCEPTED
Dedicated SSH Route               : ACCEPTED
Git Staging Clone                 : ACCEPTED
Clone Cleanup                     : ACCEPTED／RECOVERABLE
Task Routing／Cost Control         : ACCEPTED
```

次工程はRead-only Delta Inventoryである。結果を設計統括者役がReviewするまで、Original→Clone Copy、Delete、Git Add、Commit、Tag、Push、Merge、History RewriteまたはRemote変更を行わない。
