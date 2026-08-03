# GitHub Publication Sanitation Policy

```yaml
document_id: git_publication_sanitation_policy
status: current_effective
language: ja
created_at: 2026-08-02 07:39:01 JST
updated_at: 2026-08-02 07:39:01 JST
owner: 設計統括者役
decision_authority: user
applies_to: github_push_preparation
default_outside_gate: no_scan_no_delete
failure_policy: block_push
```

## 1. 目的

本書は、第一者の旧個人Account Handle、作者の個人情報その他の識別可能情報、意図しない組織名、`.DS_Store`等のOS Metadataおよび公開不要Artifactについて、検査・分類・除外・削除を行う時点をGitHub Push Preparation Gateへ限定する共通運用を定める。

本決定は、通常開発、通常Review、Phase途中のDocs更新および日常的なLocal実行のたびに同一の広範Scanや削除を繰り返さないためのScope／Cost統制である。

## 2. User Decision

2026-08-02以降、次の確認および公開用除外作業は、GitHubへPushする公開単位でだけ実施する。

- 第一者の旧個人Account Handle
- 作者の氏名、個人Email、個人連絡先、個人Profile等
- その他、個人または特定主体を不必要に識別できる情報
- 意図しないOrganization／Company／Affiliation表記
- `.DS_Store`、`__MACOSX/`、Cache、Temporary Artifactその他の公開不要物

通常開発中に、上記だけを目的とした全Project再帰Scan、名称置換、削除またはCleanupを定例実行しない。

## 3. 「Push時」の正確な意味

Gitでは、一度Commitへ含めた情報をWorking Treeから消しても、Push対象Historyに残る。したがって、本書の「GitHubにPushする時」は、送信Commandの直前だけを意味しない。

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

## 9. Clean Repository Recreation

既存Web Upload由来Historyは新しい正式Repositoryへ移行しない。新Repositoryは、GitHub公開Gateに合格したClean Root Commitから開始する。

```text
Repository Owner : margpa-labs
Contributor      : Nazuna Researchの専用GitHub Account
Commit Name      : Nazuna Research
Commit Email     : 専用AccountのGitHub noreply Email
History Source   : Clean Root Commit only
```

旧個人Accountへ紐付くCommit、Web Upload Commit、試験用Commitおよび旧Contributor統計を新RepositoryのHistoryへ含めない。

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
