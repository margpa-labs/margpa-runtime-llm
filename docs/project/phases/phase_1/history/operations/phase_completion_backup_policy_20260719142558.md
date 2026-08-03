# Phase完了Backup／Snapshot運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全上位Phaseの完了後Backup、Source Archive、Evidence Manifest、Restore
- 正本言語: 日本語
- 関連共通Rule: [documentation_rules_20260719142558.md](../requirements/documentation_rules_20260719142558.md)
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../requirements/task_role_write_authority_policy_20260719142558.md)
- supersedes: なし（新規Operations Policy系列）

## 1. 承認結論

Projectは、各上位Phaseの完了後にSource ArchiveとEvidenceを作成する。

Backupの正式Triggerは、設計者役がIndependent Reviewと必要文書を完了し、次の意味を明示的に出力した時点とする。

```text
Phase Nは完了。次はPhase N+1です。
```

文言の完全一致は必要ないが、次の両方が明示される必要がある。

1. 対象Phaseが完了・受入済みであること
2. 次Phaseへ移行すること

Implementer Statusが出ただけ、実装が終わったように見えるだけ、またはSubphaseのみが終わった時点ではBackup Triggerとしない。

## 2. Timing

正式な順序：

```text
Implementation Complete
  ↓
Implementer Status
  ↓
Designer Independent Review
  ↓
Required Follow-up Complete
  ↓
Phase Final Review／User Manual／Index確定
  ↓
Designer Phase Completion Declaration
  ↓
Phase Backup／Integrity Verification
  ↓
Next Phaseの実装変更
```

BackupはPhase完了宣言の後に取る。

原則として、次PhaseのSource／Config／Docsの実質的変更を始める前にBackupとIntegrity Verificationを完了させる。

## 3. Phase単位

定期Backupは上位Phase単位とする。

```text
Phase 1
Phase 2
Phase 3
...
```

`Phase 1-A`～`Phase 1-E`のようなSubphase完了だけで、自動的にPhase Backupを必須としない。

ただし、次の場合は臨時Snapshotを追加できる。

- 大規模Schema Migrationの直前
- 破壊的変更の直前
- Storage／Audit形式変更の直前
- Model／Backend交換の直前
- ユーザーが明示的にSnapshotを要求した場合

臨時SnapshotはPhase完了Backupと区別したName／Manifestを使用する。

## 4. Phase Completion Preconditions

設計者役は、次を確認した後にPhase完了を宣言する。

- Phase配下の必須SubphaseがComplete／Accepted
- Blockerがない
- 未解決事項が次PhaseまたはKnown Limitationとして明記済み
- Independent Review完了
- 必要なRegression／Native Verification完了
- Current User Manualが実装と整合
- Phase Final Reviewが存在
- 最新Documentation IndexがCurrent Setを正しく示す
- Backup対象と除外対象の範囲が確定

## 5. Backup Set

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

## 6. Archive Content

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

## 7. Exclusion

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

## 8. Snapshot Manifest

Manifestは最低限次を含む。

### Identity

- Schema Version
- Snapshot ID
- Project Name
- Phase ID／Phase Name／Milestone
- Completion Declaration Timestamp
- Archive Creation Timestamp
- Current Documentation Index
- Phase Final Review
- Current Roadmap

### Source

- Included Path
- Excluded Path／Reason
- Included File Inventory
- Included File Size
- Included File SHA-512
- Manifest Canonicalization
- Manifest SHA-512

### VCS

CurrentはGit未使用のため、事実として次のように記録する。

```text
vcs.type        : none
vcs.commit_hash : null
vcs.tag         : null
```

Git導入後はCommit Hash／Tagを同じSchemaへ追加できる。Git未使用時はManifest SHA-512をSource Snapshot Identityとする。

### Environment

- OS／OS Version
- Architecture
- Hardware Profile
- Python Version
- Backend／Version／Build Variant
- Acceleration
- Dependency Lock SHA-512
- Verification Script／Result参照

### Model

- Model Key／Role
- Distribution Repository／Upstream Model
- File Name
- Relative Model Path
- External Model Root
- Size
- Format／Quantization
- Model Artifact SHA-512
- Model Definition SHA-512
- Symbolic Link復元方法

### Evidence

