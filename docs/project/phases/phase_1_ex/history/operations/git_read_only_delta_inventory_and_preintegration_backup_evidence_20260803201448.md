# Git Read-only Delta Inventory／統合直前Backup Evidence

```yaml
document_id: git_read_only_delta_inventory_and_preintegration_backup_evidence
phase: phase_1_ex
status: accepted_preintegration_checkpoint
language: ja
created_at: 2026-08-03 20:14:48 JST
owner: 設計統括者役
external_mutation: none
git_mutation: none
```

## 1. 目的

本書は、長時間OrchestrationのSafe Pause優先確認、Existing GitHub RepositoryのRead-only Delta Inventory Review、Original ProjectとGit Staging Cloneの統合境界および実統合直前BackupのSHA-512 Evidenceを一つのAppend-only Recordに固定する。

本時点でOriginal→Clone Copy、Delete、`git add`、Commit、Tag、Push、Merge、History RewriteまたはRemote変更は実施していない。

## 2. Long-running OrchestrationのSafe Pause確認

「じゃ、あとよろしく」と委任された場合も、翌朝までの一Work Unit進行は運用目標であり、無理な完了を作る約束ではない。

次の例外では、進行量より安全な中断を優先する。

- AuthorityまたはScopeが不明
- User Decision、Manual Test、BackupまたはExternal Service待ち
- Unexpected Diff、Test Failure、復元不確実またはSecurity／Privacy Risk
- Codex利用可能量、Credit、Quota、Task LimitまたはPlatform制約
- 無理に進めることがユーザーの再検証、復旧または研究Asset保護負担を増やす場合

中断時は、最後の確認済み状態、停止理由、Open Finding、次の最小Actionおよび必要Authorityを残す。

## 3. Read-only Delta Inventory Review

Inventory工程は`PASS`とする。これはRead-onlyで差分を取得し、OriginalとCloneを変更しなかったことへのAcceptedであり、統合実行のAcceptedではない。

```text
Clone HEAD Match                 : PASS
Clone Working Tree              : CLEAN
Tracked Modified Candidates     : 5
Clone-only Tracked Candidates   : 41
Original-only Git Candidates    : 767
Ignored Local-only Artifacts    : 16,809
External Model Symlink          : 1／NOT FOLLOWED
Privacy Scan                    : NOT RUN／Push Gateで実施
Copy／Delete／Git Mutation      : NONE
```

分類は次のとおり。

- 5件は`UPDATE_CANDIDATE`。
- 767件は`ADD_CANDIDATE`であり、追加承認済みではない。
- Clone-only 41件は`RETAIN_PENDING_DECISION`とし、自動削除しない。旧Docs Rootと現Canonical Structureの差を含むため、統合Manifestで保持／退役を判定する。
- 16,809件のIgnore対象は`EXCLUDE`。
- `models`は`EXCLUDE_SYMLINK`とし、Link自体も外部TargetもGit StagingへCopyしない。

## 4. Source／Targetの正本境界

```text
Git Historyの正本:
  margpa-runtime-llm_git_staging/.git/

次CommitのWorking Tree内容正本:
  margpa-runtime-llm/
```

Git Staging Cloneは、GitHubへ先行掲載したExisting Historyを保持する器である。Clone内の旧または不完全なDirectory Structureを、次Snapshotの内容正本としない。

将来の統合はRoot-to-Rootで行う。

```text
Correct:
  margpa-runtime-llm/src/
    → margpa-runtime-llm_git_staging/src/

Prohibited:
  margpa-runtime-llm_git_staging/margpa-runtime-llm/src/
```

ただし、Originalの全内容を無分類で上書きせず、Source→Target Integration Manifestで承認されたPathだけを対象とする。`.git/`を維持し、`rsync --delete`等の一括削除同期を使用しない。

## 5. 統合直前Backup

ユーザーは、実統合前の規模／RiskベースBackup Gateとして、Original ProjectとGit Staging Cloneの両方をZIPで保全した。

### 5.1 ZIP File SHA-512

```text
margpa-runtime-llm_git_staging_統合直前_20260803.zip
Size   : 10,734,068 bytes
SHA-512: beee3988ab0367b576e11f3828101aeef83b56fb43eb4124e6d37388a05a93eeb2ef853a36ff973c14e14261650dbcd6e2945e27e5eff02dfd05b7f27c672d55
CRC    : PASS

margpa-runtime-llm_統合直前_20260803.zip
Size   : 139,491,044 bytes
SHA-512: 3adb5007c8047830bd6e04da5d4e916d292535ac061d883122cca698f860fc4ede702af60fe8db00850bde29be13cda9da6113395024a5582f9715d12eb065af
CRC    : PASS
```

Staging ZIPに`.git/`が収録されていることを確認した。Original ZIPの`models`はSymlinkのまま収録され、外部Model本体は展開されていない。Original ZIPは非公開Backupであり、`.venv/`と`__MACOSX/`も含むため、GitHub掲載Artifactとして使用しない。

### 5.2 Directory Tree SHA-512

Directoryには単一Fileの標準SHA-512が存在しないため、次の決定論的Tree ManifestをSHA-512化した。

```text
Relative Path
Entry Type
Regular File Size
Regular File Content SHA-512
Symlink Target／NOT FOLLOWED
Directory Entry
```

PathはByte順に固定し、Symlink Directoryを再帰追跡していない。

```text
margpa-runtime-llm
Files       : 17,834
Directories : 2,339
Symlinks    : 4
Other       : 0
File Bytes  : 412,668,376
Tree SHA-512:
397076554b9b925b7b190ecea880abc4206b5ea01e1a24b722c7462707afb1cfbe03e3f9a21180b2737ace3e7b28a51bf55d6a6bc590bf8b225b8b4ce9519828

margpa-runtime-llm_git_staging
Files       : 313
Directories : 112
Symlinks    : 0
Other       : 0
File Bytes  : 25,734,921
Tree SHA-512:
275063c8505c4b0f4fd2a0188f34eab2142005816e94ec4dba7c21b0ed338b822a83d157e1740029b840d7a3d1cb3207df01c1b7b10a02c9402f12f5a2637589
```

Tree SHA-512はZIP SHA-512と同値になるものではない。ZIPはCompression、Archive MetadataおよびEntry Orderingを含む別Artifactである。

## 6. Evidenceの時点境界

上記Tree SHA-512は、本RecordをOriginal Project内へ追加する前の「統合直前Backup時点」に対応する。本Record、Phase Index更新、History SnapshotおよびDocumentation Index Snapshotはその後に発生するDocs-only Deltaである。

したがって、実Copy前の最終Delta Refreshで本Recordと関連Index／Historyを`ADD／UPDATE_CANDIDATE`へ追加する。取得済みZIP SHA-512はImmutable Backup ArtifactのDigestとして変わらない。

## 7. Next Gate

```text
Source→Target Integration Manifestの完全Path Review
  → Clone-only 41件のRETAIN／RETIRE判定
  → ADD／UPDATE／EXCLUDE確定
  → 本Docs-only DeltaのRefresh
  → Copy Dry-run
  → ユーザー承認
  → 承認済みPathだけをRoot-to-Root Copy
  → Diff／Test／Privacy／Secret／License Review
  → Commit／Tag／Push別Gate
```

本Backupは実統合前Checkpointを満たすが、Phase 1-ex完了時の最終Phase Backupを代替しない。
