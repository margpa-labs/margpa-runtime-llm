# Phase完了Backup／Snapshot運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全Top-Level Phaseの完了後Backup、Source Archive、Evidence Manifest、Restore
- 正本言語: 日本語
- 関連共通Rule: [documentation_rules_20260719171836.md](../requirements/documentation_rules_20260719171836.md)
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../requirements/task_role_write_authority_policy_20260719142558.md)
- Known Observations: [known_issues_and_observations_20260719171836.md](known_issues_and_observations_20260719171836.md)
- supersedes: `phase_completion_backup_policy_20260719142558.md`

## 1. 承認結論

Projectは、各Top-Level Phaseについて次の2つが両方成立した後に、Phase Backupを取得する。

```text
Gate A: 設計者役によるPhase完了宣言と次Phase移行可能宣言
Gate B: ユーザーによる対象Manual／対象Snapshotの受入テスト合格宣言
```

いずれか片方だけではBackup Triggerは成立しない。

設計者宣言の意味：

```text
Phase Nは完了です。次はPhase N+1へ移行可能です。
```

ユーザー宣言の推奨形式：

```text
<対象User Manual File>のPhase Nユーザー受入テストは、全項目合格です。
```

文言の完全一致は必要ない。ただし、対象Phase、対象ManualまたはSnapshot、テスト合格が明確でなければならない。

## 2. Dual Approval Gate

Backup Triggerの状態は次で管理する。

| Designer Gate | User Test Gate | Backup |
|---|---|---|
| 未成立 | 未成立 | 不可 |
| 成立 | 未成立 | 不可 |
| 未成立 | 成立 | 不可 |
| 成立 | 成立 | 実行可能 |

推奨順序：

```text
Implementation Complete
  ↓
Implementer Status
  ↓
Designer Independent Review
  ↓
Required Follow-up Complete
  ↓
Current User Manual／Final Docs／Index
  ↓
Designer Final Readiness提示
  ↓
User Acceptance Test
  ↓
User Test Pass Declaration
  ↓
Designer Phase Completion／Next Phase Eligible Declaration
  ↓
Phase Backup／Integrity Verification
  ↓
Next Phaseの実質的変更
```

事情によりGate AとGate Bの順序が逆でも、両方が同じ対象状態を参照していればよい。

## 3. State Freeze

User TestとDesigner Declarationは、同じProject状態を対象にしなければならない。

いずれかのGate成立後、Backup作成前に次のMaterial Changeが入った場合、影響範囲に応じてReviewまたはUser Testを再実行する。

- `src/`、`tests/`、`config/`、`scripts/`の変更
- Dependency／Lock／Python Versionの変更
- Model Definition／Artifactの変更
- User Manualの操作結果に影響する変更
- Phase Acceptanceを変えるRequirements／Architecture／ADR変更

誤字だけのDocs追加など、実行状態へ影響しない変更でも、最新IndexとBackup Inventoryには反映する。

Backup Receipt／Snapshot Recordには、両Gateの対象文書とTimestampを記録する。

## 4. Triggerにならないもの

次だけではBackup Triggerとしない。

- Implementer Statusの作成
- 実装が終わったように見えること
- SubphaseのComplete／Accepted
- Designer Reviewだけの完了
- User Testだけの成功
- User Manual作成だけの完了
- 次PhaseのPlanning Docsが存在すること

`Phase 1-A`～`Phase 1-E`のようなSubphase完了だけで、Top-Level Phase Backupを必須としない。

## 5. Phase Completion Preconditions

設計者役は、次を確認した後にGate Aを成立させる。

- Phase配下の必須SubphaseがComplete／Accepted
- Blockerがない
- 未解決事項が次PhaseまたはKnown Limitationとして明記済み
- Independent Review完了
- 必要なRegression／Native Verification完了
- Current User Manualが実装と整合
- Phase Final Reviewが存在
- 最新Documentation IndexがCurrent Setを正しく示す
- User Acceptance Testの結果が確認可能
- Backup対象と除外対象の範囲が確定

UserはCurrent User Manualに従って受入テストを行い、Gate Bを明示する。

## 6. Phase単位と臨時Snapshot

定期BackupはTop-Level Phase単位とする。

```text
Phase 1
Phase 2
Phase 3
...
```

次の場合は、Dual Approval Gateとは別に臨時Snapshotを追加できる。

- 大規模Schema Migrationの直前
- 破壊的変更の直前
- Storage／Audit形式変更の直前
- Model／Backend交換の直前
- ユーザーが明示的にSnapshotを要求した場合

臨時SnapshotはPhase完了Backupと区別したName／Manifestを使用する。

## 7. Backup Set

Phase Backupは次の4点Setを基本とする。

```text
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS.zip
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_manifest.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_receipt.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_sha512.txt
```

Phase 1候補：

```text
margpa-runtime-llm_phase_1_portable_runtime_mvp_YYYYMMDDHHMMSS.zip
```

Archive、Manifest、Receipt、SHA-512 Fileを同一Basename系列で紐付ける。

## 8. Archive Content

原則としてAllowlist方式を使用する。

Include候補：

