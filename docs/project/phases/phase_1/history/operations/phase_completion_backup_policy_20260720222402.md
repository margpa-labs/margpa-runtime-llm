# Phase完了Backup／GitHub公開運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全Top-Level Phase、Phase 1-ex、Backup、Source Archive、GitHub公開
- 正本言語: 日本語
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../requirements/public_identity_and_personal_information_policy_20260720220216.md)
- supersedes: `phase_completion_backup_policy_20260719171836.md`

## 1. 基本決定

Projectは原則として、各Phaseの確定Snapshotごとに次の順序で運用する。

```text
Phase実装・検証
  → User Acceptance
  → Designer Phase完了／次Phase着手可能宣言
  → Backup Candidate作成
  → Archive Sanitation
  → Manifest／Hash／Restore検証
  → Backup確定
  → GitHub公開準備・公開
  → 次Phaseの実質的変更
```

各PhaseをGitHub上でも識別可能な履歴として残す。GitHub公開はBackupと同一の確定Source Snapshotを対象とし、別状態を黙って公開しない。

## 2. Backup Trigger

Backup Triggerは、同じProject状態について次の両Gateが成立した時点とする。

```text
Gate A: 設計者役がPhase完了と次Phase着手可能を宣言
Gate B: ユーザーが対象Manual／Snapshotの受入テスト合格を宣言
```

Implementer Status、Subphase完了、Designer Review、User Testのいずれか単独ではTriggerにならない。

一方のGate成立後にSource、Config、Dependency、Lock、Model Definition、User ManualへMaterial Changeが入った場合、必要なReviewまたはUser Testを再実行する。

## 3. PhaseごとのGitHub公開

通常運用では、各PhaseのBackup確定後に対応SnapshotをGitHubへ反映する。

最低限、次の対応関係を記録する。

- Phase ID／Milestone
- Backup Snapshot ID
- Archive SHA-512
- Documentation Index
- Git Commit Hash
- Git TagまたはRelease識別子
- 公開日時
- Known Issues

Branch、Tag、Release、Repository Visibility、GitHub Pages等の具体方式はPhase 1-exで再整備する。本文書だけではGit初期化、Remote作成、Push、公開範囲変更を許可しない。

## 4. 初回公開の例外

初回GitHub公開だけは、現在のPhase 1機能実装直後には行わない。

```text
Phase 1機能Snapshot確定
  → Phase 1-ex「運用再整備」
  → Phase 1-ex完了Gate
  → 公開候補Backup確定
  → 初回GitHub公開
```

初回公開SnapshotはPhase 1-ex完了後の状態とする。Phase 1-ex前のSnapshotはBackupとして保持できるが、初回GitHub公開対象にはしない。

## 5. Phase 1-ex

Phase 1-exをPhase 1と初回GitHub公開の間に追加する。

```text
Name   : Phase 1-ex
Purpose: 運用再整備
State  : Added／Requirements Pending
```

詳細要件、受入条件、実装範囲は後続会話で定義する。現時点ではPhaseの存在、目的、配置、初回公開Gateとの関係だけを確定し、Source変更や外部操作を許可しない。

## 6. Backup Set

Phase Backupは次を基本Setとする。

```text
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS.zip
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_manifest.json
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_receipt.json
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_sha512.txt
```

Archive内のRoot Directoryは`margpa-runtime-llm/`とする。

## 7. Archive Include

原則Allowlist方式とし、再構築に必要な管理対象だけを入れる。

```text
src/
tests/
config/
docs/
scripts/
notebooks/       # 存在し、公開対象の場合
pyproject.toml
uv.lock
.python-version
.gitignore
README*
LICENSE*
明示承認されたRoot File
```

## 8. 毎回必須のArchive Sanitation

毎回、Backup Candidate作成後かつBackup確定前に、ZIP内の`margpa-runtime-llm/`を検査し、不要Fileをすべて除去する。

最低限の除外対象：

```text
.DS_Storeおよび大小文字違い
.venv/
models Symlink／models/
*.gguf／Model Binary
.git/
__pycache__/
*.pyc／*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage／htmlcov/
.ipynb_checkpoints/
.env／Credential／Secret
var/
実会話Log／Audit実Data
Temporary File／Editor Backup／OS Metadata
Local Override
Backup Directory自体
```

Allowlist外のFileは「必要そうだから」という推測で残さず、必要性を確認してから明示Includeする。

不要物を含むZIPを発見した場合、確定済みArchiveを直接上書きしない。未確定Candidateを破棄またはCleanな内容から再構築し、新Timestamp、Manifest、Receipt、SHA-512を生成する。

## 9. Sanitation完了条件

1. ZIPのRootが`margpa-runtime-llm/`だけである
2. InventoryがAllowlistと一致する
3. `.venv`、Model、Symlink、Cache、`.DS_Store`、Credentialがない
4. 個人固有Path、Hostname、Email、SecretのContent ScanがPassする
5. 第一者の公開Identityが`Nazuna Research`へ統一されている
6. Temporary DirectoryへのExtractが成功する
7. Manifest Inventoryと実Contentが一致する
8. Archive、Manifest、Receipt、SidecarのHashが一致する

## 10. Public Identity

第一者の公開Identityは常に次へ統一する。

```text
Nazuna Research
```

Git Author／Committer、GitHub Profile、README、License／Copyrightの扱いは、Privacy PolicyとPhase 1-exで確定する。第三者の正式なAttributionは維持する。

## 11. Manifest／Receipt

ManifestにはPhase、両Gate、Current Index、Include／Exclude Inventory、各File SHA-512、Environment、Model Metadata、Test Evidence、Known Issues、Git情報を記録する。

ZIP自身のHashは自己参照を避けるためDetached Receiptへ記録する。Git開始前は`vcs.type = none`、開始後はCommit Hash、Tag、Dirty State、Remoteを記録する。

## 12. Backup Location／Retention

- BackupはProject Root内へ保存しない
- Backup Setを上書きしない
- 再作成時は新Timestampを使う
- 古いPhase Backupを原則削除しない
- 同一Disk上だけでなく、第2Storageも検討する

## 13. Restore Verification

- Temporary DirectoryへExtract
- Expected Directory／Root File確認
- Manifest Inventory／SHA-512検証
- `pyproject.toml`／`uv.lock`確認
- Model／`.venv`／Local Artifact除外確認
- Model Root復元手順確認
- Latest Index／Final Review／User Manual確認

Dependency Install、Model Download、Native Testを伴うFull Restore Drillは別途許可を必要とする。

## 14. Authorization Boundary

本Policyは運用要件を確定するが、Backup実生成、Project外Write、Git操作、GitHub操作、Cloud Upload、公開を自動許可しない。それぞれ実行時のユーザー指示または事前承認Scopeを必要とする。
