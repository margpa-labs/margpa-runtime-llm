# GitHub Publication Sanitation Policy

```yaml
document_id: git_publication_sanitation_policy
status: current_effective
language: ja
created_at: 2026-08-02 07:39:01 JST
updated_at: 2026-08-04 11:17:44 JST
owner: 設計統括者役
decision_authority: user
applies_to: git_commit_and_push_preparation
default_outside_gate: no_scan_no_delete
failure_policy: block_push
```

## 1. 目的

本書は、第一者の旧個人Account Handle、作者の個人情報その他の識別可能情報、意図しない組織名、`.DS_Store`等のOS Metadataおよび公開不要Artifactについて、検査・分類・除外・削除を行う時点をGit Commit／Push Preparation Gateへ限定する共通運用を定める。

本決定は、通常開発、通常Review、Phase途中のDocs更新および日常的なLocal実行のたびに同一の広範Scanや削除を繰り返さないためのScope／Cost統制である。

## 2. User Decision

2026-08-04以降、Gitの通常Commit／Push経路が成立したため、次の広範な確認および公開用除外作業は、CommitまたはPushを行う作業単位でだけ実施する。

- 第一者の旧個人Account Handle
- 作者の氏名、個人Email、個人連絡先、個人Profile等
- その他、個人または特定主体を不必要に識別できる情報
- 意図しないOrganization／Company／Affiliation表記
- `.DS_Store`、`__MACOSX/`、Cache、Temporary Artifactその他の公開不要物

通常開発中に、上記だけを目的とした全Project再帰Scan、名称置換、削除またはCleanupを定例実行しない。Docs作成、通常Review、Test、Phase途中のBackup、Task Handoffまたは設計更新のたびに、同じPrivacy／Secret／不要物の広範Scanを繰り返さない。

例外は、Secret混入の疑い、意図しないFile生成、対象Pathの違和感、Incidentまたはユーザーの個別指示がある場合の限定的なRead-only確認である。この例外を、平常時の全Project Scanへ拡張しない。

## 3. 「Commit／Push時」の正確な意味

Gitでは、一度Commitへ含めた情報をWorking Treeから消しても、Local Historyと将来のPush対象Historyに残る。したがって、広範SanitationはCommit前Gateで実施する。CommitとPushを同じ作業単位で行う場合は一連のGateとし、Local Commit後にPushを延期した場合は、後日のPush前にOutgoing Commit Range／Tree／Metadataを再確認する。本書の「Commit／Push時」は、送信Command直前のWorking Treeだけを意味しない。

```text
GitHub Publication Unitを確定
  → Push対象Range／Root Commitを固定
  → Working Tree、Index、Commit Metadata、全Outgoing Commit TreeをRead-only Scan
  → Candidateを分類
  → 必要な除外・修正案を提示
  → ユーザー承認
  → Public Tree／CommitをCleanに確定
  → 再Scan
  → Push対象SHAを提示
  → ユーザー最終承認
  → Push
  → Remote再検証
```

初回公開では、Sanitation合格前に公開予定Root Commitを作らない。後続公開では、Remoteの既公開SHAからPush予定HEADまでの全Outgoing Historyを検査対象とする。

## 4. Scan Scope

最低限、次を検査する。

- Gitで追跡される全Path
- Commit Author／Committer／Tagger NameとEmail
- Commit Message、Tag MessageおよびCo-author Trailer
- README、Docs、Config、Package Metadata、License、Notice、Citation
- Sample、Fixture、Log、Screenshot MetadataおよびGenerated Artifact
- Symbolic Linkそのものと公開Tree上のLink情報
- `.gitignore`／`.gitattributes`適用結果
- 初回PushではRoot Commitの全Tree
- 後続Pushでは全Outgoing CommitのTreeとMetadata

Local Working Treeの現在状態だけを見て合格判定しない。

## 5. Classification

検出文字列を一括置換しない。次へ分類する。

```text
approved_first_party_identity:
  Nazuna Research
  margpa-labs
  承認済みRepository URL／Project名

required_third_party_attribution:
  Model、Library、Platform、License、研究Source等の正式名称
  削除禁止。必要なAttributionを維持

unintended_personal_identifier:
  個人名、個人Email、個人連絡先、個人Profile、個人Path等
  Public Treeから除外または匿名化候補

unintended_affiliation_or_organization:
  Project責務上不要な所属・組織・企業名
  削除または中立化候補

technical_debris:
  .DS_Store、__MACOSX、Cache、Temporary File、Local Log等
  Git追跡対象外候補

manual_review:
  意味、Provenanceまたは権利上の必要性が不明
  自動変更禁止
```

第三者の正式名称、License、Attribution、引用元、Model配布元および技術選定理由まで「組織名」として機械的に削除してはならない。

## 6. Original Project Protection