```text
src/
tests/
config/
docs/
scripts/
notebooks/                 # 存在する場合

pyproject.toml
uv.lock
.python-version            # 存在する場合
.gitignore                 # 存在する場合
README*
LICENSE*
再構築に必要な明示済みRoot File
```

`config/`内でもSecret、Local OverrideまたはCredentialを含むFileは除外する。

## 9. Exclusion

```text
.venv/
models/
GGUF／Model Binary
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/
.DS_Store
Cache
一時File
実行Log
Audit実データ
.env
Secret／Credential
Local Override
Backup Directory自体
```

Project Rootの`models/` Symbolic LinkはArchiveから原則除外する。Absolute Linkを別環境へ復元しないためである。Link Target／復元手順はManifestへ記録する。

## 10. Snapshot Manifest

Manifestは最低限次を含む。

### Identity

- Schema Version
- Snapshot ID
- Project Name
- Phase ID／Phase Name／Milestone
- Designer Completion／Next Phase Declaration
- User Acceptance Test Declaration
- 両DeclarationのTimestamp／対象Manual／対象Index
- Archive Creation Timestamp
- Current Documentation Index
- Phase Final Review
- Current Roadmap

### Source

- Included／Excluded PathとReason
- Included File Inventory／Size／SHA-512
- Manifest Canonicalization／SHA-512

### VCS

CurrentはGit未使用のため、事実として次を記録する。

```text
vcs.type        : none
vcs.commit_hash : null
vcs.tag         : null
```

Git未使用時はManifest SHA-512をSource Snapshot Identityとする。

### Environment／Model／Evidence

- OS／Architecture／Hardware
- Python／Backend／Acceleration
- Dependency Lock Hash
- Model Key／Role／Repository／File／Size／Format／Quantization
- Model Artifact／Definition SHA-512
- Symbolic Link復元方法
- Implementer Status
- Designer Final Review
- User Test Evidence
- Static／Default／Native Gate
- Known Issues／Observations
- User Manual

## 11. Manifest／Receiptの分離

ZIP本体のSHA-512をZIP内Manifestへ格納すると自己参照になるため、次を分離する。

```text
Manifest:
  Archive内Content、File Hash、Environment、Model、Evidence

Receipt:
  完成後のZIP File Name、Size、SHA-512、Manifest SHA-512

SHA512 Sidecar:
  簡易整合性検証用
```

ReceiptはArchive完成後に作るDetached Sidecarとする。

## 12. Docs Record

各Phaseの完了時に、設計者役は次の系列を`docs/operations/`へ作成する。

```text
phase_<n>_<milestone>_snapshot_record_YYYYMMDDHHMMSS.md
```

Snapshot Recordは次を人間向けに示す。

- Dual Approval Gate Evidence
- Phase完了条件
- Final Review／Current Index／Roadmap
- Test Evidence
- Model／Environment Summary
- Backup SetのNaming Rule
- Manifest／Receiptの責務
- Exclusion
- Restore Entry Point

## 13. Backup Location

BackupはProject Root内へ保存しない。

推奨論理構造：

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ backups/
   └─ margpa-runtime-llm/
      └─ phase_<n>/
```

実体PathはBackup実行前にユーザーが確定する。同じMac／同じSSD上のCopyはDisk故障対策にはならないため、重要なBackupは第2Storageも検討する。

## 14. Integrity／Restore Verification

Backup完了条件：

1. ZIP構造検査がPass
2. ZIP SHA-512が計算済み
3. ReceiptとSHA512 Sidecarが一致
4. Manifest SHA-512が一致
5. InventoryとArchive Contentが整合
6. Secret／Model Binary／`.venv`が含まれない
7. Temporary DirectoryへのTest Extractが成功
8. Restore Entry Point／Setup Recipeが特定可能
9. Dual Approval Gate EvidenceがManifest／Snapshot Recordに存在

最低限のRestore Test：

- ZIPをTemporary DirectoryへExtract
- Expected Root File／Directory確認
- Manifest Inventory検証
- `uv.lock`／`pyproject.toml`確認
- Model除外確認
- Model Root復元手順確認
- Latest Index／Final Review／User Manual参照確認

Dependency Install、Model Download、Native Testまで行うFull Restore Drillは、別途ユーザー許可を必要とする。

## 15. Immutability／Retention

- Backup Setを上書きしない
- Timestampを持たせる
- 再作成時は新Timestampとする
- 古いPhase Backupを原則削除しない
- 再作成理由を新Manifest／Receiptへ記録する
- Backup Setを原則Renameしない

## 16. Git導入後

Gitは現時点で必須としない。将来導入した場合は、Commit Hash、Tag、Dirty State、RemoteをManifestへ追加する。

Git TagはSource History上のIdentity、ZIPは独立復元用Archive、Manifest／ReceiptはEvidenceとして併存させる。

## 17. Authorization Boundary

本PolicyはBackupのTiming／Content／Evidence規則を承認する。

本Policyの作成、Designer Gate、User Test Gateは、次を単独では自動解禁しない。

- External Backup Directoryの作成
- ZIP／Manifest／Receiptの実生成
- Project外へのWrite
- Cloud Upload
- External DriveへのCopy
- Git初期化／Commit／Tag

実際のBackup作成はDual Approval Gate成立後、ユーザーの指示または事前承認済みBackup Operator Scopeで行う。