- Implementer Status
- Designer Final Review
- Test Command／Result Summary
- Static／Default／Native Gate
- Known Limitation
- User Manual

## 9. Manifest／Receiptの分離

ZIP本体のSHA-512をZIP内のManifestへ格納すると自己参照になる。

そのため次の分離を必須とする。

```text
Manifest:
  Archive内Content、File Hash、Environment、Model、Evidence

Receipt:
  完成後のZIP File Name、Size、SHA-512、Manifest SHA-512

SHA512 Sidecar:
  簡易整合性検証用
```

ManifestはArchive内に含め、必要に応じてArchiveの外にも同一Copyを保持する。ReceiptはArchive完成後に作るDetached Sidecarとする。

## 10. Docs Record

各Phaseの完了時に、設計者役は次の系列を`docs/operations/`へ作成する。

```text
phase_<n>_<milestone>_snapshot_record_YYYYMMDDHHMMSS.md
```

Phase 1候補：

```text
phase_1_portable_runtime_mvp_snapshot_record_YYYYMMDDHHMMSS.md
```

Snapshot Recordは次を人間向けに示す。

- Phase完了条件
- Final Review
- Current Index
- Current Roadmap
- Test Evidence
- Model／Environment Summary
- Backup SetのNaming Rule
- Manifest／Receiptの責務
- Exclusion
- Restore Entry Point

ZIP自体のHashはDetached Receiptを正本とし、Snapshot Record内へ自己参照となる形で書かない。

## 11. Backup Location

BackupはProject Root内へ保存しない。Archiveが次のArchiveへ再帰的に入ることと、Project自体が肥大化することを防ぐ。

推奨論理構造：

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ backups/
   └─ margpa-runtime-llm/
      └─ phase_<n>/
```

実体PathはBackup実行前にユーザーが確定する。

同じMac／同じSSD上のCopyは誤操作対策にはなるが、Disk故障対策にはならない。重要なPhase Backupは外付けStorageまたはCloudへ第2Copyを保持することを推奨する。

## 12. Integrity Verification

Backup完了条件：

1. ZIPの構造検査がPass
2. ZIP SHA-512が計算済み
3. ReceiptとSHA512 Sidecarが一致
4. Manifest SHA-512が一致
5. Included File InventoryとArchive Contentが整合
6. Secret／Model Binary／`.venv`が含まれない
7. Temporary DirectoryへのTest Extractが成功
8. Restore Entry Point／Setup Recipeが特定できる

Modelを含まないため、Archive単体でNative Generationが完結すると主張しない。ManifestとSetup Recipeを使い、外部Modelを再配置して復元する。

## 13. Restore Test

最低限のRestore Test：

- ZIPをTemporary DirectoryへExtract
- Expected Root File／Directory確認
- Manifest File Inventory検証
- `uv.lock`／`pyproject.toml`の存在確認
- Modelが除外されていることの確認
- Model Root復元手順の確認
- DocsのLatest Index／Final Review参照確認

Dependency Install／Model Download／Native Testまで実行するFull Restore Drillは、ユーザーが別途許可した場合に行う。

## 14. Immutability／Retention

- Backup Setを上書きしない
- Timestampを持たせる
- 再作成時は新Timestampとする
- 古いPhase Backupを原則削除しない
- 再作成理由を新Manifest／Receiptへ記録する
- Backup SetのRenameを原則行わない

## 15. Git導入後

Gitは現時点で必須としない。

将来Gitを導入した場合は、Phase Backup Setに次を追加する。

```text
commit_hash
tag
dirty_state
repository_remote
```

Tag候補：

```text
phase-1-portable-runtime-mvp
```

Git TagはSource History上のIdentity、ZIPは独立復元用Archive、Manifest／ReceiptはEvidenceとして併存させる。

## 16. Authorization Boundary

本PolicyはBackupのTiming／Content／Evidence規則を承認する。

本Policyの作成だけでは、次を自動解禁しない。

- External Backup Directoryの作成
- ZIP／Manifest／Receiptの実生成
- Project外へのWrite
- Cloud Upload
- External DriveへのCopy
- Git初期化／Commit／Tag

実際のBackup作成はPhase完了Triggerの後、ユーザーの指示または事前に承認されたBackup Operator Scopeで行う。