Scanは原則Read-onlyで行う。検出しただけでは、元ProjectのFile、History、Metadataまたは外部Repositoryを変更するAuthorityは成立しない。

- 公開不要Fileは、まず`.gitignore`またはGit Index境界で追跡対象外にする。
- 元Projectから物理削除する必要がない場合は削除しない。
- 既にGit追跡済みだがLocal保持が必要なFileは、Working Treeから消さずGit追跡だけを外す案を優先する。
- 内容修正、名称変更、削除、History再構築およびRemote変更は、対象差分と影響を提示し、ユーザーの明示承認後に行う。
- Project Root外のCopy、Staging TreeまたはExternal RepositoryをTask側が勝手に作らない。

Mutationは[Research Asset Mutation Control](research_asset_mutation_control_ja.md)に従う。

## 7. `.gitignore`の役割

`.gitignore`は未追跡FileをCommit候補から除外する仕組みであり、既にCommit済みの情報をHistoryから消す仕組みではない。

現在の最低限境界：

- `.venv/`
- `.env`／`.env.*`（公開Template例外を除く）
- `models`／`*.gguf`
- Python／Test／Lint Cache
- `.DS_Store`／`__MACOSX/`
- Local Runtime Data

Push Gateでは、Ignore Ruleの存在だけで合格にせず、実際の追跡対象とOutgoing Treeへ不要物が含まれないことを確認する。

## 8. Backupとの関係

本書が時点を限定するのは、Identity／Affiliation／Public Debrisを目的とした広範な公開Sanitationである。通常Backupのたびに同じPrivacy／Presentation Scanを繰り返さない。

一方、Backupの再構築可能性と容量境界として、Model Weight、`.venv`、Cache、SecretおよびLocal Runtime DataをAllowlist方式でArchive対象外にする既存原則は維持する。これは元Projectからの削除を許可せず、GitHub公開Sanitationの代替でもない。

## 9. Existing Repository Continuity

既存Repositoryは削除・再作成せず、既に公開されたHistoryを継承して更新する。Contributor表示の単一化を目的としたHistory Rewrite、Force Push、Root Commit置換またはRepository再作成は行わない。

この方針は、少なくとも2026-07-27 JST時点で成立していた公開状態と、その後の開発連続性を保持するためのものである。正確な初回公開日時は未確定であり、本書は2026-07-27を厳密な初回公開日時として断定しない。

```text
Existing Remote History : preserve
Future GitHub Account   : nazuna-research
Historical Contributors : preserve as historical attribution
Repository Recreation   : cancelled
History Rewrite         : prohibited unless separately authorized
Visibility              : undecided; Public／Private変更は別判断
```

今後のCommit Author／Committer／TaggerおよびPush認証は、公開用GitHub Account `nazuna-research`へ統一する。GitHub-linked privacy-preserving Emailの具体値は本書へ記録しない。過去のContributor Attributionが既存Historyに残ることは受容し、それを除去するために既存Historyを破壊しない。

Local ProjectにGit Metadataが存在しない状態から既存Historyを継承する場合は、現在のProject Rootを即時`git init`してRemoteへ上書きする方式を採用しない。別途ユーザーが明示指定した作業場所へ既存RepositoryをCloneし、Remote Historyと基準Commitを確認した後、現在Projectの公開対象差分を反映・Reviewする方式を優先する。作業場所の作成、Clone、Copy、同期およびRemote操作は、各対象とActionについてユーザーの明示承認を得てから行う。

独自要素を選択的に除外した対外公開用Repositoryは、既存Repositoryとは別の公開Distributionとして扱う。両RepositoryのHistory、対象範囲および公開責務を混同せず、一方を他方へ無断で上書きしない。

既存Repositoryを将来Privateへ変更する場合は、Visibility変更前に公開状態のEvidenceを保存する。最低限、Repository URL、公開確認日時、基準Commit SHA、Source Archive、SHA-512 Manifestおよび必要な画面Evidenceを候補とする。Public継続／Private化の判断と実施時期は未確定であり、別途ユーザーが決定する。

### 9.1 Low-discoverability Current State

Existing History、先行公開性、Project名、Roadmap導線、許諾・禁止・免責を保持したまま、Repository Landing Pageと一般検索からの偶発的発見性を下げる調整を実施した。

```text
Topics            : none
About Description : empty
Website           : empty
Social Preview    : none
GitHub Pages      : unused
External Links    : intentionally absent
```

README、LICENSE、NOTICEおよびTERMS_OF_USEは低発見性版へ更新済みである。`CITATION.cff`はDefault BranchとLocal Currentから削除済みであり、削除前原文はHistory／Backupへ保持する。OSS化または再公開時にRoot公開Artifactと`CITATION.cff`を再評価・復元できる。

`CITATION.cff`削除はGitHubのMachine-readable Citation UIと発見導線を減らすが、Existing Commit History、Repository公開状態および外部Evidenceを消さない。先行公開性への影響は限定的だが、単一Artifactだけで法的優先性を保証するものではない。

低発見性運用は検索除外を保証しない。正確なProject名、Repository URL、Commit SHAまたはDocs内固有語による到達可能性は残る。

### 9.2 Dedicated SSH／Staging Clone Acceptance

GitHub更新用の専用SSH IdentityとHost Aliasをユーザー管理領域へ設定し、AuthenticationとRemote Read-only Queryに合格した。Private Key、Passphrase、個人Email、Credential実値および個人Home PathはProject Docsへ記録しない。

Original ProjectへGit Metadataを追加せず、ユーザーが明示指定した別のGit Staging CloneへExisting RepositoryをCloneした。

```text
Clone Branch          : main
Clone HEAD            : 55e0ab854db07212dce987d1a7d7c4e43e2b63c6
Expected HEAD Match   : yes
Git fsck              : pass
Clone Working Tree    : clean
Original Files Copied : none
Git Config Changed    : none
Commit／Tag／Push      : none
```

Clone直下で検出した未追跡`.DS_Store`は、生成経路を断定せず、ユーザー承認済みのExact PathだけをRecoverableにTrashへ移動した。Cleanupのための`.gitignore`変更は行っていない。

上記はClone Acceptance時点の履歴である。その後、Read-only Delta Inventory、Source→Target Manifest、Backup、実統合、Sanitation、Test、Commit、Draft Pull Request、Review、MergeおよびPostflightまで完了した。現在の運用は[Git Workflow Policy](git_workflow_policy_ja.md)に従う。

### 9.3 First Git-managed Publication Acceptance

```text
Pull Request       : #1 merged
Merge Method       : merge commit
Merge Commit       : 9fff303175a3224963254eacddd66f9cf5112a5a
Default Branch     : main
Local／origin/main : aligned
Git fsck           : pass
Publication Files  : 1,053／1,053
Source-only        : 0
Target-only        : 0
Content Mismatch   : 0
Legacy docs/phases : 0
Obsolete Images    : 0
Tag／Release        : none
```

作業BranchはPull Request Mergeと`main`包含をLocal／Remote双方で証明した後、ユーザー承認によりLocal／Remoteから削除した。Branch削除はMerge Commit、Commit SHA、PRおよびBackupを削除しない。

本Acceptanceは、既存Historyを壊さず現在のSourceをGitHub `main`へ統合できたことを示す。Phase 1-ex完了、完了Tag、Releaseまたは単一Git Rootへの移行を自動的に意味しない。

### 9.4 Direct `main`追加Docs更新／単一Git Root

PR #1 Merge後に発生した限定Docs更新は、Risk-based Git Workflowとユーザ明示承認によりDirect `main`で反映した。

```text
Commit            : 9ac8a6ba4a2120d93856356fababd130af3aa352
Message           : docs(phase-1-ex): establish git workflow and merge record
Changed Files     : 16
Insertions        : 4650
Deletions         : 18
Local／origin／remote: aligned
Git fsck          : pass
```

Commit前にExact Allowlist、Staged Diff、Secret／Personal Identifier Candidate、Author Identity、File Scopeおよび`git diff --cached --check`を確認した。Lossless／History原文の末尾空行とMarkdown改行用2 Spaceは、原文維持のため明示的例外とし、実CodeのWhitespace Errorは0件であった。

その後、Source／Git StagingのBackup、HEAD一致、Working Tree Clean、`git fsck`、Publication Set一致およびユーザ明示承認をGateとして、Git Metadataを開発内容正本`margpa-runtime-llm`へ移行した。Cutover後のFull Testは`430 passed／3 deselected`であり、旧Git Staging RootはBackup後にユーザーが退役させた。

現在のPush Gateは単一Canonical RootのWorking Tree、Index、Outgoing Commit RangeおよびRemoteを対象とする。旧Source／Staging間の二重同期を前提にしない。

## 10. Push Gate Failure

次のいずれかが未解決ならPushしない。

- Push対象範囲が不明
- Scan対象がWorking Treeだけ
- Outgoing Commit Metadata未確認
- 個人情報または旧第一者識別子のCandidateが未分類
- Secret／Credential Candidateが未解決
- 必須Third-party Attributionを誤って削除した可能性がある
- Ignore対象がGit追跡済み
- Commit Author／Committer／Taggerが承認済みIdentityと不一致
- Push対象SHAをユーザーが最終確認していない

Failure時に自動Force Push、History Rewrite、File削除またはRemote削除を行わない。

## 11. Authority

GitHub Push、Repository削除・再作成、Visibility変更、Force Push、History RewriteおよびRemote設定はユーザーの個別承認を必要とする。

本書はSanitationの時点と判定境界を定めるものであり、Git操作またはExternal Mutationを自動許可しない。
